# Plan Feature

Break a feature into implementable stages before coding. For complex features with architectural decisions, consider using `/feature-dev` which provides a full 7-phase workflow with specialized agents.

## Process

1. **Requirements** - What must it do? What are the constraints?
2. **Dependencies** - What existing code/systems does this touch?
3. **Risks** - What could go wrong? What's uncertain?
4. **Stages** - Break into 3-5 stages, each independently testable

## Stage Design Rules

Each stage must:
- Be completable in focused work (not weeks of effort)
- Compile and pass tests when done
- Provide demonstrable, testable functionality
- Build on previous stages

## Output Format

```
## Requirements
- [Functional requirement 1]
- [Functional requirement 2]
- Constraints: [any limitations]

## Dependencies
- [Existing code/systems affected]

## Risks
- [Risk 1]: Mitigation: [approach]
- [Risk 2]: Mitigation: [approach]

## Implementation Stages

### Stage 1: [Name]
- Goal: [What this achieves]
- Tasks: [Specific work items]
- Done when: [Testable criteria]

### Stage 2: [Name]
...
```

## Rules

- No code in this phase, just planning
- Each stage should be mergeable on its own
- Identify unknowns early
