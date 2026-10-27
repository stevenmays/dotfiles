---
name: model-check
description: Model-check a stateful design with Quint before it ships — a fresh subagent writes the spec and its code mapping, mutants prove each invariant can fail, and the caller runs every check. Use for queues, retries, webhooks, payments, locks, and migration ordering. Not for UI or CRUD work.
---

# Model check

A Quint spec models a stateful design, and the checker searches for executions that break an invariant. The spec checks the design, not the code. Each spec action must map to one atomic unit in the code, or a pass proves nothing about the code.

## Scope

- `quint run` samples random executions. Report its passes as "random sampling". Sampling is the default, because it's cheap and scales with the number of cores.
- `quint verify` checks every execution up to a step bound. It needs Java, and it's slow: the worked example took 82 seconds at 8 steps and didn't finish 10 steps in 11 minutes. Without Java, the runner skips it.
- The runner, `scripts/check.py`, runs every `quint` command for one spec and applies the mechanical rules. The caller makes the judgment calls.
- The runner's output fields, the `quint` output formats, and the syntax pitfalls are in `references/quint.md`. A worked example is in `references/example-queue-consumer.qnt`.

## Inputs

The caller passes:

- The ticket type: `bug`, `feature`, or `new-flow`. When it's missing, use `feature` if code paths are in scope, else `new-flow`.
- The plan file path.
- The code paths in scope.
- The plan's "invariants and failure modes" list. When it's missing, the writer derives the invariants from the plan, and the result says so.
- The scratch dir, `<scratch>`. When it's missing, use the session scratchpad.

## Preflight

1. If the plan has no stateful flow to model, write `Model check: skipped — no stateful flow in the plan` to `<scratch>/model-check.md` and stop. This applies even when a caller forces the check, for example with `--full`. The caller continues without the gate.
2. Run `quint --version`. If `quint` is missing, write `Model check: skipped — quint is missing; install it with brew install quint` to `<scratch>/model-check.md` and stop. The caller continues without the gate.

## Phases

1. Write phase: the writer creates the spec and the mapping. See "Roles", "Write the spec", and "Write mutants".
2. Claims phase: see "Verify the mapping".
3. Run phase: the caller runs the runner and writes `<scratch>/model-check.md`. See "Run", "Witnesses", and "Result".

## Roles

- A fresh `general-purpose` subagent writes the spec and the mapping. Dispatch it through `mays:claude-subagents` with `model:` unset.
- The planner never writes specs, so the author never checks its own design.
- The writer can run `quint typecheck`, but never `quint run`, `quint verify`, or the runner. A writer that sees results can tune the spec until it passes.
- The caller runs the runner itself and reads its output. A subagent's account of a run isn't evidence.

The writer's prompt follows `mays:claude-subagents` and carries every input. It tells the writer to load `mays:model-check` and follow "Write the spec" and "Write mutants", plus `references/quint.md`. The writer creates one `<scratch>/model/<flow>.qnt` per flow, plus `<scratch>/model/mapping.md`, and nothing else.

## Ticket types

- `bug`: the current-code model must violate an invariant. Its counterexample must match the reported cause, not just any violation. The design model must pass.
  - If the current model can't reproduce the bug after 2 writer attempts, record "model didn't reproduce the bug" and skip the model gate. The caller shows that note at plan approval.
- `feature`, a change to an existing flow: the current-code model is expected to pass the existing invariants.
  - A current-code failure is a bug that already exists. Record it as a risk with its counterexample, and don't fix it. It gets no test hand-off: no fix is in scope, and no protection exists to revert.
  - The design must pass every old invariant that the current model passes, plus the new ones. List each old invariant that fails as a known failure.
- `new-flow`: model the design only.

## Write the spec

- **Environment failures:** model them, not only the happy path. Cover duplicate delivery, redelivery after a crash or timeout, out-of-order events, concurrent deliveries, a timeout after a side effect, and a partial failure between side effects.
- **Countable state:** the state must be able to represent each invariant's violation. Count anything that can happen twice or concurrently, such as owners, sends, or charges, in a map of integers. Never use a set for those: a set merges 2 concurrent owners into 1 and hides the bug the invariant guards against.
- **Atomicity:** one action is one atomic unit. That's one SQL statement, one conditional write, one external call, or a transaction only when its isolation level makes it atomic.
  - Split a read-then-write into 2 actions unless one statement or a lock makes it atomic.
  - Under Postgres READ COMMITTED, a `SELECT` followed by an `UPDATE` in one transaction isn't atomic.
- **Small bounds:** use 2 or 3 entities. Give every compared field equal values too, such as timestamps with 1-second resolution, so ties get tested.
- **Steps:** write one module per flow. The runner finds each step by its name:
  - `step` is the current code.
  - `stepDesign` is the proposed design.
  - Each mutant gets one `stepMut<Name>`.
  - A new flow has `stepDesign` and its mutants only.
- **Comments:** each action gets one short comment that says why it's atomic.
- **Mapping:** `mapping.md` is a table with one row per action. Each current-code row is one claim that `mays:claims-verification` can check.

```
| Model | Action | Code | Why it's atomic |
| --- | --- | --- | --- |
```

`Model` is `current` or `design`. `Code` is `path:line` for the current code, or the intended statement for the design.

## Write mutants

- Remove each protection the design adds, one at a time: a dedup, a lease, an ordering guard, a lock, or a conditional write. If protections deliberately overlap, remove them as a pair.
- Also remove each protection that already exists, so every invariant, old ones included, can be killed.
- Flip each boundary comparison, for example `<=` to `<`.
- Every invariant must be killed by at least one mutant. The runner runs each mutant once per invariant, and a `[violation]` in that run is a kill. It reports an invariant with no kill as `unkilled-invariant`, and a mutant with no kill as `useless-mutant`.

