# dotfiles

Personal Claude Code and Codex configuration, packaged as separate versions of the `mays` plugin in one repository. Claude uses the root package; Codex uses [`codex/`](codex/README.md).

## The Claude system

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

For Codex:

```bash
codex plugin marketplace add stevenmays/dotfiles
codex plugin add mays@dotfiles
```

When developing from a local checkout, replace `stevenmays/dotfiles` with the checkout path.
Codex installs the self-contained `codex/` package with nine adapted skills. It excludes
`ste-writing`; frontend work uses Codex's built-in image capability
when available. Claude commands, agents, and hooks stay outside that package. See the
[Codex package guide](codex/README.md) for its skills, validation, and optional personal template.

Optional: install the user template. The next command replaces all of `~/.claude/CLAUDE.md` with the template's managed block, so back up anything you keep in that file first:

```bash
sed -n '/mays:managed:start/,/mays:managed:end/p' ~/.claude/plugins/marketplaces/dotfiles/templates/CLAUDE.user.md > ~/.claude/CLAUDE.md
```

Strong-model spawns leave `model:` unset and resolve through `CLAUDE_CODE_SUBAGENT_MODEL`. Set it to `opus` under `env` in `~/.claude/settings.json` on every machine, and run the session itself on the strongest model you have (`/model`). Unset, it falls back to the session model. Never set it to `sonnet`: that routes implementation and review to Sonnet.

Every subagent family has a default model and effort. An env var under `env` in `~/.claude/settings.json` changes a default for the whole machine:

| Family | Default model | Model env var | Default effort | Effort env var |
| --- | --- | --- | --- | --- |
| Claude | The session model | `CLAUDE_CODE_SUBAGENT_MODEL`, set to `opus` | Not set by the plugin | None |
| Codex (GPT) | `gpt-6.1-sol` | `CODEX_SUBAGENT_MODEL` | `high` | `CODEX_SUBAGENT_EFFORT` |
| Cursor (Grok) | The highest Grok version at the effort | `CURSOR_SUBAGENT_MODEL`; a pinned slug carries its own effort | `high` | `CURSOR_SUBAGENT_EFFORT` |
| Gemini | `gemini-3.8-flash-high` | `GEMINI_SUBAGENT_MODEL` | The slug's `-low`, `-medium`, or `-high` suffix | None |

For one call, `--model` and `--effort` on the wrapper scripts beat the env vars. A pinned Cursor slug carries its own effort and ignores both. The Gemini wrapper takes only `--model`. A Claude spawn overrides its model with `model:` on the Agent tool.

```json
{
  "env": {
    "CLAUDE_CODE_SUBAGENT_MODEL": "opus",
    "CODEX_SUBAGENT_EFFORT": "xhigh"
  }
}
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

For a local Codex checkout, update the version cachebuster in `codex/.codex-plugin/plugin.json`
with the plugin-creator helper, then reinstall:

```bash
codex plugin add mays@dotfiles
```

Start a new Codex thread after reinstalling to load the updated catalog.

## What's in the Claude plugin

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
| `adversarial-review` | Two-family review of a plan or a diff: one Claude subagent and one external run (GPT or Grok) on identical briefs, then triaged |
| `claims-verification` | Check a plan's claims about existing code against the repo before adversarial review: one blind Claude subagent answers neutral questions with `file:line` evidence |
| `claude-subagents` | Dispatch plan, review, or implementation work to a fresh Claude subagent: type, model, prompt contract, escalation |
| `external-subagents` | Run any task on a second model family as a background subagent: Codex with GPT, else Cursor with the newest Grok, behind a wrapper that cannot hang the session |
| `extreme-code-quality-review` | Rubric for the strict maintainability audit (code-judo, 1k-line rule, spaghetti) |
| `frontend-craft` | Companion to Anthropic's `frontend-design`: seed-string variety, screenshot-only design-critic loop, generated images and video, and a subtraction pass that removes AI tells |
| `html-artifact` | Self-contained local HTML pages from 11 interactive templates (plans, PR reviews, triage boards, incidents, and more); the agent edits only the embedded JSON. Templates adapted from [plan-it](https://github.com/OthmanAdi/plan-it) at `93f6606` under MIT |
| `codex-image-generator` | Default image path: Codex CLI's built-in `image_gen` tool, run in a subagent, no API key |
| `gemini-image-generator` | Nano Banana images through the Antigravity CLI's `generate_image` tool, run in a subagent, no API key; use when the user names Gemini, Nano Banana, or Antigravity |
| `gemini-subagents` | Run any task on a Gemini model as a background subagent through the Antigravity CLI, behind a wrapper that cannot hang the session |
| `serverless-aws` | AWS Lambda/DynamoDB/SQS patterns |
| `skill-optimizer` | Mutation-and-scoring loop that benchmarks a skill with binary evals and keeps only measured improvements |
| `ste-writing` | Simplified Technical English for docs, PR descriptions, and review comments — every review command drafts findings with it |
| `writing-style` | Personal writing voice for technical content |

### Using claims-verification

`claims-verification` belongs in a workflow's planning stage. It runs after a plan is drafted and before any adversarial or human review. Adversarial review attacks reasoning but misses confident false facts, so the facts get checked first. To add it to an `implement-ticket` skill, install `mays` 1.23.0 or later, then paste this prompt:

```text
Wire `mays:claims-verification` into my implement-ticket skill, in the planning stage only.
- Add a "Claims check" step after the planner returns the plan and before any review of it. It loads the skill, runs it on the saved plan file against the working tree the planner read, and saves the result next to the plan.
- Replace any informal rule that sends back plans naming missing files or wrong signatures.
- It always runs, at every plan size and under --fast, because it isn't adversarial.
- Show its result line with the plan at approval, and log it wherever plan-review verdicts go.
- Don't renumber steps or gates, and don't restate the skill's rules. Point to the skill instead.
```

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
.agents/plugins/
└── marketplace.json   # Codex marketplace; source is ./codex
codex/
├── .codex-plugin/     # Independent Codex manifest and version
├── skills/            # Nine adapted skills; no STE skill
├── templates/         # Optional personal AGENTS.md preferences
├── evals/             # Behavioral cases and validation results
└── shared-resources.json # Explicit copies from canonical source files
scripts/               # Package validation and shared-resource synchronization
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
