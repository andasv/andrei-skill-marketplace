# AI Espresso Sources

Sources are fetched in priority order. Higher priority sources are processed first
and their items take precedence in case of deduplication.

## Priority Levels

- **P0 (Critical)**: Always fetch. Items from these sources are included unless
  clearly irrelevant. These are the frontier lab official channels.
- **P1 (High)**: Always fetch. Items compete on merit with other P1 items.
- **P2 (Standard)**: Search-based discovery to fill coverage gaps after P0/P1.

---

## Source List

### P0 — Frontier Labs (Official)

| Source | Type | URL | Fetch Notes |
|--------|------|-----|-------------|
| Anthropic News | webpage | https://www.anthropic.com/news | Extract announcements, blog posts, research papers from last 24h |
| OpenAI News | rss | https://openai.com/news/rss.xml | Parse RSS feed, filter items by pubDate within last 36h. The webpage (openai.com/news/) is blocked by Cloudflare bot challenge — always use the RSS feed instead |

### P1 — Curated Aggregators

| Source | Type | URL | Fetch Notes |
|--------|------|-----|-------------|
| SMOL AI News | rss | https://news.smol.ai/rss.xml | Parse RSS feed, filter items by pubDate within last 24h |

### P2 — Search-Based Discovery

These are not fetched directly. Instead, Perplexity search queries are used
to fill coverage gaps after P0 and P1 sources are processed.

| Query Template | Tool | Filter |
|----------------|------|--------|
| "Google Gemini AI announcements today {date}" | perplexity_ask | recency: day |
| "AI industry news today {date}" | perplexity_ask | recency: day |
| "new AI products tools launched today {date}" | perplexity_search | recency: day |
| "LLM foundation model releases today {date}" | perplexity_search | recency: day |
| "Germany AI news regulations enterprise {date}" | perplexity_ask | recency: day |
| "German AI startups Aleph Alpha DeepL Helsing news {date}" | perplexity_search | recency: day |

---

## Adding Sources

To add a new source, append it to the appropriate priority table above.

**Required fields:**
- **Source**: Human-readable name
- **Type**: `webpage` (HTML page to scrape), `rss` (RSS/Atom feed), or `search` (Perplexity query)
- **URL** (for webpage/rss) or **Query Template** (for search)
- **Fetch Notes** or **Filter**: Instructions for how to extract relevant items
