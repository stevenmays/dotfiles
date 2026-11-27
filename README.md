# dotfiles

Personal Claude Code configuration, packaged as the `mays` plugin. The skills also install alone into other agents through the `skills` CLI.

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

`pre-review` checks your branch against the repo's conventions (`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`), an always-on correctness checklist (inverted conditions, missing awaits, swallowed errors, untested branches), and a baseline AI-slop checklist (obvious comments, gratuitous defensive checks, `as any`, new lint and test suppressions, single-use abstractions), then offers to apply the fixes.

New codebase? `/onboard-repo` bootstraps all of this on day one: surveys the repo, writes a real CLAUDE.md with a proposed risk map, and proposes a toolchain-matched permissions allowlist — with a choice between committing the files or keeping them local-only (`.git/info/exclude` + `settings.local.json`). A headless run writes CLAUDE.md local-only and only prints the allowlist.

## Install

Install in 1 of 2 ways:

- **The plugin, inside Claude Code:** the full package, with the commands, the skills, the review agent, and the safety hooks.
- **`npx skills`, from a terminal:** the skills only, for Claude Code or for another agent such as Codex or Cursor.

In Claude Code, pick one way. Installing both loads every skill twice, once as `mays:<name>` and once as `<name>`.

### Install the plugin in Claude Code

From within Claude Code, run the following commands:

```
/plugin marketplace add stevenmays/dotfiles
/plugin install mays@dotfiles
```

When developing from a local checkout, replace `stevenmays/dotfiles` with the checkout path.

### Install the skills with npx

