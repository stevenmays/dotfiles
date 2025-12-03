# Claude Code + Cursor Configuration

Use this when you have both Claude Code and Cursor in your environment.

## Structure

```
dot-claude/                    → rename to .claude
├── CLAUDE.md                  # Coding guidelines (both tools read this)
├── commands/
│   ├── fix-types.md           # /fix-types - Fix TS errors without any
│   ├── review-diff.md         # /review-diff - Review for AI patterns
│   └── simplify.md            # /simplify - Reduce complexity
└── skills/
    ├── code-review/SKILL.md   # Auto-applied during code review
    ├── serverless-aws/SKILL.md
    └── typescript-patterns/SKILL.md

dot-cursor/                    → rename to .cursor
└── rules/
    ├── coding-guidelines.mdc  # Always applied
    ├── serverless-aws.mdc     # Applied to handlers/, lib/
    └── typescript-patterns.mdc # Applied to *.ts, *.tsx
```

## Setup

### 1. Copy to your project

```bash
cp -r dot-claude /your/project/.claude
cp -r dot-cursor /your/project/.cursor
```

### 2. Enable Cursor imports (one-time)

In Cursor Settings → Rules:
- Enable "Include CLAUDE.md in context"
- Enable "Import Claude Commands"

This lets Cursor read CLAUDE.md and use the same `/fix-types`, `/review-diff`, `/simplify` commands.

## What Each Tool Reads

| File | Claude Code | Cursor |
|------|-------------|--------|
| `.claude/CLAUDE.md` | ✅ | ✅ (with import setting) |
| `.claude/commands/*.md` | ✅ | ✅ (with import setting) |
| `.claude/skills/*/SKILL.md` | ✅ | ❌ |
| `.cursor/rules/*.mdc` | ❌ | ✅ |

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

### Project-specific rules

Create `.claude/CLAUDE.local.md` for project-specific overrides.

### Edit glob patterns

In `.cursor/rules/*.mdc`, adjust the `globs` field to match your project:

```yaml
---
description: AWS Lambda patterns
globs: ["src/handlers/**", "src/lib/**"]
---
```
