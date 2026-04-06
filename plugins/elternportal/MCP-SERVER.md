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
| `get_termine` | Fetch upcoming school events and calendar entries |

## Prerequisites

- Python 3.10+
- An Eltern-Portal parent account
- An Anthropic API key (for vertretungsplan HTML parsing)

## Installation

```bash
cd mcp/elternportal
pip install -r requirements.txt
```

## Configuration

Add to your MCP client config (e.g. `.mcp.json`):

```json
{
  "mcpServers": {
    "elternportal": {
      "command": "python",
      "args": ["-m", "elternportal_mcp"],
      "cwd": "/path/to/andrei-skill-marketplace/mcp/elternportal",
      "env": {
        "ELTERNPORTAL_URL": "https://yourschool.eltern-portal.org",
        "ELTERNPORTAL_USER": "your@email.com",
        "ELTERNPORTAL_PASSWORD": "your-password",
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ELTERNPORTAL_URL` | Yes | School-specific Eltern-Portal URL |
| `ELTERNPORTAL_USER` | Yes | Parent account email |
| `ELTERNPORTAL_PASSWORD` | Yes | Parent account password |
| `ANTHROPIC_API_KEY` | Yes | For Claude Haiku HTML parsing (vertretungsplan) |

## License

MIT
