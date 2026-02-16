#!/usr/bin/env python3
import sys
import hashlib
import json
import argparse
import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

CACHE_DIR = Path.home() / ".cache" / "terbro"
HIST_DIR = Path.home() / ".local" / "share" / "terbro"
HISTORY_FILE = HIST_DIR / "history.json"

for d in [CACHE_DIR, HIST_DIR]: 
    d.mkdir(parents=True, exist_ok=True)

class Bcolors:
    HEADER, BOLD, CYAN, YELLOW, RED, GREEN, BLUE, ENDC = (
        '\033[95m', '\033[1m', '\033[96m', '\033[93m', 
        '\033[91m', '\033[92m', '\033[94m', '\033[0m'
    )

def die(msg, code=3):
    print(f"{Bcolors.RED}error:{Bcolors.ENDC} {msg}", file=sys.stderr)
    sys.exit(code)

def sanitize(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def fetch_content(url, refresh=False, offline=False):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    cache_key = hashlib.sha256(url.encode()).hexdigest()
    cache_path = CACHE_DIR / cache_key
    
    # REFRESH LOGIC: If refresh is True, we skip the initial cache check
    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding='utf-8'), url
    
    if offline: 
        if cache_path.exists(): return cache_path.read_text(encoding='utf-8'), url
        die("Offline mode: No cached version found.", 2)

    try:
        r = requests.get(url, headers={"User-Agent": "Terbro/2.1"}, timeout=10)
        r.raise_for_status()
        cache_path.write_text(r.text, encoding='utf-8')
        return r.text, r.url 
    except Exception as e:
        if cache_path.exists():
            return cache_path.read_text(encoding='utf-8'), url
        die(f"Network failure: {e}", 2)

def process(html, current_url, args):
    soup = BeautifulSoup(html, "html.parser")
    title = sanitize(soup.title.string.strip()) if soup.title else "Untitled Article"
    for tag in soup(["script", "style", "nav", "footer", "aside", "header", "form", "button", "iframe"]):
        tag.decompose()

    candidates = soup.find_all(["main", "article", "section", "div"])
    main_body = max(candidates, key=lambda t: len(t.get_text(strip=True)), default=soup)
    
    output = [f"{Bcolors.BOLD}{Bcolors.HEADER}{title.upper()}{Bcolors.ENDC}\n"]
    for tag in main_body.find_all(["h1", "h2", "h3", "p", "li", "blockquote", "img"]):
        if tag.name == 'img':
            if args.images:
                src = tag.get("src") or tag.get("data-src")
                if src:
                    src = urljoin(current_url, src)
                    output.append(f"{Bcolors.YELLOW}[IMAGE: {src}]{Bcolors.ENDC}")
            continue
        txt = sanitize(tag.get_text(" ", strip=True))
        if not txt: continue
        if tag.name.startswith("h"):
            output.append(f"\n{Bcolors.BOLD}{Bcolors.CYAN}{txt.upper()}{Bcolors.ENDC}")
        elif tag.name == "blockquote":
            output.append(f"    {Bcolors.YELLOW}│{Bcolors.ENDC} {txt}")
        elif tag.name == "li":
            output.append(f"  • {txt}")
        else:
            output.append(txt)
        output.append("")
    return "\n".join(output), title

def save_history(url, title):
    h_data = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r") as f: h_data = json.load(f)
        except: h_data = []
    h_data = [h for h in h_data if h['url'] != url]
    h_data.insert(0, {"url": url, "title": title, "date": datetime.now().isoformat()})
    with open(HISTORY_FILE, "w") as f: json.dump(h_data[:100], f, indent=2)

def interactive_history():
    if not HISTORY_FILE.exists():
        print("No history found.", file=sys.stderr)
        return None
    with open(HISTORY_FILE, "r") as f:
        try: data = json.load(f)
        except: return None
    
    print(f"\n{Bcolors.BOLD}--- HISTORY ---{Bcolors.ENDC}", file=sys.stderr)
    for i, entry in enumerate(data[:20], 1):
        print(f"{Bcolors.YELLOW}[{i}]{Bcolors.ENDC} {entry['title']}", file=sys.stderr)
        print(f"    {Bcolors.CYAN}{entry['url']}{Bcolors.ENDC}", file=sys.stderr)
    
    try:
        sys.stderr.write(f"\n{Bcolors.BOLD}Select # (or Enter to cancel): {Bcolors.ENDC}")
        sys.stderr.flush()
        with open('/dev/tty', 'r') as tty:
            sel = tty.readline().strip()
        if not sel: return None
        idx = int(sel) - 1
        if 0 <= idx < len(data):
            return data[idx]['url']
    except:
        pass
    return None

def main():
    parser = argparse.ArgumentParser(prog="terbro")
    parser.add_argument("url", nargs="?", help="URL to read")
    parser.add_argument("--images", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()

    if args.clear:
        for f in CACHE_DIR.glob('*'): f.unlink()
        print(f"{Bcolors.GREEN}Cache cleared successfully.{Bcolors.ENDC}")
        return

    if args.history:
        selected = interactive_history()
        if selected:
            # We print the selected URL to STDOUT so the Bash wrapper can catch it
            print(selected)
        return

    if not args.url:
        parser.print_help()
        return

    html, final_url = fetch_content(args.url, args.refresh, args.offline)
    content, title = process(html, final_url, args)
    save_history(final_url, title)
    sys.stdout.write(content + "\n")

if __name__ == "__main__":
    main()