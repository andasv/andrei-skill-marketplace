"""HTTP client for the Fish Audio API."""

from __future__ import annotations

import os
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
                f"402 Payment Required: Fish Audio quota exhausted. "
                f"Check your credit with check_credit(). Body: {resp.text[:500]}"
            )

        if resp.status_code in (429, 500, 502, 503, 504) and attempt < MAX_RETRIES:
            time.sleep(BACKOFF_SECONDS[attempt])
            last_error = f"{resp.status_code} {resp.text[:200]}"
            continue

        if resp.status_code >= 400:
            try:
                body = resp.json()
            except ValueError:
                body = resp.text
            raise FishAudioError(f"{resp.status_code} POST {TTS_PATH}: {body}")

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
    """
    out_dir = Path(output_directory).expanduser() if output_directory else Path.home() / "Desktop"
    out_dir.mkdir(parents=True, exist_ok=True)

    if output_filename:
        name = output_filename if output_filename.endswith(f".{audio_format}") else f"{output_filename}.{audio_format}"
    else:
        slug_source = text_preview.strip().replace("(", "").replace(")", "").replace("[", "").replace("]", "")
        slug = "".join(c if c.isalnum() else "_" for c in slug_source[:5]) or "out"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"tts_{slug}_{ts}.{audio_format}"

    target = out_dir / name
    target.write_bytes(audio_bytes)
    return target


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
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        raise FishAudioError(f"{resp.status_code} GET {MODELS_PATH}: {body}")
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
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        raise FishAudioError(f"{resp.status_code} GET {CREDIT_PATH}: {body}")
    return resp.json()
