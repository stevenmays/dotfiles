#!/bin/bash
# PreToolUse hook: block destructive git commands.
command -v jq >/dev/null || exit 0

cmd=$(jq -r '.tool_input.command // ""')

# --force(\s|$) deliberately does not match --force-with-lease
if echo "$cmd" | grep -qE 'git[[:space:]]+push[[:space:]]+.*--force([[:space:]]|$)|git[[:space:]]+push[[:space:]]+(.*[[:space:]])?-f([[:space:]]|$)|git[[:space:]]+reset[[:space:]]+--hard|git[[:space:]]+clean[[:space:]]+-f|git[[:space:]]+branch[[:space:]]+-D'; then
  cat >&2 <<'EOF'
Destructive git command blocked - these can cause data loss.
Alternatives:
  git push --force / -f   -> git push --force-with-lease
  git reset --hard        -> git stash (save changes first)
  git clean -f            -> git clean -n (dry run first)
  git branch -D           -> git branch -d (respects merge check)
EOF
  exit 2
fi
exit 0
