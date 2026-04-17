---
name: podcast-skill
description: Generate a 2-person AI podcast from content (default input is AI Espresso briefings). Use when the user wants to create a podcast, generate audio discussion, turn news into spoken content, or says "podcast". Converts written content into a natural dialogue transcript and synthesizes it with ElevenLabs voices.
---

# Podcast Skill

Generate a professional 2-person podcast from written content using configurable personas and ElevenLabs voice synthesis.

## MCP Dependencies

This skill uses the following MCP servers:

| MCP Server | Purpose | Required Tools |
|------------|---------|----------------|
| **ElevenLabs** *(default TTS)* | Text-to-speech synthesis and audio playback | `mcp__ElevenLabs__text_to_speech`, `mcp__ElevenLabs__play_audio`, `mcp__ElevenLabs__search_voices` |
| **Fish Audio** *(alternative TTS — used only when `tts_provider=fish-audio`)* | S1-model TTS with inline emotion tags | `mcp__fish-audio__text_to_speech`, `mcp__fish-audio__list_voices`, `mcp__fish-audio__check_credit`, `mcp__fish-audio__list_supported_tags` |
| **Transistor** *(optional — only when the user explicitly requests publishing)* | Upload audio and manage episodes on Transistor.fm | `mcp__transistor__upload_audio`, `mcp__transistor__create_episode`, `mcp__transistor__update_episode`, `mcp__transistor__publish_episode`, `mcp__transistor__delete_episode`, `mcp__transistor__get_episode`, `mcp__transistor__list_episodes`, `mcp__transistor__get_show`, `mcp__transistor__update_show` |

The ElevenLabs MCP server handles API authentication internally. The Fish Audio and Transistor MCP servers read their API keys from the MCP server config (`~/.claude.json` local scope) — register them once with `claude mcp add --env FISH_AUDIO_API_KEY=… -- python -m fish_audio_mcp` and `claude mcp add --env TRANSISTOR_API_KEY=… -- python -m transistor_mcp`. See each plugin's README for the exact commands. Keys are no longer read from `.env`.

## Parameters

The user may provide these parameters when invoking the skill. Apply defaults for anything not specified.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `input` | *(required)* | Path to the input content file (AI Espresso HTML or other) |
| `duration` | `2` | Target podcast length in minutes |
| `topics` | `1` | Number of topics to cover |
| `personas_dir` | `personas/defaults/` (relative to this skill) | Directory containing persona .md files |
| `output_dir` | `./output/` (relative to CWD) | Where to save transcript and audio |
| `style` | `collaborative` | Podcast style: collaborative, debate, interview |
| `tts_provider` | `elevenlabs` | TTS backend: `elevenlabs` (default) or `fish-audio`. When `fish-audio`, the transcript is annotated with inline `(emotion)` tags drawn from each persona's `fish_audio_emotion_palette`. |

## Execution Pipeline

Execute these three phases sequentially. Do not skip phases.

---

## Phase 1: Content Analysis

**Goal**: Parse the input content and produce a structured content brief identifying the most important topics and discussion beats.

### Steps

1. **Read the input file** at the path provided by the user.

2. **Read the content analysis guide**: Load `references/content-analysis-guide.md` from this skill's directory for ranking criteria and output format.

3. **Parse the content**:
   - If the input is an AI Espresso HTML file: extract all news items with their titles, dates, source URLs, and analysis blocks (What happened, Why it matters, Implications). Group by section.
   - If the input is plain text or markdown: identify distinct topics or sections.

4. **Rank topics** using the criteria from the content analysis guide:
   - Strategic significance (40% weight)
   - Discussion potential (35% weight)
   - Audience accessibility (25% weight)

5. **Select topics**: Pick the top N items based on the `topics` parameter (default: 1 for a 2-minute episode).

6. **Generate discussion beats**: For each selected topic, create 3-5 discussion beats with hooks, depth points, and emotional tones. Follow the beat arc pattern from the guide: surprise → analysis → implications → forward look.

