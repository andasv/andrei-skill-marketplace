# Andrei's Skill Marketplace

A plugin marketplace for [Claude Cowork](https://claude.ai/cowork). Install plugins with a single command to add new skills to your Cowork sessions.

## Available Plugins

| Plugin | Description | MCP Server |
|--------|-------------|------------|
| [`elternportal`](./plugins/elternportal/) | School data: substitutions, letters, bulletin board, calendar | Bundled (Python + FastMCP) — [`elternportal-mcp`](https://pypi.org/project/elternportal-mcp/) |
| [`aws-ses-mailer`](./plugins/aws-ses-mailer-skill/) | Send emails via AWS SES with HTML, attachments, CC/BCC & dry-run | [AWS API MCP](https://github.com/awslabs/mcp) (`awslabs.aws-api-mcp-server`) |
| [`podcast-skill`](./plugins/podcast-skill/) | Generate a 2-person AI podcast with ElevenLabs voice synthesis + optional ID3 chapter markers | [ElevenLabs MCP](https://github.com/elevenlabs/elevenlabs-mcp) |
| [`ai-espresso`](./plugins/ai-espresso-skill/) | Strategic morning AI news briefing as a self-contained HTML file | [Exa MCP](https://github.com/exa-labs/exa-mcp-server) |
| [`pushover`](./plugins/pushover/) | Urgent push notifications to your phone via Pushover | Bundled (Python + FastMCP) |
| [`transistor`](./plugins/transistor/) | Publish and manage podcast episodes on Transistor.fm (upload, create, publish, analytics) | Bundled (Python + FastMCP) |
| [`claude-code-release-podcast`](./plugins/claude-code-release-podcast/) | Auto-generate and publish a podcast episode for every Claude Code release, with ID3 chapter markers per feature | Chains `podcast-skill` + `transistor` |

## Installation

### 1. Add the marketplace

```
/plugin marketplace add andasv/andrei-skill-marketplace
```

### 2. Install a plugin

```
/plugin install elternportal@andrei-skill-marketplace
/plugin install aws-ses-mailer@andrei-skill-marketplace
/plugin install podcast-skill@andrei-skill-marketplace
/plugin install ai-espresso@andrei-skill-marketplace
/plugin install pushover@andrei-skill-marketplace
/plugin install transistor@andrei-skill-marketplace
/plugin install claude-code-release-podcast@andrei-skill-marketplace
```

### 3. Use the skills

Once installed, skills are auto-discovered. Ask naturally:

> "What substitutions are there today?"
> "Send an email to alice@example.com with the weekly report attached"
> "Create a podcast from today's AI news briefing"
> "Give me an AI espresso for this morning"
> "Send me a push notification about the deployment status"
> "Publish a podcast for the latest Claude Code release"

## Plugin Details

### elternportal

Access German school Eltern-Portal data via a bundled MCP server. Tools:
- **check_login** — Verify credentials
- **get_vertretungsplan** — Substitution plan (Claude Haiku parsing)
- **list_elternbriefe** / **get_elternbrief** — Parent letters (PDF→markdown)
- **get_schwarzes_brett** — Bulletin board announcements
- **get_termine** — Schulaufgabenplan (exam schedule)

**MCP server:** Bundled. Also published to PyPI as [`elternportal-mcp`](https://pypi.org/project/elternportal-mcp/) (`uvx elternportal-mcp@latest`).

**Prerequisites:** `ELTERNPORTAL_URL`, `ELTERNPORTAL_USER`, `ELTERNPORTAL_PASSWORD`, `ANTHROPIC_API_KEY` — set via env vars or `~/.mcp-server-config/elternportal_mcp/.env`.

### aws-ses-mailer

Sends emails through Amazon SES via the AWS API MCP Server. Features:
- Plain text and HTML email bodies
- Multiple recipients with TO, CC, and BCC
- File attachments via raw MIME
- Reply-To and sender display name
- Dry-run mode for testing

**Prerequisites:** [AWS API MCP Server](https://github.com/awslabs/mcp) (`awslabs.aws-api-mcp-server`) configured with SES permissions.

### podcast-skill

Generates a professional 2-person podcast from any written content in three phases:
1. Content analysis and topic ranking
2. Transcript generation with configurable personas
3. Audio synthesis via ElevenLabs TTS and segment merging
4. Optional ID3 chapter markers (drop a `<date>-chapters.json` in `output_dir`) — listeners can jump directly to each topic/feature

**Prerequisites:** Python 3 with `pydub` + `mutagen` (`pip install -r plugins/podcast-skill/scripts/requirements.txt`), ffmpeg, [ElevenLabs MCP](https://github.com/elevenlabs/elevenlabs-mcp) server configured.

### ai-espresso

Generates a strategic morning AI news briefing covering the last 24 hours. Searches for news from frontier labs and the broader AI industry, analyzes strategic significance, and outputs a self-contained HTML file.

**Prerequisites:** [Exa MCP](https://github.com/exa-labs/exa-mcp-server) server configured (for web search).

### pushover

Send urgent push notifications to your phone via a bundled Pushover MCP server. Features:
- **Emergency priority (2) by default** — repeats every 30s for up to an hour until acknowledged
- Custom sounds, URLs, device targeting
- Cross-skill integration — other skills can trigger alerts

**MCP server:** Bundled (Python + FastMCP).

**Prerequisites:** `PUSHOVER_APP_TOKEN` and `PUSHOVER_USER_KEY` — register an app at [pushover.net/apps/build](https://pushover.net/apps/build).

### transistor

Publish and manage podcast episodes on [Transistor.fm](https://transistor.fm/). Bundled Python FastMCP server exposes 13 tools: `upload_audio` (2-step S3 flow), `create_episode`, `update_episode`, `publish_episode`, `delete_episode` (unpublish — Transistor has no hard delete), `get_episode`, `list_episodes`, `get_show`, `list_shows`, `update_show`, plus three analytics tools. Handles 429 rate limits with exponential backoff. Show creation and hard delete are dashboard-only (Transistor API limitation).

**MCP server:** Bundled (Python + FastMCP).

**Prerequisites:** `TRANSISTOR_API_KEY` from [Transistor dashboard](https://dashboard.transistor.fm/account) → API, and `TRANSISTOR_SHOW_ID` (numeric id or slug) defaulted for single-podcast workflows.

### claude-code-release-podcast

Auto-generate and publish a podcast episode for every Claude Code release. Orchestrator skill that:
1. Fetches the official `anthropics/claude-code/CHANGELOG.md`.
2. **Filters out bug fixes and internal optimizations** — only bullets relevant to advanced users (new slash commands, env vars, behavior changes, capabilities) get covered (see the skill's `references/bullet-filter-guide.md`).
3. Researches each kept feature against the Anthropic docs and writes a **WHY / WHAT / HOW** brief.
4. Chains [`podcast-skill`](./plugins/podcast-skill/) for transcript + audio production.
5. Embeds **ID3 chapter markers — one per feature** — so listeners can jump directly to any topic.
6. Uploads + publishes via the [`transistor`](./plugins/transistor/) MCP.
7. Tracks processed releases in `./output/TRACKER.md` to prevent duplicates.

Supports default (newest unprocessed), `version=X.Y.Z`, `since=…/until=…` range backfill, and `dry_run=true` modes. Range/backfill gates on an explicit `yes, publish all N` confirmation.

**Prerequisites:** `podcast-skill` and `transistor` plugins installed, ElevenLabs MCP configured.

## Show Registry

Transistor show ids and per-show configuration live in [`SHOWS.md`](./SHOWS.md). Skills that publish via the [`transistor`](./plugins/transistor/) MCP read their show id from there rather than from `.env`. To add a new show: create it in the [Transistor dashboard](https://dashboard.transistor.fm/), then append an entry to `SHOWS.md` (see the file's "Adding a new show" section).

## Repository Structure

```
andrei-skill-marketplace/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── elternportal/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .mcp.json
│   │   ├── elternportal_mcp/        # Bundled MCP server
│   │   ├── pyproject.toml            # PyPI: elternportal-mcp
│   │   └── skills/elternportal/SKILL.md
│   ├── aws-ses-mailer-skill/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/aws-ses-mailer/SKILL.md
│   ├── podcast-skill/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/podcast-skill/SKILL.md
│   │   ├── personas/
│   │   ├── references/
│   │   └── scripts/                  # merge_audio.py + add_chapters.py
│   ├── ai-espresso-skill/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/ai-espresso/SKILL.md
│   │   ├── references/
│   │   └── evals/
│   ├── pushover/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .mcp.json
│   │   ├── pushover_mcp/             # Bundled MCP server
│   │   └── skills/pushover/SKILL.md
│   ├── transistor/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .mcp.json
│   │   └── transistor_mcp/           # Bundled MCP server (client.py + server.py)
│   └── claude-code-release-podcast/
│       ├── .claude-plugin/plugin.json
│       ├── references/               # why-what-how + filter + docs map
│       └── skills/claude-code-release-podcast/SKILL.md
└── README.md
```

## Adding a Plugin

1. Create a directory under `plugins/` with the standard Cowork plugin structure:
   - `.claude-plugin/plugin.json` — manifest with `name`, `version`, `description`, `author`
   - `skills/<skill-name>/SKILL.md` — one or more skill definitions
   - Optional: `.mcp.json`, `commands/`, `hooks/`, `scripts/`
2. Add an entry to `.claude-plugin/marketplace.json`
3. Open a PR

## License

MIT
