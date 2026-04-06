# Content Analysis Guide

## Purpose
Parse an AI Espresso HTML briefing and produce a structured content brief that the transcript generation phase will use to write the podcast dialogue.

## Input Format
The AI Espresso skill outputs a self-contained HTML file with these sections (in order):
1. **News from Anthropic and OpenAI** (`.section.official`) — factual listings, no analysis labels
2. **Frontier Labs Competition Update** (`.section.frontier`) — competitive moves with full analysis
3. **Models & Research** (`.section`) — open-source models, research breakthroughs
4. **Products & Tools** (`.section`) — new launches, developer tools
5. **Industry & Business** (`.section`) — funding, M&A, regulatory
6. **AI in Germany** (`.section.germany`) — local market news
7. **Top 5 for Anthropic Solution Architect** (`.section.sa-picks`) — curated SA-relevant items

Each item contains:
- Title (in `h3 > a` with source URL)
- Published date (in `.item-date`)
- Analysis blocks: "What happened", "Why it matters", "Implications for Anthropic" (in `.analysis-label` + `.analysis-text` pairs)
- Source link

## Topic Ranking Criteria

Score each news item on three dimensions (1-5 each):

### 1. Strategic Significance (weight: 40%)
- How much does this change the AI landscape?
- Does it affect major players, pricing, capabilities, or market dynamics?
- Is this a first-of-its-kind event or incremental?

### 2. Discussion Potential (weight: 35%)
- Does this topic have natural tension or surprise?
- Can two people with different perspectives (technical vs. business) have an interesting exchange about it?
- Are there non-obvious implications worth exploring?

### 3. Audience Accessibility (weight: 25%)
- Can this be explained engagingly to a knowledgeable but non-specialist listener?
- Is there a relatable analogy or real-world impact?
- Will the listener care about this tomorrow, not just today?

## Selection Rules
- For a 2-minute episode (default): select the **single highest-scoring item**
- For a 5-minute episode: select the **top 2 items**
- For a 10-minute episode: select the **top 3-4 items**
- If multiple items score similarly, prefer the one from a higher-priority section (frontier > official > models > industry)

## Discussion Beat Generation

For each selected topic, generate 3-5 discussion beats:

Each beat should contain:
- **Hook**: The opening angle for this beat (1 sentence)
- **Depth point**: The deeper insight to explore (1-2 sentences)
- **Emotional tone**: surprise / analysis / concern / excitement / speculation

### Beat Arc Pattern
The beats should follow this emotional arc:
1. **Opening beat**: Surprise or intrigue — "Did you see that [X] just happened?"
2. **Context beat**: Analysis — "Here's why this is significant..."
3. **Deep beat**: Implications — "What this really means for [customers/engineers/the market]..."
4. **Forward beat**: Speculation — "Where does this go from here?"
5. **Closing beat** (optional for longer episodes): Personal take — "What I find most interesting is..."

## Output Format

Produce a content brief with this structure:

```
CONTENT BRIEF
=============
Date: [date from HTML]
Source: [HTML file path]
Duration target: [X] minutes
Topics selected: [N]

TOPIC 1: [Title]
Section: [which section it came from]
Source URL: [link]
Score: [total] (significance: X, discussion: X, accessibility: X)

Discussion Beats:
1. [Hook] | Tone: [emotion]
   Depth: [deeper point]
2. [Hook] | Tone: [emotion]
   Depth: [deeper point]
3. [Hook] | Tone: [emotion]
   Depth: [deeper point]

Key facts to mention:
- [fact 1]
- [fact 2]
- [fact 3]

Suggested episode arc: [surprise → analysis → implications → forward look]
```
