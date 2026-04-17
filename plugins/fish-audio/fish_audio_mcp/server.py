"""Fish Audio MCP Server — text-to-speech with inline emotion tags."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from .client import (
    MAX_TEXT_LENGTH,
    VALID_FORMATS,
    VALID_MODELS,
    get_credit_info,
    list_voice_models,
    synthesize_speech,
    write_audio_file,
)

mcp = FastMCP("fish-audio")


S1_EMOTION_TAGS = [
    "angry", "sad", "disdainful", "excited", "surprised", "satisfied",
    "unhappy", "anxious", "hysterical", "delighted", "scared", "worried",
    "indifferent", "upset", "impatient", "nervous", "guilty", "scornful",
    "frustrated", "depressed", "embarrassed", "jealous", "awkward", "amused",
    "happy", "calm", "confident", "thoughtful", "curious", "enthusiastic",
    "warm", "friendly", "empathetic",
]

S1_TONE_TAGS = [
    "in a hurry tone", "shouting", "screaming", "whispering", "soft tone",
]


@mcp.tool()
def text_to_speech(
    text: str,
    voice_id: str | None = None,
    model: str = "s1",
    audio_format: str = "mp3",
    speed: float = 1.0,
    mp3_bitrate: int = 128,
    temperature: float = 0.7,
    top_p: float = 0.7,
    output_directory: str | None = None,
    output_filename: str | None = None,
) -> dict[str, Any]:
    """Synthesize speech from text and save it as an audio file.

    For the S1 model, embed emotion tags as parentheses at the start of a
    sentence — e.g. `(happy) What a great day!`, `(excited) Look at this!`
    (see the S1 emotion tag list at the top of this module, or call
    list_supported_tags()). Tone tags such as `(whispering)` can appear
    anywhere in the sentence.

    Args:
        text: The text to speak. Include `(emotion)` or `(tone)` tags inline.
        voice_id: Fish Audio reference_id for the voice. Use list_voices() to
            discover valid ids. If omitted, the API default voice is used.
        model: Fish Audio model. Either "s1" (parenthesis-tag syntax, fixed
            emotion list) or "s2-pro" (bracket-tag syntax, free-form tags).
            Defaults to "s1".
        audio_format: Output container: "mp3", "wav", "pcm", or "opus".
            Defaults to "mp3".
        speed: Playback speed multiplier 0.5-2.0. Default 1.0.
        mp3_bitrate: 64, 128, or 192. Only used when audio_format="mp3".
        temperature: Expressiveness knob 0-1. Default 0.7.
        top_p: Nucleus sampling diversity 0-1. Default 0.7.
        output_directory: Where to write the file. Defaults to ~/Desktop.
        output_filename: Exact filename (extension optional). If omitted, a
            timestamped name is generated.

    Returns:
        {path, size_bytes, voice_id, model, format}
    """
    if model not in VALID_MODELS:
        raise ValueError(f"model must be one of {sorted(VALID_MODELS)}")
    if audio_format not in VALID_FORMATS:
        raise ValueError(f"audio_format must be one of {sorted(VALID_FORMATS)}")
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(
            f"text exceeds the {MAX_TEXT_LENGTH}-char MCP boundary cap "
            f"(got {len(text)}). Split into smaller calls."
        )

    audio_bytes = synthesize_speech(
        text=text,
        voice_id=voice_id,
        model=model,
        audio_format=audio_format,
        mp3_bitrate=mp3_bitrate,
        speed=speed,
        temperature=temperature,
        top_p=top_p,
    )

    path = write_audio_file(
        audio_bytes=audio_bytes,
        output_directory=output_directory,
        output_filename=output_filename,
        audio_format=audio_format,
        text_preview=text,
    )

    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "voice_id": voice_id,
        "model": model,
        "format": audio_format,
    }


@mcp.tool()
def list_voices(query: str | None = None, page_size: int = 20) -> dict[str, Any]:
    """List available Fish Audio voice models (their reference_ids).

    Args:
        query: Optional substring to filter model titles.
        page_size: Max number of voices to return. Default 20.

    Pass any voice's `_id` as `voice_id` to text_to_speech().
    """
    return list_voice_models(query=query, page_size=page_size)


@mcp.tool()
def check_credit() -> dict[str, Any]:
    """Return remaining Fish Audio API credit.

    Call before a long TTS run so the caller can stop early if the wallet
    is empty instead of failing partway through.
    """
    return get_credit_info()


@mcp.tool()
def list_supported_tags() -> dict[str, list[str]]:
    """Return the inline tag vocabulary supported by the S1 model.

    S1 emotion tags MUST appear at the start of a sentence in parentheses.
    Tone tags can appear anywhere. The S2-Pro model uses free-form
    bracket-syntax tags and is not validated here.
    """
    return {
        "s1_emotion_tags": S1_EMOTION_TAGS,
        "s1_tone_tags": S1_TONE_TAGS,
    }
