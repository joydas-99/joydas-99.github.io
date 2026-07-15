import requests
from bs4 import BeautifulSoup
import os

# Create a folder to hold the article pages
os.makedirs('articles', exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# The hidden Prothom Alo Data API
api_url = "https://www.prothomalo.com/api/v1/stories?section=opinion&limit=15"

# Using a more reliable proxy (CodeTabs)
proxy_api_url = f"https://api.codetabs.com/v1/proxy?quest={api_url}"

print("Fetching links from the hidden Data API using CodeTabs proxy...")
response = requests.get(proxy_api_url, headers=headers)

# Adding a safety net to see exactly what the proxy returns if it fails
try:
    data = response.json()
except Exception as e:
    print(f"Failed to parse JSON. The proxy returned this instead:\n{response.text[:500]}")
    exit(1)

html_index = "<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Motamot</title></head><body><h1>Motamot (Opinions)</h1><ul>"

count = 0
for story in data.get('stories', []):
    if count >= 15:
        break
        
    title = story.get('headline', 'No Title')
    link = story.get('url', '')
    
    if not link:
        continue

    print(f"Downloading: {title}")
    
    try:
        # Route the article request through the new proxy as well
        proxy_art_url = f"https://api.codetabs.com/v1/proxy?quest={link}"
        art_res = requests.get(proxy_art_url, headers=headers, timeout=15)
        soup_art = BeautifulSoup(art_res.content, 'html.parser')
        
        paragraphs = soup_art.find_all('p')
        article_text = ""
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 30: 
                article_text += f"<p>{text}</p>"
                
        if not article_text:
            print(" -> Failed: No text found in this link.")
            continue
            
        safe_filename = f"motamot_{count}.html"
        with open(f"articles/{safe_filename}", "w", encoding="utf-8") as f:
            f.write(f"<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title}</title></head><body>")
            f.write(f"<a href='../index.html'>&laquo; Back to Motamot</a><hr><h1>{title}</h1>")
            f.write(article_text)
            f.write("<hr><a href='../index.html'>&laquo; Back to Motamot</a></body></html>")
            
        html_index += f"<li><a href='articles/{safe_filename}'>{title}</a><br><br></li>"
        count += 1
        print(" -> Success!")
        
    except Exception as e:
        print(f" -> Error: {e}")
        continue

html_index += "</ul></body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_index)

print(f"Finished! Processed {count} articles.")
