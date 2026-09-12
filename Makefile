# Dotfiles Makefile - Claude Code and Codex plugin management

.PHONY: help list check sync-codex

help:
	@echo "Claude Code and Codex plugin (mays)"
	@echo ""
	@echo "Commands:"
	@echo "  make list    - List plugin contents (commands, skills, agents, hooks)"
	@echo "  make check   - Verify plugin structure"
	@echo "  make sync-codex - Refresh shared Codex resources"
	@echo ""
	@echo "Install (inside Claude Code):"
	@echo "  /plugin marketplace add stevenmays/dotfiles"
	@echo "  /plugin install mays@dotfiles"
	@echo ""
	@echo "Install (Codex CLI):"
	@echo "  codex plugin marketplace add stevenmays/dotfiles"
	@echo "  codex plugin add mays@dotfiles"

list:
	@echo "=== Commands ==="
	@ls -1 commands/*.md 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "=== Skills ==="
	@find skills -name "SKILL.md" 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "=== Codex Skills ==="
	@find codex/skills -name "SKILL.md"
	@echo ""
	@echo "=== Agents ==="
	@ls -1 agents/*.md 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "=== Hooks ==="
	@ls -1 hooks/scripts/*.sh 2>/dev/null || echo "  (none)"

check:
	@python3 scripts/check_plugins.py
	@python3 -m unittest discover -s scripts/tests -q

sync-codex:
	@python3 scripts/sync_codex_resources.py
