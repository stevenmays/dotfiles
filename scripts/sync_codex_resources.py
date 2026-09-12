#!/usr/bin/env python3
"""Copy explicitly shared resources into the self-contained Codex package."""

import argparse
import json
from pathlib import Path
import shutil


def sync(root, check=False):
    package = root / "codex"
    resources = json.loads((package / "shared-resources.json").read_text())
    for target_name, source_name in resources.items():
        target = (package / target_name).resolve()
        source = (root / source_name).resolve()
        if not target.is_relative_to(package.resolve()) or not source.is_relative_to(root.resolve()):
            raise ValueError(f"Resource escapes its root: {target_name}")
        if target.name == "SKILL.md":
            raise ValueError("Skill entrypoints are maintained separately, not synchronized")
        if check:
            if not target.is_file() or source.read_bytes() != target.read_bytes():
                raise ValueError(f"Stale shared resource: {target_name}; run make sync-codex")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sync(Path(__file__).resolve().parents[1], check=args.check)
    print("Codex shared resources are current")
