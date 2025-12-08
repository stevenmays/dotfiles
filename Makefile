# Dotfiles Makefile - Manage Claude AI configuration files
# Source: ~/Git/dotfiles/ai/claude

CLAUDE_DIR := $(HOME)/Git/dotfiles/ai/claude

.PHONY: help list check

help:
	@echo "Claude Dotfiles Management"
	@echo ""
	@echo "Commands:"
	@echo "  make list    - List all Claude files (commands, skills, agent_docs)"
	@echo "  make check   - Verify all expected files exist"
	@echo ""
	@echo "To sync these files TO another repo:"
	@echo "  1. Copy ai/claude/Makefile.repo to your target repo as Makefile.claude"
	@echo "  2. cd /path/to/repo && make -f Makefile.claude sync"

list:
	@echo "=== CLAUDE.md ==="
	@ls -la $(CLAUDE_DIR)/CLAUDE.md 2>/dev/null || echo "  (not found)"
	@echo ""
	@echo "=== Commands ==="
	@ls -1 $(CLAUDE_DIR)/commands/*.md 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "=== Skills ==="
	@find $(CLAUDE_DIR)/skills -name "SKILL.md" 2>/dev/null || echo "  (none)"
	@echo ""
	@echo "=== Agent Docs ==="
	@ls -1 $(CLAUDE_DIR)/.agent_docs/*.md 2>/dev/null || echo "  (none)"

check:
	@echo "Checking Claude files..."
	@test -f $(CLAUDE_DIR)/CLAUDE.md && echo "✓ CLAUDE.md" || echo "✗ CLAUDE.md missing"
	@test -d $(CLAUDE_DIR)/commands && echo "✓ commands/" || echo "✗ commands/ missing"
	@test -d $(CLAUDE_DIR)/skills && echo "✓ skills/" || echo "✗ skills/ missing"
	@test -d $(CLAUDE_DIR)/.agent_docs && echo "✓ .agent_docs/" || echo "✗ .agent_docs/ missing"
