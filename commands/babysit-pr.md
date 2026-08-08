---
description: Keep your open PR merge-ready — fix CI failures, address review comments, resolve merge conflicts
argument-hint: "[PR number, default: the current branch's PR]"
---

# Babysit PR

Monitor your own open pull request and keep it merge-ready: resolve merge conflicts, fix CI failures, address review comments. For reviewing someone else's PR, use `/review-pr`.

## Steps

1. **Resolve the PR**: `$ARGUMENTS` if given, else the current branch's PR — `gh pr view [n] --json number,title,state,isDraft,baseRefName,mergeStateStatus,reviewDecision,statusCheckRollup`. If there is no open PR, stop and say so. If not already on the PR branch, `gh pr checkout <n>`.
2. **Triage** in this order — conflicts first, because CI results on a conflicted branch go stale the moment base merges in:
   1. Merge conflicts (`mergeStateStatus: DIRTY`)
   2. Failing CI checks
   3. Unresolved review comments
3. **Resolve conflicts**: `git fetch origin <base> && git merge origin/<base>`, then run the `fix-merge-conflict` command — its resolution priorities and validation apply.
4. **Fix CI**: `gh pr checks <n>` to list checks; if checks are pending, wait with `gh pr checks <n> --watch` before analyzing. When 3+ independent jobs fail, fan out one subagent per job in a single message — each owns its slice's logs, root cause, and fix; below that threshold, fix sequentially, since fan-out overhead beats one or two failures. For each failure, get logs via `gh run view <run-id> --log-failed`, then fix by type:
   - Test failures → run the `test-and-fix` command scoped to the failing area (its iteration limits and never-change-expectations rule apply).
   - Lint, format, or type errors → run the same tool locally, fix, re-run until clean.
   - Build failures → reproduce locally and fix the root cause. Never fix a build by loosening config (ignore flags, skipped checks) unless that is already the repo's pattern.
   - A check that also fails on the base branch is not this PR's problem — note it in the report and move on.
5. **Address review comments**: fetch unresolved threads — `gh api repos/{owner}/{repo}/pulls/<n>/comments` plus `gh pr view <n> --json reviews`. For each:
   - Mechanical or clearly-scoped fixes (typo, naming, missing check, style) → apply them.
   - Design decisions, scope questions, anything uncertain → leave the code alone and list the comment in the report with why.
   - Address comments in code only. Never reply to or resolve threads on GitHub — the user replies and resolves.
6. **Commit and push**: conventional commits, one commit per concern, subject under 72 characters summarizing the why — never a generic "address feedback". Push the PR branch. Never force-push, never push the base branch.
7. **Re-check**: after pushing, watch CI and re-triage from step 2. Max 3 fix-push-check rounds; then stop and report what is still red.
8. **Report**:
   - PR state: merge-ready, or exactly what still blocks.
   - Each fix made — conflicts resolved, checks fixed, comments addressed — and the comments left for the user with why.
   - If the PR is a draft and everything is green, say it is ready for `gh pr ready` — don't run it.
   - If review feedback was addressed, suggest `/distill-standards #<n>` to turn that feedback into a standing rule.

## Guidelines

- Never merge the PR, approve it, or change its review state — babysitting ends at "merge-ready", the user clicks the rest.
- Each run is idempotent: a clean PR produces a one-line "merge-ready" report. To keep watch over a longer window, run it on an interval (e.g. `/loop 15m /babysit-pr`).
- If the same check fails after two different fixes, stop touching it and report — don't thrash the PR history.
