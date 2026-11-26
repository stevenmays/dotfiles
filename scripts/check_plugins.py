#!/usr/bin/env python3
"""Check the Claude plugin's structure and that every skill folder installs on its own."""

import json
from pathlib import Path
import re
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_object(path):
    value = json.loads(path.read_text())
    require(isinstance(value, dict), f"Expected a JSON object: {path}")
    return value


def check(root):
    claude = read_object(root / ".claude-plugin/plugin.json")
    claude_market = read_object(root / ".claude-plugin/marketplace.json")
    require(any(p["name"] == claude["name"] and p["source"] == "./"
                for p in claude_market["plugins"]), "Claude marketplace must target the root package")
    for name in ("commands", "agents", "skills"):
        require((root / name).is_dir(), f"Missing Claude directory: {name}")
    read_object(root / "hooks/hooks.json")

    # `npx skills add` discovers a skill by its frontmatter `name` and `description`.
    names = set()
    for skill in sorted(path for path in (root / "skills").iterdir() if path.is_dir()):
        path = skill / "SKILL.md"
        frontmatter = re.match(r"\A---\nname: ([a-z0-9-]+)\ndescription: \S[^\n]*\n", path.read_text())
        require(frontmatter is not None, f"Use name and a single-line description in {path}")
        require(frontmatter.group(1) == skill.name, f"Skill name does not match its folder: {skill.name}")
        names.add(skill.name)
    return names


if __name__ == "__main__":
    try:
        names = check(Path(__file__).resolve().parents[1])
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Plugin check failed: {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Plugin structure valid; {len(names)} skills")
