"""Fetch and parse Elternbriefe (parent letters) from Eltern-Portal."""

import re
from datetime import datetime

import pymupdf
import requests
from bs4 import BeautifulSoup


def fetch_page(session: requests.Session, base_url: str) -> str:
    resp = session.get(base_url + "/aktuelles/elternbriefe")
    resp.raise_for_status()
    return resp.text


def parse_entries(html: str) -> list[dict]:
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
        row1_text = row1.get_text(" ", strip=True)
        number_match = re.search(r"#(\d+)", row1_text)
        if not number_match:
            i += 1
            continue

        number = int(number_match.group(1))
        confirmed = "noch nicht" not in row1_text

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

        link = row2.find("a", class_="link_nachrichten")
        span = row2.find("span", class_="link_nachrichten") if not link else None

        if link:
            entry["has_file"] = True
            entry["download_url"] = link.get("href", "")
            h4 = link.find("h4")
            if h4:
                entry["title"] = h4.get_text(strip=True)
            link_text = link.get_text(" ", strip=True)
            date_match = re.search(r"(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})", link_text)
            if date_match:
                entry["date"] = date_match.group(1)
        elif span:
            h4 = span.find("h4")
            if h4:
                entry["title"] = h4.get_text(strip=True)
            span_text = span.get_text(" ", strip=True)
            date_match = re.search(r"(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})", span_text)
            if date_match:
                entry["date"] = date_match.group(1)

        class_span = row2.find("span", class_="small")
        if class_span:
            class_text = class_span.get_text(strip=True)
            class_match = re.search(r"Klasse/n:\s*(.+)", class_text)
            if class_match:
                entry["classes"] = class_match.group(1).strip()

        if not link and span:
            full_row_text = row2.get_text("\n", strip=True)
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


def download_file(session: requests.Session, base_url: str, download_url: str) -> bytes:
    full_url = base_url + "/" + download_url.lstrip("/")
    resp = session.get(full_url)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "")
    if "html" in content_type and len(resp.content) < 1000:
        raise RuntimeError("Download returned HTML instead of a file (possible session/CSRF issue)")
    return resp.content


def pdf_to_markdown(pdf_bytes: bytes) -> str:
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


def list_elternbriefe(session: requests.Session, base_url: str) -> dict:
    html = fetch_page(session, base_url)
    entries = parse_entries(html)
    return {
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


def get_elternbrief(
    session: requests.Session,
    base_url: str,
    number: int | None = None,
    title: str | None = None,
) -> dict:
    html = fetch_page(session, base_url)
    entries = parse_entries(html)

    match = None
    if number is not None:
        for e in entries:
            if e["number"] == number:
                match = e
                break
        if not match:
            available = [f"#{e['number']}: {e['title']}" for e in entries[:10]]
            return {"error": f"No entry found with number #{number}", "available": available}
    elif title is not None:
        needle = title.lower()
        candidates = [e for e in entries if needle in e["title"].lower()]
        if not candidates:
            available = [f"#{e['number']}: {e['title']}" for e in entries[:10]]
            return {"error": f"No entry found matching title '{title}'", "available": available}
        match = max(candidates, key=lambda e: e["number"])
    else:
        return {"error": "Specify number or title"}

    result = {
        "number": match["number"],
        "title": match["title"],
        "date": match["date"],
        "classes": match["classes"],
        "confirmed": match["confirmed"],
        "type": "file" if match["has_file"] else "text",
        "content_markdown": "",
        "retrieved_at": datetime.now().isoformat(timespec="seconds"),
    }

    if match["has_file"] and match["download_url"]:
        pdf_bytes = download_file(session, base_url, match["download_url"])
        md_content = pdf_to_markdown(pdf_bytes)
        if match.get("inline_text"):
            result["content_markdown"] = f"# {match['title']}\n\n> {match['inline_text']}\n\n---\n\n{md_content}"
        else:
            result["content_markdown"] = f"# {match['title']}\n\n{md_content}"
    elif match.get("inline_text"):
        result["content_markdown"] = f"# {match['title']}\n\n{match['inline_text']}"
    else:
        result["content_markdown"] = f"# {match['title']}\n\n(No content available.)"

    return result
