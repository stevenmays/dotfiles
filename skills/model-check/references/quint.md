# Quint reference

These facts hold for `quint` `0.33.0`. The runner, `scripts/check.py`, runs every command and parses all output. Read the format notes here to debug the runner or to run a command by hand. Before you use a flag by hand, confirm it in `quint <command> --help` for the installed version. `quint verify --help` prints without Java.

## Commands

| Command | Use |
| --- | --- |
| `quint --version` | Record the version in the result file. |
| `quint typecheck FILE` | Run it first. Exit `0` means the spec parses and typechecks. Any other status means a broken spec. |
| `quint run FILE ...` | Random sampling: up to `--max-samples` random runs of at most `--max-steps` steps each. |
| `quint verify FILE ...` | Bounded check of every execution up to `--max-steps`, through the Apalache model checker. It needs Java. |

## Runner

`check.py SPEC --main MODULE --invariants NAMES --terminal WITNESS` takes these options:

- `--witnesses NAMES`: the reachability witnesses.
- `--steps NAMES`: the steps to run. The default is `step`, `stepDesign`, and every `stepMut<Name>` action in the spec. The list must hold `stepDesign`. Any other action without parameters whose name starts with `step` is a usage error, so a misnamed mutant can't drop out silently.
- `--samples`: `--max-samples` for each fixed run and each budget chunk. The default is 20000, and the minimum is 10000.
- `--max-steps`: `--max-steps` for each run, and the highest `quint verify` bound. The default is 30.
- `--seed`: the default is 7, so a rerun explores the same runs. Each budget chunk gets its own seed, derived from this one.
- `--budget SECONDS`: extra sampling after the fixed runs. The default is 0, which turns it off. See "Sampling budget".
- `--workers N`: the number of `quint` processes at once. The default is the number of cores.
- `--run-timeout SECONDS`: the time limit for each `quint run`. The default is 600. The runner starts each run in its own process group and kills the group at the limit.
- `--verify`: also run `quint verify` when `java -version` succeeds. It checks `stepDesign` against every invariant, and each mutant against each invariant that sampling left unkilled.
- `--verify-step NAME`: verify only this step, and repeat the option for more. A mutant is checked against each invariant it hasn't killed. This option turns on `--verify`.
- `--verify-budget`: the time limit in seconds for each verify attempt. The default is 300.
- `--format md`: print markdown for the result file instead of JSON.

The exit status follows the verdict: `0` for `pass`, `1` for `fail`, `2` for `invalid`, and `3` for `broken-spec`. A usage error exits `2`, a missing `quint` exits `4`, and a crash in the runner exits `3`. These 3 print only a message on stderr. A spec that isn't readable UTF-8 text is a usage error.

The JSON output has these fields:

| Field | Holds |
| --- | --- |
| `verdict` | `pass`, `fail`, `invalid`, or `broken-spec`. |
| `result_line` | The result line, without the caller's judgment on the current code. |
| `problems` | One entry for each broken rule, with a `code` and a `message`. |
| `matrix` | For each mutant and invariant: `true` for a kill, `false` for a survivor, or `null` for an error. |
| `kills` | For each mutant and invariant: what found the kill, `sampling`, `budget`, or `verify`, or `null` for none. |
| `current` | For `step`: its `result`, the `violated` invariants, `counterexamples` by invariant, and `explored`. It's `null` when the spec has no `step`. |
| `design` | The same fields for `stepDesign`. `explored` is the smallest total of runs across the passed invariants, budget included. A violation in `quint verify` also sets `result` to `fail`. |
| `init_probe` | The run that samples initial states only: its `command`, `result`, `explored`, and the trace count for each witness. |
| `runs` | One entry for each fixed run: the exact `command`, `result` (`ok`, `violation`, `error`, or `timeout`), `explored`, the trace count for each witness, `max_length`, `seconds`, and the `error` or the `counterexample`. |
| `budget` | `null` without `--budget`. Otherwise `status`, `spent` seconds, `workers`, `chunk_samples`, and one entry for each target: the first chunk's `command`, every chunk's seed in `seeds`, the summed `explored` and witness trace counts, and the `violated` invariants with their `counterexamples`. |
| `typecheck` | `ok`, the `command`, and the `error` text. |
| `verify` | One entry for each verified step: `status`, the `invariants` it checked, the largest finished `bound`, the `result`, the `violated` invariants with their `counterexamples`, `timed_out`, and each attempt with its `command`. It's empty without `--verify`. |
| `quint_version`, `java`, `spec`, `main`, `samples`, `max_steps`, `seed`, `workers`, `invariants`, `terminal`, `witnesses`, `steps` | The inputs and the tool versions. |

