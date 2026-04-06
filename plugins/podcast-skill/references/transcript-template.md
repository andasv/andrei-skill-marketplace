# Transcript Template

## Format

The podcast transcript is a markdown file with YAML frontmatter and speaker-labeled turns.

## Example (2-minute episode, ~300 words)

```markdown
---
date: 2026-04-06
source_file: ai-espresso-2026-04-06.html
personas:
  - alex-chen
  - sarah-kim
duration_target: 2 minutes
topic: "OpenAI launches GPT-5 with native tool use"
---

<!-- INTRO -->

**ALEX:** So OpenAI just dropped GPT-5 and honestly, the headline feature isn't what I expected. It's not about the benchmarks — it's native tool use baked right into the model architecture.

**SARAH:** Wait, native tool use? As in, not the bolted-on function calling we've been working with? That's actually a big deal for enterprise adoption.

<!-- DISCUSSION -->

**ALEX:** Exactly. So instead of the model generating a JSON blob that your app then parses and executes, GPT-5 can directly reason about when and how to use tools as part of its inference process. Think of it like the difference between reading a recipe and actually knowing how to cook.

**SARAH:** That analogy is perfect. Because from a customer perspective, the biggest friction point with AI agents has been reliability. I've had enterprise customers tell me they love the demo but can't trust it in production. If tool use is more reliable, that changes the conversion math completely.

**ALEX:** Right, and the technical reason it's more reliable is fascinating. They trained the tool-use behavior into the base model rather than fine-tuning it on top. So the model doesn't just know tools exist — it understands them the way it understands language.

**SARAH:** So what does this mean competitively? Because Anthropic and Google are both working on similar capabilities. Is this a lasting advantage or just a timing thing?

**ALEX:** I think it's a six-month window at most. But six months in this market is an eternity. The real question is who gets enterprise trust first.

<!-- OUTRO -->

**SARAH:** That's the billion-dollar question right there. Alright, that's our take on GPT-5's launch. The tool use story is the one to watch — it could be what finally makes AI agents production-ready. Until next time!
```

## Rules
- Speaker prefix format: `**NAME:**` followed by a space and dialogue text
- Section markers: `<!-- INTRO -->`, `<!-- DISCUSSION -->`, `<!-- OUTRO -->`
- Each turn: 2-4 sentences
- Frontmatter must include: date, source_file, personas, duration_target, topic
- No stage directions or parenthetical notes — just dialogue
- Names must match the `name` field in the persona .md files exactly
