---
name: ai-espresso
description: Generate a strategic morning AI news briefing covering the last 24 hours, saved as an HTML file. Use this skill whenever the user asks for an AI news update, morning briefing, AI espresso, frontier lab competition tracking, what happened in AI today/yesterday, or any request related to recent AI industry developments. Even if the user just casually mentions wanting to catch up on AI news, this is the right skill to use.
---

# AI Espresso — Morning AI Briefing Generator

Generate a concise, strategically analyzed AI news briefing covering the last 24 hours.
The output is a self-contained HTML file saved to `./output/`.

## MCP Dependencies

This skill requires the following MCP server to be configured:

| MCP Server | Purpose | Required Tools |
|------------|---------|----------------|
| **Exa** | Web search for gap-filling news coverage | `mcp__exa__web_search_exa` |

The Exa MCP server handles API authentication internally. No API keys need to be configured in the skill itself.

## Tools Used

- **mcp__exa__web_search_exa** — Gap-fill web search queries for frontier labs, industry news, and Germany AI news (date filtering embedded in query text)
- **WebFetch** — Fetch webpages (Anthropic News) and RSS feeds (OpenAI `news/rss.xml`, SMOL AI)
- **Read** — Load `sources.md`, `guidelines.md`, `references/html-template.md`, and previous editions from `./output/` for deduplication
- **Glob** — Find previous edition HTML files in `./output/` for cross-checking (Phase 3.5)
- **Write** — Save the generated HTML file to `./output/YYYY-MM-DD.html`

## Version

Read `VERSION.md` from this skill's directory when the user asks about the skill
version (e.g., "what version?", "ai-espresso version", "which version am I running?").
Report the version number from that file.

Follow these five phases in order. Do not skip phases.

---

## Phase 1: Load Configuration

1. Read `sources.md` from this skill's directory to get the source list, priorities, and fetch instructions.
2. Read `guidelines.md` from this skill's directory to get editorial rules, section structure, and analysis format.
3. Note today's date. The lookback window is the last 24 hours from now.

---

## Phase 2: Fetch Primary Sources

Process sources in priority order (P0 first, then P1). For each source:

### For Anthropic News (webpage):
Use `WebFetch` on `https://www.anthropic.com/news` to retrieve the page. Extract article titles, publication dates, summaries, and URLs. Use a **36-hour lookback window**. Items published within the last 36 hours are placed in the "News from Anthropic and OpenAI" section as factual listings (no analysis), then **excluded** from the Frontier Labs section.

### For OpenAI News (RSS — do NOT use openai.com/news/ webpage, it is blocked by Cloudflare):
Use `WebFetch` on `https://openai.com/news/rss.xml` to retrieve the RSS feed. This is the only reliable way to get OpenAI news. Parse the feed and filter items by `pubDate` within the last **36 hours**. Items are placed in the "News from Anthropic and OpenAI" section as factual listings, then **excluded** from the Frontier Labs section.

### For other webpage sources:
Use `WebFetch` to retrieve the page. Use the standard 24-hour lookback. If publication dates are ambiguous, include the item and note uncertainty.

### For RSS sources (SMOL AI News, OpenAI News):
Use `WebFetch` to retrieve the RSS feed XML. Parse the feed and extract items with `pubDate` within the lookback window. For each item, capture:
- Title
- Link
- Publication date
- Description/summary

### Handling fetch failures:
If a WebFetch call fails (timeout, 403, redirect loop), log the failure and continue with remaining sources. Do not stop the entire workflow because one source is unavailable.

Collect all items into a working list. For each item, track:
- Title
- Source name and URL
- Publication date
- Brief summary (2-3 sentences)
- Topic category (frontier_labs / models_research / products_tools / industry_business / ai_in_germany)

---

## Phase 3: Gap-Fill with Exa Search

After processing primary sources, assess coverage:
- Do you have at least 1 item about Anthropic, OpenAI, or Google Gemini competitive moves?
- Do you have coverage across at least 2 of the 5 topic categories?
- Do you have any Germany-specific AI news?

Use Exa to fill gaps. Run up to 5 queries maximum. Embed today's date in each query for recency:

1. **Always run**: Use `mcp__exa__web_search_exa` with query "Most important Anthropic OpenAI Google Gemini AI announcements competitive moves today {DATE}" and `numResults: 10`.

2. **Always run**: Use `mcp__exa__web_search_exa` with query "Biggest AI industry news stories today {DATE}" and `numResults: 10`.

3. **Always run**: Use `mcp__exa__web_search_exa` with query "AI news developments Germany today {DATE} EU AI Act German AI startups Aleph Alpha DeepL enterprise AI data sovereignty" and `numResults: 10`.

4. **If gaps remain**: Use `mcp__exa__web_search_exa` with targeted queries for uncovered topic categories, embedding today's date.

