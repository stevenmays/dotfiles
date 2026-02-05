# Cleanup

Prepare code for PR review by analyzing changes, auto-fixing issues, and reporting what needs manual attention.

## Scope

Run `git diff main --name-only` to identify changed files. All analysis and fixes target only these files.

## Phase 1: Analyze

Scan changed files for:

1. **Dead Code**: Unused imports, functions, or variables
2. **TODO/FIXME Comments**: List all TODO, FIXME, HACK, XXX comments
3. **Type Safety**: `any` types, missing type hints, unsafe casts
4. **Complexity**: Functions over 50 lines or deep nesting (3+ levels)
5. **Duplicated Code**: Similar code blocks that could be extracted

## Phase 2: Auto-fix

Apply fixes to changed files:

1. Replace nested conditionals with early returns
2. Remove comments that repeat the code
3. Remove defensive null checks on already-validated data
4. Fix `as any` casts where possible (add proper types)
5. Remove unnecessary wrappers and single-use abstractions
6. Inline single-use variables (unless line becomes excessively long)
7. Remove dead code and unused variables
8. Ensure style matches existing file patterns

Compare changes against unchanged portions of the same file to maintain consistency.

## Phase 3: Report

Output a summary in this format:

```markdown
## Cleanup Report

### Auto-fixes Applied
- [1-3 sentence summary of what was changed]

### Remaining Issues (Manual Review Needed)

#### High Priority
- [ ] Description (file:line)

#### Medium Priority
- [ ] Description (file:line)

#### Low Priority
- [ ] Description (file:line)

### TODOs Found
- [ ] TODO text (file:line)
```

## Guidelines

- Only report actionable items with file paths and line numbers
- Prioritize remaining issues by impact and effort
- Do not change correct code or add new features
- Keep behavior identical when simplifying
