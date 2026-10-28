#!/usr/bin/env python3
"""Run every quint check for one model-check spec and print one verdict."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

MIN_SAMPLES = 10000
VERIFY_FIRST_BOUND = 6
VERIFY_BOUND_STEP = 2
# Enough samples to cover a nondeterministic init, and still well under a second at --max-steps=0.
INIT_PROBE_SAMPLES = 1000
MAX_SPEC_VARS = 8
MAX_SPEC_INVARIANTS = 3
EXIT_CODES = {"pass": 0, "fail": 1, "invalid": 2, "broken-spec": 3}
EXIT_ENVIRONMENT = 4

COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
STEP_RE = re.compile(r"^\s*action\s+(\w+)\s*=", re.M)
STEP_NAME_RE = re.compile(r"step\w+")
VAR_RE = re.compile(r"^\s*var\s+\w+\s*:", re.M)
TRACE_RE = re.compile(r"^Trace length statistics: max=(\d+)", re.M)
MUTANT_RE = re.compile(r"stepMut\w+")
RESULT_RE = re.compile(r"^\[(ok|violation)\]", re.M)
WITNESS_RE = re.compile(r"^(\w+) was witnessed in (\d+) trace\(s\) out of (\d+) explored \([\d.]+%\)$", re.M)
FAILED_RE = re.compile(r"^\s*❌ (\w+)\s*$", re.M)
SEED_RE = re.compile(r"Use --seed=(0x[0-9a-fA-F]+)")
ERROR_RE = re.compile(r"^\s*(\[error\].*|error: .*|Error \[QNT\d+\].*)$", re.M)


class UsageError(Exception):
    pass


class EnvironmentProblem(Exception):
    pass


def role(step):
    if step == "step":
        return "current"
    if step == "stepDesign":
        return "design"
    return "mutant" if MUTANT_RE.fullmatch(step) else None


def discover_steps(text):
    """Returns the spec's step actions by naming convention: current, design, then mutants in file order."""
    names = list(dict.fromkeys(STEP_RE.findall(COMMENT_RE.sub("", text))))
    misnamed = [name for name in names if STEP_NAME_RE.fullmatch(name) and role(name) is None]
    if misnamed:
        raise UsageError(f"{', '.join(misnamed)}: a step must be named step, stepDesign, or stepMut<Name>")
    order = {"current": 0, "design": 1, "mutant": 2}
    return sorted((name for name in names if role(name)), key=lambda name: order[role(name)])


def count_vars(text):
    return len(VAR_RE.findall(COMMENT_RE.sub("", text)))


def error_text(output):
    """Returns the output from the first error line on, which keeps the error's location."""
    match = ERROR_RE.search(output)
    tail = output[match.start():] if match else output
    return "\n".join(line.rstrip() for line in tail.splitlines() if line.strip())


def parse_run(output):
    """Returns (result, explored, witnesses, error) for one `quint run` output. Witnesses map to trace counts."""
    lines = WITNESS_RE.findall(output)
    witnesses = {name: int(traces) for name, traces, _ in lines}
    explored = min((int(total) for _, _, total in lines), default=None)
    match = RESULT_RE.search(output)
    if match:
        return match.group(1), explored, witnesses, None
    return "error", explored, witnesses, error_text(output)


def max_trace_length(output):
    match = TRACE_RE.search(output)
    return int(match.group(1)) if match else None


def parse_verify(output):
    """Returns (result, error) for one `quint verify` output."""
    match = RESULT_RE.search(output)
    return (match.group(1), None) if match else ("error", error_text(output))


def decode(value):
    """Turns an ITF value into plain JSON."""
    if isinstance(value, list):
        return [decode(item) for item in value]
    if not isinstance(value, dict):
        return value
    if "#bigint" in value:
        return int(value["#bigint"])
    if "#set" in value:
        return [decode(item) for item in value["#set"]]
    if "#tup" in value:
        return [decode(item) for item in value["#tup"]]
    if "#map" in value:
        pairs = [(decode(key), decode(item)) for key, item in value["#map"]]
        return dict(pairs) if all(isinstance(key, str) for key, _ in pairs) else [list(pair) for pair in pairs]
    return {key: decode(item) for key, item in value.items()}


def decode_pick(value):
    # quint 0.33 wraps every nondet pick in an Option; an unused pick is None.
    if isinstance(value, dict) and value.get("tag") == "Some":
        return decode(value["value"])
    if isinstance(value, dict) and value.get("tag") == "None":
        return None
    return decode(value)


