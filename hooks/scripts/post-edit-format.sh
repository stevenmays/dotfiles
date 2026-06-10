#!/bin/bash
# PostToolUse hook: auto-format edited files with Prettier when the project uses it.
command -v jq >/dev/null || exit 0
command -v npx >/dev/null || exit 0
[ -f package.json ] || exit 0

file=$(jq -r '.tool_input.file_path // ""')
[ -f "$file" ] || exit 0

# --no-install: only format if the project already depends on prettier
npx --no-install prettier --write "$file" 2>/dev/null || true
exit 0
