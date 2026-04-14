"""Transistor.fm MCP Server — publish and manage podcast episodes."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from .client import (
    flatten_payload,
    request,
    resolve_show_id,
    upload_audio_file,
)

mcp = FastMCP("transistor")

VALID_PUBLISH_STATUS = {"draft", "scheduled", "published"}
VALID_EPISODE_TYPE = {"full", "trailer", "bonus"}


# ---------- Shows ----------

@mcp.tool()
def list_shows(
    query: str | None = None,
    page: int = 0,
    per: int = 10,
) -> dict[str, Any]:
    """List shows (podcasts) the API key has access to.

    Args:
        query: Optional search string to filter shows by title.
        page: Page number (0-indexed).
        per: Items per page (default 10).
    """
    params: dict[str, Any] = {"pagination[page]": page, "pagination[per]": per}
    if query:
        params["query"] = query
    return request("GET", "/shows", params=params)


@mcp.tool()
def get_show(show_id: str | None = None) -> dict[str, Any]:
    """Retrieve a single show by id or slug.

    Args:
        show_id: Numeric id or slug. Defaults to TRANSISTOR_SHOW_ID env var.
    """
    sid = resolve_show_id(show_id)
    return request("GET", f"/shows/{sid}")


@mcp.tool()
def update_show(
    show_id: str | None = None,
    title: str | None = None,
    description: str | None = None,
    author: str | None = None,
    website: str | None = None,
    category: str | None = None,
    secondary_category: str | None = None,
    language: str | None = None,
    keywords: str | None = None,
    copyright: str | None = None,
    owner_email: str | None = None,
    explicit: bool | None = None,
    show_type: str | None = None,
    multiple_seasons: bool | None = None,
    time_zone: str | None = None,
    image_url: str | None = None,
) -> dict[str, Any]:
    """Update show metadata. Any field left as None is not sent.

    Args:
        show_id: Numeric id or slug. Defaults to TRANSISTOR_SHOW_ID env var.
        title: Show title.
        description: Show description (supports basic HTML).
        author: Author name.
        website: Show website URL.
        category: Primary Apple Podcasts category.
        secondary_category: Secondary category.
        language: BCP 47 language code (e.g. "en").
        keywords: Comma-separated keywords.
        copyright: Copyright string.
        owner_email: Podcast owner email for directories.
        explicit: Whether the show contains explicit content.
        show_type: One of "episodic" or "serial".
        multiple_seasons: Whether the show uses seasons.
        time_zone: IANA time zone (e.g. "Berlin").
        image_url: Publicly reachable URL of cover artwork.

    Note: Transistor's public API does NOT support creating or deleting shows.
    New shows must be created in the Transistor.fm dashboard.
    """
    sid = resolve_show_id(show_id)
    fields = {
        "title": title,
        "description": description,
        "author": author,
        "website": website,
        "category": category,
        "secondary_category": secondary_category,
        "language": language,
        "keywords": keywords,
        "copyright": copyright,
        "owner_email": owner_email,
        "explicit": explicit,
        "show_type": show_type,
        "multiple_seasons": multiple_seasons,
        "time_zone": time_zone,
        "image_url": image_url,
    }
    data = flatten_payload("show", fields)
    return request("PATCH", f"/shows/{sid}", data=data)


# ---------- Episodes ----------

@mcp.tool()
def list_episodes(
    show_id: str | None = None,
    status: str | None = None,
    query: str | None = None,
    page: int = 0,
    per: int = 10,
) -> dict[str, Any]:
    """List episodes for a show.

    Args:
        show_id: Numeric id or slug. Defaults to TRANSISTOR_SHOW_ID env var.
        status: Filter by status: "published", "scheduled", or "draft".
        query: Optional search string over episode title.
        page: Page number (0-indexed).
        per: Items per page (default 10).
    """
    sid = resolve_show_id(show_id)
    params: dict[str, Any] = {
        "show_id": sid,
        "pagination[page]": page,
        "pagination[per]": per,
    }
    if status:
        params["filter[status]"] = status
    if query:
        params["query"] = query
    return request("GET", "/episodes", params=params)


@mcp.tool()
def get_episode(episode_id: str) -> dict[str, Any]:
    """Retrieve a single episode by its numeric id."""
    return request("GET", f"/episodes/{episode_id}")


@mcp.tool()
def create_episode(
    title: str,
    summary: str | None = None,
    description: str | None = None,
    audio_url: str | None = None,
    image_url: str | None = None,
    season: int | None = None,
    number: int | None = None,
    type: str = "full",
    keywords: str | None = None,
    author: str | None = None,
    explicit: bool | None = None,
    show_id: str | None = None,
) -> dict[str, Any]:
    """Create a new draft episode.

    Args:
        title: Episode title (required).
        summary: Short summary (plain text, ~1-2 sentences).
        description: Full show notes (supports basic HTML).
        audio_url: Final audio_url returned by upload_audio().
        image_url: Per-episode artwork URL.
        season: Season number.
        number: Episode number.
        type: One of "full", "trailer", "bonus". Default "full".
        keywords: Comma-separated keywords.
        author: Episode author override.
        explicit: Whether the episode contains explicit content.
        show_id: Target show. Defaults to TRANSISTOR_SHOW_ID env var.

    Newly created episodes are drafts until publish_episode() is called.
    """
    if type not in VALID_EPISODE_TYPE:
        raise ValueError(f"type must be one of {sorted(VALID_EPISODE_TYPE)}")

    sid = resolve_show_id(show_id)
    fields = {
        "show_id": sid,
        "title": title,
        "summary": summary,
        "description": description,
        "audio_url": audio_url,
        "image_url": image_url,
        "season": season,
        "number": number,
        "type": type,
        "keywords": keywords,
        "author": author,
        "explicit": explicit,
    }
    data = flatten_payload("episode", fields)
    return request("POST", "/episodes", data=data)


@mcp.tool()
def update_episode(
    episode_id: str,
    title: str | None = None,
    summary: str | None = None,
    description: str | None = None,
    audio_url: str | None = None,
    image_url: str | None = None,
    season: int | None = None,
    number: int | None = None,
    type: str | None = None,
    keywords: str | None = None,
    author: str | None = None,
    explicit: bool | None = None,
) -> dict[str, Any]:
    """Update an existing episode's metadata. Only provided fields are sent."""
    if type is not None and type not in VALID_EPISODE_TYPE:
        raise ValueError(f"type must be one of {sorted(VALID_EPISODE_TYPE)}")

    fields = {
        "title": title,
        "summary": summary,
        "description": description,
        "audio_url": audio_url,
        "image_url": image_url,
        "season": season,
        "number": number,
        "type": type,
        "keywords": keywords,
        "author": author,
        "explicit": explicit,
    }
    data = flatten_payload("episode", fields)
    if not data:
        raise ValueError("update_episode called with no fields to update")
    return request("PATCH", f"/episodes/{episode_id}", data=data)


