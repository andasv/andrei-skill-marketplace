# Podcast Personas

Each persona is defined in its own `.md` file with YAML frontmatter for voice configuration and markdown body for character definition.

## Creating a Custom Persona

1. Copy one of the defaults as a starting point
2. Update the frontmatter with your voice settings
3. Modify the character description

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name used in transcript (e.g., "Alex Chen") |
| `role` | Yes | Role title (e.g., "Senior AI Engineer") |
| `voice_id` | Yes | ElevenLabs voice ID |
| `voice_name` | No | ElevenLabs voice name (for reference) |
| `model_id` | No | ElevenLabs model (default: eleven_multilingual_v2) |
| `stability` | No | Voice stability 0-1 (default: 0.5) |
| `similarity_boost` | No | Voice similarity 0-1 (default: 0.75) |
| `style` | No | Style exaggeration 0-1 (default: 0) |
| `speed` | No | Speech speed multiplier (default: 1.0) |

## Finding Voice IDs

Use the ElevenLabs MCP tool to search for voices:
- `mcp__ElevenLabs__search_voices` — search your voice library
- `mcp__ElevenLabs__search_voice_library` — search the public library
