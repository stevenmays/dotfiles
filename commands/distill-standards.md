---
description: Distill coding standards from the repo's recent merged PRs into .claude/standards.md
argument-hint: "[number of PRs to analyze; asks if omitted, default 50]"
---

# Distill Standards

Mine the repo's recent merged PRs for recurring review feedback and conventions, then distill them into `.claude/standards.md`. The output is what `/pre-review` checks against.

**N** = `$ARGUMENTS` if given. Otherwise ask via AskUserQuestion how many merged PRs to analyze — options 25 / 50 (recommended) / 100 / 200. If asking isn't possible (non-interactive run), use 50.

## Steps

1. **Preflight**: Confirm `gh` works and the repo has a GitHub remote (`gh repo view`). If not, stop and say so.
2. **List PRs**: `gh pr list --state merged --limit N --json number,title,url`. If the repo has few merged PRs, work with what exists and note it.
3. **Gather review data** for each PR. For more than ~10 PRs, dispatch Explore subagents in batches so raw comments never enter the main context — each batch returns a condensed summary of feedback patterns, not raw comments:
   - PR metadata, reviews, and discussion: `gh pr view <n> --json title,body,reviews,comments`
   - Inline review comments: `gh api repos/{owner}/{repo}/pulls/<n>/comments --paginate`
   - Pull `gh pr diff <n>` only when a comment is unclear without code context.
4. **Distill** — never save raw comments. Extract only:
   - **Recurring feedback**: anything reviewers asked for two or more times across PRs
   - **Conventions**: naming, file structure, error handling, and testing patterns evident from accepted changes
   - **Blockers**: things that forced changes before merge or got reverted
   - Drop one-off nitpicks, personal disputes, and anything stale (contradicted by a later PR).
5. **Write `.claude/standards.md`** (create `.claude/` if needed, overwrite the file — it is regenerated, not appended):

   ```markdown
   # Code Standards

   Distilled from PRs #X–#Y on YYYY-MM-DD by /distill-standards.

   ## Conventions
   - [One line, imperative, with a short why] (#123, #145)

   ## Review Feedback Patterns
   - [Recurring asks from reviewers] (#130)

   ## Testing Expectations
   - [What reviewers expect tested] (#127)
   ```

   Every rule gets at least one PR reference so it can be audited later.
6. **Report**: how many PRs were analyzed, how many rules were distilled, and the two or three highest-signal rules.

## Guidelines

- Quality over quantity: 10–25 high-signal rules beat 100 noisy ones.
- Phrase rules so a reviewer can check a diff against them mechanically.
- If `.claude/standards.md` already exists, regenerate it fresh — but carry forward any rules under a `## Manual` section untouched (that section is user-maintained).
