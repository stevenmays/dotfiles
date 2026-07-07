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
| `/distill-standards [N \| #PR \| full]` | Mine merged PRs into `.claude/standards.md` — full regen from N PRs, delta since last run (no args), or absorb a single PR's feedback |
| `/extreme-code-quality-review` | Extremely strict maintainability audit of the current branch, standards-aware |
| `/fix-merge-conflict` | Resolve merge conflicts non-interactively |
| `/onboard-repo [N]` | Day-one bootstrap for a new codebase — CLAUDE.md, distilled standards, and a permissions allowlist in one run |
| `/pre-review` | Check the branch diff against distilled standards (with staleness warning), then offer to apply fixes |
| `/review-pr <PR#>` | Review someone else's PR against distilled standards; optionally post findings to GitHub |
| `/security-audit` | Audit home-directory dotfiles for security issues (read-only report) |
| `/ship` | The golden path as one command: pre-review → code-review → tests → commit → push → PR |
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
| `load-standards` | SessionStart | Inject `.claude/standards.md` into context so code is written compliant on the first pass, not repaired at review |

## Standards Workflow

One system: distill the repo's review history once, write code against it, pre-review before posting, and feed every new round of human feedback back into the standards.

```
/distill-standards             # once per repo (full regen; asks how many PRs, default 50)
── write code ──
/pre-review                    # standards + baseline checks before every PR
/extreme-code-quality-review   # deep structural audit — for large or structural changes
── open PR; after human review lands ──
/distill-standards #<PR>       # absorb that PR's feedback immediately
/distill-standards             # or: cheap delta over everything merged since the last run
── reviewing someone else's PR ──
/review-pr <PR# or URL>        # standards-aware review, optionally posted to GitHub
```

`distill-standards` reads PR review history via `gh` and writes distilled rules (never raw comments) to `.claude/standards.md`. Recurring feedback becomes conventions; substantive one-off feedback — edge cases, domain gotchas — lands in a `## One-offs` section and gets promoted to a convention if it recurs. Bare runs do a delta over only the PRs merged since the last run, so standards stay current without re-mining history.

`pre-review` checks your branch against every rule (one-offs included) plus a baseline AI-slop checklist (obvious comments, gratuitous defensive checks, `as any`, single-use abstractions), then offers to apply the fixes. The goal: by the time a human sees the PR, their past feedback has already been addressed.

Every review surface consults `.claude/standards.md` when it exists: `/pre-review`, `/review-pr`, and `/extreme-code-quality-review` load it directly, and `sync.sh` maintains a managed block in `~/.claude/CLAUDE.md` so the native `/code-review` picks it up in any repo. Standards also apply at **write time**: the `load-standards` SessionStart hook injects the file into context when a session opens in the repo, so code conforms on the first pass instead of being repaired at pre-review.

New codebase? `/onboard-repo` bootstraps all of this on day one: surveys the repo, writes a real CLAUDE.md, runs the full distill, and proposes a toolchain-matched permissions allowlist — with a choice between committing the files or keeping them local-only (`.git/info/exclude` + `settings.local.json`).

## The Golden Path (before every PR)

```
/ship                          # pre-review → code-review high → tests → commit → push → PR
```

`/ship` runs the whole path with one confirmation checkpoint before anything leaves the machine, opening the PR with the summary + test-plan format from the `~/.claude/CLAUDE.md` managed block. After human review lands, `/distill-standards #<PR>`.

To run the gates individually:

```
/pre-review                    # standards conformance — catches what reviewers flagged before
/code-review high              # native correctness review — bugs, not style
/extreme-code-quality-review   # structural audit — only for large or structural changes
```

## Settings

`settings.json` (synced to `~/.claude/settings.json` by `sync.sh`; the script also maintains a managed block in `~/.claude/CLAUDE.md` with the standards lookup and git conventions):

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
- `/quick-commit`, `/commit-push-pr` → plain commit/PR requests + git conventions in the `~/.claude/CLAUDE.md` managed block (via `sync.sh`)