A counterexample is a list of steps, and step 0 is `init`. Each step holds the `action` from `mbt::actionTaken`, its `picks` from `mbt::nondetPicks`, and the full `state`. A `quint verify` counterexample has no action or picks, because Apalache traces carry no `mbt::` fields.

The problem codes use the totals over the fixed runs and the budget:

| Code | Rule | Next step |
| --- | --- | --- |
| `witness-true-at-init` | A witness holds in an initial state. | Send the spec back to the writer. |
| `vacuous` | A passed step and invariant has its terminal witness at 0%, or every run stopped at the initial state. | Send the spec back to the writer. |
| `unreached-failure-path` | A reachability witness is at 0% on `stepDesign`. | Rerun with a larger `--budget`, then send the spec back to the writer. |
| `unkilled-invariant` | No mutant kills the invariant. | If no mutant targets it, send it back to the writer for one. Otherwise, find the cause as for a surviving mutant. |
| `useless-mutant` | The mutant kills no invariant. | Find the cause, as "Write mutants" in `SKILL.md` says. |
| `insufficient-samples` | A passed step and invariant explored fewer runs than `--samples`, or printed no explored count. | Rerun once, then record it in the result. |
| `run-timeout` | A `quint run` passed `--run-timeout`. | Send the spec back to the writer for smaller bounds, or raise `--run-timeout`. |
| `verify-incomplete` | `--verify` finished no bound on `stepDesign`: a timeout before the first bound, no Java, or an Apalache error. | Raise `--verify-budget` or fix the error, then rerun. Without Java, drop `--verify` and report random sampling only. |

## Sampling budget

`--budget` runs chunks of `--samples` runs on every worker until the time is spent. A chunk that is already running finishes, so the run can end a few seconds late.

1. The runner samples each mutant against each invariant that no mutant killed, in turn. A violation is a kill, and that invariant gets no more chunks. This part gets at most half the budget.
2. The rest of the budget samples `stepDesign` against every invariant at once, with every witness. A violation stops it, and the design fails.

When a chunk with several invariants finds a violation, the runner reruns its failing seed with `--max-samples=1` once for each invariant alone. The same seed replays the same run, so each violated invariant gets its own counterexample.

Each chunk's seed is a hash of `--seed` and the chunk number. quint advances each run's seed upward from `--seed`, so chunks with nearby seeds could repeat runs. `--n-threads` doesn't speed up one `quint run`: 100000 runs took 9.2 seconds at 14 threads and 9.4 at 1. So the runner gets its speed from parallel processes.

## Sample with `quint run`

The runner runs this command once for each step and invariant, here on the worked example, `example-queue-consumer.qnt`:

```
quint run example-queue-consumer.qnt --main=queue_consumer --step=stepMutNoLease --invariant=oneOwner \
  --max-samples=20000 --max-steps=30 --seed=7 --mbt --out-itf=stepMutNoLease.oneOwner.itf.json \
  --witnesses settled orphanClaim
```

The runner passes these flags on every run:

- `--main`: the module name. Quint derives the default from the file name. A wrong name fails with `error: [QNT405] Main module NAME not found`.
- `--step`: `step`, `stepDesign`, or one `stepMut<Name>`. A misspelled name stops the run with `error: [QNT404] Name '...' not found`.
- `--max-samples`: without `--seed`, the default is 10000. With `--seed`, it drops to 1, and that 1 run still prints `[ok]`.
- `--max-steps`: the default is 20. Raise it when the terminal witness fires in few runs.
- `--seed`: a fixed value, so a rerun explores the same runs.
- `--invariant`: 1 invariant, so each kill is credited to that invariant. Budget chunks on `stepDesign` use `--invariants`, which checks several names together. Only `--invariants` prints the `Use --seed=0x...` line for a violation.
- `--witnesses`: names of `val` definitions, separated by spaces. The terminal witness is always first, because witness lines are the only lines that print the explored count.
- `--mbt`: adds `mbt::actionTaken` and `mbt::nondetPicks` to every state, so each counterexample step names its action and arguments. Quint labels it experimental. It doesn't change the result or witness lines.
- `--out-itf`: writes the run as ITF JSON. Quint writes the file for an `[ok]` run too, as an example run, so the runner reads it only on a violation.

## Check bounds with `quint verify`

The runner runs this command on each verified step at each bound:

```
quint verify example-queue-consumer.qnt --main=queue_consumer --step=stepDesign \
  --invariants noLostMessages atMostOnce oneOwner --max-steps=8 --out-itf=verify.8.itf.json
```

