---
name: elternportal-elternbriefe
description: List and fetch Elternbriefe (parent letters) from Eltern-Portal. Use when the user asks about Elternbriefe, parent letters, school letters, or when you encounter an Eltern-Portal email notification about a new Elternbrief.
license: MIT
compatibility: Requires Python 3.10+, pip packages (requests, beautifulsoup4, python-dotenv, pymupdf), and a .env file with Eltern-Portal credentials.
---

# Elternportal Elternbriefe

Fetches Elternbriefe (parent letters) from any Eltern-Portal school website. Can list all available letters and download/convert individual letters to markdown.

## When to use

- The user asks about Elternbriefe, parent letters, or school communications
- You encounter an email notification from Eltern-Portal about a new Elternbrief (subject like "PG Elternbrief vom DD.MM.YYYY: Title")
- The user wants to read or summarize a specific parent letter

## Instructions

### Step 1: Check dependencies

Ensure Python dependencies are installed:

```bash
pip3 install requests beautifulsoup4 python-dotenv pymupdf
```

### Step 2: List or fetch Elternbriefe

**To list all available Elternbriefe:**

```bash
python3 {baseDir}/scripts/fetch.py list
```

**To fetch a specific Elternbrief by title (e.g. from an email notification):**

```bash
python3 {baseDir}/scripts/fetch.py get --title "Mensa - Neuerungen"
```

**To fetch by entry number:**

```bash
python3 {baseDir}/scripts/fetch.py get --number 134
```

### Step 3: Present the results

**For `list` output:**
- Show a summary table with columns: # | Title | Date | Class | Confirmed
- Indicate which entries have downloadable files vs text-only

**For `get` output:**
- The `content_markdown` field contains the letter content in markdown format
- Present it directly to the user with the metadata header (title, date, class)
- If the letter is about an action item (event, deadline, request), highlight that clearly

**For errors:**
- If `"error"` key is present, report the error. The `"available"` field lists recent entries to help retry.

### Workflow for email notifications

When you see an Eltern-Portal email notification like:
> "am 02.04.2026 ist ein neuer Elternbrief im Eltern-Portal erschienen. Mensa - Neuerungen"

Use `get --title` with the title from the email:
```bash
python3 {baseDir}/scripts/fetch.py get --title "Mensa - Neuerungen"
```

Then present the letter content to the user.

## Configuration

The script reads from a `.env` file (searched in parent directories):

- `URL` — Eltern-Portal base URL (e.g. `https://schoolcode.eltern-portal.org`)
- `USER` — Login email address
- `PASSWORD` — Login password
