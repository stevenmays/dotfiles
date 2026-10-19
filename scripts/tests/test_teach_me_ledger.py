import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from fractions import Fraction
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills/teach-me/scripts/ledger.py"
sys.path.insert(0, str(SCRIPT.parent))
# Keep __pycache__ out of the skill folder, which ships as a zip.
sys.dont_write_bytecode = True

import ledger  # noqa: E402

SPEC_EXAMPLE = """# Learning ledger

<!-- teach-me ledger v1. Change it with scripts/ledger.py so the format stays parseable. -->

## Knowledge points

### tensors — PyTorch tensors, Build a Large Language Model ch. 2
- tensor-rank: Rank is the number of indices that name one number.
- tensor-shape: Read a tensor's shape as one size per axis. (builds on: tensor-rank)

## Log

- 2026-10-14 tensor-rank learned
- 2026-10-14 tensor-shape miss — wrote [4, 8] for 8 rows of 4
"""

STATUS_FIXTURE = """# Learning ledger

<!-- teach-me ledger v1. Change it with scripts/ledger.py so the format stays parseable. -->

## Knowledge points

### tensors — PyTorch tensors
- tensor-rank: Rank is the number of indices that name one number.
- tensor-shape: Read a tensor's shape as one size per axis. (builds on: tensor-rank)
- broadcasting: Broadcasting aligns shapes from the right. (builds on: tensor-shape)

### embeddings
- embedding-lookup: An embedding layer maps token IDs to rows. (builds on: tensor-shape, tensor-rank)
- position-ids: Position IDs index each token's position. (builds on: embedding-lookup)

## Log

- 2026-10-01 tensor-rank learned
- 2026-10-01 tensor-shape learned
- 2026-10-01 broadcasting learned
- 2026-10-02 tensor-rank solid
- 2026-10-02 tensor-shape shaky
- 2026-10-02 broadcasting solid
- 2026-10-05 broadcasting miss — aligned shapes from the left
- 2026-10-05 embedding-lookup learned
"""

EXPECTED_STATUS = """Ledger: 5 knowledge points in 2 topics. Today: 2026-10-09.
Retention (reviews after the learning day): 2 of 4 solid (50%).
Next review: 2026-10-09, 3 knowledge points, about 5 questions.

Open gaps (missed, not yet relearned):
  broadcasting [tensors] missed 2026-10-05 — aligned shapes from the left
Due now (most overdue first):
  tensor-shape [tensors] due 2026-10-03, 6 days late, last shaky, interval 1d
  embedding-lookup [embeddings] due 2026-10-06, 3 days late, last learned, interval 1d
Not learned yet: position-ids
Coming up: 2026-10-10 (1)
Strength: 3 fragile (under 7d), 0 firm (7-29d), 0 long-term (30d+)
"""


def build(kp_lines, log_lines=()):
    return "\n".join([
        "# Learning ledger",
        "",
        "## Knowledge points",
        "",
        "### t",
        *kp_lines,
        "",
        "## Log",
        "",
        *log_lines,
    ]) + "\n"


def schedule(kp_lines, log_lines):
    return ledger.replay(ledger.parse(build(kp_lines, log_lines))).states


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = ledger.main([str(arg) for arg in argv])
    return code, out.getvalue(), err.getvalue()


CHAIN = ["- a: A."]


