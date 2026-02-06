# Claude Code Setup

Personal Claude Code configuration.

## Quick Install

```bash
# 1. Install plugins
claude mcp add frontend-design -- npx -y @anthropic-ai/claude-code-plugins@latest frontend-design
claude mcp add dev-browser -- npx -y @anthropic-ai/dev-browser-mcp@latest
claude mcp add ast-grep -- npx -y @anthropic-ai/ast-grep-mcp@latest
claude mcp add pg -- npx -y @anthropic-ai/pg-mcp@latest

# 2. Install marketplace skills (interactive - select all)
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
| `ralph-wiggum` | AI coding patterns (disabled by default) |

### Commands (from this repo)

| Command | Purpose |
|---------|---------|
| `/cleanup` | Identify and remove AI-generated code patterns |
| `/code-review` | Review code for quality, security, and style |
| `/commit-push-pr` | Stage, commit, push, and create PR via `gh` |
| `/fix-merge-conflict` | Resolve merge conflicts automatically |
| `/quick-commit` | Stage + commit locally, no push |
| `/scratchpad` | Track work across sessions |
| `/take-notes` | Document technical discoveries |
| `/test-and-fix` | Run tests and fix failures |

### Skills (from this repo)

| Skill | Purpose |
|-------|---------|
| `code-architect` | System design and architecture patterns |
| `code-review` | Code review checklists and standards |
| `gemini-image-generator` | Generate images via Gemini API |
| `serverless-aws` | AWS Lambda/DynamoDB/SQS patterns |
| `verify-app` | Verify application builds and runs correctly |
| `writing-style` | Personal writing voice for technical content |

### Skills (from Vercel marketplace)

| Skill | Purpose |
|-------|---------|
| `better-auth-best-practices` | TypeScript authentication framework |
| `find-skills` | Discover and install agent skills |
| `stripe-best-practices` | Stripe integration patterns |
| `supabase-postgres-best-practices` | Postgres optimization from Supabase |
| `upgrade-stripe` | Stripe API version upgrades |
| `vercel-composition-patterns` | React composition patterns |
| `vercel-react-best-practices` | React/Next.js performance rules |
| `vercel-react-native-skills` | React Native and Expo best practices |
| `web-design-guidelines` | UI audit against 100+ best practices |

### Hooks (from this repo)

| Hook | Purpose |
|------|---------|
| `block-hardcoded-secrets` | Block commits with API keys/passwords |
| `block-destructive-git` | Prevent force pushes and destructive git ops |
| `post-edit-format` | Auto-format files after edits |

### Settings

Full `settings.json` includes:

- Extended output tokens (64K) and thinking tokens (32K)
- `includeCoAuthoredBy: false` — no co-author tags in commits
- `alwaysThinkingEnabled: true` — extended thinking on every response
- `permissions.allow` — pre-approved safe commands (git status, diff, log, npm run/test, prettier, eslint, tsc, gh)
- Plugin configuration for all MCP servers

## Structure

```
ai/claude/
├── README.md
├── CLAUDE.md              # Project template (copy to repos)
├── sync.sh                # Sync config to ~/.claude/
├── settings.json          # → ~/.claude/settings.json
├── commands/              # → ~/.claude/commands/
│   ├── cleanup.md
│   ├── code-review.md
│   ├── commit-push-pr.md
│   ├── fix-merge-conflict.md
│   ├── quick-commit.md
│   ├── scratchpad.md
│   ├── take-notes.md
│   └── test-and-fix.md
├── hooks/                 # → ~/.claude/hooks/
│   ├── block-destructive-git.md
│   ├── block-hardcoded-secrets.md
│   └── post-edit-format.md
└── skills/                # → ~/.claude/skills/
    ├── code-architect/
    ├── code-review/
    ├── gemini-image-generator/
    ├── serverless-aws/
    ├── verify-app/
    └── writing-style/
```
