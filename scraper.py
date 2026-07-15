import requests
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET

# Create a folder to hold the article pages
os.makedirs('articles', exist_ok=True)

# Fetch the Prothom Alo RSS Feed
rss_url = "https://www.prothomalo.com/feed/"
response = requests.get(rss_url)
root = ET.fromstring(response.content)

# Start building the main index page
html_index = "<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Simple News</title></head><body><h1>Latest Headlines</h1><ul>"

count = 0
for item in root.findall('.//item'):
    if count >= 15: # Grab the top 15 articles
        break
    title = item.find('title').text
    link = item.find('link').text
    
    try:
        # Fetch the actual article page
        art_res = requests.get(link)
        soup = BeautifulSoup(art_res.content, 'html.parser')
        
        # Extract only paragraph text
        paragraphs = soup.find_all('p')
        article_text = ""
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 20: # Skip tiny empty blocks
                article_text += f"<p>{text}</p>"
                
        # Save the clean article as its own HTML file
        safe_filename = f"article_{count}.html"
        with open(f"articles/{safe_filename}", "w", encoding="utf-8") as f:
            f.write(f"<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title}</title></head><body>")
            f.write(f"<a href='../index.html'>&laquo; Back to Headlines</a><hr><h1>{title}</h1>")
            f.write(article_text)
            f.write("<hr><a href='../index.html'>&laquo; Back to Headlines</a></body></html>")
            
        # Add a link to the main index page
        html_index += f"<li><a href='articles/{safe_filename}'>{title}</a><br><br></li>"
        count += 1
    except Exception as e:
        continue

html_index += "</ul></body></html>"

# Save the main index page
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_index)
