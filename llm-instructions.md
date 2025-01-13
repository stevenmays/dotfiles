# Coding Instructions for LLM tools

Original source: https://github.com/tom-doerr/dotfiles/blob/master/instruction.md

Keep it simple!

## 1. Embrace Simplicity Over Cleverness
- Write code that's immediately understandable to others
- If a solution feels complex, it probably needs simplification
- Optimize for readability first, performance second unless proven otherwise
- Avoid premature optimization

```typescript
// Avoid clever one-liners
// Bad
const getPrimes = (maxNum: number): number[] => 
  [...Array(maxNum)].map((_, i) => i).filter(n => 
    n > 1 && [...Array(n)].map((_, i) => i + 1).slice(1).every(i => n % i !== 0));

// Good
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

## 2. Focus on Core Functionality
- Start with the minimum viable solution
- Question every feature: "Is this really necessary?"
- Build incrementally based on actual needs, not hypothetical ones
- Delete unnecessary code and features

```typescript
// Bad: Overengineered from the start
interface IUserManager {
    db: Database;
    cache: Cache;
    logger: Logger;
    metrics: MetricsService;
    notification: NotificationService;
}

class UserManager implements IUserManager {
    constructor(
        public db: Database,
        public cache: Cache,
        public logger: Logger,
        public metrics: MetricsService,
        public notification: NotificationService
    ) {}
}

// Good: Start simple, expand when needed
class UserManager {
    constructor(private db: Database) {}
}
```

## 3. Leverage Existing Solutions
- Use standard libraries whenever possible
- Don't reinvent the wheel
- Choose well-maintained, popular libraries for common tasks
- Keep dependencies minimal but practical

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

## 4. Function Design
- Each function should have a single responsibility
- Keep functions short (typically under 20 lines)
- Use descriptive names that indicate purpose
- Limit number of parameters (3 or fewer is ideal)

```typescript
interface UserData {
    id: string;
    email: string;
    name: string;
}

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

## 5. Project Structure
- Keep related code together
- Use consistent file organization
- Maintain a flat structure where possible
- Group by feature rather than type

```plaintext
# Good project structure
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

## 6. Code Review Guidelines
- Review for simplicity first
- Question complexity and overengineering
- Look for duplicate code and abstraction opportunities
- Ensure consistent style and naming conventions

## 7. Maintenance Practices
- Regularly remove unused code
- Keep dependencies updated
- Refactor when code becomes unclear
- Document only what's necessary and likely to change

## 8. Type System Best Practices
- Use TypeScript's type system to make code self-documenting
- Prefer interfaces over type aliases for object types
- Use union types instead of enums when possible
- Leverage generics for reusable code

```typescript
// Good use of TypeScript features
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

class UserRepository implements Repository<User> {
    async find(id: string): Promise<User | null> {
        // Implementation
        return null;
    }

    async save(user: User): Promise<void> {
        // Implementation
    }

    async delete(id: string): Promise<boolean> {
        // Implementation
        return true;
    }
}
```

Remember:
- Simple code is easier to maintain and debug
- Write code for humans first, computers second
- Add complexity only when justified by requirements
- If you can't explain your code simply, it's probably too complex
- Use TypeScript's type system to catch errors early

## 9. Prefer Functions Over Classes
- Functions are simpler to test and compose
- Avoid unnecessary class abstractions
- Use objects and closures for state management when needed
- Classes often add unnecessary complexity

```typescript
// Bad: Unnecessary class abstraction
class PriceCalculator {
    constructor(private taxRate: number) {}
    
    calculatePrice(basePrice: number): number {
        return basePrice * (1 + this.taxRate);
    }
}

const calculator = new PriceCalculator(0.2);
const price = calculator.calculatePrice(100);

// Good: Simple function
function calculatePrice(basePrice: number, taxRate: number): number {
    return basePrice * (1 + taxRate);
}

const price = calculatePrice(100, 0.2);

// If you need to maintain state, use closures
function createPriceCalculator(taxRate: number) {
    return (basePrice: number) => basePrice * (1 + taxRate);
}

const calculateWithTax = createPriceCalculator(0.2);
const price = calculateWithTax(100);

// Bad: Class with unnecessary abstraction
class UserService {
    constructor(private db: Database) {}

    async getUser(id: string): Promise<User> {
        return this.db.findUser(id);
    }
    
    async saveUser(user: User): Promise<void> {
        await this.db.saveUser(user);
    }
}

// Good: Direct functions using dependency injection
type GetUser = (db: Database) => (id: string) => Promise<User>;
const getUser: GetUser = (db) => (id) => db.findUser(id);

type SaveUser = (db: Database) => (user: User) => Promise<void>;
const saveUser: SaveUser = (db) => (user) => db.saveUser(user);

// Usage
const findUserById = getUser(database);
const user = await findUserById("123");
```