7. **Produce the content brief** in working memory (do not write to disk). Use the format specified in the content analysis guide.

---

## Phase 2: Transcript Generation

**Goal**: Transform the content brief into a natural, engaging two-person dialogue transcript.

### Steps

1. **Read persona files**: Load all `.md` files from the configured `personas_dir`. Parse YAML frontmatter for voice settings and markdown body for character traits. Note each persona's `name` field exactly — this will be used as the speaker label.

2. **Read the style guide**: Load `references/podcast-style-guide.md` from this skill's directory.

3. **Read the transcript template**: Load `references/transcript-template.md` from this skill's directory for the expected output format.

4. **Calculate word count target**: `duration_minutes × 150` words (conversational speaking pace). For the default 2-minute episode, target ~300 words.

5. **Generate the transcript** following these rules:

   **Structure** (from the style guide):
   - `<!-- INTRO -->` — 1-2 turns. Persona 1 opens with a punchy hook about the topic. Persona 2 reacts with genuine interest.
   - `<!-- DISCUSSION -->` — 4-8 turns (varies by duration). Work through the discussion beats from Phase 1. Each beat should involve both personas. Follow dialogue patterns from the style guide (yes-and, hmm-but, accessible translation, genuine surprise).
   - `<!-- OUTRO -->` — 1 turn. Brief, warm sign-off with a forward-looking thought.

   **Dialogue rules**:
   - Each turn starts with `**PERSONA_NAME:**` followed by a space and dialogue text
   - Each turn is 2-4 sentences (never exceed 5)
   - Persona 1 (typically the technical persona) introduces concepts and goes deep
   - Persona 2 (typically the business persona) translates to impact and asks "so what?"
   - Alternate between personas — never have the same persona speak twice in a row
   - Include natural reactions: "Wait, really?", "That's actually huge", "Okay so..."
   - Humor is a spice, not the dish — keep it light and natural

   **Style** (configurable):
   - `collaborative` (default): Build on each other's points, share insights, agree and add nuance
   - `debate`: Take opposing views, challenge each other, productive tension
   - `interview`: Persona 1 asks questions, Persona 2 answers in depth

   **Emotion-tag injection (only when `tts_provider=fish-audio`):**
   When Fish Audio is the TTS backend, annotate every sentence with an inline emotion tag. Skip this block entirely for `tts_provider=elevenlabs` (default).

   - **Source of truth per host**: each persona file has a `fish_audio_emotion_palette` YAML field — an array of emotion names drawn from the Fish Audio S1 vocabulary (see `mcp__fish-audio__list_supported_tags` or the list at the end of this section). The first entry is the persona's baseline emotion.
   - **Per-sentence selection**: for every sentence a persona speaks, pick exactly one emotion from *that persona's* palette whose connotation best matches the sentence's beat tone. Examples:
     - Surprise reveal → `(surprised)` or `(excited)` if in palette
     - Thoughtful explanation → `(thoughtful)` or `(calm)` if in palette
     - Empathetic reaction → `(empathetic)` or `(warm)` if in palette
     - Confident claim → `(confident)` or `(satisfied)` if in palette
     - No clear valence → fall back to the **first** palette entry (baseline)
   - **Placement**: prepend the tag to the sentence, inside parentheses, at the very start — Fish Audio S1 requires sentence-initial placement for English. Every sentence gets exactly one tag.

     ```
     **Alex Chen:** (thoughtful) This release is dense. (curious) What's the first thing you want to dig into?
     **Sarah Kim:** (delighted) I love that Auto mode is finally flag-free. (confident) That's a meaningful quality-of-life win for Max users.
     ```

   - **Cross-palette discipline**: never apply an emotion from Sarah's palette to Alex or vice versa — the palettes encode each host's personality. Do not invent emotions outside the palette.
   - **Supported S1 emotions** (validation reference): `angry, sad, disdainful, excited, surprised, satisfied, unhappy, anxious, hysterical, delighted, scared, worried, indifferent, upset, impatient, nervous, guilty, scornful, frustrated, depressed, embarrassed, jealous, awkward, amused, happy, calm, confident, thoughtful, curious, enthusiastic, warm, friendly, empathetic`. Tone tags like `(whispering)`, `(soft tone)`, `(in a hurry tone)`, `(shouting)` can appear anywhere in a sentence and are *in addition to* the mandatory sentence-initial emotion tag.

