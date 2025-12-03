# AI Coding Assistant Dotfiles

Configuration files for Claude Code and Cursor AI assistants.

## IMPORTANT: Rename After Extracting

Rename the directories to add the dot prefix:
```bash
mv dot-claude .claude
mv dot-cursor .cursor
```

## Structure

```
(after renaming)
├── .claude/
│   ├── CLAUDE.md              # Main rules (both tools read this)
│   ├── commands/
│   │   ├── review-diff.md     # Review branch for AI slop
│   │   ├── fix-types.md       # Fix TypeScript errors properly
│   │   └── simplify.md        # Simplify complex code
│   └── skills/
│       └── serverless-aws/
│           └── SKILL.md       # Serverless patterns (Claude Code only)
├── .cursor/
│   ├── rules/
│   │   └── serverless-aws.mdc # Serverless patterns (Cursor only)
│   └── user-rules.txt         # Global Cursor preferences
└── README.md
```

## Which Tool Reads What

| File | Claude Code | Cursor |
|------|-------------|--------|
| `.claude/CLAUDE.md` | ✅ | ✅ (with import setting) |
| `.claude/commands/*.md` | ✅ | ✅ (with import setting) |
| `.claude/skills/*/SKILL.md` | ✅ | ❌ |
| `.cursor/rules/*.mdc` | ❌ | ✅ |
| `.cursor/user-rules.txt` | ❌ | ✅ |

## Setup

### Cursor Import Settings

Enable in Cursor Settings → Rules and Commands:
- ✅ Include CLAUDE.md in context
- ✅ Import Claude Commands

### Option 1: Symlink to Home Directory (Claude Code global)

```bash
# For Claude Code global settings
ln -s /path/to/dotfiles/.claude ~/.claude
```

### Option 2: Copy to Project

```bash
# Copy to project root
cp -r /path/to/dotfiles/.claude /your/project/
cp -r /path/to/dotfiles/.cursor /your/project/
```

### Option 3: Symlink to Project

```bash
cd /your/project
ln -s /path/to/dotfiles/.claude .claude
ln -s /path/to/dotfiles/.cursor .cursor
```

## Usage

### Commands

In Claude Code or Cursor, use slash commands:
- `/review-diff` - Check branch for AI-generated code patterns
- `/fix-types` - Fix TypeScript errors without using `any`
- `/simplify` - Reduce code complexity

### Serverless Projects

For AWS Lambda projects, the serverless patterns are:
- **Claude Code**: Automatically loaded from `.claude/skills/serverless-aws/SKILL.md`
- **Cursor**: Copy `.cursor/rules/serverless-aws.mdc` to the project, or it auto-attaches based on globs

## Customization

### Adding Project-Specific Rules

Create `.claude/CLAUDE.local.md` in your project for project-specific overrides (both tools read this).

### Adding New Commands

Add `.md` files to `.claude/commands/` - both tools will pick them up.

### Adding Cursor-Only Rules

Add `.mdc` files to `.cursor/rules/` with appropriate globs for file-pattern matching.
