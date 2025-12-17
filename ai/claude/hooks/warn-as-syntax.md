---
name: warn-as-syntax
enabled: true
event: file
pattern: "\\s+as\\s+(?!const\\b)[A-Z]\\w+"
glob: "*.ts"
action: warn
---

**`as Type` syntax detected** - Use angle bracket syntax instead.

```typescript
// Preferred
const x = <Type>value;

// Avoid
const x = value as Type;
```

Exception: `as const` is fine.
