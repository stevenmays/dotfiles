# Code Review

Review a pull request using conventional comments format.

**Usage**: `/code-review <PR_NUMBER>`

## Steps

1. **Fetch PR details**: Run `gh pr view <PR_NUMBER>` to get PR title, description, and metadata
2. **Get the diff**: Run `gh pr diff <PR_NUMBER>` to see all changes
3. **Ask about worktree**: Ask the user if they want to create a git worktree to test the code locally
   - If yes, create worktree: `git worktree add ../review-pr-<PR_NUMBER> <branch_name>`
   - Inform user of worktree location
4. **Review the code**: Analyze the diff thoroughly, checking for:
   - Logic errors and bugs
   - Security vulnerabilities
   - Performance issues
   - Code clarity and maintainability
   - Test coverage gaps
   - Consistency with existing codebase patterns

## Conventional Comments Format

Use this format for all review comments:

```
**<label> [decorations]:** <subject>

[discussion]
```

### Labels

| Label | When to Use |
|-------|-------------|
| **praise** | Highlight something done well (include at least one per review) |
| **suggestion** | Propose an improvement with reasoning |
| **issue** | Identify a specific problem that needs fixing |
| **question** | Seek clarification on intent or approach |
| **nitpick** | Trivial preference-based request (non-blocking) |
| **thought** | Share an idea sparked by the code (non-blocking) |
| **todo** | Small necessary change before merge |
| **chore** | Simple task needed before acceptance |
| **note** | Non-blocking observation worth mentioning |
| **typo** | Spelling or grammar error |

### Decorations

- **(blocking)** - Must be resolved before approval
- **(non-blocking)** - Should not prevent merge
- **(if-minor)** - Resolve only if changes are trivial

### Examples

```
**praise:** Clean separation of concerns here. The data fetching logic being isolated makes this very testable.

**issue (blocking):** This SQL query is vulnerable to injection.

The user input is concatenated directly into the query string. Use parameterized queries instead.

**suggestion (non-blocking):** Consider extracting this into a named constant.

The magic number `86400` appears twice. A `SECONDS_PER_DAY` constant would improve readability.

**nitpick (non-blocking):** Prefer `const` over `let` here since the value is never reassigned.
```

## Output Structure

1. **PR Summary**: Brief overview of what the PR does
2. **Review Comments**: Organized list using conventional comments format
3. **Overall Assessment**:
   - Approve / Request Changes / Comment
   - Summary of blocking vs non-blocking items
4. **Worktree cleanup reminder** (if created): `git worktree remove ../review-pr-<PR_NUMBER>`

## Requirements

- Always include at least one **praise** comment
- Clearly distinguish blocking from non-blocking feedback
- Reference specific file paths and line numbers when possible
- If the PR is large, focus on the most impactful areas first
