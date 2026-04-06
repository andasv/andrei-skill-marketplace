"""Fetch and parse Termine (calendar/events) from Eltern-Portal."""

import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def get_termine(session: requests.Session, base_url: str) -> dict:
    resp = session.get(base_url + "/service/termine")
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    content = soup.find("div", id="asam_content")
    if not content:
        return {"events": [], "retrieved_at": datetime.now().isoformat(timespec="seconds")}

    events = []

    # Try table-based layout first
    for row in content.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            date_text = cells[0].get_text(strip=True)
            title_text = cells[1].get_text(strip=True) if len(cells) >= 2 else ""
            description = cells[2].get_text(strip=True) if len(cells) >= 3 else ""
            if date_text and re.search(r"\d{2}\.\d{2}\.\d{4}", date_text):
                events.append({
                    "date": date_text,
                    "title": title_text,
                    "description": description,
                })

    # Fallback: list-based layout
    if not events:
        for item in content.find_all(["li", "div"]):
            text = item.get_text(" ", strip=True)
            date_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", text)
            if date_match:
                date_str = date_match.group(1)
                rest = text.replace(date_str, "").strip(" -–:")
                events.append({
                    "date": date_str,
                    "title": rest,
                    "description": "",
                })

    return {
        "events": events,
        "total": len(events),
        "retrieved_at": datetime.now().isoformat(timespec="seconds"),
    }
