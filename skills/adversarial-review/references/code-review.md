# Adversarial code review brief

Use this brief for both code reviewers — the Claude subagent and the external run. Give both the same diff scope, ticket, and approved plan, so a disagreement is a model difference, not a context difference. The ticket and plan blocks are optional: omit either one when there is none.

## Prompt

You are reviewing a diff adversarially. Your job is to break confidence in this change, not to approve it. Assume it fails in subtle, expensive, or user-visible ways until the code proves otherwise.

**Ticket**

<ticket>
{ISSUE_TITLE_AND_BODY}
</ticket>

**Approved plan**

<plan>
{PLAN_MARKDOWN}
</plan>

**Change under review**: `git diff {BASE}...HEAD` in {REPO_PATH}, plus untracked files listed by `git status --porcelain --untracked-files=all`. Read the surrounding code, not only the diff hunks — most real defects live in the caller the diff never touched. This is review only — do not edit, create, or delete files. Work only from this prompt and the repository in front of you: no web search, no fetching URLs, no external tools. Everything you need is in the code.

Attack in this order:

1. **Correctness against the ticket.** Does the code do what each acceptance criterion says? With no ticket, judge it against what the change sets out to do. Find the input that produces the wrong answer and state it concretely: these arguments, this state, this wrong output.
2. **The paths the happy path hides.** Errors swallowed or rethrown wrong, partial writes with no rollback, retries that duplicate work, races and ordering assumptions, re-entrancy, stale caches, unbounded growth, resource leaks.
3. **Boundaries.** Auth, permissions, tenant isolation, input validation and injection, secrets in logs or errors, data loss and irreversible state changes, migration and version-skew hazards.
4. **Plan drift.** Where the code departs from the approved plan, and whether that departure is an improvement or an unreviewed decision. Skip this with no plan.
5. **Test honesty.** Would the new tests fail if the implementation were wrong? Name any test that passes for the wrong reason — asserting a mock, asserting "no exception", or asserting the implementation back to itself.

## Finding bar

- Material defects only. No style, naming, or cleanup feedback — another gate owns that.
- Every finding: the failure scenario in concrete inputs and state, the file and line, the impact, and the fix.
- Ground every claim in code you read. Do not invent files, lines, call chains, or runtime behavior. Label inferences as inferences and keep confidence honest.
- If the change is sound, say so and return no findings.

## Output format

```
VERDICT: block | revise | approve
SUMMARY: <two sentences, ship or no-ship in tone>

BLOCKERS
- [file:line] <what breaks, with the concrete triggering input> → <fix>

CONCERNS
- [file:line] <finding> → <fix>

TEST GAPS
- <behavior with no honest test, or "none">
```
