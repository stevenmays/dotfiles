# Project Guidelines

## Project Overview

<!-- TODO: Update when placed in a new project -->
- **Name**: [Project name]
- **Purpose**: [Brief description]
- **Stack**: TypeScript, [framework], [database]

## Commands

<!-- TODO: Infer from package.json or update manually -->
```bash
npm run build      # Build the project
npm run test       # Run tests
npm run lint       # Lint code
npm run typecheck  # Type check
```

## Directory Structure

<!-- TODO: Update to match actual project layout -->
```
src/
├── handlers/     # Entry points (API routes, Lambda handlers)
├── lib/          # Shared business logic
└── scripts/      # Development/build scripts
```

## Workflow Patterns

**New Feature**
1. Plan → Implement → Test (if repo has tests) → Review

**Bug Fix**
1. Reproduce → Hypothesize → Fix → Add regression test (if repo has tests)
2. **Escalation**: After 2 failed fix attempts, stop and use `/analyze-bug`

**Code Quality**
1. Review → Refactor → Validate

**Philosophy**: Make it work → Make it right → Make it fast

## Core Principles

1. **Simplicity over cleverness** - Write code that's immediately understandable
2. **Leverage existing solutions** - Use standard libraries, don't reinvent
3. **Minimum viable first** - Start simple, add complexity only when needed
4. **Single responsibility** - Functions do one thing, under 20 lines
5. **Early returns** - Guard clauses over nested conditionals
6. **Pure functions** - Separate I/O from business logic
7. **Match existing patterns** - Follow the file's conventions exactly

## Security

- Never hardcode secrets or credentials
- Validate all external inputs at system boundaries
- Use type guards for runtime validation

## Before You Start

Read the relevant reference docs in `.agent_docs/`:

| File | When to Read |
|------|--------------|
| `coding-patterns.md` | Writing new TypeScript code |
| `anti-patterns.md` | Before code review or PR |
| `error-handling.md` | Implementing error handling |
| `testing-patterns.md` | Writing or refactoring tests |
| `bug-investigation.md` | Debugging issues that resist quick fixes |
| `code-review-checklist.md` | Reviewing code or preparing a PR |

## Project-Specific Notes

<!-- Add project-specific conventions, gotchas, or context here -->
