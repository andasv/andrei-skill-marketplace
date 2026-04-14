# podcast-skill

Generate a professional 2-person AI podcast from written content using configurable personas and [ElevenLabs](https://elevenlabs.io/) voice synthesis. Works with **Claude Code** and any agentic assistant that supports the [Agent Skills](https://agentskills.io) open standard.

## Features

- 3-phase pipeline: content analysis, transcript generation, audio production
- Configurable personas with individual ElevenLabs voice settings
- Multiple podcast styles: collaborative, debate, interview
- Adjustable duration and topic count
- Automatic audio merging into a single MP3
- Optional ID3 chapter markers (one per feature/topic)
- Auto-play on completion

## Prerequisites

- [Python 3](https://www.python.org/) with `pydub` and `mutagen` (`pip install -r scripts/requirements.txt`)
- [ffmpeg](https://ffmpeg.org/) installed and on PATH
- An [ElevenLabs](https://elevenlabs.io/) account with API access (via MCP server)

## Quick Start

```
/podcast-skill input=~/ai-espresso/output/2026-04-06.html
/podcast-skill input=~/ai-espresso/output/2026-04-06.html duration=5 topics=2
/podcast-skill input=./my-article.md duration=3
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `input` | *(required)* | Path to the input content file (HTML, markdown, or plain text) |
| `duration` | `2` | Target podcast length in minutes |
| `topics` | `1` | Number of topics to cover |
| `personas_dir` | `personas/defaults/` | Directory containing persona `.md` files |
| `output_dir` | `./output/` | Where to save transcript and audio |
| `style` | `collaborative` | Podcast style: `collaborative`, `debate`, `interview` |

## How It Works

1. **Content Analysis** -- Parses the input, ranks topics by strategic significance, discussion potential, and audience accessibility, then generates discussion beats.
2. **Transcript Generation** -- Transforms the content brief into a natural two-person dialogue using persona definitions and a style guide. Targets ~150 words per minute.
3. **Audio Production** -- Synthesizes each speaker turn via ElevenLabs TTS, then merges segments into a final MP3.

## Personas

Default personas are in `personas/defaults/`. Each persona is a markdown file with YAML frontmatter containing ElevenLabs voice settings (`voice_id`, `model_id`, `stability`, `similarity_boost`, `style`, `speed`) and a markdown body describing character traits.

To use custom personas, create your own directory with persona files and pass it via the `personas_dir` parameter.

## Chapters (optional)

Drop a `<date>-chapters.json` file next to the transcript in your `output_dir` and the skill will embed ID3 `CTOC` + `CHAP` frames into the final MP3. Apple Podcasts, Overcast, Pocket Casts, Spotify, VLC, and Transistor's web player all honor these for clickable jump-to-chapter navigation.

JSON schema:

```json
{
  "chapters": [
    {"title": "Intro and headline feature", "start_turn": 1},
    {"title": "/recap command", "start_turn": 8},
    {"title": "Better error messages", "start_turn": 19}
  ]
}
```

- `start_turn` is 1-indexed and refers to the zero-padded segment files produced during audio production (`001_alex.mp3`, `002_sarah.mp3`, …).
- Chapter 1 must start at `start_turn=1`; `start_turn` values must be strictly increasing; ≥ 2 chapters required.
- Chapter start times are computed from cumulative segment durations, so they align exactly with the merged MP3 regardless of TTS timing.
- The script is idempotent — running it again overwrites any prior chapter frames.
- If the file is absent (default for AI Espresso briefings), chapter embedding is skipped silently.

You can also invoke the embedder directly:

```bash
python scripts/add_chapters.py \
  --segments-dir output/2026-04-14-segments \
  --output output/2026-04-14-podcast.mp3 \
  --chapters-json output/2026-04-14-chapters.json
```

## Project Structure

```
podcast-skill/
├── SKILL.md                  # Skill definition (execution pipeline)
├── personas/
│   └── defaults/             # Default persona files
│       ├── alex-chen.md
│       └── sarah-kim.md
├── references/
│   ├── content-analysis-guide.md
│   ├── podcast-style-guide.md
│   └── transcript-template.md
├── scripts/
│   ├── merge_audio.py        # Merges audio segments into final MP3
│   ├── add_chapters.py       # Optional: embed ID3 chapter markers
│   └── requirements.txt
└── output/                   # Generated transcripts and audio
```

## License

MIT
