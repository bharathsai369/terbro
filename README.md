

````md
# terbro — Terminal Browser Reader

`terbro` is a small CLI tool that turns any webpage into a clean, readable
man-page style reading session inside the terminal.

Instead of opening a browser, the page is fetched, cleaned, and displayed
through a pager (`less`) so you can scroll, search and read comfortably.

---

## Features

- Read webpages inside terminal
- Removes navigation, ads and scripts
- Extracts main article content heuristically
- Man-page like navigation (via `less`)
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
 └─ tbr-env/ (created later)
```

---

### 2) Create virtual environment

Inside project directory:

```bash
python3 -m venv tbr-env
source tbr-env/bin/activate
pip install requests beautifulsoup4
or
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

if [ -z "$1" ]; then
    echo "Usage: terbro <url>"
    exit 1
fi

"$PY" "$SCRIPT" "$1" | less -R -M -i
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

```bash
terbro <url>
```

Example:

```bash
terbro https://en.wikipedia.org/wiki/Linux
```

The page opens in a terminal reading session.

Quit with:

```
q
```

---

## How It Works

1. Bash command runs Python inside virtual environment
2. Python downloads webpage safely
3. HTML is parsed using BeautifulSoup
4. Scripts/navigation removed
5. Largest readable content block selected
6. Clean text piped to `less`

```
terbro → bash → python → clean text → less pager
```

---

## Security Measures

The reader performs basic safety checks:

* Only http/https URLs allowed
* Content-type must be HTML
* Max page size limit (5MB)
* Timeout on requests
* Custom user agent

---

## Project Structure

```
terbro/
├── main.py          # reader engine
├── tbr-env/         # virtual environment
└── README.md

~/bin/
└── terbro           # command launcher
```

---
