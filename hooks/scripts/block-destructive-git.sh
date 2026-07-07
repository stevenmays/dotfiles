#!/bin/bash
# PreToolUse hook: block destructive git commands.
command -v jq >/dev/null || exit 0

cmd=$(jq -r '.tool_input.command // ""')

# --force(\s|$) deliberately does not match --force-with-lease.
# Short flags match in any combined order (-f, -df, -xdf); +refspec is the
# force-push spelling that skips --force entirely.
if echo "$cmd" | grep -qE \
  -e 'git[[:space:]]+push[[:space:]]+.*--force([[:space:]]|$)' \
  -e 'git[[:space:]]+push[[:space:]]+(.*[[:space:]])?-[A-Za-z]*f[A-Za-z]*([[:space:]]|$)' \
  -e 'git[[:space:]]+push[[:space:]]+.*[[:space:]]\+[^[:space:]]' \
  -e 'git[[:space:]]+reset[[:space:]]+--hard' \
  -e 'git[[:space:]]+clean[[:space:]]+(.*[[:space:]])?(-[A-Za-z]*f|--force)' \
  -e 'git[[:space:]]+branch[[:space:]]+(.*[[:space:]])?(-[A-Za-z]*D[A-Za-z]*|--delete[[:space:]]+--force|--force[[:space:]]+--delete)'; then
  cat >&2 <<'EOF'
Destructive git command blocked - these can cause data loss.
Alternatives:
  git push --force / -f / +ref -> git push --force-with-lease
  git reset --hard             -> git stash (save changes first)
  git clean -f                 -> git clean -n (dry run first)
  git branch -D                -> git branch -d (respects merge check)
EOF
  exit 2
fi
exit 0