def trace_from_itf(data):
    """Returns one step per ITF state: the action, its nondet picks, and the state without `mbt::` fields."""
    steps = []
    for state in data["states"]:
        picks = {name: decode_pick(value) for name, value in state.get("mbt::nondetPicks", {}).items()}
        steps.append({
            "action": state.get("mbt::actionTaken"),
            "picks": {name: value for name, value in picks.items() if value is not None},
            "state": {name: decode(value) for name, value in state.items()
                      if name != "#meta" and not name.startswith("mbt::")},
        })
    return steps


def read_trace(path):
    try:
        return trace_from_itf(json.loads(Path(path).read_text()))
    except (OSError, ValueError, KeyError):
        return []


def quint_env():
    # quint colors its output when FORCE_COLOR is set, and the color codes break every parser here.
    return {**os.environ, "NO_COLOR": "1", "FORCE_COLOR": "0"}


def capture(cmd, cwd=None):
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=quint_env())
    return result.returncode, result.stdout + result.stderr


def stop_group(pgid):
    # `quint verify` starts an Apalache JVM in its process group, and the JVM can outlive quint.
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.1)


def capture_in_group(cmd, timeout, cwd):
    """Runs cmd in its own process group and kills the whole group afterwards. Returns (code, output, timed_out)."""
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            start_new_session=True, env=quint_env())
    try:
        output, _ = proc.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        # A JVM that holds the pipe open can outlast a quint that already finished.
        timed_out = proc.poll() is None
        os.killpg(proc.pid, signal.SIGKILL)
        output, _ = proc.communicate()
    except BaseException:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
        raise
    stop_group(proc.pid)
    return proc.returncode, output, timed_out


def quint_version():
    if not shutil.which("quint"):
        raise EnvironmentProblem("quint is missing; install it with brew install quint")
    code, output = capture(["quint", "--version"])
    if code != 0:
        raise EnvironmentProblem(f"quint --version failed: {output.strip()}")
    return output.strip()


def java_version():
    """Returns the first line of `java -version`, or None when Java doesn't work."""
    try:
        code, output = capture(["java", "-version"])
    except OSError:
        return None
    lines = output.strip().splitlines()
    return lines[0] if code == 0 and lines else None


def sample(args, spec, step, invariants, witnesses, cwd, name, samples, seed):
    """Runs one `quint run` and returns its record, with each violated invariant mapped to its counterexample."""
    # A relative --out-itf keeps each command exact and rerunnable from any directory.
    itf = f"{name}.itf.json"
    checks = [f"--invariant={invariants[0]}"] if len(invariants) == 1 else ["--invariants", *invariants]
    cmd = ["quint", "run", spec, f"--main={args.main}", f"--step={step}", *checks, f"--max-samples={samples}",
           f"--max-steps={args.max_steps}", f"--seed={seed}", "--mbt", f"--out-itf={itf}", "--witnesses", *witnesses]
    start = time.monotonic()
    _, output, timed_out = capture_in_group(cmd, args.run_timeout, cwd)
    result, explored, traces, error = ("timeout", None, {}, None) if timed_out else parse_run(output)
    violated = {}
    if result == "violation" and len(invariants) == 1:
        violated = {invariants[0]: read_trace(Path(cwd) / itf)}
    elif result == "violation":
        violated = attribute(args, spec, step, invariants, witnesses, cwd, name, output, itf)
    return {"step": step, "role": role(step), "invariants": list(invariants), "seed": seed, "command": shlex.join(cmd),
            "result": result, "explored": explored, "witnesses": traces, "max_length": max_trace_length(output),
            "error": error, "violated": violated, "seconds": round(time.monotonic() - start, 1)}


def attribute(args, spec, step, invariants, witnesses, cwd, name, output, itf):
    """Maps each invariant that a multi-invariant violation broke to its own counterexample."""
    seed = SEED_RE.search(output)
    if seed:
        reruns = [sample(args, spec, step, [invariant], witnesses, cwd, f"{name}.{invariant}", 1, seed.group(1))
                  for invariant in invariants]
        found = {invariant: trace for rerun in reruns for invariant, trace in rerun["violated"].items()}
        if found:
            return found
    trace = read_trace(Path(cwd) / itf)
    return {invariant: trace for invariant in FAILED_RE.findall(output) if invariant in invariants}


def probe_init(args, spec, witnesses, cwd):
    """Samples initial states only, so a witness that holds there shows up before any step fires."""
    cmd = ["quint", "run", spec, f"--main={args.main}", "--step=stepDesign", "--max-steps=0",
           f"--max-samples={INIT_PROBE_SAMPLES}", f"--seed={args.seed}", "--witnesses", *witnesses]
    _, output, timed_out = capture_in_group(cmd, args.run_timeout, cwd)
    result, explored, traces, error = ("timeout", None, {}, None) if timed_out else parse_run(output)
    return {"command": shlex.join(cmd), "result": result, "explored": explored, "witnesses": traces, "error": error}


