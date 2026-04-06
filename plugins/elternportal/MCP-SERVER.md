# Eltern-Portal MCP Server

An MCP server that provides access to German school [Eltern-Portal](https://eltern-portal.org) data. Enables AI assistants to fetch substitution plans, parent letters, bulletin board announcements, and school calendar events.

## Tools

| Tool | Description |
|------|-------------|
| `check_login` | Verify that credentials are valid |
| `get_vertretungsplan` | Fetch the current substitution plan (uses Claude Haiku for HTML parsing) |
| `list_elternbriefe` | List all parent letters with metadata |
| `get_elternbrief` | Fetch a specific parent letter by number or title (PDF converted to markdown) |
| `get_schwarzes_brett` | Fetch bulletin board announcements |
| `get_termine` | Fetch upcoming school events and calendar entries (Schulaufgabenplan) |

## Prerequisites

- Python 3.10+
- An Eltern-Portal parent account
- An Anthropic API key (for vertretungsplan HTML parsing)

## Installation

```bash
cd plugins/elternportal
pip install -r elternportal_mcp/requirements.txt
```

## Configuration

The server loads credentials in this priority order:

### 1. Config file (recommended)

Create `~/.mcp-server-config/elternportal_mcp/.env`:

```
URL=https://yourschool.eltern-portal.org
USER=your@email.com
PASSWORD=your-password
ANTHROPIC_API_KEY=sk-ant-...
```

This is the simplest setup. The server reads this file on startup and uses the values as defaults. No other configuration needed.

### 2. Environment variables (override)

Environment variables take precedence over the config file. Both long and short names are supported:

| Long name (MCP config) | Short name (.env file) | Description |
|------------------------|----------------------|-------------|
| `ELTERNPORTAL_URL` | `URL` | School-specific Eltern-Portal URL |
| `ELTERNPORTAL_USER` | `USER` | Parent account email |
| `ELTERNPORTAL_PASSWORD` | `PASSWORD` | Parent account password |
| `ANTHROPIC_API_KEY` | `ANTHROPIC_API_KEY` | For Claude Haiku HTML parsing |

### 3. Plugin .mcp.json (auto-configured via marketplace)

When installed as a Cowork plugin, the `.mcp.json` is auto-discovered. It uses `${VAR}` syntax to pull from the environment. Set the env vars via `~/.claude/settings.json`:

```json
{
  "env": {
    "ELTERNPORTAL_URL": "https://yourschool.eltern-portal.org",
    "ELTERNPORTAL_USER": "your@email.com",
    "ELTERNPORTAL_PASSWORD": "your-password",
    "ANTHROPIC_API_KEY": "sk-ant-..."
  }
}
```

### Manual MCP client config

For non-plugin setups, add to your `.mcp.json`:

```json
{
  "elternportal": {
    "command": "python",
    "args": ["-m", "elternportal_mcp"],
    "cwd": "/path/to/plugins/elternportal",
    "env": {
      "ELTERNPORTAL_URL": "https://yourschool.eltern-portal.org",
      "ELTERNPORTAL_USER": "your@email.com",
      "ELTERNPORTAL_PASSWORD": "your-password",
      "ANTHROPIC_API_KEY": "sk-ant-..."
    }
  }
}
```

## License

MIT
