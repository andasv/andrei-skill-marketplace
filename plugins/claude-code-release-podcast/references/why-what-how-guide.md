# WHY / WHAT / HOW Schema

Every CHANGELOG bullet is expanded into exactly three sentences, in this order:

## WHY (one sentence)
The **motivating problem** this feature addresses. What was annoying, slow, impossible, or error-prone before?
- Speak in terms of the user's pain: "Teams kept losing context when…", "Users couldn't…", "Long-running sessions hit…"
- No fluff ("to improve UX") — name the concrete friction.
- Max 25 words.

## WHAT (one sentence)
What the feature **actually is**, in plain terms.
- Name the mechanism: a new flag, a new slash command, a new env var, a new hook event, a new model, etc.
- No marketing verbs ("empowers", "unlocks"). Prefer "adds", "allows", "exposes", "switches".
- Max 25 words.

## HOW (one sentence)
The **minimum concrete invocation** to use it today.
- Include the exact command, flag, env var, or settings.json key.
- Use monospace-friendly output when possible (the podcast transcript and description both benefit).
- If the feature is an internal change with no user-facing switch, say so: "Automatic — no user action required."
- Max 25 words.

## Tone rules

- Write for a developer who uses Claude Code daily but hasn't read the changelog.
- No hype. No "we're excited to announce". Just the signal.
- Prefer present tense: "adds", "lets you", "reports", not "will add" or "has added".
- Quote exact syntax rather than paraphrasing: `ENABLE_PROMPT_CACHING_1H=true`, `/recap`, `--resume`.
- If a bullet references a feature you can't verify from the docs + one search, say so honestly in the WHAT line ("Details not yet documented publicly.") rather than guessing.

## Example

**CHANGELOG bullet:**
> Added `ENABLE_PROMPT_CACHING_1H` env var to opt into 1-hour prompt cache TTL on API key, Bedrock, Vertex, and Foundry

**Expanded:**
- **WHY**: Default prompt cache TTL of 5 minutes forces long-running sessions to re-pay for cache misses every few exchanges.
- **WHAT**: Adds an opt-in env var that extends the prompt cache TTL to one hour across all supported provider backends.
- **HOW**: Set `ENABLE_PROMPT_CACHING_1H=true` in your shell or Claude Code config before starting a session.
