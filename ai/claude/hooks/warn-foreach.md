---
name: warn-foreach
enabled: true
event: file
pattern: "\\.forEach\\("
glob: "*.ts"
action: warn
---

**`.forEach()` detected** - Use `for...of` instead.

```typescript
// Preferred
for (const item of items) {
    processItem(item);
}

// Avoid
items.forEach((item) => {
    processItem(item);
});
```

`for...of` works with `break`, `continue`, `return`, `await`, and has better stack traces.

Use `map`/`filter`/`reduce` for transformations, not side effects.