def run_matrix(args, spec, steps, witnesses, cwd):
    pairs = [(step, invariant) for step in steps for invariant in args.invariants]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        return list(pool.map(lambda pair: sample(args, spec, pair[0], [pair[1]], witnesses, cwd,
                                                 f"{pair[0]}.{pair[1]}", args.samples, args.seed), pairs))


def chunk_seed(seed, index):
    # quint steps each run's seed upward from --seed, so walks from nearby seeds can merge and repeat runs.
    return "0x" + hashlib.sha256(f"{seed}/{index}".encode()).hexdigest()[:14]


def run_budget(args, spec, witnesses, mutants, unkilled, cwd):
    """Samples until the budget is spent: each unkilled invariant against each mutant, then the design."""
    start = time.monotonic()
    pairs = [(mutant, invariant) for invariant in unkilled for mutant in mutants]
    # The mutants get at most half the budget, so the design always gets the rest.
    mutant_deadline, deadline = start + args.budget / 2, start + args.budget
    chunks, running, killed = [], set(), set()
    state = {"submitted": 0, "design_open": True, "broken": False}

    def next_target():
        now = time.monotonic()
        open_pairs = [pair for pair in pairs if pair[1] not in killed]
        if state["broken"]:
            return None
        if open_pairs and now < mutant_deadline:
            mutant, invariant = open_pairs[state["submitted"] % len(open_pairs)]
            return mutant, [invariant]
        if state["design_open"] and now < deadline:
            return "stepDesign", args.invariants
        return None

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        while True:
            while len(running) < args.workers and (target := next_target()):
                state["submitted"] += 1
                index = state["submitted"]
                running.add(pool.submit(sample, args, spec, *target, witnesses, cwd, f"budget.{index}",
                                        args.samples, chunk_seed(args.seed, index)))
            if not running:
                break
            done, running = wait(running, return_when=FIRST_COMPLETED)
            for future in done:
                chunk = future.result()
                chunks.append(chunk)
                state["broken"] = state["broken"] or chunk["result"] == "error"
                if chunk["role"] == "mutant":
                    killed.update(chunk["violated"])
                elif chunk["result"] != "ok":
                    state["design_open"] = False
    return chunks, round(time.monotonic() - start, 1)


def budget_targets(chunks):
    """Sums the budget's chunks per step and invariant set."""
    targets = {}
    for chunk in chunks:
        target = targets.setdefault((chunk["step"], tuple(chunk["invariants"])), {
            "step": chunk["step"], "invariants": chunk["invariants"], "command": chunk["command"], "seeds": [],
            "explored": 0, "witnesses": {}, "violated": [], "counterexamples": {}, "errors": []})
        target["seeds"].append(chunk["seed"])
        target["explored"] += chunk["explored"] or 0
        for name, traces in chunk["witnesses"].items():
            target["witnesses"][name] = target["witnesses"].get(name, 0) + traces
        for invariant, trace in chunk["violated"].items():
            if invariant not in target["counterexamples"]:
                target["violated"].append(invariant)
                target["counterexamples"][invariant] = trace
        if chunk["error"]:
            target["errors"].append(chunk["error"])
    return list(targets.values())


def free_port():
    # Each attempt gets its own Apalache server, so 2 runners at once don't share the default port 8822.
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        return sock.getsockname()[1]


def verify_record(status, reason=None, invariants=()):
    return {"status": status, "reason": reason, "invariants": list(invariants), "bound": None, "result": None,
            "violated": [], "counterexamples": {}, "timed_out": False, "attempts": [], "error": None}


def verify_targets(args, mutants, kills):
    """Returns {step: invariants}: the named steps, or the design plus each mutant on the still-unkilled invariants."""
    unkilled = [invariant for invariant in args.invariants if not any(kills[m][invariant] for m in mutants)]
    targets = {}
    for step in args.verify_step or ["stepDesign", *(mutant for mutant in mutants if unkilled)]:
        if role(step) == "design":
            targets[step] = list(args.invariants)
        elif args.verify_step:
            targets[step] = [invariant for invariant in args.invariants if not kills[step][invariant]]
        else:
            targets[step] = unkilled
    return targets


