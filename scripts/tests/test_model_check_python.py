"""Test the model-check runner on Python specs: the worked example, then one broken variant for each rule."""

import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SKILL = Path(__file__).resolve().parents[2] / "skills/model-check"
EXAMPLE = SKILL / "references/example-queue-consumer.py"
QUINT_EXAMPLE = SKILL / "references/example-queue-consumer.qnt"
sys.path.insert(0, str(SKILL / "scripts"))
# Keep __pycache__ out of the skill folder, which ships as a zip.
sys.dont_write_bytecode = True

import check  # noqa: E402
import explore  # noqa: E402

INVARIANTS = ["noLostMessages", "atMostOnce", "oneOwner"]
ARGS = ["--invariants", *INVARIANTS, "--terminal", "settled", "--witnesses", "orphanClaim"]

# The mutant breaks only after 4 "advance" events in a row and then a "fire". Random sampling misses that path in
# about 4 of 5 runs of 10000 samples. A full search always finds it.
RARE_SPEC = """
NEEDED = 4

def init():
    return {"stage": 0, "broken": False}

def event(s, number, guarded):
    if s["stage"] > NEEDED:
        return False
    s["broken"] = s["broken"] or (not guarded and number == 1 and s["stage"] == NEEDED)
    s["stage"] = s["stage"] + 1 if number == 0 else 0

stepDesign = [(event, number, True) for number in range(14)]
stepMutNoGuard = [(event, number, False) for number in range(14)]

def safe(s):
    return not s["broken"]

def advanced(s):
    return s["stage"] > 0
"""
RARE_ARGS = ["--invariants", "safe", "--terminal", "advanced"]

# The counter never stops, so only the step limit or the state limit ends the search.
UNBOUNDED_SPEC = """
def init():
    return {"count": 0, "broken": False}

def tick(s, guarded):
    s["count"] += 1
    s["broken"] = s["broken"] or not guarded

stepDesign = [(tick, True)]
stepMutBreak = [(tick, False)]

def safe(s):
    return not s["broken"]

def moved(s):
    return s["count"] > 0
"""
UNBOUNDED_ARGS = ["--invariants", "safe", "--terminal", "moved"]

# 2 initial states, a bare action as a move, and a state with a set and a tuple key.
TWO_STARTS_SPEC = """
def init():
    return [{"count": start, "seen": set(), "by": {(1, 2): 0}} for start in (0, 10)]

def tick(s):
    if s["count"] % 10 >= 2:
        return False
    s["count"] += 1
    s["seen"].add(s["count"])

def skip(s):
    if s["count"] % 10 != 0:
        return False
    s["count"] += 2
    s["by"][(1, 2)] += 1

stepDesign = [tick]
stepMutSkip = [tick, skip]

def counted(s):
    return len(s["seen"]) == s["count"] % 10

def done(s):
    return s["count"] % 10 == 2
"""
TWO_STARTS_ARGS = ["--invariants", "counted", "--terminal", "done"]


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


class SpecCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, text, name="spec.py"):
        path = Path(self.tmp.name) / name
        path.write_text(text)
        return path

    def variant(self, old, new):
        source = EXAMPLE.read_text()
        self.assertEqual(source.count(old), 1, old)
        return self.write(source.replace(old, new), "variant.py")


class ExampleRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code, cls.report, _ = run_json(EXAMPLE, *ARGS)

    def test_passes_with_a_full_search(self):
        self.assertEqual((self.code, self.report["verdict"], self.report["problems"]), (0, "pass", []))
        self.assertEqual(self.report["warnings"], [])
        self.assertTrue(all(search["stopped"] is None for search in self.report["searches"].values()))

    def test_every_invariant_is_killed(self):
        self.assertEqual(self.report["matrix"], {
            "stepMutNoLease": {"noLostMessages": False, "atMostOnce": True, "oneOwner": True},
            "stepMutAckLiveLease": {"noLostMessages": True, "atMostOnce": False, "oneOwner": False},
        })

    def test_current_code_loses_messages_by_the_shortest_path(self):
        current = self.report["current"]
        self.assertEqual(current["violated"], ["noLostMessages"])
        trace = current["counterexamples"]["noLostMessages"]
        self.assertEqual([step["action"] for step in trace], ["init", "receiveCurrent", "crash", "receiveCurrent"])
        self.assertEqual(trace[1]["picks"], {"m": "m1"})
        self.assertEqual(trace[-1]["state"]["visible"]["m1"], 0)

    def test_result_line_names_the_search(self):
        states = self.report["searches"]["stepDesign"]["states"]
        self.assertEqual(self.report["result_line"], "Model check: example-queue-consumer — 3 invariants, 2/2 mutants "
                         f"killed; full search, {states} states; current code: fails noLostMessages")

    def test_markdown_holds_the_result_file_sections(self):
        md = check.render_md(self.report)
        self.assertTrue(md.startswith(self.report["result_line"] + "\n"))
        for heading in ("## Search", "## Mutants", "## Counterexamples", "### `step` violates `noLostMessages`"):
            self.assertIn(heading, md)
        self.assertIn('1. `receiveCurrent(m: "m1")`: visible[m1] = 0', md)
        for heading in ("## Commands", "## Bounded check", "## Problems"):
            self.assertNotIn(heading, md)

    def test_needs_no_quint(self):
        with mock.patch.object(shutil, "which", return_value=None):
            code, report, _ = run_json(EXAMPLE, *ARGS)
        self.assertEqual((code, report["verdict"]), (0, "pass"))

    @unittest.skipUnless(shutil.which("quint"), "quint is not installed")
    def test_agrees_with_the_quint_example(self):
        code, quint, _ = run_json(QUINT_EXAMPLE, "--main", "queue_consumer", *ARGS, "--samples", "10000")
        self.assertEqual((code, quint["verdict"]), (self.code, self.report["verdict"]))
        self.assertEqual(quint["matrix"], self.report["matrix"])
        self.assertEqual(quint["current"]["violated"], self.report["current"]["violated"])


