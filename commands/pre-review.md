---
description: Review the current branch for correctness, AI slop, and repo-convention drift before opening a PR
argument-hint: "[base branch, default main]"
---

# Pre-Review

Review the current branch's changes before opening a PR. Catch the feedback reviewers would give, before they give it.

## Steps

1. **Get the change**: Base = `$ARGUMENTS` if given, else `main` (fall back to `master`). `git rev-parse --verify --quiet <base>` must succeed. Otherwise stop and report that `<base>` does not exist. Run `git merge-base <base> HEAD` and call the commit it prints `<merge-base>`. If it prints nothing, stop and report that `<base>` and `HEAD` share no history. Run `git diff <merge-base>`, `git diff --name-only <merge-base>`, and `git status --porcelain --untracked-files=all`. The diff covers commits, staged edits, and unstaged edits. Diffs never show untracked files, so without the status check a brand-new file that was never `git add`ed is invisible.
   - Read the full current contents of every changed file — the diff alone gives you hunks with three lines of context, and an untracked file has no diff at all. On a large branch (roughly 10+ changed files), dispatch `Explore` subagents with `model: "sonnet"` to read them and return condensed summaries instead of pulling everything into the main context.
   - For any exported signature that changed, grep the repo for callers and check them too — the diff cannot show you a caller it didn't touch.
2. **Check every changed file** against:
   - The repo's conventions. Read `CLAUDE.md` and `AGENTS.md` at the root and in every directory between the root and each changed file. Read `CONTRIBUTING.md` and `CODING_STANDARDS.md` at the root, in `.github/`, or in `docs/`. A copy in `.github/` or `docs/` counts as root level. Use only rules a reviewer would flag, not setup or process steps. Apply every rule from every file on a changed file's path. When two rules conflict, the rule from the nearer file wins. When two files at the same level disagree, report the conflict under Worth a Look and apply neither rule.
   - The correctness and baseline checks below
3. **Run the repo's static gates**: detect the typecheck and lint commands from the repo itself — package.json scripts, Makefile targets, CI config, or the ecosystem's standard runner — and run any that exist. Never invent one; skip silently if none exist or they're impractically slow, and never block the review on them. Report only real errors touching changed files, in the same finding format as everything else — never paste raw tool output or pre-existing debt on untouched lines. These gates mechanically cover unused imports and type errors; escape-hatch overuse (`as any`), new suppressions, and naming drift are invisible to them and stay manual checks. A suppression makes a gate pass without a fix.
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

   For each violation cite the specific convention and the file it comes from so it's clear this isn't generic opinion. If everything passes, say so briefly — don't manufacture findings. A suspicion you can't confirm goes under Worth a Look with what would confirm or kill it — not dressed up as a confirmed finding, not silently dropped. Worth a Look items never block the verdict on their own.
5. **Offer fixes**: If there are findings, ask via AskUserQuestion (multi-select) which categories to apply — Convention violations / Correctness issues / Baseline issues. Worth a Look items are never offered for auto-apply: they're suspicions to triage, not fixes. Apply what's approved with minimal diffs, then confirm each fix resolved its finding. Skip the question entirely when there are no findings. When nobody can answer (a headless run), apply nothing: the report is the result.

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
- New suppressions on added lines: `eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `# noqa`, `# type: ignore`, `#[allow(`, `// nolint`, `.skip(`, `xit(`, `pytest.mark.skip`. Search with `grep`, not by eye: the `+` lines of the diff from step 1, and every line of each untracked file. In the diff, a suppression on a `+` line is unchanged only when a `-` line in the same hunk carries identical suppression text on the same statement. Identical means the same marker with the same rule list, condition, or test name, such as `# type: ignore[attr-defined]` on both lines. Pair each `-` line with at most one `+` line, and flag every other `+` occurrence. Accept any spacing after the comment marker, such as `//nolint` or `#noqa`. `xit(` counts only as a whole word, so `exit(` doesn't match. `.skip(` counts when it skips a test, such as `it.skip(` or `this.skip()`, not an iterator or query `.skip(n)`. Flag every hit, even one with a stated reason: the reviewer decides whether the reason holds. The fix removes the cause the suppression hides, never the marker alone, so it changes behavior.
- Dead code, unused imports, debug logging left behind
- Single-use wrappers and abstractions that obscure rather than simplify
- Naming, style, or error-handling drift from the surrounding file's patterns
- Tautological tests: the assertion recomputes the expected value the same way the code does, so it passes by construction — expected values must come from an independent source
- Implementation-coupled tests: tests that break on refactor rather than on behavior change (asserting on internals, mocking the unit under test)
