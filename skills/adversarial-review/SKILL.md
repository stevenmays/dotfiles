---
name: adversarial-review
description: Two-family adversarial review of a plan or a diff — one fresh Claude subagent and one external run (GPT through Codex, or Grok through Cursor) on identical briefs, launched concurrently, then triaged into verified blockers, concerns, and rejected findings. Use before approving a plan, before shipping a change, or whenever a workflow asks for an adversarial review.
---

# Adversarial review

Adversarial review comes in pairs — one fresh Claude subagent and one external run, on identical briefs, launched concurrently. Different model families fail differently, so agreement between them is signal. Each pair costs roughly 3–8 minutes of wall clock.

Reviewers read; the caller applies every fix, so one actor owns the diff.

## Modes

| Mode | Reviewers see | Brief |
| --- | --- | --- |
| `plan` | The plan text and the ticket | `references/plan-review.md` |
| `code` | `git diff <base>...HEAD` plus untracked files from `git status --porcelain --untracked-files=all`; the ticket and approved plan when there are any | `references/code-review.md` |

In code mode, `<base>` is the repo default branch (`main`, else `master`) unless the caller names another.

Fill the brief's placeholders. Inline the ticket and plan text; never send a path the reviewer cannot read. Keep the two prompts identical apart from tool guidance, so disagreement comes from the models, not the prompts.

## Launch

Launch both reviewers in one message so they run concurrently:

- **Claude**: the reviewer role in `mays:claude-subagents`, `model:` unset.
- **External**: the review role in `mays:external-subagents`, `--effort medium`, launched with `Bash(run_in_background: true)`. The wrapper picks the engine and pins that engine's default model.

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/external-subagents/scripts/external-run.sh" \
  --prompt <scratch>/external-<mode>-review-prompt.md --out <scratch>/external-<mode>-review.md \
  --effort medium --label review --idle 300 --hard 1800
```

Plan mode may drop the external run to `--effort low` when the plan touches 3 files or fewer. Code mode never goes below `medium`. On cursor, effort selects the Grok slug's effort suffix.

## Family rules

- **Two families, not two of the same.** Never substitute a second Claude subagent for the external run or the reverse — the point is uncorrelated failure modes.
- When the author of the plan or code shares a family with a reviewer, that reviewer is grading its own homework. Its findings count in full, but its agreement is not a second opinion.
- Label every verdict with its family: `Claude`, or the external run's family with its engine, `GPT (codex)` or `Grok (cursor)`. No finding is weighted, discounted, or promoted by its source. A finding is true or false against the code, and that is the only test it gets.
- Cross-family agreement is corroboration; same-family agreement is not. Either way, verify before you act — a lone finding can still be correct.

## Triage

- Triage every finding into confirmed blocker, non-blocking, or rejected with a one-line reason. A rejected finding with no reason is an unexamined one.
- **Verify each blocker against the code yourself before acting** — both families hallucinate line numbers and control flow.
- The caller fixes confirmed blockers, then re-runs both reviewers scoped to the changed areas.

## Degraded mode

- The caller names one family because the user chose it: run that family alone and put `single-family review` in the result's first line.
- The external run stalled after its one retry: its partial findings still count. Mark them partial.
- No external engine (neither `codex` nor a logged-in `cursor-agent`), a stall that salvaged nothing, or an external engine that fails before producing any output (exit 126, such as a Cursor Free plan): running Claude alone is a downgrade the user chooses. Ask whether to continue with Claude alone or stop.
- When nobody can answer (a headless run), continue with Claude alone and put `single-family review` in the result's first line.
- Never downgrade silently.

## Result

```
Claude: VERDICT <verdict> — <summary>
GPT (codex) | Grok (cursor): VERDICT <verdict> — <summary>   (mark "partial" when salvaged)

BLOCKERS (verified)
- [file:line] <what breaks> → <fix> (<family>, or both)

CONCERNS
- [file:line] <finding> → <fix> (<family>)

REJECTED
- <finding> (<family>) — <one-line reason>

TEST GAPS (code mode) | SIMPLER PATH (plan mode)
- <gap or alternative, or "none">
```