class BrokenExamples(SpecCase):
    def test_design_without_the_lease_fails(self):
        spec = self.variant('stepDesign = designWith("retry")', 'stepDesign = designWith("takeOver")')
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, report["verdict"]), (1, "fail"))
        self.assertEqual(report["design"]["violated"], ["atMostOnce", "oneOwner"])
        self.assertTrue(report["result_line"].endswith("design: fails atMostOnce, oneOwner"), report["result_line"])

    def test_syntax_error_is_a_broken_spec(self):
        spec = self.variant("def init():", "def init(:")
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, report["verdict"], report["searches"]), (3, "broken-spec", {}))
        line = EXAMPLE.read_text().splitlines().index("def init():") + 1
        self.assertRegex(report["result_line"],
                         rf"broken spec: SyntaxError: .* at {re.escape(str(spec.resolve()))}:{line}$")
        self.assertIn("## Errors", check.render_md(report))

    def test_error_in_an_action_is_a_broken_spec(self):
        spec = self.variant('    s["dlq"].add(m)', '    s["dlq"].add(s["zz"])')
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, report["verdict"]), (3, "broken-spec"))
        line = EXAMPLE.read_text().splitlines().index('    s["dlq"].add(m)') + 1
        self.assertRegex(report["result_line"], rf"broken spec: KeyError: 'zz' at .*variant\.py:{line}$")

    def test_unknown_invariant_is_a_broken_spec(self):
        code, report, _ = run_json(EXAMPLE, "--invariants", "noSuchRule", "--terminal", "settled")
        self.assertEqual((code, report["verdict"]), (3, "broken-spec"))
        self.assertIn("no function named noSuchRule", report["error"])

    def test_terminal_witness_that_never_holds_is_vacuous(self):
        spec = self.variant("    return all(s[\"visible\"][m] == 0 and s[\"running\"][m] == 0 for m in MESSAGES)",
                            "    return False")
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, report["verdict"]), (2, "invalid"))
        self.assertEqual(set(codes(report)), {"vacuous"})
        self.assertIn("never settles", report["problems"][0]["message"])

    def test_design_step_that_never_fires_is_vacuous(self):
        spec = self.write(UNBOUNDED_SPEC.replace('    s["count"] += 1', "    return False"))
        code, report, _ = run_json(spec, "--invariants", "safe", "--terminal", "moved", "--steps", "stepDesign")
        self.assertEqual((code, report["verdict"]), (2, "invalid"))
        self.assertEqual(codes(report), ["vacuous", "unkilled-invariant"])
        self.assertIn("never fires", report["problems"][0]["message"])

    def test_witness_true_at_init_is_invalid(self):
        spec = self.variant('s["claim"][m] == "processing" and s["running"][m] == 0 for', 's["claim"][m] == "none" for')
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, codes(report)), (2, ["witness-true-at-init"]))
        self.assertIn("orphanClaim", report["problems"][0]["message"])

    def test_failure_path_that_never_happens_is_unreached(self):
        spec = self.variant("def atMostOnce(s):", "def neverHappens(s):\n    return False\n\n\ndef atMostOnce(s):")
        code, report, _ = run_json(spec, *ARGS, "neverHappens")
        self.assertEqual((code, codes(report)), (2, ["unreached-failure-path"]))
        self.assertIn("neverHappens", report["problems"][0]["message"])

    def test_mutant_identical_to_the_design_is_useless(self):
        spec = self.variant('stepDesign = designWith("retry")',
                            'stepDesign = designWith("retry")\nstepMutSame = designWith("retry")')
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, codes(report)), (2, ["useless-mutant"]))
        self.assertIn("stepMutSame", report["problems"][0]["message"])

    def test_nine_state_variables_warn_over_budget(self):
        spec = self.variant('        "dlq": set(),', '        "dlq": set(),\n        "extra": 0,')
        code, report, _ = run_json(spec, *ARGS)
        self.assertEqual((code, report["verdict"]), (0, "pass"))
        self.assertEqual([warning["code"] for warning in report["warnings"]], ["spec-over-budget"])
        self.assertIn("9 state variables", report["warnings"][0]["message"])


