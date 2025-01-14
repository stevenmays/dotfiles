# Coding Instructions for LLM tools

Inspiration: https://github.com/tom-doerr/dotfiles/blob/master/instruction.md

Keep it simple!

## Core Principles

### 1. Embrace Simplicity Over Cleverness
- Write code that's immediately understandable to others
- If a solution feels complex, it probably needs simplification
- Optimize for readability first, performance second unless proven otherwise
- Avoid premature optimization
- Write code for humans first, computers second

Example of simplicity:
```typescript
// Avoid clever one-liners like this:
const getPrimes = (maxNum: number): number[] => 
  [...Array(maxNum)].map((_, i) => i).filter(n => 
    n > 1 && [...Array(n)].map((_, i) => i + 1).slice(1).every(i => n % i !== 0));

// Instead, write clear, readable code:
function findPrimeNumbers(maxNum: number): number[] {
    const primes: number[] = [];
    for (let number = 2; number < maxNum; number++) {
        if (isPrime(number)) {
            primes.push(number);
        }
    }
    return primes;
}

function isPrime(n: number): boolean {
    if (n < 2) return false;
    for (let i = 2; i <= Math.sqrt(n); i++) {
        if (n % i === 0) return false;
    }
    return true;
}
```

### 2. Leverage Existing Solutions
- Use standard libraries whenever possible
- Don't reinvent the wheel
- Choose well-maintained, popular libraries for common tasks
- Keep dependencies minimal but practical

Example:
```typescript
// Bad: Custom implementation
const parseJsonFile = (filePath: string): unknown => {
    const content = fs.readFileSync(filePath, 'utf-8');
    // Custom parsing logic...
};

// Good: Use standard library
import { readFileSync } from 'fs';

function readConfig<T>(filePath: string): T {
    const content = readFileSync(filePath, 'utf-8');
    return JSON.parse(content) as T;
}
```

### 3. Focus on Core Functionality
- Start with the minimum viable solution
- Question every feature: "Is this really necessary?"
- Build incrementally based on actual needs, not hypothetical ones
- Delete unnecessary code and features
- Leverage existing solutions and standard libraries
- Don't reinvent the wheel

### 3. Function Design
- Each function should have a single responsibility
- Keep functions focused and relatively short (aim for under 20 lines)
- Use descriptive names that indicate purpose
- Limit number of parameters (3 or fewer is ideal)
- Write pure functions where possible
- Return consistent types (don't mix returned types)
- Avoid terminating awaits - return promises instead

Example:
```typescript
// Bad: Multiple responsibilities
async function processUserData(userData: UserData): Promise<void> {
    if (validateUser(userData)) {
        await saveToDatabase(userData);
        await sendWelcomeEmail(userData);
        await updateMetrics(userData);
    }
}

// Good: Single responsibility
async function saveUser(userData: UserData): Promise<string> {
    if (!userData) {
        throw new Error("User data cannot be empty");
    }
    return database.insert("users", userData);
}
```

### 4. Error Handling
- Handle errors explicitly - don't rely on top-level handlers
- Use try/catch blocks appropriately but don't make them overly large
- Always throw real Error objects, not strings or other types
- Add useful context to error messages
- Don't use errors for control flow

### 5. Data Structures and Type System
- Keep data structures as simple as possible
- Prefer shallow object hierarchies over deep nesting
- Use consistent property naming
- Use TypeScript's type system to make code self-documenting
- Prefer interfaces over type aliases for object types
- Use union types instead of enums when possible
- Don't mutate parameters during iteration/mapping

Example:
```typescript
interface Repository<T> {
    find(id: string): Promise<T | null>;
    save(item: T): Promise<void>;
    delete(id: string): Promise<boolean>;
}

type Status = 'pending' | 'active' | 'inactive';

interface User {
    id: string;
    name: string;
    status: Status;
    metadata: Record<string, unknown>;
}
```

### 6. Code Organization
- Keep related code together
- Use consistent file organization
- Maintain a flat structure where possible
- Group by feature rather than type
- Follow consistent naming conventions:
  - camelCase for local variables and functions
  - kebab-case for files and folders

Example structure:
```
project/
├── src/
│   ├── index.ts
│   ├── config.ts
│   ├── users/
│   │   ├── models.ts
│   │   ├── services.ts
│   │   └── __tests__/
│   └── utils/
│       └── helpers.ts
├── package.json
└── tsconfig.json
```

### 7. Prefer Functions Over Classes
- Functions are simpler to test and compose
- Avoid unnecessary class abstractions
- Use objects and closures for state management when needed
- Classes often add unnecessary complexity

Example:
```typescript
// Bad: Unnecessary class
class PriceCalculator {
    constructor(private taxRate: number) {}
    
    calculatePrice(basePrice: number): number {
        return basePrice * (1 + this.taxRate);
    }
}

// Good: Simple function
function calculatePrice(basePrice: number, taxRate: number): number {
    return basePrice * (1 + taxRate);
}

// If you need state, use closures
function createPriceCalculator(taxRate: number) {
    return (basePrice: number) => basePrice * (1 + taxRate);
}
```

### 8. Promise/Async Handling
- Prefer async/await over raw promises where appropriate
- Handle promise rejections explicitly
- Don't mix promise chain syntax with async/await
- Only await promises, not regular values

### 9. Comments and Documentation
- Comment complex logic that isn't immediately clear
- Keep comments focused on explaining why, not what
- Avoid redundant or obvious comments
- Document public APIs and interfaces
- Document only what's necessary and likely to change

### Patterns to Avoid
- Don't use global state/variables
- Avoid deeply nested callbacks
- Don't mix sync and async code styles
- Avoid complex/clever one-liners
- Don't overuse optional chaining
- Avoid redundant type assertions

## Remember
- If you can't explain your code simply, it's probably too complex
- Simple code is easier to maintain and debug
- Add complexity only when justified by requirements
- Use TypeScript's type system to catch errors early
- Regular code review and maintenance are essential