---
description: Distill human review feedback on your PR into the Manual section of .claude/standards.md
argument-hint: "[PR number or URL, defaults to the current branch's open PR]"
---

# Learn From Review

Fold the feedback human reviewers left on one of your PRs back into `.claude/standards.md`, so `/pre-review` catches the same thing next time.

## Steps

1. **Resolve the PR**: Use `$ARGUMENTS` if given. Otherwise `gh pr view --json number,title` for the current branch. If neither finds a PR, stop and say so.
2. **Gather feedback**:
   - Reviews and discussion: `gh pr view <n> --json title,reviews,comments`
   - Inline review comments: `gh api repos/{owner}/{repo}/pulls/<n>/comments --paginate`
   - Pull `gh pr diff <n>` only when a comment is unclear without code context.
3. **Distill rules** from human reviewer comments only:
   - Skip bot comments, approvals with no content, and questions that were answered without a code change.
   - One line per rule, imperative, phrased so a diff can be checked against it mechanically, with the why when the reviewer gave one.
   - Read the existing `.claude/standards.md` first and skip anything an existing rule already covers.
4. **Append to the `## Manual` section** of `.claude/standards.md` (create the file or the section if missing):

   ```markdown
   - [Rule] (#123, learned YYYY-MM-DD)
   ```

   Manual is the right home: `/distill-standards` regenerates every other section but carries `## Manual` forward untouched.
5. **Report**: rules added, and what was skipped as duplicate or non-actionable.

## Guidelines

- High bar: a rule must be something the reviewer would flag again on a different diff. One-off comments about this PR's specific logic are not rules.
- Never store raw comment text or reviewer names — distilled rules only.