Where `{DATE}` is the current date in human-readable format (e.g., "April 6 2026").

For each new item discovered via search:
- Check it is not a duplicate of an item already in the working list
- Add it with source attribution from the Exa result URLs
- Mark its topic category

---

## Phase 3.5: Cross-Check Against Previous Editions

Before selecting items, check for prior coverage to avoid repeating stories:

1. Use `Glob` to find existing HTML files in `./output/` (pattern: `output/*.html`).
2. For each file from the previous 3 days, use `Read` to scan for item titles.
3. Build a list of previously covered story titles/topics.
4. Mark any items in the working list that were already covered. These are excluded from the "Top 5 for Agentic AI Engineering Leader" section (unless there is a material update). They may still appear in other sections if they are from the last 24h.

---

## Phase 4: Prioritize, Filter, and Analyze

### Selection (target: 5-8 items for main sections + 5 for leader picks section)

Apply these rules in order:

1. **Frontier Labs items are mandatory.** Any item about Anthropic, OpenAI, or Google Gemini competitive moves (model launches, product updates, API changes, pricing, partnerships, benchmarks) must be included. Target 1-3 items for this section.

2. **Fill remaining slots by significance.** From the remaining items, select the most strategically significant ones. Balance across Models & Research, Products & Tools, and Industry & Business. Prefer fewer, deeper items over many shallow ones.

3. **Cut to 8 maximum.** If you have more than 8 strong items, drop the least impactful ones. If you have fewer than 5, expand the Exa search scope (broaden queries to cover the past week, e.g., "AI news this week {DATE}").

### Analysis

For each selected item, write the analysis as defined in `guidelines.md`:

- **What happened**: Factual account, 2-3 sentences. Cite the source with a link.
- **Why it matters**: Strategic significance, competitive dynamics, market implications. 2-3 sentences.
- **Implications for Anthropic**: Tactical and strategic implications to Anthropic's business. Neutral observations covering commercial, product, hiring, and regulatory positioning. 2-3 sentences. For the AI in Germany section, add extra depth referencing DACH market dynamics, data sovereignty, works councils, and local competitive landscape.

### Top 5 for Agentic AI Engineering Leader

After selecting the main section items, separately curate the leader picks section:

1. From ALL collected items (primary sources + Exa, using a **72-hour lookback**), filter for leadership relevance: LLM API changes, developer tooling, agentic workflows, enterprise deployment patterns, MCP/RAG/function calling, coding agents, competitive positioning signals.
2. Run one additional Exa query if needed: `mcp__exa__web_search_exa` with query "Claude API Claude Code OpenAI API coding agent developer AI tooling news past 3 days {DATE}" and `numResults: 10`.
3. Exclude any story already covered in a previous day's `./output/` HTML file (from Phase 3.5 dedup), unless there is a material update.
4. Select exactly 5 items. Each gets a 2-3 sentence summary explaining why it matters to an agentic AI engineering leader (technical decisions, team tooling, competitive landscape, deployment strategy).
5. Items in this section MAY also appear in the main sections above — this is the only section where duplication is allowed, since it serves a different analytical lens.

### Grouping

Assign each item to exactly one main section (leader picks section is separate):
1. News from Anthropic and OpenAI (factual listings only, no analysis — populated in Phase 2 from official newsrooms with 36h lookback)
2. Frontier Labs Competition Update (excludes items already in section 1)
3. Models & Research
4. Products & Tools
5. Industry & Business
6. AI in Germany
7. Top 5 for Agentic AI Engineering Leader (separate curation, 72h lookback, deduped against previous editions)

The "News from Anthropic and OpenAI" section always appears — show "N/A — No new announcements in the last 36 hours" if empty. The Frontier Labs section also always appears. Other sections with no items are omitted. The "AI in Germany" section should appear whenever relevant German AI news exists.

---

## Phase 5: Generate HTML Output

1. Read `references/html-template.md` from this skill's directory for the HTML structure and CSS styling to follow.

2. Generate the HTML file following that template exactly:
   - Use `class="section frontier"` for the Frontier Labs section
   - Use `class="section"` for all other sections
   - Every item title links to the source article
   - Include all three analysis parts for every item
   - Header shows "AI Espresso" and today's date in human-readable format
   - Footer shows generation timestamp

3. Write the file to `./output/YYYY-MM-DD.html` using today's date (e.g., `./output/2026-03-22.html`). Create the `output/` directory if it does not exist.

4. Confirm to the user:
   - Output file path
   - Number of items included
   - Section breakdown (how many items per section)
   - Any sources that failed to fetch

---

## Quiet Day Handling

If very few items are found (fewer than 3 after all fetching and searching):
- Still produce the briefing with what you have
- Add a note at the top: "Light news day — fewer items than usual"
- The Frontier Labs section must still appear, even if it's a brief "no major moves" status check
