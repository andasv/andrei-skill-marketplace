# Transistor Episode Description Template

Transistor's `description` field accepts basic HTML. Use this template to build the HTML string passed to `mcp__transistor__create_episode`.

## Structure

```html
<h2>What's new in Claude Code v{VERSION}</h2>

<p>{SUMMARY_PARAGRAPH}</p>

<h3>{BULLET_1_HEADLINE}</h3>
<p><strong>Why:</strong> {WHY_SENTENCE}</p>
<p><strong>What:</strong> {WHAT_SENTENCE}</p>
<p><strong>How:</strong> <code>{COMMAND_OR_FLAG}</code> — {HOW_SENTENCE_REMAINDER}</p>

<h3>{BULLET_2_HEADLINE}</h3>
<p><strong>Why:</strong> …</p>
<p><strong>What:</strong> …</p>
<p><strong>How:</strong> …</p>

<!-- repeat <h3> + three <p> per remaining bullet -->

<hr>

<p>Hosts: Alex Chen &amp; Sarah Kim · Generated from the official Claude Code CHANGELOG.</p>
<p>Full changelog: <a href="https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md">github.com/anthropics/claude-code/CHANGELOG.md</a></p>
<p>Claude Code docs: <a href="https://docs.claude.com/en/docs/claude-code">docs.claude.com/en/docs/claude-code</a></p>
```

## Rules

- **Headlines (`<h3>`)** are derived from the CHANGELOG bullet, trimmed to ≤60 chars, capitalized as a short sentence. Example: `- Added /recap feature…` → `New /recap command`.
- **HOW** prefers `<code>` for the command/flag. If there's nothing to invoke, write the remainder as plain prose and omit the `<code>` element.
- **Summary paragraph** is a single sentence (≤200 chars) capturing the headline feature of the release. It doubles as the Transistor `summary` field (strip HTML when copying to `summary`).
- Allowed HTML tags only: `<h2> <h3> <p> <a> <strong> <em> <code> <ul> <li> <hr>`. No inline styles, no scripts.
- Always end with the CHANGELOG link and the docs link. These anchor search and attribution.

## Summary (plain text, for the `summary` field)

Take the first `<p>` of the description, strip tags, truncate to 200 chars. Example:

> `Claude Code v2.1.108 extends the prompt cache TTL to 1 hour via a new env var and ships a /recap command for mid-session context catch-ups.`
