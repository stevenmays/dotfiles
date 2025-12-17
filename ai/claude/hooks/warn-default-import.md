---
name: warn-default-import
enabled: true
event: file
pattern: "^import\\s+[A-Z]\\w+\\s+from\\s+['\"]"
glob: "*.ts"
action: warn
---

**Default import detected** - Use namespace imports instead.

```typescript
// Preferred
import * as mongodb from 'mongodb';

// Avoid
import MongoDB from 'mongodb';
```

Exception: React and framework-specific default exports.