The [`skills` CLI](https://github.com/vercel-labs/skills) copies skill folders from this repo into an agent's skills directory. The commands, the review agent, and the hooks come only with the plugin.

To pick the skills and the agents from a prompt, run the following command:

```bash
npx skills add stevenmays/dotfiles
```

To install every skill for Claude Code, run the following command:

```bash
npx skills add stevenmays/dotfiles --skill '*' -a claude-code
```

To install one skill for another agent, name both:

```bash
npx skills add stevenmays/dotfiles --skill ste-writing -a codex
```

- Add `-g` to install for every project, not only the current one.
- The **Works in** column of the [skills table](#skills) shows which skills run outside Claude Code.
- Install `adversarial-review` together with `external-subagents`, because the review calls that skill's wrapper script.

### Optional: install the user template

The template ships with the plugin. The next command replaces all of `~/.claude/CLAUDE.md` with the template's managed block, so back up anything you keep in that file first:

```bash
sed -n '/mays:managed:start/,/mays:managed:end/p' ~/.claude/plugins/marketplaces/dotfiles/templates/CLAUDE.user.md > ~/.claude/CLAUDE.md
```

### Set the subagent models

Strong-model spawns leave `model:` unset and resolve through `CLAUDE_CODE_SUBAGENT_MODEL`. Set it to `opus` under `env` in `~/.claude/settings.json` on every machine, and run the session itself on the strongest model you have (`/model`). Unset, it falls back to the session model. Never set it to `sonnet`: that routes implementation and review to Sonnet.

Every subagent family has a default model and effort. An env var under `env` in `~/.claude/settings.json` changes a default for the whole machine:

| Family | Default model | Model env var | Default effort | Effort env var |
| --- | --- | --- | --- | --- |
| Claude | The session model | `CLAUDE_CODE_SUBAGENT_MODEL`, set to `opus` | Not set by the plugin | None |
| Codex (GPT) | `gpt-6.1-sol` | `CODEX_SUBAGENT_MODEL` | `high` | `CODEX_SUBAGENT_EFFORT` |
| Cursor (Grok) | The highest Grok version at the effort | `CURSOR_SUBAGENT_MODEL`; a pinned slug carries its own effort | `high` | `CURSOR_SUBAGENT_EFFORT` |
| Gemini | `gemini-4-neon-high` | `GEMINI_SUBAGENT_MODEL` | The slug's `-low`, `-medium`, `-high`, or `-xhigh` suffix | None |

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

To update skills that the `skills` CLI installed, run the following command:

```bash
npx skills update
```

## What's in the Claude plugin

### Commands

| Command | Purpose |
|---------|---------|
| `/babysit-pr [PR#]` | Keep your open PR merge-ready — resolve conflicts, fix CI, address review comments (delegates to `/fix-merge-conflict` and `/test-and-fix`) |
| `/diagnose-bug [description]` | Root-cause an unclear bug — red-capable repro loop first, then bisect, ranked hypotheses, fix, regression test |
| `/extreme-code-quality-review` | Extremely strict maintainability audit of the current branch |
| `/fix-merge-conflict` | Resolve merge conflicts non-interactively |
| `/onboard-repo` | Day-one bootstrap for a new codebase — CLAUDE.md and a permissions allowlist in one run |
| `/pre-review` | Review the branch's committed and uncommitted changes for correctness, AI slop, and repo-convention drift, then offer to apply fixes |
| `/review-pr <PR#>` | Review someone else's PR against its originating ticket (GitHub/Linear/Jira/Shortcut); findings are STE-written Conventional Comments, optionally posted to GitHub |
| `/security-audit` | Audit home-directory dotfiles for security issues (read-only report) |
| `/ship` | The golden path as one command: pre-review → code-review → tests → commit → push → PR |
| `/test-and-fix` | Run tests and fix failures until green (also /ship's test gate) |

### Skills

The **Works in** column shows where a skill runs when the `skills` CLI installs it. A skill marked Claude Code dispatches Claude subagents or calls its scripts through `${CLAUDE_SKILL_DIR}`, which only Claude Code sets.

| Skill | Works in | Purpose |
|-------|----------|---------|
| `adversarial-review` | Claude Code | Two-family review of a plan or a diff: one Claude subagent and one external run (GPT or Grok) on identical briefs, then triaged |
| `claims-verification` | Claude Code | Check a plan's claims about existing code against the repo before adversarial review: one blind Claude subagent answers neutral questions with `file:line` evidence |
| `model-check` | Claude Code | Check the failure paths of a design before it ships: a fresh Claude subagent writes a small model of the design in Quint or in Python, mutants prove each rule can fail, and the caller runs every check |
| `claude-subagents` | Claude Code | Dispatch plan, review, or implementation work to a fresh Claude subagent: type, model, prompt contract, escalation |
| `external-subagents` | Claude Code | Run any task on a second model family as a background subagent: Codex with GPT, else Cursor with the newest Grok, behind a wrapper that cannot hang the session |
| `deslop` | Any agent | Clean up AI slop in existing code: measure complexity, delete dead code, refactor the worst hotspots first, and prove behavior is unchanged |
| `extreme-code-quality-review` | Any agent | Rubric for the strict maintainability audit (code-judo, 1k-line rule, spaghetti) |
| `codex-image-generator` | Claude Code | Default image path: Codex CLI's built-in `image_gen` tool, run in a subagent, no API key |
| `gemini-image-generator` | Claude Code | Nano Banana images through the Antigravity CLI's `generate_image` tool, run in a subagent, no API key; use when the user names Gemini, Nano Banana, or Antigravity |
| `gemini-subagents` | Claude Code | Run any task on a Gemini model as a background subagent through the Antigravity CLI, behind a wrapper that cannot hang the session |
| `teach-me` | Any agent | Learn a technical concept to long-term mastery: an interactive HTML lesson page first, then practice and quizzes with confidence ratings in chat, drills on gaps and shaky right answers, and spaced reviews tracked in an in-chat progress card or a ledger file |
| `skill-optimizer` | Any agent | Mutation-and-scoring loop that benchmarks a skill with binary evals and keeps only measured improvements |
| `ste-writing` | Any agent | Simplified Technical English for docs, PR descriptions, and review comments — every review command drafts findings with it |
| `writing-style` | Any agent | Personal writing voice for technical content |

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

### Using model-check

`model-check` belongs in a workflow's planning stage, for plans that rely on a protection against a race or a failure, such as a lease, dedup, lock, conditional write, ordering guard, or idempotency key. A spec writer models the design, the claims check verifies the spec's mapping to the code, and the session runs every check. The writer writes the spec in Quint or in Python. Quint needs `quint` (`brew install quint`), and `quint verify` also needs Java. Python needs nothing more, and the skill uses it when `quint` is missing. To add it to an `implement-ticket` skill, install `mays` 1.40.0 or later, then paste this prompt:

```text
Wire `mays:model-check` into my implement-ticket skill, in the planning stage only.
- Run it only when the plan relies on a protection against a race or a failure, such as a lease, dedup, lock, conditional write, ordering guard, or idempotency key. Skip it for UI work, CRUD work, and pure money math such as rounding or proration.
- When a flag such as --full forces the check on a plan that relies on no protection against a race or a failure, the skill records "Model check: skipped — no failure path to model" and the run continues.
- Ask the planner for an "invariants and failure modes" list in every plan that relies on a protection against a race or a failure. The planner never writes the spec.
- Pass the skill the ticket type (bug, feature, or new-flow), the plan file path, the code paths in scope, that list, and the scratch dir.
- Run its write phase after the planner returns. Its writer creates one spec per flow in <scratch>/model/, as <flow>.qnt or <flow>.py, plus <scratch>/model/mapping.md.
- Check the mapping's current-code rows with mays:claims-verification, in the same pass as the plan's claims.
- After the claims check, run its run phase in the session. It writes <scratch>/model-check.md with the result line, the full mapping table, and the test hand-offs. Plan reviewers get the spec and that file.
- Show the result line, and any "model didn't reproduce the bug" note, with the plan at approval. Give the test hand-offs to the implementer.
- Never block a headless run: after 2 writer attempts per phase, record the failure and continue.
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
scripts/               # Plugin checks and tests
commands/              # Slash commands
agents/                # Subagents
skills/                # Auto-activated skills; `npx skills add` installs these folders
hooks/
├── hooks.json         # Hook configuration
└── scripts/           # Hook implementations
templates/
├── CLAUDE.md          # Project CLAUDE.md template (copy into a repo)
└── CLAUDE.user.md     # User CLAUDE.md template (copy to ~/.claude/CLAUDE.md)
```