6. **Add YAML frontmatter** to the transcript:
   ```yaml
   ---
   date: [today's date]
   source_file: [input filename]
   personas:
     - [persona 1 name]
     - [persona 2 name]
   duration_target: [X] minutes
   topic: "[selected topic title]"
   tts_provider: [elevenlabs or fish-audio]
   ---
   ```
   Include `tts_provider` so the audio phase knows which MCP to route to, and so a reader can tell at a glance whether the transcript is tagged.

7. **Save the transcript** to `{output_dir}/{date}-podcast.md` using the Write tool.

---

## Phase 3: Audio Production

**Goal**: Synthesize speech for each speaker turn and merge into a final podcast MP3.

### Steps

1. **Read the saved transcript** from Phase 2.

2. **Parse speaker turns**: Split the transcript into ordered turns. For each turn, extract:
   - Speaker name (text between `**` and `:**`)
   - Dialogue text (everything after `**NAME:** `)
   - Turn index (starting from 1)

3. **Map speakers to voice settings**: For each unique speaker name, find the matching persona file and extract voice settings from frontmatter:
   - `voice_id` (required)
   - `model_id` (default: `eleven_multilingual_v2`)
   - `stability` (default: 0.5)
   - `similarity_boost` (default: 0.75)
   - `style` (default: 0)
   - `speed` (default: 1.0)

4. **Create segments directory**: `{output_dir}/{date}-segments/` using Bash `mkdir -p`.

5. **Synthesize each turn** sequentially. Route based on `tts_provider`:

   **When `tts_provider=elevenlabs` (default):**
   Call `mcp__ElevenLabs__text_to_speech` with:
   - `text`: the dialogue text (stripped of speaker prefix)
   - `voice_id`: from the speaker's persona (`voice_id` field)
   - `model_id`: from the speaker's persona
   - `stability`: from the speaker's persona
   - `similarity_boost`: from the speaker's persona
   - `style`: from the speaker's persona
   - `speed`: from the speaker's persona
   - `output_format`: `mp3_44100_128`
   - `output_directory`: the segments directory

   **When `tts_provider=fish-audio`:**
   First, call `mcp__fish-audio__check_credit` once before the loop. If credit is insufficient for the full transcript (<1 char per sentence × safety margin), stop and surface the error.

   Then for each turn, call `mcp__fish-audio__text_to_speech` with:
   - `text`: the dialogue text (stripped of speaker prefix) — **keep all `(emotion)` tags intact**; the Fish Audio S1 model reads them as prosody control
   - `voice_id`: from the speaker's persona (`fish_audio_voice_id` field)
   - `model`: `"s1"`
   - `audio_format`: `"mp3"`
   - `speed`: from the speaker's persona (`fish_audio_speed` field)
   - `mp3_bitrate`: `128`
   - `output_directory`: the segments directory

   After each TTS call (regardless of provider), rename the output file to `{NNN}_{speaker_name_lowercase}.mp3` where NNN is the zero-padded turn index (001, 002, 003...). This ensures correct merge order. The file returned by Fish Audio follows the same `tts_<prefix>_<timestamp>.mp3` naming convention as ElevenLabs, so the rename step is identical across providers.

6. **Merge audio segments**: Run the merge script:
   ```bash
   python {skill_dir}/scripts/merge_audio.py \
     --segments-dir {output_dir}/{date}-segments \
     --output {output_dir}/{date}-podcast.mp3
   ```

