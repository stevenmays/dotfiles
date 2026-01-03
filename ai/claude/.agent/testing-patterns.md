# Testing Patterns

Read this before writing tests or making code testable.

## Core Principle: Separate I/O from Logic

The key to testable code is separating pure business logic from I/O operations.

```typescript
// Pure function: easy to test
export function calculateDiscount(order: Order): number {
    if (order.total > 100) return order.total * 0.1;
    return 0;
}

// I/O wrapper: calls the pure function
async function processOrder(orderId: string) {
    const order = await fetchOrder(orderId);     // I/O
    const discount = calculateDiscount(order);   // Pure (testable)
    await updateOrder(orderId, { discount });    // I/O
}
```

Test the pure function directly:

```typescript
describe('calculateDiscount', () => {
    it('returns 10% for orders over 100', () => {
        const order = { total: 150 };
        expect(calculateDiscount(order)).toBe(15);
    });

    it('returns 0 for orders under 100', () => {
        const order = { total: 50 };
        expect(calculateDiscount(order)).toBe(0);
    });
});
```

## Design for Testability

**Export functions that need testing**
```typescript
// Internal helper - export if it has complex logic worth testing
export function parseOrderItems(raw: string): OrderItem[] {
    // complex parsing logic
}
```

**Accept dependencies as parameters**
```typescript
// Hard to test: hidden dependency
function getUser(id: string) {
    return database.findOne({ id });
}

// Testable: dependency injection
function getUser(id: string, db: Database) {
    return db.findOne({ id });
}

// Or: factory pattern
function createUserService(db: Database) {
    return {
        getUser: (id: string) => db.findOne({ id })
    };
}
```

## What to Test

**Do test:**
- Business logic and calculations
- Data transformations
- Validation functions
- Edge cases and error conditions

**Skip testing:**
- Simple pass-through functions
- Direct database/API wrappers
- Framework boilerplate

## Test Structure

```typescript
describe('functionName', () => {
    // Group by scenario
    describe('when input is valid', () => {
        it('returns expected result', () => {});
        it('handles edge case X', () => {});
    });

    describe('when input is invalid', () => {
        it('throws ValidationError', () => {});
    });
});
```

## Mocking Guidelines

- Mock at boundaries (database, external APIs)
- Don't mock internal functions unless necessary
- Prefer dependency injection over mocking imports
