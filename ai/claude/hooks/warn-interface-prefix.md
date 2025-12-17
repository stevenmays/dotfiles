---
name: warn-interface-prefix
enabled: true
event: file
pattern: "interface I[A-Z]\\w+"
glob: "*.ts"
action: warn
---

**`I` prefix on interface detected** - Drop the prefix.

```typescript
// Preferred
interface User { ... }

// Avoid
interface IUser { ... }
```

Also avoid `Data` suffix (`UserData` → `User`).
