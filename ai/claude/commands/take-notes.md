# Take Notes

Capture complex technical discoveries for future reference.

## When to Use

After you've:
- Spent 30+ minutes understanding non-obvious system behavior
- Debugged something complex through extensive exploration
- Discovered architectural patterns not documented elsewhere
- Found integration gotchas between multiple components

## Skip If

- Straightforward bug fix
- Well-documented existing functionality
- Obvious implementation

## Output Location

`.claude/notes/{feature}.md` (in current repo)

Use kebab-case for feature name.

## Template

```markdown
# [Feature/Discovery Name]

## Context
[Why this matters, when you'd need this knowledge]

## Key Findings
- [Non-obvious behavior 1]
- [Non-obvious behavior 2]

## Gotchas
- [Thing that will bite you if you don't know]

## Code Examples
[If applicable, minimal examples showing the pattern]

## References
- [Link to relevant source files]
- [Link to related docs]
```

## Rules

- Focus on what's NOT obvious from reading the code
- Include the "why" not just the "what"
- Make it actionable for future-you
- Run `qmd update` after writing
