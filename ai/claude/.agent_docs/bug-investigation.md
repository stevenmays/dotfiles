# Bug Investigation Protocol

Read this when debugging issues that resist quick fixes.

## 6-Step Protocol

### 1. Symptoms
- Exact error message and stack trace
- When does it happen? (Always, sometimes, specific conditions)
- What changed recently? (commits, dependencies, config)

### 2. Reproduce
- Find minimal steps to trigger consistently
- Isolate: does it happen in tests? Different environments?
- If intermittent: identify timing, load, or race conditions

### 3. Hypotheses
Generate 3-5 possible causes:
```
1. [Most likely based on evidence]
2. [Second most likely]
3. [Less likely but possible]
```

Rank by: evidence strength, code familiarity, recent changes

### 4. Test Hypotheses
For each hypothesis:
- How to confirm it? (add logging, write test, check state)
- How to eliminate it? (what would prove it wrong)
- Test in order of likelihood

### 5. Root Cause (5 Whys)
Once confirmed, dig deeper:
```
Bug: API returns 500
Why? Database query fails
Why? Connection timeout
Why? Pool exhausted
Why? Connections not released
Why? Missing finally block ← Root cause
```

### 6. Fix
- Address root cause, not symptoms
- Add regression test if repo has tests
- Consider: could this happen elsewhere?

## Common Bug Categories

| Type | Signs | Where to Look |
|------|-------|---------------|
| Race condition | Intermittent, timing-dependent | Async code, shared state |
| State bug | Works once, fails on retry | Initialization, cleanup |
| Integration | Works in isolation | Boundaries between systems |
| Config | Works locally, fails elsewhere | Environment, secrets, paths |

## Rules

- Evidence over intuition
- Change one thing at a time
- If stuck after 2 attempts, step back and re-hypothesize
