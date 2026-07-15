import requests
from bs4 import BeautifulSoup
import os

# Create a folder to hold the article pages
os.makedirs('articles', exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

# We will use the main opinion section URL
motamot_url = "https://www.prothomalo.com/opinion"
print(f"Fetching main page: {motamot_url}")

response = requests.get(motamot_url, headers=headers)
print(f"Main page status code: {response.status_code}")

soup_main = BeautifulSoup(response.content, 'html.parser')

html_index = "<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Motamot</title></head><body><h1>Motamot (Opinions)</h1><ul>"

count = 0
seen_links = set()

# Grab all links on the page
all_links = soup_main.find_all('a', href=True)
print(f"Found {len(all_links)} total links on the page.")

for a_tag in all_links:
    link = a_tag['href']
    
    # Convert relative links to full URLs
    if link.startswith('/'):
        link = "https://www.prothomalo.com" + link
        
    # Cast a wider net: grab links that look like articles (they usually have a longer URL)
    # and exclude category pages or author profiles
    if 'prothomalo.com/opinion/' in link and '/author/' not in link and link not in seen_links:
        title = a_tag.get_text().strip()
        
        if len(title) < 15: # Skip very short titles or empty images
            continue
            
        if count >= 15:
            break
            
        seen_links.add(link)
        print(f"Trying to fetch article: {title}")
        
        try:
            art_res = requests.get(link, headers=headers)
            soup_art = BeautifulSoup(art_res.content, 'html.parser')
            
            paragraphs = soup_art.find_all('p')
            article_text = ""
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 20: 
                    article_text += f"<p>{text}</p>"
                    
            if not article_text:
                print(f"  -> Failed: No paragraph text found for {link}")
                continue 
                
            safe_filename = f"motamot_{count}.html"
            with open(f"articles/{safe_filename}", "w", encoding="utf-8") as f:
                f.write(f"<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title}</title></head><body>")
                f.write(f"<a href='../index.html'>&laquo; Back to Motamot</a><hr><h1>{title}</h1>")
                f.write(article_text)
                f.write("<hr><a href='../index.html'>&laquo; Back to Motamot</a></body></html>")
                
            html_index += f"<li><a href='articles/{safe_filename}'>{title}</a><br><br></li>"
            count += 1
            print(f"  -> Success: Saved as {safe_filename}")
            
        except Exception as e:
            print(f"  -> Error fetching {link}: {e}")
            continue

html_index += "</ul></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_index)

print(f"Finished! Successfully scraped {count} articles.")
