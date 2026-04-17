"""HTTP client for the Fish Audio API."""

from __future__ import annotations

import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

API_BASE = "https://api.fish.audio"
TTS_PATH = "/v1/tts"
MODELS_PATH = "/model"
CREDIT_PATH = "/wallet/self/api-credit"
MAX_RETRIES = 3
BACKOFF_SECONDS = (1, 2, 4)

VALID_MODELS = {"s1", "s2-pro"}
VALID_FORMATS = {"mp3", "wav", "pcm", "opus"}

MAX_TEXT_LENGTH = 10_000
ERROR_BODY_MAX_CHARS = 200

# Patterns we scrub from any response body before surfacing it in an
# exception message, so a bug report pasted into chat can't leak a key.
_SECRET_PATTERNS = (
    re.compile(r"Bearer\s+\S+", re.IGNORECASE),
    re.compile(r"sk-ant-\S+"),
    re.compile(r"fish[_-]?audio[_-]?api[_-]?key\s*[:=]\s*\S+", re.IGNORECASE),
)


class FishAudioError(RuntimeError):
    """Raised for any non-2xx response from the Fish Audio API."""


def _api_key() -> str:
    key = os.environ.get("FISH_AUDIO_API_KEY", "")
    if not key:
        raise RuntimeError("Missing FISH_AUDIO_API_KEY environment variable")
    return key


def _headers(model: str, content_type: str = "application/json") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": content_type,
        "model": model,
    }


def _redact(body: Any) -> str:
    """Trim and scrub a response body for safe inclusion in an exception message."""
    text = body if isinstance(body, str) else str(body)
    if len(text) > ERROR_BODY_MAX_CHARS:
        text = text[:ERROR_BODY_MAX_CHARS] + "…"
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def _body_for_error(resp: requests.Response) -> str:
    """Best-effort, redacted rendering of a failed response's body."""
    try:
        return _redact(resp.json())
    except ValueError:
        return _redact(resp.text)


def synthesize_speech(
    text: str,
    voice_id: str | None,
    *,
    model: str = "s1",
    audio_format: str = "mp3",
    mp3_bitrate: int = 128,
    speed: float = 1.0,
    chunk_length: int = 300,
    latency: str = "normal",
    temperature: float = 0.7,
    top_p: float = 0.7,
) -> bytes:
    """Call POST /v1/tts and return the raw audio bytes.

    Retries once on transient 5xx errors with a 2-second backoff. A 402
    (payment required / quota exhausted) surfaces immediately so the caller
    can stop the pipeline.
    """
    if model not in VALID_MODELS:
        raise ValueError(f"model must be one of {sorted(VALID_MODELS)}")
    if audio_format not in VALID_FORMATS:
        raise ValueError(f"format must be one of {sorted(VALID_FORMATS)}")
    if not text.strip():
        raise ValueError("text must not be empty")
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(
            f"text exceeds {MAX_TEXT_LENGTH}-char cap (got {len(text)}); "
            "split it into smaller calls so Fish Audio doesn't bill or reject the whole batch"
        )

    payload: dict[str, Any] = {
        "text": text,
        "format": audio_format,
        "mp3_bitrate": mp3_bitrate,
        "chunk_length": chunk_length,
        "latency": latency,
        "temperature": temperature,
        "top_p": top_p,
        "prosody": {"speed": speed},
    }
    if voice_id:
        payload["reference_id"] = voice_id

    url = f"{API_BASE}{TTS_PATH}"
    last_error: str | None = None

    for attempt in range(MAX_RETRIES + 1):
        resp = requests.post(
            url,
            headers=_headers(model),
            json=payload,
            timeout=120,
        )

        if resp.status_code == 402:
            raise FishAudioError(
                "402 Payment Required: Fish Audio quota exhausted. "
                f"Check your credit with check_credit(). Body: {_body_for_error(resp)}"
            )

        if resp.status_code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
            time.sleep(BACKOFF_SECONDS[attempt])
            last_error = f"{resp.status_code} {_body_for_error(resp)}"
            continue

        if resp.status_code >= 400:
            raise FishAudioError(f"{resp.status_code} POST {TTS_PATH}: {_body_for_error(resp)}")

        if not resp.content:
            raise FishAudioError("TTS returned 200 but empty body")
        return resp.content

    raise FishAudioError(f"Exhausted {MAX_RETRIES} retries: {last_error}")


