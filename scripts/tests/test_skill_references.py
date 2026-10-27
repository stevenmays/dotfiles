"""Check that agents and commands reach skill files in a way Claude Code can resolve."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


def markdown(*dirs):
    return [path for name in dirs for path in sorted((ROOT / name).rglob("*.md"))]


class SkillReferenceTests(unittest.TestCase):
    def test_hidden_skills_are_not_loaded_through_the_skill_tool(self):
        # `disable-model-invocation: true` hides a skill from the Skill tool, which then resolves the name to a
        # same-named command or to nothing. Read such a skill by its `${CLAUDE_PLUGIN_ROOT}` path instead.
        hidden = [path.parent.name for path in sorted((ROOT / "skills").glob("*/SKILL.md"))
                  if re.search(r"^disable-model-invocation: true$", path.read_text().split("\n---", 1)[0], re.M)]
        for path in markdown("agents", "commands"):
            for number, line in enumerate(path.read_text().splitlines(), 1):
                for name in hidden:
                    with self.subTest(file=str(path.relative_to(ROOT)), line=number, skill=name):
                        self.assertFalse("`Skill`" in line and f"`{name}`" in line, line)

    def test_plugin_root_paths_exist(self):
        for path in markdown("agents", "commands", "skills"):
            for rel in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`\"']+)", path.read_text()):
                with self.subTest(file=str(path.relative_to(ROOT)), path=rel):
                    self.assertTrue((ROOT / rel).exists())


if __name__ == "__main__":
    unittest.main()
