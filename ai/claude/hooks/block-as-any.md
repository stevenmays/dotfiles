---
name: block-as-any
enabled: true
event: file
pattern: "as any\\b"
glob: "*.ts"
action: block
---

**`as any` cast blocked** - Fix the type instead of escaping the type system.

Options:
1. Add proper type definitions
2. Use a type guard for runtime validation
3. Use `unknown` with narrowing

Never silence type errors with `as any`.
