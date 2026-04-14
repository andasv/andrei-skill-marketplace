---
name: claude-code-release-podcast
description: Generate and publish a podcast episode for every Claude Code release. Fetches the official CHANGELOG, filters out bug fixes and internal optimizations so only features relevant to advanced Claude Code users remain, researches each kept bullet with WHY/WHAT/HOW explanations, chains the podcast-skill for audio production, and publishes to Transistor.fm. Tracks processed releases in ./output/TRACKER.md to avoid duplicates. Use whenever the user mentions Claude Code release notes, a new Claude Code version, turning the changelog into audio, or says "release podcast". Default mode publishes only the newest unprocessed release.
---

# Claude Code Release Notes Podcast

Turn every Claude Code release into a published podcast episode, grounded in the official docs.

## Pipeline summary

```
CHANGELOG.md  →  research per bullet  →  brief.md  →  podcast-skill  →  mp3 + transcript  →  transistor MCP  →  TRACKER.md
```

## MCP Dependencies

| MCP Server | Purpose | Required Tools |
|------------|---------|----------------|
| **ElevenLabs** (via podcast-skill) | Text-to-speech | `mcp__ElevenLabs__text_to_speech`, `mcp__ElevenLabs__play_audio` |
| **Transistor** | Publishing episodes | `mcp__transistor__upload_audio`, `mcp__transistor__create_episode`, `mcp__transistor__publish_episode`, `mcp__transistor__list_episodes` |
| **Exa** (fallback research) | Web search when docs are ambiguous | `mcp__exa__web_search_exa` (or built-in `WebSearch`) |

## Tools used directly

- **WebFetch** — CHANGELOG and Anthropic docs pages
- **WebSearch** / **mcp__exa__web_search_exa** — fallback research per bullet
- **Read** / **Write** / **Edit** — TRACKER.md, brief files
- **Glob** — enumerate `./output/` for prior transcripts/audio
- **Bash** — invoke `podcast-skill` (file I/O chain)

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `version` | *(unset)* | Specific version (e.g. `2.1.108`). Overrides tracker; publishes regardless. |
| `since` | *(unset)* | Range mode: lower bound version (inclusive). |
| `until` | *(unset)* | Range mode: upper bound version (inclusive). Both `since` and `until` must be set together. |
| `dry_run` | `false` | Preview planned episodes without generating audio, publishing, or touching TRACKER.md. |
| `include_non_essential` | `false` | Include bug fixes and internal optimizations. By default these are filtered out (see `references/bullet-filter-guide.md`). Set `true` for an exhaustive changelog read-through. |
| `output_dir` | `./output/` | Where briefs, transcripts, audio, and TRACKER.md live. |
| `personas_dir` | podcast-skill default (Alex Chen + Sarah Kim) | Passed through to podcast-skill. |
| `style` | `collaborative` | Passed through to podcast-skill. |

**Mode precedence**: `version` > `since`/`until` > default (newest unprocessed).

## Execution Pipeline

Execute phases sequentially. Do not skip phases. Serialize per-version processing (no parallel publishes — Transistor rate limit is 10 req / 10 s).

---

### Phase 1: Load state

1. **Fetch the CHANGELOG**. WebFetch `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` with prompt: *"Return the raw markdown verbatim, preserving all `## <version>` headings and bullet lists."*

2. **Parse versions**. Split the markdown on lines matching `^## ` at the start of a line. For each block, capture:
   - `version` — the text after `## ` (e.g. `2.1.108`)
   - `bullets` — every top-level `- ` bullet in that block, preserving sub-bullets as continuation text on the parent bullet.
   Preserve CHANGELOG order (newest first).

3. **Load TRACKER**. Read `{output_dir}/TRACKER.md`. If missing, create it with this skeleton:

   ```markdown
   # Claude Code Release Podcast Tracker

   | Version | Processed   | Transcript | Audio | Transistor ID | Published URL | Status    |
   |---------|-------------|------------|-------|---------------|---------------|-----------|
   ```

   Parse the table into a set of processed versions.

