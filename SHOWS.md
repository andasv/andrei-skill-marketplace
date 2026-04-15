# Transistor Shows Registry

Configuration for every podcast show this marketplace publishes to. Skills that publish via the [`transistor`](./plugins/transistor/) MCP read their show id from this file rather than baking it into the SKILL.md or relying on `TRANSISTOR_SHOW_ID` env var. Shows themselves are created in the [Transistor.fm dashboard](https://dashboard.transistor.fm) — the API does not expose `POST /v1/shows`.

This file is the single source of truth for show ids. Update it whenever you add a new show in the dashboard.

## Schema

Each entry must include:

| Field | Required | Description |
| --- | --- | --- |
| `key` | yes | Stable identifier used by skills (e.g. `claude-code-release-podcast`). Must match the consumer skill name where applicable. |
| `slug` | yes | Transistor URL slug (also valid as `show_id` in API calls). |
| `numeric_id` | recommended | Transistor numeric show id. Stable even if the slug changes. |
| `title` | yes | Display title shown in directories. |
| `feed_url` | yes | Public RSS feed. |
| `consumer_skill` | yes | Skill that publishes to this show, by plugin path. |
| `default_personas` | recommended | Persona dir passed to `podcast-skill`. |
| `default_style` | recommended | `collaborative` / `debate` / `interview`. |
| `notes` | optional | Anything else a future consumer should know. |

## Shows

### claude-code-release-podcast

| Field | Value |
| --- | --- |
| `key` | `claude-code-release-podcast` |
| `slug` | `ai-coding-assistant-release-notes-podcast` |
| `numeric_id` | `77078` |
| `title` | AI Coding Assistant Release Notes Podcast |
| `feed_url` | https://feeds.transistor.fm/ai-coding-assistant-release-notes-podcast |
| `dashboard_url` | https://dashboard.transistor.fm/shows/ai-coding-assistant-release-notes-podcast |
| `consumer_skill` | [`plugins/claude-code-release-podcast`](./plugins/claude-code-release-podcast) |
| `default_personas` | `plugins/podcast-skill/personas/defaults/` (Alex Chen + Sarah Kim) |
| `default_style` | `collaborative` |
| `category` | Technology |
| `language` | en |
| `time_zone` | Berlin |
| `notes` | One episode per Claude Code CHANGELOG entry. ID3 chapter markers per feature. Default filter drops bug fixes and internal optimizations. |

### daily-ai-espresso

| Field | Value |
| --- | --- |
| `key` | `daily-ai-espresso` |
| `slug` | `daily-ai-espresso` |
| `numeric_id` | `77097` |
| `title` | Daily AI Espresso |
| `feed_url` | https://feeds.transistor.fm/daily-ai-espresso |
| `dashboard_url` | https://dashboard.transistor.fm/shows/daily-ai-espresso |
| `consumer_skill` | [`plugins/daily-ai-espresso-podcast`](./plugins/daily-ai-espresso-podcast) (consumes HTML produced by [`plugins/ai-espresso-skill`](./plugins/ai-espresso-skill)) |
| `default_personas` | `plugins/podcast-skill/personas/defaults/` (Alex Chen + Sarah Kim) |
| `default_style` | `collaborative` |
| `category` | Technology |
| `language` | en |
| `time_zone` | Berlin |
| `notes` | One episode per day. Source: the AI Espresso morning briefing HTML in `./output/YYYY-MM-DD.html`. Target ~15 minutes covering 5–7 stories with one ID3 chapter per covered story. |

## Adding a new show

1. Create the show in the [Transistor dashboard](https://dashboard.transistor.fm/shows/new) (Configure a new podcast → fill metadata → Create My Podcast).
2. Note the resulting URL — the slug appears as `dashboard.transistor.fm/shows/<slug>`.
3. Confirm the numeric id and other attributes:
   ```bash
   set -a && . .env && set +a
   cd plugins/transistor && python3 -c "
   from transistor_mcp.client import request
   print(request('GET', '/shows/<slug>')['data'])
   "
   ```
4. Append a new entry to this file under "Shows" with all required fields.
5. Update the consumer skill (if any) to reference the new entry by `key`.
