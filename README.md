# Andrei's Skill Marketplace

A plugin marketplace for [Claude Cowork](https://claude.ai/cowork). Install plugins with a single command to add new skills to your Cowork sessions.

## Available Plugins

| Plugin | Description | MCP Server |
|--------|-------------|------------|
| `elternportal` | School data: substitutions, letters, bulletin board, calendar | Bundled (Python + FastMCP) |
| `aws-ses-mailer` | Send emails via AWS SES with HTML, attachments, CC/BCC & dry-run | [AWS API MCP](https://github.com/awslabs/mcp) (`awslabs.aws-api-mcp-server`) |
| `podcast-skill` | Generate a 2-person AI podcast with ElevenLabs voice synthesis | [ElevenLabs MCP](https://github.com/elevenlabs/elevenlabs-mcp) |
| `ai-espresso` | Strategic morning AI news briefing as a self-contained HTML file | [Exa MCP](https://github.com/exa-labs/exa-mcp-server) |
| `pushover` | Urgent push notifications to your phone via Pushover | Bundled (Python + FastMCP) |

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
```

### 3. Use the skills

Once installed, skills are auto-discovered. Ask naturally:

> "What substitutions are there today?"
> "Send an email to alice@example.com with the weekly report attached"
> "Create a podcast from today's AI news briefing"
> "Give me an AI espresso for this morning"
> "Send me a push notification about the deployment status"

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

**Prerequisites:** Python 3 with pydub, ffmpeg, [ElevenLabs MCP](https://github.com/elevenlabs/elevenlabs-mcp) server configured.

### ai-espresso

Generates a strategic morning AI news briefing covering the last 24 hours. Searches for news from frontier labs and the broader AI industry, analyzes strategic significance, and outputs a self-contained HTML file.

**Prerequisites:** [Exa MCP](https://github.com/exa-labs/exa-mcp-server) server configured (for web search).

### pushover

Send urgent push notifications to your phone via a bundled Pushover MCP server. Features:
- High priority by default (bypasses quiet hours)
- Emergency priority with repeat until acknowledged
- Cross-skill integration — other skills can trigger alerts
- Custom sounds, URLs, device targeting

**MCP server:** Bundled (Python + FastMCP).

**Prerequisites:** `PUSHOVER_APP_TOKEN` and `PUSHOVER_USER_KEY` — register an app at [pushover.net/apps/build](https://pushover.net/apps/build).

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
│   │   └── scripts/
│   ├── ai-espresso-skill/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/ai-espresso/SKILL.md
│   │   ├── references/
│   │   └── evals/
│   └── pushover/
│       ├── .claude-plugin/plugin.json
│       ├── .mcp.json
│       ├── pushover_mcp/             # Bundled MCP server
│       └── skills/pushover/SKILL.md
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
