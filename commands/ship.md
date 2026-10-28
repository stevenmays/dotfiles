---
description: Run the full pre-PR golden path — convention review, correctness review, tests — then commit, push, and open the PR
argument-hint: "[base branch, defaults to the repo's default branch]"
---

# Ship

Take the current work from done-coding to an opened PR with every quality gate applied: convention review, correctness review, tests, conventional commit, push, PR. The golden path as one command.

## Steps

1. **Preflight**:
   - Run `gh api user -q .login` and call its output `<login>`.
   - Run `git config user.email` and call its output `<email>`. If it prints nothing, stop and report that `user.email` is unset.
   - Run `gh repo view --json nameWithOwner,viewerPermission,defaultBranchRef` and call its `nameWithOwner` value `<nameWithOwner>`.
   - Stop unless `viewerPermission` is `ADMIN`, `MAINTAIN`, or `WRITE`. Report the value it shows.
   - If any of these commands fails, stop and report its error.
   - Base = `$ARGUMENTS` if given, else `defaultBranchRef.name` from the `gh repo view` output. If neither gives a name, stop and report that the repo has no default branch.
   - If there is nothing to ship (no commits ahead of base and no uncommitted changes per `git status --porcelain --untracked-files=all` — untracked files count), stop and say so.
   - If currently on the base branch, create a feature branch now, named `<type>/<short-slug>` after the change's conventional-commit type (e.g. `feat/retry-webhooks`). Never commit to or push the base branch.
2. **Gate 1 — conventions**: run the `pre-review` command against the base. Apply the convention-violation and baseline fixes it reports with minimal diffs — /ship applies fixes itself, so skip pre-review's own apply-fixes question. Correctness findings change behavior by definition: hold them for the checkpoint, along with any other finding that would change behavior rather than conform structure or style (Gate 2 independently deep-checks correctness). Surface Worth a Look items at the checkpoint too — never auto-apply anything for them.
3. **Gate 2 — correctness**: run the native `code-review` skill at high effort on the branch diff. Apply fixes for confirmed correctness findings; hold uncertain ones for the checkpoint.
4. **Gate 3 — tests**: run the `test-and-fix` command scoped to the code changed on the branch, with this run's base as its base (its iteration limits and never-change-expectations rule apply). If regressions are still red when it stops, stop /ship and report — never ship a red branch. Failures that `test-and-fix` classifies as pre-existing or flaky don't stop /ship; list them at the checkpoint.
5. **Checkpoint** — one AskUserQuestion before anything leaves the machine. Show: gate results including any held findings, the planned commit message, the PR title and body, and the line "commit as `<email>`, push as `<login>` to `<nameWithOwner>`" filled from step 1. Options: Ship it / Fix held findings first / Stop here (leave the working tree as-is, no commit).
   - Fix held findings first: apply the fixes, then re-run step 4 on the fixed code. Rebuild the commit message and the PR body, test plan included, from that code. The test plan states that Gates 1 and 2 ran before these fixes. Then show this checkpoint again. It repeats the same question, so the one-question rule still holds.
6. **Commit**: stage the relevant files — never `.env*`, credential files, `*.pem`, or `*.key`. Conventional commit format, subject under 72 characters, summarizing the why. Split into multiple commits only when the branch clearly contains independent logical changes.
7. **Push** the feature branch with `-u`. Never push the base branch.
8. **Open the PR**: `gh pr create` against the base. Description: a 1–3 bullet summary plus a test plan section listing what the gates checked and the actual test results. End the test plan with these two lines:
   - `Unverified:` each claim or acceptance criterion that no gate or test checked, or `none`.
   - `Merge danger:` a one-way or two-way door call, the blast radius, and the rollback route. A one-way door is a change that reverting the PR doesn't undo.
9. **Report**: PR URL, gate outcomes, and the fixes applied at each gate.

## Guidelines

- For large or structural changes, run `/extreme-code-quality-review` before shipping — /ship deliberately skips the deep structural audit to stay fast.
- Gates run in this order because each is cheaper to fix before the next: convention drift first, then correctness, then the full test suite.
- The checkpoint is the only question. Everything before it is read-only or reversible; everything after it follows from a yes.
