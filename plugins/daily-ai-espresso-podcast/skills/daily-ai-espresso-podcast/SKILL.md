---
name: daily-ai-espresso-podcast
description: Turn the daily AI Espresso morning briefing into a published 15-minute podcast episode. Reads the latest AI Espresso HTML from the user's ./output/ directory, chains podcast-skill to generate a two-host conversation with per-story chapter markers, and publishes to the "Daily AI Espresso" show on Transistor.fm. Tracks processed days in AI_ESPRESSO_TRACKER.md to prevent duplicates. Use whenever the user mentions a daily AI podcast, AI Espresso podcast, turning today's briefing into audio, or says "publish daily AI espresso".
---

# Daily AI Espresso Podcast

Turn every AI Espresso briefing into a published 15-minute podcast episode.

## Pipeline summary

```
./output/<date>.html  →  podcast-skill (15 min, ~6 topics)  →  mp3 + transcript
                            │
                            ▼ map stories → turns, write chapters.json
                       add_chapters.py → mp3 with CTOC/CHAP frames
                            │
                            ▼ transistor MCP upload + create + publish
                       AI_ESPRESSO_TRACKER.md updated
```

## MCP Dependencies

| MCP Server | Purpose | Required Tools |
|---|---|---|
| **ElevenLabs** (via podcast-skill) | Text-to-speech | `mcp__ElevenLabs__text_to_speech`, `mcp__ElevenLabs__play_audio` |
| **Transistor** | Publishing episodes | `mcp__transistor__upload_audio`, `mcp__transistor__create_episode`, `mcp__transistor__publish_episode`, `mcp__transistor__list_episodes` |

## Tools used directly

- **Read** / **Write** / **Edit** — AI_ESPRESSO_TRACKER.md, transcripts
- **Glob** — find latest `./output/YYYY-MM-DD.html`
- **Bash** — invoke `add_chapters.py` and `merge_audio.py` indirectly via podcast-skill

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `date` | *(unset)* | Specific date in `YYYY-MM-DD`. Overrides tracker; publishes regardless. |
| `since` | *(unset)* | Range mode: lower bound date (inclusive). |
| `until` | *(unset)* | Range mode: upper bound date (inclusive). Both must be set together. |
| `dry_run` | `false` | Preview the planned episode without generating audio, publishing, or touching the tracker. |
| `output_dir` | `./output/` | Where AI Espresso HTML lives + where briefs/transcripts/audio/tracker get written. |
| `personas_dir` | podcast-skill default (Alex Chen + Sarah Kim) | Passed to podcast-skill. |
| `style` | `collaborative` | Passed to podcast-skill. |
| `duration` | `15` | Target episode length in minutes. Override only if you know what you're doing. |
| `topics` | `6` | Number of stories to cover in dialogue. |

**Mode precedence**: `date` > `since`/`until` > default (newest unprocessed `<date>.html`).

## Configuration

Hard-coded values for this skill (sourced from [`/SHOWS.md`](../../../../SHOWS.md) → `daily-ai-espresso` entry — update that file first if anything changes in the dashboard):

| Constant | Value |
|---|---|
| `SHOW_ID` | `daily-ai-espresso` (numeric: `77097`) |
| `SHOW_TITLE` | `Daily AI Espresso` |
| `SEASON` | `1` |
| `EPISODE_TYPE` | `full` |
| `DEFAULT_DURATION_MIN` | `15` |
| `DEFAULT_TOPIC_COUNT` | `6` |
| `TRACKER_FILENAME` | `AI_ESPRESSO_TRACKER.md` |

## Execution Pipeline

Execute phases sequentially. Serialize per-date processing (Transistor rate limit is 10 req / 10 s).

---

### Phase 1: Load state

1. **Find candidate HTML files** in `{output_dir}` matching `YYYY-MM-DD.html` (use Glob).
2. **Read** `{output_dir}/AI_ESPRESSO_TRACKER.md`. If missing, create with this skeleton:
   ```markdown
   # Daily AI Espresso Podcast Tracker

   | Date | Processed   | Source HTML | Transcript | Audio | Transistor ID | Published URL | Status    |
   |------|-------------|-------------|------------|-------|---------------|---------------|-----------|
   ```
