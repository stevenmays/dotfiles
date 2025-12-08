# AI-Specific Anti-Patterns

These patterns commonly appear in AI-generated code. Avoid them, and remove them during code review.

## Excessive Comments

```typescript
// Bad: states the obvious
// Check if the user is valid
if (isValidUser(user)) {

// Bad: repeats the code
// Set the status to active
status = 'active';

// Good: explains why (keep these)
// Must check expiry before validation - expired tokens cause cryptic errors
if (isExpired(token)) return null;
```

**Rule**: If deleting the comment loses no information, delete it.

## Gratuitous Defensive Checks

```typescript
// Bad: type system already guarantees this
function processOrder(order: Order) {
    if (!order) throw new Error('Order is required');
    if (!order.items) throw new Error('Items required');
}

// Good: validate at entry points only
export async function handleRequest(event: APIGatewayEvent) {
    if (!event.body) return { statusCode: 400, body: 'Missing body' };
    const order = JSON.parse(event.body);
    // Internal functions trust their callers
    return processOrder(order);
}
```

**Rule**: Validate at system boundaries. Trust internal code.

## Type Escape Hatches

```typescript
// Bad: casting to silence errors
const result = (data as any).value;

// Good: fix the type
const result = (<DataWithValue>data).value;

// Better: type guard for runtime safety
if (hasValue(data)) {
    const result = data.value;
}
```

**Rule**: Never use `as any`. Fix the type or use a type guard.

## Over-Engineering

```typescript
// Bad: wrapper that adds nothing
function getItemCount(items: Item[]) {
    return items.length;
}

// Bad: single-use interface
interface ProcessingOptions {
    validate: boolean;
}
// Only ever called: process(data, { validate: true })

// Bad: abstraction for one case
function createHandler(config: HandlerConfig) {
    return async (event) => { /* ... */ };
}
// Only one handler ever created
```

**Rule**: Don't abstract until you have 3+ concrete cases.

## Verbose Logging

```typescript
// Bad: log spam
function processItems(items: Item[]) {
    console.log('Starting processItems');
    console.log(`Processing ${items.length} items`);
    for (const item of items) {
        console.log(`Processing item ${item.id}`);
        // ...
        console.log(`Finished item ${item.id}`);
    }
    console.log('Finished processItems');
}

// Good: match existing file's logging level
function processItems(items: Item[]) {
    for (const item of items) {
        // actual work
    }
}
```

**Rule**: Match the file's existing logging patterns.

## Style Inconsistencies

Before writing code, check the file for:
- Naming conventions used
- Import style
- Error handling patterns
- Spacing and formatting

**Rule**: Match existing patterns exactly. Don't "improve" style in unrelated code.

## Backwards Compatibility Cruft

```typescript
// Bad: keeping dead code "just in case"
// const oldFunction = () => {}; // REMOVED - use newFunction instead

// Bad: unused re-exports
export { oldThing }; // No longer used anywhere

// Bad: underscore prefix for "unused"
const _legacyConfig = getConfig(); // Actually unused
```

**Rule**: Delete unused code completely. Git has history.
