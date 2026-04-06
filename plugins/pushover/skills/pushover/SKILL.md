---
name: pushover
description: Send urgent push notifications to the user's phone via Pushover. Use when the user asks to be notified, alerted, or when another skill discovers something requiring immediate attention. Trigger words include notify, alert, pushover, urgent, push notification, ping me, let me know, immediate attention.
---

# Pushover Notifications

Send urgent push notifications to the user's phone via the Pushover MCP server. Use this skill when immediate attention is needed — schedule changes, critical alerts, time-sensitive information.

## MCP Dependencies

| MCP Server | Purpose | Required Tools |
|------------|---------|----------------|
| **pushover** (`pushover-mcp` on npm) | Send push notifications | `send` |

The MCP server handles authentication via app token and user key configured at startup.

## Tool: `send`

| Parameter | Required | Description |
|-----------|----------|-------------|
| `message` | Yes | The notification message body (max 1024 chars) |
| `title` | No | Message title (default: app name "Claude Assistant") |
| `priority` | No | -2 (lowest) to 2 (emergency). **Default to 1 (high)** for this skill |
| `sound` | No | Notification sound (e.g. `siren`, `spacealarm`, `persistent`) |
| `url` | No | Supplementary URL to include |
| `url_title` | No | Title for the URL |
| `device` | No | Target a specific device |

### Priority Levels

| Priority | Behavior | When to use |
|----------|----------|-------------|
| **1 (high)** | Bypasses quiet hours, always plays sound. **Use by default.** | Urgent info needing prompt action |
| **2 (emergency)** | Repeats until acknowledged | Critical: missed exams, cancelled classes, security alerts |
| **0 (normal)** | Standard notification | Informational updates, low urgency |
| **-1 (low)** | No sound/vibration | FYI only, can wait |

## Usage

### Standalone

> "Send me a push notification that the backup is done"
> "Alert me on my phone about the meeting change"
> "Ping me when you're done with the analysis"

Call `send` with the message and `priority: 1`.

### Cross-Skill Integration

Other skills can use Pushover to alert the user about urgent findings. Examples:

**From elternportal:**
> "Check the substitution plan and notify me if there are any changes"

1. Call `get_vertretungsplan` from elternportal MCP
2. If substitutions found for today/tomorrow, call pushover `send` with:
   - title: "Vertretungsplan"
   - message: summary of substitutions
   - priority: 1

**From ai-espresso:**
> "Generate the briefing and push me the top story"

1. Generate the briefing as normal
2. Call pushover `send` with:
   - title: "AI Espresso"
   - message: top headline + one-line summary
   - priority: 0

### Emergency Example

> "Alert me IMMEDIATELY if a Schulaufgabe is scheduled for tomorrow"

1. Call `get_termine` from elternportal MCP
2. Check for exams tomorrow
3. If found, call pushover `send` with:
   - title: "Schulaufgabe morgen!"
   - message: exam details
   - priority: 2
   - sound: "siren"