A surviving mutant has 4 possible causes:

- The protection is unnecessary.
- The invariant is too weak.
- The state can't represent the violation.
- Sampling missed it.

The `--budget` run already gives each mutant extra samples against the invariants that no mutant killed. Before you conclude, the caller asks the writer for a witness of the exact interleaving that the protection guards. The caller then reruns with `--verify`, which also checks each mutant against each invariant that sampling left unkilled. To check only a mutant that kills no invariant, pass `--verify-step stepMut<Name>` instead.

Then report which cause applies. A weak invariant or a state that can't represent the violation goes back to the writer. An unnecessary protection goes into the result as a finding for the plan.

## Verify the mapping

Run `mays:claims-verification` on the mapping's current-code rows. Inside `implement-ticket`, that happens in the same pass as the plan's claims. A standalone caller runs it alone. A false mapping claim sends the spec back to the writer once. If a claim is still false, record the gate as unverified and continue.

## Run

Run the runner on each spec, and save its output:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/model-check/scripts/check.py" <scratch>/model/<flow>.qnt \
  --main MODULE --invariants INVARIANTS --terminal TERMINAL --witnesses WITNESSES \
  --budget 60 --format md > <scratch>/model/<flow>.md
```

`MODULE` is the spec's module name, and `TERMINAL` is the terminal witness. `INVARIANTS` and `WITNESSES` are names separated by spaces. `references/quint.md` lists the defaults and the output fields.

After the fixed runs, the budget spends 60 seconds of sampling on every core. It first samples each mutant against the invariants that no mutant killed, then samples `stepDesign`. Add `--verify` only when a mutant survives the budget, or when an invariant guards money or security. Examples are a double charge, a cross-tenant leak, and an auth bypass. Act on the exit status:

| Exit | Verdict | Next step |
| --- | --- | --- |
| `0` | `pass` | Make the judgment calls that follow. |
| `1` | `fail` | The design violates an invariant. Record it as a finding for the plan, with its counterexample. |
| `2` | `invalid` | The check proves nothing. `references/quint.md` lists each problem code and its next step. A usage error also exits `2`, with its message on stderr. |
| `3` | `broken-spec` | A parse, type, or runtime error. Send the error to the writer. |
| `4` | none | `quint` is missing. Skip the gate, as "Preflight" says. |

The caller makes the judgment calls, never the runner:

- Does a current-code counterexample match the reported cause, and what does a failure mean for the ticket type? See "Ticket types".
- Which of the 4 causes explains a surviving mutant? See "Write mutants".
- Is a mapping claim wrong? See "Verify the mapping".

## Witnesses

A Quint witness is a state predicate. Quint reports the percentage of runs in which it held. A run counts when the witness holds in any state, the initial state included. So every witness must be false at the initial state. The runner samples the initial states alone and reports a witness that holds there as `witness-true-at-init`. The spec goes back to the writer.

- **Reachability witnesses** prove that a failure path happened, such as a crash that leaves an orphaned claim. Pass them as `--witnesses`. The runner reports one at 0% on `stepDesign` as `unreached-failure-path`. Rerun with a larger `--budget` and a higher `--max-steps`. A witness still at 0% goes back to the writer.
- **A forbidden state** is an invariant. Never use it as a witness.
- **Terminal witness:** use one, such as `settled`, to show that runs reach a finished state. Pass it as `--terminal`. The runner reports `vacuous` for an `[ok]` run with the terminal witness at 0%, or with every run stopped at the initial state. The step never fires or never settles, so the spec goes back to the writer.
  - The terminal witness must be reachable only through the full flow. Quint ends a run silently when no action is enabled, so a flow that deadlocks early can still pass.
  - Don't judge by other trace-length statistics: they flag healthy runs and miss broken ones.
- **Branch coverage:** to show that a particular branch fires, add a ghost variable that the branch sets.

## Retries

Each phase gets at most 2 writer attempts: the write phase, the claims phase, and the run phase. After that, record the failure in the result and continue. Never block a headless run.

## Result

Build `<scratch>/model-check.md` from each flow's runner output. That output holds the result line, a table of every command with its result, the mutant matrix, and each counterexample as numbered steps. Add these parts:

- The judgment on the current code in the result line.
- The full mapping table from `mapping.md`. Plan reviewers get only the spec and this file, and they need the table to attack the atomicity claims.
- On each counterexample step, the `path:line` from that action's mapping row.
- The test hand-offs.

```
Model check: <flow> — <n> invariants, <k>/<m> mutants killed; <random sampling, N runs ≤K steps | bounded check to K steps>; current code: <passes | fails <invariant> (matches reported bug | pre-existing bug)>
```

The runner writes the line up to `fails <invariant>`, and the caller adds `(matches reported bug)` or `(pre-existing bug)`. The runner drops the current-code part when the spec has no `step`. For a `fail` verdict, it appends `; design: fails <invariant>`, and for `invalid`, it appends `; invalid: <codes>`. For `broken-spec`, it writes `broken spec: <error>` in place of the counts. A skipped or unverified gate says so, with the reason.

Test hand-offs come from 2 sources only: each killed mutant's counterexample, and a `bug` ticket's current-code counterexample. A bug that already exists on a `feature` ticket is a risk only, as "Ticket types" says. Each hand-off follows 2 rules:

- The hand-off is a regression test at an honest seam. Reverting the protection in the real code must make that test fail.
- A race that no test seam can reproduce is recorded as untested, with its trace.

## Artifacts

- Specs and traces live in `<scratch>` and are never committed to the repo. A committed spec drifts from the code unless conformance tests replay it.
- The caller attaches the specs and key traces wherever it logs results.
