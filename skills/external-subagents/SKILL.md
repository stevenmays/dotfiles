---
name: external-subagents
description: Run a planning, research, review, or implementation task on a second model family as a background subagent that cannot hang the session — GPT through the Codex CLI, or the newest Grok through the Cursor CLI where Codex is missing. A wrapper kills stalled runs and salvages partial output. Use whenever a workflow sends work to Codex, Cursor, GPT, Grok, a second model, or a non-Claude subagent. Not for images.
---

# External subagents

Run a task on a non-Claude model as a background subagent. The engine the machine has decides the family: Codex runs GPT, and Cursor runs Grok where Codex is missing. Callers never branch on the engine.

Always invoke an engine through `scripts/external-run.sh`, never `codex exec` or `cursor-agent -p` directly. Neither CLI has a timeout of its own, and a run that reaches for web search, a browser tool, or an MCP server can block for an hour with no output. The wrapper prevents that three ways: it switches off every network-reaching tool the engine allows, it kills a run that stops emitting events, and it salvages whatever arrived before the kill.

Not for images: `mays:codex-image-generator` covers those.

## Preflight

```bash
command -v codex cursor-agent; jq --version
```

- Codex present: `codex --version` must succeed. The wrapper picks Codex first.
- Cursor only: `cursor-agent status` must say you are logged in.
- Neither engine usable: say so and stop. The caller decides any fallback.
- Missing `jq`: the wrapper cannot extract findings from a run's event stream. Install it or expect raw JSONL.

## Engines

| Engine | Chosen when | Family | Model default | Env override | Effort | `read-only` | `workspace-write` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `codex` | `codex` is on `PATH` | GPT | `gpt-6-astra` | `CODEX_SUBAGENT_MODEL` | `--effort`, else `CODEX_SUBAGENT_EFFORT`, else `medium` | `-s read-only` | `-s workspace-write` |
| `cursor` | `codex` is missing and `cursor-agent` is on `PATH` | Grok | Highest Grok version in `cursor-agent models`, at the requested effort; `-fast` excluded (same model, double price) | `CURSOR_SUBAGENT_MODEL` | `--effort`, else `medium`: selects the slug's effort suffix | `--mode ask --trust`, no `--force` | `--force` |

- `EXTERNAL_SUBAGENT_ENGINE` or `--engine codex|cursor` forces an engine. The default is `auto`.
- Cursor resolves its model at run time. At the highest Grok version it prefers `grok-` over `cursor-grok-`, then takes the `-<effort>` slug, else the base slug, else `-high`. `-fast`, `-mini`, and unnumbered slugs such as `grok-code-fast-1` never qualify.
- A slug pinned through `--model` or `CURSOR_SUBAGENT_MODEL` already carries its effort, so the wrapper records `effort n/a`.
- The cursor engine exits 2 on a model without `grok` in its slug. Cursor also serves Claude and `auto`, and either would make the second opinion same-family.

## Run it

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/external-subagents/scripts/external-run.sh" \
  --prompt <scratch>/external-<role>-prompt.md --out <scratch>/external-<role>.md \
  --effort medium --label <role> \
  [--sandbox read-only|workspace-write] [--idle 300] [--hard 1800] [--cd <repo>]
