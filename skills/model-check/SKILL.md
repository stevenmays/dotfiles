---
name: model-check
description: Check the failure paths of a design before it ships — races, crashes, redelivery, duplicate delivery, out-of-order events, and timeouts. A fresh subagent writes a small model of the design in Quint or in Python, and a runner searches the model for an order of events that breaks one of the plan's rules. Mutants prove that each rule can fail. After implementation, a conformance phase checks the code against the model. Use when a plan relies on a protection against a race or a failure, such as a lease, dedup, lock, conditional write, ordering guard, or idempotency key. Not for UI work, CRUD work, or pure money math such as rounding or proration, because property-based tests catch those more cheaply.
---

# Model check

A model check tests a design against bad timing before anyone writes the code. A subagent writes a spec: a small model of the design's state and of the actions that change that state. A runner then tries the actions in many orders and looks for an order that breaks one of the plan's rules.

The spec covers only the failure paths that can break the plan's protections, never the whole system. The spec checks the design, not the code. A pass says something about the code only when each spec action matches one atomic unit in the code.

## Terms

- **Spec:** the model file. Write one spec per flow.
- **Action:** one change to the state, such as "claim the row". One action is one atomic unit: nothing else can run in the middle of it.
- **Step:** one version of the flow, as the set of actions that can run. `step` is the current code, and `stepDesign` is the proposed design.
- **Invariant:** a rule that must hold in every state, such as "a message has at most 1 owner".
- **Counterexample:** the actions, in order, that lead to a state that breaks an invariant.
- **Mutant:** a copy of the design with one protection removed. A mutant must break an invariant. That break is a kill, and it proves that the invariant can fail.
- **Witness:** a condition that must come true in some run. It proves that the runs got that far.

## Roles

- **The caller** is the session that loads this skill. It runs every check and makes every judgment call.
- **The writer** is a fresh `general-purpose` subagent. It writes the spec and the mapping. Dispatch it through `claude-subagents` with `model:` unset.
- **The runner** is `scripts/check.py`. It runs every check for one spec and applies the mechanical rules.

Each role has limits:

- The planner never writes specs, so the author never checks its own design.
- With Quint, the writer can run `quint typecheck`. The writer never runs `quint run`, `quint verify`, or the runner. A writer that sees results can change the spec until it passes.
- The caller runs the runner itself and reads its output. A subagent's account of a run isn't evidence.

The writer's prompt follows `claude-subagents` and carries every input, plus the engine. It tells the writer to load `model-check`, and to follow "Write the spec", "Write mutants", and the engine's reference file. The writer creates one spec per flow in `<scratch>/model/`, plus `<scratch>/model/mapping.md`, and nothing else.

## Engines

The runner checks a spec with one of 2 engines. The spec's file extension picks the engine.

| | Quint | Python |
| --- | --- | --- |
| Spec file | `<flow>.qnt` | `<flow>.py` |
| Needs | `quint`, installed with `brew install quint`. `--verify` also needs Java. | Python 3.9 or later |
| How it checks | `quint run` tries random runs. With `--verify`, `quint verify` also checks every run up to a step bound. | The runner visits every state that the spec can reach. |
| Report a pass as | "random sampling", or "bounded check" with `--verify` | "full search", or "search to K steps" when a limit stops the search |
| Limit | Sampling can miss a rare path. `quint verify` is slow: the worked example took 82 seconds at 8 steps and didn't finish 10 steps in 11 minutes. | The search of a step stops past 500,000 states or 600 seconds. The worked example has 1,296 states and takes under 1 second. |
| Reference | `references/quint.md` | `references/python.md` |
| Worked example | `references/example-queue-consumer.qnt` | `references/example-queue-consumer.py` |

Each reference file lists the runner's options, its output fields, and the engine's pitfalls.

## Inputs

The caller passes:

- The ticket type: `bug`, `feature`, or `new-flow`. When it's missing, use `feature` if code paths are in scope, else `new-flow`.
- The plan file path.
- The code paths in scope.
- The plan's "invariants and failure modes" list. When it's missing, the writer derives the invariants from the plan, and the result says so.
- The scratch dir, `<scratch>`. When it's missing, use the session scratchpad.
- The engine: `quint` or `python`. When it's missing, "Preflight" picks one.

## Preflight

