# Fix Types

Fix TypeScript type errors in this file without using `any` or `as any`.

## Strategies

1. Add type guards for runtime validation
2. Use generics where appropriate
3. Fix interface definitions
4. Use `unknown` and narrow with type guards
5. Use angle bracket syntax: `<Type>value`

## Rules

- Do not suppress errors with casts
- Fix the underlying type issue
- If a type is truly unknown at compile time, use `unknown` with a type guard

## Example

```typescript
// Bad: Suppressing with any
const result = (data as any).value;

// Good: Type guard
function hasValue(obj: unknown): obj is { value: string } {
    return typeof obj === 'object' && obj !== null && 'value' in obj;
}

if (hasValue(data)) {
    const result = data.value;
}

// Good: Angle bracket cast when type is known
const config = <AppConfig>JSON.parse(configJson);
```
