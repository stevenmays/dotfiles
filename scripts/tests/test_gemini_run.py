"""Drive gemini-run.sh against a fake agy binary; the real agy never runs."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "skills/gemini-subagents/scripts/gemini-run.sh"

# Records argv NUL-separated, because the prompt is a multi-line argument.
FAKE = """#!/bin/sh
printf '%s\\0' "$@" > "$0.argv"
pwd > "$0.cwd"
cat "$0.jsonl"
cat "$0.err" >&2
sleep "$(cat "$0.sleep")"
exit "$(cat "$0.rc")"
"""

CONVERSATION = "c0ffee00-0000-4000-8000-000000000000"
PARAMETERS = {"AbsolutePath": "/abs/file.txt"}


def step(**fields):
    return {"event": "step_update", "step_update": {"conversation_id": CONVERSATION, **fields}}


def agy_events(model="gemini-3.1-pro-high", response="final answer", status="SUCCESS", denied=()):
    result = {"conversation_id": CONVERSATION, "status": status, "response": response,
              "duration_seconds": 2.56, "num_turns": 1, "usage": {"total_tokens": 42}}
    if denied:
        result["denied_actions"] = [{"action": action, "display_name": action.title()} for action in denied]
    return [
        {"event": "init", "conversation_id": CONVERSATION,
         "init": {"model": model, "cwd": "/repo", "tools": [], "permission_mode": "request-review"}},
        step(step_index=0, state="DONE", step_type="user_input"),
        step(step_index=1, state="ACTIVE", step_type="tool", tool_name="view_file",
             tool_info={"name": "view_file", "parameters": PARAMETERS}),
        step(step_index=1, state="DONE", step_type="tool", tool_name="view_file", duration_seconds=0.69,
             tool_info={"name": "view_file", "parameters": PARAMETERS, "output": "3 lines, 11 bytes"}),
        step(step_index=2, state="ACTIVE", step_type="agent_response", text_delta="streamed fin"),
        step(step_index=2, state="DONE", step_type="agent_response", text_delta="dings\n", duration_seconds=2.5),
        {"event": "result", "result": result},
    ]


class GeminiRunTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)
        self.bin = self.dir / "bin"
        self.bin.mkdir()
        jq = shutil.which("jq")
        if not Path("/usr/bin/jq").exists() and jq:
            (self.bin / "jq").symlink_to(jq)
        self.prompt = self.dir / "prompt.md"
        self.prompt.write_text("Review this.\nSecond line.\n")
        self.out = self.dir / "out.md"

    def fake(self, events, rc=0, stderr="", sleep=0):
        path = self.bin / "agy"
        path.write_text(FAKE)
        path.chmod(0o755)
        Path(f"{path}.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))
        Path(f"{path}.err").write_text(stderr)
        Path(f"{path}.sleep").write_text(str(sleep))
        Path(f"{path}.rc").write_text(str(rc))

    def argv(self):
        path = self.bin / "agy.argv"
        return path.read_bytes().decode().split("\0")[:-1] if path.exists() else None

    def run_wrapper(self, *args, env=None, cwd=None):
        return subprocess.run(
            [str(SCRIPT), "--prompt", str(self.prompt), "--out", str(self.out), "--cd", str(self.dir), *args],
            env={"PATH": f"{self.bin}:/usr/bin:/bin", **(env or {})}, cwd=cwd,
            capture_output=True, text=True, timeout=15)

    def assertPair(self, argv, flag, value):
        self.assertIn([flag, value], [argv[i:i + 2] for i in range(len(argv) - 1)])

    def test_success_writes_header_provenance_and_response(self):
        self.fake(agy_events())
        result = self.run_wrapper("--label", "review")
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = self.out.read_text().splitlines()
        self.assertRegex(lines[0], r"^# Gemini review — complete \(\d+s\)$")
        self.assertEqual(lines[1], "Engine: gemini · Model: gemini-3.1-pro-high · effort high")
        self.assertIn("final answer", lines)
        self.assertNotIn("streamed", self.out.read_text())
        self.assertNotIn("Denied", self.out.read_text())

    def test_read_only_argv(self):
        self.fake(agy_events())
        self.assertEqual(self.run_wrapper().returncode, 0)
        argv = self.argv()
        self.assertPair(argv, "-p", "Review this.\nSecond line.")
        self.assertPair(argv, "--model", "gemini-3.1-pro-high")
        self.assertPair(argv, "--output-format", "stream-json")
        self.assertPair(argv, "--print-timeout", "1800s")
        for flag in ("--mode", "--dangerously-skip-permissions", "--effort"):
            self.assertNotIn(flag, argv)

    def test_workspace_write_adds_accept_edits(self):
        self.fake(agy_events())
        self.assertEqual(self.run_wrapper("--sandbox", "workspace-write").returncode, 0)
        argv = self.argv()
        self.assertPair(argv, "--mode", "accept-edits")
        self.assertNotIn("--dangerously-skip-permissions", argv)

    def test_runs_agy_from_cd_with_relative_paths(self):
        work = self.dir / "work"
        work.mkdir()
        self.fake(agy_events())
        result = self.run_wrapper("--prompt", "prompt.md", "--out", "rel.md", "--cd", "work", cwd=self.dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path((self.bin / "agy.cwd").read_text().strip()).resolve(), work.resolve())
        self.assertPair(self.argv(), "-p", "Review this.\nSecond line.")
        self.assertIn("final answer", (self.dir / "rel.md").read_text())

    def test_model_precedence(self):
        cases = [
            ({}, (), "gemini-3.1-pro-high", "high"),
            ({"GEMINI_SUBAGENT_MODEL": "gemini-3.8-flash-medium"}, (), "gemini-3.8-flash-medium", "medium"),
            ({"GEMINI_SUBAGENT_MODEL": "gemini-3.8-flash-medium"}, ("--model", "gemini-3.8-flash-low"),
             "gemini-3.8-flash-low", "low"),
            ({}, ("--model", "Gemini-Experimental"), "Gemini-Experimental", "model default"),
        ]
        for env, args, model, effort in cases:
            with self.subTest(model=model):
                self.fake(agy_events(model=model))
                result = self.run_wrapper(*args, env=env)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertPair(self.argv(), "--model", model)
                self.assertEqual(self.out.read_text().splitlines()[1],
                                 f"Engine: gemini · Model: {model} · effort {effort}")

    def test_rejects_non_gemini_models(self):
        self.fake(agy_events())
        for model in ("claude-sonnet-4-6", "claude-opus-4-6-thinking", "gpt-oss-120b-medium"):
            with self.subTest(model=model):
                result = self.run_wrapper("--model", model)
                self.assertEqual(result.returncode, 2)
                self.assertIn("Gemini models only", result.stderr)
                self.assertIsNone(self.argv())

    def test_missing_prompt_exits_2(self):
        self.fake(agy_events())
        result = self.run_wrapper("--prompt", str(self.dir / "missing.md"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("prompt file not readable", result.stderr)
        self.assertIsNone(self.argv())

    def test_trailing_flag_exits_2(self):
        self.fake(agy_events())
        result = self.run_wrapper("--label")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--label requires a value", result.stderr)

    def test_no_agy_exits_2(self):
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 2)
        self.assertIn("agy not on PATH", result.stderr)

    def test_nonzero_exit_gives_126_with_stderr(self):
        self.fake(agy_events(), rc=3, stderr="agy: quota exhausted\n")
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 126)
        text = self.out.read_text()
        self.assertIn("— FAILED, exit 3", text.splitlines()[0])
        self.assertIn("## stderr", text)
        self.assertIn("agy: quota exhausted", text)

    def test_result_status_not_success_gives_126(self):
        self.fake(agy_events(status="ERROR"))
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 126)
        self.assertIn("— FAILED, result status ERROR", self.out.read_text().splitlines()[0])

    def test_empty_response_falls_back_to_text_deltas(self):
        self.fake(agy_events(response=""))
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("streamed findings", self.out.read_text().splitlines())

    def test_denied_actions_listed_without_failing(self):
        self.fake(agy_events(response="", denied=("write_file", "command", "command")),
                  stderr='jetski: no output produced — a tool required the "command" permission\n')
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = self.out.read_text().splitlines()
        self.assertIn("complete", lines[0])
        self.assertEqual(lines[2], "Denied in headless mode: command, write_file")

    def test_reported_model_appended_when_it_differs(self):
        self.fake(agy_events(model="gemini-3.1-pro"))
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.out.read_text().splitlines()[1],
                         "Engine: gemini · Model: gemini-3.1-pro-high · effort high"
                         " · agy reported model: gemini-3.1-pro")

    def test_idle_stall_gives_125_and_names_last_tool_call(self):
        self.fake(agy_events()[:4], sleep=8)
        result = self.run_wrapper("--idle", "1")
        self.assertEqual(result.returncode, 125, result.stderr)
        text = self.out.read_text()
        self.assertIn("— PARTIAL: stalled", text.splitlines()[0])
        self.assertIn("Last tool call before the kill: `view_file: /abs/file.txt`", text)

    def test_hard_timeout_gives_124(self):
        self.fake(agy_events()[:4], sleep=8)
        result = self.run_wrapper("--hard", "1", "--idle", "30")
        self.assertEqual(result.returncode, 124, result.stderr)
        self.assertPair(self.argv(), "--print-timeout", "1s")
        self.assertIn("— PARTIAL: hard timeout at 1s", self.out.read_text().splitlines()[0])


if __name__ == "__main__":
    unittest.main()
