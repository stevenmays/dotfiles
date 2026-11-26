# Dotfiles Makefile - Claude Code plugin management

.PHONY: help list check

help:
	@echo "Claude Code plugin (mays)"
	@echo ""
	@echo "Commands:"
	@echo "  make list    - List plugin contents (commands, skills, agents, hooks)"
	@echo "  make check   - Verify plugin structure"
	@echo ""
	@echo "Install (inside Claude Code):"
	@echo "  /plugin marketplace add stevenmays/dotfiles"
	@echo "  /plugin install mays@dotfiles"
	@echo ""
	@echo "Install the skills alone, into any agent:"
	@echo "  npx skills add stevenmays/dotfiles"

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
	@python3 scripts/check_plugins.py
	@python3 -m unittest discover -s scripts/tests -q
