"""Run every backticked `git diff` command in the review instructions against fixture repos."""

import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

# An agent runs these commands verbatim, so the strings in these files are the code under test.
SCOPE_FILES = [
    "skills/adversarial-review/SKILL.md",
    "skills/adversarial-review/references/code-review.md",
    "commands/pre-review.md",
    "commands/extreme-code-quality-review.md",
    "agents/extreme-code-quality-review.md",
]
# The brief receives `{MERGE_BASE}` already filled in, so it names no `git merge-base` command.
NO_MERGE_BASE_COMMAND = {"skills/adversarial-review/references/code-review.md"}

IDENTITY = ["-c", "user.name=Review Scope Test", "-c", "user.email=review-scope@example.com"]


class ReviewScopeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name) / "repo"
        self.repo.mkdir()
        # A minimal env keeps the developer's git config, hooks, and any inherited GIT_DIR out of the fixture.
        self.env = {"PATH": os.environ["PATH"], "HOME": temp.name,
                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q", "-b", "master")
        self.commit("a.txt")
        self.git("switch", "-q", "-c", "feat")

    def run_git(self, argv):
        return subprocess.run(argv, cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=10)

    def git(self, *args):
        result = self.run_git(["git", *IDENTITY, *args])
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def commit(self, name):
        (self.repo / name).write_text(f"{name}\n")
        self.git("add", name)
        self.git("commit", "-q", "-m", name)

    def commit_upstream(self):
        self.git("switch", "-q", "master")
        self.commit("c.txt")
        self.git("switch", "-q", "feat")

    def edit(self):
        (self.repo / "a.txt").write_text("a.txt edited\n")

    def fill(self, span, merge_base):
        command = (span.replace("<merge-base>", merge_base).replace("{MERGE_BASE}", merge_base)
                   .replace("<base>", "master").replace("{BASE}", "master"))
        self.assertNotRegex(command, r"[<{]", "unfilled placeholder")
        return command

    def assertScope(self, expected):
        merge_base = self.git("merge-base", "master", "HEAD").strip()
        for rel in SCOPE_FILES:
            text = (ROOT / rel).read_text()
            merge_base_spans = re.findall(r"`(git merge-base[^`]*)`", text)
            spans = re.findall(r"`(git diff[^`]*)`", text)
            with self.subTest(file=rel):
                self.assertTrue(spans, "no backticked git diff command")
                if rel not in NO_MERGE_BASE_COMMAND:
                    self.assertTrue(merge_base_spans, "no backticked git merge-base command")
            for span in merge_base_spans:
                with self.subTest(file=rel, command=span):
                    result = self.run_git(shlex.split(self.fill(span, merge_base)))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), merge_base)
            for span in spans:
                with self.subTest(file=rel, command=span):
                    command = self.fill(span, merge_base)
                    result = self.run_git(shlex.split(command))
                    if "--quiet" in command:
                        self.assertEqual(result.returncode, 1 if expected else 0, result.stderr)
                        continue
                    self.assertEqual(result.returncode, 0, result.stderr)
                    if "--name-only" in command:
                        paths = set(result.stdout.split())
                    else:
                        paths = set(re.findall(r"^diff --git a/\S+ b/(\S+)$", result.stdout, re.M))
                    self.assertEqual(paths, expected)

    def test_unstaged_edit(self):
        self.edit()
        self.assertScope({"a.txt"})

    def test_staged_edit(self):
        self.edit()
        self.git("add", "a.txt")
        self.assertScope({"a.txt"})

    def test_commit_upstream_commit_and_uncommitted_edit(self):
        self.commit("b.txt")
        self.commit_upstream()
        self.edit()
        self.assertScope({"a.txt", "b.txt"})

    def test_branch_commit(self):
        self.commit("b.txt")
        self.assertScope({"b.txt"})

    def test_upstream_commit_only(self):
        self.commit_upstream()
        self.assertScope(set())


if __name__ == "__main__":
    unittest.main()
