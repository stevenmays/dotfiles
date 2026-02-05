# Test and Fix

Run tests and iteratively fix any failures until all tests pass.

## Steps

1. **Detect test runner**: Look for package.json scripts, pytest, go test, cargo test, etc.
2. **Run tests**: Execute the appropriate test command
3. **Analyze failures**: If tests fail, identify the root cause from error output
4. **Fix issues**: Make minimal, targeted fixes to resolve failures
5. **Re-run tests**: Verify the fix worked
6. **Iterate**: Repeat steps 3-5 until all tests pass (max 5 iterations)

## Guidelines

- Make the smallest possible fix that resolves the failure
- Do not refactor unrelated code
- Do not change test expectations unless the test is clearly wrong
- If a fix requires changing multiple files, explain why before proceeding
- If stuck after 3 iterations on the same error, stop and explain the situation

## Test Commands by Ecosystem

- Node.js: `npm test` or `npm run test`
- Python: `pytest` or `python -m pytest`
- Go: `go test ./...`
- Rust: `cargo test`
- Ruby: `bundle exec rspec` or `rake test`

## Output

Report final test results and summarize any fixes made.