def verify_step(args, spec, step, invariants, tmp):
    """Raises the bound while each attempt finishes in the budget. A mutant keeps checking the invariants it hasn't
    broken yet, at the same bound."""
    record = verify_record("ran", invariants=invariants)
    remaining, bound = list(invariants), min(VERIFY_FIRST_BOUND, args.max_steps)
    while remaining and bound <= args.max_steps:
        itf = f"verify.{step}.{len(record['attempts'])}.itf.json"
        cmd = ["quint", "verify", spec, f"--main={args.main}", f"--step={step}", "--invariants", *remaining,
               f"--max-steps={bound}", f"--out-itf={itf}", f"--server-endpoint=localhost:{free_port()}"]
        start = time.monotonic()
        # Apalache writes _apalache-out/ into its working directory, so run it in tmp.
        _, output, timed_out = capture_in_group(cmd, args.verify_budget, tmp)
        attempt = {"max_steps": bound, "invariants": list(remaining), "command": shlex.join(cmd),
                   "seconds": round(time.monotonic() - start, 1)}
        record["attempts"].append(attempt)
        if timed_out:
            attempt["result"], record["timed_out"] = "timeout", True
            break
        attempt["result"], error = parse_verify(output)
        if attempt["result"] == "error":
            record["error"] = error
            break
        record["bound"] = bound
        if attempt["result"] == "ok":
            bound += VERIFY_BOUND_STEP
            continue
        names = [name for name in FAILED_RE.findall(output) if name in remaining]
        names = names or (remaining if len(remaining) == 1 else [])
        trace = read_trace(Path(tmp) / itf)
        record["violated"] += names
        record["counterexamples"].update({name: trace for name in names})
        if not names:
            record["error"] = "quint verify found a violation but named no invariant"
        if role(step) == "design" or not names:
            break
        remaining = [invariant for invariant in remaining if invariant not in names]
    results = [attempt["result"] for attempt in record["attempts"]]
    record["result"] = "violation" if "violation" in results else "ok" if record["bound"] else None
    return record


def run_verify(args, spec, targets, java):
    if java is None:
        return {step: verify_record("skipped", "java -version failed, so the check is random sampling only")
                for step in targets}
    report = {}
    with tempfile.TemporaryDirectory() as tmp:
        for step, invariants in targets.items():
            report[step] = (verify_step(args, spec, step, invariants, tmp) if invariants else
                            verify_record("skipped", "the mutant already kills every invariant"))
    return report


def tally(records):
    """Sums explored runs and witness traces per (step, invariant) over every sampling run."""
    totals = {}
    for record in records:
        for invariant in record["invariants"]:
            total = totals.setdefault((record["step"], invariant),
                                      {"explored": 0, "witnesses": {}, "max_length": None, "result": "ok"})
            total["explored"] += record["explored"] or 0
            for name, traces in record["witnesses"].items():
                total["witnesses"][name] = total["witnesses"].get(name, 0) + traces
            if record.get("max_length") is not None:
                total["max_length"] = max(total["max_length"] or 0, record["max_length"])
            if record["result"] == "error":
                total["result"] = "error"
            elif invariant in record["violated"] and total["result"] in ("ok", "timeout"):
                total["result"] = "violation"
            elif record["result"] == "timeout" and total["result"] == "ok":
                total["result"] = "timeout"
    return totals


def problem(code, message):
    return {"code": code, "message": message}


def find_problems(args, steps, totals, kills, mutants, init_probe, verify):
    problems = [problem("witness-true-at-init", f"witness `{name}` holds at the initial state, so it counts runs "
                        "in which no step fired") for name, traces in init_probe["witnesses"].items() if traces]
    for step in steps:
        passed = [(invariant, totals[(step, invariant)]) for invariant in args.invariants
                  if totals[(step, invariant)]["result"] == "ok"]
        short = [invariant for invariant, total in passed if total["explored"] < args.samples]
        if short:
            problems.append(problem("insufficient-samples", f"`{step}` passed {', '.join(short)} after fewer than "
                                    f"{args.samples} explored runs, or printed no explored count"))
        stuck = [invariant for invariant, total in passed if total["max_length"] == 1]
        if stuck:
            problems.append(problem("vacuous", f"`{step}` passed {', '.join(stuck)}, but every run stopped at the "
                                    "initial state: the step never fires"))
        vacuous = [invariant for invariant, total in passed
                   if total["witnesses"].get(args.terminal, 0) == 0 and invariant not in stuck]
        if vacuous:
            problems.append(problem("vacuous", f"`{step}` passed {', '.join(vacuous)}, but terminal witness "
                                    f"`{args.terminal}` is 0%: the step never fires or never settles"))
        slow = [invariant for invariant in args.invariants if totals[(step, invariant)]["result"] == "timeout"]
        if slow:
            problems.append(problem("run-timeout", f"`{step}` ran past --run-timeout of {args.run_timeout:g} "
                                    f"seconds for {', '.join(slow)}"))
    design = [totals[("stepDesign", invariant)] for invariant in args.invariants
              if totals[("stepDesign", invariant)]["result"] == "ok"]
    for witness in args.witnesses:
        if design and all(total["witnesses"].get(witness, 0) == 0 for total in design):
            problems.append(problem("unreached-failure-path",
                                    f"reachability witness `{witness}` is 0% on `stepDesign`"))
    for invariant in args.invariants:
        if not any(kills[mutant][invariant] for mutant in mutants):
            problems.append(problem("unkilled-invariant", f"no mutant violates `{invariant}`"))
    for mutant in mutants:
        if not any(kills[mutant].values()):
            problems.append(problem("useless-mutant", f"`{mutant}` violates no invariant"))
    design = verify.get("stepDesign")
    if design and design["bound"] is None:
        reason = design["reason"] or design["error"] or ("it timed out" if design["timed_out"] else "it stopped")
        problems.append(problem("verify-incomplete", f"`quint verify` finished no bound on `stepDesign`: {reason}"))
    return problems


