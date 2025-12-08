# Code Review Checklist

Read this before reviewing code or preparing a PR.

## Priority Order

Review in this order. Stop at critical issues.

### 1. Correctness (Critical)
- [ ] Logic errors, off-by-one, wrong operator
- [ ] Edge cases: null, empty, zero, negative, max values
- [ ] Async: race conditions, unhandled promises, missing await
- [ ] Data flow: correct inputs → correct outputs

### 2. Security (Critical)
- [ ] Input validation at system boundaries
- [ ] No hardcoded secrets or credentials
- [ ] SQL/command injection possible?
- [ ] Sensitive data exposure in logs/errors

### 3. Maintainability (Important)
- [ ] Code is readable without comments explaining it
- [ ] Names are clear and consistent with codebase
- [ ] Functions are focused (single responsibility)
- [ ] Error messages are actionable

### 4. Performance (Important)
- [ ] N+1 queries or unnecessary loops
- [ ] Resource leaks (connections, file handles)
- [ ] Blocking operations in async code
- [ ] Unbounded growth (memory, data structures)

### 5. Testing (Important)
- [ ] New code has tests (if repo has tests)
- [ ] Edge cases covered
- [ ] Tests are deterministic, not flaky

## Feedback Format

```
[CRITICAL] file.ts:42 - SQL injection via unsanitized input
[IMPORTANT] file.ts:78 - N+1 query in loop, use batch fetch
[MINOR] file.ts:12 - Naming: `data` → `userRecords` for clarity
```

## Rules

- Provide specific file:line references
- Explain the problem AND suggest a fix
- Critical blocks merge, Important should fix, Minor is optional
- Match existing code style, don't "improve" unrelated code