1. If the plan relies on no protection against a race or a failure, write `Model check: skipped — no failure path to model` to `<scratch>/model-check.md` and stop. This rule applies even when a caller forces the check, for example with `--full`. The caller continues without the gate.
2. Pick the engine. Use the caller's engine when it names one. Otherwise run `quint --version`: use Quint when the command works, else Python.
3. If the caller names Quint and `quint` is missing, use Python. Note the switch in the result.

## Phases

1. Write phase: the writer creates the spec and the mapping. See "Roles", "Write the spec", and "Write mutants".
2. Claims phase: see "Verify the mapping".
3. Run phase: the caller runs the runner and writes `<scratch>/model-check.md`. See "Run", "Witnesses", and "Result".
4. Conformance phase: after implementation, the caller checks the code against the mapping's design rows. See "Check conformance".

## Ticket types

- `bug`: the current-code step must break an invariant. Its counterexample must match the reported cause, not just any break. The design step must pass.
  - If the current-code step can't reproduce the bug after 2 writer attempts, record "model didn't reproduce the bug" and skip the model gate. The caller shows that note at plan approval.
- `feature`, a change to an existing flow: the current-code step is expected to pass the existing invariants.
  - A current-code failure is a bug that already exists. Record it as a risk with its counterexample, and don't fix it. It gets no test hand-off: no fix is in scope, and no protection exists to revert.
  - The design must pass every old invariant that the current-code step passes, plus the new ones. List each old invariant that fails as a known failure.
- `new-flow`: model the design only.

## Write the spec

- **Failure paths:** each spec asks one question: can a failure in the environment break a protection that the plan relies on? The protections and invariants in the plan's "invariants and failure modes" list set the scope. When that input is missing, the list the writer derived sets it. Cut any invariant, action, or variable outside that scope.
  - **Keep it small:** keep a state variable only if an invariant, an action's guard, or a witness reads it. Model business logic as one action that can succeed or fail. Give an external system only the behavior the race depends on, such as delivering twice, delivering out of order, or timing out after a side effect. Reduce payloads to IDs and counters. Model the happy path only as far as the terminal witness.
  - **Size limit:** use at most 8 state variables and 3 invariants per spec. Trim a bigger spec by the "Keep it small" rule first. If it's still over either limit, split it into 2 flows. The runner reports a spec over either limit with the warning `spec-over-budget`.
  - **Assumptions:** list in `mapping.md` every behavior the spec assumes and doesn't model, such as "the Postgres row lock holds" or "SQS delivers every message at least once". A pass holds only while those assumptions hold.
- **Environment failures:** check each protection against these 6: duplicate delivery, redelivery after a crash or timeout, out-of-order events, concurrent deliveries, a timeout after a side effect, and a partial failure between side effects. Model each one that can reach a protection, even when the plan's list leaves it out. Skip each one that can't.
- **Count, don't collect:** the state must be able to show each invariant's break. Count anything that can happen twice or at the same time, such as owners, sends, or charges, in a map of integers. Never use a set for those: a set merges 2 owners into 1 and hides the bug the invariant guards against.
- **One action, one atomic unit:** that unit is one SQL statement, one conditional write, one external call, or a transaction only when its isolation level makes it atomic.
  - Split a read-then-write into 2 actions unless one statement or a lock makes it atomic.
  - Under Postgres READ COMMITTED, a `SELECT` followed by an `UPDATE` in one transaction isn't atomic.
- **Small bounds:** use 2 or 3 entities. Give every compared field equal values too, such as timestamps with 1-second resolution, so ties get tested.
- **Steps:** the runner finds each step by its name:
  - `step` is the current code.
  - `stepDesign` is the proposed design.
  - Each mutant gets one `stepMut<Name>`.
  - A new flow has `stepDesign` and its mutants only.
- **Comments:** each action gets one short comment that says why it's atomic.
- **Mapping:** `mapping.md` is a table with one row per action. Each current-code row is one claim that `claims-verification` can check. Each design row becomes one claim in the conformance phase.

```
| Model | Action | Code | Why it's atomic |
| --- | --- | --- | --- |
```

`Model` is `current` or `design`. `Code` is `path:line` for the current code, or the intended statement for the design.

After the table, `mapping.md` has an `## Assumptions` list with one line per assumption:

```
## Assumptions

- <behavior the spec assumes and doesn't model>
```

## Write mutants

