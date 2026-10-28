"""Test the model-check runner: output parsing without quint, then full runs on the worked example and on a spec
whose mutant fails only on a rare path."""

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SKILL = Path(__file__).resolve().parents[2] / "skills/model-check"
SCRIPT = SKILL / "scripts/check.py"
EXAMPLE = SKILL / "references/example-queue-consumer.qnt"
sys.path.insert(0, str(SCRIPT.parent))
# Keep __pycache__ out of the skill folder, which ships as a zip.
sys.dont_write_bytecode = True

import check  # noqa: E402

INVARIANTS = ["noLostMessages", "atMostOnce", "oneOwner"]
ARGS = ["--main", "queue_consumer", "--invariants", *INVARIANTS, "--terminal", "settled",
        "--witnesses", "orphanClaim", "--samples", "10000"]
RESULT_LINE = re.compile(r"Model check: [\w-]+ — \d+ invariants?, \d+/\d+ mutants killed; "
                         r"(random sampling, \d+ runs ≤\d+ steps|bounded check to \d+ steps)"
                         r"(; current code: (passes|fails \w+(, \w+)*))?")

OK_OUTPUT = """An example execution:

[State 0]
{
  claim: Map("m1" -> "none", "m2" -> "none"),
  mbt::actionTaken: "init",
  mbt::nondetPicks: { m: None },
  visible: Map("m1" -> 1, "m2" -> 1)
}

[ok] No violation found (856ms at 11682 traces/second).
Trace length statistics: max=24, min=9, average=13.32
You may increase --max-samples and --max-steps.
Use --verbosity to produce more (or less) output.
Witnesses:
settled was witnessed in 10000 trace(s) out of 10000 explored (100.00%)
orphanClaim was witnessed in 7465 trace(s) out of 10000 explored (74.65%)
"""

VIOLATION_OUTPUT = """An example execution:

[State 0]
{
  visible: Map("m1" -> 1, "m2" -> 1)
}

[violation] Found an issue (12ms at 83 traces/second).
  ❌ oneOwner
Use --verbosity=3 to show executions.
Witnesses:
settled was witnessed in 0 trace(s) out of 1 explored (0.00%)
orphanClaim was witnessed in 1 trace(s) out of 1 explored (100.00%)
Use --seed=0x7 --backend=rust to reproduce.
error: Invariant violated
"""

RUNTIME_ERROR_OUTPUT = """An example execution:

[error] Runtime error (10ms at 0 traces/second).

 Error [QNT507]: Called 'get' with a non-existing key. Key is "zz". Map has keys: "m2", "m1"

  at /tmp/runtime.qnt:42:5
  42:     visible.get("zz") > 0,
          ^^^^^^^^^^^^^^^^^

Use --seed=0x7 --backend=rust to reproduce.
error: Runtime error
"""

UNKNOWN_NAME_OUTPUT = """error: [QNT404] Name 'stepNope' not found
error: Argument error
"""

PARSE_ERROR_OUTPUT = """ Error [QNT000]: missing '}' at ','

  at /tmp/syntax.qnt:21:38
  21:     visible' = MESSAGES.mapBy(_ => 1),
                                           ^

error: parsing failed
"""

# The mutant breaks only after 4 "advance" events in a row and then a "fire", out of 14 events at each step.
# About 1 in 5 runs of 10000 samples finds that path, and seed 7's run misses it.
RARE_SPEC = """module rare_path {
  pure val NEEDED = 4

  var stage: int
  var broken: bool

  action init = all { stage' = 0, broken' = false }

  // Event 0 advances the sequence, event 1 fires, and every other event resets it.
  action stepWith(guarded) = {
    nondet event = 0.to(13).oneOf()
    all {
      stage' = if (event == 0) stage + 1 else 0,
      broken' = (broken or (not(guarded) and event == 1 and stage == NEEDED)),
    }
  }

  action stepDesign = stepWith(true)
  action stepMutNoGuard = stepWith(false)

  val safe = not(broken)
  val bounded = stage <= 30
  val advanced = stage > 0
}
"""
RARE_ARGS = ["--main", "rare_path", "--invariants", "safe", "--terminal", "advanced", "--samples", "10000"]
RARE_NOTE = ("The rare-path tests depend on quint 0.33.0's random sampling: seed 7's 10000 runs miss the path, and "
             "budget chunk 4 finds it. After a quint upgrade, find new seeds before you call this a regression.")

