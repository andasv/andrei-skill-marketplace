# Fish Audio MCP Plugin

Local MCP server that calls the [Fish Audio](https://fish.audio) TTS API. Targets the **S1** model (parenthesis-syntax emotion tags, fixed tag list) and ships alongside the existing `elevenlabs` backend in the `podcast-skill`.

## Why this plugin

- Adds a second TTS provider so the podcast pipeline isn't stuck when ElevenLabs quota is exhausted.
- S1's `(emotion)` inline tags let each podcast host have a distinct, controllable emotional personality.
- Same MCP stdio transport and `${CLAUDE_PLUGIN_ROOT}` pattern as the repo's existing `plugins/transistor/`, so registration and dependency handling are consistent.

## Tools exposed

| Tool | Purpose |
|---|---|
| `text_to_speech(text, voice_id, model, audio_format, speed, …, output_directory, output_filename)` | Synthesize speech and write an audio file. Returns `{path, size_bytes, voice_id, model, format}`. |
| `list_voices(query, page_size)` | List available voice reference_ids. |
| `check_credit()` | Return remaining API credit — call before a long run. |
| `list_supported_tags()` | Return the S1 emotion/tone tag vocabulary. |

The S2-Pro model (free-form bracket tags, multi-speaker tokens) is accepted via `model="s2-pro"` but not validated — the podcast-skill currently only generates S1-syntax tags.

## S1 emotion tag reference

Emotion tags **must** be placed at the very start of a sentence, in parentheses:

```
(happy) What a beautiful day!
(excited) Look at this!
(sad) I'm sorry to hear that.
```

Supported emotions: `angry, sad, disdainful, excited, surprised, satisfied, unhappy, anxious, hysterical, delighted, scared, worried, indifferent, upset, impatient, nervous, guilty, scornful, frustrated, depressed, embarrassed, jealous, awkward, amused, happy, calm, confident, thoughtful, curious, enthusiastic, warm, friendly, empathetic`.

Tone tags can appear anywhere:

```
I thought everything was fine. (whispering) Then I heard the noise.
```

Supported tones: `in a hurry tone, shouting, screaming, whispering, soft tone`.

## Setup

The API key lives in the MCP server config (`~/.claude.json` local scope) — **not** in `.env`. Registration with `claude mcp add --env KEY=value` embeds the key directly in the MCP entry, which is scoped to this project and never committed to git.

### 1. Install dependencies

```bash
pip install fastmcp requests
```

(Same runtime dependencies as the existing `transistor` plugin — if you've already set up that plugin you're done.)

### 2. Register the MCP server with the key embedded (one time, local scope)

From this plugin directory (so the MCP server's `cwd` resolves correctly):

```bash
cd plugins/fish-audio
claude mcp add fish-audio \
  --scope local \
  --transport stdio \
  --env FISH_AUDIO_API_KEY=<your-fish-audio-key> \
  -- python -m fish_audio_mcp
```

This writes a local-scope entry under `~/.claude.json` containing the literal key value. The MCP runtime launches the Python process with `FISH_AUDIO_API_KEY` already in its environment, and the plugin reads it via `os.environ.get("FISH_AUDIO_API_KEY")`.

Confirm it's connected:

```bash
claude mcp list
# expect: fish-audio: ✓ Connected
```

To rotate the key later, `claude mcp remove fish-audio -s local` then re-run step 2 with the new value.

### 4. Smoke test

```
Call fish-audio check_credit to confirm the key works.
```

Then:

```
Call fish-audio text_to_speech with
  text="(happy) Hello from Fish Audio. (whispering) This is a test."
  voice_id="<pick one from list_voices>"
  output_directory="/tmp"
```

Play `/tmp/tts_*.mp3`. You should hear the emotional delivery shift between the two sentences.

## Using in the podcast-skill

Invoke the skill with `tts_provider=fish-audio` — the skill picks up each persona's `fish_audio_voice_id`, `fish_audio_speed`, and `fish_audio_emotion_palette` from persona frontmatter and injects one `(emotion)` tag per sentence drawn from the palette.

```
Generate a podcast from output/claude-code-2.1.111-brief.md with tts_provider=fish-audio duration=2 topics=1
```

Default (`tts_provider=elevenlabs`) keeps the existing behavior: no emotion tags, straight ElevenLabs TTS.

## Troubleshooting

- **`Missing FISH_AUDIO_API_KEY environment variable`** — the key isn't reaching the MCP process. Confirm `claude mcp list` shows the fish-audio entry as connected, and that `~/.claude.json` (local scope for this project) has a `"FISH_AUDIO_API_KEY"` value under the `env` block of the fish-audio MCP entry. If it's missing, remove and re-add with the `--env FISH_AUDIO_API_KEY=<key>` flag per the Setup section.
- **HTTP 402 on TTS** — wallet is empty. Check `check_credit()`.
- **Emotion not audible** — the tag must sit *at the start* of the sentence for English (S1). `What a (happy) day!` is ignored; `(happy) What a day!` works.
- **Chosen voice sounds wrong** — voices on Fish Audio are cloned models, so inflection and energy vary. Try `list_voices(query="narrator")` and sample a few `reference_id` values in smoke tests before wiring one into a persona file.

## License

MIT.
