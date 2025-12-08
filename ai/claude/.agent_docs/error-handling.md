# Error Handling Conventions

Read this before implementing error handling logic.

## Core Principles

1. Handle errors at the top level of functions
2. Throw real Error objects, never strings
3. Add useful context to error messages
4. Don't use errors for control flow
5. Consider downstream impact when choosing strategy

## Basic Pattern

```typescript
async function processData(data: Data[]) {
    try {
        return data.map(processItem);
    } catch (error) {
        // Option 1: Log and return default (non-critical operations)
        console.warn(`Data processing warning: ${error.message}`);
        return getDefaultData();

        // Option 2: Throw with context (critical operations)
        throw new Error(`Data processing failed: ${error.message}`);
    }
}
```

## When to Catch vs Throw

**Catch and handle:**
- Non-critical operations where a default is acceptable
- Errors you can meaningfully recover from
- Boundary functions that must return a response

**Throw with context:**
- Critical operations that must succeed
- Errors that indicate bugs or invalid state
- When caller needs to decide how to handle

## Custom Error Classes

Use when you need to distinguish error types:

```typescript
export class ValidationError extends Error {
    field?: string;
    code: string;

    constructor(message: string, code: string, field?: string) {
        super(message);
        this.name = 'ValidationError';
        this.code = code;
        this.field = field;
    }
}

// Usage
throw new ValidationError('Email format invalid', 'INVALID_EMAIL', 'email');

// Catching specific types
try {
    validate(input);
} catch (error) {
    if (error instanceof ValidationError) {
        return { statusCode: 400, body: error.message };
    }
    throw error; // Re-throw unexpected errors
}
```

## Avoid

```typescript
// Bad: throwing strings
throw 'Something went wrong';

// Bad: swallowing errors silently
try {
    riskyOperation();
} catch (error) {
    // nothing
}

// Bad: nested try/catch
try {
    try {
        innerOperation();
    } catch (e) {
        // ...
    }
} catch (e) {
    // ...
}

// Bad: using errors for control flow
try {
    const user = getUser(id);
} catch {
    // User not found, create new one
    createUser(id);
}
```

## Context in Error Messages

```typescript
// Bad: no context
throw new Error('Failed to process');

// Good: actionable context
throw new Error(`Failed to process order ${orderId}: ${error.message}`);

// Good: structured for logging
throw new Error(JSON.stringify({
    message: 'Order processing failed',
    orderId,
    reason: error.message,
    timestamp: Date.now()
}));
```