3. Determine target dates by mode:
   - **Default**: newest `<date>.html` not in tracker. Empty target set → print `Already up to date: latest tracked AI Espresso episode is YYYY-MM-DD` and exit cleanly.
   - **`date=YYYY-MM-DD`**: that one date. Warn if already in tracker; require user confirmation to regenerate (creates a duplicate Transistor episode).
   - **`since=A until=B`**: every `<date>.html` in `[A, B]` not in tracker, oldest-first (chronological order matches feed order).

4. **Bulk safety gate**: if `len(targets) > 1`, print preview table:
   ```
   Planned episodes (N):
     - 2026-04-13  ~15 min  "<top story tagline>"
     - 2026-04-14  ~15 min  "<top story tagline>"
   Publish all N to Transistor? Reply exactly: yes, publish all N
   ```
   Proceed only on exact match. Anything else aborts with zero side effects.

5. **Dry run gate**: if `dry_run=true`, print preview and exit without writing or publishing.

---

### Phase 2: Generate the podcast

For each target date:

1. **Verify the source HTML** is readable. Check it has at least one `.section.frontier` `.item` and at least 3 total items across all sections. If thinner, the briefing is too sparse for a 15-min episode — abort that date with a tracker row `Status=skipped-thin-briefing`.

2. **Invoke `podcast-skill`** with:
   - `input`: `{output_dir}/{date}.html`
   - `duration`: `15`
   - `topics`: `6` (or whatever the user passed)
   - `personas_dir`: default
   - `output_dir`: `{output_dir}`
   - `style`: `collaborative`

   podcast-skill's content-analysis phase already understands the AI Espresso HTML structure (it's the originally-intended input). It will:
   - Extract items from `.item` divs across all `.section` blocks.
   - Rank by strategic significance / discussion potential / accessibility.
   - Pick the top `topics` items.
   - Generate beats following surprise → analysis → implications → forward-look.
   - Produce a transcript (~2,250 words for 15 min).
   - Synthesize TTS via ElevenLabs and merge into `{output_dir}/{date}-podcast.mp3`.

   Apply the **selection priority** from `references/coverage-guide.md` if the model needs guidance:
   1. Frontier Labs items first (always)
   2. Anthropic/OpenAI official news (cover all in-window)
   3. Models & Research with practical impact
   4. Products & Tools developers will use this week
   5. Industry & Business only if landscape-shifting
   6. Skip Germany and SA picks unless exceptional or user-requested

3. **Capture output paths** from podcast-skill's report. If it failed, surface the error and do NOT publish; tracker stays untouched.

---

### Phase 3: Embed chapter markers (one per covered story)

1. Read `{output_dir}/{date}-podcast.md` (the transcript).

2. Identify each *covered* story by scanning the transcript for distinctive keywords. Common keyword sources:
   - The story's `<h3>` text from the source HTML (often a product name, model name, or company + verb).
   - Quoted versions ("Gemini 3 Flash", "M5 Pro", "o3-pro pricing").
   - The first content-bearing word in the title.

   The first turn whose dialogue text contains a story's distinctive keyword is that story's `start_turn`. Chapter 1 must always be `start_turn=1` (intro).

3. **Title each chapter**:
   - Chapter 1: `Today's headline` (or `Intro & headline` if you want it more obvious)
   - Story chapters: short noun phrase derived from the source headline (≤ 50 chars). Examples:
     - `Apple M5 Pro chip`
     - `Gemini 3 Flash 1M context`
     - `o3-pro price drop`

4. **Write `{output_dir}/{date}-chapters.json`**:
   ```json
   {
     "chapters": [
       {"title": "Today's headline",            "start_turn": 1},
       {"title": "Apple M5 Pro chip",           "start_turn": 4},
       {"title": "Gemini 3 Flash 1M context",   "start_turn": 9},
       {"title": "o3-pro price drop",           "start_turn": 14},
       {"title": "Anthropic Skills GA",         "start_turn": 19},
       {"title": "Hugging Face router release", "start_turn": 24},
       {"title": "Wrap & tomorrow watch",       "start_turn": 29}
     ]
   }
   ```

5. **Run `add_chapters.py`**:
   ```bash
   python plugins/podcast-skill/scripts/add_chapters.py \
     --segments-dir {output_dir}/{date}-segments \
     --output {output_dir}/{date}-podcast.mp3 \
     --chapters-json {output_dir}/{date}-chapters.json
   ```

   Verify the printed chapter list is monotonic and matches expectations.

   If only 0–1 stories made it into the dialogue, the script will skip writing chapters (ID3 spec needs ≥ 2). Proceed to publish without chapters.

---

