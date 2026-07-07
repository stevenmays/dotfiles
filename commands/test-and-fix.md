---
description: Run tests and fix failures until green
argument-hint: "[optional test file or pattern to scope the run]"
---

# Test and Fix

Run the repo's tests and fix failures until the suite is green. This is the single test-fixing policy — `/ship`'s test gate delegates here.

## Steps

1. **Detect the test command from the repo itself** — package.json scripts, Makefile targets, CI config, or the ecosystem's standard runner. Never invent one; if nothing is found, say so and stop.
2. **Run**, scoped to `$ARGUMENTS` when given.
3. **Fix and re-run** until green, within these limits:
   - Max 5 iterations total; if the same failure survives 3 attempts, stop and explain what's known.
   - Make the smallest fix that resolves the failure; no unrelated refactors.
   - Never change a test's expectations unless the test is demonstrably wrong — and say so when you do.
   - A fix spanning multiple files gets one sentence of justification before it's made.

## Output

Final test results, plus each fix made and why.