4. **Determine target versions** based on mode:
   - **Default**: first version in CHANGELOG not in TRACKER. If all are tracked → print `Already up to date: latest tracked release is v{X.Y.Z}` and exit. This phase is the only exit point; do not continue.
   - **`version=X.Y.Z`**: that one version, even if already tracked. Warn the user: "Version X.Y.Z is already in TRACKER (status=…). Regenerating will create a new Transistor episode." Wait for confirmation before continuing.
   - **`since=A until=B`**: every CHANGELOG version between A and B inclusive that is not in TRACKER, newest-first.
   - **`dry_run=true`** applies on top of the above — it changes what happens in later phases, not how targets are selected.

5. **Bulk safety gate**. If `len(targets) > 1` (range or multiple-untracked backfill), print a preview table to the user:

   ```
   Planned episodes (N):
     - v2.1.108  ~4 min  "1-Hour Prompt Cache TTL + /recap"
     - v2.1.107  ~2 min  "Hook priority fix"
     - v2.1.105  ~3 min  "Bedrock region failover"
   Publish all N to Transistor.fm? Reply exactly: yes, publish all N
   ```

   Wait for the user's reply. Proceed only if they respond with the exact phrase `yes, publish all N` (with N substituted). Any other response aborts with zero side effects.

6. **Dry run gate**. If `dry_run=true`, print the preview table above and exit without writing briefs, calling podcast-skill, or publishing.

---

### Phase 2.0: Filter bullets (default behavior)

Unless `include_non_essential=true`, apply the filter from `references/bullet-filter-guide.md` to every bullet in the release. Each bullet is classified as either `KEEP` (feature relevant to an advanced Claude Code user) or `SKIP` (bug fix, minor UI polish, or internal optimization).

Quick rules:

- **SKIP** bullets that start with `Fixed ` (bug fixes) — unless the fix resolves a behavioral trap that actively changes user-visible behavior going forward (e.g. "Fixed subscribers with `DISABLE_TELEMETRY` falling back to 5-minute cache" — KEEP because it changes effective behavior under a common config).
- **SKIP** bullets describing internal performance optimizations with no API change (e.g. "Reduced memory footprint…", "loading grammars on demand").
- **SKIP** cosmetic-only UI tweaks with no workflow impact (e.g. a new indicator in the transcript view).
- **KEEP** bullets that add a new slash command, env var, flag, setting, hook event, tool, MCP capability, or model.
- **KEEP** bullets describing behavior changes that affect daily advanced usage (default changes, deprecations requiring action, `/foo` now warns / defaults / aliases).
- **KEEP** bullets that meaningfully change Claude Code's capabilities (e.g. "model can now discover slash commands via the Skill tool").

Split the bullet list into `kept_bullets` and `skipped_bullets`. `skipped_bullets` are recorded in the brief (bottom section) for transparency but are not researched and not covered in the podcast dialogue.

**Empty-keep short-circuit**: If `kept_bullets` is empty (the release is pure bug fixes), skip generation entirely. Append a TRACKER.md row with `Status=skipped-no-essential-changes` and no transcript/audio/Transistor columns, then continue to the next target version (or exit in default mode). Do NOT call podcast-skill. Do NOT publish.

**Edge case**: If `kept_bullets` has exactly 1 entry, still generate the episode — one meaningful feature deserves coverage. Minimum duration (2 min) applies.

### Phase 2: Per-release research

For each target version, for each bullet in `kept_bullets` (skipped bullets are not researched):

