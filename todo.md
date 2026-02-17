
---

# TERBRO DEVELOPMENT ROADMAP

Think of it as stages:

**CLI → Reader → Offline Tool → Mini Browser → Knowledge Tool**

---

## Current Status (Implemented So Far)

TerBro is now a **real usable terminal article reader** with caching, history, markdown export, and pager integration.

You can already use it as:

```
terbro https://example.com
terbro https://example.com --markdown
terbro https://example.com --offline
terbro https://example.com --refresh
terbro https://example.com --images
terbro https://example.com --save article.txt
terbro --history
terbro --clear
```

It behaves like a lightweight `man`-style reader for web articles.

---

## 0. Foundation (Stability first)

Make the current tool solid before adding features.

* [x] Proper error handling (timeouts, DNS failure fallback to cache)
* [x] Friendly error messages
* [x] Exit codes (0 success / 2 network / 3 error)
* [ ] Config file `~/.config/terbro/config.json`
* [ ] Logging (debug mode `--debug`)

---

## 1. Real CLI Interface (turn script → program)

### Argument System (`argparse`)

Commands:

```
terbro URL
terbro URL --markdown
terbro URL --save article.txt
terbro URL --images
terbro URL --offline
terbro URL --refresh
terbro --history
terbro --clear
```

Tasks:

* [x] Replace sys.argv with argparse
* [x] Help page (`-h`)
* [x] Flags validation
* [x] Multiple output modes

---

## 2. Reading Experience (make it pleasant)

### Man-Page Style Reading

Make it feel like `man`:

* [x] section separators
* [x] bold headings
* [x] pager friendly formatting
* [x] optional colors
* [x] opens automatically inside `less`

### Styling

* [x] ANSI headings
* [x] quote indentation
* [x] list formatting
* [x] colored links
* [x] image markers

---

## 3. Storage & Offline Mode (real usefulness)

### Caching System

```
~/.cache/terbro/
```

* [x] URL → SHA256 filename
* [x] auto load if cached
* [x] `--refresh`
* [x] `--offline`
* [x] network fallback to cache
* [x] `--clear` cache

---

### Save Articles

```
terbro URL --save article.txt
terbro URL --markdown --save article.md
```

* [x] plain text save
* [x] markdown save

---

### History System

```
~/.local/share/terbro/history.json
```

* [x] remember opened URLs
* [x] `terbro --history`
* [x] reopen previous article
* [x] interactive selection menu

---

## 4. Output Formats

### Markdown Export

```
terbro URL --markdown
```

* [x] convert HTML → markdown
* [x] compatible with note apps

---

### Image Listing

```
terbro URL --images
```

Shows inline image URLs.

---

## 5. Mini Browser Mode

### Search Engine Mode

```
terbro --search "tcp handshake"
```

Behavior:

1. Fetch search results page
2. Extract top 10 links
3. Show numbered menu
4. Open selected article

* [ ] Not implemented

---

### Navigation

* [ ] open link from article
* [ ] back to previous page
* [ ] open numbered links

Now TerBro becomes a lightweight terminal browser launcher.

---

## 6. Knowledge Tool Features

### Search Inside Saved Articles

```
terbro --library search "linux kernel"
```

* [ ] Not implemented

---

### Dictionary Integration

```
terbro define recursion
```

* [ ] Not implemented

---

### RSS Reader

```
terbro --rss https://site/feed.xml
```

* [ ] Not implemented

---

### Reading Session Mode

```
terbro session URL1 URL2 URL3
```

* [ ] Not implemented

---

## 7. GUI Mode (Optional Interface)

```
terbro URL --gui
```

Tkinter window:

* scrollable article

* clickable links

* search box

* open from clipboard

* [ ] Not implemented

---

## 8. Automation & Launcher

### Bash Integration

* [x] pager wrapper script
* [ ] clipboard reader
* [ ] hotkey launcher
* [ ] open highlighted URL

---

### Keybinding Launcher

Select URL → press shortcut → opens reader.

* [ ] Not implemented

---

## 9. Security & Safety

Protect against hostile internet content:

* [ ] max download size
* [ ] redirect limit
* [ ] block local IP ranges (SSRF)
* [ ] encoding validation
* [ ] content-type validation

---

## 10. Advanced / Fun Features

* [ ] TTS reading (`--listen`)
* [ ] article scoring algorithm
* [ ] readability ranking
* [ ] multi-page article detection
* [ ] export to PDF

---

# What This Becomes

If completed:

**Terminal Readability Browser**

Capabilities:

* article reader
* offline archive
* searchable knowledge base
* rss reader
* dictionary
* mini browser
* research assistant

---

# Recommended Build Order (important)

Follow this to avoid burnout:

1. argparse flags ✅
2. save + markdown ✅
3. cache + offline ✅
4. history ✅
5. search mode
6. navigation
7. rss
8. dictionary
9. gui
10. fancy features

---

## Quick Usage

```
terbro https://example.com
```

Inside pager:

* `/` → search text
* `q` → quit
* arrows / j k → scroll

---
