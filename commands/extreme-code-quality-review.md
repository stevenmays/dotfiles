---
description: Extremely strict maintainability audit of the current branch (code-judo, 1k-line rule, spaghetti growth)
argument-hint: "[base branch, default main]"
---

# Extreme Code Quality Review

Run an extremely strict maintainability audit of the current branch's changes.

**Usage**: `/extreme-code-quality-review [base-branch]` (defaults to `main`, falls back to `master`)

## Steps

1. **Determine the base branch**: Use the argument if given, otherwise `main`. If `git rev-parse --verify main` fails, fall back to `master`.
2. **Gather the diff**: Run `git diff <base>...HEAD` and `git diff --name-only <base>...HEAD`. If the diff is empty, report that and stop.
   Also read `.claude/standards.md` if it exists — its rules (every section, including `## One-offs` and `## Manual`) are additional review criteria on top of the rubric; cite the specific rule when flagging a violation.
3. **Read full file contents for every changed file** — not just the touched hunks. Whole-file context is required to judge file size, structural drift, and boundary leaks. For large changesets, dispatch an `Explore` subagent to collect file contents instead of pulling them all into the main context.
4. **Load the rubric**: Invoke the `extreme-code-quality-review` skill via the `Skill` tool. Treat its `SKILL.md` as the **complete** rubric — tone, approval bar, output ordering, code-judo / 1k-line / spaghetti rules.
5. **Optional — dispatch the subagent**: If the `extreme-code-quality-review` subagent is available (it ships with this plugin), you may dispatch it via `Agent(subagent_type: "extreme-code-quality-review", ...)` with the diff, file contents, and distilled standards (when they exist) as the prompt. This protects the main context from large file payloads. Otherwise, apply the rubric directly.
6. **Apply the rubric** to what the diff and contents show. Trace cross-file impact when the change touches module boundaries.
7. **Output findings** in the priority order the rubric specifies. Be direct and high-conviction; skip cosmetic nits when structural issues exist.

## Requirements

- Do not approve merely because behavior seems correct — see the rubric's approval bar.
- Prefer a smaller number of high-conviction comments over a long list of cosmetic notes.
- Push hard for "code judo" simplifications when a plausible path exists.
