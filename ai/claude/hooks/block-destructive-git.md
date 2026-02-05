---
name: block-destructive-git
enabled: true
event: PreToolUse
tool: Bash
pattern: "(git\\s+push\\s+.*--force|git\\s+reset\\s+--hard|git\\s+clean\\s+-f|git\\s+branch\\s+-D)"
action: block
---

**Destructive git command blocked** - These commands can cause data loss.

## Blocked Commands

- `git push --force` - Can overwrite remote history
- `git reset --hard` - Discards uncommitted changes
- `git clean -f` - Deletes untracked files permanently
- `git branch -D` - Force deletes branch without merge check

## Alternatives

```bash
# Instead of push --force, use:
git push --force-with-lease

# Instead of reset --hard, use:
git stash  # Save changes first

# Instead of clean -f, use:
git clean -n  # Dry run first

# Instead of branch -D, use:
git branch -d  # Safe delete (checks merge status)
```

If you truly need these commands, run them manually in your terminal.
