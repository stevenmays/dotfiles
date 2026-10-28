"""Check the literal commands and cross-references in the ship and diagnose-bug steps."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]

# Models follow these steps literally, so the text is the code under test.
SHIP = (ROOT / "commands/ship.md").read_text()
DIAGNOSE = (ROOT / "commands/diagnose-bug.md").read_text()


def step(text, n):
    return re.search(rf"^{n}\. (.*?)(?=^\d+\. |^## |\Z)", text, re.M | re.S).group(1)


def bullets(text):
    return re.findall(r"^\s+- (.*)$", text, re.M)


class ShipTests(unittest.TestCase):
    def test_preflight_runs_identity_and_repo_commands(self):
        preflight = step(SHIP, 1)
        for command in [
            "gh api user -q .login",
            "git config user.email",
            "gh repo view --json nameWithOwner,viewerPermission,defaultBranchRef",
        ]:
            with self.subTest(command=command):
                self.assertIn(f"`{command}`", preflight)

    def test_preflight_gates_on_write_permission(self):
        preflight = step(SHIP, 1)
        for value in ["ADMIN", "MAINTAIN", "WRITE"]:
            with self.subTest(permission=value):
                self.assertIn(f"`{value}`", preflight)
        gate = [line for line in bullets(preflight) if "`WRITE`" in line]
        self.assertTrue(gate and all("Stop unless" in line for line in gate),
                        "the permission bullet doesn't stop on a value outside the allowlist")
        for role in ["`READ`", "`TRIAGE`", "`TRIAGE_PLUS`"]:
            with self.subTest(role=role):
                self.assertFalse(any(role in line for line in gate), f"{role} is in the permission gate")
        self.assertTrue(any("fails" in line and "stop" in line for line in bullets(preflight)),
                        "a failed preflight command doesn't stop /ship")
        email = [line for line in bullets(preflight) if "`git config user.email`" in line]
        self.assertTrue(email and all("stop" in line for line in email), "an unset user.email doesn't stop /ship")

    def test_base_defaults_to_the_repo_default_branch(self):
        preflight = step(SHIP, 1)
        self.assertIn("defaultBranchRef.name", preflight)
        self.assertIn("no default branch", preflight, "a repo without a default branch doesn't stop /ship")
        self.assertIsNone(re.search(r"`(main|master)`", preflight), "preflight falls back to a hardcoded base")
        self.assertLess(preflight.index("defaultBranchRef.name"), preflight.index("nothing to ship"),
                        "the base resolves after the check that needs it")

    def test_checkpoint_names_identity_from_preflight(self):
        self.assertIn("commit as `<email>`, push as `<login>` to `<nameWithOwner>`", step(SHIP, 5))
        for placeholder in ["<email>", "<login>", "<nameWithOwner>"]:
            with self.subTest(placeholder=placeholder):
                self.assertIn(f"`{placeholder}`", step(SHIP, 1), "the checkpoint uses a placeholder preflight never sets")

    def test_held_fixes_rerun_the_test_gate(self):
        bullet = re.search(r"^\s+- Fix held findings first: (.*)$", step(SHIP, 5), re.M)
        self.assertTrue(bullet, "the checkpoint doesn't say what Fix held findings first does")
        target = re.search(r"step (\d+)", bullet.group(1))
        self.assertTrue(target, "Fix held findings first names no step to re-run")
        self.assertRegex(step(SHIP, int(target.group(1))), r"^\*\*Gate \d — tests\*\*",
                         "Fix held findings first re-runs a step other than the test gate")
        for phrase in ["commit message", "test plan", "Gates 1 and 2", "checkpoint again", "same question"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, bullet.group(1))

    def test_test_plan_ends_with_unverified_and_merge_danger(self):
        open_pr = step(SHIP, 8)
        for phrase in ["`Unverified:`", "`Merge danger:`", "one-way", "two-way", "blast radius", "rollback", "End the test plan"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, open_pr)


class DiagnoseBugTests(unittest.TestCase):
    def test_captured_output_is_redacted(self):
        loop = step(DIAGNOSE, 1)
        for phrase in ["`<REDACTED>`", "env var", "tokens", "cookies", "auth headers", "passwords", "API keys", "in a test"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, loop)

    def test_lessons_route_by_kind(self):
        report = step(DIAGNOSE, 7)
        for phrase in ["lint rule", "`## Conventions`", "`/extreme-code-quality-review`"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
