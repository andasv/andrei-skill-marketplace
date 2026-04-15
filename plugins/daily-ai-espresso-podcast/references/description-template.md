# Transistor Episode Description Template

Used by `daily-ai-espresso-podcast` to build the `description` field passed to `mcp__transistor__create_episode` for the **Daily AI Espresso** show.

## Structure

```html
<h2>{{HUMAN_DATE}} — Daily AI Espresso</h2>

<p>{{ONE_LINE_HOOK}}</p>

<h3>Today's stories</h3>
<ol>
  <li><a href="{{ITEM_URL_1}}">{{ITEM_TITLE_1}}</a> — {{ONE_LINE_TAKEAWAY_1}}</li>
  <li><a href="{{ITEM_URL_2}}">{{ITEM_TITLE_2}}</a> — {{ONE_LINE_TAKEAWAY_2}}</li>
  <!-- repeat per covered item, in narrative order -->
</ol>

<hr>

<p>Hosts: Alex Chen &amp; Sarah Kim · Generated from the AI Espresso morning briefing.</p>
<p>Source briefing: <a href="https://github.com/andasv/andrei-skill-marketplace">andrei-skill-marketplace</a> · Feed: <a href="https://feeds.transistor.fm/daily-ai-espresso">daily-ai-espresso</a></p>
```

## Rules

- `{{HUMAN_DATE}}` — e.g. `April 15, 2026` (matches the AI Espresso HTML header date format).
- `{{ONE_LINE_HOOK}}` — single sentence ≤ 200 chars summarizing the day's top story or theme. Doubles as the Transistor `summary` field (strip HTML when copying).
- `{{ITEM_URL_*}}` — source article URL straight from the AI Espresso HTML `<h3><a href="...">` element.
- `{{ITEM_TITLE_*}}` — story headline as it appears in the briefing.
- `{{ONE_LINE_TAKEAWAY_*}}` — one short sentence summarizing what changed and why a builder should care. ≤ 100 chars.
- Order items in the list by the order they're discussed in the dialogue (matches the chapter order).
- Keep total description under 4,000 chars to render cleanly in podcast directories.

## Summary field (plain text)

Take `{{ONE_LINE_HOOK}}` verbatim, no HTML, ≤ 200 chars. Example:

> Apple drops M5 Pro with 45 TOPS NPU; Google ships Gemini 3 Flash with 1M-token context; OpenAI quietly halves o3-pro pricing.