NEVER_FIRES_SPEC = """module never_fires {
  var stage: int
  var broken: bool
  action init = all { stage' = 0, broken' = false }
  // The design step is never enabled, so every run ends at the initial state.
  action stepDesign = all { stage > 100, stage' = stage, broken' = broken }
  action stepMutBreak = all { stage' = stage + 1, broken' = true }
  val safe = not(broken)
  val idle = stage == 0
}
"""

# 9 state variables, one over the limit. Otherwise it passes: the mutant breaks `safe` on its first step.
WIDE_SPEC = """module wide {
  var count: int
  var broken: bool
  var a: int
  var b: int
  var c: int
  var d: int
  var e: int
  var f: int
  var g: int
  action init = all { count' = 0, broken' = false, a' = 0, b' = 0, c' = 0, d' = 0, e' = 0, f' = 0, g' = 0 }
  action stepWith(guarded) = all {
    count' = count + 1,
    broken' = (broken or not(guarded)),
    a' = a, b' = b, c' = c, d' = d, e' = e, f' = f, g' = g,
  }
  action stepDesign = stepWith(true)
  action stepMutBreak = stepWith(false)
  val safe = not(broken)
  val moved = count > 0
}
"""

VERIFY_OK_OUTPUT = """The outcome is: NoError                                           I@10:37:57.951
[ok] No violation found (12791ms).
You may increase --max-steps.
"""

ITF = {
    "#meta": {"format": "ITF", "status": "violation"},
    "vars": ["dlq", "running", "mbt::actionTaken", "mbt::nondetPicks", "mbt::actionTaken", "mbt::nondetPicks"],
    "states": [
        {"#meta": {"index": 0}, "dlq": {"#set": []},
         "running": {"#map": [["m1", {"#bigint": "0"}], ["m2", {"#bigint": "0"}]]},
         "mbt::actionTaken": "init", "mbt::nondetPicks": {"m": {"tag": "None", "value": {"#tup": []}}}},
        {"#meta": {"index": 1}, "dlq": {"#set": ["m2"]},
         "running": {"#map": [["m1", {"#bigint": "1"}], ["m2", {"#bigint": "0"}]]},
         "mbt::actionTaken": "receiveDesign", "mbt::nondetPicks": {"m": {"tag": "Some", "value": "m1"}}},
    ],
}


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = check.main([str(arg) for arg in argv])
    return code, out.getvalue(), err.getvalue()


def run_json(*argv):
    code, out, err = run_cli(*argv)
    return code, json.loads(out), err


def codes(report):
    return [problem["code"] for problem in report["problems"]]


def write_variant(directory, old, new):
    """Writes a copy of the example with one replacement, without cp, which prompts on this machine."""
    source = EXAMPLE.read_text()
    assert source.count(old) == 1, old
    path = Path(directory) / "variant.qnt"
    path.write_text(source.replace(old, new))
    return path


def java_works():
    return check.java_version() is not None


