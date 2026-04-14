# Bullet Keyword → Anthropic Docs URL Map

Heuristic guide for Phase 2 research. Given a CHANGELOG bullet, look for these patterns to pick the first WebFetch URL. If the pattern doesn't match, fall back to WebSearch.

Base URL: `https://docs.claude.com/en/docs/claude-code/`

## Slash commands

| Bullet contains | WebFetch target |
| --- | --- |
| `/<name>` (e.g. `/recap`, `/config`, `/model`) | `https://docs.claude.com/en/docs/claude-code/slash-commands` |
| "slash command" | same |

## Environment variables

| Bullet contains | WebFetch target |
| --- | --- |
| `<UPPER_SNAKE_CASE>` env var name (e.g. `ENABLE_PROMPT_CACHING_1H`, `ANTHROPIC_API_KEY`) | `https://docs.claude.com/en/docs/claude-code/settings` |

## Hooks / settings

| Bullet contains | WebFetch target |
| --- | --- |
| "hook", "PostToolUse", "PreToolUse", "UserPromptSubmit" | `https://docs.claude.com/en/docs/claude-code/hooks` |
| "settings.json" | `https://docs.claude.com/en/docs/claude-code/settings` |
| "permissions", "allow", "deny" | `https://docs.claude.com/en/docs/claude-code/settings` |

## MCP

| Bullet contains | WebFetch target |
| --- | --- |
| "MCP server", "Model Context Protocol" | `https://docs.claude.com/en/docs/claude-code/mcp` |

## Agent / plugins / skills

| Bullet contains | WebFetch target |
| --- | --- |
| "subagent", "Task tool", "agent type" | `https://docs.claude.com/en/docs/claude-code/sub-agents` |
| "plugin", "marketplace" | `https://docs.claude.com/en/docs/claude-code/plugins` |
| "skill", "SKILL.md" | `https://docs.claude.com/en/docs/claude-code/skills` |

## Providers / deployments

| Bullet contains | WebFetch target |
| --- | --- |
| "Bedrock", "Vertex", "Foundry", "Azure" | `https://docs.claude.com/en/docs/claude-code/third-party-integrations` |
| "IDE", "VS Code", "JetBrains" | `https://docs.claude.com/en/docs/claude-code/ide-integrations` |

## Fallback strategy

When no pattern matches:
1. Try the root docs page: `https://docs.claude.com/en/docs/claude-code`
2. If still unclear, run `mcp__exa__web_search_exa` or `WebSearch` with `"claude code" <bullet keyword>`. Max 2 queries per bullet.
3. If research still yields nothing, write the WHAT line as `Details not yet documented publicly.` and keep the WHY/HOW as best-effort.
