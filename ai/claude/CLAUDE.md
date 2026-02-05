# Project Guidelines

## Project Overview

- **Name**: [Project name]
- **Purpose**: [Brief description]
- **Stack**: [Stack]

## Commands

```bash
npm run build      # Build the project
npm run test       # Run tests
npm run lint       # Lint code
npm run typecheck  # Type check
```

## Directory Structure

```
src/
├── handlers/     # Entry points (API routes, Lambda handlers)
├── lib/          # Shared business logic
└── scripts/      # Development/build scripts
```

## Project-Specific Notes

<!-- Add project-specific conventions, gotchas, or context here -->

---

## Workflow Rules

### Planning & Approval

- Describe approach and wait for approval before writing code
- Ask clarifying questions when requirements are ambiguous
- If task requires 3+ file changes, break into smaller tasks first

### Verification

- After writing code, list what could break and suggest tests
- Never mark tasks complete without proving they work
- For bugs: if the repo has tests, write a failing test first, then fix until it passes

### Subagent Strategy

- Offload research/exploration to subagents to keep main context clean
- One focused task per subagent

### Quality Bar

- For non-trivial changes, ask "is there a more elegant way?"
- Skip this for simple/obvious fixes—don't over-engineer
- Simplicity first: make changes as minimal as possible

---

## Self-Improvement

When corrected:
1. **Small fix** (1 sentence): Add to "Lessons Learned" section below
2. **Pattern** (recurring or multi-step): Create `.agent/[pattern-name].md` or `.cursor/rules/[pattern-name].md`

Review lessons at session start.

---

## Living Document

This file should evolve as you work on the project. After every correction or discovery, update the relevant section.

### Lessons Learned

<!-- Corrections and discoveries from this project -->
<!-- Example: "All API routes use kebab-case: /user-settings not /userSettings" -->
<!-- Example: "The auth middleware silently fails if JWT_SECRET is not set" -->

### Patterns to Follow

<!-- Document patterns that work well in this codebase -->
<!-- Example: "Use the Result type from lib/result.ts for error handling" -->

### Patterns to Avoid

<!-- Document anti-patterns or approaches that caused problems -->
<!-- Example: "Don't use default exports - breaks IDE refactoring" -->
