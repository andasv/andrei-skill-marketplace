---
name: elternportal-vertretungsplan
description: Fetch the current Vertretungsplan (substitution plan) from Eltern-Portal. Use when the user asks about substitutions, schedule changes, Vertretung, or which classes are affected today.
license: MIT
compatibility: Requires Python 3.10+, pip packages (requests, beautifulsoup4, python-dotenv, anthropic), and a .env file with Eltern-Portal credentials and Anthropic API key.
---

# Elternportal Vertretungsplan

Fetches the current substitution plan for the child's class from any Eltern-Portal school website.

## Instructions

### Step 1: Check dependencies

Ensure Python dependencies are installed:

```bash
pip3 install requests beautifulsoup4 python-dotenv anthropic
```

### Step 2: Fetch the data

Run the extraction script:

```bash
python3 {baseDir}/scripts/fetch.py
```

The script:
1. Reads credentials from `.env` (walks up parent directories to find it)
2. Authenticates against the Eltern-Portal using CSRF token + POST login
3. Fetches the Vertretungsplan HTML page
4. Uses Claude Haiku with structured tool use to extract JSON data

### Step 3: Present the results

Parse the JSON output and present it to the user:

- **If the output contains an `"error"` key:** Report the error clearly. Common issues: missing `.env`, wrong credentials, missing `ANTHROPIC_API_KEY`.
- **If there are substitutions:** Show a summary with:
  - Class name and last-updated timestamp
  - For each day, a markdown table with columns: Period | Absent Teacher | Substitute | Subject Change | Room | Info
  - For subject changes where `original_subject` is non-empty, format as "Original → Replacement" (e.g. "D_1 → G")
  - If `original_subject` is empty, just show `replacement_subject`
- **If there are no days at all:** Tell the user there are currently no substitutions listed.

### Example output format

**Vertretungsplan Klasse 6C** (Stand: 16.03.2026 07:41:22)

**Mo., 16.03.2026 (KW 12)**

| Std. | Absent | Substitute | Subject | Room | Info |
|------|--------|------------|---------|------|------|
| 6.   | Ru     | Pb         | D_1 → G | A105 | Vertretung |

## Configuration

The script reads from a `.env` file (searched in parent directories):

- `URL` — Eltern-Portal base URL (e.g. `https://schoolcode.eltern-portal.org`)
- `USER` — Login email address
- `PASSWORD` — Login password
- `ANTHROPIC_API_KEY` — Anthropic API key for Claude Haiku extraction
