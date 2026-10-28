---
description: Run tests and fix failures until green
argument-hint: "[optional test file or pattern to scope the run]"
---

# Test and Fix

Run the repo's tests and fix regressions until the suite is green, except for failures that step 3 classifies as flaky or pre-existing. This is the single test-fixing policy — `/ship`'s test gate delegates here.

## Steps

1. **Detect the test command from the repo itself** — package.json scripts, Makefile targets, CI config, or the ecosystem's standard runner. Never invent one; if nothing is found, say so and stop.
2. **Run**, scoped to `$ARGUMENTS` when given.
3. **Classify each failure the first time it appears, before any fix.** Classification edits nothing and doesn't count against step 4's iteration budget.
   - Find the files the branch touched. Base = the base branch the caller names, else the open PR's `baseRefName` from `gh pr view --json baseRefName`, else `main` (fall back to `master`). In git commands, use `origin/<base>` whenever that ref exists, and the local `<base>` only when it doesn't. A stale local branch would count upstream changes as touched. Run `git merge-base <base> HEAD` and call the commit it prints `<merge-base>`. The touched files are the output of `git diff --name-only <merge-base>` plus the untracked files in `git status --porcelain --untracked-files=all`. If no base resolves or the merge-base command prints nothing, skip the base check, treat every failure as a regression, and say so in the report.
   - A failure is a regression when its test file or its failure output names a touched file. Never classify it flaky or pre-existing.
   - Re-run each other failing test by itself, one invocation per test. Use the narrowest scope the runner supports: the test, else its file. Never invent a filter flag. Report the scope you used.
   - A test that passes alone is a flaky candidate. When any candidate exists, run step 2's command once more, at most once per run. A candidate that fails in exactly one of these two full runs is flaky. A candidate that fails in both is order-dependent: send it to the base check. A candidate first seen in a step 4 run uses that run and step 4's next full run as its two runs; that next run counts toward step 4's budget. Every test that failed alone also goes to the base check.
   - Base check, at most once per run. Make a new directory with `mktemp -d` and run `git worktree add --detach <dir> <merge-base>`. Set up dependencies only inside `<dir>`, for example `npm ci` there or a new `<dir>/.venv` with `VIRTUAL_ENV` unset. Install packages only: skip any step that writes git hooks or git config, such as `pre-commit install` or a husky `prepare` script (set `HUSKY=0`). Never install into an environment the main checkout uses, and never copy `.env` or other secrets into `<dir>`. Run step 2's exact command in `<dir>` once, with `<dir>`'s own environment first on `PATH`, for example `PATH=<dir>/.venv/bin:$PATH` when `<dir>` has a venv. Never call an interpreter or binary from the main checkout. If the base run's output names source files outside `<dir>`, discard it and use base CI instead. Reuse the base run's results for failures that appear later. Remove the worktree with `git worktree remove --force <dir>` when that run ends, whether it passed, failed, or errored. `--force` is safe because this command made `<dir>` and nothing else lives there. If removal fails, name `<dir>` in the report.
   - When the worktree can't run the tests, read base CI instead. That covers setup that can't target `<dir>`, a failed install, a missing service or env var, or setup that runs past about 10 minutes. List runs for that exact commit with `gh run list --branch <base> --commit <merge-base> --json databaseId,conclusion,workflowName,url`, with the bare branch name. Read each failed run with `gh run view <id> --log-failed`. Runs at any other commit are not evidence.
   - A failure is pre-existing only when the same test fails on base with the same error. Same error means the same test ID, the same exception type, and the same message after you remove file paths, line numbers, memory addresses, and timings. Leave a pre-existing failure untouched. A different error, a pass on base, or no evidence makes it a regression.
4. **Fix regressions and re-run** until only flaky or pre-existing failures remain, within these limits:
   - Max 5 iterations total; if the same failure survives 3 attempts, stop and explain what's known.
   - A failure that survives 2 attempts gets one fresh strong-model subagent with `model:` unset, the failure output, and the files it touches. Only the session spawns; subagents never do. Never fork.
   - When regressions span 3+ unrelated files, fan out one `sonnet` subagent per file or group in a single message. Each gets a fresh context with only its failure output and the files it names, and inherits the rules below. Re-run the full suite once they return. Below that threshold, fix sequentially; fan-out overhead beats one or two failures.
   - Make the smallest fix that resolves the failure; no unrelated refactors.
   - Never change a test's expectations unless the test is demonstrably wrong — and say so when you do.
   - A fix spanning multiple files gets one sentence of justification before it's made.

## Output

- Final state: `green`; `green except` followed by the listed pre-existing or flaky failures; or `red`, with the regressions still failing.
- Each fix made, and why.
- Each pre-existing failure, with its evidence: the worktree run at `<merge-base>`, or the base CI run URL.
- Each flaky failure: which full run it failed in, and the scope of its isolated re-run.
- If the base check was skipped, say so and give the reason.
- **Proposed `CLAUDE.md` lines**: one `## Gotchas` line per flaky test, in this form: `` - `<test id>` is flaky: it failed in one full run and passed in another. `` Skip a test the repo's `CLAUDE.md` already names. Never write the line during the run, and never ask: `/ship` allows only its checkpoint question. Write it only when the user approves in a later turn, and create `## Gotchas` if it is missing. With no approval, write nothing.
