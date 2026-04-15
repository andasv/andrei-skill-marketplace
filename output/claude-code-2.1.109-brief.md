---
version: 2.1.109
source_url: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
kept_bullet_count: 1
skipped_bullet_count: 0
target_duration_minutes: 2
include_non_essential: true
---

# Claude Code v2.1.109 — Release Notes (Override: include_non_essential)

A one-bullet polish release. Default filter would have skipped this; published per explicit `include_non_essential=true` override.

## Live thinking progress hint

**Why:** The previous static "thinking…" indicator gave no signal of progress, so during long extended-thinking passes you couldn't tell if Claude was still working or quietly hung.
**What:** Adds a rotating progress hint to the extended-thinking indicator, so the visual updates while the model reasons rather than sitting frozen.
**How:** Automatic — no user action required. Works in any session with extended thinking on (the default); press `Ctrl+O` to also see the underlying reasoning text in verbose mode.
