---
name: block-hardcoded-secrets
enabled: true
event: file
pattern: "(api[_-]?key|secret|password|token|credential)\\s*[:=]\\s*['\"][^'\"]{8,}['\"]"
glob: "*.ts"
action: block
---

**Hardcoded secret detected** - Use environment variables instead.

```typescript
// Blocked
const apiKey = 'sk-abc123...';

// Preferred
const apiKey = process.env.API_KEY;
```

Never commit secrets to source control.
