---
description: Review someone else's PR against the repo's distilled standards — findings as STE-written Conventional Comments, with optional posting to GitHub
argument-hint: "<PR number or URL> (required)"
---

# Review PR

Review another author's pull request against the repo's distilled standards (`.claude/standards.md`) plus baseline correctness. For your own branch, use `/pre-review` instead.

## Steps

1. **Resolve the PR**: `$ARGUMENTS` is required — a PR number or URL. If missing, stop and say this command reviews others' PRs by number (`/pre-review` covers the current branch). Confirm it exists: `gh pr view <n> --json number,title,author,state,baseRefName`.
2. **Load standards**: Read `.claude/standards.md` — every section, including `## One-offs` and `## Manual`. `## Known False Positives` is a suppression list, not a rule set: drop findings matching an entry there instead of reporting them. If it doesn't exist, note that `/distill-standards` generates it and continue with only the baseline checks. Apply the same staleness check as `/pre-review`: if 15+ PRs merged since the header date (or it's over 90 days old), lead the report with a one-line suggestion to run `/distill-standards` (a bare run does a cheap delta). Skip silently if the check fails.
3. **Gather the change**:
   - Diff and file list: `gh pr diff <n>` and `gh pr view <n> --json files`
   - PR description and existing discussion: `gh pr view <n> --json body,reviews,comments` — don't re-raise points a reviewer already made.
   - Ticket: find the originating ticket and fetch it, so the review can check the diff against what was asked, not just how it's written. Look for references in the PR body (`Closes #N`, `Fixes #N`, issue URLs), the branch name (`gh pr view <n> --json headRefName`), and the PR title — GitHub issue numbers, or tracker keys like `ABC-123` (Linear, Jira) and `sc-12345` (Shortcut). Resolve through whatever is available locally: `gh issue view` for GitHub issues; a connected tracker MCP tool or installed CLI for the rest — memory or the repo's CLAUDE.md may record which tracker the team uses. If a reference exists but nothing resolves it, say so in the report and review against the PR description alone — never block the review on the ticket.
   - For non-trivial changes, dispatch an Explore subagent to read the full contents of changed files on the PR's branch for context, so findings aren't hunk-blind.
4. **Review** every changed file against:
   - Each rule in `.claude/standards.md` — cite the specific rule in the finding
   - Intent — was the right thing built? Check the diff against the ticket and PR description: requirements missing or partial, behavior nobody asked for (scope creep), and requirements implemented wrong. Skip silently only when there is neither ticket nor description to check against.
   - General correctness: inverted conditions, off-by-one bounds, missing await or unhandled promise, null paths the types claim are impossible, error handling that swallows failures the caller needs, broken contracts with unchanged callers, new branches with no test
   - Baseline checks: comments that restate the code, defensive checks on already-validated data, type escape hatches (`as any`, unchecked casts), dead code / debug logging, single-use wrappers, drift from the surrounding file's patterns
5. **Report** — every finding is a Conventional Comment (conventionalcomments.org), written in Simplified Technical English:
   - Load the `ste-writing` skill before drafting, and apply its PR-review-comment format: at most 2 sentences per finding — the defect, then the fix — with exact names, lines, and values in backticks.
   - Label each finding: `issue` (must fix), `suggestion` (worth considering), `nitpick` (minor), `question` (needs the author's answer), `praise` (genuinely good). Decorate where it disambiguates: `issue (blocking):`, `suggestion (non-blocking):`.
   - Include `praise` only when genuine — at most one or two, never manufactured.

   ```markdown
   ## Review of PR #123 — [title]

   > Standards distilled YYYY-MM-DD; N PRs merged since — consider re-running /distill-standards. (only when stale)

   ### Intent
   Built what was asked? Yes / Partly / No — [one line against the ticket (cite its ID) or description; note when a ticket reference couldn't be resolved. Omit the section only when there was nothing to check against.]

   ### Findings
   - **issue (blocking):** `file.ts:42` — [defect]. [Fix]. (violates: [standard rule], #130)
   - **suggestion (non-blocking):** `file.ts:88` — [improvement]. [Why it matters].
   - **question:** `file.ts:120` — [what needs the author's answer].
   - **praise:** `file.ts:12` — [what is genuinely good].

   ### Verdict
   Approve / Approve with nits / Request changes — [one-line rationale]
   ```

   Order findings by severity. If the PR is clean, say so briefly — don't manufacture findings.
6. **Offer to post**: If there are findings, ask via AskUserQuestion how to deliver them — Post as inline review comments (`gh api repos/{owner}/{repo}/pulls/<n>/reviews` with per-line comments) / Post as a single summary comment (`gh pr comment`) / Keep local only. When posting inline, each comment body is the finding's conventional comment verbatim — label, decoration, then the two STE sentences. Never post to GitHub without asking, and never submit an approval or request-changes verdict on the user's behalf — post comments only; the user clicks the verdict themselves.

## Guidelines

- Prefer a few high-conviction findings over a long list of nits — this lands in another person's review queue.
- Cite standards rules wherever they apply so feedback reads as repo policy, not personal opinion.
- Skip anything the repo's linter, formatter, or CI already enforces — tooling catches it without spending the author's attention.
- For a deep architectural audit of your own work, use `/extreme-code-quality-review`.
