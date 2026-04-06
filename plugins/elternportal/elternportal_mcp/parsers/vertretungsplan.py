"""Fetch and parse Vertretungsplan (substitution plan) from Eltern-Portal."""

import os
from datetime import datetime

import anthropic
import requests
from bs4 import BeautifulSoup

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


def fetch_html(session: requests.Session, base_url: str) -> str:
    resp = session.get(base_url + "/service/vertretungsplan")
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
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("Missing ANTHROPIC_API_KEY environment variable")

    client = anthropic.Anthropic(api_key=api_key)
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


def get_vertretungsplan(session: requests.Session, base_url: str) -> dict:
    html = fetch_html(session, base_url)
    data = extract_with_llm(html)
    data["retrieved_at"] = datetime.now().isoformat(timespec="seconds")
    return data
