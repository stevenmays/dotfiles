---
name: typescript-patterns
description: Best practices for TypeScript types, interfaces, assertions, and type safety. Use when writing or reviewing TypeScript code.
---

# TypeScript Patterns Skill

Best practices for types, interfaces, assertions, and type safety.

## Type Inference Over Explicit Returns
```typescript
// ✅ Inferred return type
function calculateTotal(items: OrderItem[]) {
    return items.reduce((sum, item) => sum + item.price, 0);
}

// ❌ Explicit return type
function calculateTotal(items: OrderItem[]): number {
    return items.reduce((sum, item) => sum + item.price, 0);
}
```

**Why:** Inference catches implicit type coercion bugs.

## Runtime Type Assertions

Never hard cast from `JSON.parse`. Validate at runtime.
```typescript
// ❌ Hard cast
const value: MyType = JSON.parse(message);

// ✅ Runtime assertion
function isMyType(value: unknown): value is MyType {
    return typeof value === 'object' &&
        value !== null &&
        typeof (<MyType>value).prop === 'string';
}

const value = JSON.parse(message);
assert(isMyType(value), 'Invalid message format');
```

## Type Assertion Functions
```typescript
// Parameter: 'value' with 'unknown' type
// Always return boolean, never throw
function isStrategy(value: unknown): value is Strategy {
    return typeof value === 'object' &&
        value !== null &&
        typeof (<Strategy>value).name === 'string';
}

// Use with assert
assert(isStrategy(value), 'Value is not a valid Strategy');
```

## Interfaces vs Types
```typescript
// Interface for module-scope object types
export interface Product {
    id: string;
    name: string;
    price: number;
}

// Type for local function-scoped types
function validate(input: unknown) {
    type Result = { errors: string[]; valid: boolean };
    const output: Result = { errors: [], valid: true };
    // ...
}

// Type for unions
type Status = 'pending' | 'active' | 'inactive';
```

## Casting Syntax
```typescript
// ✅ Angle bracket syntax
const x = <number>y;
const config = <ConfigType>JSON.parse(json);

// ❌ 'as' syntax
const x = y as number;
```

## Interface Conventions

- No `I` prefix or `Data` suffix
- Properties in alphabetical order
- Think of interfaces as nouns or adjectives (Shippable, Refundable)
- When extending, inherit ALL properties (no `Omit`)
```typescript
// Adjective interfaces
interface Shippable {
    shipping_address: string;
    shipping_cost: number;
}

// Concrete interface
interface Order extends Shippable {
    id: string;
    total: number;
}
```

## Enums

Use explicit values. Prefer union types for small sets.
```typescript
// ✅ Explicit string enum (4+ values)
export enum TenantModel {
    USER = 'user',
    ORGANIZATION = 'organization',
    EMPLOYER = 'employer'
}

// ✅ Union type (2-3 values)
type Status = 'active' | 'inactive';

// Validate with Object.values
if (!Object.values(AttributionModel).includes(model)) {
    throw new Error('Invalid model');
}
```

## Iteration
```typescript
// ✅ for...of loop
for (const item of items) {
    processItem(item);
}

// ❌ forEach
items.forEach((item) => {
    processItem(item);
});
```

**Why:** `for...of` works with `break`, `continue`, `return`, `await`, and has better debugging/stack traces.

Use `map`/`filter`/`reduce` for transformations, not side effects.

## Import Style
```typescript
// ✅ Namespace imports
import * as mongodb from 'mongodb';
import * as Types from './types/index.js';

// ❌ Default imports
import MongoDB from 'mongodb';
```

## Organization

- Keep types with related code (not in `types/` directories)
- Only export types that are part of public API
- Use `ReturnType` and `Parameters` to access private types