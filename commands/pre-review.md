---
description: Review the current branch against distilled repo standards before opening a PR
argument-hint: "[base branch, default main]"
---

# Pre-Review

Review the current branch's changes against the repo's distilled standards (`.claude/standards.md`) before opening a PR. Catch the feedback reviewers would give, before they give it.

## Steps

1. **Load standards**: Read `.claude/standards.md`. If it doesn't exist, note that `/distill-standards` generates it, and continue with only the baseline checks below.
   - **Staleness check**: the file header records when and from which PRs it was distilled. Count merged PRs since that date — `gh pr list --state merged --search "merged:>YYYY-MM-DD" --json number --limit 100` — and if 15+ have merged (or the distill date is over 90 days old), lead the report with a one-line warning to re-run `/distill-standards`. Skip this silently if `gh` fails; never block the review on it.
2. **Get the diff**: Base = `$ARGUMENTS` if given, else `main` (fall back to `master`). Run `git diff <base>...HEAD` and `git diff --name-only <base>...HEAD`. If the branch diff is empty, review uncommitted work via `git diff HEAD` instead.
3. **Check every changed file** against:
   - Each rule in `.claude/standards.md`
   - The baseline checks below
4. **Report** — do not change code yet:

   ```markdown
   ## Pre-Review

   > Standards distilled YYYY-MM-DD; N PRs merged since — consider re-running /distill-standards. (only when stale)

   ### Standards Violations
   - `file.ts:42` — [rule violated] → [suggested fix]

   ### Baseline Issues
   - `file.ts:88` — [issue] → [suggested fix]

   ### Verdict
   Ready to open PR / Fix the above first
   ```

   For each violation cite the specific standard so it's clear this isn't generic opinion. If everything passes, say so briefly — don't manufacture findings.

5. **Offer fixes**: If there are findings, ask via AskUserQuestion whether to apply them — Apply all / Standards violations only / Baseline issues only / None. Apply what's approved with minimal diffs, then confirm each fix resolved its finding. Skip the question entirely when there are no findings.

## Baseline Checks (always run)

- Comments that restate the code instead of explaining why
- Defensive checks on data already validated upstream
- Type escape hatches (`as any`, unchecked casts) instead of fixed types
- Dead code, unused imports, debug logging left behind
- Single-use wrappers and abstractions that obscure rather than simplify
- Naming, style, or error-handling drift from the surrounding file's patterns
