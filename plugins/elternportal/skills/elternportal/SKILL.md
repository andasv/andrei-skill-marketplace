---
name: elternportal
description: Access Eltern-Portal school data — substitution plans (Vertretungsplan), parent letters (Elternbriefe), bulletin board (Schwarzes Brett), and school calendar (Termine). Use when the user asks about substitutions, schedule changes, parent letters, school announcements, or upcoming events.
---

# Eltern-Portal

Access school data from Eltern-Portal via MCP tools. Covers substitution plans, parent letters, bulletin board, and school calendar.

## MCP Dependencies

This skill requires the following MCP server to be configured:

| MCP Server | Purpose | Required Tools |
|------------|---------|----------------|
| **elternportal** | Access Eltern-Portal school data | `check_login`, `get_vertretungsplan`, `list_elternbriefe`, `get_elternbrief`, `get_schwarzes_brett`, `get_termine` |

The MCP server handles authentication internally via environment variables. No credentials need to be passed in tool calls.

## Available Tools

### check_login
Verify that credentials are valid and login succeeds. Use this to diagnose connection issues.

### get_vertretungsplan
Fetch the current substitution plan. Returns structured data with:
- Class name and last updated timestamp
- List of days with substitutions (period, affected teacher, substitute, subjects, room, info)

### list_elternbriefe
List all parent letters with metadata: entry number, title, date, classes, confirmation status, and whether a PDF is available.

### get_elternbrief
Fetch a specific parent letter. Pass either:
- `number` — exact entry number (e.g. 134)
- `title` — case-insensitive substring search (e.g. "Mensa")

Returns the full content as markdown (PDF automatically converted).

### get_schwarzes_brett
Fetch bulletin board announcements with title and content text.

### get_termine
Fetch upcoming school events and calendar entries with date, title, and description.

## Usage Examples

> "What substitutions are there today?"
→ Call `get_vertretungsplan`, then summarize the substitutions for today.

> "Show me the latest Elternbrief"
→ Call `list_elternbriefe`, find the highest number, then call `get_elternbrief` with that number.

> "Is there a parent letter about Mensa?"
→ Call `get_elternbrief` with `title="Mensa"`.

> "What's on the bulletin board?"
→ Call `get_schwarzes_brett`.

> "What school events are coming up?"
→ Call `get_termine`.