def find_warnings(args, variables):
    if variables <= MAX_SPEC_VARS and len(args.invariants) <= MAX_SPEC_INVARIANTS:
        return []
    return [problem("spec-over-budget", f"the spec has {plural(variables, 'state variable')} and "
                    f"{plural(len(args.invariants), 'invariant')}; the limit is {MAX_SPEC_VARS} and "
                    f"{MAX_SPEC_INVARIANTS}, so split it into 2 flows or trim it")]


def summary(records, totals, step, invariants, verify=None):
    selected = [record for record in records if record["step"] == step]
    found = {}
    for record in selected:
        for invariant, trace in record["violated"].items():
            found.setdefault(invariant, trace)
    for invariant, trace in (verify or {}).get("counterexamples", {}).items():
        found.setdefault(invariant, trace)
    failed = found or any(record["result"] == "violation" for record in selected) or \
        (verify or {}).get("result") == "violation"
    passed = [totals[(step, invariant)]["explored"] for invariant in invariants
              if totals[(step, invariant)]["result"] == "ok"]
    return {
        "result": "error" if any(r["result"] == "error" for r in selected) else "fail" if failed else "pass",
        "violated": [invariant for invariant in invariants if invariant in found],
        "counterexamples": found,
        "explored": min(passed, default=None),
    }


def run_entry(record):
    invariant = record["invariants"][0]
    return {"step": record["step"], "role": record["role"], "invariant": invariant, "command": record["command"],
            "result": record["result"], "explored": record["explored"], "witnesses": record["witnesses"],
            "max_length": record["max_length"], "seconds": record["seconds"], "error": record["error"],
            "counterexample": record["violated"].get(invariant)}


def plural(count, word):
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def first_error(report):
    texts = [report["typecheck"]["error"], *(run["error"] for run in report["runs"]),
             *(error for target in (report["budget"] or {}).get("targets", []) for error in target["errors"])]
    lines = [line for text in texts if text for line in text.splitlines() if line.strip()]
    return next((line for line in lines if "QNT" in line), lines[0] if lines else "unknown error")


def build_result_line(report):
    flow = Path(report["spec"]).stem
    if report["verdict"] == "broken-spec":
        return f"Model check: {flow} — broken spec: {first_error(report)}"
    mutants = report["matrix"]
    killed = sum(any(row.values()) for row in mutants.values())
    bound = report["verify"].get("stepDesign", {}).get("bound")
    runs = report["design"]["explored"] or report["samples"]
    method = (f"bounded check to {bound} steps" if bound else
              f"random sampling, {runs} runs ≤{report['max_steps']} steps")
    parts = [f"Model check: {flow} — {plural(len(report['invariants']), 'invariant')}, "
             f"{killed}/{len(mutants)} mutants killed", method]
    if report["current"] is not None:
        violated = report["current"]["violated"]
        parts.append(f"current code: fails {', '.join(violated)}" if violated else "current code: passes")
    if report["verdict"] == "fail":
        parts.append(f"design: fails {', '.join(report['design']['violated']) or 'the bounded check'}")
    if report["verdict"] == "invalid":
        parts.append(f"invalid: {', '.join(dict.fromkeys(item['code'] for item in report['problems']))}")
    return "; ".join(parts)


