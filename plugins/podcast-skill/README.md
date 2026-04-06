# podcast-skill

Generate a professional 2-person AI podcast from written content using configurable personas and [ElevenLabs](https://elevenlabs.io/) voice synthesis. Works with **Claude Code** and any agentic assistant that supports the [Agent Skills](https://agentskills.io) open standard.

## Features

- 3-phase pipeline: content analysis, transcript generation, audio production
- Configurable personas with individual ElevenLabs voice settings
- Multiple podcast styles: collaborative, debate, interview
- Adjustable duration and topic count
- Automatic audio merging into a single MP3
- Auto-play on completion

## Prerequisites

- [Python 3](https://www.python.org/) with `pydub` (`pip install pydub`)
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
│   └── requirements.txt
└── output/                   # Generated transcripts and audio
```

## License

MIT