class ParseTests(unittest.TestCase):
    def test_ok_reads_explored_count_and_witnesses(self):
        self.assertEqual(check.parse_run(OK_OUTPUT),
                         ("ok", 10000, {"settled": 10000, "orphanClaim": 7465}, None))

    def test_violation_ignores_its_error_line(self):
        self.assertEqual(check.parse_run(VIOLATION_OUTPUT),
                         ("violation", 1, {"settled": 0, "orphanClaim": 1}, None))
        self.assertEqual(check.FAILED_RE.findall(VIOLATION_OUTPUT), ["oneOwner"])
        self.assertEqual(check.SEED_RE.search(VIOLATION_OUTPUT).group(1), "0x7")

    def test_runtime_error_keeps_the_location(self):
        result, explored, witnesses, error = check.parse_run(RUNTIME_ERROR_OUTPUT)
        self.assertEqual((result, explored, witnesses), ("error", None, {}))
        self.assertTrue(error.startswith("[error] Runtime error"))
        self.assertIn("Error [QNT507]", error)
        self.assertIn("/tmp/runtime.qnt:42:5", error)

    def test_unknown_name_is_an_error(self):
        result, _, _, error = check.parse_run(UNKNOWN_NAME_OUTPUT)
        self.assertEqual(result, "error")
        self.assertIn("[QNT404] Name 'stepNope' not found", error)

    def test_parse_error_is_an_error(self):
        result, _, _, error = check.parse_run(PARSE_ERROR_OUTPUT)
        self.assertEqual(result, "error")
        self.assertIn("missing '}' at ','", error)
        self.assertIn("error: parsing failed", error)

    def test_reads_the_longest_trace(self):
        self.assertEqual(check.max_trace_length(OK_OUTPUT), 24)
        self.assertIsNone(check.max_trace_length(VIOLATION_OUTPUT))

    def test_verify_results(self):
        self.assertEqual(check.parse_verify(VERIFY_OK_OUTPUT), ("ok", None))
        self.assertEqual(check.parse_verify("[violation] Found an issue (3698ms).\nerror: found a counterexample\n"),
                         ("violation", None))
        self.assertEqual(check.parse_verify(PARSE_ERROR_OUTPUT)[0], "error")

    def test_trace_from_itf(self):
        self.assertEqual(check.trace_from_itf(ITF), [
            {"action": "init", "picks": {}, "state": {"dlq": [], "running": {"m1": 0, "m2": 0}}},
            {"action": "receiveDesign", "picks": {"m": "m1"}, "state": {"dlq": ["m2"], "running": {"m1": 1, "m2": 0}}},
        ])

    def test_render_trace_shows_changed_keys(self):
        self.assertEqual(check.render_trace(check.trace_from_itf(ITF)), [
            '0. `init`: dlq = []; running = {"m1": 0, "m2": 0}',
            '1. `receiveDesign(m: "m1")`: dlq = ["m2"]; running[m1] = 1',
        ])

    def test_chunk_seeds_are_distinct_and_repeatable(self):
        seeds = [check.chunk_seed("7", index) for index in range(1, 101)]
        self.assertEqual(len(set(seeds)), 100)
        self.assertEqual(seeds[0], check.chunk_seed("7", 1))
        self.assertNotEqual(seeds[0], check.chunk_seed("8", 1))

    def test_tally_sums_runs_and_chunks_per_invariant(self):
        records = [
            {"step": "stepDesign", "invariants": ["a"], "result": "ok", "explored": 10000,
             "witnesses": {"settled": 9000}, "max_length": 7, "violated": {}},
            {"step": "stepDesign", "invariants": ["a", "b"], "result": "violation", "explored": 500,
             "witnesses": {"settled": 400}, "max_length": None, "violated": {"b": []}},
        ]
        totals = check.tally(records)
        self.assertEqual(totals[("stepDesign", "a")],
                         {"explored": 10500, "witnesses": {"settled": 9400}, "max_length": 7, "result": "ok"})
        self.assertEqual(totals[("stepDesign", "b")]["result"], "violation")

    def test_verify_targets_the_design_and_unkilled_invariants(self):
        args = check.build_parser().parse_args(["spec.qnt", "--main", "m", "--invariants", "a", "b",
                                                "--terminal", "t", "--verify"])
        kills = {"stepMutX": {"a": "sampling", "b": None}, "stepMutY": {"a": None, "b": None}}
        self.assertEqual(check.verify_targets(args, ["stepMutX", "stepMutY"], kills),
                         {"stepDesign": ["a", "b"], "stepMutX": ["b"], "stepMutY": ["b"]})
        args.verify_step = ["stepMutY"]
        self.assertEqual(check.verify_targets(args, ["stepMutX", "stepMutY"], kills), {"stepMutY": ["a", "b"]})

    def test_discovers_steps_by_naming_convention(self):
        self.assertEqual(check.discover_steps(EXAMPLE.read_text()),
                         ["step", "stepDesign", "stepMutNoLease", "stepMutAckLiveLease"])

    def test_discovery_rejects_a_misnamed_step(self):
        with self.assertRaisesRegex(check.UsageError, "stepNoGuard"):
            check.discover_steps("action stepDesign = x\naction stepNoGuard = y\n")

    def test_insufficient_samples_uses_the_summed_count(self):
        args = check.build_parser().parse_args(["spec.qnt", "--main", "m", "--invariants", "a", "--terminal", "t"])
        totals = {("stepDesign", "a"): {"explored": 900, "witnesses": {"t": 900}, "max_length": 5, "result": "ok"}}
        init_probe = {"witnesses": {"t": 0}}
        self.assertEqual([p["code"] for p in check.find_problems(args, ["stepDesign"], totals, {}, [], init_probe, {})],
                         ["insufficient-samples", "unkilled-invariant"])
        totals[("stepDesign", "a")]["explored"] = 20000
        self.assertEqual([p["code"] for p in check.find_problems(args, ["stepDesign"], totals, {}, [], init_probe, {})],
                         ["unkilled-invariant"])

    def test_discovery_skips_comments_and_actions_with_parameters(self):
        text = ("// action stepMutOld = x\n/* action stepMutGone = y */\n"
                "action stepMutReal(a) = z\naction stepDesign = w\n")
        self.assertEqual(check.discover_steps(text), ["stepDesign"])

    def test_var_count_skips_comments(self):
        text = ("var a: int  // var b: int\n// var c: int\n/* var d: int\n   var e: int */\n"
                "  var f : bool\nval variant = a\n")
        self.assertEqual(check.count_vars(text), 2)
        self.assertEqual(check.count_vars(EXAMPLE.read_text()), 8)

    def test_spec_over_budget_only_past_a_limit(self):
        def warnings(variables, invariants):
            args = check.build_parser().parse_args(["spec.qnt", "--main", "m", "--invariants", *invariants,
                                                    "--terminal", "t"])
            return check.find_warnings(args, variables)

        self.assertEqual(warnings(8, ["a", "b", "c"]), [])
        self.assertEqual(warnings(9, ["a"]), [check.problem(
            "spec-over-budget", "the spec has 9 state variables and 1 invariant; the limit is 8 and 3, "
            "so split it into 2 flows or trim it")])
        self.assertEqual([w["code"] for w in warnings(2, ["a", "b", "c", "d"])], ["spec-over-budget"])


