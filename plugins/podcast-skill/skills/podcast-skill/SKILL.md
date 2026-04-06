---
name: podcast-skill
description: Generate a 2-person AI podcast from content (default input is AI Espresso briefings). Use when the user wants to create a podcast, generate audio discussion, turn news into spoken content, or says "podcast". Converts written content into a natural dialogue transcript and synthesizes it with ElevenLabs voices.
---

# Podcast Skill

Generate a professional 2-person podcast from written content using configurable personas and ElevenLabs voice synthesis.

## MCP Dependencies

This skill requires the following MCP server to be configured:

| MCP Server | Purpose | Required Tools |
|------------|---------|----------------|
| **ElevenLabs** | Text-to-speech synthesis and audio playback | `mcp__ElevenLabs__text_to_speech`, `mcp__ElevenLabs__play_audio`, `mcp__ElevenLabs__search_voices` |

The ElevenLabs MCP server handles API authentication internally. No API keys need to be configured in the skill itself.

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
   ---
   ```

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

5. **Synthesize each turn** sequentially. For each turn:

   Call `mcp__ElevenLabs__text_to_speech` with:
   - `text`: the dialogue text (stripped of speaker prefix)
   - `voice_id`: from the speaker's persona
   - `model_id`: from the speaker's persona
   - `stability`: from the speaker's persona
   - `similarity_boost`: from the speaker's persona
   - `style`: from the speaker's persona
   - `speed`: from the speaker's persona
   - `output_format`: `mp3_44100_128`
   - `output_directory`: the segments directory

   After each TTS call, rename the output file to `{NNN}_{speaker_name_lowercase}.mp3` where NNN is the zero-padded turn index (001, 002, 003...). This ensures correct merge order.

6. **Merge audio segments**: Run the merge script:
   ```bash
   python {skill_dir}/scripts/merge_audio.py \
     --segments-dir {output_dir}/{date}-segments \
     --output {output_dir}/{date}-podcast.mp3
   ```

7. **Auto-play the podcast**: Call `mcp__ElevenLabs__play_audio` with the merged file path.

8. **Report results** to the user:
   - Transcript path
   - Audio file path
   - Number of segments
   - Approximate duration

---

## Error Handling

- If no persona files are found in the configured directory, report the error and suggest checking the path.
- If a persona file is missing `voice_id`, use `mcp__ElevenLabs__search_voices` to find a voice matching the persona's `voice_name` field and update the persona file.
- If the TTS call fails for a segment, report which segment failed and continue with remaining segments.
- If the merge script fails, check that pydub is installed (`pip install pydub`) and ffmpeg is available.
- If the input file cannot be parsed as HTML, treat it as plain text and extract topics from paragraphs.

---

## Quick Start Example

```
User: /podcast-skill input=~/ai-espresso/output/2026-04-06.html
User: /podcast-skill input=~/ai-espresso/output/2026-04-06.html duration=5 topics=2
User: /podcast-skill input=./my-article.md duration=3
```