1. **Pick the primary doc URL** using `references/doc-slug-map.md`:
   - Slash command `/foo` → `https://docs.claude.com/en/docs/claude-code/slash-commands`
   - `UPPER_SNAKE` env var or "settings.json" / "permissions" → `https://docs.claude.com/en/docs/claude-code/settings`
   - "hook" / `PreToolUse` / `PostToolUse` → `https://docs.claude.com/en/docs/claude-code/hooks`
   - "MCP" / "Model Context Protocol" → `https://docs.claude.com/en/docs/claude-code/mcp`
   - "subagent", "agent type" → `https://docs.claude.com/en/docs/claude-code/sub-agents`
   - "plugin", "marketplace" → `https://docs.claude.com/en/docs/claude-code/plugins`
   - "skill", "SKILL.md" → `https://docs.claude.com/en/docs/claude-code/skills`
   - "Bedrock" / "Vertex" / "Foundry" → `https://docs.claude.com/en/docs/claude-code/third-party-integrations`
   - "IDE" / "VS Code" / "JetBrains" → `https://docs.claude.com/en/docs/claude-code/ide-integrations`
   - Unknown → root `https://docs.claude.com/en/docs/claude-code`

2. **WebFetch** the chosen URL with prompt: *"What is `{feature_term}`? Explain (1) why it exists — what problem it solves, (2) what it actually does, (3) the exact command/flag/env var to use it today. Quote syntax verbatim. If the page does not cover `{feature_term}`, say so."*

3. **If the fetch reports the feature isn't documented**, run ONE follow-up via `mcp__exa__web_search_exa` (preferred) or `WebSearch` with query `"claude code" {feature_term}`. Take the top result's summary. Max 2 search queries per bullet.

4. **Produce the WHY/WHAT/HOW block** per `references/why-what-how-guide.md`. Hard length cap: 25 words per sentence, three sentences total per bullet. If research still yields nothing, set WHAT to `Details not yet documented publicly.` and continue.

5. **Derive a bullet headline**: ≤60 chars, capitalized short sentence (e.g. `- Added /recap feature…` → `New /recap command`).

6. **Write the release brief** to `{output_dir}/claude-code-{version}-brief.md`:

   ```markdown
   ---
   version: 2.1.108
   source_url: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
   kept_bullet_count: 2
   skipped_bullet_count: 22
   target_duration_minutes: 2
   include_non_essential: false
   ---

   # Claude Code v2.1.108 — Release Notes (Advanced User Cut)

   ## New /recap command
   **Why:** …
   **What:** …
   **How:** `/recap`

   ## 1-hour prompt cache TTL
   **Why:** …
   **What:** …
   **How:** `ENABLE_PROMPT_CACHING_1H=true`

   ---

   ## Skipped (not covered in this episode)

   Omitted from the dialogue per `bullet-filter-guide.md` — bug fixes and internal optimizations that don't change daily advanced-user workflows. Listed here for transparency.

   - [fix] Fixed paste not working in the `/login` code prompt (regression in 2.1.105)
   - [fix] Fixed Agent tool prompting for permission in auto mode when the safety classifier's transcript exceeded its context window
   - [internal] Reduced memory footprint for file reads, edits, and syntax highlighting by loading language grammars on demand
   - …
   ```

   Tag each skipped bullet with a short reason: `[fix]`, `[internal]`, `[cosmetic]`, or `[other]`.

---

### Phase 3: Podcast generation

Compute duration: `ceil(kept_bullet_count * 0.75)` minutes, **minimum 2**. Skipped bullets do not count toward the duration.

Invoke `podcast-skill` with the brief as input. Since skills in this marketplace are invoked by natural language (not a hard-coded function call), **chain the skill by issuing a clear Task-level instruction in the conversation** describing the parameters:

> Run the podcast-skill with `input={output_dir}/claude-code-{version}-brief.md`, `duration={N}`, `topics=1`, `personas_dir={personas_dir or default}`, `output_dir={output_dir}`, `style={style}`.

podcast-skill's own pipeline handles persona loading, transcript generation, ElevenLabs TTS, and audio merging. It writes:
- Transcript: `{output_dir}/{YYYY-MM-DD}-podcast.md`
- Audio: `{output_dir}/{YYYY-MM-DD}-podcast.mp3`
- Segments dir: `{output_dir}/{YYYY-MM-DD}-segments/`

