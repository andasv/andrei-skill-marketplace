# Claude Code Release Notes Podcast

A Claude Code skill that turns every Claude Code release into a published podcast episode.

## What it does

1. Fetches the official Claude Code CHANGELOG (`anthropics/claude-code/main/CHANGELOG.md`).
2. For each feature in a release, researches the Anthropic docs and produces a concise **WHY / WHAT / HOW** explanation.
3. Chains the [`podcast-skill`](../podcast-skill/) to generate a 2-person audio discussion (Alex Chen + Sarah Kim).
4. Uploads and publishes the episode to Transistor.fm via the [`transistor` MCP plugin](../transistor/).
5. Records the result in `./output/TRACKER.md` so repeat runs skip already-processed versions.

One episode per CHANGELOG entry. Default run publishes only the newest unprocessed release.

## Dependencies

This skill is an **orchestrator** — it does not produce audio or publish on its own. It depends on:

| Plugin | Required for |
|--------|--------------|
| [`podcast-skill`](../podcast-skill/) | Transcript generation + ElevenLabs TTS + audio merging |
| [`transistor`](../transistor/) | Uploading audio and publishing episodes (needs `TRANSISTOR_API_KEY` and `TRANSISTOR_SHOW_ID` in `.env`) |

Optional MCP servers used for research:
- **ElevenLabs MCP** — via podcast-skill (for TTS)
- **Exa MCP** — fallback research when Anthropic docs don't cover a bullet

Install all three plugins from the marketplace:

```
/plugin install podcast-skill@andrei-skill-marketplace
/plugin install transistor@andrei-skill-marketplace
/plugin install claude-code-release-podcast@andrei-skill-marketplace
```

## Usage

The skill is triggered by natural language. Examples:

```
Publish a podcast for the latest Claude Code release.
Generate a Claude Code release podcast for version 2.1.108.
Preview the next Claude Code release podcast without publishing.
Backfill Claude Code release podcasts for versions 2.1.100 through 2.1.108.
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `version` | *(unset)* | Specific version (e.g. `2.1.108`). Overrides the tracker; publishes even if already processed. |
| `since` / `until` | *(unset)* | Range mode: publish every unprocessed version in `[since, until]` inclusive. Both must be set. |
| `dry_run` | `false` | Preview planned episodes without generating audio, publishing, or touching TRACKER.md. |
| `output_dir` | `./output/` | Where briefs, transcripts, audio, and TRACKER.md live. |
| `personas_dir` | podcast-skill default | Passed through to podcast-skill. |
| `style` | `collaborative` | Passed through to podcast-skill. |

Mode precedence: `version` > `since`/`until` > default (newest unprocessed).

## Outputs

Every successful run produces (under `./output/`):

- `claude-code-{version}-brief.md` — the pre-digested research brief (input to podcast-skill)
- `{YYYY-MM-DD}-podcast.md` — the 2-person dialogue transcript
- `{YYYY-MM-DD}-podcast.mp3` — the merged audio
- `{YYYY-MM-DD}-segments/` — per-turn audio segments (kept for debugging)
- A new row in `TRACKER.md`

On Transistor, the episode is created as a draft, then published live.

## TRACKER.md format

```markdown
# Claude Code Release Podcast Tracker

| Version | Processed   | Transcript | Audio | Transistor ID | Published URL | Status    |
|---------|-------------|------------|-------|---------------|---------------|-----------|
| 2.1.108 | 2026-04-14  | [md](./2026-04-14-podcast.md) | [mp3](./2026-04-14-podcast.mp3) | 12345 | https://share.transistor.fm/s/abc | published |
```

`Status` values: `published`, `draft` (if publish failed after create), `dry-run` (if `dry_run=true`, but the row is *not* written in dry run — only printed).

## Safety

- **Bulk confirmation**: if range or backfill mode would process more than 1 version, the skill prints a preview table and waits for the exact phrase `yes, publish all N` before generating or publishing anything.
- **Idempotency**: re-running with no args after a successful run prints `Already up to date` and does nothing.
- **No auto-publish without user invocation**: the skill never runs on a schedule by default. Invoking it IS the explicit publish command.

## Rate limits

Transistor enforces 10 requests per 10 seconds. Backfill mode processes versions serially. The `transistor` MCP client retries 429s with exponential backoff (1s / 2s / 4s).
