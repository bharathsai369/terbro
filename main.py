#!/usr/bin/env python3
import sys
import hashlib
import json
import argparse
import requests
import textwrap
import shutil
import re
import io
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

# --- CONFIG & DIRECTORIES ---
CACHE_DIR = Path.home() / ".cache" / "terbro"
HIST_DIR = Path.home() / ".local" / "share" / "terbro"
HISTORY_FILE = HIST_DIR / "history.json"

# Optional: Try importing PIL for ASCII images
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

for d in [CACHE_DIR, HIST_DIR]: 
    d.mkdir(parents=True, exist_ok=True)

class Bcolors:
    HEADER = '\033[95m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

# --- UTILS ---
def die(msg, code=3):
    print(f"{Bcolors.RED}error:{Bcolors.ENDC} {msg}", file=sys.stderr)
    sys.exit(code)

def get_term_width():
    # Get terminal size, default to 80 if failing
    return shutil.get_terminal_size((80, 24)).columns

def sanitize(text):
    # Security: Remove existing ANSI codes from web content to prevent injection
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def image_to_ascii(url, width=60):
    if not HAS_PIL:
        return f"[Image: {url} (Install 'pillow' to view)]"
    
    try:
        resp = requests.get(url, stream=True, timeout=5)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content))
        
        # Calculate aspect ratio
        aspect_ratio = img.height / img.width
        # Terminal characters are roughly twice as tall as they are wide
        new_height = int(width * aspect_ratio * 0.55)
        img = img.resize((width, new_height))
        img = img.convert('L') # Grayscale

        pixels = img.getdata()
        chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
        new_pixels = [chars[pixel // 25] for pixel in pixels]
        new_pixels = ''.join(new_pixels)
        
        # Split string of chars into multiple strings of length equal to new width and create a list
        new_pixels_count = len(new_pixels)
        ascii_image = [new_pixels[index:index + width] for index in range(0, new_pixels_count, width)]
        return "\n".join(ascii_image)
    except Exception as e:
        return f"[Image Error: {url}]"

# --- LOGIC ---
def fetch_content(url, refresh=False, offline=False):
    # Security: Validate URL scheme
    if not url.startswith(('http://', 'https://')):
        if not url.startswith('http'):
            url = 'https://' + url

    cache_key = hashlib.sha256(url.encode()).hexdigest()
    cache_path = CACHE_DIR / cache_key
    
    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding='utf-8'), url
    
    if offline: 
        die("Offline mode: No cached version found.", 2)

    try:
        r = requests.get(url, headers={"User-Agent": "Terbro/2.1"}, timeout=10)
        r.raise_for_status()
        cache_path.write_text(r.text, encoding='utf-8')
        return r.text, r.url # Return final URL in case of redirects
    except Exception as e:
        if cache_path.exists():
            print(f"{Bcolors.YELLOW}Warning: Refresh failed. Showing cached version.{Bcolors.ENDC}", file=sys.stderr)
            return cache_path.read_text(encoding='utf-8'), url
        die(f"Network failure: {e}", 2)

def process(html, current_url, args):
    soup = BeautifulSoup(html, "html.parser")
    title = sanitize(soup.title.string.strip()) if soup.title else "Untitled Article"
    
    # Cleaning
    for tag in soup(["script", "style", "nav", "footer", "aside", "header", "form", "button", "iframe"]):
        tag.decompose()

    candidates = soup.find_all(["main", "article", "section", "div"])
    main_body = max(candidates, key=lambda t: len(t.get_text(strip=True)), default=soup)
    
    output = []
    links_found = [] # Stores tuples: (url, text)

    # Dynamic Width Calculation
    term_width = get_term_width()
    wrap_width = min(term_width - 4, 100) # Cap at 100 for readability, but fill small screens

    # 1. Title Banner
    output.append(f"{Bcolors.BOLD}{Bcolors.HEADER}{title.upper()}{Bcolors.ENDC}")
    output.append("=" * min(len(title), wrap_width) + "\n")

    # 2. Content Processing
    # We iterate over tags. If we are in interactive mode, we extract links.
    for tag in main_body.find_all(["h1", "h2", "h3", "p", "li", "blockquote", "img"]):
        
        # Image Handling
        if tag.name == 'img':
            if args.images:
                src = tag.get("src") or tag.get("data-src")
                if src:
                    # Resolve relative URLs
                    if src.startswith('/'):
                        from urllib.parse import urljoin
                        src = urljoin(current_url, src)
                    
                    output.append(f"\n{Bcolors.YELLOW}-- IMAGE --{Bcolors.ENDC}")
                    output.append(image_to_ascii(src, width=min(60, wrap_width)))
                    output.append(f"{Bcolors.YELLOW}-----------{Bcolors.ENDC}\n")
            continue

        # Text Handling
        txt = sanitize(tag.get_text(" ", strip=True))
        if not txt: continue

        # Link Extraction (Only if text contains links and we aren't in pure markdown mode)
        # This is a simple approximation. For strict link placement, we'd need recursive traversal.
        # Here we append found links to the bottom of the paragraph or replace them.
        
        display_text = txt
        
        if args.navigate:
            # Find links within this specific tag
            tag_links = tag.find_all("a", href=True)
            for link in tag_links:
                href = link['href']
                # Resolve relative URLs
                if not href.startswith(('http', 'mailto')):
                    from urllib.parse import urljoin
                    href = urljoin(current_url, href)
                
                link_text = sanitize(link.get_text(strip=True))
                if not link_text: link_text = "Link"

                links_found.append({'url': href, 'text': link_text})
                idx = len(links_found)
                
                # Replace text in display (Naive replacement, but effective for reading)
                # We use a unique marker to avoid replacing common words
                # OSC 8 Hyperlink support: \033]8;;URL\033\\TEXT\033]8;;\033\\
                # Plus the visual index [N]
                clickable = f"\033]8;;{href}\033\\{link_text}\033]8;;\033\\"
                marker = f"{clickable} {Bcolors.BLUE}[{idx}]{Bcolors.ENDC}"
                
                # Try to replace the exact text in the parent string
                # This can be buggy if link text is repeated, but good enough for CLI
                display_text = display_text.replace(link_text, marker, 1)

        # Formatting
        if args.markdown:
            if tag.name.startswith("h"): output.append(f"{'#' * int(tag.name[1])} {txt}\n")
            elif tag.name == "blockquote": output.append(f"> {txt}\n")
            else: output.append(f"{txt}\n")
        else:
            if tag.name.startswith("h"):
                output.append(f"\n{Bcolors.BOLD}{Bcolors.CYAN}{txt.upper()}{Bcolors.ENDC}")
            elif tag.name == "blockquote":
                wrapped = textwrap.fill(display_text, width=wrap_width - 4)
                output.append("\n".join(f"    {Bcolors.YELLOW}│{Bcolors.ENDC} {line}" for line in wrapped.splitlines()))
            elif tag.name == "li":
                # Handle list indentation
                wrapper = textwrap.TextWrapper(width=wrap_width, initial_indent="  • ", subsequent_indent="    ")
                output.append(wrapper.fill(display_text))
            else:
                # Standard paragraph
                # Note: textwrap breaks ANSI codes, so we have to be careful.
                # Since we inserted ANSI for links, textwrap might count them as length.
                # We use a simple wrap here, knowing it might be slightly ragged with ANSI links.
                output.append(textwrap.fill(display_text, width=wrap_width))
            
            output.append("")

    return "\n".join(output), title, links_found

def save_history(url, title):
    h_data = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f: 
            try: h_data = json.load(f)
            except: h_data = []
    
    # Remove duplicates (move to top)
    h_data = [h for h in h_data if h['url'] != url]
    h_data.insert(0, {"url": url, "title": title, "date": datetime.now().isoformat()})
    
    with open(HISTORY_FILE, "w") as f: 
        json.dump(h_data[:100], f, indent=2)

def interactive_history():
    if not HISTORY_FILE.exists(): return None
    with open(HISTORY_FILE, "r") as f: data = json.load(f)
    
    print(f"\n{Bcolors.BOLD}--- HISTORY ---{Bcolors.ENDC}")
    for i, entry in enumerate(data[:20], 1):
        print(f"{Bcolors.YELLOW}[{i}]{Bcolors.ENDC} {entry['title']}")
        print(f"    {Bcolors.CYAN}{entry['url']}{Bcolors.ENDC}")
    
    try:
        sel = input(f"\n{Bcolors.BOLD}Select # (or Enter to cancel): {Bcolors.ENDC}")
        if not sel: return None
        idx = int(sel) - 1
        if 0 <= idx < len(data):
            return data[idx]['url']
    except ValueError:
        pass
    return None

def manage_cache(limit=100):
    files = sorted(CACHE_DIR.glob('*'), key=lambda x: x.stat().st_mtime)
    if len(files) > limit:
        for f in files[:len(files) - limit]:
            f.unlink()

def main():
    parser = argparse.ArgumentParser(prog="terbro")
    parser.add_argument("url", nargs="?", help="URL to read")
    parser.add_argument("--markdown", action="store_true", help="Output as Markdown")
    parser.add_argument("--images", action="store_true", help="Attempt to render images (ASCII)")
    parser.add_argument("--save", metavar="FILE", help="Save output to file")
    parser.add_argument("--offline", action="store_true", help="Use cache only")
    parser.add_argument("--refresh", action="store_true", help="Force network fetch")
    parser.add_argument("--navigate", action="store_true", help="Interactive navigation mode")
    parser.add_argument("--history", action="store_true", help="View/Select from history")
    parser.add_argument("--clear", action="store_true", help="Clear cache")

    args = parser.parse_args()

    if args.clear:
        for f in CACHE_DIR.glob('*'): f.unlink()
        print("Cache cleared.")
        return

    # Initial URL resolution
    url = args.url
    
    # History Mode (Standalone)
    if args.history and not url:
        url = interactive_history()
        if not url: sys.exit(0)
        # If user selected from history, assume they want to read it.
        # If they used --navigate flag alongside --history, we enter the loop.
    
    if not url:
        parser.print_help()
        sys.exit(0)

    # --- MAIN LOOP (for navigation) ---
    history_stack = []
    
    while True:
        # Fetch
        print(f"{Bcolors.GREEN}Loading...{Bcolors.ENDC}")
        html, final_url = fetch_content(url, args.refresh, args.offline)
        
        # Process
        content, title, links = process(html, final_url, args)
        save_history(final_url, title)
        
        # If not interactive, just print and exit
        if not args.navigate:
            if args.save:
                with open(args.save, "w") as f: f.write(content)
                print(f"Saved to {args.save}")
            else:
                sys.stdout.write(content + "\n")
            break

        # Interactive Display
        # We clear screen for a "browser" feel, or just print separators
        print("\033c", end="") # Clear terminal
        print(content)
        
        print("-" * get_term_width())
        print(f" {Bcolors.BOLD}Current:{Bcolors.ENDC} {title}")
        print(f" {Bcolors.CYAN}{final_url}{Bcolors.ENDC}")
        print("-" * get_term_width())
        
        # Prompt
        try:
            cmd = input(f"{Bcolors.BOLD}>> [Number] to go, (B)ack, (H)istory, (R)eload, (Q)uit: {Bcolors.ENDC}").strip().lower()
        except EOFError:
            break

        if cmd == 'q':
            break
        elif cmd == 'b':
            if history_stack:
                url = history_stack.pop()
                continue
            else:
                print("No history back.")
                input("Press Enter...")
        elif cmd == 'h':
            new_url = interactive_history()
            if new_url:
                history_stack.append(final_url)
                url = new_url
        elif cmd == 'r':
            args.refresh = True # Force refresh next loop
            continue
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(links):
                history_stack.append(final_url)
                url = links[idx]['url']
                args.refresh = False # Reset refresh
            else:
                print("Invalid link number.")
                input("Press Enter...")
        else:
            # Check if user typed a new URL directly
            if "." in cmd:
                history_stack.append(final_url)
                url = cmd if cmd.startswith("http") else "https://" + cmd

    manage_cache()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        die(f"Unexpected error: {e}")