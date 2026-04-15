---
version: 2.1.108
source_url: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
kept_bullet_count: 9
skipped_bullet_count: 15
target_duration_minutes: 7
include_non_essential: false
---

# Claude Code v2.1.108 — Release Notes (Advanced User Cut)

A patch release, but genuinely workflow-relevant for power users: new cache-TTL knobs, a brand-new `/recap` command, the Skill tool can now invoke built-in slash commands, and a couple of defaults quietly moved in your favor.

## 1-hour prompt cache TTL

**Why:** The default 5-minute prompt cache expired between exchanges in long sessions, so every deep conversation kept re-paying for the same cached tokens.
**What:** Adds opt-in env var `ENABLE_PROMPT_CACHING_1H` for 1-hour cache TTL across API key, Bedrock, Vertex, and Foundry; deprecates `ENABLE_PROMPT_CACHING_1H_BEDROCK`; adds `FORCE_PROMPT_CACHING_5M` to force the old default back.
**How:** `export ENABLE_PROMPT_CACHING_1H=true` before starting Claude Code, or set it in `settings.json` env.

## /recap command for returning to a session

**Why:** Coming back to a long session meant scrolling the transcript or asking Claude "where were we" — manual context recovery every time.
**What:** A new recap feature that summarizes session state and unfinished work, auto-offered when returning to a session; configurable in `/config`.
**How:** Type `/recap` any time, or force it on for telemetry-disabled setups with `CLAUDE_CODE_ENABLE_AWAY_SUMMARY=true`.

## Skill tool can invoke built-in commands

**Why:** Claude couldn't reach its own built-in commands like `/init`, `/review`, `/security-review` during agentic work — you had to type them yourself even when the right thing to do was obvious.
**What:** The model now discovers and invokes the bundled slash commands through the Skill tool, the same mechanism that runs user-defined skills.
**How:** Automatic — no user action required. Ask for a PR review or a CLAUDE.md init and Claude runs the command itself.

## /undo is now an alias for /rewind

**Why:** Muscle-memory `/undo` got "unknown command" for users who expected the standard name.
**What:** `/undo` is wired as an alias for the existing `/rewind` command, which reverts Claude's last turn.
**How:** Type `/undo` — identical behavior to `/rewind`.

## /model warns before mid-conversation switches

**Why:** Switching models mid-conversation silently invalidates the prompt cache — the next response re-reads the full history uncached, costing real money and latency for no obvious reason.
**What:** `/model` now prints a warning before the switch takes effect so you can cancel or accept the cache-miss cost deliberately.
**How:** Run `/model` mid-conversation and read the prompt before confirming; nothing changes if you switch models only between sessions.

## /resume defaults to current directory

**Why:** The `/resume` picker listed sessions across every project, so picking up today's work in the current repo meant scrolling past stale sessions from other directories.
**What:** The picker now filters to sessions started in the current working directory by default, with a single keystroke to widen the scope.
**How:** Type `/resume` — press `Ctrl+A` inside the picker to show sessions from all projects.

## Better error messages

**Why:** When a run failed, it wasn't obvious whether you'd hit the API server's rate limit, your plan's usage limit, a transient 5xx, or just a typo in a slash command.
**What:** Error output now distinguishes server rate limits from plan limits, links 5xx/529 errors to `status.claude.com`, and suggests the closest match when you type an unknown slash command.
**How:** Automatic — the next failure will show richer, actionable text and a link where applicable.

## Startup warning when prompt caching is disabled

**Why:** `DISABLE_PROMPT_CACHING*` env vars silently kill caching, and users who inherited them from a shared dotfile often didn't know they were paying full price on every turn.
**What:** Claude Code now prints a warning at startup whenever any `DISABLE_PROMPT_CACHING*` env var is set, so the config is visible.
**How:** Automatic — if you see the warning, `unset DISABLE_PROMPT_CACHING` (or the provider-specific variant) in your shell.

## DISABLE_TELEMETRY no longer caps cache at 5 minutes

**Why:** Users who disabled telemetry assumed they were getting the default 1-hour cache TTL. They weren't — the flag silently forced a 5-minute fallback, doubling or tripling their cache-miss bill over long sessions.
**What:** Fix: `DISABLE_TELEMETRY` users now get the expected 1-hour TTL instead of the 5-minute fallback.
**How:** Automatic — upgrade to 2.1.108 and the telemetry-disabled setup inherits 1-hour caching. Pair with `ENABLE_PROMPT_CACHING_1H` if you want it explicit.

---

## Skipped (not covered in this episode)

Omitted from the dialogue per `bullet-filter-guide.md` — bug fixes, internal optimizations, and edge-case handling that don't change daily advanced-user workflows. Listed here for transparency.

- [internal] Reduced memory footprint for file reads, edits, and syntax highlighting by loading language grammars on demand
- [cosmetic] Added "verbose" indicator when viewing the detailed transcript (Ctrl+O)
- [fix] Fixed paste not working in the `/login` code prompt (regression in 2.1.105)
- [fix] Fixed Agent tool prompting for permission in auto mode when the safety classifier's transcript exceeded its context window
- [fix] Fixed Bash tool producing no output when `CLAUDE_ENV_FILE` (e.g. `~/.zprofile`) ends with a `#` comment line
- [fix] Fixed `claude --resume <session-id>` losing the session's custom name and color set via `/rename`
- [fix] Fixed session titles showing placeholder example text when the first message is a short greeting
- [fix] Fixed terminal escape codes appearing as garbage text in the prompt input after `--teleport`
- [fix] Fixed `/feedback` retry: pressing Enter to resubmit after a failure now works without first editing the description
- [fix] Fixed `--teleport` and `--resume <id>` precondition errors (e.g. dirty git tree, session not found) exiting silently instead of showing the error message
- [fix] Fixed Remote Control session titles set in the web UI being overwritten by auto-generated titles after the third message
- [fix] Fixed `--resume` truncating sessions when the transcript contained a self-referencing message
- [fix] Fixed transcript write failures (e.g., disk full) being silently dropped instead of being logged
- [fix] Fixed diacritical marks (accents, umlauts, cedillas) being dropped from responses when the `language` setting is configured
- [fix] Fixed policy-managed plugins never auto-updating when running from a different project than where they were first installed
