#!/bin/bash
# Sync Claude Code config from dotfiles to ~/.claude

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Syncing Claude Code config..."

# Initialize counters
commands_count=0
hooks_count=0
skills_count=0

# --- Cleanup legacy prefixes from previous sync approaches ---
echo "  Cleaning legacy prefixes..."
rm -f "$CLAUDE_DIR"/commands/custom-*.md
rm -f "$CLAUDE_DIR"/commands/cmd-*.md
for d in "$CLAUDE_DIR"/skills/sk-*/; do
  [ -d "$d" ] && rm -rf "$d"
done

# Clean orphaned scripts directory (not a skill)
rm -rf "$CLAUDE_DIR/skills/scripts"

# --- Commands (direct copy, no prefix) ---
echo "  Commands..."
for f in "$SCRIPT_DIR"/commands/*.md; do
  [ -f "$f" ] || continue
  cp "$f" "$CLAUDE_DIR/commands/$(basename "$f")"
  ((commands_count++))
done

# --- Hooks (direct copy) ---
echo "  Hooks..."
for f in "$SCRIPT_DIR"/hooks/*.md; do
  [ -f "$f" ] || continue
  cp "$f" "$CLAUDE_DIR/hooks/$(basename "$f")"
  ((hooks_count++))
done

# --- Skills (direct copy, skip symlinks) ---
echo "  Skills..."
for skill in "$SCRIPT_DIR"/skills/*/; do
  [ -d "$skill" ] || continue
  skill_name=$(basename "$skill")
  target="$CLAUDE_DIR/skills/$skill_name"

  # Skip if target is a symlink (managed by marketplace, not dotfiles)
  if [ -L "$target" ]; then
    echo "    Skipping $skill_name (marketplace symlink)"
    continue
  fi

  cp -r "$skill" "$target"
  ((skills_count++))
done

# --- Settings ---
echo "  Settings..."
cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"

echo ""
echo "Sync complete:"
echo "  - Commands: $commands_count"
echo "  - Hooks:    $hooks_count"
echo "  - Skills:   $skills_count"
echo "  - Settings: synced"
echo ""
echo "Start a new Claude session to pick up changes."
