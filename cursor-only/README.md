# Cursor AI Configuration

Configuration files for Cursor without Claude Code.

## Structure

```
(after renaming dot-cursor to .cursor)
├── .cursor/
│   ├── rules/
│   │   ├── coding-guidelines.mdc   # Core patterns (always applied)
│   │   ├── typescript-patterns.mdc # TS conventions (*.ts, *.tsx)
│   │   └── serverless-aws.mdc      # AWS Lambda patterns (handlers/, lib/)
│   └── prompts/
│       ├── review-diff.md          # Review branch for AI slop
│       ├── fix-types.md            # Fix TS errors without `any`
│       └── simplify.md             # Reduce complexity
├── USER-RULES.txt                  # Content for Cursor Settings → Rules
└── README.md
```

## Setup

### Step 1: User Rules (Global)

1. Open Cursor Settings (`Cmd+Shift+P` → "Cursor Settings" or `Cmd+,`)
2. Go to **Rules** section
3. Paste the content from `USER-RULES.txt` into the User Rules text area

These rules apply to ALL projects globally.

### Step 2: Project Rules

Copy `dot-cursor` to your project and rename:

```bash
cp -r /path/to/dot-cursor /your/project/
mv /your/project/dot-cursor /your/project/.cursor
```

Or symlink for shared config:

```bash
ln -s /path/to/dot-cursor /your/project/.cursor
```

### Step 3: Customize for Your Project

Edit the `globs` patterns in each `.mdc` file to match your project structure:

```yaml
---
description: AWS Lambda patterns
globs: ["src/handlers/**", "src/lib/**"]  # ← adjust these
alwaysApply: false
---
```

## Rule Types

| File | Type | When Applied |
|------|------|--------------|
| `coding-guidelines.mdc` | `alwaysApply: true` | Every conversation |
| `typescript-patterns.mdc` | Auto-attached | When *.ts/*.tsx files referenced |
| `serverless-aws.mdc` | Auto-attached | When handlers/lib files referenced |

## Using Prompts

Prompts are available as slash commands. Type `/` in chat to see available prompts:

- `/review-diff` - Check branch for AI-generated patterns
- `/fix-types` - Fix TypeScript errors properly
- `/simplify` - Reduce code complexity

## Customization

### Adding New Rules

Create new `.mdc` files in `.cursor/rules/`:

```yaml
---
description: Your rule description
globs: ["pattern/**"]
alwaysApply: false
---

# Rule Title

Your rule content...
```

### Adding New Prompts

Create new `.md` files in `.cursor/prompts/`.

### Rule Precedence

1. User Rules (global, always first)
2. `alwaysApply: true` rules
3. Auto-attached rules (based on file globs)
4. Manually invoked rules

## Without Serverless

If your project isn't serverless AWS, delete `serverless-aws.mdc` or change its globs to not match any files.
