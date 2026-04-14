# Transistor.fm MCP Server

Publish and manage podcast episodes on [Transistor.fm](https://transistor.fm) from Claude Code.

## Setup

1. Get your API key from the Transistor dashboard: **Account → API**.
2. Add the following to the repo-root `.env`:

   ```
   TRANSISTOR_API_KEY=your_api_key_here
   TRANSISTOR_SHOW_ID=your_show_slug_or_numeric_id
   ```

   `TRANSISTOR_SHOW_ID` can be either the numeric show id or the URL slug (e.g. `ai-coding-assistant-release-notes-podcast`). Tools that accept a `show_id` argument fall back to this value when the argument is omitted.

3. Install Python dependencies (same as the pushover plugin):

   ```bash
   pip install fastmcp requests
   ```

4. Enable the `transistor` plugin in Claude Code. The MCP server will be launched automatically via `.mcp.json`.

## Tools

### Episode lifecycle
| Tool | Purpose |
| --- | --- |
| `upload_audio(local_path)` | Upload an audio file to Transistor's S3 and return `audio_url`. Handles the 2-step `authorize_upload` + `PUT` flow. |
| `create_episode(title, ..., audio_url=...)` | Create a draft episode. |
| `update_episode(episode_id, ...)` | Patch any subset of metadata fields on an existing episode. |
| `publish_episode(episode_id, status, scheduled_for=None)` | Set state to `published`, `scheduled`, or `draft`. |
| `delete_episode(episode_id)` | Maps to unpublish (`status=draft`). Transistor's API has no hard delete — use the dashboard for permanent removal. |
| `get_episode(episode_id)` | Fetch a single episode by id. |
| `list_episodes(show_id=None, status=None, query=None, page=0, per=10)` | List episodes for a show. |

### Show metadata
| Tool | Purpose |
| --- | --- |
| `list_shows(query=None, page=0, per=10)` | List shows accessible with this API key. |
| `get_show(show_id=None)` | Fetch a single show. |
| `update_show(show_id=None, ...)` | Patch show metadata. |

**Note:** Transistor's public API does **not** support creating or deleting shows/podcasts. New podcasts must be created in the Transistor dashboard; deletion is dashboard-only as well.

### Analytics
| Tool | Purpose |
| --- | --- |
| `get_show_analytics(show_id=None, start_date=None, end_date=None)` | Total show downloads (default window: last 14 days). |
| `get_show_episode_analytics(show_id=None, start_date=None, end_date=None)` | Downloads per episode (default window: last 7 days). |
| `get_episode_analytics(episode_id, start_date=None, end_date=None)` | Downloads for a specific episode. |

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
  → { data: { id: "12345", ... } }

# Optional refinement
update_episode(episode_id="12345", keywords="ai, claude, codex")

# Publish immediately OR schedule
publish_episode(episode_id="12345", status="published")
# or: publish_episode(episode_id="12345", status="scheduled", scheduled_for="2026-05-01T09:00:00Z")
```

## Rate limits

Transistor enforces **10 requests per 10 seconds**. The client retries 429 responses with exponential backoff (1s → 2s → 4s, max 3 retries) before surfacing the error.
