# Coding Guidelines

## Core Principles

### Embrace Simplicity Over Cleverness
- Write code that's immediately understandable
- If a solution feels complex, simplify it
- Optimize for readability first, performance second unless proven otherwise
- Write code for humans first, computers second

### Leverage Existing Solutions
- Use standard libraries whenever possible
- Don't reinvent the wheel
- Keep dependencies minimal but practical
- Prefer organization-specific packages when available

### Focus on Core Functionality
- Start with the minimum viable solution
- Question every feature: "Is this really necessary?"
- Build incrementally based on actual needs, not hypothetical ones
- Delete unnecessary code and features

## Function Design

- Each function should have a single responsibility
- Keep functions focused and short (aim for under 20 lines)
- Use descriptive names that indicate purpose
- Limit parameters to 3 or fewer
- Write pure functions where possible
- Prefer early returns over nested conditionals
- Extract complex logic into separate pure functions
```typescript
// Bad: Multiple responsibilities
async function processUserData(userData: UserData) {
    if (validateUser(userData)) {
        await saveToDatabase(userData);
        await sendWelcomeEmail(userData);
        await updateMetrics(userData);
    }
}

// Good: Single responsibility
async function saveUser(userData: UserData) {
    if (!userData) {
        throw new Error('User data cannot be empty');
    }
    return database.insert('users', userData);
}
```

## Control Flow

- Use guard clauses at function start
- Reduce indentation levels
- Keep the main flow obvious
```typescript
// Bad: Deeply nested
function processOrder(order) {
    if (order) {
        if (order.items && order.items.length > 0) {
            if (order.status === 'new') {
                return true;
            }
        }
    }
    return false;
}

// Good: Early returns
function processOrder(order) {
    if (!order) return false;
    if (!order.items?.length) return false;
    if (order.status !== 'new') return false;
    
    return true;
}
```

## Error Handling

- Handle errors explicitly at function top level
- Avoid nesting try/catch blocks deeply
- Always throw real Error objects, not strings
- Add useful context to error messages
- Don't use errors for control flow
- Consider downstream impact when deciding strategy
```typescript
// Good: Top-level error handling
async function processData(data) {
    try {
        return data.map(processItem);
    } catch (error) {
        // Option 1: Log and return default for non-critical operations
        console.warn(`Data processing warning: ${error.message}`);
        return getDefaultData();
        
        // Option 2: Throw with context for critical operations
        throw new Error(`Data processing failed: ${error.message}`);
    }
}

// Good: Custom error class
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
```

## TypeScript Patterns

### Type System
- Prefer interfaces for object shapes
- Use type aliases for unions and primitives
- Let TypeScript infer return types when possible
- Use angle brackets for type assertions: `<Type>value`
- Use type guards for runtime validation
- Avoid `any` - use `unknown` for truly unknown values
```typescript
// Interface for object types
interface CustomerData {
    id: string;
    email: string;
    status: 'active' | 'inactive';
}

// Type inference for returns
function getCustomer(id: string) {
    return database.findOne({ id });
}

// Angle bracket assertion
const config = <ConfigType>JSON.parse(configJson);

// Type guard
function isValidOrder(value: unknown): value is Order {
    return typeof value === 'object' && 
           value !== null && 
           'id' in value;
}
```

### Naming Conventions
- camelCase for local variables and functions
- kebab-case for files and folders
- camelCase for TypeScript interface properties
- snake_case for database/API fields

### Import Organization
- Use ES module imports (never `require`)
- Prefer namespace imports: `import * as mongodb from 'mongodb'`
- Group imports: node builtins, external, internal
- Use explicit file extensions
```typescript
import assert from 'node:assert';
import * as mongodb from 'mongodb';
import { validateOrder } from '../lib/validation.js';
```

## Data Structures

- Keep structures as simple as possible
- Prefer shallow hierarchies over deep nesting
- Don't mutate parameters during iteration/mapping

## Code Organization
```
src/
├── handlers/          # Entry points
├── lib/              # Shared business logic
└── scripts/          # Development scripts
```

- Keep related code together
- Group by feature rather than type
- Separate handlers from business logic

## Prefer Functions Over Classes
```typescript
// Bad: Unnecessary class
class PriceCalculator {
    constructor(private taxRate: number) {}
    calculatePrice(basePrice: number) {
        return basePrice * (1 + this.taxRate);
    }
}

// Good: Simple function
function calculatePrice(basePrice: number, taxRate: number) {
    return basePrice * (1 + taxRate);
}

// If you need state, use closures
function createPriceCalculator(taxRate: number) {
    return (basePrice: number) => basePrice * (1 + taxRate);
}
```

## Comments

- Comment complex logic explaining *why*, not *what*
- Avoid redundant or obvious comments
- Document public APIs with JSDoc
- Include examples for complex functions

## Testing

- Write testable pure functions
- Separate I/O from business logic
- Export functions that need testing
- Design functions to accept dependencies
```typescript
// Testable pure function
export function calculateDiscount(order: Order): number {
    if (order.total > 100) return order.total * 0.1;
    return 0;
}

// Separate I/O from logic
async function processOrder(orderId: string) {
    const order = await fetchOrder(orderId);  // I/O
    const discount = calculateDiscount(order); // Pure (testable)
    await updateOrder(orderId, { discount }); // I/O
}
```

## Security

- Never hardcode secrets or credentials
- Authenticate all incoming requests
- Validate and sanitize all inputs
- Use type guards for runtime validation

## Patterns to Avoid

### General
- Global state/variables
- Deeply nested callbacks
- Mixed sync and async code styles
- Complex/clever one-liners
- Overuse of optional chaining

### AI-Specific Anti-Patterns

These patterns commonly appear in AI-generated code. Avoid them, and remove them during code review.

**Excessive comments**
```typescript
// ❌ States the obvious
// Check if the user is valid
if (isValidUser(user)) {

// ❌ Repeats the code
// Set the status to active
status = 'active';

// ✅ Explains why (keep these)
// Must check expiry before validation - expired tokens cause cryptic errors
if (isExpired(token)) return null;
```

**Gratuitous defensive checks**
```typescript
// ❌ Remove if upstream already validates
function processOrder(order: Order) {
    if (!order) throw new Error('Order is required');  // Type guarantees this
    if (!order.items) throw new Error('Items required');  // Already validated
}

// ✅ Keep: Boundary validation at entry points
export async function handleRequest(event: APIGatewayEvent) {
    if (!event.body) return { statusCode: 400, body: 'Missing body' };
}
```

**Type escape hatches**
```typescript
// ❌ Casting to any to silence errors
const result = (data as any).value;

// ✅ Fix the type properly
const result = (<DataWithValue>data).value;

// ✅ Or use a type guard
if (hasValue(data)) {
    const result = data.value;
}
```

**Over-engineering**
```typescript
// ❌ Unnecessary wrapper
function getItemCount(items: Item[]) {
    return items.length;
}

// ❌ Single-use interface
interface ProcessingOptions {
    validate: boolean;
}
// Only called once: process(data, { validate: true })
```

**Verbose logging** - Match the file's existing logging level. Don't add console.log for every step.

**Style inconsistencies** - Match the existing file's patterns for naming, imports, error handling, spacing.