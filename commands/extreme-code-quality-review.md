---
description: Extremely strict maintainability audit of the current branch (code-judo, 1k-line rule, spaghetti growth)
argument-hint: "[base branch, default main]"
---

# Extreme Code Quality Review

Run an extremely strict maintainability audit of the current branch's changes.

**Usage**: `/extreme-code-quality-review [base-branch]` (defaults to `main`, falls back to `master`)

## Steps

1. **Determine the base branch**: Use the argument if given, otherwise `main`. If `git rev-parse --verify main` fails, fall back to `master`.
2. **Gather the diff**: `git rev-parse --verify --quiet <base>` must succeed. Otherwise stop and report that `<base>` does not exist. Run `git merge-base <base> HEAD` and call the commit it prints `<merge-base>`. If it prints nothing, report that `<base>` and `HEAD` share no history and stop. Run `git diff <merge-base>`, `git diff --name-only <merge-base>`, and `git status --porcelain --untracked-files=all`. If the diff is empty and there are no untracked files, report that and stop.
3. **Read full file contents for every changed or untracked file** — not just the touched hunks. Whole-file context is required to judge file size, structural drift, and boundary leaks. For large changesets, dispatch an `Explore` subagent with `model: "sonnet"` to collect file contents instead of pulling them all into the main context.
4. **Load the rubric**: `Read` `${CLAUDE_PLUGIN_ROOT}/skills/extreme-code-quality-review/SKILL.md`. The skill sets `disable-model-invocation: true`, so the `Skill` tool cannot load it. Treat the file as the **complete** rubric — tone, approval bar, output ordering, code-judo / 1k-line / spaghetti rules.
5. **Optional — dispatch the subagent**: If the `extreme-code-quality-review` subagent is available (it ships with this plugin), you may dispatch it via `Agent(subagent_type: "extreme-code-quality-review", ...)` with the diff and file contents as the prompt. This protects the main context from large file payloads. Otherwise, apply the rubric directly.
6. **Apply the rubric** to what the diff and contents show. Trace cross-file impact when the change touches module boundaries.
7. **Output findings** in the priority order the rubric specifies. Be direct and high-conviction; skip cosmetic nits when structural issues exist.

## Requirements

- Do not approve merely because behavior seems correct — see the rubric's approval bar.
- Prefer a smaller number of high-conviction comments over a long list of cosmetic notes.
- Push hard for "code judo" simplifications when a plausible path exists.
