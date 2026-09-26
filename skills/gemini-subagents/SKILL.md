---
name: gemini-subagents
description: Run a planning, research, review, or implementation task on a Gemini model as a background subagent through the Antigravity CLI (`agy`), behind a wrapper that kills stalled runs and salvages partial output. Use when a workflow names Gemini, Antigravity, or `agy` as the second model. Not for images.
---

# Gemini subagents

Run a task on a Gemini model as a background subagent through the Antigravity CLI, `agy`. This skill mirrors `mays:external-subagents`: the same flags, exit codes, and `--out` file, without `--engine` and `--effort`.

Always invoke `agy` through `scripts/gemini-run.sh`, never `agy -p` directly. `agy` has no per-run switch for its network-reaching tools: `search_web`, `read_url_content`, `call_mcp_tool`, `open_browser_url`, and `browser_*`. A run that reaches for one can hang. The wrapper passes `--print-timeout` at the hard budget, and its idle watchdog kills a run that stops emitting events. Then it salvages whatever arrived before the kill.

Not for images: `mays:gemini-image-generator` covers those.

## Preflight

```bash
command -v agy; jq --version; agy models
```

- `agy models` must list the Gemini slugs in the Models table. Whether a listing also proves the login is unverified.
- To log in, open the Antigravity app or run `agy` once interactively (unverified).
- Missing `agy` or no Gemini slug in the listing: say so and stop. The caller decides any fallback.
- Missing `jq`: the wrapper cannot extract findings from the event stream. Install it or expect raw JSONL.

## Run it

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/gemini-subagents/scripts/gemini-run.sh" \
  --prompt <scratch>/gemini-<role>-prompt.md --out <scratch>/gemini-<role>.md \
  --label <role> \
  [--model SLUG] [--sandbox read-only|workspace-write] [--idle 300] [--hard 1800] [--cd <repo>]
