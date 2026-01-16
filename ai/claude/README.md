# Claude Code Setup

Personal Claude Code configuration. Optimized for Opus 4.5.

## Quick Install

```bash
# 1. Install plugins
claude mcp add frontend-design -- npx -y @anthropic-ai/claude-code-plugins@latest frontend-design
claude mcp add dev-browser -- npx -y @anthropic-ai/dev-browser-mcp@latest
claude mcp add ast-grep -- npx -y @anthropic-ai/ast-grep-mcp@latest
claude mcp add pg -- npx -y @anthropic-ai/pg-mcp@latest

# 2. Install skills (interactive - select all)
npx add-skill vercel-labs/agent-skills

# 3. Sync this dotfiles config
./sync.sh
```

## What Gets Installed

### Plugins (MCP servers)

| Plugin | Purpose |
|--------|---------|
| `frontend-design` | Create production-grade UI components |
| `dev-browser` | Browser automation and testing |
| `ast-grep` | AST-based code search and analysis |
| `pg` | PostgreSQL/TimescaleDB guidance |

### Skills (from Vercel)

| Skill | Purpose |
|-------|---------|
| `react-best-practices` | 45 React/Next.js performance rules |
| `web-design-guidelines` | UI audit against 100+ best practices |

### Skills (from this repo)

| Skill | Purpose |
|-------|---------|
| `writing-style` | Personal writing voice for technical content |
| `serverless-aws` | AWS Lambda/DynamoDB/SQS patterns |
| `gemini-image-generator` | Generate images via Gemini API |

### Commands (from this repo)

| Command | Purpose |
|---------|---------|
| `/custom-scratchpad` | Track work across sessions |
| `/custom-take-notes` | Document technical discoveries |
| `/custom-fix-merge-conflict` | Resolve merge conflicts automatically |

### Hooks (from this repo)

| Hook | Purpose |
|------|---------|
| `block-hardcoded-secrets` | Block commits with API keys/passwords |

## Settings

Recommended `~/.claude/settings.json`:

```json
{
  "env": {
    "MAX_THINKING_TOKENS": "31999"
  },
  "includeCoAuthoredBy": false,
  "alwaysThinkingEnabled": true
}
```

## Structure

```
ai/claude/
├── README.md           # This file
├── CLAUDE.md           # Project template (copy to repos)
├── sync.sh             # Sync script
├── commands/           # → ~/.claude/commands/ (prefixed custom-)
│   ├── scratchpad.md
│   ├── take-notes.md
│   └── fix-merge-conflict.md
├── hooks/              # → ~/.claude/hooks/
│   └── block-hardcoded-secrets.md
└── skills/             # → ~/.claude/skills/
    ├── writing-style/
    ├── serverless-aws/
    └── gemini-image-generator/
```

## Manual Sync

```bash
# Commands (add custom- prefix)
for f in commands/*.md; do
  cp "$f" ~/.claude/commands/custom-$(basename "$f")
done

# Hooks and skills (direct copy)
cp -r hooks/* ~/.claude/hooks/
cp -r skills/* ~/.claude/skills/
```