class ParseTests(unittest.TestCase):
    def test_parses_valid_ledger(self):
        parsed = ledger.parse(SPEC_EXAMPLE)
        self.assertEqual(list(parsed.topics), ["tensors"])
        self.assertEqual(parsed.topics["tensors"].title, "PyTorch tensors, Build a Large Language Model ch. 2")
        self.assertEqual(list(parsed.kps), ["tensor-rank", "tensor-shape"])
        self.assertEqual(parsed.kps["tensor-shape"].statement, "Read a tensor's shape as one size per axis.")
        self.assertEqual(parsed.kps["tensor-shape"].builds_on, ["tensor-rank"])
        self.assertEqual(parsed.kps["tensor-rank"].builds_on, [])
        self.assertEqual(
            [(e.day, e.kp, e.result, e.note) for e in parsed.events],
            [
                (date(2026, 10, 14), "tensor-rank", "learned", None),
                (date(2026, 10, 14), "tensor-shape", "miss", "wrote [4, 8] for 8 rows of 4"),
            ],
        )

    def test_ignores_blank_lines_and_multiline_comments(self):
        text = build(["<!-- a note", "spanning lines -->", "- a: A.", "", "<!-- one line -->"])
        self.assertEqual(list(ledger.parse(text).kps), ["a"])

    def test_each_validation_error_names_its_line(self):
        cases = [
            ("malformed kp line", ["a: A."], [], "a: A.", "expected a '### TOPIC_ID' heading"),
            ("malformed topic heading", ["### Tensors"], [], "### Tensors", "malformed topic heading"),
            ("malformed log line", ["- a: A."], ["- 2026-10-14 a"], "- 2026-10-14 a", "malformed log line"),
            ("log note without dash", ["- a: A."], ["- 2026-10-14 a solid extra"], "- 2026-10-14 a solid extra", "malformed log line"),
            ("duplicate id", ["- a: A.", "- a: Again."], [], "- a: Again.", "duplicate knowledge point id 'a'"),
            ("unknown builds on", ["- a: A. (builds on: zzz)"], [], "- a: A. (builds on: zzz)", "unknown id 'zzz'"),
            ("cycle", ["- a: A. (builds on: b)", "- b: B. (builds on: a)"], [], "- a: A. (builds on: b)", "builds-on cycle: a -> b -> a"),
            ("self cycle", ["- a: A. (builds on: a)"], [], "- a: A. (builds on: a)", "builds-on cycle"),
            ("bad result", ["- a: A."], ["- 2026-10-14 a passed"], "- 2026-10-14 a passed", "bad result 'passed'"),
            ("bad date format", ["- a: A."], ["- 10/14/2026 a solid"], "- 10/14/2026 a solid", "bad date '10/14/2026'"),
            ("impossible date", ["- a: A."], ["- 2026-02-30 a solid"], "- 2026-02-30 a solid", "bad date '2026-02-30'"),
            ("unknown log kp", ["- a: A."], ["- 2026-10-14 zzz solid"], "- 2026-10-14 zzz solid", "unknown knowledge point 'zzz'"),
        ]
        for name, kp_lines, log_lines, bad_line, fragment in cases:
            with self.subTest(name):
                text = build(kp_lines, log_lines)
                number = text.split("\n").index(bad_line) + 1
                with self.assertRaises(ledger.LedgerError) as caught:
                    ledger.parse(text)
                self.assertIn(f"line {number}: ", str(caught.exception))
                self.assertIn(fragment, str(caught.exception))

    def test_kp_before_topic_heading_is_an_error(self):
        text = "# Learning ledger\n\n## Knowledge points\n\n- a: A.\n\n## Log\n"
        with self.assertRaisesRegex(ledger.LedgerError, "line 5: knowledge point before any"):
            ledger.parse(text)