class UsageTests(unittest.TestCase):
    def test_too_few_samples_is_a_usage_error(self):
        code, out, err = run_cli(EXAMPLE, *ARGS, "--samples", "100")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("--samples must be 10000 or more", err)

    def test_missing_design_step_is_a_usage_error(self):
        code, out, err = run_cli(EXAMPLE, *ARGS, "--steps", "step", "stepMutNoLease")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("stepDesign", err)

    def test_step_outside_the_naming_convention_is_a_usage_error(self):
        code, _, err = run_cli(EXAMPLE, *ARGS, "--steps", "stepDesign", "designWith")
        self.assertEqual(code, 2)
        self.assertIn("designWith", err)

    def test_verify_step_must_be_the_design_or_a_mutant(self):
        code, _, err = run_cli(EXAMPLE, *ARGS, "--verify-step", "step")
        self.assertEqual(code, 2)
        self.assertIn("--verify-step", err)

    def test_misnamed_step_in_the_spec_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = write_variant(tmp, "action stepMutNoLease =", "action stepNoLease =")
            code, out, err = run_cli(spec, *ARGS)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("stepNoLease", err)

    def test_unreadable_or_binary_spec_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "binary.qnt"
            binary.write_bytes(b"\xff\xfe")
            locked = Path(tmp) / "locked.qnt"
            locked.write_text("module m {}")
            locked.chmod(0)
            try:
                for spec in (binary, locked):
                    code, out, err = run_cli(spec, *ARGS)
                    self.assertEqual((code, out), (2, ""), err)
                    self.assertIn("can't read", err)
            finally:
                locked.chmod(0o644)

    def test_crash_exits_3(self):
        with mock.patch.object(check, "check", side_effect=RuntimeError("boom")):
            code, out, err = run_cli(EXAMPLE, *ARGS)
        self.assertEqual((code, out), (3, ""))
        self.assertIn("RuntimeError: boom", err)

    def test_missing_quint_exits_4(self):
        result = subprocess.run([sys.executable, SCRIPT, EXAMPLE, *ARGS], capture_output=True, text=True,
                                env={"PATH": "/nonexistent", "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("quint is missing", result.stderr)


@unittest.skipUnless(shutil.which("quint"), "quint is not installed")
class ExampleRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code, cls.report, _ = run_json(EXAMPLE, *ARGS)

    def test_passes(self):
        self.assertEqual((self.code, self.report["verdict"], self.report["problems"]), (0, "pass", []))
        self.assertEqual(self.report["design"]["result"], "pass")

    def test_spec_at_the_size_limit_has_no_warnings(self):
        self.assertEqual(self.report["warnings"], [])
        self.assertNotIn("## Warnings", check.render_md(self.report))

    def test_every_invariant_is_killed(self):
        matrix = self.report["matrix"]
        self.assertEqual(set(matrix), {"stepMutNoLease", "stepMutAckLiveLease"})
        for invariant in INVARIANTS:
            self.assertTrue(any(row[invariant] for row in matrix.values()), invariant)

    def test_current_code_loses_messages(self):
        current = self.report["current"]
        self.assertEqual(current["violated"], ["noLostMessages"])
        trace = current["counterexamples"]["noLostMessages"]
        self.assertGreater(len(trace), 1)
        self.assertEqual(trace[0]["action"], "init")
        self.assertTrue(all(isinstance(step["action"], str) and step["action"] for step in trace))
        self.assertIn("visible", trace[-1]["state"])

    def test_every_run_explores_or_fails(self):
        self.assertEqual(len(self.report["runs"]), 12)
        for run in self.report["runs"]:
            self.assertIn(run["result"], ("ok", "violation"), run["command"])
            if run["result"] == "ok":
                self.assertEqual(run["explored"], 10000)

    def test_result_line_matches_the_format(self):
        line = self.report["result_line"]
        self.assertRegex(line, f"^{RESULT_LINE.pattern}$")
        self.assertTrue(line.endswith("random sampling, 10000 runs ≤30 steps; current code: fails noLostMessages"),
                        line)

    def test_markdown_holds_the_result_file_sections(self):
        md = check.render_md(self.report)
        self.assertTrue(md.startswith(self.report["result_line"] + "\n"))
        for heading in ("## Commands", "## Mutants", "## Counterexamples", "### `step` violates `noLostMessages`"):
            self.assertIn(heading, md)
        self.assertIn("1. `", md)


@unittest.skipUnless(shutil.which("quint"), "quint is not installed")
class BrokenExamples(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_design_without_the_lease_fails(self):
        spec = write_variant(self.tmp.name, 'action stepDesign = designWith("retry")',
                             'action stepDesign = designWith("takeOver")')
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, report["verdict"]), (1, "fail"))
        self.assertIn("oneOwner", report["design"]["violated"])
        self.assertIn("design: fails", report["result_line"])

    def test_syntax_error_is_a_broken_spec(self):
        spec = write_variant(self.tmp.name, "action init = all {", "action init = all {{")
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, report["verdict"], report["runs"]), (3, "broken-spec", []))
        self.assertIn("parsing failed", report["typecheck"]["error"])
        self.assertIn("broken spec: Error [QNT000]", report["result_line"])

    def test_broken_spec_still_warns_over_budget(self):
        spec = write_variant(self.tmp.name, "action init = all {", "action init = all {{")
        code, report, _ = run_json(spec, "--main", "queue_consumer", "--invariants", *INVARIANTS, "extra",
                                   "--terminal", "settled")
        self.assertEqual((code, report["verdict"]), (3, "broken-spec"))
        self.assertEqual([w["code"] for w in report["warnings"]], ["spec-over-budget"])
        self.assertIn("8 state variables and 4 invariants", report["warnings"][0]["message"])

    def test_runtime_error_is_a_broken_spec(self):
        spec = write_variant(self.tmp.name, "visible.get(m) > 0,\n    receives.get(m) >= MAX_RECEIVES,",
                             'visible.get("zz") > 0,\n    receives.get(m) >= MAX_RECEIVES,')
        code, report, _ = run_json(spec, *ARGS, "--steps", "stepDesign")
        self.assertEqual((code, report["verdict"]), (3, "broken-spec"))
        self.assertTrue(report["typecheck"]["ok"])
        self.assertIn("QNT507", report["runs"][0]["error"])

    def test_terminal_witness_that_never_holds_is_vacuous(self):
        spec = write_variant(self.tmp.name,
                             "val settled = MESSAGES.forall(m => visible.get(m) == 0 and running.get(m) == 0)",
                             "val settled = false")
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, report["verdict"]), (2, "invalid"))
        self.assertIn("vacuous", codes(report))

    def test_design_step_that_never_fires_is_vacuous(self):
        spec = Path(self.tmp.name) / "never-fires.qnt"
        spec.write_text(NEVER_FIRES_SPEC)
        code, report, _ = run_json(spec, "--main", "never_fires", "--invariants", "safe", "--terminal", "idle",
                                   "--samples", "10000")
        self.assertEqual((code, report["verdict"]), (2, "invalid"))
        self.assertIn("witness-true-at-init", codes(report))
        self.assertTrue(any(p["code"] == "vacuous" and "initial state" in p["message"] for p in report["problems"]),
                        report["problems"])

    def test_witness_true_at_init_is_invalid(self):
        spec = write_variant(self.tmp.name, 'claim.get(m) == "processing" and running.get(m) == 0)',
                             'claim.get(m) == "none")')
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, codes(report)), (2, ["witness-true-at-init"]))
        self.assertIn("orphanClaim", report["problems"][0]["message"])

    def test_failure_path_that_never_happens_is_unreached(self):
        spec = write_variant(self.tmp.name, "val atMostOnce =", "val neverHappens = false\n  val atMostOnce =")
        code, report, _ = run_json(spec, *ARGS[:-2], "neverHappens", *ARGS[-2:])
        self.assertEqual((code, codes(report)), (2, ["unreached-failure-path"]))
        self.assertIn("neverHappens", report["problems"][0]["message"])

    def test_forced_color_output_still_parses(self):
        with mock.patch.dict(os.environ, {"FORCE_COLOR": "1"}):
            code, report, _ = run_json(EXAMPLE, *ARGS)
        self.assertEqual((code, report["verdict"]), (0, "pass"))

    def test_run_timeout_is_invalid(self):
        code, report, _ = run_json(EXAMPLE, *ARGS, "--steps", "stepDesign", "--run-timeout", "0.05")
        self.assertEqual((code, report["verdict"]), (2, "invalid"))
        self.assertIn("run-timeout", codes(report))
        self.assertTrue(all(run["result"] == "timeout" for run in report["runs"]))

    def test_wide_spec_passes_with_a_warning(self):
        spec = Path(self.tmp.name) / "wide.qnt"
        spec.write_text(WIDE_SPEC)
        code, report, _ = run_json(spec, "--main", "wide", "--invariants", "safe", "--terminal", "moved",
                                   "--samples", "10000", "--max-steps", "3")
        self.assertEqual((code, report["verdict"], report["problems"]), (0, "pass", []))
        self.assertEqual([w["code"] for w in report["warnings"]], ["spec-over-budget"])
        self.assertIn("9 state variables", report["warnings"][0]["message"])
        self.assertIn("## Warnings\n\n- `spec-over-budget`: the spec has 9", check.render_md(report))
        self.assertNotIn("spec-over-budget", report["result_line"])

    def test_mutant_identical_to_the_design_is_useless(self):
        spec = write_variant(self.tmp.name, 'action stepDesign = designWith("retry")',
                             'action stepDesign = designWith("retry")\n  action stepMutSame = designWith("retry")')
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, report["verdict"]), (2, "invalid"))
        self.assertEqual(codes(report), ["useless-mutant"])
        self.assertIn("stepMutSame", report["problems"][0]["message"])


