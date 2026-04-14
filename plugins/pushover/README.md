# pushover

Send urgent push notifications to your phone via [Pushover](https://pushover.net/). Ships with a bundled Python MCP server — no npm dependency, no external host.

## Features

- High-priority alerts that bypass Quiet Hours
- **Emergency priority (2) by default**, repeating until acknowledged
- Custom sounds, titles, device targeting, and supplementary URLs
- Cross-skill integration — other skills can trigger alerts (see examples)

## Prerequisites

- An active [Pushover account](https://pushover.net/) and a registered app at [pushover.net/apps/build](https://pushover.net/apps/build)
- Python 3 with `fastmcp` and `requests` on PATH
- Environment variables set in the repo-root `.env`:
  ```
  PUSHOVER_APP_TOKEN=<your_app_token>
  PUSHOVER_USER_KEY=<your_user_key>
  ```

The MCP server is launched automatically via `.mcp.json` when the plugin is enabled.

## Install

```
/plugin marketplace update andrei-skill-marketplace
/plugin install pushover@andrei-skill-marketplace
```

## Usage

Trigger the skill with natural language — "notify", "alert", "ping me", "urgent", etc.:

```
Send me a push notification that the deploy finished.
Alert me on my phone if the build fails tonight.
Ping me when the audit is ready to review.
```

## MCP tool: `send`

| Parameter | Required | Default | Description |
|---|---|---|---|
| `message` | Yes | — | Notification body (max 1024 chars) |
| `title` | No | app name | Message title shown in the banner |
| `priority` | No | `2` (emergency) | `-2` lowest → `2` emergency. Emergency repeats every 30s for up to 1h until acknowledged. |
| `sound` | No | `persistent` | Pushover sound name (`siren`, `spacealarm`, `persistent`, etc.) |
| `url` | No | — | Supplementary URL shown in the notification |
| `url_title` | No | — | Label for the supplementary URL |
| `device` | No | all devices | Target a specific device name |

Priority reference:

| Priority | Behavior |
|---|---|
| `2` Emergency (default) | Repeats every 30s for up to 1h until acknowledged; bypasses quiet hours |
| `1` High | Plays sound, bypasses quiet hours |
| `0` Normal | Honors quiet hours |
| `-1` Low | No sound/vibration |
| `-2` Lowest | Silent notification |

## Cross-skill integration

Other skills can call `send` to surface urgent findings to the user:

- **elternportal** — alert on schedule changes, exam announcements
- **ai-espresso** — push the top AI headline after the morning briefing
- Any skill that discovers something time-sensitive during its run

## Project structure

```
pushover/
├── .claude-plugin/plugin.json
├── .mcp.json                    # Server config (python -m pushover_mcp)
├── pushover_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   └── server.py                # FastMCP server with the `send` tool
└── skills/pushover/SKILL.md     # Natural-language skill wrapper
```

## License

MIT
