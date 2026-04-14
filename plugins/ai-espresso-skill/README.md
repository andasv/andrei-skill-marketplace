# AI Espresso

A Claude Code skill that generates a strategic morning AI news briefing as a self-contained HTML file.

## What it does

Scans curated AI news sources and web search results from the last 24 hours, then produces a concise HTML briefing with strategic analysis. The marquee section tracks the **Frontier Labs Competition** between Anthropic, OpenAI, and Google Gemini. Every run also deduplicates against the previous 3 days of output so stories are never repeated.

## Features

- Source-driven fetch: combines curated feeds (Anthropic News, OpenAI RSS, SMOL AI) with gap-filling web search
- Strategic scoring: ranks items by significance, relevance, and recency
- Self-contained HTML output — no external assets, archive-friendly
- Deduplication against prior 3 days of output
- Built-in evaluator for coverage + factual-accuracy checks
- Configurable sources and editorial guidelines

## Prerequisites

- Claude Code + the marketplace added
- [Exa MCP](https://github.com/exa-labs/exa-mcp-server) configured — used for gap-filling web search
- `EXA_API_KEY` available to Claude Code (via the Exa MCP setup)

## Install

```
/plugin marketplace update andrei-skill-marketplace
/plugin install ai-espresso@andrei-skill-marketplace
```

## Usage

Natural language works; the skill name is also directly invocable:

```
Give me my morning AI update.
What happened in AI today?
/ai-espresso
```

## Output

An HTML file saved to `./output/YYYY-MM-DD.html` with 5–8 strategically analyzed items across four sections:

1. **Frontier Labs Competition Update** (always first)
2. **Models & Research**
3. **Products & Tools**
4. **Industry & Business**

## Configuration

- `sources.md` — add, remove, or reprioritize news sources (P0/P1/P2 tiers)
- `guidelines.md` — adjust editorial guidelines, sections, tone, and analysis depth
- `references/html-template.md` — HTML output template

## Evaluation

Run the evaluator to check briefing quality:

```
Evaluate the latest AI espresso output.
```

Produces a JSON report in `./output/eval-YYYY-MM-DD.json` scoring coverage completeness, relevance, and factual accuracy.

## Cross-skill integration

- **[podcast-skill](../podcast-skill/)** — feed the briefing HTML into the podcast generator: `Create a podcast from today's AI briefing.`
- **[pushover](../pushover/)** — push the top headline after the briefing is ready: `Generate the briefing and ping me the top story.`

## License

MIT
