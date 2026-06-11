# dotfiles

Personal Claude Code configuration, packaged as an installable plugin (`mays`).

## Install

From within Claude Code:

```
/plugin marketplace add stevenmays/dotfiles
/plugin install mays@dotfiles
```

Then sync personal settings (optional, overwrites `~/.claude/settings.json`):

```bash
./sync.sh
```

## Update

After new commits land in this repo, refresh the marketplace catalog — Claude Code re-pulls the source and upgrades the installed `mays` plugin in the same step:

```
/plugin marketplace update dotfiles
```

Then run `/reload-plugins` when prompted (or restart Claude Code) to load the new version. To make this automatic, enable auto-update for the marketplace under `/plugin` → Marketplaces → dotfiles.

Non-interactive equivalent:

```bash
claude plugin marketplace update dotfiles
```

## What's in the Plugin

### Commands

| Command | Purpose |
|---------|---------|
| `/commit-push-pr` | Stage, commit, push, and create PR via `gh` |
| `/distill-standards [N]` | Mine the last N merged PRs (asks how many, default 50) for review patterns, distill into `.claude/standards.md` |
| `/extreme-code-quality-review` | Extremely strict maintainability audit of the current branch, standards-aware |
| `/fix-merge-conflict` | Resolve merge conflicts non-interactively |
| `/pre-review` | Check the branch diff against distilled standards before opening a PR, then offer to apply fixes |
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
/distill-standards      # once per repo (asks how many PRs, default 50; re-run as PRs accumulate)
/pre-review             # before every PR
```

`distill-standards` reads the repo's merged PR history via `gh`, extracts recurring review feedback and conventions (distilled rules, not raw comments), and writes `.claude/standards.md`. `pre-review` checks your branch against those rules plus a baseline AI-slop checklist (obvious comments, gratuitous defensive checks, `as any`, single-use abstractions), then offers to apply the fixes.

Every review surface consults `.claude/standards.md` when it exists: `/pre-review` and `/extreme-code-quality-review` load it directly, and `sync.sh` adds a note to `~/.claude/CLAUDE.md` so the native `/code-review` picks it up in any repo.

## Settings

`settings.json` (synced to `~/.claude/settings.json` by `sync.sh`; the script also appends the standards note to `~/.claude/CLAUDE.md` once):

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