def validate(args):
    spec_path = Path(args.spec)
    if not spec_path.is_file():
        raise UsageError(f"{args.spec} is not a file")
    if args.samples < MIN_SAMPLES:
        raise UsageError(f"--samples must be {MIN_SAMPLES} or more, got {args.samples}")
    if args.budget < 0 or args.workers < 1 or args.run_timeout <= 0:
        raise UsageError("--budget must be 0 or more, --workers 1 or more, and --run-timeout above 0")
    try:
        text = spec_path.read_text()
    except (OSError, UnicodeDecodeError) as error:
        raise UsageError(f"can't read {args.spec} as UTF-8 text: {error}") from error
    discovered = discover_steps(text)
    steps = args.steps or discovered
    unnamed = [step for step in steps if role(step) is None]
    if unnamed:
        raise UsageError(f"{', '.join(unnamed)}: a step must be named step, stepDesign, or stepMut<Name>")
    if "stepDesign" not in steps:
        raise UsageError(f"{args.spec} has no `action stepDesign`, and the design step is required")
    unknown = [step for step in args.verify_step or [] if step not in steps or role(step) == "current"]
    if unknown:
        raise UsageError(f"--verify-step takes stepDesign or a mutant that runs: {', '.join(unknown)}")
    return str(spec_path.resolve()), list(dict.fromkeys(steps)), count_vars(text)


def check(args):
    spec, steps, variables = validate(args)
    args.verify = args.verify or bool(args.verify_step)
    mutants = [step for step in steps if role(step) == "mutant"]
    witnesses = list(dict.fromkeys([args.terminal, *args.witnesses]))

    report = {"quint_version": quint_version(), "java": java_version(), "spec": spec, "main": args.main,
              "samples": args.samples, "max_steps": args.max_steps, "seed": args.seed, "workers": args.workers,
              "invariants": args.invariants, "terminal": args.terminal, "witnesses": args.witnesses,
              "steps": steps}
    cmd = ["quint", "typecheck", spec]
    code, output = capture(cmd)
    report["typecheck"] = {"command": shlex.join(cmd), "ok": code == 0, "error": None if code == 0 else output.strip()}
    budget = {"seconds": args.budget, "status": "skipped", "reason": None, "spent": 0, "workers": args.workers,
              "chunk_samples": args.samples, "targets": []} if args.budget else None
    skipped_verify = {step: verify_record("skipped", "typecheck failed") for step in args.verify_step or ["stepDesign"]}
    report.update(init_probe=None, runs=[], matrix={}, kills={}, current=None, design=None, budget=budget, problems=[],
                  warnings=find_warnings(args, variables), verify=skipped_verify if args.verify else {})
    if code != 0:
        if budget:
            budget["reason"] = "typecheck failed"
        report["verdict"] = "broken-spec"
        report["result_line"] = build_result_line(report)
        return report

    with tempfile.TemporaryDirectory() as tmp:
        report["init_probe"] = probe_init(args, spec, witnesses, tmp)
        records = run_matrix(args, spec, steps, witnesses, tmp)
        kills = {mutant: {invariant: None for invariant in args.invariants} for mutant in mutants}
        for record in records:
            for invariant in record["violated"] if record["role"] == "mutant" else ():
                kills[record["step"]][invariant] = "sampling"
        broken = any(record["result"] == "error" for record in records)
        design_failed = any(record["result"] == "violation" for record in records if record["role"] == "design")
        chunks = []
        if budget and (broken or design_failed):
            budget["reason"] = "a run failed with an error" if broken else "sampling already found a design violation"
        elif budget:
            unkilled = [invariant for invariant in args.invariants if not any(kills[m][invariant] for m in mutants)]
            chunks, budget["spent"] = run_budget(args, spec, witnesses, mutants, unkilled, tmp)
            budget.update(status="ran", targets=budget_targets(chunks))
    for chunk in chunks:
        for invariant in chunk["violated"] if chunk["role"] == "mutant" else ():
            kills[chunk["step"]][invariant] = kills[chunk["step"]][invariant] or "budget"
    broken = broken or any(chunk["result"] == "error" for chunk in chunks)
    design_failed = design_failed or any(chunk["result"] != "ok" for chunk in chunks if chunk["role"] == "design")

    if args.verify and (broken or design_failed):
        reason = "a run failed with an error" if broken else "sampling already found a design violation"
        report["verify"] = {step: verify_record("skipped", reason) for step in args.verify_step or ["stepDesign"]}
    elif args.verify:
        report["verify"] = run_verify(args, spec, verify_targets(args, mutants, kills), report["java"])
    for step, record in report["verify"].items():
        for invariant in record["violated"] if role(step) == "mutant" else ():
            kills[step][invariant] = kills[step][invariant] or "verify"

    errored = {(record["step"], record["invariants"][0]) for record in records
               if record["result"] in ("error", "timeout")}
    report["kills"] = kills
    report["matrix"] = {mutant: {invariant: True if kills[mutant][invariant] else
                                 None if (mutant, invariant) in errored else False
                                 for invariant in args.invariants} for mutant in mutants}
    totals = tally(records + chunks)
    report["runs"] = [run_entry(record) for record in records]
    report["design"] = summary(records + chunks, totals, "stepDesign", args.invariants,
                               report["verify"].get("stepDesign"))
    if "step" in steps:
        report["current"] = summary(records, totals, "step", args.invariants)
    report["problems"] = find_problems(args, steps, totals, kills, mutants, report["init_probe"], report["verify"])

    if broken:
        report["verdict"] = "broken-spec"
    elif report["design"]["result"] == "fail":
        report["verdict"] = "fail"
    else:
        report["verdict"] = "invalid" if report["problems"] else "pass"
    report["result_line"] = build_result_line(report)
    return report