class SearchLimits(SpecCase):
    def test_full_search_kills_the_rare_path_mutant(self):
        code, report, _ = run_json(self.write(RARE_SPEC), *RARE_ARGS)
        self.assertEqual((code, report["verdict"], report["problems"]), (0, "pass", []))
        trace = report["searches"]["stepMutNoGuard"]["counterexamples"]["safe"]
        self.assertEqual([step["picks"].get("number") for step in trace], [None, 0, 0, 0, 0, 1])

    def test_step_limit_reports_a_search_to_that_depth(self):
        code, report, _ = run_json(self.write(UNBOUNDED_SPEC), *UNBOUNDED_ARGS, "--max-steps", "5")
        design = report["searches"]["stepDesign"]
        self.assertEqual((code, report["verdict"]), (0, "pass"))
        self.assertEqual((design["stopped"], design["depth"], design["states"]), ("step limit", 5, 6))
        self.assertIn("search to 5 steps, 6 states", report["result_line"])

    def test_state_limit_is_invalid(self):
        code, report, _ = run_json(self.write(UNBOUNDED_SPEC), *UNBOUNDED_ARGS, "--max-states", "3")
        design = report["searches"]["stepDesign"]
        self.assertEqual((code, codes(report)), (2, ["state-limit"]))
        self.assertEqual((design["stopped"], design["depth"]), ("state limit", 2))
        self.assertIn("`stepDesign` passed safe only to 2 steps", report["problems"][0]["message"])

    def test_search_starts_from_every_initial_state(self):
        code, report, _ = run_json(self.write(TWO_STARTS_SPEC), *TWO_STARTS_ARGS)
        self.assertEqual((code, report["verdict"], report["problems"]), (0, "pass", []))
        design = report["searches"]["stepDesign"]
        self.assertEqual((design["states"], design["witnesses"]["done"], design["stopped"]), (6, 2, None))

    def test_counterexample_prints_a_bare_action_a_set_and_a_tuple_key(self):
        _, report, _ = run_json(self.write(TWO_STARTS_SPEC), *TWO_STARTS_ARGS)
        trace = report["searches"]["stepMutSkip"]["counterexamples"]["counted"]
        self.assertEqual(trace, [
            {"action": "init", "picks": {}, "state": {"count": 0, "seen": [], "by": {"(1, 2)": 0}}},
            {"action": "skip", "picks": {}, "state": {"count": 2, "seen": [], "by": {"(1, 2)": 1}}},
        ])
        self.assertIn("1. `skip`: count = 2; by[(1, 2)] = 1", check.render_md(report))

    def test_spec_without_init_is_a_broken_spec(self):
        code, report, _ = run_json(self.write(UNBOUNDED_SPEC.replace("def init():", "def start():")), *UNBOUNDED_ARGS)
        self.assertEqual((code, report["verdict"]), (3, "broken-spec"))
        self.assertIn("broken spec: the spec defines no `init()` function", report["result_line"])

    def test_init_that_returns_no_dict_is_a_broken_spec(self):
        spec = self.write(UNBOUNDED_SPEC.replace('return {"count": 0, "broken": False}', "return []"))
        code, report, _ = run_json(spec, *UNBOUNDED_ARGS)
        self.assertEqual((code, report["verdict"]), (3, "broken-spec"))
        self.assertIn("`init()` must return one state dict", report["error"])

    def test_error_in_init_names_its_line(self):
        spec = self.write(UNBOUNDED_SPEC.replace('return {"count": 0, "broken": False}', "return {}[0]"))
        code, report, _ = run_json(spec, *UNBOUNDED_ARGS)
        self.assertEqual((code, report["verdict"]), (3, "broken-spec"))
        self.assertRegex(report["result_line"], r"broken spec: KeyError: 0 at .*spec\.py:3$")

    def test_search_that_ends_at_the_step_limit_is_still_full(self):
        spec = self.write(TWO_STARTS_SPEC)
        _, exact, _ = run_json(spec, *TWO_STARTS_ARGS, "--max-steps", "2")
        self.assertEqual((exact["searches"]["stepDesign"]["stopped"], exact["searches"]["stepDesign"]["states"]),
                         (None, 6))
        self.assertIn("full search, 6 states", exact["result_line"])
        _, short, _ = run_json(spec, *TWO_STARTS_ARGS, "--max-steps", "1")
        self.assertEqual(short["searches"]["stepDesign"]["stopped"], "step limit")
        self.assertIn("search to 1 step, 4 states", short["result_line"])

    def test_time_limit_is_invalid(self):
        with mock.patch.object(explore.time, "monotonic", side_effect=range(0, 10**6, 100)):
            code, report, _ = run_json(self.write(UNBOUNDED_SPEC), *UNBOUNDED_ARGS, "--steps", "stepDesign",
                                       "--run-timeout", "50")
        self.assertEqual((code, codes(report)), (2, ["run-timeout", "unkilled-invariant"]))
        self.assertEqual(report["searches"]["stepDesign"]["stopped"], "time limit")
        self.assertIn("--run-timeout of 50 seconds", report["problems"][0]["message"])

    def test_spec_that_exits_is_a_broken_spec(self):
        for old, new in (('    s["count"] += 1', "    raise SystemExit(0)"), ("def moved(s):", "raise SystemExit(0)\n\ndef moved(s):")):
            code, report, _ = run_json(self.write(UNBOUNDED_SPEC.replace(old, new)), *UNBOUNDED_ARGS)
            self.assertEqual((code, report["verdict"]), (3, "broken-spec"), new)
            self.assertIn("broken spec: SystemExit: 0 at ", report["result_line"])

    def test_print_in_the_spec_stays_out_of_the_report(self):
        spec = self.write(UNBOUNDED_SPEC.replace('    s["count"] += 1', '    s["count"] += 1\n    print("debug", s)'))
        code, out, err = run_cli(spec, *UNBOUNDED_ARGS, "--max-steps", "3")
        self.assertEqual((code, json.loads(out)["verdict"]), (0, "pass"))
        self.assertIn("debug {'count': 1", err)

    def test_equal_states_count_once(self):
        frozen = {explore.freeze({"a": {"x": 1, "y": [1, {2}]}, "b": set()}),
                  explore.freeze({"b": set(), "a": {"y": [1, {2}], "x": 1}})}
        self.assertEqual(len(frozen), 1)

    def test_states_of_different_types_stay_apart(self):
        pairs = [({"a": 1}, {"a": True}), ({"a": [1, 2]}, {"a": (1, 2)}), ({"a": {}}, {"a": set()}),
                 ({"a": {1: 2}}, {"a": {(1, ("dict", frozenset()))}})]
        for left, right in pairs:
            self.assertNotEqual(explore.freeze(left), explore.freeze(right), (left, right))

    def test_an_action_never_changes_the_state_it_was_given(self):
        state = {"count": 0, "items": {"a": [1]}, "seen": {1}}
        after = explore.copy(state)
        after["items"]["a"].append(2)
        after["seen"].add(2)
        self.assertEqual(state, {"count": 0, "items": {"a": [1]}, "seen": {1}})


