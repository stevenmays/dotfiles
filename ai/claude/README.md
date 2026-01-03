# Claude Configuration

Personal Claude Code configuration synced across projects via `Makefile.repo`.

## Quick Start

```bash
# Copy Makefile.repo to your project
cp ~/Git/dotfiles/ai/claude/Makefile.repo ./Makefile.claude

# Sync all config
make -f Makefile.claude sync
```

## Structure

```
ai/claude/
├── CLAUDE.md              # Project guidelines template (synced to repo root)
├── Makefile.repo          # Sync makefile (copy to target repos)
├── README.md              # This file
├── .agent/                # Reference documentation (synced to .claude/.agent/)
│   ├── anti-patterns.md
│   ├── bug-investigation.md
│   ├── code-review-checklist.md
│   ├── coding-patterns.md
│   ├── error-handling.md
│   ├── testing-patterns.md
│   └── writing/
│       └── writing-style-examples.md
├── commands/              # Slash commands (synced with custom- prefix)
│   ├── analyze-bug.md     → /custom-analyze-bug
│   ├── fix-types.md       → /custom-fix-types
│   ├── plan-feature.md    → /custom-plan-feature
│   ├── review-diff.md     → /custom-review-diff
│   ├── simplify.md        → /custom-simplify
│   └── take-notes.md      → /custom-take-notes
├── hooks/                 # Hookify rules (synced to ~/.claude/hooks/)
│   ├── block-as-any.md
│   ├── block-hardcoded-secrets.md
│   ├── warn-any-type.md
│   ├── warn-as-syntax.md
│   ├── warn-debug-code.md
│   ├── warn-default-import.md
│   ├── warn-foreach.md
│   └── warn-interface-prefix.md
└── skills/                # Domain skills (synced to ~/.claude/skills/)
    ├── code-review/
    ├── serverless-aws/
    ├── typescript-patterns/
    └── writing-style/
```

## Sync Destinations

| Source | Destination | Notes |
|--------|-------------|-------|
| `CLAUDE.md` | `./CLAUDE.md` | Prompts before overwrite |
| `.agent/` | `./.claude/.agent/` | Per-repo |
| `commands/` | `~/.claude/commands/` | Prefixed with `custom-` |
| `skills/` | `~/.claude/skills/` | User-global |
| `hooks/` | `~/.claude/hooks/` | User-global |

## Makefile Commands

```bash
make sync        # Sync all (prompts before replacing CLAUDE.md)
make sync-force  # Sync all (overwrites CLAUDE.md)
make dry-run     # Preview changes
make clean       # Remove repo-specific files
make help        # Show available commands
```

## Installed Plugins

These plugins complement the custom commands:

| Plugin | Commands | Purpose |
|--------|----------|---------|
| **hookify** | — | Runtime enforcement of TypeScript patterns |
| **pr-review-toolkit** | — | 6 specialized review agents |
| **commit-commands** | `/commit`, `/commit-push-pr`, `/clean_gone` | Git workflow |
| **feature-dev** | `/feature-dev` | 7-phase feature development |

## Custom Commands

| Command | Purpose |
|---------|---------|
| `/custom-analyze-bug` | Systematic root cause analysis |
| `/custom-fix-types` | Fix TypeScript errors without `any` |
| `/custom-plan-feature` | Break features into stages |
| `/custom-review-diff` | Quick diff review for anti-patterns |
| `/custom-simplify` | Simplify code, preserve behavior |
| `/custom-take-notes` | Document technical discoveries |
| `/custom-scratchpad` | Track work for session continuity |

## Hooks (Hookify)

| Hook | Action | Trigger |
|------|--------|---------|
| `warn-any-type` | warn | `: any`, `<any>`, `any[]` |
| `block-as-any` | **block** | `as any` casts |
| `warn-as-syntax` | warn | `as Type` (use `<Type>`) |
| `warn-foreach` | warn | `.forEach()` (use `for...of`) |
| `warn-interface-prefix` | warn | `interface IFoo` |
| `warn-debug-code` | warn | `console.log`, `debugger` |
| `warn-default-import` | warn | Default imports |
| `block-hardcoded-secrets` | **block** | Hardcoded API keys/passwords |

## Skills

| Skill | When to Use |
|-------|-------------|
| `typescript-patterns` | Writing/reviewing TypeScript |
| `code-review` | Removing AI-generated anti-patterns |
| `serverless-aws` | Lambda/DynamoDB/SQS patterns |
| `writing-style` | Essays, blog posts, technical articles |
