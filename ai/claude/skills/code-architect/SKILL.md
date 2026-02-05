---
name: code-architect
description: Design implementation plans for complex multi-file features
triggers:
  - architect
  - design
  - plan
  - "how should I implement"
  - "implementation plan"
---

# Code Architect

Design a detailed implementation plan for a complex feature before writing code.

## When to Use

- Features spanning 3+ files
- Architectural decisions with tradeoffs
- Refactors affecting multiple modules
- New systems or subsystems

## Process

1. **Understand the requirement**: Clarify goals, constraints, and success criteria
2. **Explore existing code**: Find relevant files, patterns, and conventions
3. **Identify options**: List 2-3 approaches with tradeoffs
4. **Recommend approach**: Pick one and explain why
5. **Create implementation plan**: Break down into ordered steps

## Output Format

```markdown
## Feature: [Name]

### Goal
[What we're building and why]

### Constraints
- [Technical constraints]
- [Time/scope constraints]

### Options Considered

#### Option A: [Name]
- Pros: ...
- Cons: ...

#### Option B: [Name]
- Pros: ...
- Cons: ...

### Recommended Approach
[Which option and why]

### Implementation Plan

1. [ ] **Step 1**: [Description]
   - Files: `path/to/file.ts`
   - Changes: [What to add/modify]

2. [ ] **Step 2**: [Description]
   - Files: `path/to/file.ts`
   - Changes: [What to add/modify]

### Testing Strategy
- [ ] Unit tests for...
- [ ] Integration tests for...

### Rollout Considerations
- [ ] Feature flag needed?
- [ ] Migration required?
- [ ] Breaking changes?
```

## Guidelines

- Read existing code before proposing patterns
- Match existing conventions in the codebase
- Prefer incremental changes over big bang rewrites
- Identify risks and mitigation strategies
- Ask clarifying questions before finalizing the plan
