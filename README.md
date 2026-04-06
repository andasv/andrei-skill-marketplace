# andrei-skill-marketplace

A [Claude Code](https://claude.ai/claude-code) plugin marketplace.

## Available Plugins

| Plugin | Description | Repo |
|--------|-------------|------|
| `elternportal` | Substitution plans & parent letters from Eltern-Portal | [andasv/elternportal-skill](https://github.com/andasv/elternportal-skill) |

## Installation

### 1. Add this marketplace

```
/plugin marketplace add andasv/andrei-skill-marketplace
```

Or add to `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "andrei-skill-marketplace": {
      "source": {
        "source": "github",
        "repo": "andasv/andrei-skill-marketplace"
      }
    }
  }
}
```

### 2. Install a plugin

```
/plugin install elternportal@andrei-skill-marketplace
```

### 3. Use the skills

```
/elternportal:elternportal-vertretungsplan
/elternportal:elternportal-elternbriefe
```

## Adding a Plugin

To add your plugin to this marketplace:

1. Ensure your repo has a `.claude-plugin/plugin.json` manifest
2. Ensure your skills are in `skills/<skill-name>/SKILL.md`
3. Open a PR adding your plugin entry to `.claude-plugin/marketplace.json`
