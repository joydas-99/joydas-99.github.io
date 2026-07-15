import cloudscraper
from bs4 import BeautifulSoup
import os
import re

# Create a folder to hold the article pages
os.makedirs('articles', exist_ok=True)

# Create a Cloudscraper instance to bypass the security wall
scraper = cloudscraper.create_scraper(browser={
    'browser': 'chrome',
    'platform': 'windows',
    'desktop': True
})

motamot_url = "https://www.prothomalo.com/opinion"
print(f"Fetching: {motamot_url}")

# Use the scraper instead of standard requests
response = scraper.get(motamot_url)
html_content = response.text

seen_links = set()
article_urls = []

print("Scanning for hidden links...")

# 1. Search for normal links
soup_main = BeautifulSoup(html_content, 'html.parser')
for a in soup_main.find_all('a', href=True):
    href = a['href']
    if '/opinion/' in href and '/author/' not in href:
        url = href if href.startswith('http') else "https://www.prothomalo.com" + href
        if url not in seen_links:
            seen_links.add(url)
            article_urls.append(url)

# 2. X-Ray Method: Search the hidden Javascript data package directly
slugs = re.findall(r'"slug":\s*"([^"]+)"', html_content)
for slug in slugs:
    if slug.startswith('opinion/') and '/author/' not in slug:
        url = "https://www.prothomalo.com/" + slug
        if url not in seen_links:
            seen_links.add(url)
            article_urls.append(url)

print(f"Found {len(article_urls)} potential articles.")

html_index = "<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Motamot</title></head><body><h1>Motamot (Opinions)</h1><ul>"

count = 0
for link in article_urls:
    if count >= 15:
        break
        
    print(f"Downloading: {link}")
    try:
        # Use the scraper to bypass security on the article page too
        art_res = scraper.get(link)
        soup_art = BeautifulSoup(art_res.content, 'html.parser')
        
        title_tag = soup_art.find('title')
        if not title_tag:
            continue
            
        title = title_tag.text.replace(' - Prothom Alo', '').replace('প্রথম আলো', '').strip()
        if title.endswith('-'):
            title = title[:-1].strip()
            
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