- `quint verify` takes `--main`, `--step`, `--invariants`, and `--max-steps`, whose default is 10. It has no `--max-samples`, `--seed`, or `--witnesses`, so the runner checks witnesses with `quint run`.
- Run time grows fast with `--max-steps`. The worked example's `stepDesign` took 13 seconds at 6 steps and 82 seconds at 8.
- `quint verify` starts an Apalache server, a Java process, in its own process group. The Java process can outlive `quint`, so the runner kills the whole group after each attempt.
- Apalache writes `_apalache-out/` into the working directory, so the runner runs `quint verify` in a temporary directory.
- `--out-itf` writes a file only for a violation. The `--help` text says that it suppresses console output, but in `0.33.0` it doesn't.
- A pass prints `[ok] No violation found (...)` with no explored count. A failure prints `[violation] Found an issue (...)`, then `error: found a counterexample`.
- For 2 or more invariants, a failure also prints a `❌ NAME` line for each invariant that failed. On a mutant, the runner credits those kills, then checks the remaining invariants at the same bound.
- The server's default port is 8822, so 2 runners at once would share one server. Each runner attempt passes `--server-endpoint=localhost:PORT` with a free port, and `quint` starts a server on that port. The runner still verifies one step at a time, because each server can take 4 GB of memory.

## Read a result

`quint run` exits `1` for a violation, a parse error, a misspelled name, and a runtime error alike. It exits `0` for a vacuous `[ok]`. So the runner judges each run by its output, never by its exit status. quint colors its output when `FORCE_COLOR` is set, so the runner sets `NO_COLOR=1` and `FORCE_COLOR=0` for every `quint` call:

| Output | Meaning |
| --- | --- |
| `[ok] No violation found (...)` | No sampled run broke an invariant. It's a pass only when the `[ok]` rules hold. |
| `[violation] Found an issue (...)` | A run broke an invariant. The trace printed before this line is the counterexample. |
| `❌ NAME` after `[violation]` | Printed only for 2 or more invariants. It names the invariants that failed in the first failing run. |
| `[error] Runtime error (...)` | The spec failed while it ran, for example `Called 'get' with a non-existing key`. The spec is broken. |
| `error: parsing failed` or `error: typechecking failed` | The spec is broken. |
| `error: [QNT404] Name 'NAME' not found` | A misspelled `--step`, `--invariant`, or `--witnesses` name. The run is broken. |

A witness line reads `NAME was witnessed in N trace(s) out of M explored (P%)`. A witness counts a run when its predicate holds in any state of that run.

Rules for an `[ok]`:

- Reject it when M, the explored count, is under 10000.
- Reject it when the terminal witness is at 0%. A step that is never enabled ends every run at once and still prints `[ok]` with exit `0`.
- Reject it when `Trace length statistics` shows `max=1`. Every run then stopped at the initial state, so no step ever fired.
- Reject it when a witness holds at the initial state. Quint counts a run when the witness holds in any state, so such a witness is above 0% even when no step fires. The runner checks with `quint run --max-steps=0`, which samples initial states only.
- Quint ends a run silently when no action is enabled. So an `[ok]` never shows that the flow can't get stuck.

Rules for a `[violation]`:

- One failing run is enough, so a violation stands at any explored count. The count covers the runs that every thread finished before the first failure stopped quint, such as `out of 1 explored` or `out of 9893 explored`.
- The runner adds a violation's explored count and witness traces to the totals of the other invariants in that run. Those runs passed them. The violated invariant's total counts as a violation, so the `[ok]` rules skip it.

## Read a counterexample

- Quint prints the failing run as `[State 0]`, `[State 1]`, and so on, with the value of every variable. The runner reads the ITF file instead.
- With `--format md`, the runner prints each step as one numbered line: the action, its arguments, and the variables that changed.
- Add the `path:line` from that action's mapping row to each step.

## Syntax pitfalls

- Every branch of an `any` or an `if` must assign the same variables. Assign each unchanged variable as `x' = x`. Otherwise typecheck fails with `Expected [x] and [x,y] to be the same`.
- `Map.get` and `Map.set` need an existing key. A missing key passes typecheck and fails only at run time with `[QNT507]`. Build each map in `init` with `mapBy` over the full key set, and use `put` to add a key.
- `--invariants` and `--witnesses` take definition names, not expressions. Define each one as a `val` over state.
- Pass a protection as an action parameter, as the example's `designWith(onLiveLease)` does. Each mutant then changes 1 argument instead of copying an action.
