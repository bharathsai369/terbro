#!/usr/bin/env python3
import sys
import hashlib
import json
import argparse
import requests
import textwrap
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import os

# --- CONFIG & DIRECTORIES ---
CACHE_DIR = Path.home() / ".cache" / "terbro"
HIST_DIR = Path.home() / ".local" / "share" / "terbro"
HISTORY_FILE = HIST_DIR / "history.json"

for d in [CACHE_DIR, HIST_DIR]: 
    d.mkdir(parents=True, exist_ok=True)

class Bcolors:
    HEADER = '\033[95m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def die(msg, code=3):
    print(f"{Bcolors.RED}error:{Bcolors.ENDC} {msg}", file=sys.stderr)
    sys.exit(code)

# --- LOGIC ---
def fetch_content(url, refresh=False, offline=False):
    cache_path = CACHE_DIR / hashlib.sha256(url.encode()).hexdigest()
    
    # 1. Check if we can just use the cache
    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding='utf-8')
    
    if offline: 
        die("Offline mode: No cached version found.", 2)

    try:
        r = requests.get(url, headers={"User-Agent": "Terbro/2.0"}, timeout=10)
        r.raise_for_status()
        
        # Only write to disk if we got a 200 OK
        cache_path.write_text(r.text, encoding='utf-8')
        return r.text
    except Exception as e:
        # 2. Friendly Fallback: If refresh fails, try to show the old cache anyway
        if cache_path.exists():
            print(f"{Bcolors.YELLOW}Warning: Refresh failed. Showing cached version.{Bcolors.ENDC}", file=sys.stderr)
            return cache_path.read_text(encoding='utf-8')
        die(f"Network failure: {e}", 2)

def process(html, args):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else "Untitled Article"
    
    # Cleaning
    for tag in soup(["script", "style", "nav", "footer", "aside", "header", "form", "button"]):
        tag.decompose()

    # Find main content
    candidates = soup.find_all(["main", "article", "section", "div"])
    main_body = max(candidates, key=lambda t: len(t.get_text(strip=True)), default=soup)
    
    output = []
    
    # 1. Title Banner
    output.append(f"{Bcolors.BOLD}{Bcolors.HEADER}{title.upper()}{Bcolors.ENDC}")
    output.append("=" * len(title) + "\n")

    # 2. Image Extraction
    if args.images:
        output.append(f"{Bcolors.BOLD}[ IMAGES ]{Bcolors.ENDC}")
        found_imgs = False
        # Checking 'src' and 'data-src' for lazy-loaded images
        for i, img in enumerate(main_body.find_all("img"), 1):
            src = img.get("src") or img.get("data-src")
            if src:
                alt = img.get("alt", "no description")
                output.append(f"  {i}. {Bcolors.YELLOW}{src}{Bcolors.ENDC}\n     Alt: {alt}")
                found_imgs = True
        if not found_imgs: output.append("  (No images found)")
        output.append("\n" + "-"*40 + "\n")

    # 3. Text Formatting
    for tag in main_body.find_all(["h1", "h2", "h3", "p", "li", "blockquote"]):
        txt = tag.get_text(" ", strip=True)
        if not txt: continue

        if args.markdown:
            if tag.name.startswith("h"): output.append(f"{'#' * int(tag.name[1])} {txt}\n")
            elif tag.name == "blockquote": output.append(f"> {txt}\n")
            else: output.append(f"{txt}\n")
        else:
            if tag.name.startswith("h"):
                output.append(f"\n{Bcolors.BOLD}{Bcolors.CYAN}{txt.upper()}{Bcolors.ENDC}")
            elif tag.name == "blockquote":
                wrapped = textwrap.fill(txt, width=76)
                output.append("\n".join(f"    {Bcolors.YELLOW}│{Bcolors.ENDC} {line}" for line in wrapped.splitlines()))
            elif tag.name == "li":
                output.append(f"  • {textwrap.fill(txt, width=78, subsequent_indent='    ')}")
            else:
                output.append(textwrap.fill(txt, width=80))
            output.append("")

    return "\n".join(output), title

def handle_history(query=None):
    if not HISTORY_FILE.exists(): 
        print("No history recorded yet.")
        return
    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)
    if query:
        data = [h for h in data if query.lower() in h['title'].lower() or query.lower() in h['url'].lower()]
    
    print(f"{Bcolors.BOLD}RECENT ARTICLES:{Bcolors.ENDC}")
    for i, entry in enumerate(data[:20]):
        print(f"[{i}] {Bcolors.CYAN}{entry['title']}{Bcolors.ENDC}\n    {entry['url']}")

# New Function: Cache Maintenance
def manage_cache(limit=100):
    """Removes the oldest files if the cache exceeds the limit."""
    files = sorted(CACHE_DIR.glob('*'), key=lambda x: x.stat().st_mtime)
    if len(files) > limit:
        for f in files[:len(files) - limit]:
            f.unlink()

def clear_cache():
    """Force deletes everything in the cache folder."""
    for f in CACHE_DIR.glob('*'):
        f.unlink()
    print(f"{Bcolors.YELLOW}Cache cleared.{Bcolors.ENDC}")


def main():
    parser = argparse.ArgumentParser(prog="terbro", description="Terbro: Terminal Reader")
    parser.add_argument("url", nargs="?", help="URL to read")
    parser.add_argument("--markdown", action="store_true", help="Output as Markdown")
    parser.add_argument("--images", action="store_true", help="List images found in article")
    parser.add_argument("--save", metavar="FILE", help="Save output to file")
    parser.add_argument("--offline", action="store_true", help="Use cache only")
    parser.add_argument("--refresh", action="store_true", help="Force network fetch")
    parser.add_argument("--history", action="store_true", help="Show history")
    parser.add_argument("--search", metavar="QUERY", help="Search history")
    parser.add_argument("--clear", action="store_true", help="Delete all cached articles")

    args = parser.parse_args()

    # History Logic
    if args.history or args.search:
        handle_history(args.search)
        return

    # Clear cache logic
    if args.clear:
        clear_cache()
        return

    # Trigger auto-clean every time you fetch a new article
    manage_cache(limit=100)

    # Help Logic
    if not args.url:
        parser.print_help()
        sys.exit(0)

    html = fetch_content(args.url, args.refresh, args.offline)
    content, title = process(html, args)

    # Save to history file
    h_data = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f: h_data = json.load(f)
    h_data = [h for h in h_data if h['url'] != args.url]
    h_data.insert(0, {"url": args.url, "title": title, "date": datetime.now().isoformat()})
    with open(HISTORY_FILE, "w") as f: json.dump(h_data[:100], f, indent=2)

    # Output
    if args.save:
        with open(args.save, "w") as f: f.write(content)
        print(f"File saved to: {args.save}")
    else:
        sys.stdout.write(content + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        die(f"unexpected error: {e}")