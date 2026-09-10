---
description: Day-one bootstrap for a new codebase — CLAUDE.md and a permissions allowlist in one run
---

# Onboard Repo

Set up a repo you've just joined so every future session starts fully informed: a real CLAUDE.md and a permission allowlist matched to the toolchain. Run once from the repo root.

## Steps

1. **Survey the repo** (read-only):
   - Stack and tooling from manifests: package.json, pyproject.toml, go.mod, Cargo.toml, Gemfile, Makefile, CI config.
   - Build, test, lint, and typecheck commands that actually exist — verify each against scripts/targets; never invent commands.
   - Directory layout (top two levels) and the purpose of each major directory.
   - README and docs for the project's purpose.
   For large repos, dispatch `Explore` subagents with `model: "sonnet"` rather than reading everything into the main context.
2. **Write CLAUDE.md** from the survey. If one already exists, don't overwrite it — report the gaps against this structure and offer to fill them:

   ```markdown
   # Project Guidelines

   ## Project Overview
   - **Name** / **Purpose** / **Stack**

   ## Commands
   (verified commands only, each with a one-line comment)

   ## Directory Structure
   (real tree, annotated)

   ## Conventions
   (only what a reviewer would flag)

   ## Gotchas
   (non-obvious constraints found in docs, CI, or code — required env vars, ordering requirements, things that fail silently)
   ```
3. **Permissions allowlist**: propose a `permissions.allow` list derived from the toolchain found in step 1 — read-only git, the verified build/test/lint commands, the package manager's run and install. Show the list before writing anything.
4. **Ask about visibility** (AskUserQuestion) before writing the files:
   - **Shared**: CLAUDE.md committed for the team; permissions go in `.claude/settings.json`.
   - **Local-only**: add CLAUDE.md and `.claude/` to `.git/info/exclude` (personal ignore, invisible to the repo's .gitignore) so the tooling leaves no footprint in the shared repo; permissions go in `.claude/settings.local.json`.
5. **Report**: what was created and the next step — write code, then `/ship`.
