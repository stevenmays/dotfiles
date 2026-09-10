# dotfiles

Personal Claude Code configuration, packaged as an installable plugin (`mays`). One system: onboard a repo, gate every PR through layered review, and keep it merge-ready.

## The System

```
/onboard-repo                  # day one in a new codebase: CLAUDE.md + permissions
/ship                          # pre-review → code-review high → tests → commit → push → PR
/babysit-pr                    # keep the open PR merge-ready: conflicts, CI, review comments
── reviewing someone else's PR ──
/review-pr <PR# or URL>        # review as Conventional Comments, optionally posted
```

`/ship` runs the whole pre-PR path with one confirmation checkpoint before anything leaves the machine, opening the PR with the summary + test-plan format from the `~/.claude/CLAUDE.md` managed block. To run its gates individually:

```
/pre-review                    # repo conventions, correctness, and AI-slop checks
/code-review high              # native correctness review — bugs, not style
/extreme-code-quality-review   # structural audit — only for large or structural changes
```

`pre-review` checks your branch against the repo's CLAUDE.md conventions, an always-on correctness checklist (inverted conditions, missing awaits, swallowed errors, untested branches), and a baseline AI-slop checklist (obvious comments, gratuitous defensive checks, `as any`, single-use abstractions), then offers to apply the fixes.

New codebase? `/onboard-repo` bootstraps all of this on day one: surveys the repo, writes a real CLAUDE.md, and proposes a toolchain-matched permissions allowlist — with a choice between committing the files or keeping them local-only (`.git/info/exclude` + `settings.local.json`).

## Install

From within Claude Code:

```
/plugin marketplace add stevenmays/dotfiles
/plugin install mays@dotfiles
```

Optional: install the user template. The next command replaces all of `~/.claude/CLAUDE.md` with the template's managed block, so back up anything you keep in that file first:

```bash
sed -n '/mays:managed:start/,/mays:managed:end/p' ~/.claude/plugins/marketplaces/dotfiles/templates/CLAUDE.user.md > ~/.claude/CLAUDE.md
```

Strong-model spawns leave `model:` unset and resolve through `CLAUDE_CODE_SUBAGENT_MODEL`. On a machine with Fable access, set it to `fable` under `env` in `~/.claude/settings.json`. Elsewhere set it to `opus`. Unset, it falls back to the session model. Never set it to `sonnet`: that routes implementation and review to Sonnet.

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
| `/babysit-pr [PR#]` | Keep your open PR merge-ready — resolve conflicts, fix CI, address review comments (delegates to `/fix-merge-conflict` and `/test-and-fix`) |
| `/diagnose-bug [description]` | Root-cause an unclear bug — red-capable repro loop first, then bisect, ranked hypotheses, fix, regression test |
| `/extreme-code-quality-review` | Extremely strict maintainability audit of the current branch |
| `/fix-merge-conflict` | Resolve merge conflicts non-interactively |
| `/onboard-repo` | Day-one bootstrap for a new codebase — CLAUDE.md and a permissions allowlist in one run |
| `/pre-review` | Review the branch diff for correctness, AI slop, and repo-convention drift, then offer to apply fixes |
| `/review-pr <PR#>` | Review someone else's PR against its originating ticket (GitHub/Linear/Jira/Shortcut); findings are STE-written Conventional Comments, optionally posted to GitHub |
| `/security-audit` | Audit home-directory dotfiles for security issues (read-only report) |
| `/ship` | The golden path as one command: pre-review → code-review → tests → commit → push → PR |
| `/test-and-fix` | Run tests and fix failures until green (also /ship's test gate) |

### Skills

| Skill | Purpose |
|-------|---------|
| `extreme-code-quality-review` | Rubric for the strict maintainability audit (code-judo, 1k-line rule, spaghetti) |
| `frontend-craft` | Companion to Anthropic's `frontend-design`: seed-string variety, screenshot-only design-critic loop, generated images and video, and a subtraction pass that removes AI tells |
| `gemini-image-generator` | Generate images via Gemini API |
| `serverless-aws` | AWS Lambda/DynamoDB/SQS patterns |
| `skill-optimizer` | Mutation-and-scoring loop that benchmarks a skill with binary evals and keeps only measured improvements |
| `ste-writing` | Simplified Technical English for docs, PR descriptions, and review comments — every review command drafts findings with it |
| `writing-style` | Personal writing voice for technical content |

### Agents

| Agent | Purpose |
|-------|---------|
| `extreme-code-quality-review` | Runs the strict audit in a subagent to protect the main context |

### Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `block-destructive-git` | PreToolUse (Bash) | Block force pushes (including `+refspec`), hard resets, forced cleans and branch deletes |
| `block-hardcoded-secrets` | PreToolUse (Edit/Write) | Block edits that introduce hardcoded API keys/passwords |
| `post-edit-format` | PostToolUse (Edit/Write) | Auto-format edited files with Prettier when the project uses it |

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
templates/
├── CLAUDE.md          # Project CLAUDE.md template (copy into a repo)
└── CLAUDE.user.md     # User CLAUDE.md template (copy to ~/.claude/CLAUDE.md)
```