class ScheduleTests(unittest.TestCase):
    def test_worked_check_intervals(self):
        states = schedule(CHAIN, ["- 2026-10-14 a learned"])
        self.assertEqual((states["a"].interval, states["a"].due), (1, date(2026, 10, 15)))
        log = ["- 2026-10-14 a learned"]
        expected = [("2026-10-15", 3, date(2026, 10, 18)), ("2026-10-18", 8, date(2026, 10, 26)), ("2026-10-26", 20, date(2026, 11, 15))]
        for day, interval, due in expected:
            log.append(f"- {day} a solid")
            state = schedule(CHAIN, log)["a"]
            self.assertEqual((state.interval, state.due, state.ease), (interval, due, Fraction(5, 2)))

    def test_late_solid_uses_half_the_lateness(self):
        state = schedule(CHAIN, ["- 2026-10-14 a learned", "- 2026-10-15 a solid", "- 2026-10-22 a solid"])["a"]
        # (3 + 4/2) * 2.5 = 12.5 rounds up to 13; full lateness would give 18.
        self.assertEqual((state.interval, state.due), (13, date(2026, 11, 4)))

    def test_early_solid_uses_elapsed_days(self):
        log = ["- 2026-10-14 a learned", "- 2026-10-15 a solid", "- 2026-10-18 a solid", "- 2026-10-22 a solid"]
        state = schedule(CHAIN, log)["a"]
        self.assertEqual((state.interval, state.due), (10, date(2026, 11, 1)))

    def test_interval_caps_at_365_days(self):
        state = schedule(CHAIN, ["- 2026-10-14 a learned", "- 2026-10-15 a solid", "- 2027-10-18 a solid"])["a"]
        self.assertEqual(state.interval, 365)

    def test_shaky_review_means_retry_tomorrow(self):
        base = ["- 2026-10-14 a learned", "- 2026-10-15 a solid", "- 2026-10-18 a solid"]
        for name, day, due in [
            ("early", "2026-10-20", date(2026, 10, 21)),
            ("on time", "2026-10-26", date(2026, 10, 27)),
            ("late", "2026-10-30", date(2026, 10, 31)),
        ]:
            with self.subTest(name):
                state = schedule(CHAIN, base + [f"- {day} a shaky"])["a"]
                self.assertEqual(state.interval, 1)
                self.assertEqual(state.due, due)
                self.assertEqual(state.ease, Fraction("2.35"))
                self.assertEqual(state.lapses, 0)
                self.assertFalse(state.open_gap)

    def test_shaky_on_learning_day_still_learns(self):
        state = schedule(CHAIN, ["- 2026-10-14 a shaky"])["a"]
        self.assertTrue(state.learned)
        self.assertEqual((state.interval, state.ease), (1, Fraction(5, 2)))

    def test_miss_review_lowers_ease_counts_a_lapse_and_opens_a_gap(self):
        state = schedule(CHAIN, ["- 2026-10-14 a learned", "- 2026-10-15 a solid", "- 2026-10-18 a miss"])["a"]
        self.assertEqual((state.ease, state.lapses, state.interval), (Fraction("2.3"), 1, 1))
        self.assertTrue(state.open_gap)
        self.assertEqual(state.due, date(2026, 10, 18))

    def test_learned_on_a_review_day_relearns_with_interval_one(self):
        log = ["- 2026-10-14 a learned", "- 2026-10-15 a solid", "- 2026-10-18 a miss", "- 2026-10-19 a learned"]
        state = schedule(CHAIN, log)["a"]
        self.assertFalse(state.open_gap)
        self.assertEqual((state.interval, state.due), (1, date(2026, 10, 20)))

    def test_ease_floors_at_1_3(self):
        log = ["- 2026-10-01 a learned"] + [f"- 2026-10-{day:02d} a miss" for day in range(2, 9)]
        state = schedule(CHAIN, log)["a"]
        self.assertEqual((state.ease, state.lapses), (Fraction("1.3"), 7))
        state = schedule(CHAIN, log + ["- 2026-10-09 a shaky"])["a"]
        self.assertEqual((state.ease, state.lapses, state.open_gap), (Fraction("1.3"), 7, False))

    def test_ease_stays_exact_to_two_decimals(self):
        log = ["- 2026-10-01 a learned"] + [f"- 2026-10-{day:02d} a shaky" for day in range(2, 7)]
        state = schedule(CHAIN, log)["a"]
        self.assertEqual(state.ease, Fraction("1.75"))
        self.assertEqual(state.ease * 100, round(state.ease * 100))
        log = ["- 2026-10-01 a learned", "- 2026-10-02 a shaky", "- 2026-10-03 a shaky"]
        self.assertEqual(schedule(CHAIN, log)["a"].ease, Fraction("2.2"))

    def test_miss_then_solid_same_day_takes_the_worst(self):
        log = ["- 2026-10-14 a learned", "- 2026-10-15 a solid", "- 2026-10-18 a miss", "- 2026-10-18 a solid"]
        state = schedule(CHAIN, log)["a"]
        self.assertEqual((state.interval, state.due, state.lapses), (1, date(2026, 10, 19), 1))
        self.assertEqual(state.ease, Fraction("2.3"))
        self.assertFalse(state.open_gap)
        self.assertEqual(state.last_result, "miss")

    def test_miss_as_last_event_leaves_an_open_gap(self):
        log = ["- 2026-10-14 a learned", "- 2026-10-15 a solid", "- 2026-10-18 a solid", "- 2026-10-18 a miss"]
        state = schedule(CHAIN, log)["a"]
        self.assertTrue(state.open_gap)
        self.assertEqual((state.due, state.lapses), (date(2026, 10, 18), 1))

    def test_learning_day_miss_stays_unlearned_with_a_gap(self):
        state = schedule(CHAIN, ["- 2026-10-14 a miss"])["a"]
        self.assertFalse(state.learned)
        self.assertTrue(state.open_gap)
        self.assertEqual((state.due, state.ease, state.lapses), (date(2026, 10, 14), Fraction(5, 2), 0))
        state = schedule(CHAIN, ["- 2026-10-14 a miss", "- 2026-10-15 a learned"])["a"]
        self.assertTrue(state.learned)
        self.assertFalse(state.open_gap)
        self.assertEqual((state.interval, state.due), (1, date(2026, 10, 16)))

    def test_retention_counts_review_days_by_their_worst_result(self):
        log = [
            "- 2026-10-14 a miss",
            "- 2026-10-14 a learned",
            "- 2026-10-15 a solid",
            "- 2026-10-18 a solid",
            "- 2026-10-18 a shaky",
            "- 2026-10-19 a solid",
        ]
        self.assertEqual(ledger.replay(ledger.parse(build(CHAIN, log))).reviews, ["solid", "shaky", "solid"])


