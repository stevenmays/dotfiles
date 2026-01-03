# Scratchpad

Track current work for session continuity. Update `.claude/scratchpad.md` in the repo.

## When to Use

- Starting a multi-session task
- Before ending a session with incomplete work
- When context compaction is imminent (long sessions)

## Output Location

`.claude/scratchpad.md` (in current repo, gitignored)

## Template

```markdown
# Scratchpad

**Branch**: `feature/xyz`
**Last Updated**: YYYY-MM-DD HH:MM

## Current Task
[One-line description of what you're working on]

## Progress
- [x] Completed step
- [ ] In progress step
- [ ] Pending step

## Files Changed
| File | Change |
|------|--------|
| `src/foo.ts` | Added validation logic |
| `src/bar.ts` | Fixed null check |

## Blockers / Open Questions
- [Any issues preventing progress]

## Next Steps
1. [Immediate next action]
2. [Following action]

## Notes
[Anything important to remember across sessions]
```

## Rules

- Update before ending session
- Keep it brief — this is a working doc, not documentation
- Delete completed items, don't accumulate history
- If task is done, delete the scratchpad
