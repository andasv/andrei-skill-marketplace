# elternportal

Access German school [Eltern-Portal](https://www.eltern-portal.org/) data from Claude Cowork. Covers substitution plans (Vertretungsplan), parent letters (Elternbriefe), bulletin board (Schwarzes Brett), and school calendar (Termine).

## Features

- Structured substitution plans with per-period details
- Parent letter listing + full-content fetch (PDF → markdown conversion via Claude Haiku)
- Bulletin board announcements
- School calendar (Schulaufgabenplan / exam dates)
- Secure credential handling via env vars

## Prerequisites

- Claude Code + the marketplace added
- A valid Eltern-Portal account for your school
- [uv](https://docs.astral.sh/uv/) installed on PATH (for `uvx`) — the server is published to PyPI as [`elternportal-mcp`](https://pypi.org/project/elternportal-mcp/)
- An Anthropic API key (for PDF → markdown conversion)
- Environment variables set in the repo-root `.env`:
  ```
  ELTERNPORTAL_URL=https://<your-school>.eltern-portal.org
  ELTERNPORTAL_USER=<portal username>
  ELTERNPORTAL_PASSWORD=<portal password>
  ELTERNPORTAL_ANTHROPIC_API_KEY=<anthropic api key>
  ```

## Install

```
/plugin marketplace update andrei-skill-marketplace
/plugin install elternportal@andrei-skill-marketplace
```

## Usage

Trigger the skill with natural language — German or English both work:

```
What substitutions are there today?
Show me the latest Elternbrief.
Is there a parent letter about Mensa?
What's on the bulletin board?
What school events are coming up?
```

## MCP tools

| Tool | Purpose |
|---|---|
| `check_login` | Verify credentials resolve a session; use to diagnose auth issues |
| `get_vertretungsplan` | Current substitution plan with per-period entries (teacher, substitute, room, subjects) |
| `list_elternbriefe` | List all parent letters with number, title, date, confirmation status |
| `get_elternbrief` | Fetch a letter by `number` or case-insensitive `title` substring — returns markdown (PDF auto-converted) |
| `get_schwarzes_brett` | Bulletin board announcements with title + body |
| `get_termine` | Schulaufgabenplan / upcoming school events with date + description |

## MCP server

Published to PyPI as [`elternportal-mcp`](https://pypi.org/project/elternportal-mcp/) and launched via `uvx elternportal-mcp@latest`. The plugin's `.mcp.json` wires up the env var mapping automatically.

## Project structure

```
elternportal/
├── .claude-plugin/plugin.json
├── .mcp.json                       # Launches via uvx
├── elternportal_mcp/               # Server source (also the PyPI package)
├── pyproject.toml                  # PyPI publishing metadata
├── .github/workflows/              # OIDC-based PyPI release pipeline
└── skills/elternportal/SKILL.md    # Natural-language skill wrapper
```

## Cross-skill integration

Combine with the [`pushover`](../pushover/) plugin for urgent notifications:

```
Check substitutions and push me any changes for tomorrow.
Alert me immediately if a Schulaufgabe is scheduled for tomorrow.
```

## License

MIT
