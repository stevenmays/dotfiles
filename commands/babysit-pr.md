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
4. **Fix CI**: `gh pr checks <n>` to list checks; if checks are pending, wait with `gh pr checks <n> --watch` before analyzing. When 3+ independent jobs fail, fan out one `sonnet` subagent per job in a single message. Each gets a fresh context with only its logs and owns its slice's root cause and fix. Below that threshold, fix sequentially, since fan-out overhead beats one or two failures. For each failure, get logs via `gh run view <run-id> --log-failed`, then fix by type:
   - Test failures → run the `test-and-fix` command scoped to the failing area, with the PR's bare base branch name as its base (its iteration limits, failure classification, and never-change-expectations rule apply). Run `git fetch origin <base>` once before any test fix or fan-out, never inside each subagent. The fetch updates `origin/<base>`, which `test-and-fix` uses in git commands; its `gh` commands get the bare name.
   - Lint, format, or type errors → run the same tool locally, fix, re-run until clean.
   - Build failures → reproduce locally and fix the root cause. Never fix a build by loosening config (ignore flags, skipped checks) unless that is already the repo's pattern.
   - A check that also fails on the base branch is not this PR's problem — note it in the report and move on. The same applies to a check whose only failures `test-and-fix` classifies as pre-existing or flaky.
5. **Address review comments**: fetch unresolved threads — `gh api repos/{owner}/{repo}/pulls/<n>/comments` plus `gh pr view <n> --json reviews`. For each:
   - Mechanical or clearly-scoped fixes (typo, naming, missing check, style) → apply them.
   - Design decisions, scope questions, anything uncertain → leave the code alone and list the comment in the report with why.
   - A comment that states a convention — a rule a reviewer could check on other code — gets a proposed `## Conventions` line for the repo's `CLAUDE.md`, whether or not you apply the comment. Use the form `- <rule as one imperative sentence>.` Skip it when `CLAUDE.md` already states the rule. List the proposal in the report and write nothing. Write it only when the user approves in a later turn; with no approval, write nothing.
   - Address comments in code only. Never reply to or resolve review threads on GitHub — the user replies and resolves. Step 8's `escaped:` comment is the only comment this command posts.
6. **Commit and push**: conventional commits, one commit per concern, subject under 72 characters summarizing the why — never a generic "address feedback". Push the PR branch. Never force-push, never push the base branch.
7. **Re-check**: after pushing, watch CI and re-triage from step 2. Max 3 fix-push-check rounds; then stop and report what is still red.
8. **Record escapes**: after the step 7 loop ends, post one top-level PR comment for the defects this run fixed. A defect is a CI failure that is green after this run's fix commits, or a review-comment defect this run committed a fix for. A check that went green with no fix commit from this run, or that is still red, gets no line. For a CI failure, `<short-sha>` is the commit that made its check green. Merge conflicts, and failures `test-and-fix` classified as pre-existing or flaky, get no line. Each defect gets one line:

   `escaped: <gate> — <defect in a few words> (fixed in <short-sha>)`

   `<gate>` names the `/ship` gate that owns that kind of defect:
   - CI test failure → `test-and-fix` (Gate 3).
   - CI lint, format, or type error → `pre-review` (Gate 1).
   - CI build failure or any other CI job → `none`. No `/ship` gate checks it, so this value marks a gap in the gates.
   - Reviewer-found logic or correctness defect → `code-review` (Gate 2).
   - Reviewer-found convention, naming, style, or dead-code defect, or a missing test → `pre-review` (Gate 1).

   Read existing comments first with `gh pr view <n> --json comments --jq '.comments[].body'`. Drop each line whose `<short-sha>` already appears in an existing `escaped:` line. Post the rest with `gh pr comment <n> --body-file -`. Post nothing when no lines remain.
9. **Report**:
   - PR state: merge-ready, or exactly what still blocks.
   - Each fix made — conflicts resolved, checks fixed, comments addressed — and the comments left for the user with why.
   - Failures `test-and-fix` classified as pre-existing or flaky, with their evidence.
   - The `escaped:` lines posted, or that none were new.
   - Proposed `CLAUDE.md` lines from `test-and-fix` and from review comments, each marked unwritten until the user approves.
   - If the PR is a draft and everything is green, say it is ready for `gh pr ready` — don't run it.

## Guidelines

- Never merge the PR, approve it, or change its review state — babysitting ends at "merge-ready", the user clicks the rest.
- Each run is idempotent: a clean PR produces a one-line "merge-ready" report and posts no comment. To keep watch over a longer window, run it on an interval (e.g. `/loop 15m /babysit-pr`).
- If the same check fails after two different fixes, stop touching it and report — don't thrash the PR history.
