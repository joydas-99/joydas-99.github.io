import requests
from bs4 import BeautifulSoup
import os

# Create a folder to hold the article pages
os.makedirs('articles', exist_ok=True)

# The "disguise" - pretending to be a real web browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Fetch the specific Prothom Alo Motamot (Opinion) page
motamot_url = "https://www.prothomalo.com/collection/opinion-all"
response = requests.get(motamot_url, headers=headers)
soup_main = BeautifulSoup(response.content, 'html.parser')

# Start building the main index page
html_index = "<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Motamot</title></head><body><h1>Motamot (Opinions)</h1><ul>"

count = 0
seen_links = set() # This prevents duplicate articles if the same link appears twice

# Find all links on the Motamot page
for a_tag in soup_main.find_all('a', href=True):
    link = a_tag['href']
    
    # Make sure the link is a full URL
    if link.startswith('/'):
        link = "https://www.prothomalo.com" + link
        
    # Filter to only grab opinion articles that we haven't seen yet
    if '/opinion/' in link and link not in seen_links:
        title = a_tag.get_text().strip()
        
        # Skip empty titles or tiny UI text
        if len(title) < 10:
            continue
            
        if count >= 15: # Grab the top 15 articles
            break
            
        seen_links.add(link)
        
        try:
            # Fetch the actual opinion piece
            art_res = requests.get(link, headers=headers)
            soup_art = BeautifulSoup(art_res.content, 'html.parser')
            
            # Extract only paragraph text
            paragraphs = soup_art.find_all('p')
            article_text = ""
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 20: 
                    article_text += f"<p>{text}</p>"
                    
            if not article_text:
                continue # Skip if no text was found
                
            # Save the clean article as its own HTML file
            safe_filename = f"motamot_{count}.html"
            with open(f"articles/{safe_filename}", "w", encoding="utf-8") as f:
                f.write(f"<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title}</title></head><body>")
                f.write(f"<a href='../index.html'>&laquo; Back to Motamot</a><hr><h1>{title}</h1>")
                f.write(article_text)
                f.write("<hr><a href='../index.html'>&laquo; Back to Motamot</a></body></html>")
                
            # Add a link to the main index page
            html_index += f"<li><a href='articles/{safe_filename}'>{title}</a><br><br></li>"
            count += 1
            
        except Exception as e:
            print(f"Failed to fetch article {link}: {e}")
            continue

html_index += "</ul></body></html>"

# Save the main index page
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_index)
