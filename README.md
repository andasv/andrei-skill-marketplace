# Andrei's Skill Marketplace

A plugin marketplace for [Claude Cowork](https://claude.ai/cowork). Install plugins with a single command to add new skills to your Cowork sessions.

## Available Plugins

| Plugin | Description | Keywords |
|--------|-------------|----------|
| `elternportal` | Substitution plans & parent letters from Eltern-Portal | school, vertretungsplan, elternbriefe |
| `aws-ses-mailer` | Send emails via AWS SES with HTML, attachments, CC/BCC & dry-run | email, aws, ses, mailer |
| `podcast-skill` | Generate a 2-person AI podcast with ElevenLabs voice synthesis | podcast, audio, elevenlabs, tts |
| `ai-espresso` | Strategic morning AI news briefing as a self-contained HTML file | ai-news, briefing, espresso |

## Installation

### 1. Add the marketplace

In a Claude Cowork session:

```
/plugin marketplace add andasv/andrei-skill-marketplace
```

### 2. Install a plugin

```
/plugin install elternportal@andrei-skill-marketplace
/plugin install aws-ses-mailer@andrei-skill-marketplace
/plugin install podcast-skill@andrei-skill-marketplace
/plugin install ai-espresso@andrei-skill-marketplace
```

### 3. Use the skills

Once installed, skills are auto-discovered. You can invoke them directly:

```
/elternportal:elternportal-vertretungsplan
/elternportal:elternportal-elternbriefe
/aws-ses-mailer:aws-ses-mailer
/podcast-skill:podcast-skill
/ai-espresso:ai-espresso
```

Or just ask naturally — Cowork will match your request to the right skill:

> "What substitutions are there today?"
> "Send an email to alice@example.com with the weekly report attached"
> "Create a podcast from today's AI news briefing"
> "Give me an AI espresso for this morning"

## Plugin Details

### elternportal

Fetches data from German school Eltern-Portal websites. Two skills:
- **elternportal-vertretungsplan** — Retrieves the current substitution plan
- **elternportal-elternbriefe** — Lists and fetches parent letters

**Prerequisites:** Eltern-Portal credentials configured via environment variables.

### aws-ses-mailer

Sends emails through Amazon SES. Features:
- Plain text and HTML email bodies
- Multiple recipients with TO, CC, and BCC
- File attachments with automatic MIME type detection
- Reply-To and sender display name
- Dry-run mode for testing

**Prerequisites:** AWS CLI, Python 3, verified SES sender identity. Set `SES_FROM_ADDRESS` and `SES_AWS_REGION` environment variables.

### podcast-skill

Generates a professional 2-person podcast from any written content in three phases:
1. Content analysis and topic ranking
2. Transcript generation with configurable personas
3. Audio synthesis via ElevenLabs TTS and segment merging

**Prerequisites:** Python 3 with pydub, ffmpeg, ElevenLabs MCP server configured.

### ai-espresso

Generates a strategic morning AI news briefing covering the last 24 hours. Searches for news from frontier labs and the broader AI industry, analyzes strategic significance, and outputs a self-contained HTML file.

**Prerequisites:** Exa MCP server configured (for web search).

## Repository Structure

```
andrei-skill-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace manifest (lists all plugins)
├── plugins/
│   ├── elternportal/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       # Plugin manifest
│   │   └── skills/
│   │       ├── elternportal-vertretungsplan/
│   │       │   └── SKILL.md
│   │       └── elternportal-elternbriefe/
│   │           └── SKILL.md
│   ├── aws-ses-mailer-skill/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/
│   │   │   └── aws-ses-mailer/
│   │   │       └── SKILL.md
│   │   └── scripts/
│   │       ├── send_ses_email.sh
│   │       ├── send_ses_raw.py
│   │       └── check_ses_identity.sh
│   ├── podcast-skill/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── skills/
│   │   │   └── podcast-skill/
│   │   │       └── SKILL.md
│   │   ├── personas/
│   │   ├── references/
│   │   └── scripts/
│   │       └── merge_audio.py
│   └── ai-espresso-skill/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── skills/
│       │   └── ai-espresso/
│       │       └── SKILL.md
│       ├── references/
│       └── evals/
└── README.md
```

## Adding a Plugin

To add a new plugin to this marketplace:

1. Create a directory under `plugins/` with the standard Cowork plugin structure:
   - `.claude-plugin/plugin.json` — manifest with `name`, `version`, `description`, `author`
   - `skills/<skill-name>/SKILL.md` — one or more skill definitions
   - Optional: `commands/`, `hooks/`, `scripts/`, `.mcp.json`
2. Add an entry to `.claude-plugin/marketplace.json`
3. Open a PR

## License

MIT