7. **Embed chapter markers (optional, opt-in)**: If `{output_dir}/{date}-chapters.json` exists, run:
   ```bash
   python {skill_dir}/scripts/add_chapters.py \
     --segments-dir {output_dir}/{date}-segments \
     --output {output_dir}/{date}-podcast.mp3 \
     --chapters-json {output_dir}/{date}-chapters.json
   ```
   The script writes ID3 `CTOC` + `CHAP` frames in place and is idempotent. If the chapters file is absent (the default for AI-Espresso-style single-topic podcasts), skip this step silently. See the README's "Chapters" section for the JSON schema.

8. **Auto-play the podcast**: Call `mcp__ElevenLabs__play_audio` with the merged file path.

9. **Report results** to the user:
   - Transcript path
   - Audio file path
   - Number of segments
   - Approximate duration
   - Chapter count (if chapters.json was present)

---

## Publishing to Transistor.fm (opt-in, explicit command only)

**Do NOT publish automatically.** Phase 3 ends with a local MP3. Publishing to Transistor.fm only happens when the user explicitly asks in that same turn — phrases like "publish it", "upload to transistor", "post this episode", "push to the podcast feed". Producing audio never implies publishing. If the user's command is ambiguous (e.g. "share this"), ask before calling any Transistor write tool.

### Tools provided by the Transistor MCP

- `mcp__transistor__upload_audio(local_path)` — 2-step flow: authorizes an S3 upload URL, PUTs the file, returns `{ audio_url, content_type, filename, size_bytes }`. Pass `audio_url` into the next step.
- `mcp__transistor__create_episode(title, summary?, description?, audio_url?, image_url?, season?, number?, type?, keywords?, author?, explicit?, show_id?)` — creates a **draft** episode. `type` is one of `full` / `trailer` / `bonus` (default `full`).
- `mcp__transistor__update_episode(episode_id, ...)` — PATCH any subset of metadata fields.
- `mcp__transistor__publish_episode(episode_id, status, scheduled_for?)` — `status` is `published`, `scheduled`, or `draft`. `scheduled_for` is an ISO 8601 datetime, required when `status="scheduled"`.
- `mcp__transistor__delete_episode(episode_id)` — **unpublishes** the episode (sets `status=draft`). Transistor's public API has no hard delete; permanent removal is dashboard-only.
- `mcp__transistor__get_episode` / `mcp__transistor__list_episodes` — read-only inspection.
- `mcp__transistor__get_show` / `mcp__transistor__list_shows` / `mcp__transistor__update_show` — show metadata. Transistor does **not** allow creating or deleting shows via API.

Every `show_id` argument defaults to `TRANSISTOR_SHOW_ID` from the env, so single-podcast workflows can omit it.

### Canonical publish flow

When the user has explicitly asked to publish, execute these steps in order:

1. **Upload the merged mp3**
   ```
   mcp__transistor__upload_audio(local_path="{output_dir}/{date}-podcast.mp3")
   → { audio_url: "https://...", ... }
   ```
   Capture `audio_url` from the response.

2. **Build episode metadata from the transcript**
   - `title`: Derive from the transcript YAML frontmatter `topic` field, or ask the user if unclear.
   - `summary`: 1–2 sentence plain-text hook (≤ 200 chars). Use the topic headline.
   - `description`: Full show notes as basic HTML. Include: the discussion beats, source links from the original input (AI Espresso news items), persona names. Plain `<p>`, `<ul>`, `<li>`, `<a href>` tags are safe.
   - `season` / `number`: Ask the user or look up the next number with `list_episodes(status="published", per=1)`.
   - `type`: `full` unless the user says trailer/bonus.
   - `keywords`: Comma-separated, drawn from the topic.
   - `image_url`: Only if the user provides cover art; otherwise omit and Transistor falls back to show artwork.
   - `explicit`: `false` unless the user says otherwise.

3. **Create the draft episode**
   ```
   mcp__transistor__create_episode(
     title=...,
     summary=...,
     description=...,
     audio_url="<from step 1>",
     season=..., number=..., type="full",
     keywords=...,
   )
   → { data: { id: "<episode_id>", ... } }
   ```
   Save the returned `data.id` — it's needed for every subsequent call.

