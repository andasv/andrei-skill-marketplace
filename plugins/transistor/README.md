# transistor

Publish and manage podcast episodes on [Transistor.fm](https://transistor.fm/) from Claude Code. Bundled Python MCP server — no external service, no npm dependency.

## Features

- Full episode lifecycle: upload audio, create, update, publish, schedule, unpublish, list, fetch
- 2-step S3 audio upload handled as a single `upload_audio(local_path)` call
- Show metadata management (update, list, fetch)
- Analytics: show-level, per-episode, and per-show episode rollups
- Exponential backoff on Transistor's 10-req/10s rate limit (1s / 2s / 4s, max 3 retries)
- Tools accept `show_id` explicitly per call (recommended). For single-show workflows you can also set `TRANSISTOR_SHOW_ID` in `.env` as a fallback default.

## Prerequisites

- Claude Code + the marketplace added
- A [Transistor.fm](https://dashboard.transistor.fm/) account and existing show (show creation is not possible via the API)
- API key from **Account → API** in the Transistor dashboard
- Python 3 with `fastmcp` and `requests` (`pip install fastmcp requests`)
- Environment variable in the repo-root `.env`:
  ```
  TRANSISTOR_API_KEY=<your_api_key>
  ```
- Optional fallback default for single-show workflows (not a secret — usually configured per-consumer in the calling skill instead):
  ```
  TRANSISTOR_SHOW_ID=<numeric_id_or_slug>
  ```
  Tools that accept `show_id` will honor this env var when the argument is omitted.

## Install

```
/plugin marketplace update andrei-skill-marketplace
/plugin install transistor@andrei-skill-marketplace
```

The MCP server launches automatically via `.mcp.json` once the plugin is enabled and Claude Code is restarted.

## Tools

### Episode lifecycle

| Tool | Purpose |
| --- | --- |
| `upload_audio(local_path)` | Upload an audio file to Transistor's S3 and return the `audio_url`. Handles the 2-step `authorize_upload` + `PUT` flow. |
| `create_episode(title, summary?, description?, audio_url?, season?, number?, type?, keywords?, author?, explicit?, show_id?)` | Create a draft episode. |
| `update_episode(episode_id, ...)` | Patch any subset of metadata fields on an existing episode. |
| `publish_episode(episode_id, status, scheduled_for?)` | Set state to `published`, `scheduled`, or `draft`. |
| `delete_episode(episode_id)` | Maps to unpublish (`status=draft`) — Transistor's API has no hard delete; use the dashboard for permanent removal. |
| `get_episode(episode_id)` | Fetch a single episode by id. |
| `list_episodes(show_id?, status?, query?, page?, per?)` | List episodes for a show. |

### Show metadata

| Tool | Purpose |
| --- | --- |
| `list_shows(query?, page?, per?)` | List shows accessible with this API key. |
| `get_show(show_id?)` | Fetch a single show. |
| `update_show(show_id?, ...)` | Patch show metadata (title, description, category, language, explicit flag, etc.). |

> **Note:** Transistor's public API does **not** support creating or deleting shows. New podcasts must be created in the dashboard; deletion is dashboard-only.

### Analytics

| Tool | Purpose |
| --- | --- |
| `get_show_analytics(show_id?, start_date?, end_date?)` | Total show downloads (default window: last 14 days). |
| `get_show_episode_analytics(show_id?, start_date?, end_date?)` | Downloads per episode (default window: last 7 days). |
| `get_episode_analytics(episode_id, start_date?, end_date?)` | Downloads for a specific episode. |

Dates use Transistor's `dd-mm-yyyy` format.

## Canonical publish flow

```text
upload_audio(local_path="/path/to/episode.mp3")
  → { audio_url: "...", ... }

create_episode(
    title="Episode 7 — ...",
    summary="...",
    description="<p>Show notes HTML</p>",
    audio_url="<from step 1>",
    season=1, number=7,
)
  → { data: { id: "12345", share_url: "...", ... } }

# Optional refinement
update_episode(episode_id="12345", keywords="ai, claude, codex")

# Publish immediately OR schedule
publish_episode(episode_id="12345", status="published")
# or: publish_episode(episode_id="12345", status="scheduled", scheduled_for="2026-05-01T09:00:00Z")
```

## Rate limits

Transistor enforces **10 requests per 10 seconds**. The client retries 429 responses with exponential backoff (1s → 2s → 4s, max 3 retries) before surfacing the error.

## Chapter markers

Transistor's audio pipeline **preserves ID3 `CTOC` + `CHAP` frames** through re-encoding (verified on live episodes). If you want per-chapter jump points, embed them into the mp3 before calling `upload_audio` — see the [`podcast-skill`](../podcast-skill/) README's chapter section for the generic `add_chapters.py` utility.

## Cross-skill integration

- **[claude-code-release-podcast](../claude-code-release-podcast/)** — orchestrator that uses this MCP to auto-publish a new podcast episode for every Claude Code release, with chapter markers per feature.
- **[podcast-skill](../podcast-skill/)** — produces the audio that gets fed into `upload_audio`.

## Project structure

```
transistor/
├── .claude-plugin/plugin.json
├── .mcp.json                          # Launches via `python -m transistor_mcp`
├── transistor_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   ├── client.py                      # httpx-free client with 429 backoff + 2-step upload helper
│   └── server.py                      # FastMCP server exposing all 13 tools
└── README.md
```

## License

MIT
