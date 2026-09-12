#!/usr/bin/env python3
"""Check this repository's plugin boundaries and packaged resources."""

import json
from pathlib import Path
import re
import sys

from sync_codex_resources import sync


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

    market = read_object(root / ".agents/plugins/marketplace.json")
    entries = market["plugins"]
    require(len({p["name"] for p in entries}) == len(entries), "Duplicate marketplace plugin names")
    entry = next(p for p in entries if p["name"] == "mays")
    require(entry["source"] == {"source": "local", "path": "./codex"}, "Codex source must be ./codex")
    require(entry["policy"]["installation"] in {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"},
            "Invalid installation policy")
    require(entry["policy"]["authentication"] in {"ON_INSTALL", "ON_USE"}, "Invalid authentication policy")
    require(bool(entry["category"]), "Missing marketplace category")

    package = root / "codex"
    manifest = read_object(package / ".codex-plugin/plugin.json")
    require(manifest["name"] == entry["name"], "Plugin name does not match marketplace")
    require(re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?",
                         manifest["version"]), "Invalid version")
    require(manifest["skills"] == "./skills/", "Unexpected Codex skills path")
    for field in ("description", "author", "interface"):
        require(bool(manifest[field]), f"Missing manifest field: {field}")
    require(isinstance(manifest["description"], str), "Description must be a string")
    for field in ("author", "interface"):
        require(isinstance(manifest[field], dict), f"{field} must be an object")
    require(isinstance(manifest["author"].get("name"), str) and manifest["author"]["name"].strip(),
            "Author name must be a nonempty string")
    for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        value = manifest["interface"].get(field)
        require(isinstance(value, str) and value.strip(), f"Missing interface string: {field}")
    require(not (root / ".codex-plugin/plugin.json").exists(), "Remove the legacy root Codex manifest")
    for name in (".claude-plugin", "commands", "hooks", ".codex-plugin/migrated-command-skills"):
        require(not (package / name).exists(), f"Unexpected legacy content in Codex package: {name}")
    for path in package.rglob("*"):
        require(not path.is_symlink(), f"Packaged symlink is not portable: {path}")

    names = set()
    for skill in sorted((package / "skills").iterdir()):
        require(skill.is_dir(), f"Unexpected entry in skills/: {skill}")
        path = skill / "SKILL.md"
        text = path.read_text()
        frontmatter = re.match(r"\A---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n", text)
        require(frontmatter is not None, f"Use name and a single-line description in {path}")
        name, description = frontmatter.groups()
        require(name == skill.name and name not in names, f"Duplicate or mismatched skill name: {name}")
        require(len(name) <= 64 and not name.startswith("source-command-"), f"Invalid skill name: {name}")
        require(len(description) <= 300, f"Description too broad or long: {name}")
        require(name not in {"ste-writing", "gemini-image-generator"}, f"Disabled skill packaged: {name}")
        require(not re.search(r"ste-writing|claude -p|AskUserQuestion|CLAUDE_CODE_SUBAGENT_MODEL", text),
                f"Legacy runtime instruction: {name}")
        names.add(name)

    for path in (package / "skills").rglob("*.md"):
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if re.match(r"[a-z]+://|#", link):
                continue
            target = (path.parent / link.split("#")[0]).resolve()
            require(target.is_relative_to(package.resolve()) and target.is_file(),
                    f"Missing or escaping resource in {path}: {link}")
    require(len(names) == 8, f"Expected eight Codex skills, found {len(names)}")
    sync(root, check=True)
    return names


if __name__ == "__main__":
    try:
        names = check(Path(__file__).resolve().parents[1])
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        print(f"Plugin check failed: {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Plugin boundaries and resources valid; {len(names)} Codex skills")
