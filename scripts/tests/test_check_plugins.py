"""Exercise the plugin checks and their failure reporting with disposable copies."""

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_plugins import check

SOURCE = Path(__file__).resolve().parents[2]


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in (".claude-plugin", "skills", "hooks"):
            shutil.copytree(SOURCE / name, self.root / name)
        for name in ("commands", "agents"):
            (self.root / name).mkdir()
        self.addCleanup(self.temp.cleanup)

    def test_valid_package(self):
        self.assertEqual(check(self.root), {path.parent.name for path in (SOURCE / "skills").glob("*/SKILL.md")})

    def test_missing_manifest_fails(self):
        (self.root / ".claude-plugin/plugin.json").unlink()
        with self.assertRaises(FileNotFoundError):
            check(self.root)

    def test_malformed_manifest_fails(self):
        (self.root / ".claude-plugin/plugin.json").write_text('{"name":')
        with self.assertRaises(json.JSONDecodeError):
            check(self.root)

    def test_marketplace_must_target_the_root(self):
        path = self.root / ".claude-plugin/marketplace.json"
        value = json.loads(path.read_text())
        value["plugins"][0]["source"] = "./elsewhere"
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "must target the root package"):
            check(self.root)

    def test_skill_name_must_match_its_folder(self):
        skills = self.root / "skills"
        shutil.copytree(skills / "deslop", skills / "deslop-copy")
        with self.assertRaisesRegex(ValueError, "does not match its folder"):
            check(self.root)

    def test_skill_without_description_fails(self):
        (self.root / "skills/deslop/SKILL.md").write_text("---\nname: deslop\n---\n")
        with self.assertRaisesRegex(ValueError, "single-line description"):
            check(self.root)

    def test_skill_folder_without_entry_file_fails(self):
        (self.root / "skills/empty").mkdir()
        with self.assertRaises(FileNotFoundError):
            check(self.root)


if __name__ == "__main__":
    unittest.main()