4. **(Optional) Refine metadata**
   If the user wants to tweak anything after creation, use `update_episode(episode_id, ...)`. Only send the fields that change.

5. **Publish or schedule** (only on explicit user command — do not auto-publish a draft)
   - Immediate: `publish_episode(episode_id, status="published")`
   - Scheduled: `publish_episode(episode_id, status="scheduled", scheduled_for="2026-05-01T09:00:00Z")` (ISO 8601, UTC recommended)
   - Keep as draft: do nothing; the episode stays private until explicitly published.

6. **Report back** to the user with:
   - The Transistor dashboard URL for the episode (derivable from show slug + episode id, or use the `share_url` attribute from the response).
   - Its current status (`draft` / `scheduled` / `published`).
   - The public `media_url` / `audio_url` if published.

### Nuances and gotchas

- **Rate limit**: Transistor enforces 10 requests per 10 seconds. The MCP client retries 429s with 1s/2s/4s backoff (max 3 retries). Don't fire bursts of calls.
- **Draft-first is mandatory**: `create_episode` always produces a draft. Publishing is a separate `publish_episode` call. This gives the user a chance to review in the Transistor dashboard before the episode goes live on feeds.
- **"Delete" semantics**: `delete_episode` is actually an unpublish. The episode remains in the Transistor dashboard. To permanently delete, direct the user to the Transistor.fm dashboard UI.
- **Artwork size**: Per-episode `image_url` should be a square PNG/JPG at least 1400×1400 and no more than 3000×3000, RGB, under 512 KB. Transistor will reject images outside that range.
- **Summary vs description**: Summary is plain text shown in directory listings; description is the full show notes and supports limited HTML. Keep summary short and punchy; put all detail in description.
- **Season and episode numbers** are required by some podcast directories (Apple Podcasts flags missing numbers). Always set them. If unsure of the next number, call `list_episodes(status="published", per=1)` and increment.
- **Scheduled publishing** uses the show's configured time zone (see `get_show()`), but `scheduled_for` should be sent as ISO 8601 with an explicit timezone offset (e.g. `Z` for UTC). Confirm the resulting local-time publish moment with the user before scheduling.
- **Creating or deleting podcasts** is not possible via API — it must be done through the Transistor dashboard at https://dashboard.transistor.fm.
- **Environment**: If the user hasn't set `TRANSISTOR_API_KEY` and `TRANSISTOR_SHOW_ID` in `.env`, the first tool call will fail with a clear RuntimeError. Direct them to the plugin README.

---

## Error Handling

- If no persona files are found in the configured directory, report the error and suggest checking the path.
- If a persona file is missing `voice_id`, use `mcp__ElevenLabs__search_voices` to find a voice matching the persona's `voice_name` field and update the persona file.
- If the TTS call fails for a segment, report which segment failed and continue with remaining segments.
- **Fish Audio quota exhausted (HTTP 402)**: stop the pipeline immediately — partial audio is not useful for a multi-turn podcast. Report the error, list any segments already written, and keep the transcript on disk so the run can resume after top-up. Same contract as ElevenLabs quota failures.
- **Persona missing Fish Audio fields**: when `tts_provider=fish-audio`, if a persona file lacks `fish_audio_voice_id` or `fish_audio_emotion_palette`, stop and tell the user which file to update — don't try to synthesize with a bad configuration.
- If the merge script fails, check that pydub is installed (`pip install pydub`) and ffmpeg is available.
- If the input file cannot be parsed as HTML, treat it as plain text and extract topics from paragraphs.

---

## Quick Start Example

```
User: /podcast-skill input=~/ai-espresso/output/2026-04-06.html
User: /podcast-skill input=~/ai-espresso/output/2026-04-06.html duration=5 topics=2
User: /podcast-skill input=./my-article.md duration=3
```