- Remove each protection the design adds, one at a time: a dedup, a lease, an ordering guard, a lock, or a conditional write. If protections overlap on purpose, remove them as a pair.
- Also remove each protection that already exists, so every invariant, old ones included, can be killed.
- Flip each boundary comparison, for example `<=` to `<`.
- At least one mutant must kill each invariant. The runner checks each mutant against each invariant. It reports an invariant with no kill as `unkilled-invariant`, and a mutant with no kill as `useless-mutant`.

A mutant that survives has 4 possible causes:

- The protection is unnecessary.
- The invariant is too weak.
- The state can't show the break.
- The check missed the break: sampling didn't reach it, or the search stopped at a limit.

Rule out a missed break first:

- **Quint:** the `--budget` run already gives each mutant extra samples against the invariants that no mutant killed. The caller asks the writer for a witness of the exact order of events that the protection guards against. The caller then reruns with `--verify`, which also checks each mutant against each invariant that sampling left unkilled. To check only a mutant that kills no invariant, pass `--verify-step stepMut<Name>` instead.
- **Python:** a full search can't miss a break. If the search stopped at a limit, raise `--max-steps`, `--max-states`, or `--run-timeout` and rerun.

Then report which cause applies. A weak invariant, or a state that can't show the break, goes back to the writer. An unnecessary protection goes into the result as a finding for the plan.

## Verify the mapping

Run `claims-verification` on the mapping's current-code rows. Inside `implement-ticket`, that check happens in the same pass as the plan's claims. A standalone caller runs it alone. A false mapping claim sends the spec back to the writer once. If a claim is still false, record the gate as unverified and continue.

## Run

Run the runner on each spec, and save its output. For a Quint spec:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check.py" <scratch>/model/<flow>.qnt \
  --main MODULE --invariants INVARIANTS --terminal TERMINAL --witnesses WITNESSES \
  --budget 60 --format md > <scratch>/model/<flow>.md
```

For a Python spec:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check.py" <scratch>/model/<flow>.py \
  --invariants INVARIANTS --terminal TERMINAL --witnesses WITNESSES \
  --format md > <scratch>/model/<flow>.md
```

`MODULE` is the Quint spec's module name, and `TERMINAL` is the terminal witness. `INVARIANTS` and `WITNESSES` are names separated by spaces.

The Quint command samples a fixed number of runs, and then `--budget 60` adds 60 seconds of sampling on every core. The budget first samples each mutant against the invariants that no mutant killed, then samples `stepDesign`. Add `--verify` only when a mutant survives the budget, or when an invariant guards money or security. Examples are a double charge, a cross-tenant leak, and an auth bypass. A Python spec needs neither option, because its search already checks every state.

Act on the exit status:

| Exit | Verdict       | Next step                                                                                                                                   |
| ---- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `0`  | `pass`        | Make the judgment calls that follow.                                                                                                        |
| `1`  | `fail`        | The design breaks an invariant. Record it as a finding for the plan, with its counterexample.                                               |
| `2`  | `invalid`     | The check proves nothing. The engine's reference file lists each problem code and its next step. A usage error also exits `2`, with its message on stderr. |
| `3`  | `broken-spec` | The spec has a syntax error, a type error, or an error while it runs. Send the error to the writer.                                         |
| `4`  | none          | `quint` is missing for a Quint spec. Have the writer rewrite the spec in Python. That return counts as a run-phase attempt under "Retries". |

A spec over the size limit in "Write the spec" gets a `spec-over-budget` warning in the output's `## Warnings` section. The warning never changes the verdict or the exit status. On that warning, the caller sends the spec back to the writer once to trim or split it. That return counts as a run-phase attempt under "Retries". If the returned spec is still over the limit, the caller runs it as is, and the result notes the warning.

The caller makes the judgment calls, never the runner:

- Does a current-code counterexample match the reported cause, and what does a failure mean for the ticket type? See "Ticket types".
- Which of the 4 causes explains a mutant that survives? See "Write mutants".
- Is a mapping claim wrong? See "Verify the mapping".

## Witnesses

A witness is a condition on the state. Quint reports the percentage of runs in which a witness held, and Python reports the number of states. Every witness must be false at the initial state. A witness that holds there comes true even when no action ever runs, so it proves nothing. The runner reports such a witness as `witness-true-at-init`, and the spec goes back to the writer.

- **Reachability witnesses** prove that a failure path happened, such as a crash that leaves an orphaned claim. Pass them as `--witnesses`. The runner reports one that never holds on `stepDesign` as `unreached-failure-path`.
  - With Quint, rerun with a larger `--budget` and a higher `--max-steps`. A witness still at 0% goes back to the writer.
  - With Python, the witness goes back to the writer, unless the search stopped at a limit. Then raise the limit and rerun first.
