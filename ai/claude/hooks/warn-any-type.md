---
name: warn-any-type
enabled: true
event: file
pattern: ": any\\b|<any>|any\\[\\]"
glob: "*.ts"
action: warn
---

**`any` type detected** - Use proper types, `unknown` with type guards, or generics instead.

See: `.claude/skills/typescript-patterns/SKILL.md`
