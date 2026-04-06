"""Fetch and parse Termine (Schulaufgabenplan) from Eltern-Portal."""

import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def get_termine(session: requests.Session, base_url: str) -> dict:
    """Fetch the Schulaufgabenplan (exam schedule) for the student's class."""
    resp = session.get(base_url + "/service/termine/liste/schulaufgaben")
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    content = soup.find("div", id="asam_content")
    if not content:
        return {"events": [], "retrieved_at": datetime.now().isoformat(timespec="seconds")}

    # Extract class name from the active button text, e.g. "Schulaufgabenplan (6C)"
    class_name = ""
    active_btn = content.find("a", class_="active")
    if active_btn:
        btn_text = active_btn.get_text(strip=True)
        match = re.search(r"\((\w+)\)", btn_text)
        if match:
            class_name = match.group(1)

    table = content.find("table", class_="termine-table")
    if not table:
        return {"class_name": class_name, "events": [], "retrieved_at": datetime.now().isoformat(timespec="seconds")}

    events = []
    current_month = ""
    current_year = ""

    for row in table.find_all("tr"):
        cells = row.find_all("td")

        # Year header row: <td colspan="3"><h4> 2025</h4></td>
        if len(cells) == 1 and cells[0].get("colspan"):
            h4 = cells[0].find("h4")
            if h4 and not h4.find("a"):
                year_text = h4.get_text(strip=True)
                if re.match(r"^\d{4}$", year_text):
                    current_year = year_text
                    continue

            # Month header row: <td colspan="3" style="...background-color..."><h4><a name="09">September</a></h4></td>
            if h4 and h4.find("a"):
                current_month = h4.get_text(strip=True)
                continue

        # Event row: <td>29.09.2025</td><td></td><td>description</td>
        if len(cells) >= 3:
            date_text = cells[0].get_text(strip=True)
            description = cells[2].get_text(strip=True)
            if date_text and re.match(r"\d{2}\.\d{2}\.\d{4}", date_text) and description:
                events.append({
                    "date": date_text,
                    "month": current_month,
                    "description": description,
                })

    return {
        "class_name": class_name,
        "events": events,
        "total": len(events),
        "retrieved_at": datetime.now().isoformat(timespec="seconds"),
    }
