import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re   # moved up (good practice: all imports top)


url = input("URL: ")

parsed = urlparse(url)
if parsed.scheme not in ("http", "https"):
    raise ValueError("Invalid URL scheme")

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ReaderCLI/1.0"
}

# resp = requests.get(url, headers=headers, timeout=10)
# ↑ Good but lacks security checks and size checks

resp = requests.get(
    url,
    headers=headers,           # FIX: actually use headers
    timeout=10,
    allow_redirects=True,
    stream=True                # stream so we can inspect headers before downloading
)

# Some servers don't send content-length → default 0 is fine
if int(resp.headers.get("content-length", 0)) > 5_000_000:
    raise ValueError("Page too large")

# content-type may contain charset, e.g. text/html; charset=utf-8
if "text/html" not in resp.headers.get("content-type", "").lower():
    raise ValueError("Not HTML")

resp.raise_for_status()

# html = resp.text
# ↑ BAD: this downloads whole thing ignoring encoding detection

resp.encoding = resp.apparent_encoding  # better decoding guess
html = resp.text


# html = requests.get(url).text
# ↑ Old unsafe version (no timeout / headers / validation)


soup = BeautifulSoup(html, "html.parser")

# Remove scripts/styles
for script in soup(["script", "style"]):
    script.decompose()


# Prefer semantic article tag
# article = soup.find("article")
# if article:
#     soup = article


# Heuristic: choose largest readable container
candidates = soup.find_all(["main", "section", "div"], recursive=True)

best = max(
    candidates,
    key=lambda tag: len(tag.get_text(strip=True)),
    default=soup
)
soup = best


# Remove navigation garbage
for tag in soup(["nav", "footer", "aside", "header", "form", "button"]):
    tag.decompose()


def extract_text(node):
    """Structured extraction — keeps readability"""
    for tag in node.find_all(["h1", "h2", "h3", "p", "li", "blockquote"]):
        print(tag.get_text(strip=True))
        print()


# text = re.sub(r'\n{3,}', '\n\n', text)
# text = re.sub(r'[ \t]{2,}', ' ', text)
# ↑ BUG: text not defined yet — moved AFTER extraction


# text = soup.get_text()
# ↑ This destroys structure — keep but comment as fallback


# --- STRUCTURED OUTPUT (better readability) ---
extract_text(soup)


# --- FLAT TEXT FALLBACK (your original behavior) ---
text = soup.get_text()

lines = (line.strip() for line in text.splitlines())
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
text = '\n'.join(chunk for chunk in chunks if chunk)

# now safe to normalize
text = re.sub(r'\n{3,}', '\n\n', text)
text = re.sub(r'[ \t]{2,}', ' ', text)

# print("\n--- RAW TEXT MODE ---\n")
# print(text)