PAIR = ["- p: P.", "- x: X. (builds on: p)"]


class ImplicitCreditTests(unittest.TestCase):
    def test_solid_on_dependent_gives_due_prerequisite_half_a_repetition(self):
        log = ["- 2026-10-14 p learned", "- 2026-10-14 x learned", "- 2026-10-15 p solid", "- 2026-10-19 x solid"]
        p = schedule(PAIR, log)["p"]
        # late 1: (3 + 1/2) * (1 + 1.5/2) = 6.125 rounds to 6.
        self.assertEqual((p.interval, p.due, p.implicit_credits), (6, date(2026, 10, 25), 1))
        self.assertEqual((p.ease, p.last_review), (Fraction(5, 2), date(2026, 10, 19)))

    def test_no_credit_before_the_prerequisites_first_explicit_review(self):
        log = ["- 2026-10-14 p learned", "- 2026-10-14 p solid", "- 2026-10-14 x learned", "- 2026-10-16 x solid"]
        p = schedule(PAIR, log)["p"]
        self.assertEqual((p.interval, p.due, p.implicit_credits), (1, date(2026, 10, 15), 0))

    def test_no_credit_when_prerequisites_last_result_was_shaky_or_miss(self):
        base = ["- 2026-10-14 p learned", "- 2026-10-14 x learned", "- 2026-10-15 p solid"]
        for result in ("shaky", "miss"):
            with self.subTest(result):
                log = base + [f"- 2026-10-18 p {result}", "- 2026-10-18 p solid" if result == "miss" else "- 2026-10-18 p shaky", "- 2026-10-20 x solid"]
                p = schedule(PAIR, log)["p"]
                self.assertEqual((p.interval, p.due, p.implicit_credits), (1, date(2026, 10, 19), 0))

    def test_no_credit_when_prerequisite_is_not_due(self):
        log = ["- 2026-10-14 p learned", "- 2026-10-14 x learned", "- 2026-10-15 p solid", "- 2026-10-16 x solid"]
        p = schedule(PAIR, log)["p"]
        self.assertEqual((p.interval, p.due, p.implicit_credits), (3, date(2026, 10, 18), 0))

    def test_no_credit_when_prerequisite_had_its_own_graded_event(self):
        log = ["- 2026-10-14 p learned", "- 2026-10-14 x learned", "- 2026-10-16 p solid", "- 2026-10-16 x solid"]
        p = schedule(PAIR, log)["p"]
        # p's own late solid: (1 + 1/2) * 2.5 = 3.75 rounds to 4.
        self.assertEqual((p.interval, p.implicit_credits), (4, 0))

    def test_credit_does_not_flow_transitively(self):
        kps = ["- a: A.", "- b: B. (builds on: a)", "- c: C. (builds on: b)"]
        log = [f"- 2026-10-14 {k} learned" for k in "abc"] + ["- 2026-10-15 a solid", "- 2026-10-15 b solid", "- 2026-10-19 c solid"]
        states = schedule(kps, log)
        self.assertEqual(states["b"].implicit_credits, 1)
        self.assertEqual((states["a"].implicit_credits, states["a"].interval), (0, 3))

    def test_no_credit_below_ease_2_2(self):
        log = [
            "- 2026-10-01 p learned",
            "- 2026-10-01 x learned",
            "- 2026-10-02 p miss",
            "- 2026-10-02 p learned",
            "- 2026-10-03 p shaky",
            "- 2026-10-04 p solid",
            "- 2026-10-07 x solid",
        ]
        p = schedule(PAIR, log)["p"]
        self.assertEqual((p.ease, p.last_result), (Fraction("2.15"), "solid"))
        self.assertEqual((p.interval, p.due, p.implicit_credits), (2, date(2026, 10, 6), 0))

    def test_credit_applies_at_exactly_ease_2_2(self):
        log = [
            "- 2026-10-01 p learned",
            "- 2026-10-01 x learned",
            "- 2026-10-02 p shaky",
            "- 2026-10-03 p shaky",
            "- 2026-10-04 p solid",
            "- 2026-10-07 x solid",
        ]
        p = schedule(PAIR, log)["p"]
        self.assertEqual(p.ease, Fraction("2.2"))
        # late 1: (2 + 1/2) * (1 + 1.2/2) = 4.
        self.assertEqual((p.interval, p.due, p.implicit_credits), (4, date(2026, 10, 11), 1))

    def test_covers_skips_prerequisites_that_need_their_own_question(self):
        kps = ["- p: P.", "- q: Q.", "- x: X. (builds on: p, q)"]
        log = [f"- 2026-10-14 {k} learned" for k in "pqx"] + ["- 2026-10-15 p solid", "- 2026-10-15 q solid", "- 2026-10-15 x solid", "- 2026-10-18 q shaky"]
        parsed = ledger.parse(build(kps, log))
        out = ledger.render_status(parsed, ledger.replay(parsed), date(2026, 10, 19))
        self.assertIn("Covers: a solid on x also credits due p.\n", out)
        self.assertIn("Next review: 2026-10-19, 3 knowledge points, about 4 questions.\n", out)


