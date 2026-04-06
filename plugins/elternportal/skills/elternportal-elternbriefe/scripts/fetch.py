#!/usr/bin/env python3
"""Fetch Elternbriefe (parent letters) from Eltern-Portal.

Supports listing all entries and downloading/converting individual letters to markdown.
Uses HTTP requests for authentication and download, PyMuPDF for PDF-to-text conversion.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pymupdf
import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values


def _find_env_file() -> Path:
    """Walk up from script dir to find .env at the project root."""
    d = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = d / ".env"
        if candidate.exists():
            return candidate
        d = d.parent
    raise FileNotFoundError("Could not find .env file in any parent directory")


_env = dotenv_values(_find_env_file())
URL = _env.get("URL", "").rstrip("/")
USER = _env.get("USER", "")
PASSWORD = _env.get("PASSWORD", "")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}


def login(session: requests.Session) -> None:
    """Authenticate against Eltern-Portal."""
    resp = session.get(URL + "/")
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf"})
    if not csrf_input:
        raise RuntimeError("Could not find CSRF token on login page")

    resp = session.post(
        URL + "/includes/project/auth/login.php",
        data={
            "csrf": csrf_input["value"],
            "username": USER,
            "password": PASSWORD,
            "go_to": "",
        },
        headers={"Referer": URL + "/", "Origin": URL},
        allow_redirects=True,
    )
    resp.raise_for_status()
    if "form-signin" in resp.text:
        raise RuntimeError("Login failed — check credentials")


def fetch_elternbriefe_page(session: requests.Session) -> str:
    """Fetch the Elternbriefe page and return its HTML."""
    resp = session.get(URL + "/aktuelles/elternbriefe")
    resp.raise_for_status()
    return resp.text


def parse_entries(html: str) -> list[dict]:
    """Parse the Elternbriefe HTML into a list of structured entries."""
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", id="asam_content")
    if not content:
        return []

    table = content.find("table", class_="ui")
    if not table:
        return []

    rows = table.find_all("tr")
    entries = []
    i = 0
    while i < len(rows):
        row1 = rows[i]
        # Row 1 should contain the entry number (#NNN)
        row1_text = row1.get_text(" ", strip=True)
        number_match = re.search(r"#(\d+)", row1_text)
        if not number_match:
            i += 1
            continue

        number = int(number_match.group(1))
        confirmed = "noch nicht" not in row1_text

        # Row 2 has the content
        if i + 1 >= len(rows):
            break
        row2 = rows[i + 1]
        i += 2

        entry = {
            "number": number,
            "title": "",
            "date": "",
            "classes": "",
            "confirmed": confirmed,
            "has_file": False,
            "download_url": None,
            "inline_text": None,
        }

        # Check for file link (<a>) or text-only (<span>)
        link = row2.find("a", class_="link_nachrichten")
        span = row2.find("span", class_="link_nachrichten") if not link else None

        if link:
            entry["has_file"] = True
            href = link.get("href", "")
            entry["download_url"] = href

            h4 = link.find("h4")
            if h4:
                entry["title"] = h4.get_text(strip=True)

            # Date is the text after <h4> inside the link
            link_text = link.get_text(" ", strip=True)
            date_match = re.search(
                r"(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})", link_text
            )
            if date_match:
                entry["date"] = date_match.group(1)

        elif span:
            entry["has_file"] = False
            h4 = span.find("h4")
            if h4:
                entry["title"] = h4.get_text(strip=True)

            span_text = span.get_text(" ", strip=True)
            date_match = re.search(
                r"(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})", span_text
            )
            if date_match:
                entry["date"] = date_match.group(1)

        # Extract class info from the row
        class_span = row2.find("span", class_="small")
        if class_span:
            class_text = class_span.get_text(strip=True)
            class_match = re.search(r"Klasse/n:\s*(.+)", class_text)
            if class_match:
                entry["classes"] = class_match.group(1).strip()

        # Extract inline text content (for text-only entries, or entries with extra text)
        if not link and span:
            # Get all text after the span element in row2
            all_text_parts = []
            for child in row2.children:
                if child == span or (hasattr(child, "class_") and "small" in (child.get("class") or [])):
                    continue
                if isinstance(child, str):
                    t = child.strip()
                    if t:
                        all_text_parts.append(t)
            # Also get text content from the row that's not in span/class elements
            full_row_text = row2.get_text("\n", strip=True)
            # Remove the title, date marker, and class info to get the inline text
            inline = full_row_text
            if entry["title"]:
                inline = inline.replace(entry["title"], "", 1)
            if entry["date"]:
                inline = inline.replace(entry["date"], "", 1)
            inline = re.sub(r"\(keine Datei.*?bestätigen\)", "", inline)
            inline = re.sub(r"Klasse/n:.*", "", inline)
            inline = inline.strip()
            if inline:
                entry["inline_text"] = inline

        entries.append(entry)

    return entries


def download_file(session: requests.Session, download_url: str) -> bytes:
    """Download a file from the portal using an authenticated session."""
    full_url = URL + "/" + download_url.lstrip("/")
    resp = session.get(full_url)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "")
    if "html" in content_type and len(resp.content) < 1000:
        raise RuntimeError(f"Download returned HTML instead of a file (possible session/CSRF issue)")
    return resp.content


def pdf_to_markdown(pdf_bytes: bytes) -> str:
    """Convert PDF bytes to markdown text using PyMuPDF."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            pages.append(text.strip())
    doc.close()
    if not pages:
        return "(This PDF appears to contain only images/scanned content and could not be converted to text.)"
    return "\n\n---\n\n".join(pages)


