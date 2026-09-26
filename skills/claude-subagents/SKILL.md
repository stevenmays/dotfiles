---
name: claude-subagents
description: Dispatch planning, review, implementation, or a scoped question to a fresh Claude subagent with the Agent tool — which subagent type and model to pick, what the prompt must carry, and how to check what comes back. Use whenever a workflow hands work to a Claude subagent, including the Claude half of adversarial-review.
---

# Claude subagents

Send work to a fresh Claude context with the `Agent` tool. The session orchestrates; the subagent reads the code and does the work, so the session's context stays small.

## Pick the agent

| Work | `subagent_type` |
| --- | --- |
| Plan, review, implementation | `general-purpose` |
| One scoped read-only question | `Explore` |

- Leave `model:` unset for strong work — planning, implementation, debugging, adversarial review — so `CLAUDE_CODE_SUBAGENT_MODEL` picks the strong model for this machine.
- Pin `model: "sonnet"` only where a test, lint, compile, or known-target grep verifies the output. Never name any other model.
- Never `subagent_type: "fork"`. A fork re-sends the whole conversation.

## Write the prompt

Fresh context, small prompt. The subagent sees none of this conversation. Give it what the conversation holds and the repo cannot show; give paths, not file contents, for everything it can read itself. The prompt carries:

1. The reason: the larger task, who it's for, and what the output enables.
2. Decisions already made, with their why: user preferences, constraints, non-goals, and approaches already rejected. Without them the subagent re-decides from scratch and can undo them.
3. Exact file paths.
4. The rules that apply.
5. The definition of done.
6. The judgment calls it owns, and when to stop and report instead.
7. The output format.

A `general-purpose` subagent loads the user and project `CLAUDE.md`; an `Explore` agent loads neither, so state any convention its answer depends on.

Inline text a reviewer must judge, such as the ticket and the plan, instead of a path. The external counterpart in `mays:external-subagents` then gets identical input.

## Roles

| Role | Writes | Contract |
| --- | --- | --- |
| Planner | Nothing | Reads the code. Its final message is the deliverable. |
| Reviewer | Nothing | Read-only, never edits. Same brief as its external counterpart apart from tool guidance. Gets the ticket and the artifact, never the author's reasoning: a reviewer that reads the justification first confirms it instead of attacking it. |
| Implementer | The change and its tests | See below. |

The implementer:

- Builds exactly the spec and writes the tests the change needs. No unrelated refactors; match surrounding code.
- Stops once its change and its own new tests pass. It never runs the full suite or loops on failures.
- Stops and reports when the spec turns out to be wrong, instead of improvising.

## Run and check

- Launch concurrent agents in one message, and keep working while they run.
- Continue an agent with `SendMessage`, not a new brief.
- The final report is not evidence. Read the diff yourself, and verify each finding against the code before acting on it.

## Escalation

1. A failing check goes to a `model: "sonnet"` agent with only the failure output and the files it names.
2. A failure that survives 2 attempts gets one fresh strong agent, `model:` unset.
3. Still failing: stop and report.
