#!/bin/bash
# Sync Claude Code config from dotfiles to ~/.claude

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Syncing Claude Code config..."

# Commands (add custom- prefix)
echo "  Commands..."
for f in "$SCRIPT_DIR"/commands/*.md; do
  [ -f "$f" ] || continue
  cp "$f" ~/.claude/commands/custom-"$(basename "$f")"
done

# Hooks (direct copy)
echo "  Hooks..."
cp -r "$SCRIPT_DIR"/hooks/* ~/.claude/hooks/ 2>/dev/null || true

# Skills (direct copy)
echo "  Skills..."
for skill in "$SCRIPT_DIR"/skills/*/; do
  [ -d "$skill" ] || continue
  cp -r "$skill" ~/.claude/skills/
done

echo "Done."