def write_audio_file(
    audio_bytes: bytes,
    output_directory: str | None,
    output_filename: str | None,
    audio_format: str,
    text_preview: str,
) -> Path:
    """Write TTS bytes to a file with a deterministic, merge-friendly name.

    Naming matches the ElevenLabs convention used by the podcast-skill:
    `tts_<first5chars>_<YYYYMMDD_HHMMSS>.<ext>` — renamed by the skill
    afterwards to `NNN_speaker.<ext>` for merge ordering.

    Security: ``output_filename`` must be a plain basename with no path
    separators, ``..`` components, or null bytes. ``output_directory``
    must resolve to a location inside the invoking user's home — the
    MCP tool caller is not allowed to write anywhere else on the
    filesystem. Violations raise ``ValueError``.
    """
    if output_filename is not None:
        if output_filename in ("", ".", ".."):
            raise ValueError("output_filename must be a valid basename")
        for token in ("/", "\\", "\x00"):
            if token in output_filename:
                raise ValueError("output_filename must be a plain basename, no path separators or null bytes")
        if output_filename.startswith(".."):
            raise ValueError("output_filename must not start with '..'")

    home = Path.home().resolve()
    if output_directory:
        out_dir = Path(output_directory).expanduser().resolve()
    else:
        # Default to ./output/ under the current working directory, matching
        # the podcast-skill convention. Fall back to home if cwd is outside
        # home (e.g. launched from /tmp).
        candidate = (Path.cwd() / "output").resolve()
        out_dir = candidate if str(candidate).startswith(str(home)) else (home / "fish-audio-output").resolve()

    # Confine writes to within the user's home to block the caller from
    # dropping files in /etc, /tmp, /Library/LaunchAgents, etc.
    try:
        out_dir.relative_to(home)
    except ValueError:
        raise ValueError(
            f"output_directory must resolve to a path inside {home}; got {out_dir}"
        ) from None

    out_dir.mkdir(parents=True, exist_ok=True)

    if output_filename:
        name = output_filename if output_filename.endswith(f".{audio_format}") else f"{output_filename}.{audio_format}"
    else:
        slug_source = text_preview.strip().replace("(", "").replace(")", "").replace("[", "").replace("]", "")
        slug = "".join(c if c.isalnum() else "_" for c in slug_source[:5]) or "out"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"tts_{slug}_{ts}.{audio_format}"

    target = out_dir / name
    # Final belt-and-suspenders: resolve the target and confirm it's still
    # inside out_dir, catching any esoteric filename the earlier checks missed.
    resolved_target = target.resolve()
    try:
        resolved_target.relative_to(out_dir)
    except ValueError:
        raise ValueError(
            f"resolved target {resolved_target} escaped output_directory {out_dir}"
        ) from None

    resolved_target.write_bytes(audio_bytes)
    return resolved_target


def list_voice_models(
    query: str | None = None,
    page_size: int = 20,
) -> dict[str, Any]:
    """GET /model — list available voice models (reference_ids).

    Fish Audio uses `reference_id` in the TTS call to pick a voice; this
    helper surfaces ids/titles so the caller can choose one.
    """
    url = f"{API_BASE}{MODELS_PATH}"
    params: dict[str, Any] = {"page_size": page_size}
    if query:
        params["title"] = query

    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {_api_key()}"},
        params=params,
        timeout=30,
    )
    if resp.status_code >= 400:
        raise FishAudioError(f"{resp.status_code} GET {MODELS_PATH}: {_body_for_error(resp)}")
    return resp.json()


def get_credit_info() -> dict[str, Any]:
    """GET /wallet/self/api-credit — return remaining API credit balance."""
    url = f"{API_BASE}{CREDIT_PATH}"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {_api_key()}"},
        timeout=30,
    )
    if resp.status_code >= 400:
        raise FishAudioError(f"{resp.status_code} GET {CREDIT_PATH}: {_body_for_error(resp)}")
    return resp.json()