After podcast-skill returns, **capture both output paths** from its report. If podcast-skill fails (missing ElevenLabs MCP, voice_id missing, merge error), surface the error and do NOT proceed to publishing; the TRACKER stays untouched so the release can be retried.

---

### Phase 3.5: Embed chapter markers (one per feature)

Listeners jump by feature via ID3 `CTOC` + `CHAP` frames. Build the chapter map from the transcript and embed it into the merged mp3 before upload.

1. **Read the saved transcript** at `{output_dir}/{date}-podcast.md`.

2. **For each `## <headline>` section in the brief** (one per kept bullet), locate the first turn in the transcript whose dialogue text introduces that feature. Matching heuristic — scan turn texts for a **distinctive keyword** drawn from the headline:

   | Feature type | Keywords to match |
   | --- | --- |
   | Slash command | The literal `/recap`, `/undo`, `/model`, `/resume`, etc. |
   | Env var | The literal env var name: `ENABLE_PROMPT_CACHING_1H`, `DISABLE_TELEMETRY`, `CLAUDE_CODE_*` |
   | Capability change | Distinctive phrase from the headline: `Skill tool`, `built-in commands`, `error messages`, `startup warning` |

   The first turn containing any of the feature's keywords is that feature's `start_turn` (1-indexed to match `001_alex.mp3`). If the top feature is introduced only in the intro (which is typical — Alex leads with the headline in turn 1), set its `start_turn=1`.

3. **Sort chapters by `start_turn` ascending.** Chapter 1 must always be `start_turn=1` (the intro lives inside the first chapter). Non-monotonic or duplicate `start_turn` values are rejected by the script.

4. **Title each chapter** with the brief's `## <headline>` text, trimmed, trailing punctuation stripped, ≤ 60 chars.

5. **Write `{output_dir}/{date}-chapters.json`**:
   ```json
   {
     "chapters": [
       {"title": "1-hour prompt cache TTL", "start_turn": 1},
       {"title": "DISABLE_TELEMETRY cap fix", "start_turn": 5},
       {"title": "/recap command", "start_turn": 8}
     ]
   }
   ```

6. **Run the chapter embedder** on the merged mp3:
   ```bash
   python plugins/podcast-skill/scripts/add_chapters.py \
     --segments-dir {output_dir}/{date}-segments \
     --output {output_dir}/{date}-podcast.mp3 \
     --chapters-json {output_dir}/{date}-chapters.json
   ```
   The script prints one line per chapter with the computed `HH:MM:SS` start time. Verify the output matches expectations (chapter count equals kept bullet count, times are monotonic).

7. **Empty or single-chapter short-circuit**: if only one kept bullet made it through the filter, the script will skip writing chapters (the ID3 spec requires ≥ 2). That's fine — proceed to publish without chapters.

Chapter frames survive Transistor's audio re-processing (verified against episode 3170909 on 2026-04-14). No action needed on the Transistor side.

---

### Phase 4: Publish to Transistor

Skipped entirely when `dry_run=true`.

1. **Upload audio**:
   ```
   mcp__transistor__upload_audio(local_path="{output_dir}/{date}-podcast.mp3")
   → { audio_url, content_type, filename, size_bytes }
   ```

2. **Determine next episode number**:
   ```
   mcp__transistor__list_episodes(status="published", per=1)
   ```
   Take the first episode's `attributes.number`, add 1. If the show has no published episodes yet, start at 1.

