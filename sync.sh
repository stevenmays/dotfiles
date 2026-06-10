#!/bin/bash
# Sync personal settings to ~/.claude and clean up artifacts from the old
# copy-based sync. Commands, skills, agents, and hooks are no longer copied —
# they ship via the plugin (/plugin install mays-tools@dotfiles).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Cleaning up files installed by the old copy-based sync..."

rm -f "$CLAUDE_DIR"/commands/{custom-,cmd-}*.md
rm -f "$CLAUDE_DIR"/commands/{cleanup,code-review,commit-push-pr,extreme-code-quality-review,fix-merge-conflict,quick-commit,remember,repo-init,scratchpad,take-notes,test-and-fix}.md
rm -f "$CLAUDE_DIR"/hooks/{block-destructive-git,block-hardcoded-secrets,post-edit-format}.md
rm -f "$CLAUDE_DIR"/agents/extreme-code-quality-review.md

for name in code-architect code-review extreme-code-quality-review gemini-image-generator serverless-aws verify-app writing-style; do
  target="$CLAUDE_DIR/skills/$name"
  # Symlinks are marketplace-managed, not ours
  [ -d "$target" ] && [ ! -L "$target" ] && rm -rf "$target"
done
rm -rf "$CLAUDE_DIR/skills/scripts"

echo "Syncing settings..."
cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"

echo ""
echo "Done. Install the plugin from within Claude Code if you haven't:"
echo "  /plugin marketplace add stevenmays/dotfiles"
echo "  /plugin install mays-tools@dotfiles"
