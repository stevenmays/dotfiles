---
description: Distill coding standards from merged PRs into .claude/standards.md — full history, delta since last run, or a single PR
argument-hint: "[N = regenerate from last N PRs | #123 or PR URL = absorb one PR | empty = delta since last run | full]"
---

# Distill Standards

Mine the repo's PR review feedback and conventions, then distill them into `.claude/standards.md`. The output drives `/pre-review`, `/review-pr`, and `/extreme-code-quality-review`.

## Mode selection (`$ARGUMENTS`)

| Argument | Mode |
|----------|------|
| Bare number (`50`) | **Full regenerate** from the last N merged PRs |
| `#123` or a PR URL | **Single PR**: absorb that one PR's review feedback into the existing standards (works on open PRs too — run it right after human review lands on your PR) |
| *(empty)* | **Delta** if `.claude/standards.md` exists: analyze only PRs merged since the run recorded in its header. Otherwise fall through to full regenerate |
| `full` | Force full regenerate |

For a full regenerate with no N given, ask via AskUserQuestion how many merged PRs to analyze — options 25 / 50 (recommended) / 100 / 200. If asking isn't possible (non-interactive run), use 50.

## Steps

1. **Preflight**: Confirm `gh` works and the repo has a GitHub remote (`gh repo view`). If not, stop and say so.
2. **List PRs** for the selected mode:
   - **Full**: `gh pr list --state merged --limit N --json number,title,url`. If the repo has few merged PRs, work with what exists and note it.
   - **Delta**: read the header of `.claude/standards.md` for the last run's date, then `gh pr list --state merged --search "merged:>YYYY-MM-DD" --json number,title,url --limit 200`. Exclude PRs already covered by the header's range. If nothing new merged, say so and stop.
   - **Single PR**: resolve the number/URL with `gh pr view <n> --json number,title,state`. The PR does not need to be merged.
3. **Gather review data** for each PR. For more than ~10 PRs, dispatch Explore subagents in batches so raw comments never enter the main context — each batch returns a condensed summary of feedback patterns, not raw comments:
   - PR metadata, reviews, and discussion: `gh pr view <n> --json title,body,reviews,comments`
   - Inline review comments: `gh api repos/{owner}/{repo}/pulls/<n>/comments --paginate`
   - Pull `gh pr diff <n>` only when a comment is unclear without code context.
4. **Distill** — never save raw comments. Two-tier extraction:
   - **Recurring** (→ Conventions / Review Feedback Patterns / Testing Expectations):
     - Anything reviewers asked for two or more times across PRs
     - Naming, file structure, error handling, and testing patterns evident from accepted changes
     - Blockers: things that forced changes before merge or got reverted
   - **One-offs** (→ One-offs section): substantive feedback seen only once — edge cases, domain gotchas, "this broke prod" learnings, non-obvious constraints a future diff could violate again. The bar: would a reviewer flag this again on a *different* diff? If yes, keep it even though it only appeared once.
   - **Drop entirely**: pure style nitpicks, personal disputes, questions answered without a code change, and anything stale (contradicted by a later PR).
5. **Write `.claude/standards.md`** (create `.claude/` if needed):

   ```markdown
   # Code Standards

   Distilled from PRs #X–#Y on YYYY-MM-DD by /distill-standards. Last update: YYYY-MM-DD (delta PRs #A–#B | single PR #n).

   ## Conventions
   - [One line, imperative, with a short why] (#123, #145)

   ## Review Feedback Patterns
   - [Recurring asks from reviewers] (#130)

   ## Testing Expectations
   - [What reviewers expect tested] (#127)

   ## One-offs
   - [Substantive one-time feedback, phrased as a checkable rule] (#152, YYYY-MM-DD)

   ## Manual
   - [Hand-written rules — never touched by this command]
   ```

   Every rule gets at least one PR reference so it can be audited later. Per mode:
   - **Full**: rewrite the three recurring sections from scratch. Carry `## One-offs` and `## Manual` forward untouched, then dedupe One-offs against the newly derived recurring rules (a one-off now covered by a recurring rule is deleted).
   - **Delta / Single PR**: merge into the existing file — add new rules, strengthen existing ones with new PR refs, append new one-offs. Update the header's "Last update" line; delta also extends the covered PR range.
   - **Promotion**: in any mode, when new evidence shows an existing one-off a second time, move it to the appropriate recurring section (keeping both PR refs) and remove the one-off entry.
6. **Report**: mode used, PRs analyzed, rules added/updated/promoted, and the two or three highest-signal findings.

## Guidelines

- Quality over quantity: 10–25 high-signal recurring rules beat 100 noisy ones. One-offs may accumulate more freely, but each must still be checkable against a diff.
- Phrase every rule so a reviewer can check a diff against it mechanically.
- `## Manual` is user-maintained: never add to it, edit it, or remove it.
