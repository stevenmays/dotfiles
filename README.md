# Claude Code Tools

A collection of configurations, skills, hooks, and commands for AI coding assistants—primarily Claude Code and Cursor.

```
ai/
├── claude/          # Claude Code configuration
│   ├── .agent_docs/ # Reference documentation
│   ├── commands/    # Workflow shortcuts (/analyze-bug, /simplify, etc.)
│   ├── hooks/       # Convention enforcement rules
│   ├── skills/      # Domain expertise (TypeScript, AWS, etc.)
│   └── install.sh   # Setup script
└── cursor/          # Cursor configuration
    ├── rules/       # Coding guidelines and patterns
    └── prompts/     # Reusable prompts
```

Based on [Steven Mays's article on optimizing Claude Code](https://mays.co/optimizing-claude-code).

## Customization Layers

Claude Code's customization system has multiple layers that work together:

| Layer | Purpose | Location |
|-------|---------|----------|
| **Settings** | Global behavior (thinking, tokens, plugins) | `~/.claude/settings.json` |
| **CLAUDE.md** | Project context (commands, structure, principles) | Project root |
| **Skills** | Domain expertise applied automatically | `~/.claude/skills/` |
| **Hooks** | Real-time convention enforcement (warn/block) | `~/.claude/hooks/` |
| **Commands** | Workflow shortcuts (`/analyze-bug`, `/simplify`) | `~/.claude/commands/` |
| **Agent Docs** | Reference material loaded on demand | `.claude/agent_docs/` |
| **Plugins** | Extended capabilities | Via `/plugin install` |

### How They Interact

When Claude Code starts a session, it reads your settings, loads relevant skills based on context, and injects CLAUDE.md into its system prompt. Skills *teach* Claude your conventions; hooks *enforce* them in real-time. Commands trigger consistent workflows without lengthy prompts.

The key insight: these layers compound. A skill teaches "prefer `for...of` over `.forEach()`", a hook warns when `.forEach()` is used, and Claude learns to avoid it automatically.

## Settings

```json
{
  "alwaysThinkingEnabled": true,
  "env": {
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "64000"
  }
}
```

- **alwaysThinkingEnabled** — Extended thinking on every response (tradeoff: latency for quality)
- **CLAUDE_CODE_MAX_OUTPUT_TOKENS** — Prevents truncation on large refactors

## Hooks

Hooks catch convention violations in real-time using the **hookify** plugin:

| Hook | Action | What It Catches |
|------|--------|-----------------|
| block-as-any | block | `as any` casts |
| warn-foreach | warn | `.forEach()` (prefer `for...of`) |
| warn-debug-code | warn | `console.log`, `debugger` |
| block-hardcoded-secrets | block | Hardcoded API keys/passwords |

## Commands

| Command | Purpose |
|---------|---------|
| `/analyze-bug` | 6-step root cause analysis |
| `/simplify` | Reduce complexity while preserving behavior |
| `/plan-feature` | Break features into implementable stages |
| `/review-diff` | Review changes against project guidelines |
| `/fix-types` | Fix TypeScript errors systematically |

## Quick Setup

```bash
# Run install script
curl -sL https://raw.githubusercontent.com/stevenmays/dotfiles/master/ai/claude/install.sh | bash

# Then install plugins in Claude Code:
/plugin marketplace add anthropics/claude-code
/plugin install hookify@claude-code-plugins
/plugin install pr-review-toolkit@claude-code-plugins
/plugin install commit-commands@claude-code-plugins
/plugin install feature-dev@claude-code-plugins
```

## Recommended Plugins

| Plugin | Purpose |
|--------|---------|
| **hookify** | Convention enforcement via markdown rules |
| **commit-commands** | `/commit`, `/commit-push-pr`, `/clean_gone` |
| **feature-dev** | 7-phase structured feature development |
| **pr-review-toolkit** | 6 parallel review agents (code, types, tests, comments, errors, simplification) |
| **ast-grep** | Structural code search using AST patterns |
| **dev-browser** | Browser automation for testing web apps |

## Resources

- [Steven Mays's dotfiles](https://github.com/stevenmays/dotfiles/tree/master/ai/claude)
- [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code plugins](https://github.com/anthropics/claude-code)
