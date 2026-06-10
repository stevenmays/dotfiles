# Dotfiles Makefile - Claude Code plugin management

.PHONY: help list check

help:
	@echo "Claude plugin (mays-tools)"
	@echo ""
	@echo "Commands:"
	@echo "  make list    - List plugin contents (commands, skills, agents, hooks)"
	@echo "  make check   - Verify plugin structure"
	@echo ""
	@echo "Install (inside Claude Code):"
	@echo "  /plugin marketplace add stevenmays/dotfiles"
	@echo "  /plugin install mays-tools@dotfiles"

list:
	@echo "=== Commands ==="
	@ls -1 commands/*.md 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "=== Skills ==="
	@find skills -name "SKILL.md" 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "=== Agents ==="
	@ls -1 agents/*.md 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "=== Hooks ==="
	@ls -1 hooks/scripts/*.sh 2>/dev/null || echo "  (none)"

check:
	@echo "Checking plugin structure..."
	@test -f .claude-plugin/plugin.json && echo "✓ plugin.json" || echo "✗ plugin.json missing"
	@test -f .claude-plugin/marketplace.json && echo "✓ marketplace.json" || echo "✗ marketplace.json missing"
	@test -d commands && echo "✓ commands/" || echo "✗ commands/ missing"
	@test -d skills && echo "✓ skills/" || echo "✗ skills/ missing"
	@test -d agents && echo "✓ agents/" || echo "✗ agents/ missing"
	@test -f hooks/hooks.json && echo "✓ hooks/hooks.json" || echo "✗ hooks/hooks.json missing"