```

- Launch every run with `Bash(run_in_background: true)` and read the exit code when it returns. Never poll a run by hand, and never wait on one in the foreground.
- A Gemini run can go out in the same message as a Claude agent, so both work concurrently.
- Give `--out` a `.md` name. The wrapper writes the raw events and stderr next to it as `.jsonl` and `.stderr`.
- `--label` names the run in the `--out` header. It defaults to `run`.
- `--cd` sets the working directory. It defaults to the current one. `agy` has no such flag, so the wrapper starts `agy` inside that directory.
- Keep every file the run needs under `--cd`. The wrapper passes no `--add-dir`, and reads outside the working directory are unverified.
- The prompt travels as a command-line argument, so the OS argument limit caps its size (`getconf ARG_MAX`). Split a diff that large.

## Models

The wrapper always pins the model. An unpinned run would take `agy`'s own default, which can drift between runs without notice, the same risk as an unpinned Codex run.

| `--model` | Use for |
| --- | --- |
| Omitted: `gemini-3.1-pro-high` | Strong work: planning, review, a second implementation |
| `gemini-3.8-flash-high` or `gemini-3.8-flash-medium` | Work a deterministic check verifies: a test, lint, compile, or known-target grep |
| `gemini-3.8-flash-low` | Trivial work |

- `--model` beats `GEMINI_SUBAGENT_MODEL`, which beats the default.
- The slug carries the effort. The wrapper reads the `-low`, `-medium`, or `-high` suffix for the provenance line, else records `model default`.
- `gemini-3.1-pro` comes in `-high` and `-low` only. `agy models` also lists older `gemini-3.7-flash-*` and `gemini-3.6-flash-*` slugs.
- `agy` has its own `--effort` flag. The wrapper never passes it, because its interaction with the slug suffix is unverified.
- The wrapper exits 2 on a slug without `gemini`. `agy` also serves 3 other slugs: `claude-sonnet-4-6`, `claude-opus-4-6-thinking`, and `gpt-oss-120b-medium`.
- A Claude slug would make the second opinion same-family, and this skill exists to run Gemini.

## Roles

| Role | `--sandbox` | Budget | What comes back |
| --- | --- | --- | --- |
| Plan / research | `read-only` | `--idle 300 --hard 900` | The final message is the deliverable |
| Review | `read-only` | `--idle 300 --hard 1800` | Findings in the brief's output format |
| Implementation | `workspace-write` | `--idle 300 --hard 3600` | Edits in the working tree |

- `read-only` is the default. The run can view and search files, but it cannot write a file or run a command, `git` included.
- `workspace-write` can write files but still cannot run a command. An implementation run cannot run its tests, a build, or `git`. The caller runs the tests and reads `git diff` afterwards.
- Plan and research: an empty `response` makes the wrapper fall back to the streamed text. That text can put the run's commentary above the deliverable. Strip everything before the first heading.
- Implementation runs on a feature branch only, never the base branch. It gets the longest budget because it makes many more tool calls than a review.
- The wrapper never stages, commits, or reverts. After an implementation run, `--out` is the run's own account of what it did, not evidence. Read `git diff` and `git status --porcelain --untracked-files=all` yourself, then run the tests.

## Headless permissions

Headless `agy` cannot ask for permission, so it auto-denies any tool that needs one. A live run verified this matrix, apart from the cell marked unverified:

| Tool | `read-only` (no `--mode`) | `workspace-write` (`--mode accept-edits`) |
| --- | --- | --- |
| `view_file` and file search (grep, list, find) | Allowed | Allowed (unverified) |
| `write_to_file` | Denied | Allowed |
| `run_command` | Denied | Denied |
| `search_web`, `read_url_content`, `call_mcp_tool`, `open_browser_url`, `browser_*` | No per-run switch | No per-run switch |

- `--mode plan` denies the same tools as no `--mode`. The wrapper never passes it.
- The wrapper never passes `--dangerously-skip-permissions`, which would lift every denial. The user's policy forbids it.
- A denied tool does not fail the run. `agy` still exits 0 with `status` `SUCCESS` and lists the tool in `denied_actions`. The `response` can come back empty.
- The wrapper prints that list on the line after the provenance line, such as `Denied in headless mode: command`. `agy` also writes a line that starts `jetski: no output produced` to `.stderr`.

## Exit codes

| Exit | Meaning | What to do |
| --- | --- | --- |
| 0 | Completed | Use the output normally. Check for a `Denied in headless mode` line |
| 125 | Stalled: no events for `--idle` seconds | Retry once with a narrower scope. Still stalling means use the partial output and say so |
| 124 | Hard timeout at `--hard` seconds | Same as 125. The input is probably too large for one pass, so split it |
| 126 | `agy` failed: a nonzero exit, or a `result` event whose `status` is not `SUCCESS` | Read the `.stderr` file next to the output. Do not retry blindly |
| 2 | Bad usage, `agy` not on `PATH`, or a non-Gemini model | Fix the call |

- The `--out` file always exists. Its second line names the engine, model, and effort, such as `Engine: gemini · Model: gemini-3.1-pro-high · effort high`.
- When the `init` event reports a different model, the second line names that model too.
- A stalled or timed-out run says `PARTIAL` in its first line and names the last tool call before the kill. Findings salvaged from a stalled run are still findings: use them, and mark them partial.
- `--print-timeout` makes `agy` stop itself at `--hard` too. The wrapper reports that stop as exit 124.
- Defaults are 300s idle and 1800s hard. Raise `--hard` for a large diff. Do not raise `--idle` above 600: silence that long is a hang, not thinking.

## Prompt contract

Write the prompt to a file in a scratch directory outside the repo: the session scratchpad if the harness gave you one, else `mktemp -d`. Nothing generated gets committed.

The Gemini model cannot see the conversation. Do not count on it loading any `CLAUDE.md`. By Antigravity convention, `agy` reads `~/.gemini/GEMINI.md` and any `AGENTS.md` or `GEMINI.md` in the workspace. That loading is unverified, so verify which files it reads before relying on it. Carry the rules that apply in the prompt, and name the project `CLAUDE.md` path for the run to read.

Every prompt carries the same items as the prompt list in `mays:claude-subagents`. That includes the decisions already made and the judgment calls the run owns. Add these:

- The role's rule. Read-only roles: "do not edit, create, or delete files." Implementation: the implementer contract in `mays:claude-subagents`, except that the run cannot run its tests. It writes the change and its tests, then stops, and the caller runs them.
- The tool limit: "You cannot run shell commands. Read and search with your file tools." A run that reaches for a denied `run_command` can end with an empty response.
- The no-network clause, verbatim: "Work only from this prompt and the repository in front of you: no web search, no fetching URLs, no external tools."
