# Quick Commit

Stage all changes and create a commit with an auto-generated message. Does not push.

## Steps

1. Run `git status` to see current changes
2. Run `git diff` to understand what changed
3. Stage all modified files (be careful with new files - review them first)
4. Generate a concise commit message that:
   - Follows conventional commits format (feat:, fix:, chore:, docs:, refactor:, test:)
   - Summarizes the "why" not just the "what"
   - Is under 72 characters for the subject line
5. Create the commit

## Safety Checks

- Do not stage files matching: `.env*`, `*credentials*`, `*.pem`, `*.key`
- Do not stage files over 1MB without explicit confirmation
- If there are no changes, report that and stop

## Output

Show the commit hash and message when complete.
