# Bullet Filter Guide

Decide whether each CHANGELOG bullet is `KEEP` or `SKIP` for the podcast.

**Audience assumption**: listener is an advanced Claude Code user — uses it daily, already knows the basics, cares about features that change their workflow, trusts that bug fixes ship.

## Decision rules

### KEEP — bullet affects what an advanced user can do or how they work

- Adds a **new slash command** (`/foo`, `/bar`) or changes an existing one's behavior meaningfully.
- Adds a **new environment variable**, flag, or settings.json key (especially `UPPER_SNAKE_CASE`).
- Adds a **new hook event**, tool, MCP capability, subagent type, plugin mechanism, or IDE integration.
- Introduces a **new model** or changes which models are routed/available.
- Changes a **default** that affects daily usage (e.g. "`/resume` now defaults to current directory sessions").
- **Deprecates** something that still works but requires migration (e.g. env var rename).
- Adds **security-relevant** visibility (e.g. "warning at startup when prompt caching is disabled") — advanced users need to know about config footguns.
- Gives the model a **new capability** or integration surface (e.g. "model can now discover and invoke built-in slash commands via the Skill tool").
- Changes **error handling / retry / UX** in a way that advanced users will feel (e.g. "improved `/model` to warn before switching mid-conversation").

### SKIP — bullet is noise for an advanced user

- **Bug fixes** (starts with `Fixed `, `Resolved `) — the feature worked before and works now, no daily impact. **Exception**: see the "Fix-that-is-actually-a-behavior-change" rule below.
- **Internal optimizations** with no user-facing API change (memory footprint, loading on demand, dependency bumps, internal refactors). Phrases like "reduced memory footprint", "improved performance", "loading X on demand" without a new knob to turn.
- **Cosmetic UI tweaks** that don't change workflow (a new indicator icon, spacing fix, color adjustment) — unless the indicator exposes previously-hidden state.
- **Regression fixes** — if the bullet says `(regression in X.Y.Z)`, it's just restoring prior behavior. Skip.
- **Edge case handling** for rare config combinations (e.g. "fixed X when zprofile ends with a comment").
- **Policy / enterprise-config** fixes the single-user advanced listener doesn't hit.

## Fix-that-is-actually-a-behavior-change rule

Some bullets look like fixes but actually change effective behavior going forward in a way that affects existing configs. These are KEEP:

> "Fixed subscribers who set `DISABLE_TELEMETRY` falling back to 5-minute prompt cache TTL instead of 1 hour"

The user has `DISABLE_TELEMETRY` set right now, assumes they're getting 1h cache. They weren't. Now they are. That's a behavior change that matters → **KEEP**.

Heuristic: if the fix changes the **effective behavior** of a common config that a user is likely running today, keep it. If the fix just stops a crash or restores obvious expected behavior, skip it.

## Examples from Claude Code v2.1.108

### KEEP
| Bullet | Reason |
| --- | --- |
| Added `ENABLE_PROMPT_CACHING_1H` env var + `FORCE_PROMPT_CACHING_5M` | New env vars, new opt-in behavior. |
| Added `/recap` feature (slash command + `CLAUDE_CODE_ENABLE_AWAY_SUMMARY`) | New slash command + new env var. |
| Model can now discover built-in slash commands via the Skill tool | New model capability. |
| `/undo` is now an alias for `/rewind` | Command surface change. |
| Improved `/model` to warn before switching mid-conversation | UX change that affects daily usage and cache hit rate. |
| Improved `/resume` picker to default to current directory | Default change; `Ctrl+A` to override. |
| Improved error messages (rate limit vs plan limit, 5xx links, unknown slash command suggestions) | Visibly different UX advanced users will see during failures. |
| Added warning at startup when prompt caching is disabled via `DISABLE_PROMPT_CACHING*` | Config footgun visibility. |
| Fixed `DISABLE_TELEMETRY` falling back to 5-min TTL instead of 1 hour | Behavior change for a common config (see Fix-that-is-actually-a-behavior-change). |

### SKIP
| Bullet | Reason tag |
| --- | --- |
| Reduced memory footprint for file reads, edits, syntax highlighting | `[internal]` |
| Added "verbose" indicator when viewing the detailed transcript (Ctrl+O) | `[cosmetic]` |
| Fixed paste not working in the `/login` code prompt (regression in 2.1.105) | `[fix]` + regression |
| Fixed Agent tool prompting in auto mode when safety classifier transcript exceeds context | `[fix]` edge case |
| Fixed Bash tool producing no output when `CLAUDE_ENV_FILE` ends with `#` | `[fix]` edge case |
| Fixed `claude --resume <session-id>` losing custom name/color | `[fix]` |
| Fixed session titles showing placeholder text on short greetings | `[fix]` |
| Fixed terminal escape codes after `--teleport` | `[fix]` |
| Fixed `/feedback` retry requiring an edit first | `[fix]` |
| Fixed `--teleport` and `--resume <id>` silent exit on precondition errors | `[fix]` |
| Fixed Remote Control session titles being overwritten | `[fix]` |
| Fixed `--resume` truncation on self-referencing transcripts | `[fix]` edge case |
| Fixed transcript write failures being silently dropped | `[fix]` |
| Fixed diacritical marks dropped when `language` setting is configured | `[fix]` |
| Fixed policy-managed plugins never auto-updating across projects | `[fix]` enterprise edge case |

## Tag vocabulary (for the Skipped section of the brief)

- `[fix]` — a plain bug fix.
- `[internal]` — internal optimization, refactor, or dependency change.
- `[cosmetic]` — pure UI/presentation tweak with no workflow impact.
- `[other]` — doesn't fit the above categories but was skipped (rare; explain in the bullet if used).

## When in doubt

**Default to KEEP.** Under-filtering is safer than silently dropping a feature a user would care about. The podcast's value is coverage of things that matter; a marginal feature in an episode is less bad than a missed feature.
