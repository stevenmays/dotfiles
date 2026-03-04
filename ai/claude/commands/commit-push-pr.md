# Commit, Push, and Create PR

Stage all changes, create a commit with an auto-generated message, push to remote, and open a pull request.

## Steps

1. **Check status**: Run `git status` to see what's changed
2. **Stage changes**: Stage all modified and untracked files (excluding `.env`, credentials, or large binaries)
3. **Generate commit message**: Analyze the diff and create a concise commit message following conventional commits format
4. **Commit**: Create the commit
5. **Push**: Push to the current branch (create remote branch if needed with `-u`)
6. **Create PR**: Use `gh pr create` with:
   - A clear, descriptive title (under 70 chars)
   - A summary section with 1-3 bullet points describing the changes
   - A test plan section

## Requirements

- Do not force push
- Do not push to main/master directly
- If there are no changes, report that and stop
- If a PR already exists for this branch, report the existing PR URL instead

## Output

Report the PR URL when complete, or explain what blocked the workflow.