3. **Build metadata**:
   - `title`: `Claude Code v{version} — {top_feature_tagline}`. Tagline ≤50 chars, derived from the most impactful bullet (usually the first). Examples: `New /recap command`, `1-hour prompt cache TTL`, `Bedrock region failover`.
   - `summary`: one plain-text sentence ≤200 chars summarizing the release. This is the directory-listing hook.
   - `description`: HTML built per `references/description-template.md`. One `<h3>` + three `<p>` (Why/What/How) per bullet, closing with the CHANGELOG and docs links.
   - `season`: `1` (single season).
   - `number`: computed in step 2.
   - `type`: `"full"`.
   - `keywords`: `"claude code, release notes, {top_1}, {top_2}"` — derive `top_1` and `top_2` from the most prominent features (slash command names, env var names, etc.).

4. **Create the episode (draft)**:
   ```
   mcp__transistor__create_episode(
     title=…, summary=…, description=…,
     audio_url=<from step 1>,
     season=1, number=<from step 2>, type="full",
     keywords=…,
   )
   → { data: { id: "<episode_id>", attributes: { share_url, media_url, … } } }
   ```
   Capture `data.id` and `data.attributes.share_url`.

5. **Publish live**:
   ```
   mcp__transistor__publish_episode(episode_id=<id>, status="published")
   ```
   Invoking this skill is itself the explicit user command to publish — consistent with podcast-skill's explicit-command rule.

---

### Phase 5: Update TRACKER and report

1. **Append** a row to `{output_dir}/TRACKER.md` (create the file with the skeleton from Phase 1 if still missing):

   Normal publish:
   ```markdown
   | 2.1.108 | 2026-04-14  | [md](./2026-04-14-podcast.md) | [mp3](./2026-04-14-podcast.mp3) | 12345 | https://share.transistor.fm/s/abc | published |
   ```

   Skipped release (pure bug fixes, zero kept bullets):
   ```markdown
   | 2.1.107 | 2026-04-14  | —          | —     | —             | —             | skipped-no-essential-changes |
   ```

   Use today's date in `YYYY-MM-DD`. Keep relative paths for portability. A `skipped-no-essential-changes` row still counts as "processed" for dedup — re-running default mode will not re-visit the release.

2. **Report to user** in chat:
   - Version just published
   - Transcript path
   - Audio file path
   - Transistor share URL
   - Approximate duration
   - For range/backfill mode: a running counter (`3 of 5 done`).

3. **Loop**: If there are more target versions (range/backfill), go back to Phase 2 for the next one. Do NOT parallelize. Respect rate limits.

---

## Error handling

- **CHANGELOG unreachable**: abort entire run with a clear error. Nothing written.
- **podcast-skill failure**: surface the error; keep the brief file on disk so the user can retry; DO NOT publish; DO NOT update TRACKER.
- **Transistor upload fails**: keep mp3 + transcript; DO NOT update TRACKER; surface error.
- **Transistor create fails**: same as above.
- **Transistor publish fails** (episode created but publish returned non-2xx): update TRACKER row with `status=draft` and the episode id/URL, so the user can retry publish later. Do not delete the draft.
- **Rate limit hit despite MCP backoff**: the MCP client already retries 429 with 1s/2s/4s backoff. If a call still fails with 429, sleep 15s and retry once manually before surfacing.
- **Ambiguous bullet**: fall back to `Details not yet documented publicly.` for WHAT; keep WHY/HOW as best-effort.
- **Ambiguous filter call (KEEP vs SKIP)**: default to KEEP. Under-filtering is safer than silently dropping a feature an advanced user would care about. The `references/bullet-filter-guide.md` explicit examples take precedence over the quick rules when they conflict.
- **All releases in a backfill range are pure bug fixes**: each gets a `skipped-no-essential-changes` TRACKER row, no episodes published, report lists the skipped versions in the final summary.

---

## Invocation examples

```
# Default: publish the newest unprocessed release
Publish a podcast for the latest Claude Code release.

# Specific version
Generate a Claude Code release podcast for version 2.1.108.

# Dry run
Preview the Claude Code release podcast for version 2.1.108 without publishing.

# Range / backfill
Backfill Claude Code release podcasts for versions 2.1.100 through 2.1.108.
```
