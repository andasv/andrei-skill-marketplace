# AI Espresso Editorial Guidelines

## Audience

Technology leaders and AI practitioners who need a strategic morning briefing.
Assume the reader understands AI concepts but values time-efficient synthesis.

## Tone

- Professional but not dry
- Confident analytical voice
- No hype, no breathless language ("revolutionary", "game-changing", "unprecedented")
- Direct and concise — every sentence should earn its place

## Newsletter Sections (in order)

### 1. News from Anthropic and OpenAI (REQUIRED, always first)

Official announcements directly from the Anthropic and OpenAI newsrooms.
This section uses a **36-hour lookback window** (wider than the 24h for other sections).

- **Source**: Only items published on https://www.anthropic.com/news and
  https://openai.com/news/
- **Format**: Factual listings only — no strategic analysis. Each item gets:
  - Title (linked to source article)
  - Published date
  - 2-3 sentence factual summary
- **If no news**: Show "N/A — No new announcements in the last 36 hours"
- **Deduplication**: Items listed here are NOT duplicated in the Frontier Labs
  section. They appear in one place only.

### 2. Frontier Labs Competition Update (REQUIRED, always second)

Tracking competitive moves between Anthropic, OpenAI, and Google DeepMind/Gemini.
This is the marquee section. Include items about (excluding items already listed
in the "News from Anthropic and OpenAI" section):

- New model releases or capability upgrades
- API/product launches or pricing changes
- Partnership or platform announcements
- Hiring, org changes, or strategic pivots
- Benchmark results or capability demonstrations

Even on quiet days, include at least one item here (a "status check" if nothing
major happened).

### 3. Models & Research

LLM and foundation model developments beyond the big three:

- Open-source model releases (Meta Llama, Mistral, etc.)
- Research breakthroughs (papers, techniques)
- Benchmark methodology or evaluation news

### 4. Products & Tools

AI-powered products, developer tools, and platforms:

- New product launches or major updates
- Developer tooling and infrastructure
- Notable integrations or platform plays

### 5. Industry & Business

Business, regulatory, and market dynamics:

- Funding rounds and acquisitions
- Regulatory developments
- Market analysis and adoption trends
- Notable enterprise deployments

### 6. AI in Germany

German-specific AI developments relevant to enterprise deployment:

- **Regulatory landscape**: EU AI Act transposition status in Germany,
  BNetzA/KoKIVO enforcement updates, GDPR implications for LLM deployment,
  BSI security requirements, BaFin rules for AI in financial services
- **Local champions**: German AI companies (Aleph Alpha, DeepL, Helsing,
  Cognigy, Parloa, Langdock, Synthflow AI, etc.) — new funding, product
  launches, partnerships, competitive positioning vs. frontier labs
- **Government initiatives**: Federal AI strategy, data center expansion,
  sovereign cloud programs, public-sector AI adoption
- **Enterprise adoption**: German enterprise deals, partnerships between
  German companies and frontier labs, DACH-specific deployments
- **Data sovereignty**: Developments affecting where and how frontier models
  (Claude, ChatGPT Enterprise, Gemini Enterprise) can be deployed for
  German customers

This section should always include at least one item when relevant news exists.
On quiet days it may be omitted.

### 7. Top 5 for Anthropic Solution Architect (REQUIRED, always last)

Curated picks most relevant to an Anthropic Principal Solution Architect
who works with Claude API and Claude Code daily. Uses a **72-hour lookback**
window and draws from ALL sources (primary + Perplexity).

**Relevance filter** — include news that directly affects:
- Claude API usage patterns, pricing, limits, or capabilities
- Claude Code features, updates, or competitive positioning
- Competitor API/SDK changes (OpenAI API, Gemini API, open-weight model APIs)
- Developer tooling, IDE integrations, coding agents, and agentic workflows
- Enterprise deployment patterns, security, compliance for AI APIs
- Customer objections, competitive losses, or win opportunities
- Technical architecture decisions (RAG, function calling, long context, MCP)

**Deduplication** — Before including an item, check all existing HTML files
in `./output/` from previous days. If a story was already covered in a prior
edition, do NOT include it again unless there is a material update.

**Format** — Each item gets:
- Title (linked)
- Published date
- 2-3 sentence summary explaining **why this matters to a Solutions Architect**
  (not generic significance — specific to customer conversations, demos,
  technical guidance, or competitive positioning)

Exactly 5 items. If fewer than 5 qualify after dedup, include the best
available and note "X of 5 — light period for SA-relevant news."

## Per-Item Analysis Format

Each item includes a published date and the analysis pair:

**Published date**: The exact date the news was published (e.g., "March 21, 2026").
If the exact date is uncertain, use the best estimate and add "(approx.)".

**What happened**: Factual account. 2-3 sentences. Cite the source.
Include the source link.

**Why it matters**: Strategic significance. Connect to broader trends,
competitive dynamics, or market implications. 2-3 sentences.

**Implications for Anthropic**: Tactical and strategic implications to
Anthropic's business. Frame as neutral observations, not recommendations.
Cover the full strategic scope: commercial impact (sales, customers,
partnerships), product implications (feature gaps, capability comparisons,
roadmap pressure), hiring/talent dynamics, and regulatory positioning.
2-3 sentences.

For the **AI in Germany** section, add extra depth to the Anthropic
implications: reference specific local market dynamics (Betriebsrat/works
council requirements, DACH competitive landscape, data sovereignty
expectations, German enterprise buying patterns, local partner ecosystem).

## Selection Criteria

- 5-8 items total per edition
- Frontier Labs section: 1-3 items (always at least 1)
- Remaining sections: distribute remaining items by significance
- Prefer fewer, deeper items over many shallow ones
- An item that spans multiple sections goes in the most relevant one

## What NOT to Include

- Routine job postings or minor hiring
- Social media drama without substance
- Unverified rumors (unless from highly credible sources, clearly labeled)
- Tutorials, how-to content, or educational material
- Events/conferences unless a major announcement was made there
- Minor version bumps or patch releases

## Date Handling

- "Last 24 hours" means from the current time minus 24 hours
- When publication dates are ambiguous, include the item but note uncertainty
- If a story broke late yesterday and is still developing, include it