class UsageTests(SpecCase):
    def test_missing_design_step_is_a_usage_error(self):
        code, out, err = run_cli(EXAMPLE, *ARGS, "--steps", "step", "stepMutNoLease")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("stepDesign", err)

    def test_misnamed_step_in_the_spec_is_a_usage_error(self):
        spec = self.variant("stepMutNoLease =", "stepNoLease =")
        code, out, err = run_cli(spec, *ARGS)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("stepNoLease", err)

    def test_step_that_the_spec_lacks_is_a_usage_error(self):
        code, out, err = run_cli(EXAMPLE, *ARGS, "--steps", "stepDesign", "stepMutGone")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("stepMutGone", err)

    def test_quint_options_are_a_usage_error(self):
        for option in (["--verify"], ["--budget", "60"], ["--verify-step", "stepDesign"]):
            code, out, err = run_cli(EXAMPLE, *ARGS, *option)
            self.assertEqual((code, out), (2, ""), option)
            self.assertIn("apply to a .qnt spec", err)

    def test_limit_out_of_range_is_a_usage_error(self):
        for option in (["--max-states", "0"], ["--max-steps", "-1"], ["--run-timeout", "0"]):
            code, out, err = run_cli(EXAMPLE, *ARGS, *option)
            self.assertEqual((code, out), (2, ""), option)
            self.assertIn("--max-states must be 1 or more", err)

    def test_step_that_is_not_a_list_is_a_usage_error(self):
        for new in ('stepMutNoLease = tuple(designWith("takeOver"))', 'def stepMutNoLease():\n    return []'):
            spec = self.variant('stepMutNoLease = designWith("takeOver")', new)
            code, out, err = run_cli(spec, *ARGS)
            self.assertEqual((code, out), (2, ""), new)
            self.assertIn("stepMutNoLease must be a module-level list of moves", err)

    def test_qnt_spec_without_main_is_a_usage_error(self):
        code, out, err = run_cli(QUINT_EXAMPLE, *ARGS)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("--main", err)


if __name__ == "__main__":
    unittest.main()
