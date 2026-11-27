# Python reference

A Python spec is one `.py` file of plain Python. The runner, `scripts/check.py`, loads the file and searches it with `scripts/explore.py`. The engine needs Python 3.9 or later and nothing else. The worked example is `example-queue-consumer.py`.

## Write a spec

A spec defines 4 kinds of names. `SKILL.md` gives the rules for what to model.

| Part | Python form |
| --- | --- |
| State | `init()` returns one dict with one key per state variable. To start from several states, return a list of dicts. |
| Action | A function `name(s, ...)` that changes the state `s` in place. It returns `False` when it can't run in that state. |
| Step | A module-level list of moves named `step`, `stepDesign`, or `stepMut<Name>`. A move is `(action, argument, ...)`, or the bare action when it takes no argument. |
| Invariant or witness | A function `name(s)` that returns `True` or `False`. |

These rules keep the search correct:

- An action must give the same result for the same state and arguments. Don't use `random`, the clock, or a global that changes.
- Model each choice as its own move. To let 2 messages each crash, list `(crash, "m1")` and `(crash, "m2")`.
- Build a state from `dict`, `list`, `set`, `tuple`, `int`, `str`, `bool`, and `None` only. The runner copies those types before each action. It doesn't copy an object of your own class.
- Give each counter a bound in its action's guard, as `MAX_RECEIVES` does in the example. A counter with no bound never lets the search finish.
- Pass a protection as an action parameter, as the example's `designWith(onLiveLease)` does. Each mutant then changes 1 argument and copies no action.
- Any other module-level list whose name starts with `step` is a usage error. So is a `step`, `stepDesign`, or `stepMut<Name>` that isn't a list. A misnamed or mistyped mutant then can't drop out silently.

## Run

`check.py SPEC.py --invariants NAMES --terminal WITNESS` takes these options:

- `--witnesses NAMES`: the reachability witnesses.
- `--steps NAMES`: the steps to search. The default is every step list in the spec. The list must hold `stepDesign`.
- `--max-steps`: the largest number of actions in a run. The default is 30.
- `--max-states`: the search of one step stops past this many states. The default is 500000.
- `--run-timeout SECONDS`: the search of one step stops past this time. The default is 600.
- `--format md`: print markdown for the result file. The default is JSON.

`--budget`, `--verify`, and `--verify-step` are usage errors for a Python spec. The runner ignores the other Quint options.

The exit status follows the verdict: `0` for `pass`, `1` for `fail`, `2` for `invalid`, and `3` for `broken-spec`. A usage error exits `2`, and a crash in the runner exits `3`. These 2 print only a message on stderr.

## How the search works

The runner searches each step on its own, breadth-first:

1. It starts from the initial states.
2. In each state, it tries every move of the step. A move whose action returns `False` adds nothing.
3. It checks every invariant and every witness in each state it hasn't seen before. Two equal states count as one.
4. It repeats from each state it hasn't seen before.

The search of a step ends in one of 5 ways:

| `stopped` | Meaning | Result line |
| --- | --- | --- |
| `null` | No unseen state is left. The search checked every state that the spec can reach. A search whose longest run has exactly `--max-steps` actions also ends this way. | `full search, N states` |
| `step limit` | The search checked every run of up to `--max-steps` actions, and longer runs exist. | `search to K steps, N states` |
| `state limit` | The search passed `--max-states`. It checked every run of up to K actions, where K is the `depth` field. | `search to K steps, N states`, and the problem `state-limit` |
| `time limit` | The search passed `--run-timeout`. It checked every run of up to K actions, as for `state limit`. | `search to K steps, N states`, and the problem `run-timeout` |
| `every invariant is broken` | Nothing is left to find. | `search to K steps, N states` |

The search finds the shortest states first, so each counterexample has the fewest actions that can break its invariant.

A full search proves the invariants for the spec's bounds only, such as 2 messages and 3 receives. It proves nothing about a larger system.

## Output

The JSON output has these fields:

| Field | Holds |
| --- | --- |
| `verdict` | `pass`, `fail`, `invalid`, or `broken-spec`. |
| `result_line` | The result line, without the caller's judgment on the current code. |
| `problems` | One entry for each broken rule, with a `code` and a `message`. |
| `warnings` | Problems that don't change the verdict, in the same shape. |
| `matrix` | For each mutant and invariant: `true` for a kill, or `false` for a survivor. |
| `kills` | For each mutant and invariant: `search` for a kill, or `null` for none. |
| `current` | For `step`: its `result`, the `violated` invariants, `counterexamples` by invariant, and `explored`, the number of states. It's `null` when the spec has no `step`. |
| `design` | The same fields for `stepDesign`. |
| `searches` | For each step: `states`, `transitions`, `depth`, `stopped`, the state count for each witness in `witnesses`, the witnesses that hold at an initial state in `init_witnesses`, the `violated` invariants, their `counterexamples`, the `error`, and `seconds`. |
| `error` | The first spec error, or `null`. Its first line names the error and its `path:line` in the spec. |
| `engine`, `python`, `spec`, `max_steps`, `max_states`, `invariants`, `terminal`, `witnesses`, `steps` | The inputs and the Python version. `engine` is `python`. |

A counterexample is a list of steps, and step 0 is `init`. Each step holds the `action` name, its arguments by parameter name in `picks`, and the full `state`. With `--format md`, the runner prints each step as one numbered line: the action, its arguments, and the variables that changed. Add the `path:line` from that action's mapping row to each step.

Each problem code has one rule and one next step. The warning code, `spec-over-budget`, doesn't change the verdict:

| Code | Rule | Next step |
| --- | --- | --- |
| `witness-true-at-init` | A witness holds in an initial state. | Send the spec back to the writer. |
| `vacuous` | A step passes an invariant, but no move ever fires, or the terminal witness holds in no state. | Send the spec back to the writer. |
| `unreached-failure-path` | A reachability witness holds in no state of `stepDesign`. | Send the spec back to the writer. If the search stopped at a limit, raise the limit and rerun first. |
| `unkilled-invariant` | No mutant kills the invariant. | If no mutant targets it, send it back to the writer for one. Otherwise, find the cause as for a mutant that survives. |
| `useless-mutant` | The mutant kills no invariant. | Find the cause, as "Write mutants" in `SKILL.md` says. |
| `state-limit` | A step passes an invariant, but its search stopped past `--max-states`. | Send the spec back to the writer for smaller bounds, or raise `--max-states`. |
| `run-timeout` | A step passes an invariant, but its search stopped past `--run-timeout`. | Send the spec back to the writer for smaller bounds, or raise `--run-timeout`. |
| `spec-over-budget` | `init()` returns more than 8 state variables, or `--invariants` names more than 3. | Send the spec back to the writer once to split it into 2 flows or trim it. A spec still over the limit after that runs as is, and the result notes the warning. |

A `broken-spec` verdict means the spec raised an error. The causes are a syntax error, an error in `init()`, an action, an invariant, or a witness, and a name on the command line that the spec doesn't define. A spec that calls `sys.exit()` is a broken spec too.

## Pitfalls

- An action that returns nothing has run. Only `False` means "can't run here", so write `return False` in each guard.
- An action that returns `False` changes nothing, even when it changed `s` first. The runner throws that copy away.
- A set hides a second owner or a second send. Count them in a dict of integers, as "Write the spec" in `SKILL.md` says.
- A dict key that isn't a string prints as its `repr` in a counterexample.
- A `print` in the spec goes to stderr, so the report on stdout stays clean.
- The runner checks `--run-timeout` between states. An action with a loop that never ends stops the runner from returning.
