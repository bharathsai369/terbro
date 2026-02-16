#!/usr/bin/env python3

import sys
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


# -------- CLI ARG --------
if len(sys.argv) < 2:
    print("Usage: terbro <url>")
    sys.exit(1)

url = sys.argv[1]


# -------- VALIDATION --------
parsed = urlparse(url)
if parsed.scheme not in ("http", "https"):
    raise ValueError("Invalid URL scheme")


# -------- FETCH --------
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Terbro/1.0"
}

resp = requests.get(
    url,
    headers=headers,
    timeout=10,
    allow_redirects=True,
    stream=True
)

if int(resp.headers.get("content-length", 0)) > 5_000_000:
    raise ValueError("Page too large")

if "text/html" not in resp.headers.get("content-type", "").lower():
    raise ValueError("Not HTML")

resp.raise_for_status()

resp.encoding = resp.apparent_encoding
html = resp.text


# -------- PARSE --------
soup = BeautifulSoup(html, "html.parser")

# remove junk
for tag in soup(["script", "style", "nav", "footer", "aside", "header", "form", "button"]):
    tag.decompose()


# -------- FIND MAIN CONTENT --------
candidates = soup.find_all(["main", "section", "div"], recursive=True)

best = max(
    candidates,
    key=lambda tag: len(tag.get_text(strip=True)),
    default=soup
)

soup = best


# -------- EXTRACT STRUCTURED TEXT --------
output = []

for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "blockquote"]):
    txt = tag.get_text(" ", strip=True)
    if txt:
        output.append(txt)
        output.append("")


text = "\n".join(output)

# normalize whitespace
text = re.sub(r'\n{3,}', '\n\n', text)
text = re.sub(r'[ \t]{2,}', ' ', text)


# -------- OUTPUT FOR PAGER --------
sys.stdout.write(text)