### Phase 4: Publish to Transistor

Skipped entirely when `dry_run=true`.

1. **Upload audio**:
   ```
   mcp__transistor__upload_audio(local_path="{output_dir}/{date}-podcast.mp3")
   → { audio_url, ... }
   ```

2. **Determine next episode number** (pass `SHOW_ID` explicitly):
   ```
   mcp__transistor__list_episodes(show_id="daily-ai-espresso", status="published", per=1)
   ```
   Take the first episode's `attributes.number`, add 1. If empty, start at 1.

3. **Build metadata** per `references/description-template.md`:
   - `title`: `Daily AI Espresso — {Mon DD}: {top_story_tagline}` — e.g. `Daily AI Espresso — Apr 15: Apple M5 Pro + Gemini 3 Flash`. Keep total ≤ 80 chars.
   - `summary`: single plain-text sentence ≤ 200 chars summarizing the day's top story or theme.
   - `description`: HTML per the template — opening hook + ordered list of stories with one-line takeaways and source links + footer.
   - `season`: `1`
   - `number`: from step 2
   - `type`: `full`
   - `keywords`: `"ai news, daily, {top_company_1}, {top_company_2}, {top_model_1}"` — derive from the covered stories.

4. **Create the draft episode** (pass `SHOW_ID` explicitly):
   ```
   mcp__transistor__create_episode(
     show_id="daily-ai-espresso",
     title=…, summary=…, description=…,
     audio_url=<from step 1>,
     season=1, number=<from step 2>, type="full",
     keywords=…,
   )
   → { data: { id: "<episode_id>", attributes: { share_url, ... } } }
   ```

5. **Publish live**:
   ```
   mcp__transistor__publish_episode(episode_id=<id>, status="published")
   ```
   Invoking this skill is itself the explicit publish command (consistent with podcast-skill's explicit-command rule).

---

### Phase 5: Update tracker and report

1. **Append a row** to `{output_dir}/AI_ESPRESSO_TRACKER.md`:

   Normal publish:
   ```markdown
   | 2026-04-15 | 2026-04-15 | [html](./2026-04-15.html) | [md](./2026-04-15-podcast.md) | [mp3](./2026-04-15-podcast.mp3) | 12345 | https://share.transistor.fm/s/abc | published |
   ```

   Skipped (briefing too thin):
   ```markdown
   | 2026-04-15 | 2026-04-15 | [html](./2026-04-15.html) | — | — | — | — | skipped-thin-briefing |
   ```

2. **Report to user**:
   - Date just processed
   - Transcript path
   - Audio file path (with chapter count)
   - Transistor share URL
   - Approximate duration
   - For range/backfill: running counter (`3 of 5 done`).

3. **Loop** for additional target dates. Strictly serial.

---

## Error handling

- **No `<date>.html` files in `{output_dir}`**: report "No AI Espresso briefings found in {output_dir}" and exit. No tracker change.
- **`{date}.html` doesn't exist for a specific `date=` request**: error out, no tracker change.
- **Source briefing too thin** (< 3 items, or no Frontier Labs items): tracker row with `Status=skipped-thin-briefing`. Do NOT publish.
- **podcast-skill failure**: surface the error; brief/segments stay on disk; do NOT publish; do NOT update tracker.
- **Transistor upload fails**: keep mp3 + transcript; do NOT update tracker.
- **Transistor create fails**: same.
- **Transistor publish fails after create**: tracker row with `Status=draft` and the episode id/URL so the user can retry publish later.
- **Rate limit hit despite MCP backoff**: sleep 15s, retry once.
- **Ambiguous chapter mapping** (story keyword absent from transcript): omit that chapter; surface a warning. Do NOT block the publish.

---

## Invocation examples

```
# Default: publish today's (or latest unprocessed) briefing
Publish today's AI espresso podcast.

# Specific date
Generate the AI espresso podcast for 2026-04-15.

# Dry run preview
Preview tomorrow's AI espresso podcast without publishing.

# Range / backfill
Backfill AI espresso podcasts for 2026-04-10 through 2026-04-15.
```

---

## Cross-skill chain

This skill is the back half of a two-step daily workflow:

1. **`ai-espresso`** generates the morning briefing as `./output/YYYY-MM-DD.html`.
2. **`daily-ai-espresso-podcast`** (this skill) turns that HTML into a published podcast episode.

You can chain them in a single utterance: *"Generate today's AI espresso, then publish it as a podcast."*
