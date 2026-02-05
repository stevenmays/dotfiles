#!/bin/bash
# Sync Claude Code config from dotfiles to ~/.claude

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Syncing Claude Code config..."

# Initialize counters
commands_count=0
hooks_count=0
skills_count=0

# Clean old prefixed items to avoid duplicates
rm -f ~/.claude/commands/custom-*.md
rm -rf ~/.claude/skills/verify-app
rm -rf ~/.claude/skills/code-architect

# Commands (add cmd- prefix)
echo "  Commands..."
for f in "$SCRIPT_DIR"/commands/*.md; do
  [ -f "$f" ] || continue
  cp "$f" ~/.claude/commands/cmd-"$(basename "$f")"
  ((commands_count++))
done

# Hooks (direct copy)
echo "  Hooks..."
for f in "$SCRIPT_DIR"/hooks/*.md; do
  [ -f "$f" ] || continue
  cp "$f" ~/.claude/hooks/
  ((hooks_count++))
done

# Skills (add sk- prefix)
echo "  Skills..."
for skill in "$SCRIPT_DIR"/skills/*/; do
  [ -d "$skill" ] || continue
  skill_name=$(basename "$skill")
  cp -r "$skill" ~/.claude/skills/sk-"$skill_name"
  ((skills_count++))
done

echo ""
echo "Sync complete:"
echo "  - Commands: $commands_count"
echo "  - Hooks:    $hooks_count"
echo "  - Skills:   $skills_count"
echo ""
echo "Start a new Claude session to pick up changes."
