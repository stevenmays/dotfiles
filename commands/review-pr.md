---
description: Review someone else's PR against the repo's distilled standards, with optional posting to GitHub
argument-hint: "<PR number or URL> (required)"
---

# Review PR

Review another author's pull request against the repo's distilled standards (`.claude/standards.md`) plus baseline correctness. For your own branch, use `/pre-review` instead.

## Steps

1. **Resolve the PR**: `$ARGUMENTS` is required — a PR number or URL. If missing, stop and say this command reviews others' PRs by number (`/pre-review` covers the current branch). Confirm it exists: `gh pr view <n> --json number,title,author,state,baseRefName`.
2. **Load standards**: Read `.claude/standards.md` — every section, including `## One-offs` and `## Manual`. If it doesn't exist, note that `/distill-standards` generates it and continue with only the baseline checks. Apply the same staleness check as `/pre-review`: if 15+ PRs merged since the header date (or it's over 90 days old), lead the report with a one-line suggestion to run `/distill-standards` (a bare run does a cheap delta). Skip silently if the check fails.
3. **Gather the change**:
   - Diff and file list: `gh pr diff <n>` and `gh pr view <n> --json files`
   - PR description and existing discussion: `gh pr view <n> --json body,reviews,comments` — don't re-raise points a reviewer already made.
   - For non-trivial changes, dispatch an Explore subagent to read the full contents of changed files on the PR's branch for context, so findings aren't hunk-blind.
4. **Review** every changed file against:
   - Each rule in `.claude/standards.md` — cite the specific rule in the finding
   - General correctness: logic errors, unhandled edge cases, broken contracts with unchanged callers
   - Baseline checks: comments that restate the code, defensive checks on already-validated data, type escape hatches (`as any`, unchecked casts), dead code / debug logging, single-use wrappers, drift from the surrounding file's patterns
5. **Report** — findings ordered by severity:

   ```markdown
   ## Review of PR #123 — [title]

   > Standards distilled YYYY-MM-DD; N PRs merged since — consider re-running /distill-standards. (only when stale)

   ### Findings
   - `file.ts:42` — [issue] (violates: [standard rule], #130) → [suggested fix]
   - `file.ts:88` — [correctness/baseline issue] → [suggested fix]

   ### Verdict
   Approve / Approve with nits / Request changes — [one-line rationale]
   ```

   If the PR is clean, say so briefly — don't manufacture findings.
6. **Offer to post**: If there are findings, ask via AskUserQuestion how to deliver them — Post as inline review comments (`gh api repos/{owner}/{repo}/pulls/<n>/reviews` with per-line comments) / Post as a single summary comment (`gh pr comment`) / Keep local only. Never post to GitHub without asking, and never submit an approval or request-changes verdict on the user's behalf — post comments only; the user clicks the verdict themselves.

## Guidelines

- Prefer a few high-conviction findings over a long list of nits — this lands in another person's review queue.
- Cite standards rules wherever they apply so feedback reads as repo policy, not personal opinion.
- For a deep architectural audit of your own work, use `/extreme-code-quality-review`.
