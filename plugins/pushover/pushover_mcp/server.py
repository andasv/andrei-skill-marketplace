"""Pushover MCP Server — send push notifications via Pushover API."""

import os

import requests
from fastmcp import FastMCP

mcp = FastMCP("pushover")

PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"


def _get_config() -> tuple[str, str]:
    token = os.environ.get("PUSHOVER_APP_TOKEN", "")
    user = os.environ.get("PUSHOVER_USER_KEY", "")
    if not token or not user:
        raise RuntimeError("Missing PUSHOVER_APP_TOKEN or PUSHOVER_USER_KEY environment variables")
    return token, user


@mcp.tool()
def send(
    message: str,
    title: str | None = None,
    priority: int = 2,
    sound: str = "persistent",
    url: str | None = None,
    url_title: str | None = None,
    device: str | None = None,
) -> dict:
    """Send a push notification via Pushover.

    Args:
        message: The notification message (max 1024 chars, required)
        title: Message title (default: app name)
        priority: -2 (lowest) to 2 (emergency). Default 2 (emergency, repeats until acknowledged)
        sound: Notification sound. Default 'persistent' (long repeating alert)
        url: Supplementary URL to include
        url_title: Title for the URL
        device: Target a specific device name
    """
    token, user = _get_config()

    data = {
        "token": token,
        "user": user,
        "message": message,
    }

    if title:
        data["title"] = title
    if priority is not None:
        data["priority"] = priority
        if priority == 2:
            data["retry"] = 30
            data["expire"] = 3600
    if sound:
        data["sound"] = sound
    if url:
        data["url"] = url
    if url_title:
        data["url_title"] = url_title
    if device:
        data["device"] = device

    resp = requests.post(PUSHOVER_API_URL, data=data)

    if resp.status_code == 200 and resp.json().get("status") == 1:
        return {"status": "ok", "request": resp.json().get("request")}
    else:
        return {"status": "error", "details": resp.json()}
