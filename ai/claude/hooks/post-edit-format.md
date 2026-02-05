---
name: post-edit-format
enabled: true
event: PostToolUse
tool: Edit
action: run
command: |
  if [ -f package.json ] && command -v npx >/dev/null; then
    npx prettier --write "$FILE_PATH" 2>/dev/null || true
  fi
---

Auto-formats files after edits using Prettier when available.

Runs silently - only formats if:
- A `package.json` exists in the project
- `npx` is available
- Prettier is installed (fails gracefully if not)
