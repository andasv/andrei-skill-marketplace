#!/usr/bin/env python3
"""Fetch Vertretungsplan (substitution plan) from Eltern-Portal as JSON.

Uses HTTP requests to authenticate and fetch HTML, then Claude to extract
structured data from the page content via tool use with structured output.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import anthropic
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
ANTHROPIC_API_KEY = _env.get("ANTHROPIC_API_KEY", "")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}

EXTRACTION_TOOL = {
    "name": "extract_vertretungsplan",
    "description": "Extract the substitution plan data from the HTML content.",
    "input_schema": {
        "type": "object",
        "properties": {
            "class_name": {
                "type": "string",
                "description": "The class identifier, e.g. '6C'",
            },
            "last_updated": {
                "type": "string",
                "description": "The 'Stand:' timestamp from the page, e.g. '16.03.2026 07:41:22'",
            },
            "days": {
                "type": "array",
                "description": "List of days with substitution entries",
                "items": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Day and date, e.g. 'Mo., 16.03.2026'",
                        },
                        "week": {
                            "type": "string",
                            "description": "Calendar week, e.g. 'KW 12'",
                        },
                        "substitutions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "period": {
                                        "type": "string",
                                        "description": "Lesson period number, e.g. '6.'",
                                    },
                                    "affected_teacher": {
                                        "type": "string",
                                        "description": "Teacher abbreviation who is absent",
                                    },
                                    "substitute_teacher": {
                                        "type": "string",
                                        "description": "Substitute teacher abbreviation",
                                    },
                                    "original_subject": {
                                        "type": "string",
                                        "description": "The original subject that was cancelled (shown with strikethrough), empty if none",
                                    },
                                    "replacement_subject": {
                                        "type": "string",
                                        "description": "The replacement subject, or the subject if no change",
                                    },
                                    "room": {
                                        "type": "string",
                                        "description": "Room number",
                                    },
                                    "info": {
                                        "type": "string",
                                        "description": "Additional info text",
                                    },
                                },
                                "required": [
                                    "period",
                                    "affected_teacher",
                                    "substitute_teacher",
                                    "original_subject",
                                    "replacement_subject",
                                    "room",
                                    "info",
                                ],
                            },
                        },
                    },
                    "required": ["date", "week", "substitutions"],
                },
            },
        },
        "required": ["class_name", "last_updated", "days"],
    },
}

# Few-shot example HTML for prompting
_FEW_SHOT_HTML = (
    "<div class='list bold full_width text_center'>Fr., 14.03.2026 - KW 11</div>"
    "<table class='table'>"
    "<tr class='vp_plan_head'><td class='table_header'>Std.</td><td class='table_header'>Betrifft.</td>"
    "<td class='table_header'>Vertretung</td><td class='table_header'>Fach</td>"
    "<td class='table_header'>Raum</td><td class='table_header'>Info</td></tr>"
    "<tr class='liste_grau'><td>3.</td><td>Kp</td><td>Sm</td>"
    "<td><span style='text-decoration: line-through;'>&nbsp;M&nbsp;</span> NuT_1</td>"
    "<td>A204</td><td>Vertretung</td></tr>"
    "<tr class='liste_grau'><td>5.</td><td>Ro</td><td>---</td>"
    "<td>E</td><td>A105</td><td>Entfall</td></tr>"
    "</table>"
    "<div class='list full_width'>Stand:&nbsp;14.03.2026&nbsp;08:12:05</div>"
)

_FEW_SHOT_OUTPUT = {
    "class_name": "6C",
    "last_updated": "14.03.2026 08:12:05",
    "days": [
        {
            "date": "Fr., 14.03.2026",
            "week": "KW 11",
            "substitutions": [
                {
                    "period": "3.",
                    "affected_teacher": "Kp",
                    "substitute_teacher": "Sm",
                    "original_subject": "M",
                    "replacement_subject": "NuT_1",
                    "room": "A204",
                    "info": "Vertretung",
                },
                {
                    "period": "5.",
                    "affected_teacher": "Ro",
                    "substitute_teacher": "---",
                    "original_subject": "",
                    "replacement_subject": "E",
                    "room": "A105",
                    "info": "Entfall",
                },
            ],
        }
    ],
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


def fetch_html(session: requests.Session) -> str:
    """Fetch the Vertretungsplan page and return the main content HTML."""
    resp = session.get(URL + "/service/vertretungsplan")
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    content = soup.find("div", id="asam_content")
    if content:
        hr = content.find("hr")
        if hr:
            for sibling in list(hr.find_next_siblings()):
                sibling.decompose()
            hr.decompose()
        return str(content)
    return resp.text


def extract_with_llm(html: str) -> dict:
    """Use Claude to extract structured data from the HTML via tool use."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "extract_vertretungsplan"},
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract the Vertretungsplan (substitution plan) data from this HTML.\n\n"
                    f"```html\n{_FEW_SHOT_HTML}\n```"
                ),
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "example_1",
                        "name": "extract_vertretungsplan",
                        "input": _FEW_SHOT_OUTPUT,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "example_1",
                        "content": "Correct extraction. Now extract from the next HTML.",
                    }
                ],
            },
            {
                "role": "user",
                "content": (
                    "Extract the Vertretungsplan data from this HTML. "
                    "Strikethrough text (<span style='text-decoration: line-through;'>) is the "
                    "original cancelled subject; text after the span is the replacement subject. "
                    "If no strikethrough, leave original_subject empty and put subject in replacement_subject.\n\n"
                    f"```html\n{html}\n```"
                ),
            },
        ],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_vertretungsplan":
            return block.input

    raise RuntimeError("LLM did not return structured extraction")


def main():
    if not URL or not USER or not PASSWORD:
        print(json.dumps({"error": "Missing URL, USER, or PASSWORD in .env"}))
        sys.exit(1)
    if not ANTHROPIC_API_KEY:
        print(json.dumps({"error": "Missing ANTHROPIC_API_KEY in .env"}))
        sys.exit(1)

    session = requests.Session()
    session.headers.update(_HEADERS)
    try:
        login(session)
        html = fetch_html(session)
        data = extract_with_llm(html)
        data["retrieved_at"] = datetime.now().isoformat(timespec="seconds")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
