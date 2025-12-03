# AI Assistant Dotfiles

Configuration files for Claude Code and Cursor AI assistants.

## Choose Your Setup

| Folder | When to Use |
|--------|-------------|
| [`claude-and-cursor/`](claude-and-cursor/) | You have both Claude Code and Cursor |
| [`cursor-only/`](cursor-only/) | You only have Cursor |

Each folder is self-contained with its own README and setup instructions.

## Quick Start

### Claude Code + Cursor

```bash
cd /your/project
cp -r /path/to/dotfiles/claude-and-cursor/dot-claude .claude
cp -r /path/to/dotfiles/claude-and-cursor/dot-cursor .cursor
```

### Cursor Only

```bash
cd /your/project
cp -r /path/to/dotfiles/cursor-only/dot-cursor .cursor
# Also paste USER-RULES.txt into Cursor Settings → Rules
```

## What's Included

### Commands

| Command | Description |
|---------|-------------|
| `/fix-types` | Fix TypeScript errors without using `any` |
| `/review-diff` | Review branch for AI-generated anti-patterns |
| `/simplify` | Simplify code while keeping behavior identical |

### Rules/Skills

| Topic | Description |
|-------|-------------|
| Coding Guidelines | Core patterns: simplicity, early returns, error handling |
| TypeScript Patterns | Type inference, assertions, interfaces, casting |
| Serverless AWS | Lambda handlers, secrets caching, SQS, cold starts |
| Code Review | Remove AI slop: excessive comments, defensive checks, `as any` |

## Coding Philosophy

- Simplicity over cleverness
- Functions under 20 lines, single responsibility
- Early returns over nested conditionals
- Type guards over `any` casts
- Match existing file patterns
