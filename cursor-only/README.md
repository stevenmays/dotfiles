# Cursor Configuration (No Claude Code)

Use this when you only have Cursor in your environment.

## Structure

```
dot-cursor/                    → rename to .cursor
├── rules/
│   ├── coding-guidelines.mdc  # Always applied
│   ├── serverless-aws.mdc     # Applied to handlers/, lib/
│   └── typescript-patterns.mdc # Applied to *.ts, *.tsx
└── prompts/
    ├── fix-types.md           # /fix-types - Fix TS errors without any
    ├── review-diff.md         # /review-diff - Review for AI patterns
    └── simplify.md            # /simplify - Reduce complexity

USER-RULES.txt                 # Paste into Cursor Settings → Rules
```

## Setup

### 1. Set User Rules (global, one-time)

1. Open Cursor Settings (`Cmd+Shift+P` → "Cursor Settings")
2. Go to **Rules** section
3. Paste content from `USER-RULES.txt` into the User Rules text area

These apply to all projects.

### 2. Copy to your project

```bash
cp -r dot-cursor /your/project/.cursor
```

## Commands

Type `/` in Cursor chat to use:

- `/fix-types` - Fix TypeScript errors using type guards, not `any`
- `/review-diff` - Review branch diff, remove AI anti-patterns
- `/simplify` - Simplify code while keeping behavior identical

## Rules

| Rule | When Applied |
|------|--------------|
| `coding-guidelines.mdc` | Every conversation (`alwaysApply: true`) |
| `typescript-patterns.mdc` | When *.ts/*.tsx files are referenced |
| `serverless-aws.mdc` | When handlers/ or lib/ files are referenced |

## Customization

### Edit glob patterns

Adjust the `globs` field in `.cursor/rules/*.mdc` to match your project:

```yaml
---
description: AWS Lambda patterns
globs: ["src/handlers/**", "src/lib/**"]
alwaysApply: false
---
```

### Remove serverless rules

If not using AWS Lambda, delete `serverless-aws.mdc` or change its globs to not match any files.

### Add new rules

Create `.mdc` files in `.cursor/rules/`:

```yaml
---
description: Your rule description
globs: ["pattern/**"]
alwaysApply: false
---

# Rule content here
```
