# AI Espresso Evaluator

Evaluate a generated AI Espresso newsletter for quality across three dimensions:
coverage, relevance, and accuracy.

## Input

Read the most recent HTML file from `./output/` (or a specific file if provided).
Extract all news items, their summaries, source links, and section assignments.

## Evaluation Process

### Step 1: Coverage Completeness

Determine whether the newsletter captured the major AI stories of the day.

1. Use `mcp__perplexity__perplexity_ask` with `search_recency_filter: "day"` to query:
   "What were the most important AI news stories in the last 24 hours?"
2. Extract the list of major stories from the Perplexity response.
3. For each major story, check if the newsletter contains a matching item.
4. Calculate: `coverage_score = matched_stories / total_major_stories`
5. List any missed stories.

### Step 2: Relevance / Signal Quality

Assess whether each included item belongs in a strategic AI briefing.

For each item in the newsletter, evaluate:
- Is it about AI? (yes/no)
- Is it from the last 48 hours? (yes/no)
- Is it strategically significant, not trivial? (yes/no)
- Is it placed in the correct section? (yes/no)

Calculate: `relevance_score = items_passing_all_checks / total_items`

Flag any items that fail a check, with the reason.

### Step 3: Factual Accuracy

Verify that each item's "What happened" summary is faithful to the source.

For each item:
1. Use `WebFetch` to visit the cited source URL
2. Compare the newsletter's summary against the actual source content
3. Check for:
   - Invented facts not in the source
   - Exaggerated claims
   - Misattributed quotes
   - Wrong dates or numbers
4. Mark as: accurate, minor_issue, or major_issue

Calculate: `accuracy_score = accurate_items / total_items`

### Step 4: Structural Checks

Verify the newsletter follows the guidelines:
- Frontier Labs section exists and is first
- Total items between 5 and 8
- Every item has all three analysis parts
- Every item has a source link
- No hype language detected

### Step 5: Generate Report

Write the evaluation report as JSON to `./output/eval-YYYY-MM-DD.json`:

```json
{
  "date": "YYYY-MM-DD",
  "file_evaluated": "./output/YYYY-MM-DD.html",
  "coverage": {
    "score": 0.0,
    "major_stories_found": [],
    "stories_in_newsletter": [],
    "missed": []
  },
  "relevance": {
    "score": 0.0,
    "items_evaluated": 0,
    "items_relevant": 0,
    "flagged": []
  },
  "accuracy": {
    "score": 0.0,
    "items_checked": 0,
    "items_verified": 0,
    "issues": []
  },
  "structure": {
    "frontier_section_first": true,
    "item_count": 0,
    "item_count_in_range": true,
    "all_items_have_analysis_triple": true,
    "all_items_have_source_links": true,
    "hype_language_detected": false
  },
  "overall_score": 0.0
}
```

The `overall_score` is the average of coverage, relevance, and accuracy scores.

## Output

After writing the JSON report, print a human-readable summary:
- Overall score with pass/fail (threshold: 0.7)
- Per-dimension scores
- Any missed stories or flagged issues
- Recommendations for improving the skill if score is below threshold
