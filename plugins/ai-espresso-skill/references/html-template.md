# HTML Template Reference

When generating the newsletter HTML, follow this exact structure and styling.
The output must be a self-contained HTML file with all CSS inline (no external stylesheets or fonts).

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Espresso — {{DATE}}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #fafafa;
      color: #1a1a1a;
      line-height: 1.6;
      padding: 24px 16px;
    }

    .container {
      max-width: 680px;
      margin: 0 auto;
    }

    .header {
      margin-bottom: 32px;
      padding-bottom: 16px;
      border-bottom: 2px solid #e0e0e0;
    }

    .header h1 {
      font-size: 28px;
      font-weight: 700;
      color: #1a1a1a;
    }

    .header .date {
      font-size: 14px;
      color: #666;
      margin-top: 4px;
    }

    .section {
      margin-bottom: 32px;
    }

    .section-title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid #e0e0e0;
    }

    /* Official news section (Anthropic & OpenAI) */
    .section.official .section-title {
      color: #6b4c35;
      border-bottom-color: #6b4c35;
    }

    .section.official .item-summary {
      font-size: 14px;
      color: #333;
      margin-bottom: 8px;
    }

    .na-text {
      font-size: 14px;
      color: #888;
      font-style: italic;
      padding: 12px 0;
    }

    /* Frontier Labs section gets a colored accent */
    .section.frontier .section-title {
      color: #1a56db;
      border-bottom-color: #1a56db;
    }

    /* SA picks section gets a teal accent */
    .section.sa-picks .section-title {
      color: #0d7377;
      border-bottom-color: #0d7377;
    }

    .section.sa-picks .sa-relevance {
      font-size: 14px;
      color: #333;
      margin-bottom: 8px;
    }

    /* Germany section gets a distinct accent */
    .section.germany .section-title {
      color: #c4161c;
      border-bottom-color: #c4161c;
    }

    .item {
      margin-bottom: 24px;
      padding: 16px;
      background: #fff;
      border: 1px solid #e8e8e8;
      border-radius: 6px;
    }

    .item h3 {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 12px;
      color: #1a1a1a;
    }

    .item h3 a {
      color: #1a56db;
      text-decoration: none;
    }

    .item h3 a:hover {
      text-decoration: underline;
    }

    .item-date {
      font-size: 12px;
      color: #888;
      margin-bottom: 10px;
    }

    .analysis-label {
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #888;
      margin-top: 10px;
      margin-bottom: 4px;
    }

    .analysis-text {
      font-size: 14px;
      color: #333;
      margin-bottom: 8px;
    }

    .source-link {
      font-size: 12px;
      color: #888;
    }

    .source-link a {
      color: #1a56db;
      text-decoration: none;
    }

    .footer {
      margin-top: 40px;
      padding-top: 16px;
      border-top: 1px solid #e0e0e0;
      font-size: 12px;
      color: #999;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>AI Espresso</h1>
      <div class="date">{{DATE}} — Your morning AI briefing</div>
    </div>

    <!-- Official news section ALWAYS first, uses class="section official" -->
    <div class="section official">
      <h2 class="section-title">News from Anthropic and OpenAI</h2>

      <!-- If items exist: simplified format (no analysis labels) -->
      <div class="item">
        <h3><a href="{{ITEM_URL}}">{{ITEM_TITLE}}</a></h3>
        <div class="item-date">Published: {{PUBLISHED_DATE}}</div>
        <div class="item-summary">{{FACTUAL_SUMMARY}}</div>
        <div class="source-link">Source: <a href="{{SOURCE_URL}}">{{SOURCE_NAME}}</a></div>
      </div>

      <!-- If no items in 36h window: -->
      <div class="na-text">N/A — No new announcements in the last 36 hours</div>
    </div>

    <!-- Frontier Labs section always second, uses class="section frontier" -->
    <div class="section frontier">
      <h2 class="section-title">Frontier Labs Competition Update</h2>

      <div class="item">
        <h3><a href="{{ITEM_URL}}">{{ITEM_TITLE}}</a></h3>
        <div class="item-date">Published: {{PUBLISHED_DATE}}</div>
        <div class="analysis-label">What happened</div>
        <div class="analysis-text">{{WHAT_HAPPENED}}</div>
        <div class="analysis-label">Why it matters</div>
        <div class="analysis-text">{{WHY_IT_MATTERS}}</div>
        <div class="analysis-label">Implications for Anthropic</div>
        <div class="analysis-text">{{ANTHROPIC_IMPLICATIONS}}</div>
        <div class="source-link">Source: <a href="{{SOURCE_URL}}">{{SOURCE_NAME}}</a></div>
      </div>
      <!-- Repeat .item for each item in section -->
    </div>

    <!-- Other sections: Models & Research, Products & Tools, Industry & Business -->
    <div class="section">
      <h2 class="section-title">{{SECTION_TITLE}}</h2>
      <!-- Same .item structure as above -->
    </div>

    <!-- Germany section uses class="section germany" for red accent -->
    <div class="section germany">
      <h2 class="section-title">AI in Germany</h2>
      <!-- Same .item structure as above -->
    </div>

    <!-- SA picks section ALWAYS last, uses class="section sa-picks" -->
    <div class="section sa-picks">
      <h2 class="section-title">Top 5 for Anthropic Solution Architect</h2>

      <div class="item">
        <h3><a href="{{ITEM_URL}}">{{ITEM_TITLE}}</a></h3>
        <div class="item-date">Published: {{PUBLISHED_DATE}}</div>
        <div class="sa-relevance">{{SA_RELEVANCE_SUMMARY}}</div>
        <div class="source-link">Source: <a href="{{SOURCE_URL}}">{{SOURCE_NAME}}</a></div>
      </div>
      <!-- Exactly 5 items. Simplified format: title, date, SA-relevance summary, source. -->
    </div>

    <div class="footer">
      Generated on {{TIMESTAMP}} by AI Espresso
    </div>
  </div>
</body>
</html>
```

## Key Rules

1. The "News from Anthropic and OpenAI" section ALWAYS renders first using `class="section official"` (brown accent). Show "N/A" if no items in 36h. Uses simplified item format (no analysis labels).
2. The Frontier Labs section ALWAYS uses `class="section frontier"` for the blue accent. Excludes items already in the official section.
3. The Germany section uses `class="section germany"` for the red accent
4. The SA picks section ALWAYS renders last using `class="section sa-picks"` (teal accent). Simplified format: title, date, SA-relevance summary. Exactly 5 items. 72h lookback, deduped against previous editions.
5. Other sections use just `class="section"`
3. Every item title links to the source article
4. Every item must show a "Published: " date line (e.g., "Published: March 21, 2026") immediately below the title
5. The three analysis parts (what happened, why it matters, implications for Anthropic) must always be present
5. Keep the HTML valid and self-contained — no external resources
6. Date format in the header: "March 22, 2026" (human-readable)
7. Timestamp in the footer: ISO format with time