```

- Launch every run with `Bash(run_in_background: true)` and read the exit code when it returns. Never poll a run by hand, and never wait on one in the foreground.
- An external run can go out in the same message as a Claude agent, so both work concurrently.
- Give `--out` a `.md` name. The wrapper writes the raw events and stderr next to it as `.jsonl` and `.stderr`. A cursor run that resolves its model also leaves the `cursor-agent models` listing as `.models`.
- `--label` names the run in the `--out` header. It defaults to `run`.
- `--cd` sets the working directory. It defaults to the current one.
- On cursor the prompt travels as a command-line argument, so the OS argument limit caps its size (`getconf ARG_MAX`). Split a diff that large.

## Models

The wrapper always pins the model. An unset Codex model inherits `~/.codex/config.toml`, which tracks whatever the user last picked in the TUI, so an unpinned run would change strength between runs without saying so.

| `--model` | Engine | Use for |
| --- | --- | --- |
| Omitted | Both | Strong work: planning, review, a second implementation |
| `gpt-5.6-sol` | `codex` only | Work a deterministic check verifies: a test, lint, compile, or known-target grep |

- Omit `--model` for strong work, so the engine default applies.
- Cursor has no check tier. Omit `--model` there: `gpt-5.6-sol` fails the Grok guard and exits 2.
- `--effort` works on both engines and defaults to `medium`. On cursor it selects the Grok slug's effort suffix.

## Roles

| Role | `--sandbox` | Budget | What comes back |
| --- | --- | --- | --- |
| Plan / research | `read-only` | `--idle 300 --hard 900` | The final message is the deliverable |
| Review | `read-only` | `--idle 300 --hard 1800` | Findings in the brief's output format |
| Implementation | `workspace-write` | `--idle 300 --hard 3600` | Edits in the working tree |

- `read-only` is the default. On codex it still lets the run execute `git` and read files itself.
- `codex exec` is non-interactive and auto-approves whatever the sandbox permits. `cursor-agent -p` is non-interactive too: without `--force` it proposes edits and applies none. Nothing blocks on a prompt.
- Plan and research: the salvage can put the run's running commentary above the deliverable. Strip everything before the first heading.
- Implementation runs on a feature branch only, never the base branch. It gets the longest budget because it makes many more tool calls than a review.
- The wrapper never stages, commits, or reverts. After an implementation run, `--out` is the run's own account of what it did, not evidence. Read `git diff` and `git status --porcelain --untracked-files=all` yourself.

## Cursor caveats

- Cursor's sandbox allows reads and writes inside the workspace and blocks network by default, so `--force --sandbox enabled` is right for implementation.
- Headless Ask mode runs read-only terminal commands such as `git diff` and refuses file writes (verified live). Without `--trust`, a new workspace stops the run at a trust prompt, so the wrapper always passes it.
- Cursor's Free plan allows only `auto`, so every named model, Grok included, fails with exit 126 and "Named models unavailable" in `.stderr`. Grok needs a paid Cursor plan. Treat that failure as no usable engine.
- Web search has no per-run switch. The idle watchdog and the prompt's no-network clause are the only guards.

## Exit codes

| Exit | Meaning | What to do |
| --- | --- | --- |
| 0 | Completed | Use the output normally |
| 125 | Stalled — no events for `--idle` seconds | Retry once with a narrower scope; still stalling means use the partial output and say so |
| 124 | Hard timeout at `--hard` seconds | Same as 125 — the input is probably too large for one pass; split it |
| 126 | The engine failed: a nonzero exit, or a cursor `result` event with `is_error` | Read the `.stderr` file next to the output; do not retry blindly |
| 2 | Bad usage, no external engine, or no usable Grok model on cursor | Fix the call. On cursor, run `cursor-agent login` or set `CURSOR_SUBAGENT_MODEL` to a Grok slug |

- The `--out` file always exists. Its second line names the engine, model, and effort, such as `Engine: cursor · Model: grok-4.7-medium · effort medium`. Codex's event stream carries no model, so this line is the only record of what produced a run. On cursor the line also names the model Cursor reported when that differs from the requested slug.
- A stalled or timed-out run's output says `PARTIAL` in its first line and names the last tool call before the kill. Findings salvaged from a stalled run are still findings — use them, and mark them partial.
- Defaults are 300s idle and 1800s hard. Raise `--hard` for a large diff; do not raise `--idle` above 600 — silence that long is a hang, not thinking.

## Prompt contract

Write the prompt to a file in a scratch directory outside the repo — the session scratchpad if the harness gave you one, else `mktemp -d`. Nothing generated gets committed.

The external model cannot see the conversation, and it never loads the user-level `CLAUDE.md`. Codex reads only `AGENTS.md`; Cursor reads the project-root `AGENTS.md`, `CLAUDE.md`, and `.cursor/rules`. So carry the rules that apply in the prompt, and on codex name the project `CLAUDE.md` path for the run to read.

Every prompt carries the same items as the prompt list in `mays:claude-subagents`, including the decisions already made and the judgment calls the run owns, plus:

- The role's rule. Read-only roles: "do not edit, create, or delete files." Implementation: the implementer contract in `mays:claude-subagents`.
- The no-network clause, verbatim: "Work only from this prompt and the repository in front of you: no web search, no fetching URLs, no external tools."
