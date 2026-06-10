# dotfiles

Personal Claude Code configuration, packaged as an installable plugin (`mays-tools`).

## Install

From within Claude Code:

```
/plugin marketplace add stevenmays/dotfiles
/plugin install mays-tools@dotfiles
```

Then sync personal settings (optional, overwrites `~/.claude/settings.json`):

```bash
./sync.sh
```

## What's in the Plugin

### Commands

| Command | Purpose |
|---------|---------|
| `/commit-push-pr` | Stage, commit, push, and create PR via `gh` |
| `/distill-standards [N]` | Mine the last N merged PRs for review patterns, distill into `.claude/standards.md` |
| `/extreme-code-quality-review` | Extremely strict maintainability audit of the current branch |
| `/fix-merge-conflict` | Resolve merge conflicts non-interactively |
| `/pre-review` | Check the branch diff against distilled standards before opening a PR |
| `/quick-commit` | Stage + commit locally, no push |
| `/test-and-fix` | Run tests and fix failures until green |

### Skills

| Skill | Purpose |
|-------|---------|
| `extreme-code-quality-review` | Rubric for the strict maintainability audit (code-judo, 1k-line rule, spaghetti) |
| `gemini-image-generator` | Generate images via Gemini API |
| `serverless-aws` | AWS Lambda/DynamoDB/SQS patterns |
| `writing-style` | Personal writing voice for technical content |

### Agents

| Agent | Purpose |
|-------|---------|
| `extreme-code-quality-review` | Runs the strict audit in a subagent to protect the main context |

### Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `block-destructive-git` | PreToolUse (Bash) | Block force pushes, hard resets, and other destructive git ops |
| `block-hardcoded-secrets` | PreToolUse (Edit/Write) | Block edits that introduce hardcoded API keys/passwords |
| `post-edit-format` | PostToolUse (Edit/Write) | Auto-format edited files with Prettier when the project uses it |

## Standards Workflow

```
/distill-standards 30   # once per repo (re-run as PRs accumulate)
/pre-review             # before every PR
```

`distill-standards` reads the repo's merged PR history via `gh`, extracts recurring review feedback and conventions (distilled rules, not raw comments), and writes `.claude/standards.md`. `pre-review` checks your branch against those rules plus a baseline AI-slop checklist (obvious comments, gratuitous defensive checks, `as any`, single-use abstractions).

## Settings

`settings.json` (synced to `~/.claude/settings.json` by `sync.sh`):

- Extended output tokens (64K) and thinking tokens (32K)
- `includeCoAuthoredBy: false` — no co-author tags in commits
- `alwaysThinkingEnabled: true`
- `permissions.allow` — pre-approved safe commands (git status/diff/log, npm run/test, prettier, eslint, tsc, gh)
- `enabledPlugins` — marketplace plugins, including this one

## Structure

```
.claude-plugin/
├── plugin.json        # Plugin manifest
└── marketplace.json   # Lets this repo act as a marketplace
commands/              # Slash commands
agents/                # Subagents
skills/                # Auto-activated skills
hooks/
├── hooks.json         # Hook configuration
└── scripts/           # Hook implementations
templates/CLAUDE.md    # Project CLAUDE.md template (copy into repos)
settings.json          # Personal settings (synced by sync.sh, not part of the plugin)
sync.sh                # Sync settings + clean up old copy-based installs
```

## Removed in the Plugin Migration

These used to live here but are now handled natively by Claude Code:

- `/remember`, `/take-notes` → native persistent memory
- `/scratchpad` → native context management and session resume
- `/cleanup`, `code-review` skill → native `/simplify` and `/code-review --fix`
- `/code-review` command → native `/code-review` and `/review`
- `verify-app` skill → native `/verify`
- `code-architect` skill → native plan mode
- qmd integration (`/repo-init`, `deep-memory.md`, MCP server) → native memory
