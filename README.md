
---

````md
# terbro — Terminal Browser Reader

`terbro` is a small CLI tool that turns any webpage into a clean, readable
man-page style reading session inside the terminal.

Instead of opening a browser, the page is fetched, cleaned, cached and displayed
through a pager (`less`) so you can scroll, search and read comfortably — even offline.

---

## Features

- Read webpages inside terminal
- Removes navigation, ads and scripts
- Extracts main article content heuristically
- Man-page like navigation (via `less`)
- Automatic pager integration
- Page caching for offline reading
- History system (reopen previously read pages)
- Markdown export
- Image link listing
- Refresh cached pages
- Clear cache
- Runs in isolated Python virtual environment
- Simple one-command usage

---

## Demo (concept)

```bash
terbro https://example.com
````

You get a reading interface similar to `man`:

| Key   | Action        |
| ----- | ------------- |
| Space | next page     |
| b     | previous page |
| /word | search        |
| n     | next match    |
| g     | top           |
| G     | bottom        |
| q     | quit          |

---

## Requirements

* Linux / macOS terminal
* Python 3.9+
* bash
* `less`

Install less if missing:

```bash
sudo dnf install less        # Fedora
sudo apt install less        # Debian/Ubuntu
```

---

## Installation

### 1) Clone project

```bash
git clone <repo-url> terbro
cd terbro
```

Or place files manually so structure becomes:

```
terbro/
 ├─ main.py
 ├─ README.md
 ├─ terbro (launcher script)
 └─ tbr-env/ (created later)
```

---

### 2) Create virtual environment

Inside project directory:

```bash
python3 -m venv tbr-env
source tbr-env/bin/activate
pip install requests beautifulsoup4
# OR
pip install -r requirements.txt
deactivate
```

This installs dependencies locally (no system pollution).

---

### 3) Create command

Create user command directory if missing:

```bash
mkdir -p ~/bin
```

Create file:

```
~/bin/terbro
```

Paste:

```bash
#!/usr/bin/env bash

APP="$HOME/Documents/workspace/terbro"
VENV="$APP/tbr-env"
PY="$VENV/bin/python"
SCRIPT="$APP/main.py"

# 1. Clear Cache/Save Mode - No pager
if [[ "$*" == *"--clear"* ]] || [[ "$*" == *"--save"* ]]; then
    "$PY" "$SCRIPT" "$@"
    exit 0
fi

# 2. History Mode - Interactive
if [[ "$*" == *"--history"* ]]; then
    SELECTED_URL=$("$PY" "$SCRIPT" --history)
    if [ -n "$SELECTED_URL" ]; then
        "$PY" "$SCRIPT" "$SELECTED_URL" | less -R -i -M
    fi
    exit 0
fi

# 3. Help
if [[ "$*" == *"-h"* ]] || [[ "$*" == *"--help"* ]] || [ -z "$1" ]; then
    "$PY" "$SCRIPT" --help
    exit 0
fi

# 4. Standard Usage
"$PY" "$SCRIPT" "$@" | less -R -i -M
```

Make executable:

```bash
chmod +x ~/bin/terbro
```

Add to PATH:

```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Usage

### Basic reading

```bash
terbro <url>
```

Example:

```bash
terbro https://en.wikipedia.org/wiki/Linux
```

---

### Markdown export

```bash
terbro https://example.com --markdown
```

---

### Save article

```bash
terbro https://example.com --save article.txt
terbro https://example.com --markdown --save article.md
```

---

### Offline mode

Reads cached version only:

```bash
terbro https://example.com --offline
```

---

### Refresh cache

```bash
terbro https://example.com --refresh
```

---

### Show image links

```bash
terbro https://example.com --images
```

---

### History

Reopen previously read pages interactively:

```bash
terbro --history
```

---

### Clear cache

```bash
terbro --clear
```

---

Quit reader with:

```
q
```

---

## How It Works

1. Bash command runs Python inside virtual environment
2. Python downloads webpage safely (or loads cache)
3. HTML is parsed using BeautifulSoup
4. Scripts/navigation removed
5. Largest readable content block selected
6. Clean text piped to `less`

```
terbro → bash → python → clean text → less pager
```

---

## Storage Locations

Cache:

```
~/.cache/terbro/
```

History:

```
~/.local/share/terbro/history.json
```

---

## Security Measures

The reader performs basic safety checks:

* Only http/https URLs allowed
* Timeout on requests
* Graceful fallback to cached copy if network fails
* ANSI escape sanitization before saving

---

## Project Structure

```
terbro/
├── main.py          # reader engine
├── terbro           # launcher script
├── tbr-env/         # virtual environment
└── README.md

~/bin/
└── terbro           # command launcher
```

---