def verify_processes():
    pids = set()
    for pattern in (["-x", "java"], ["-f", "apalache"], ["-f", "quint verify"]):
        output = subprocess.run(["pgrep", *pattern], capture_output=True, text=True).stdout
        pids |= {int(pid) for pid in output.split()}
    return pids


@unittest.skipUnless(shutil.which("quint"), "quint is not installed")
class RarePath(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.spec = Path(self.tmp.name) / "rare-path.qnt"
        self.spec.write_text(RARE_SPEC)

    # Every chunk in the budget's first wave finishes, even past the deadline. With 4 workers, chunks 1 to 4 always
    # run, so these tests don't depend on the machine's speed.

    def test_fixed_samples_miss_the_rare_kill(self):
        code, report, _ = run_json(self.spec, *RARE_ARGS)
        self.assertEqual((code, codes(report)), (2, ["unkilled-invariant", "useless-mutant"]), RARE_NOTE)

    def test_budget_kills_the_mutant(self):
        code, report, _ = run_json(self.spec, *RARE_ARGS, "--budget", "6", "--workers", "4")
        self.assertEqual((code, report["verdict"], report["problems"]), (0, "pass", []), RARE_NOTE)
        self.assertEqual(report["kills"], {"stepMutNoGuard": {"safe": "budget"}})
        mutant = next(t for t in report["budget"]["targets"] if t["step"] == "stepMutNoGuard")
        self.assertTrue(mutant["counterexamples"]["safe"][-1]["state"]["broken"])

    def test_budget_sums_the_design_runs(self):
        code, report, _ = run_json(self.spec, *RARE_ARGS, "--steps", "stepDesign", "--budget", "1", "--workers", "4")
        self.assertEqual(code, 2)
        self.assertGreaterEqual(report["design"]["explored"], 10000 + 4 * 10000)
        self.assertIn(f"random sampling, {report['design']['explored']} runs ≤30 steps", report["result_line"])

    def test_budget_attributes_a_design_violation_to_its_invariant(self):
        self.spec.write_text(RARE_SPEC.replace("action stepDesign = stepWith(true)",
                                               "action stepDesign = stepWith(false)"))
        code, report, _ = run_json(self.spec, "--main", "rare_path", "--invariants", "safe", "bounded",
                                   "--terminal", "advanced", "--samples", "10000", "--steps", "stepDesign",
                                   "--budget", "6", "--workers", "4")
        self.assertEqual((code, report["verdict"]), (1, "fail"), RARE_NOTE)
        self.assertEqual(report["design"]["violated"], ["safe"])
        self.assertTrue(report["design"]["counterexamples"]["safe"][-1]["state"]["broken"])
        self.assertTrue(report["result_line"].endswith("design: fails safe"), report["result_line"])

    @unittest.skipUnless(java_works(), "Java is missing")
    def test_verify_step_kills_the_mutant_exhaustively(self):
        code, report, _ = run_json(self.spec, *RARE_ARGS, "--verify", "--verify-step", "stepMutNoGuard")
        self.assertEqual((code, report["verdict"]), (0, "pass"), report["problems"])
        self.assertEqual(report["kills"], {"stepMutNoGuard": {"safe": "verify"}})
        verify = report["verify"]["stepMutNoGuard"]
        self.assertEqual((verify["result"], verify["violated"], verify["bound"]), ("violation", ["safe"], 6))
        self.assertNotIn("stepDesign", report["verify"])


@unittest.skipUnless(shutil.which("quint") and java_works(), "quint or Java is missing")
class VerifyBudget(unittest.TestCase):
    def test_timeout_reports_no_bound_and_leaves_no_process(self):
        before = verify_processes()
        code, report, _ = run_json(EXAMPLE, *ARGS, "--steps", "stepDesign", "--verify", "--verify-budget", "1")
        verify = report["verify"]["stepDesign"]
        self.assertEqual((verify["status"], verify["timed_out"], verify["bound"]), ("ran", True, None))
        self.assertEqual([attempt["result"] for attempt in verify["attempts"]], ["timeout"])
        self.assertEqual((code, report["verdict"]), (2, "invalid"))
        self.assertIn("verify-incomplete", codes(report))
        self.assertIn("random sampling", report["result_line"])
        deadline = time.monotonic() + 5
        while (left := verify_processes() - before) and time.monotonic() < deadline:
            time.sleep(0.2)
        self.assertEqual(left, set(), f"processes left behind: {left}")


if __name__ == "__main__":
    unittest.main()