def show(value):
    return json.dumps(value, ensure_ascii=False)


def percent(traces, explored):
    return f"{100 * traces / explored:.2f}%" if explored else ""


def changes(before, after):
    out = []
    for name, value in after.items():
        old = before.get(name)
        if before and isinstance(value, dict) and isinstance(old, dict):
            out += [f"{name}[{key}] = {show(item)}" for key, item in value.items() if old.get(key) != item]
        elif value != old or not before:
            out.append(f"{name} = {show(value)}")
    return out


def render_trace(trace):
    lines, before = [], {}
    for number, step in enumerate(trace):
        picks = ", ".join(f"{name}: {show(value)}" for name, value in step["picks"].items())
        action = f"{step['action']}({picks})" if step["action"] and picks else step["action"] or "state"
        lines.append(f"{number}. `{action}`: {'; '.join(changes(before, step['state'])) or 'no change'}")
        before = step["state"]
    return lines


def cell(text):
    return str(text).replace("|", "\\|")


def table(header, rows):
    return ["| " + " | ".join(header) + " |", "| --- " * len(header) + "|"] + \
        ["| " + " | ".join(str(item) for item in row) + " |" for row in rows]


def render_md(report):
    witnesses = [report["terminal"], *(w for w in report["witnesses"] if w != report["terminal"])]
    lines = [report["result_line"], "", "## Commands", "",
             f"`quint` {report['quint_version']}; Java: {report['java'] or 'missing'}.", ""]
    typecheck = report["typecheck"]
    rows = [["typecheck", "", "ok" if typecheck["ok"] else "error", "", *[""] * len(witnesses),
             f"`{cell(typecheck['command'])}`"]]
    probe = report["init_probe"]
    if probe:
        rows.append(["init probe", "", probe["result"], probe["explored"] or "",
                     *(percent(probe["witnesses"].get(w, 0), probe["explored"]) for w in witnesses),
                     f"`{cell(probe['command'])}`"])
    rows += [[f"`{run['step']}`", f"`{run['invariant']}`", run["result"], run["explored"] or "",
              *(percent(run["witnesses"].get(w, 0), run["explored"]) for w in witnesses), f"`{cell(run['command'])}`"]
             for run in report["runs"]]
    lines += table(["Step", "Invariant", "Result", "Explored", *(f"`{w}`" for w in witnesses), "Command"], rows)

    budget = report["budget"]
    if budget:
        lines += ["", "## Budget", ""]
        if budget["status"] == "ran":
            lines += [f"Spent {budget['spent']} of {budget['seconds']} seconds on {budget['workers']} workers, "
                      f"in chunks of {budget['chunk_samples']} runs.", ""]
            lines += table(["Step", "Invariants", "Chunks", "Explored", "Violated", *(f"`{w}`" for w in witnesses),
                            "First command"],
                           [[f"`{t['step']}`", ", ".join(f"`{i}`" for i in t["invariants"]), len(t["seeds"]),
                             t["explored"], ", ".join(f"`{i}`" for i in t["violated"]) or "none",
                             *(percent(t["witnesses"].get(w, 0), t["explored"]) for w in witnesses),
                             f"`{cell(t['command'])}`"] for t in budget["targets"]])
        else:
            lines.append(f"Skipped: {budget['reason']}.")

    if report["matrix"]:
        marks = {"sampling": "killed", "budget": "killed by the budget", "verify": "killed by the bounded check"}
        lines += ["", "## Mutants", ""]
        lines += table(["Mutant", *(f"`{i}`" for i in report["invariants"])],
                       [[f"`{mutant}`", *(marks[report["kills"][mutant][i]] if report["kills"][mutant][i] else
                                          "error" if row[i] is None else "survived" for i in report["invariants"])]
                        for mutant, row in report["matrix"].items()])

    lines += ["", "## Bounded check", ""]
    attempts = [[f"`{step}`", ", ".join(f"`{i}`" for i in a["invariants"]), a["max_steps"], a["result"], a["seconds"],
                 f"`{cell(a['command'])}`"] for step, record in report["verify"].items() for a in record["attempts"]]
    if attempts:
        lines += table(["Step", "Invariants", "Max steps", "Result", "Seconds", "Command"], attempts)
    notes = [f"`{step}`: skipped, {record['reason']}." if record["status"] == "skipped" else
             f"`{step}`: {record['error']}." for step, record in report["verify"].items()
             if record["status"] == "skipped" or record["error"]]
    lines += ([""] if attempts and notes else []) + notes
    if not report["verify"]:
        lines.append("Skipped: not requested.")

    if report["problems"]:
        lines += ["", "## Problems", ""] + [f"- `{p['code']}`: {p['message']}" for p in report["problems"]]
    if report["warnings"]:
        lines += ["", "## Warnings", ""] + [f"- `{w['code']}`: {w['message']}" for w in report["warnings"]]
    errors = [(run["command"], run["error"]) for run in report["runs"] if run["error"]]
    errors += [(target["command"], error) for target in (budget or {}).get("targets", []) for error in target["errors"]]
    if typecheck["error"]:
        errors.append((typecheck["command"], typecheck["error"]))
    if errors:
        lines += ["", "## Errors", ""]
        for command, error in errors:
            lines += [f"`{command}`", "", "```", error, "```", ""]

    traces = [(f"`{run['step']}` violates `{run['invariant']}`", run["counterexample"])
              for run in report["runs"] if run["counterexample"]]
    traces += [(f"`{target['step']}` violates `{invariant}` (budget)", trace)
               for target in (budget or {}).get("targets", [])
               for invariant, trace in target["counterexamples"].items()]
    traces += [(f"`{step}` violates `{invariant}` (bounded check to {record['bound']} steps)", trace)
               for step, record in report["verify"].items() for invariant, trace in record["counterexamples"].items()]
    if traces:
        lines += ["", "## Counterexamples"]
        for title, trace in traces:
            lines += ["", f"### {title}", ""] + render_trace(trace)
    return "\n".join(lines).rstrip()


