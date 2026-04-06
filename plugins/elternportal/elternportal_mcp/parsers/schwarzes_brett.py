"""Fetch and parse Schwarzes Brett (bulletin board) from Eltern-Portal."""

from datetime import datetime

import requests
from bs4 import BeautifulSoup


def get_schwarzes_brett(session: requests.Session, base_url: str) -> dict:
    resp = session.get(base_url + "/aktuelles/schwarzes_brett")
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    content = soup.find("div", id="asam_content")
    if not content:
        return {"entries": [], "retrieved_at": datetime.now().isoformat(timespec="seconds")}

    entries = []
    for card in content.find_all("div", class_="card"):
        title_el = card.find("h4") or card.find("h3") or card.find("strong")
        title = title_el.get_text(strip=True) if title_el else ""

        body_el = card.find("div", class_="card-body") or card
        body_text = body_el.get_text("\n", strip=True)
        if title and body_text.startswith(title):
            body_text = body_text[len(title):].strip()

        entries.append({"title": title, "content": body_text})

    # Fallback: if no card structure, extract all text blocks
    if not entries:
        for item in content.find_all(["div", "p", "li"]):
            text = item.get_text("\n", strip=True)
            if text and len(text) > 20:
                entries.append({"title": "", "content": text})

    return {
        "entries": entries,
        "total": len(entries),
        "retrieved_at": datetime.now().isoformat(timespec="seconds"),
    }
