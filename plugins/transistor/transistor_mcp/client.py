"""HTTP client for the Transistor.fm API."""

from __future__ import annotations

import mimetypes
import os
import time
from pathlib import Path
from typing import Any

import requests

API_BASE = "https://api.transistor.fm/v1"
MAX_RETRIES = 3
BACKOFF_SECONDS = (1, 2, 4)


class TransistorError(RuntimeError):
    """Raised for any non-2xx response from the Transistor API."""


def _api_key() -> str:
    key = os.environ.get("TRANSISTOR_API_KEY", "")
    if not key:
        raise RuntimeError("Missing TRANSISTOR_API_KEY environment variable")
    return key


def default_show_id() -> str | None:
    value = os.environ.get("TRANSISTOR_SHOW_ID", "").strip()
    return value or None


def resolve_show_id(show_id: str | None) -> str:
    value = show_id or default_show_id()
    if not value:
        raise ValueError(
            "show_id is required: pass it explicitly or set TRANSISTOR_SHOW_ID in the environment"
        )
    return value


def _headers() -> dict[str, str]:
    return {"x-api-key": _api_key(), "Accept": "application/json"}


def request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call the Transistor API with exponential backoff on 429."""
    url = f"{API_BASE}{path}"
    last_error: str | None = None

    for attempt in range(MAX_RETRIES + 1):
        resp = requests.request(
            method,
            url,
            headers=_headers(),
            params=params,
            data=data,
            timeout=30,
        )

        if resp.status_code == 429 and attempt < MAX_RETRIES:
            time.sleep(BACKOFF_SECONDS[attempt])
            continue

        if resp.status_code >= 400:
            try:
                body = resp.json()
            except ValueError:
                body = resp.text
            last_error = f"{resp.status_code} {method} {path}: {body}"
            raise TransistorError(last_error)

        if not resp.content:
            return {}
        return resp.json()

    raise TransistorError(f"Rate limit exceeded after {MAX_RETRIES} retries: {last_error}")


def flatten_payload(resource: str, fields: dict[str, Any]) -> dict[str, Any]:
    """Build Transistor's form-encoded payload shape: resource[field]=value."""
    payload: dict[str, Any] = {}
    for key, value in fields.items():
        if value is None:
            continue
        payload[f"{resource}[{key}]"] = value
    return payload


def upload_audio_file(local_path: str) -> dict[str, str]:
    """Run the 2-step audio upload flow and return the final audio_url.

    1. Authorize: GET /v1/episodes/authorize_upload?filename=<basename>
       → returns { upload_url, audio_url, content_type }
    2. PUT the raw file bytes to upload_url with the returned content_type.
    3. Return audio_url (for use in episode[audio_url]).
    """
    path = Path(local_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")

    filename = path.name
    auth = request("GET", "/episodes/authorize_upload", params={"filename": filename})

    attrs = (auth.get("data") or {}).get("attributes") or {}
    upload_url = attrs.get("upload_url")
    audio_url = attrs.get("audio_url")
    content_type = attrs.get("content_type") or mimetypes.guess_type(filename)[0] or "audio/mpeg"

    if not upload_url or not audio_url:
        raise TransistorError(f"authorize_upload response missing upload_url/audio_url: {auth}")

    with path.open("rb") as fh:
        put_resp = requests.put(
            upload_url,
            data=fh,
            headers={"Content-Type": content_type},
            timeout=600,
        )
    if put_resp.status_code >= 400:
        raise TransistorError(
            f"S3 upload failed: {put_resp.status_code} {put_resp.text[:500]}"
        )

    return {
        "audio_url": audio_url,
        "content_type": content_type,
        "filename": filename,
        "size_bytes": path.stat().st_size,
    }