def build_parser():
    parser = argparse.ArgumentParser(prog="check.py", description=__doc__)
    parser.add_argument("spec", help="the .qnt file")
    parser.add_argument("--main", required=True, help="the module name")
    parser.add_argument("--invariants", nargs="+", required=True, metavar="NAME")
    parser.add_argument("--terminal", required=True, metavar="WITNESS", help="the witness for a finished run")
    parser.add_argument("--witnesses", nargs="+", default=[], metavar="NAME", help="reachability witnesses")
    parser.add_argument("--steps", nargs="+", metavar="NAME",
                        help="step actions to run (default: step, stepDesign, and every stepMut<Name>)")
    parser.add_argument("--samples", type=int, default=20000, help="--max-samples for every run and budget chunk")
    parser.add_argument("--max-steps", type=int, default=30, help="--max-steps for runs, and the verify ceiling")
    parser.add_argument("--seed", default="7")
    parser.add_argument("--budget", type=float, default=0, metavar="SECONDS",
                        help="extra sampling time: unkilled invariants against each mutant, then the design")
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1, help="quint processes at once")
    parser.add_argument("--run-timeout", type=float, default=600, metavar="SECONDS",
                        help="time limit for each quint run")
    parser.add_argument("--verify", action="store_true",
                        help="also run quint verify on stepDesign and on each mutant against each unkilled invariant")
    parser.add_argument("--verify-step", action="append", metavar="NAME",
                        help="verify only this step; repeatable; implies --verify")
    parser.add_argument("--verify-budget", type=float, default=300, metavar="SECONDS",
                        help="time limit for each verify attempt")
    parser.add_argument("--format", choices=("json", "md"), default="json")
    return parser


def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exit:
        return exit.code if isinstance(exit.code, int) else 2
    try:
        report = check(args)
    except UsageError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except EnvironmentProblem as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ENVIRONMENT
    except Exception as error:
        # A crash proves nothing, so it takes the broken-spec code instead of reading as a pass or a design failure.
        print(f"error: the runner crashed: {type(error).__name__}: {error}", file=sys.stderr)
        return EXIT_CODES["broken-spec"]
    print(render_md(report) if args.format == "md" else json.dumps(report, indent=2, ensure_ascii=False))
    return EXIT_CODES[report["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
