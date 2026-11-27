"""Search every run of a Python spec, breadth-first. `check.py` calls this module for a `.py` spec."""

from __future__ import annotations

import inspect
import time
import traceback


# A spec that calls `sys.exit()` must not end the runner, because the caller reads exit 0 as a pass.
SPEC_FAULTS = (Exception, SystemExit)


class SpecError(Exception):
    """The spec failed to load, or raised while it ran. The first line names the error and its place in the spec."""


def spec_error(error, path):
    lines = [frame.lineno for frame in traceback.extract_tb(error.__traceback__) if frame.filename == path]
    line = error.lineno if isinstance(error, SyntaxError) and error.filename == path else lines[-1] if lines else None
    place = f" at {path}:{line}" if line else ""
    # The 3-argument form also runs on Python 3.9, the system Python on macOS.
    text = "".join(traceback.format_exception(type(error), error, error.__traceback__)).strip()
    return SpecError(f"{type(error).__name__}: {error}{place}\n{text}")


def load(path, text):
    """Runs the spec file and returns its names. The compile keeps `__pycache__` out of the scratch dir."""
    names = {"__name__": "model_spec", "__file__": path}
    try:
        exec(compile(text, path, "exec"), names)
    except SPEC_FAULTS as error:
        raise spec_error(error, path) from error
    return names


def initial_states(names, path):
    init = names.get("init")
    if not callable(init):
        raise SpecError("the spec defines no `init()` function")
    try:
        states = init()
    except SPEC_FAULTS as error:
        raise spec_error(error, path) from error
    states = states if isinstance(states, list) else [states]
    if not states or not all(isinstance(state, dict) for state in states):
        raise SpecError("`init()` must return one state dict, or a list of state dicts")
    return states


def predicates(names, wanted):
    missing = [name for name in wanted if not callable(names.get(name))]
    if missing:
        raise SpecError(f"the spec defines no function named {', '.join(missing)}")
    return {name: names[name] for name in wanted}


def copy(value):
    if isinstance(value, dict):
        return {key: copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [copy(item) for item in value]
    return set(value) if isinstance(value, set) else value


def freeze(value):
    """Returns a hashable form, so 2 equal states count as 1. The type tags keep `[1]` apart from `(1,)`, a dict
    apart from a set of pairs, and `True` apart from `1`, which Python hashes alike."""
    if isinstance(value, dict):
        return "dict", frozenset((key, freeze(item)) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return type(value).__name__, tuple(freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return "set", frozenset(value)
    return ("bool", value) if isinstance(value, bool) else value


def plain(value):
    """Turns a state value into plain JSON."""
    if isinstance(value, dict):
        return {key if isinstance(key, str) else repr(key): plain(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted((plain(item) for item in value), key=repr)
    return [plain(item) for item in value] if isinstance(value, (list, tuple)) else value


def parts(move):
    """Returns (action, arguments). A move is a tuple, or a bare action that takes no argument."""
    action, *args = move if isinstance(move, tuple) else (move,)
    return action, args


def fire(move, state):
    """Applies one move to the state in place. Returns False when the action's guard refuses the state."""
    action, args = parts(move)
    return action(state, *args) is not False


def successors(state, moves):
    """Yields (move index, next state) for each move that fires in the state."""
    for index, move in enumerate(moves):
        after = copy(state)
        if fire(move, after):
            yield index, after


def trace(inits, moves, origins, key):
    """Replays the moves that lead to the state `key`. Returns one step per state, as `check.py` renders them."""
    path = []
    while key is not None:
        key, index = origins[key]
        path.append(index)
    state = copy(inits[path.pop()])
    steps = [{"action": "init", "picks": {}, "state": plain(state)}]
    for index in reversed(path):
        action, args = parts(moves[index])
        action(state, *args)
        parameters = list(inspect.signature(action).parameters)[1:]
        steps.append({"action": action.__name__, "picks": dict(zip(parameters, map(plain, args))),
                      "state": plain(state)})
    return steps


def search(path, step, inits, moves, invariants, witnesses, max_steps, max_states, timeout):
    """Visits every state that `moves` can reach from `inits`, level by level, so each counterexample is a shortest
    one. Stops early at `max_steps` levels, past `max_states` states, past `timeout` seconds, or when every invariant
    is broken."""
    start = time.monotonic()
    origins, counts, broken = {}, {name: 0 for name in witnesses}, {}
    record = {"step": step, "states": 0, "transitions": 0, "depth": 0, "stopped": None, "witnesses": counts,
              "init_witnesses": [], "violated": [], "counterexamples": {}, "error": None, "seconds": 0}

    def visit(state, origin, level):
        key = freeze(state)
        if key in origins:
            return
        origins[key] = origin
        level.append(state)
        for name, holds in witnesses.items():
            if holds(state):
                counts[name] += 1
                if origin[0] is None and name not in record["init_witnesses"]:
                    record["init_witnesses"].append(name)
        for name, holds in invariants.items():
            if name not in broken and not holds(state):
                broken[name] = key

    try:
        level = []
        for index, state in enumerate(inits):
            visit(state, (None, index), level)
        while level and record["stopped"] is None:
            if len(broken) == len(invariants):
                record["stopped"] = "every invariant is broken"
            elif record["depth"] == max_steps:
                # The search is still full when the last level leads to no unseen state.
                if any(freeze(after) not in origins for state in level for _, after in successors(state, moves)):
                    record["stopped"] = "step limit"
                level = []
            else:
                following = []
                for state in level:
                    key = freeze(state)
                    for index, after in successors(state, moves):
                        record["transitions"] += 1
                        visit(after, (key, index), following)
                    if len(origins) > max_states:
                        record["stopped"] = "state limit"
                    elif time.monotonic() - start > timeout:
                        record["stopped"] = "time limit"
                    if record["stopped"]:
                        break
                else:
                    record["depth"] += 1
                level = following
        record["counterexamples"] = {name: trace(inits, moves, origins, key) for name, key in broken.items()}
    except SPEC_FAULTS as error:
        record["error"] = str(spec_error(error, path))
    record.update(states=len(origins), violated=[name for name in invariants if name in broken],
                  seconds=round(time.monotonic() - start, 1))
    return record
