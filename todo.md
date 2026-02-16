
Think of it as stages:
**CLI → Reader → Offline Tool → Mini Browser → Knowledge Tool**

---

# TERBRO DEVELOPMENT ROADMAP

---

## 0. Foundation (Stability first)

Make the current tool solid before adding features.

* [ ] Proper error handling (timeouts, DNS failure, blocked site)
* [ ] Friendly error messages
* [ ] Exit codes (0 success / 1 usage / 2 network / 3 parse)
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
terbro --search "query"
terbro --history
```

Tasks:

* [ ] Replace sys.argv with argparse
* [ ] Help page (`-h`)
* [ ] Flags validation
* [ ] Multiple output modes

---

## 2. Reading Experience (make it pleasant)

### Man-Page Style Reading

Make it feel like `man`:

* [ ] section separators
* [ ] bold headings
* [ ] wrapped paragraphs
* [ ] pager friendly formatting
* [ ] optional colors

### Styling

* [ ] ANSI headings
* [ ] quote indentation
* [ ] list formatting

---

## 3. Storage & Offline Mode (real usefulness)

### Caching System

```
~/.cache/terbro/
```

* [ ] URL → SHA256 filename
* [ ] auto load if cached
* [ ] `--refresh`
* [ ] `--offline`

---

### Save Articles

```
terbro URL --save article.txt
terbro URL --markdown --save article.md
```

* [ ] plain text save
* [ ] markdown save

---

### History System

```
~/.local/share/terbro/history
```

* [ ] remember opened URLs
* [ ] remember search queries
* [ ] `terbro --history`
* [ ] reopen previous article

---

## 4. Output Formats

### Markdown Export

```
terbro URL --markdown
```

* [ ] convert HTML → markdown
* [ ] compatible with note apps

---

### Image Listing

```
terbro URL --images
```

Shows:

```
[1] image.jpg
[2] diagram.png
```

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

```
1. What is TCP?
2. TCP Explained
3. TCP vs UDP
```

User selects:

```
> 2
```

Opens article in reader.

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

---

### Dictionary Integration

Select word → definition

```
terbro define recursion
```

Later integrate with selection hotkey.

---

### RSS Reader

```
terbro --rss https://site/feed.xml
```

Pick article → open in reader.

---

### Reading Session Mode

A continuous session like a book:

```
terbro session URL1 URL2 URL3
```

Navigate between articles like chapters.

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

CLI remains primary — GUI is optional frontend.

---

## 8. Automation & Launcher

### Bash Integration

* [ ] clipboard reader
* [ ] hotkey launcher
* [ ] open highlighted URL

---

### Keybinding Launcher

Select URL → press shortcut → opens reader.

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

1. argparse flags
2. save + markdown
3. cache + offline
4. history
5. search mode
6. navigation
7. rss
8. dictionary
9. gui
10. fancy features

---
