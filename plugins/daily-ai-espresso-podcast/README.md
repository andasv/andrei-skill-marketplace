# Daily AI Espresso Podcast

A Claude Code skill that turns the daily AI Espresso morning briefing into a published 15-minute podcast episode on the [Daily AI Espresso show](https://share.transistor.fm/daily-ai-espresso) at Transistor.fm.

## What it does

1. Finds the latest `./output/YYYY-MM-DD.html` produced by the [`ai-espresso`](../ai-espresso-skill/) skill.
2. Picks the **top 6 stories** from the briefing (Frontier Labs first, then official Anthropic/OpenAI news, then Models & Research, etc. — see `references/coverage-guide.md`).
3. Chains [`podcast-skill`](../podcast-skill/) to generate a ~2,250-word transcript and ~15-minute audio with Alex Chen + Sarah Kim.
4. Embeds **ID3 chapter markers — one per covered story** — so listeners can jump directly to any topic.
5. Uploads + publishes to Transistor.fm via the [`transistor`](../transistor/) MCP.
6. Records the result in `./output/AI_ESPRESSO_TRACKER.md` so repeat runs skip already-processed days.

One episode per AI Espresso briefing. Default run publishes only the newest unprocessed day.

## Dependencies

This skill is an **orchestrator** — it doesn't generate audio or publish on its own. It depends on:

| Plugin | Required for |
|---|---|
| [`ai-espresso`](../ai-espresso-skill/) | Producing the source HTML briefing in `./output/YYYY-MM-DD.html` |
| [`podcast-skill`](../podcast-skill/) | Transcript + ElevenLabs TTS + audio merging + chapter embedding |
| [`transistor`](../transistor/) | Uploading audio and publishing episodes (needs `TRANSISTOR_API_KEY` in `.env`; show id is hardcoded in this skill, sourced from [`/SHOWS.md`](../../SHOWS.md)) |

Optional MCP servers used by `podcast-skill` and `ai-espresso`:

- **ElevenLabs MCP** — TTS (via `podcast-skill`)
- **Exa MCP** — web search (via `ai-espresso`)

## Install

```
/plugin marketplace update andrei-skill-marketplace
/plugin install ai-espresso@andrei-skill-marketplace
/plugin install podcast-skill@andrei-skill-marketplace
/plugin install transistor@andrei-skill-marketplace
/plugin install daily-ai-espresso-podcast@andrei-skill-marketplace
```

## Usage

The skill is triggered by natural language. Examples:

```
Publish today's AI espresso podcast.
Generate the AI espresso podcast for 2026-04-15.
Preview tomorrow's AI espresso podcast without publishing.
Backfill AI espresso podcasts for 2026-04-10 through 2026-04-15.
```

Two-step daily flow:

```
Generate today's AI espresso, then publish it as a podcast.
```

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `date` | *(unset)* | Specific `YYYY-MM-DD`. Overrides tracker; publishes regardless. |
| `since` / `until` | *(unset)* | Range mode: process every unprocessed day in `[since, until]`. Both must be set. |
| `dry_run` | `false` | Preview without writing audio, publishing, or touching the tracker. |
| `output_dir` | `./output/` | Where the AI Espresso HTML, briefs, audio, and tracker live. |
| `personas_dir` | podcast-skill default | Passed through to podcast-skill. |
| `style` | `collaborative` | Passed through to podcast-skill. |
| `duration` | `15` | Target episode length in minutes. |
| `topics` | `6` | Number of stories covered in the dialogue. |

Mode precedence: `date` > `since`/`until` > default (newest unprocessed).

## Outputs

Per successful run (under `./output/`):

- `{date}-podcast.md` — the two-host dialogue transcript
- `{date}-podcast.mp3` — merged audio with ID3 chapter markers
- `{date}-segments/` — per-turn audio segments (gitignored — regenerable)
- `{date}-chapters.json` — chapter map (titles + start_turn)
- A new row in `AI_ESPRESSO_TRACKER.md`

On Transistor: a new published episode on the `daily-ai-espresso` show.

## AI_ESPRESSO_TRACKER.md format

```markdown
# Daily AI Espresso Podcast Tracker

| Date | Processed | Source HTML | Transcript | Audio | Transistor ID | Published URL | Status |
|------|-----------|-------------|------------|-------|---------------|---------------|--------|
| 2026-04-15 | 2026-04-15 | [html](./2026-04-15.html) | [md](./2026-04-15-podcast.md) | [mp3](./2026-04-15-podcast.mp3) | 12345 | https://share.transistor.fm/s/abc | published |
```

`Status` values: `published`, `draft` (publish failed after create), `skipped-thin-briefing` (briefing had < 3 items or no Frontier Labs items), `dry-run` (preview only — row is *not* written in dry run).

## Safety

- **Bulk confirmation**: range/backfill mode prints a preview table and waits for `yes, publish all N` before generating or publishing anything.
- **Idempotency**: re-running default mode after a successful run prints `Already up to date` and does nothing.
- **Thin-briefing skip**: AI Espresso briefings with too few items are skipped instead of producing a low-quality episode.
- **No auto-publish without user invocation**: the skill never runs on a schedule by default. Invoking it IS the explicit publish command.

## Show config

The target Transistor show is registered in [`/SHOWS.md`](../../SHOWS.md) at the repo root:

| Field | Value |
|---|---|
| `show_id` (slug) | `daily-ai-espresso` |
| `numeric_id` | `77097` |
| `feed_url` | https://feeds.transistor.fm/daily-ai-espresso |
| `dashboard_url` | https://dashboard.transistor.fm/shows/daily-ai-espresso |

If the show is renamed or recreated in the dashboard, update SHOWS.md first, then this skill's Configuration table.