class PenaltyTests(unittest.TestCase):
    BASE = [
        "- 2026-10-01 p learned",
        "- 2026-10-01 x learned",
        "- 2026-10-02 p solid",
        "- 2026-10-02 x solid",
        "- 2026-10-05 p solid",
        "- 2026-10-05 x solid",
    ]

    def test_miss_pulls_dependent_due_date_to_tomorrow(self):
        before = schedule(PAIR, self.BASE)["x"]
        self.assertEqual((before.interval, before.due), (8, date(2026, 10, 13)))
        x = schedule(PAIR, self.BASE + ["- 2026-10-07 p miss"])["x"]
        self.assertEqual(x.due, date(2026, 10, 8))
        self.assertEqual((x.interval, x.ease, x.last_review), (8, Fraction(5, 2), date(2026, 10, 5)))

    def test_penalty_never_pushes_a_due_date_later(self):
        log = ["- 2026-10-01 p learned", "- 2026-10-01 x learned", "- 2026-10-02 p solid", "- 2026-10-04 p miss"]
        self.assertEqual(schedule(PAIR, log)["x"].due, date(2026, 10, 2))

    def test_no_penalty_when_dependent_had_its_own_graded_event(self):
        x = schedule(PAIR, self.BASE + ["- 2026-10-07 p miss", "- 2026-10-07 x solid"])["x"]
        # Early solid: max(8, rhu(2 * 2.5)) = 8, due 10-15.
        self.assertEqual((x.interval, x.due), (8, date(2026, 10, 15)))

    def test_penalty_reaches_direct_dependents_only(self):
        kps = ["- a: A.", "- b: B. (builds on: a)", "- c: C. (builds on: b)"]
        log = [f"- 2026-10-01 {k} learned" for k in "abc"]
        log += [f"- 2026-10-02 {k} solid" for k in "abc"] + [f"- 2026-10-05 {k} solid" for k in "abc"]
        states = schedule(kps, log + ["- 2026-10-07 a miss"])
        self.assertEqual(states["b"].due, date(2026, 10, 8))
        self.assertEqual(states["c"].due, date(2026, 10, 13))

    def test_penalty_wins_over_credit_on_the_same_day(self):
        kps = ["- p: P.", "- m: M. (builds on: p)", "- x: X. (builds on: m)"]
        base = [f"- 2026-10-01 {k} learned" for k in "pmx"] + ["- 2026-10-02 p solid", "- 2026-10-02 m solid"]
        m = schedule(kps, base + ["- 2026-10-06 p miss", "- 2026-10-06 x solid"])["m"]
        self.assertEqual((m.implicit_credits, m.interval, m.due), (0, 3, date(2026, 10, 5)))
        without_miss = schedule(kps, base + ["- 2026-10-06 x solid"])["m"]
        self.assertEqual(without_miss.implicit_credits, 1)


class CommandTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "ledger.md"

    def test_init_creates_skeleton_and_refuses_to_overwrite(self):
        self.assertEqual(run_cli("init", self.path)[0], 0)
        self.assertEqual(self.path.read_text(encoding="utf-8"), ledger.SKELETON)
        self.path.write_text("keep me", encoding="utf-8")
        code, _, err = run_cli("init", self.path)
        self.assertEqual(code, 2)
        self.assertIn("already exists", err)
        self.assertEqual(self.path.read_text(encoding="utf-8"), "keep me")

    def test_add_creates_topics_and_appends_within_a_topic_block(self):
        run_cli("init", self.path)
        steps = [
            ("tensors", "tensor-rank", "Rank is the number of indices.", "--title", "PyTorch tensors"),
            ("tensors", "tensor-shape", "Shape lists sizes.", "--builds-on", "tensor-rank"),
            ("embeddings", "embedding-lookup", "Lookup maps ids to rows.", "--builds-on", "tensor-shape,tensor-rank"),
            ("tensors", "broadcasting", "Broadcasting aligns shapes from the right.", "--builds-on", "tensor-shape", "--title", "ignored"),
        ]
        for step in steps:
            code, _, err = run_cli("add", self.path, *step)
            self.assertEqual(code, 0, err)
        self.assertEqual(self.path.read_text(encoding="utf-8"), """# Learning ledger

<!-- teach-me ledger v1. Change it with scripts/ledger.py so the format stays parseable. -->

## Knowledge points

### tensors — PyTorch tensors
- tensor-rank: Rank is the number of indices.
- tensor-shape: Shape lists sizes. (builds on: tensor-rank)
- broadcasting: Broadcasting aligns shapes from the right. (builds on: tensor-shape)

### embeddings
- embedding-lookup: Lookup maps ids to rows. (builds on: tensor-shape, tensor-rank)

## Log
""")

    def test_add_rejects_duplicate_and_unknown_ids_without_writing(self):
        self.path.write_text(SPEC_EXAMPLE, encoding="utf-8")
        before = self.path.read_bytes()
        code, _, err = run_cli("add", self.path, "other", "tensor-rank", "Again.")
        self.assertEqual(code, 1)
        self.assertIn("'tensor-rank' already exists on line 8", err)
        code, _, err = run_cli("add", self.path, "tensors", "new-kp", "New.", "--builds-on", "nope")
        self.assertEqual(code, 1)
        self.assertIn("unknown knowledge point 'nope'", err)
        self.assertEqual(self.path.read_bytes(), before)

    def test_log_appends_entries_and_prints_status_for_the_log_date(self):
        run_cli("init", self.path)
        run_cli("add", self.path, "tensors", "tensor-rank", "Rank.")
        code, out, err = run_cli("log", self.path, "tensor-rank learned", "--date", "2026-10-14")
        self.assertEqual(code, 0, err)
        code, out, err = run_cli("log", self.path, "tensor-rank solid", "tensor-rank miss — off by one", "--date", "2026-10-15")
        self.assertEqual(code, 0, err)
        text = self.path.read_text(encoding="utf-8")
        self.assertTrue(text.endswith(
            "## Log\n\n"
            "- 2026-10-14 tensor-rank learned\n"
            "- 2026-10-15 tensor-rank solid\n"
            "- 2026-10-15 tensor-rank miss — off by one\n"
        ))
        self.assertTrue(out.startswith("Ledger: 1 knowledge point in 1 topic. Today: 2026-10-15.\n"))
        self.assertIn("  tensor-rank [tensors] missed 2026-10-15 — off by one\n", out)

    def test_log_with_one_bad_entry_leaves_file_unchanged(self):
        self.path.write_text(SPEC_EXAMPLE, encoding="utf-8")
        before = self.path.read_bytes()
        code, out, err = run_cli("log", self.path, "tensor-rank solid", "tensor-shape aced", "--date", "2026-10-15")
        self.assertEqual(code, 1)
        self.assertIn("entry 2 'tensor-shape aced': bad result 'aced'", err)
        self.assertEqual(out, "")
        self.assertEqual(self.path.read_bytes(), before)

    def test_status_prints_expected_sections(self):
        self.path.write_text(STATUS_FIXTURE, encoding="utf-8")
        code, out, err = run_cli("status", self.path, "--today", "2026-10-09")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, EXPECTED_STATUS)

    def test_status_accepts_date_as_alias_for_today(self):
        self.path.write_text(STATUS_FIXTURE, encoding="utf-8")
        code, out, err = run_cli("status", self.path, "--date", "2026-10-09")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, EXPECTED_STATUS)

    def test_status_all_adds_one_row_per_kp(self):
        self.path.write_text(STATUS_FIXTURE, encoding="utf-8")
        code, out, _ = run_cli("status", self.path, "--today", "2026-10-09", "--all")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith(EXPECTED_STATUS + "\nAll knowledge points:\n"))
        rows = [" ".join(line.split()) for line in out.split("All knowledge points:\n")[1].splitlines()]
        self.assertEqual(rows, [
            "id topic state interval ease last due lapses",
            "tensor-rank tensors fragile 5d 2.50 solid 2026-10-10 0",
            "tensor-shape tensors fragile 1d 2.35 shaky 2026-10-03 0",
            "broadcasting tensors open gap 1d 2.30 miss 2026-10-05 1",
            "embedding-lookup embeddings fragile 1d 2.50 learned 2026-10-06 0",
            "position-ids embeddings not learned - 2.50 - - 0",
        ])

    def test_status_on_empty_ledger(self):
        run_cli("init", self.path)
        code, out, _ = run_cli("status", self.path, "--today", "2026-10-14")
        self.assertEqual((code, out), (0, "Ledger: 0 knowledge points in 0 topics. Today: 2026-10-14.\nRetention (reviews after the learning day): none yet.\n"))

    def test_status_reports_validation_errors_with_exit_1(self):
        self.path.write_text(SPEC_EXAMPLE.replace("tensor-rank learned", "tensor-rank aced"), encoding="utf-8")
        code, _, err = run_cli("status", self.path)
        self.assertEqual(code, 1)
        self.assertIn("error: line 13: bad result 'aced'", err)

    def test_script_exit_codes(self):
        self.path.write_text(SPEC_EXAMPLE, encoding="utf-8")
        cases = [
            (["status", self.path, "--today", "2026-10-15"], 0),
            (["status", self.path, "--today", "10/15/2026"], 2),
            (["status", self.path.with_name("missing.md")], 2),
            (["frobnicate"], 2),
            (["log", self.path, "nope solid"], 1),
        ]
        for argv, expected in cases:
            with self.subTest(argv=argv):
                result = subprocess.run([sys.executable, SCRIPT, *map(str, argv)], capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
