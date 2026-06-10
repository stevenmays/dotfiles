#!/bin/bash
# PreToolUse hook: block edits that introduce hardcoded secrets.
command -v jq >/dev/null || exit 0

input=$(cat)
file=$(echo "$input" | jq -r '.tool_input.file_path // ""')

case "$file" in
  *.ts|*.tsx|*.js|*.jsx|*.py|*.rb|*.go|*.java|*.rs|*.yaml|*.yml|*.toml) ;;
  *) exit 0 ;;
esac

content=$(echo "$input" | jq -r '.tool_input.content // .tool_input.new_string // ""')

if echo "$content" | grep -qiE "(api[_-]?key|secret|password|token|credential)[[:space:]]*[:=][[:space:]]*['\"][^'\"]{8,}['\"]"; then
  echo "Hardcoded secret detected - use environment variables instead (e.g. process.env.API_KEY). Never commit secrets to source control." >&2
  exit 2
fi
exit 0
