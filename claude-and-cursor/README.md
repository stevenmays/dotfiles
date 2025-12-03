# Claude Code + Cursor Configuration

Use this when you have both Claude Code and Cursor in your environment.

## Structure

```
dot-claude/                    → rename to .claude
├── CLAUDE.md                  # Lean root file with core principles
├── agent_docs/                # Detailed reference docs (read on demand)
│   ├── coding-patterns.md     # TypeScript patterns with examples
│   ├── anti-patterns.md       # AI-specific mistakes to avoid
│   ├── error-handling.md      # Error handling conventions
│   └── testing-patterns.md    # How to write testable code
├── commands/
│   ├── fix-types.md           # /fix-types - Fix TS errors without any
│   ├── review-diff.md         # /review-diff - Review for AI patterns
│   └── simplify.md            # /simplify - Reduce complexity
└── skills/
    ├── code-review/SKILL.md   # Auto-applied during code review
    ├── serverless-aws/SKILL.md
    └── typescript-patterns/SKILL.md
```

## Setup

### 1. Copy to your project

```bash
cp -r dot-claude /your/project/.claude
```

### 2. Enable Cursor imports (one-time)

In Cursor Settings → Rules:
- Enable "Include CLAUDE.md in context"
- Enable "Import Claude Commands"

This lets Cursor read CLAUDE.md (which references agent_docs/) and use the same `/fix-types`, `/review-diff`, `/simplify` commands.

## What Each Tool Reads

| File | Claude Code | Cursor |
|------|-------------|--------|
| `.claude/CLAUDE.md` | ✅ | ✅ (with import setting) |
| `.claude/agent_docs/*.md` | ✅ (on demand) | ✅ (via CLAUDE.md reference) |
| `.claude/commands/*.md` | ✅ | ✅ (with import setting) |
| `.claude/skills/*/SKILL.md` | ✅ | ❌ |

## Commands

All three commands work in both Claude Code and Cursor:

- `/fix-types` - Fix TypeScript errors using type guards, not `any`
- `/review-diff` - Review branch diff, remove AI anti-patterns
- `/simplify` - Simplify code while keeping behavior identical

## Skills (Claude Code only)

Skills auto-activate based on context:

- **code-review** - Removes excessive comments, defensive checks, `as any` casts
- **serverless-aws** - Lambda handler patterns, secrets caching, SQS processing
- **typescript-patterns** - Type inference, runtime assertions, interface conventions

## Customization

Create `.claude/CLAUDE.local.md` for project-specific overrides.
