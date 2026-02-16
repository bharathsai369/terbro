#!/usr/bin/env python3
import sys
import re
import os
import hashlib
import json
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
CACHE_DIR = Path.home() / ".cache" / "terbro"
HISTORY_FILE = Path.home() / ".local" / "share" / "terbro" / "history.json"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

# --- STYLING ---
class Bcolors:
    HEADER = '\033[95m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def log_error(msg):
    print(f"{Bcolors.FAIL}Error:{Bcolors.ENDC} {msg}", file=sys.stderr)

# --- CORE LOGIC ---
def get_cache_path(url):
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    return CACHE_DIR / f"{url_hash}.html"

def save_history(url, title):
    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    
    # Keep last 50 entries, remove duplicates
    history = [h for h in history if h['url'] != url]
    history.insert(0, {"url": url, "title": title, "date": datetime.now().isoformat()})
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[:50], f, indent=2)

def fetch_url(url, refresh=False, offline=False):
    cache_path = get_cache_path(url)
    
    if cache_path.exists() and not refresh:
        return cache_path.read_text()
    
    if offline:
        log_error("Offline mode enabled and page not in cache.")
        sys.exit(2)

    try:
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Terbro/2.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        # Save to cache
        cache_path.write_text(resp.text)
        return resp.text
    except requests.exceptions.RequestException as e:
        log_error(f"Network failure: {e}")
        sys.exit(2)

def process_content(html, mode="text", include_images=False):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string if soup.title else "Untitled Article"

    # Remove junk
    for tag in soup(["script", "style", "nav", "footer", "aside", "header", "form", "button"]):
        tag.decompose()

    # Heuristic for main content
    candidates = soup.find_all(["main", "article", "section", "div"])
    best = max(candidates, key=lambda t: len(t.get_text(strip=True)), default=soup)
    
    output = []
    images = []

    if mode == "images" or include_images:
        for img in best.find_all("img"):
            src = img.get("src")
            alt = img.get("alt", "No description")
            if src: images.append(f"[{alt}] -> {src}")

    if mode == "images":
        return "\n".join([f"[{i+1}] {img}" for i, img in enumerate(images)]), title

    # Extraction loop
    for tag in best.find_all(["h1", "h2", "h3", "p", "li", "blockquote"]):
        txt = tag.get_text(" ", strip=True)
        if not txt: continue

        if mode == "markdown":
            if tag.name.startswith("h"):
                level = "#" * int(tag.name[1])
                output.append(f"{level} {txt}\n")
            elif tag.name == "blockquote":
                output.append(f"> {txt}\n")
            elif tag.name == "li":
                output.append(f"* {txt}")
            else:
                output.append(f"{txt}\n")
        else:
            # Pager friendly with ANSI
            if tag.name.startswith("h"):
                output.append(f"{Bcolors.BOLD}{Bcolors.CYAN}{txt.upper()}{Bcolors.ENDC}\n" + "—" * len(txt))
            elif tag.name == "blockquote":
                output.append(f"    {Bcolors.YELLOW}│ {txt}{Bcolors.ENDC}")
            elif tag.name == "li":
                output.append(f"  • {txt}")
            else:
                output.append(txt)
            output.append("")

    return "\n".join(output), title

# --- CLI DEFINITION ---
def main():
    parser = argparse.ArgumentParser(description="Terbro: A terminal browser for reading.")
    parser.add_argument("url", nargs="?", help="URL to read")
    parser.add_argument("--markdown", action="store_true", help="Output in Markdown format")
    parser.add_argument("--save", metavar="FILE", help="Save output to a file")
    parser.add_argument("--images", action="store_true", help="List all images in the article")
    parser.add_argument("--offline", action="store_true", help="Only use cached version")
    parser.add_argument("--refresh", action="store_true", help="Force refresh cache")
    parser.add_argument("--history", action="store_true", help="Show reading history")
    parser.add_argument("--search", metavar="QUERY", help="Search history for a term")

    args = parser.parse_args()

    # Handle History/Search
    if args.history or args.search:
        if not HISTORY_FILE.exists():
            print("No history found.")
            return
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        
        if args.search:
            history = [h for h in history if args.search.lower() in h['title'].lower() or args.search.lower() in h['url'].lower()]
        
        for i, entry in enumerate(history):
            print(f"[{i}] {Bcolors.BOLD}{entry['title']}{Bcolors.ENDC}\n    {entry['url']}")
        return

    if not args.url:
        parser.print_help()
        sys.exit(1)

    # Fetch and Process
    html = fetch_url(args.url, refresh=args.refresh, offline=args.offline)
    
    mode = "markdown" if args.markdown else ("images" if args.images else "text")
    content, title = process_content(html, mode=mode)
    
    save_history(args.url, title)

    if args.save:
        with open(args.save, "w") as f:
            f.write(content)
        print(f"Saved to {args.save}")
    else:
        sys.stdout.write(content + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        log_error(f"An unexpected error occurred: {e}")
        sys.exit(3)