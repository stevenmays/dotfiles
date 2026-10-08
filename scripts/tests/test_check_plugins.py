"""Exercise package isolation and failure reporting with disposable copies."""

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_plugins import check


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[2]
        for name in (".claude-plugin", ".agents", "skills", "hooks", "codex"):
            shutil.copytree(source / name, self.root / name)
        for name in ("commands", "agents"):
            (self.root / name).mkdir()
        self.addCleanup(self.temp.cleanup)

    def test_valid_package(self):
        self.assertEqual(len(check(self.root)), 8)

    def test_missing_manifest_fails(self):
        (self.root / "codex/.codex-plugin/plugin.json").unlink()
        with self.assertRaises(FileNotFoundError):
            check(self.root)

    def test_malformed_manifest_fails(self):
        (self.root / "codex/.codex-plugin/plugin.json").write_text('{"name":')
        with self.assertRaises(json.JSONDecodeError):
            check(self.root)

    def test_root_package_cannot_leak_into_codex(self):
        path = self.root / ".agents/plugins/marketplace.json"
        value = json.loads(path.read_text())
        value["plugins"][0]["source"]["path"] = "."
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "source must be ./codex"):
            check(self.root)

    def test_invalid_interface_fails(self):
        path = self.root / "codex/.codex-plugin/plugin.json"
        value = json.loads(path.read_text())
        value["interface"] = "not an object"
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "interface must be an object"):
            check(self.root)

    def test_duplicate_identity_fails(self):
        skills = self.root / "codex/skills"
        shutil.copytree(skills / "deslop", skills / "deslop-copy")
        with self.assertRaisesRegex(ValueError, "Duplicate or mismatched"):
            check(self.root)

    def test_legacy_commands_fail(self):
        (self.root / "codex/commands").mkdir()
        with self.assertRaisesRegex(ValueError, "Unexpected legacy content"):
            check(self.root)

    def test_stale_shared_resource_fails(self):
        path = self.root / "codex/skills/writing-style/references/examples.md"
        path.write_text("stale copy")
        with self.assertRaisesRegex(ValueError, "Stale shared resource"):
            check(self.root)

    def test_reference_escape_fails(self):
        path = self.root / "codex/skills/deslop/SKILL.md"
        path.write_text(path.read_text() + "\n[Escape](../../../README.md)\n")
        with self.assertRaisesRegex(ValueError, "Missing or escaping"):
            check(self.root)

    def test_external_symlink_fails(self):
        (self.root / "codex/external").symlink_to(self.root / "skills", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink is not portable"):
            check(self.root)


if __name__ == "__main__":
    unittest.main()
