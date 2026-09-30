---
name: claims-verification
description: Check the factual claims a plan makes about existing code against the repo — extract atomic claims, have a fresh subagent answer neutral questions without seeing the plan, then score each claim. Use after a plan is drafted and before adversarial review, or whenever a workflow asks to verify a plan's claims.
---

# Claims verification

A plan can reason soundly from a wrong fact about the code. Claims verification catches the wrong fact. It can't flag a claim the plan never made, and it can't judge reasoning or omissions: `mays:adversarial-review` owns those. So verification runs first, and the adversaries attack reasoning built on checked facts.

## Oracle

- Every verdict cites `file:line` or command output.
- Check the same working tree the author read. Another ref turns true claims into false contradictions.
- Model recall is never evidence. A verifier that shares the author's priors confirms the same hallucination.
- One Claude verifier is enough. The repo is the oracle, not model judgment, so a second model family adds nothing. Don't turn this skill into an `adversarial-review`-style pair.

## Extract claims

The orchestrator extracts the claims, because it already holds the plan.

- Extract only claims about the code as it exists now. A proposal such as "add X" or "rename Y" isn't a claim. Whether it's a good idea is adversarial review's job.
- Make each claim atomic, one fact each, with ids `C1` to `Cn`.
- Extract implicit claims too. Look for these kinds:
  - Existence: a file, symbol, flag, config key, command, or test.
  - Signatures, types, defaults, and return values.
  - Counts and completeness. "Update the two callers" claims that exactly two callers exist.
  - Absence. "Nothing else reads this field" and "no migration needed" are both absence claims.
  - Existing behavior the plan relies on.
  - Repo conventions the plan assumes.
- When the plan argues from a premise, extract the premise and leave the inference to adversarial review. From "X is only called from Y, so the lock is safe", extract "X is only called from Y".
- Mark a claim `unverifiable` when no oracle is in reach: third-party API behavior, production data, runtime timing, or a guess the plan labels as a guess. List it, but don't send it to the verifier.

## Write neutral questions

The verifier must not anchor on the claim, so it never sees one.

- Write one open question per claim. Ask for the fact, never the claimed answer.
  - Bad: "Confirm `retry_webhook` has two callers."
  - Good: "List every call site of `retry_webhook`, with file:line."
- Never ask a yes/no question. It leaks the claim.
- Scope completeness and absence questions to the whole repo, not the file the plan names.
- Number each question after its claim: `Q3` asks about `C3`.

## Dispatch a blind verifier

Dispatch through `mays:claude-subagents`:

- Use `subagent_type: "Explore"`, which has no `Edit` or `Write` tool, with `model: "sonnet"`. Sonnet is enough because every answer carries a citation you check.
- Split more than about 15 questions into batches. Launch the batches concurrently in one message.
- The prompt carries only the questions and the repo path. It never carries the plan, the ticket, the claims, or the author's reasoning.
- State the reason generically, as the brief does. Never name the ticket, the plan's goal, or a decision from it, because any hint of the plan anchors the verifier.

Fill the placeholders in this brief:

```
Answer factual questions about the working tree at {REPO_PATH}.
Your answers check the facts in a plan you won't see.

Rules:
- Answer only from files you read and commands you run.
- Read-only. No web.
- A guess is worse than NOT FOUND.
- No preamble.

Answer each question in this format:
Q<n>: <answer>
EVIDENCE: <file:line — quoted line> or <command> → <relevant output>

When nothing turns up:
Q<n>: NOT FOUND: <what you searched>

Questions:
{QUESTIONS}
```

## Score

Compare each answer with its claim yourself:

- `supported`: the evidence matches the claim.
- `contradicted`: the evidence shows the claim is false. Open the cited line yourself before you act, because verifiers misread too.
- `unsupported`: the answer is `NOT FOUND` or has no citation. Never promote an unsupported claim to supported.
- `unverifiable`: assigned at extraction.

## Act

Every branch has a default that needs no human.

- Send contradicted and unsupported claims back to the plan's author once. Include each question and the verifier's answer with its evidence, not just "wrong".
  - Claude author: use `SendMessage`.
  - External author: re-run it with the findings.
  - The orchestrator wrote the plan: fix it yourself.
- A contradicted claim that a step depends on changes that step, not just its wording.
- The corrected plan replaces the plan file the caller handed in, so the next gate reviews the corrected plan.
- Extract claims from the changed steps only. Verify them with a fresh blind verifier.
- After that one round, a claim can still be contradicted or unsupported. Continue anyway, and append the claim to the plan under `## Known contradictions` with its evidence. The next reviewer and the human then see it. Never drop one silently.

## Result

```
CLAIMS: <n> extracted — <s> supported, <c> contradicted, <u> unsupported, <v> unverifiable; <r> corrected

CONTRADICTED
- C<n> "<claim>" — <file:line evidence> → <corrected | known contradiction>

UNSUPPORTED
- C<n> "<claim>" — searched <what> → <corrected | known contradiction>

UNVERIFIABLE
- C<n> "<claim>" — <why no oracle is in reach>
```

Save the full table of claims, questions, answers, and verdicts with this result. The caller names the scratch path, else use the session scratchpad.