def get_entry_content(session: requests.Session, entry: dict) -> dict:
    """Get the full content of an Elternbrief entry."""
    result = {
        "number": entry["number"],
        "title": entry["title"],
        "date": entry["date"],
        "classes": entry["classes"],
        "confirmed": entry["confirmed"],
        "type": "file" if entry["has_file"] else "text",
        "content_markdown": "",
        "retrieved_at": datetime.now().isoformat(timespec="seconds"),
    }

    if entry["has_file"] and entry["download_url"]:
        pdf_bytes = download_file(session, entry["download_url"])
        md_content = pdf_to_markdown(pdf_bytes)
        if entry.get("inline_text"):
            result["content_markdown"] = (
                f"# {entry['title']}\n\n"
                f"> {entry['inline_text']}\n\n---\n\n{md_content}"
            )
        else:
            result["content_markdown"] = f"# {entry['title']}\n\n{md_content}"
    elif entry.get("inline_text"):
        result["content_markdown"] = f"# {entry['title']}\n\n{entry['inline_text']}"
    else:
        result["content_markdown"] = f"# {entry['title']}\n\n(No content available.)"

    return result


def cmd_list(session: requests.Session) -> None:
    """List all Elternbriefe."""
    html = fetch_elternbriefe_page(session)
    entries = parse_entries(html)
    output = {
        "entries": [
            {
                "number": e["number"],
                "title": e["title"],
                "date": e["date"],
                "classes": e["classes"],
                "confirmed": e["confirmed"],
                "has_file": e["has_file"],
            }
            for e in entries
        ],
        "total": len(entries),
        "retrieved_at": datetime.now().isoformat(timespec="seconds"),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_get(session: requests.Session, number: int | None, title: str | None) -> None:
    """Get a specific Elternbrief by number or title."""
    html = fetch_elternbriefe_page(session)
    entries = parse_entries(html)

    match = None
    if number is not None:
        for e in entries:
            if e["number"] == number:
                match = e
                break
        if not match:
            available = [f"#{e['number']}: {e['title']}" for e in entries[:10]]
            print(json.dumps({
                "error": f"No entry found with number #{number}",
                "available": available,
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
    elif title is not None:
        needle = title.lower()
        candidates = [e for e in entries if needle in e["title"].lower()]
        if not candidates:
            available = [f"#{e['number']}: {e['title']}" for e in entries[:10]]
            print(json.dumps({
                "error": f"No entry found matching title '{title}'",
                "available": available,
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
        # Return the most recent match (highest number)
        match = max(candidates, key=lambda e: e["number"])
    else:
        print(json.dumps({"error": "Specify --number or --title"}, ensure_ascii=False))
        sys.exit(1)

    result = get_entry_content(session, match)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Fetch Elternbriefe from Eltern-Portal")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List all Elternbriefe")

    get_parser = subparsers.add_parser("get", help="Get a specific Elternbrief")
    get_group = get_parser.add_mutually_exclusive_group(required=True)
    get_group.add_argument("--number", type=int, help="Entry number (e.g. 134)")
    get_group.add_argument("--title", type=str, help="Title substring to search for")

    args = parser.parse_args()

    if not URL or not USER or not PASSWORD:
        print(json.dumps({"error": "Missing URL, USER, or PASSWORD in .env"}))
        sys.exit(1)

    session = requests.Session()
    session.headers.update(_HEADERS)
    try:
        login(session)
        if args.command == "list":
            cmd_list(session)
        elif args.command == "get":
            cmd_get(session, args.number, args.title)
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
