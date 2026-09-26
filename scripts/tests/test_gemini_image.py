"""Drive the gemini-image-generator wrapper against a fake agy binary; the real agy never runs."""

import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib

SCRIPT = Path(__file__).resolve().parents[2] / "skills/gemini-image-generator/scripts/generate.sh"

# Records argv NUL-separated, because the prompt is a multi-line argument.
FAKE = """#!/bin/sh
printf '%s\\0' "$@" > "$0.argv"
pwd > "$0.cwd"
if [ -f "$0.stderr" ]; then cat "$0.stderr" >&2; fi
if [ -f "$0.dest" ]; then
  dest="$ANTIGRAVITY_CLI_HOME/$(cat "$0.dest")"
  mkdir -p "$(dirname "$dest")"
  cp "$0.image" "$dest"
fi
cat "$0.json"
exit "$(cat "$0.exit" 2>/dev/null || echo 0)"
"""

# A JFIF header is enough for `file` to report JPEG image data.
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
REPLY = "Reply with only the absolute path of the saved image file."


def png_bytes():
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) + chunk(b"IEND", b""))


def agy_result(conversation="conv-1", **extra):
    return {"conversation_id": conversation, "status": "SUCCESS", "response": "/brain/path.jpg",
            "duration_seconds": 15.8, "num_turns": 1, **extra}


class GeminiImageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)
        self.bin = self.dir / "bin"
        self.bin.mkdir()
        jq = shutil.which("jq")
        if not Path("/usr/bin/jq").exists() and jq:
            (self.bin / "jq").symlink_to(jq)
        self.home = self.dir / "antigravity"
        self.agy = self.bin / "agy"

    def fake(self, payload, dest=None, image=JPEG, exit_code=0, stderr=None):
        self.agy.write_text(FAKE)
        self.agy.chmod(0o755)
        Path(f"{self.agy}.json").write_text(json.dumps(payload) + "\n")
        Path(f"{self.agy}.image").write_bytes(image)
        Path(f"{self.agy}.exit").write_text(str(exit_code))
        if dest:
            Path(f"{self.agy}.dest").write_text(dest)
        if stderr:
            Path(f"{self.agy}.stderr").write_text(stderr)

    def argv(self):
        path = Path(f"{self.agy}.argv")
        return path.read_bytes().decode().split("\0")[:-1] if path.exists() else None

    def run_wrapper(self, *args):
        return subprocess.run(
            [str(SCRIPT), *args], cwd=self.dir, capture_output=True, text=True, timeout=10,
            env={"PATH": f"{self.bin}:/usr/bin:/bin", "HOME": str(self.dir), "TMPDIR": str(self.dir),
                 "ANTIGRAVITY_CLI_HOME": str(self.home)})

    def reference(self, name):
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(png_bytes())
        return path

    def assertPair(self, argv, flag, value):
        self.assertIn([flag, value], [argv[i:i + 2] for i in range(len(argv) - 1)])

    def assertUsageError(self, *args):
        result = self.run_wrapper("--prompt", "a teapot", *args)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIsNone(self.argv())
        return result

    def test_success_copies_image_and_prints_two_lines(self):
        self.fake(agy_result(), dest="brain/conv-1/hero_123.jpg")
        out = self.dir / "assets/hero.jpg"
        result = self.run_wrapper("--prompt", "a teapot", "--output", "assets/hero.jpg")
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 2, result.stdout)
        self.assertEqual(Path(lines[0]).resolve(), out.resolve())
        self.assertEqual(out.read_bytes(), JPEG)
        self.assertTrue(lines[1].startswith("JPEG image data"), lines[1])
        self.assertIn(f", {len(JPEG)} bytes, ", lines[1])
        self.assertTrue(lines[1].endswith(", driver gemini-3.8-flash-low, conversation conv-1"), lines[1])
        argv = self.argv()
        self.assertPair(argv, "--model", "gemini-3.8-flash-low")
        self.assertPair(argv, "--output-format", "json")
        self.assertPair(argv, "--print-timeout", "240s")
        self.assertNotIn("--dangerously-skip-permissions", argv)
        cwd = Path(f"{self.agy}.cwd").read_text().strip()
        self.assertEqual(Path(cwd).resolve(), out.parent.resolve())

    def test_prompt_names_tool_aspect_image_name_and_references(self):
        self.fake(agy_result(), dest="brain/conv-1/launch_hero_banner_123.jpg")
        first, second = self.reference("ref1.png"), self.reference("refs/ref2.png")
        result = self.run_wrapper("--prompt", "Keep the teapot; make it cobalt blue.",
                                   "--output", "out/Launch Hero-Banner v2.jpg", "--aspect", "16:9",
                                   "--reference", "ref1.png", "--reference", str(second),
                                   "--model", "gemini-3.1-pro-low", "--timeout", "90")
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = self.argv()
        self.assertPair(argv, "--model", "gemini-3.1-pro-low")
        self.assertPair(argv, "--print-timeout", "90s")
        prompt = argv[argv.index("-p") + 1]
        self.assertIn("Use your generate_image tool (never run_command or any shell)", prompt)
        self.assertIn("AspectRatio 16:9", prompt)
        self.assertIn("ImageName launch_hero_banner", prompt)
        paths = json.loads(prompt.split("ImagePaths ", 1)[1].split(" to generate:", 1)[0])
        self.assertTrue(all(Path(path).is_absolute() for path in paths), paths)
        self.assertEqual([Path(path).resolve() for path in paths], [first.resolve(), second.resolve()])
        self.assertIn("to generate: Keep the teapot; make it cobalt blue.", prompt)
        self.assertTrue(prompt.endswith(REPLY), prompt)

    def test_bad_aspect_exits_2(self):
        self.fake(agy_result())
        result = self.assertUsageError("--output", "out.jpg", "--aspect", "21:9")
        self.assertIn("--aspect", result.stderr)

    def test_bad_output_extension_exits_2(self):
        self.fake(agy_result())
        self.assertUsageError("--output", "out.webp")

    def test_missing_reference_exits_2(self):
        self.fake(agy_result())
        result = self.assertUsageError("--output", "out.jpg", "--reference", "missing.png")
        self.assertIn("missing.png", result.stderr)

    def test_fourth_reference_exits_2(self):
        self.fake(agy_result())
        refs = [arg for i in range(4) for arg in ("--reference", str(self.reference(f"r{i}.png")))]
        result = self.assertUsageError("--output", "out.jpg", *refs)
        self.assertIn("at most 3", result.stderr)

    def test_existing_output_is_not_overwritten(self):
        self.fake(agy_result(), dest="brain/conv-1/hero_123.jpg")
        out = self.dir / "hero.jpg"
        out.write_bytes(b"keep")
        result = self.assertUsageError("--output", "hero.jpg")
        self.assertEqual(out.read_bytes(), b"keep")
        self.assertIn("hero-v2.jpg", result.stderr)

    def test_missing_agy_exits_3(self):
        result = self.run_wrapper("--prompt", "a teapot", "--output", "out.jpg")
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("agy", result.stderr)

    def test_agy_failure_exits_4(self):
        self.fake(agy_result(), exit_code=1, stderr="model not found\n")
        result = self.run_wrapper("--prompt", "a teapot", "--output", "out.jpg")
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn("model not found", result.stderr)
        self.assertFalse((self.dir / "out.jpg").exists())

    def test_no_image_in_brain_exits_5(self):
        self.fake(agy_result())
        result = self.run_wrapper("--prompt", "a teapot", "--output", "out.jpg")
        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertIn("brain/conv-1", result.stderr)
        self.assertFalse((self.dir / "out.jpg").exists())

    def test_denied_actions_warn_on_stderr(self):
        denied = [{"action": "command", "display_name": "RunCommand"}]
        self.fake(agy_result(response="", denied_actions=denied),
                  stderr='jetski: no output produced - a tool required the "command" permission\n')
        result = self.run_wrapper("--prompt", "a teapot", "--output", "out.jpg")
        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertIn("warning: agy denied RunCommand (command)", result.stderr)

    @unittest.skipUnless(shutil.which("sips"), "sips converts formats only on macOS")
    def test_png_output_converts_jpeg_source(self):
        png = self.reference("source.png")
        jpeg = self.dir / "source.jpg"
        subprocess.run(["sips", "-s", "format", "jpeg", str(png), "--out", str(jpeg)],
                       check=True, capture_output=True)
        self.fake(agy_result(), dest="brain/conv-1/cutout_123.jpg", image=jpeg.read_bytes())
        result = self.run_wrapper("--prompt", "a teapot", "--output", "cutout.png")
        self.assertEqual(result.returncode, 0, result.stderr)
        line = result.stdout.splitlines()[1]
        self.assertTrue(line.startswith("PNG image data"), line)
        self.assertTrue(line.endswith(", converted from JPEG source"), line)
        self.assertEqual((self.dir / "cutout.png").read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
