---
description: Review the current branch for correctness, AI slop, and repo-convention drift before opening a PR
argument-hint: "[base branch, default main]"
---

# Pre-Review

Review the current branch's changes before opening a PR. Catch the feedback reviewers would give, before they give it.

## Steps

1. **Get the change**: Base = `$ARGUMENTS` if given, else `main` (fall back to `master`). Run `git diff <base>...HEAD`, `git diff --name-only <base>...HEAD`, and `git status --porcelain --untracked-files=all` — diffs never show untracked files, so without the status check a brand-new file that was never `git add`ed is invisible. If the branch diff is empty, review uncommitted work instead: `git diff HEAD` plus the untracked files from that same status output.
   - Read the full current contents of every changed file — the diff alone gives you hunks with three lines of context, and an untracked file has no diff at all. On a large branch (roughly 10+ changed files), dispatch `Explore` subagents with `model: "sonnet"` to read them and return condensed summaries instead of pulling everything into the main context.
   - For any exported signature that changed, grep the repo for callers and check them too — the diff cannot show you a caller it didn't touch.
2. **Check every changed file** against:
   - The repo's CLAUDE.md conventions
   - The correctness and baseline checks below
3. **Run the repo's static gates**: detect the typecheck and lint commands from the repo itself — package.json scripts, Makefile targets, CI config, or the ecosystem's standard runner — and run any that exist. Never invent one; skip silently if none exist or they're impractically slow, and never block the review on them. Report only real errors touching changed files, in the same finding format as everything else — never paste raw tool output or pre-existing debt on untouched lines. These gates mechanically cover unused imports and type errors; escape-hatch overuse (`as any`) and naming drift are invisible to them and stay manual checks.
4. **Report** — do not change code yet:

   ```markdown
   ## Pre-Review

   ### Convention Violations
   - `file.ts:42` — [rule violated] → [suggested fix]

   ### Correctness Issues
   - `file.ts:57` — [defect] → [suggested fix]

   ### Baseline Issues
   - `file.ts:88` — [issue] → [suggested fix]

   ### Worth a Look
   - `file.ts:120` — [suspicion] — unconfirmed; [what would confirm or kill it]

   ### Verdict
   Ready to open PR / Fix the above first
   ```

   Write findings in Simplified Technical English — load the `ste-writing` skill and apply its PR-review-comment format: a phrase — the fix as a bare command, or the defect in a few words — with exact names and values in backticks; one sentence only when the phrase alone is not actionable. No hedges, no restating the diff back, no background you won't act on.

   For each violation cite the specific convention so it's clear this isn't generic opinion. If everything passes, say so briefly — don't manufacture findings. A suspicion you can't confirm goes under Worth a Look with what would confirm or kill it — not dressed up as a confirmed finding, not silently dropped. Worth a Look items never block the verdict on their own.
5. **Offer fixes**: If there are findings, ask via AskUserQuestion (multi-select) which categories to apply — Convention violations / Correctness issues / Baseline issues. Worth a Look items are never offered for auto-apply: they're suspicions to triage, not fixes. Apply what's approved with minimal diffs, then confirm each fix resolved its finding. Skip the question entirely when there are no findings.

## Correctness Checks (always run)

- Inverted conditions, off-by-one bounds, wrong variable in a near-duplicate block
- Missing await or unhandled promise — or the language's equivalent dropped async result or unchecked error — and sequential-vs-parallel mistakes
- Null/undefined paths the types claim are impossible but the data allows
- Error handling that swallows: empty catch, logged-and-continued where the caller needs the failure
- Callers of a changed exported signature that the diff didn't touch
- New branches with no test exercising them

## Baseline Checks (always run)

- Comments that restate the code instead of explaining why
- Defensive checks on data already validated upstream
- Type escape hatches (`as any`, unchecked casts) instead of fixed types
- Dead code, unused imports, debug logging left behind
- Single-use wrappers and abstractions that obscure rather than simplify
- Naming, style, or error-handling drift from the surrounding file's patterns
- Tautological tests: the assertion recomputes the expected value the same way the code does, so it passes by construction — expected values must come from an independent source
- Implementation-coupled tests: tests that break on refactor rather than on behavior change (asserting on internals, mocking the unit under test)
