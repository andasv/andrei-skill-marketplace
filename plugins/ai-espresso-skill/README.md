# AI Espresso

A Claude Code skill that generates a strategic morning AI news briefing.

## What it does

Scans curated AI news sources and web search results, then produces a concise HTML briefing with strategic analysis. The marquee section tracks the **Frontier Labs Competition** between Anthropic, OpenAI, and Google Gemini.

## Usage

```
/ai-espresso
```

Or just say: "Give me my morning AI update", "What happened in AI today?"

## Output

An HTML file saved to `./output/YYYY-MM-DD.html` with 5-8 strategically analyzed items across four sections:

1. **Frontier Labs Competition Update** (always first)
2. **Models & Research**
3. **Products & Tools**
4. **Industry & Business**

## Configuration

- **sources.md** — Add, remove, or reprioritize news sources
- **guidelines.md** — Adjust editorial guidelines, sections, tone, and analysis depth

## Evaluation

Run the evaluator to check newsletter quality:

```
Evaluate the latest AI espresso output
```

This measures coverage completeness, relevance, and factual accuracy, producing a JSON report in `./output/eval-YYYY-MM-DD.json`.
