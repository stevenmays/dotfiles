"""Drive external-run.sh against fake codex and cursor-agent binaries; no real engine runs."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "skills/external-subagents/scripts/external-run.sh"

# Records argv NUL-separated, because the cursor prompt is a multi-line positional argument.
FAKE = """#!/bin/sh
if [ "$1" = models ]; then cat "$0.models"; exit 0; fi
printf '%s\\0' "$@" > "$0.argv"
cat > /dev/null
cat "$0.jsonl"
"""

MODELS = """Available models

auto - Auto
grok-4.7-high-fast - Grok 4.7 High Fast
grok-4.7-low - Grok 4.7 Low
grok-4.7-medium - Grok 4.7 Medium
grok-4.7-high - Grok 4.7 High (default)
grok-4.7-xhigh - Grok 4.7 Extra High
grok-4.7-medium-fast - Grok 4.7 Medium Fast
cursor-grok-4.6-high - Cursor Grok 4.6 High
grok-4.5-high - Grok 4.5 High
grok-code-fast-1 - Grok Code Fast
gpt-5.6 - GPT-5.6
sonnet-5 - Sonnet 5
"""

CODEX_EVENTS = [
    {"type": "item.completed", "item": {"type": "agent_message", "text": "codex findings"}},
]


def cursor_events(is_error=False):
    call = {"readToolCall": {"args": {"path": "file.txt"}}}
    return [
        {"type": "system", "subtype": "init", "model": "Grok 4.7 Medium"},
        {"type": "assistant", "message": {"role": "assistant",
                                          "content": [{"type": "text", "text": "Reading the file."}]}},
        {"type": "tool_call", "subtype": "started", "call_id": "c1", "tool_call": call},
        {"type": "tool_call", "subtype": "completed", "call_id": "c1", "tool_call": call},
        {"type": "result", "subtype": "success", "is_error": is_error,
         "result": "cursor findings", "duration_ms": 1234},
    ]


class ExternalRunTests(unittest.TestCase):
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

    def fake(self, name, events, models=MODELS):
        path = self.bin / name
        path.write_text(FAKE)
        path.chmod(0o755)
        Path(f"{path}.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))
        Path(f"{path}.models").write_text(models)

    def argv(self, name):
        path = self.bin / f"{name}.argv"
        return path.read_bytes().decode().split("\0")[:-1] if path.exists() else None

    def run_wrapper(self, *args, env=None):
        return subprocess.run(
            [str(SCRIPT), "--prompt", str(self.prompt), "--out", str(self.out), "--cd", str(self.dir), *args],
            env={"PATH": f"{self.bin}:/usr/bin:/bin", **(env or {})}, capture_output=True, text=True, timeout=10)

    def resolved_model(self, models, *args):
        self.fake("cursor-agent", cursor_events(), models=models)
        result = self.run_wrapper(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = self.argv("cursor-agent")
        return argv[argv.index("--model") + 1]

    def assertPair(self, argv, flag, value):
        self.assertIn([flag, value], [argv[i:i + 2] for i in range(len(argv) - 1)])

    def test_auto_prefers_codex_when_both_exist(self):
        self.fake("codex", CODEX_EVENTS)
        self.fake("cursor-agent", cursor_events())
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNotNone(self.argv("codex"))
        self.assertIsNone(self.argv("cursor-agent"))

    def test_auto_falls_back_to_cursor(self):
        self.fake("cursor-agent", cursor_events())
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNotNone(self.argv("cursor-agent"))

    def test_no_engine_exits_2(self):
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 2)
        self.assertIn("no external engine", result.stderr)

    def test_cursor_resolves_medium_effort_and_salvages_result(self):
        self.fake("cursor-agent", cursor_events())
        result = self.run_wrapper("--engine", "cursor")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertPair(self.argv("cursor-agent"), "--model", "grok-4.7-medium")
        text = self.out.read_text()
        self.assertTrue(text.startswith("# Cursor run — complete"), text)
        self.assertIn("Engine: cursor · Model: grok-4.7-medium · effort medium", text)
        self.assertIn("cursor findings", text)
        self.assertNotIn("Reading the file.", text)

    def test_cursor_read_only_argv(self):
        self.fake("cursor-agent", cursor_events())
        self.assertEqual(self.run_wrapper().returncode, 0)
        argv = self.argv("cursor-agent")
        self.assertPair(argv, "--mode", "ask")
        self.assertPair(argv, "--output-format", "stream-json")
        self.assertPair(argv, "--sandbox", "enabled")
        self.assertPair(argv, "--workspace", str(self.dir))
        self.assertIn("--trust", argv)
        for flag in ("--force", "--approve-mcps", "--browser"):
            self.assertNotIn(flag, argv)
        self.assertEqual(argv[-1], "Review this.\nSecond line.")

    def test_cursor_workspace_write_argv(self):
        self.fake("cursor-agent", cursor_events())
        self.assertEqual(self.run_wrapper("--sandbox", "workspace-write").returncode, 0)
        argv = self.argv("cursor-agent")
        self.assertIn("--force", argv)
        self.assertNotIn("--mode", argv)

    def test_cursor_effort_selects_slug_suffix(self):
        self.assertEqual(self.resolved_model(MODELS, "--effort", "xhigh"), "grok-4.7-xhigh")

    def test_cursor_falls_back_to_base_slug(self):
        self.assertEqual(self.resolved_model("grok-4.7 - Grok 4.7\ngrok-4.5-high - Grok 4.5 High\n"), "grok-4.7")

    def test_cursor_prefers_grok_prefix_over_cursor_grok(self):
        models = "cursor-grok-4.7-medium - Cursor Grok 4.7\ngrok-4.7-medium - Grok 4.7 Medium\n"
        self.assertEqual(self.resolved_model(models), "grok-4.7-medium")

    def test_cursor_pinned_model_records_effort_na(self):
        self.fake("cursor-agent", cursor_events())
        result = self.run_wrapper("--effort", "xhigh", env={"CURSOR_SUBAGENT_MODEL": "grok-4.5-high"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertPair(self.argv("cursor-agent"), "--model", "grok-4.5-high")
        self.assertIn("Engine: cursor · Model: grok-4.5-high · effort n/a", self.out.read_text())

    def test_cursor_rejects_non_grok_models(self):
        self.fake("cursor-agent", cursor_events())
        for model in ("sonnet-4", "gpt-5"):
            with self.subTest(model=model):
                result = self.run_wrapper("--model", model)
                self.assertEqual(result.returncode, 2)
                self.assertIsNone(self.argv("cursor-agent"))

    def test_cursor_without_usable_grok_exits_2(self):
        lists = {
            "unnumbered": "auto - Auto\ngrok-code-fast-1 - Grok Code Fast\ngpt-5.6 - GPT-5.6\nsonnet-5 - Sonnet 5\n",
            "fast only": "grok-4.7-high-fast - Grok 4.7 High Fast\ngrok-4.7-medium-fast - Grok 4.7 Medium Fast\n",
        }
        for name, models in lists.items():
            with self.subTest(name):
                self.fake("cursor-agent", cursor_events(), models=models)
                result = self.run_wrapper()
                self.assertEqual(result.returncode, 2)
                self.assertIn("cursor-agent login", result.stderr)
                self.assertIn("CURSOR_SUBAGENT_MODEL", result.stderr)
                self.assertIsNone(self.argv("cursor-agent"))

    def test_codex_pins_default_model_and_effort(self):
        self.fake("codex", CODEX_EVENTS)
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = self.argv("codex")
        self.assertPair(argv, "-m", "gpt-6-astra")
        self.assertPair(argv, "-c", 'model_reasoning_effort="medium"')
        text = self.out.read_text()
        self.assertTrue(text.startswith("# Codex run — complete"), text)
        self.assertIn("Engine: codex · Model: gpt-6-astra · effort medium", text)

    def test_cursor_result_error_exits_126(self):
        self.fake("cursor-agent", cursor_events(is_error=True))
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 126)
        self.assertIn("FAILED", self.out.read_text())


if __name__ == "__main__":
    unittest.main()
