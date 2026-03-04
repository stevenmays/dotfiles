# Remember

Quick capture of a decision, gotcha, or piece of context.

## When to Use

- A decision was made that future-Claude should know about
- A gotcha or non-obvious behavior was discovered
- Context that would be lost between sessions

## Output Location

`.claude/notes/remember.md` (append, never overwrite)

## Format

Append:

```
## YYYY-MM-DD: [one-line summary]

[1-5 lines of context. Why this matters.]
```

## Rules

- Create `.claude/notes/` directory if it doesn't exist
- Append to file, never replace
- Keep entries under 5 lines
- Run `qmd update` after writing