- **A forbidden state** is an invariant. Never use it as a witness.
- **Terminal witness:** use one, such as `settled`, to show that runs reach a finished state. Pass it as `--terminal`. The runner reports `vacuous` when a step breaks no invariant and its terminal witness never holds, or when every run stops at the initial state. The step never fires or never settles, so the spec goes back to the writer.
  - The terminal witness must be reachable only through the full flow. Neither engine reports a run that ends early because no action can fire. So a flow that gets stuck early can still pass.
  - Don't judge by other trace-length statistics: they flag healthy runs and miss broken ones.
- **Branch coverage:** to show that one branch fires, add a state variable that only that branch sets, and a witness that reads it.

## Retries

Each phase gets at most 2 writer attempts: the write phase, the claims phase, and the run phase. After that, record the failure in the result and continue. Never block a headless run. The conformance phase sends nothing back to the writer, because it only reports.

## Result

Build `<scratch>/model-check.md` from each flow's runner output. That output holds the result line, a table of every check with its result, the mutant matrix, each counterexample as numbered steps, and any warnings. Add these parts:

- The judgment on the current code in the result line.
- The full mapping table and the assumptions list from `mapping.md`. Plan reviewers get only the spec and this file. They need the table to attack the atomicity claims, and the list to attack what the spec didn't model.
- On each counterexample step, the `path:line` from that action's mapping row.
- The test hand-offs.

```
Model check: <flow> — <n> invariants, <k>/<m> mutants killed; <random sampling, N runs ≤K steps | bounded check to K steps | full search, N states | search to K steps, N states>; current code: <passes | fails <invariant> (matches reported bug | pre-existing bug)>
```

The runner writes the line up to `fails <invariant>`, and the caller adds `(matches reported bug)` or `(pre-existing bug)`. The runner drops the current-code part when the spec has no `step`. For a `fail` verdict, it appends `; design: fails <invariant>`, and for `invalid`, it appends `; invalid: <codes>`. For `broken-spec`, it writes `broken spec: <error>` in place of the counts. A skipped or unverified gate says so, with the reason.

Test hand-offs come from 2 sources only: each killed mutant's counterexample, and a `bug` ticket's current-code counterexample. A bug that already exists on a `feature` ticket is a risk only, as "Ticket types" says. Each hand-off follows 2 rules:

- The hand-off is a regression test at an honest seam. Reverting the protection in the real code must make that test fail.
- A race that no test seam can reproduce is recorded as untested, with its counterexample.

## Check conformance

A pass says nothing about the code unless each spec action matches one atomic unit in the code. The claims phase checks only the current-code rows, because the design code doesn't exist yet. The conformance phase checks the design rows after implementation. Inside `implement-ticket`, it runs before code review.

When the write phase didn't run, or the model check was skipped, skip this phase. Write `Model conformance: skipped — <reason>` to `<scratch>/model-conformance.md`.

Run `claims-verification` on the design rows of `<scratch>/model/mapping.md`, against the implemented working tree. Each design row is one claim with 2 parts:

- The code implements the row's action as the row's intended statement.
- That code is atomic for the reason in the row's "Why it's atomic" column.

When that reason rests on a behavior in the mapping's `## Assumptions` list, such as "the Postgres row lock holds", the verifier checks only that the code uses that mechanism. The assumption stays an assumption, as in the run phase. When the reason rests on a behavior outside the repo that the list omits, the row scores `unverifiable`, and its false-row entry names the missing assumption.

The verifier cites the `path:line` that implements each row. A row holds only when its claim scores `supported`. Every other score makes it a false row.

Write `<scratch>/model-conformance.md`. Its first line is the result line:

```
Model conformance: <k>/<n> design rows hold
```

After the result line, list each false row: its action, its intended statement, and what the code at `path:line` does in its place. For an unsupported row, write `not found` and the search the verifier ran. For an unverifiable row, write why no oracle is in reach.

A false row means the code breaks an assumption that the spec's pass depends on, so the pass no longer covers the code. The model check only reports. Skip the "Act" step of `claims-verification`, because the caller decides what to do with a false row.

## Artifacts

- Specs and counterexamples live in `<scratch>` and are never committed to the repo. A committed spec drifts from the code unless tests replay its counterexamples.
- The caller attaches the specs and the main counterexamples wherever it logs results.
