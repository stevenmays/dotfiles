---
name: verify-app
description: Run build, typecheck, lint, and test checks with a pass/fail report
triggers:
  - verify
  - check
  - validate
  - "run all checks"
  - "is it working"
---

# Verify App

Run a comprehensive verification of the application to ensure everything works.

## Checks to Run

Execute these in order, continuing even if earlier steps fail:

1. **Build**: Compile/bundle the application
2. **Typecheck**: Verify type correctness
3. **Lint**: Check code style and potential issues
4. **Test**: Run the test suite

## Detection

Detect the project type and use appropriate commands:

| Project Type | Build | Typecheck | Lint | Test |
|--------------|-------|-----------|------|------|
| Node.js (package.json) | `npm run build` | `npx tsc --noEmit` | `npm run lint` | `npm test` |
| Python (pyproject.toml) | - | `mypy .` | `ruff check .` | `pytest` |
| Go (go.mod) | `go build ./...` | `go vet ./...` | `golangci-lint run` | `go test ./...` |
| Rust (Cargo.toml) | `cargo build` | - | `cargo clippy` | `cargo test` |

Skip any step if the command/tool is not available.

## Output Format

```
## Verification Report

| Check     | Status | Details |
|-----------|--------|---------|
| Build     | PASS/FAIL | (error summary if failed) |
| Typecheck | PASS/FAIL | (error count if failed) |
| Lint      | PASS/FAIL | (warning/error count) |
| Test      | PASS/FAIL | (X passed, Y failed) |

**Overall: PASS/FAIL**
```

## Guidelines

- Run all checks even if early ones fail
- Capture and summarize errors, don't dump full output
- Report skip if a check doesn't apply to the project
- Suggest fixes for common failures
