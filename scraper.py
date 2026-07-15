import requests
from bs4 import BeautifulSoup
import os

# Create a folder to hold the article pages
os.makedirs('articles', exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Fetching the Google News Sitemap...")
# We point directly to the file meant for search engine bots
sitemap_url = "https://www.prothomalo.com/news_sitemap.xml"
response = requests.get(sitemap_url, headers=headers)

# Parse the sitemap
soup_xml = BeautifulSoup(response.content, 'xml')

html_index = "<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Motamot</title></head><body><h1>Motamot (Opinions)</h1><ul>"

count = 0
# Look at every single link published recently
for loc in soup_xml.find_all('loc'):
    link = loc.text
    
    # Filter out everything except opinion pieces
    if '/opinion/' in link:
        if count >= 15:
            break
            
        print(f"Found Motamot link: {link}")
        
        try:
            # Fetch the actual article page
            art_res = requests.get(link, headers=headers)
            soup_art = BeautifulSoup(art_res.content, 'html.parser')
            
            # Extract the title and clean it up
            title_tag = soup_art.find('title')
            title = title_tag.text.replace(' - Prothom Alo', '').strip() if title_tag else "No Title"
            
            # Extract only paragraph text
            paragraphs = soup_art.find_all('p')
            article_text = ""
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 20: 
                    article_text += f"<p>{text}</p>"
                    
            if not article_text:
                continue 
                
            # Save the clean article as its own HTML file
            safe_filename = f"motamot_{count}.html"
            with open(f"articles/{safe_filename}", "w", encoding="utf-8") as f:
                f.write(f"<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title}</title></head><body>")
                f.write(f"<a href='../index.html'>&laquo; Back to Motamot</a><hr><h1>{title}</h1>")
                f.write(article_text)
                f.write("<hr><a href='../index.html'>&laquo; Back to Motamot</a></body></html>")
                
            # Add a link to the main index page
            html_index += f"<li><a href='articles/{safe_filename}'>{title}</a><br><br></li>"
            count += 1
            print(f" -> Success!")
            
        except Exception as e:
            print(f" -> Error: {e}")
            continue

html_index += "</ul></body></html>"

# Save the main index page
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_index)

print(f"Finished! Successfully built the site with {count} articles.")
