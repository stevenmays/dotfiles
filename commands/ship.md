---
description: Run the full pre-PR golden path — standards review, correctness review, tests — then commit, push, and open the PR
argument-hint: "[base branch, default main]"
---

# Ship

Take the current work from done-coding to an opened PR with every quality gate applied: standards conformance, correctness review, tests, conventional commit, push, PR. The golden path as one command.

## Steps

1. **Preflight**:
   - Base = `$ARGUMENTS` if given, else `main` (fall back to `master`).
   - If there is nothing to ship (no commits ahead of base and no uncommitted changes), stop and say so.
   - If currently on the base branch, create a feature branch now, named `<type>/<short-slug>` after the change's conventional-commit type (e.g. `feat/retry-webhooks`). Never commit to or push the base branch.
2. **Gate 1 — standards**: run the `pre-review` command against the base. Apply every fix it reports (standards violations and baseline issues) with minimal diffs — /ship applies fixes itself, so skip pre-review's own apply-fixes question. If a finding would change behavior rather than conform structure or style, hold it for the checkpoint instead of auto-applying.
3. **Gate 2 — correctness**: run the native `code-review` skill at high effort on the branch diff. Apply fixes for confirmed correctness findings; hold uncertain ones for the checkpoint.
4. **Gate 3 — tests**: detect the repo's test command (package.json scripts, pytest, go test, cargo test). Run tests scoped to the changed code when the runner supports it, otherwise the full suite. Fix failures caused by this branch (max 3 iterations); if still red, stop and report — never ship a red branch.
5. **Checkpoint** — one AskUserQuestion before anything leaves the machine. Show: gate results including any held findings, the planned commit message, and the PR title and body. Options: Ship it / Fix held findings first / Stop here (leave the working tree as-is, no commit).
6. **Commit**: stage the relevant files — never `.env*`, credential files, `*.pem`, or `*.key`. Conventional commit format, subject under 72 characters, summarizing the why. Split into multiple commits only when the branch clearly contains independent logical changes.
7. **Push** the feature branch with `-u`. Never push the base branch.
8. **Open the PR**: `gh pr create` against the base. Description: a 1–3 bullet summary plus a test plan section listing what the gates checked and the actual test results.
9. **Report**: PR URL, gate outcomes, and the fixes applied at each gate.

## Guidelines

- For large or structural changes, run `/extreme-code-quality-review` before shipping — /ship deliberately skips the deep structural audit to stay fast.
- Gates run in this order because each is cheaper to fix before the next: standards drift first, then correctness, then the full test suite.
- The checkpoint is the only question. Everything before it is read-only or reversible; everything after it follows from a yes.
- After human review lands on the PR, close the loop: `/distill-standards #<PR>`.
