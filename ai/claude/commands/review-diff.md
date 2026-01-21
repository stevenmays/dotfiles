# Review Diff

Check the diff against main branch and remove anti-pattern violations. For deeper analysis, use pr-review-toolkit's specialized agents (silent-failure-hunter, type-design-analyzer, pr-test-analyzer).

## Process

1. Run `git diff main`
2. For each changed file, look for:
   - Comments that state the obvious or repeat the code
   - Defensive null/type checks on already-validated data
   - `as any` casts - fix the types instead
   - Unnecessary wrappers or single-use abstractions
   - Logging that exceeds the file's existing pattern
   - Style inconsistent with the rest of the file
3. Compare changes against unchanged portions of same file
4. Remove violations without changing correct code

## Output

Report 1-3 sentences summarizing what was changed.

Example:
```
Removed 3 redundant null checks in order-processor.ts (upstream validation handles these).
Deleted 8 obvious comments and converted 2 unnecessary try/catch blocks to let errors propagate.
```