@mcp.tool()
def publish_episode(
    episode_id: str,
    status: str = "published",
    scheduled_for: str | None = None,
) -> dict[str, Any]:
    """Change an episode's publish state.

    Args:
        episode_id: Episode numeric id.
        status: One of "published", "scheduled", or "draft".
        scheduled_for: ISO 8601 datetime for future publishing. Required when status="scheduled".

    Use status="scheduled" with an ISO 8601 datetime (e.g. "2026-05-01T09:00:00Z")
    to schedule, "published" to publish immediately, or "draft" to unpublish.
    """
    if status not in VALID_PUBLISH_STATUS:
        raise ValueError(f"status must be one of {sorted(VALID_PUBLISH_STATUS)}")
    if status == "scheduled" and not scheduled_for:
        raise ValueError("scheduled_for is required when status='scheduled'")

    fields: dict[str, Any] = {"status": status}
    if scheduled_for:
        fields["scheduled_for"] = scheduled_for
    data = flatten_payload("episode", fields)
    return request("PATCH", f"/episodes/{episode_id}/publish", data=data)


@mcp.tool()
def delete_episode(episode_id: str) -> dict[str, Any]:
    """"Delete" an episode.

    Transistor.fm's public API does NOT expose a hard DELETE for episodes.
    This tool maps to PATCH /v1/episodes/:id/publish with status="draft",
    which unpublishes the episode and removes it from the public feed.
    The episode remains in the Transistor dashboard and can be republished.
    To permanently remove an episode, use the Transistor.fm dashboard UI.
    """
    data = flatten_payload("episode", {"status": "draft"})
    result = request("PATCH", f"/episodes/{episode_id}/publish", data=data)
    return {
        "status": "unpublished",
        "note": "Transistor API does not support hard delete; episode set to draft.",
        "episode": result,
    }


# ---------- Audio ----------

@mcp.tool()
def upload_audio(local_path: str) -> dict[str, Any]:
    """Upload an audio file to Transistor's S3 bucket and return the audio_url.

    Args:
        local_path: Absolute or ~-expanded path to the audio file (mp3, m4a, wav).

    Flow:
        1. GET /v1/episodes/authorize_upload?filename=<basename> → pre-signed S3 URL.
        2. PUT the raw bytes to the S3 URL with the returned Content-Type.
        3. Return { audio_url, content_type, filename, size_bytes }.

    Pass audio_url to create_episode() or update_episode() to attach it.
    """
    return upload_audio_file(local_path)


# ---------- Analytics ----------

@mcp.tool()
def get_show_analytics(
    show_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Retrieve downloads for a show (default window: last 14 days).

    Args:
        show_id: Numeric id or slug. Defaults to TRANSISTOR_SHOW_ID env var.
        start_date: Start of window, format "dd-mm-yyyy".
        end_date: End of window, format "dd-mm-yyyy".
    """
    sid = resolve_show_id(show_id)
    params: dict[str, Any] = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    return request("GET", f"/analytics/{sid}", params=params or None)


@mcp.tool()
def get_show_episode_analytics(
    show_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Retrieve per-episode downloads for a show (default window: last 7 days).

    Args:
        show_id: Numeric id or slug. Defaults to TRANSISTOR_SHOW_ID env var.
        start_date: Start of window, format "dd-mm-yyyy".
        end_date: End of window, format "dd-mm-yyyy".
    """
    sid = resolve_show_id(show_id)
    params: dict[str, Any] = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    return request("GET", f"/analytics/{sid}/episodes", params=params or None)


@mcp.tool()
def get_episode_analytics(
    episode_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Retrieve downloads for a single episode (default window: last 14 days).

    Args:
        episode_id: Episode numeric id.
        start_date: Start of window, format "dd-mm-yyyy".
        end_date: End of window, format "dd-mm-yyyy".
    """
    params: dict[str, Any] = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    return request("GET", f"/analytics/episodes/{episode_id}", params=params or None)
