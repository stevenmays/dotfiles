---
description: Day-one bootstrap for a new codebase — CLAUDE.md and a permissions allowlist in one run
---

# Onboard Repo

Set up a repo you've just joined so every future session starts fully informed: a real CLAUDE.md and a permission allowlist matched to the toolchain. Run once from the repo root.

## Steps

1. **Survey the repo** (read-only):
   - Stack and tooling from manifests: package.json, pyproject.toml, go.mod, Cargo.toml, Gemfile, Makefile, CI config.
   - Build, test, lint, and typecheck commands that actually exist — verify each against scripts/targets; never invent commands.
   - Directory layout (top two levels). Use it to understand the code and find risk zones. Never copy the tree into CLAUDE.md, because it goes stale.
   - README and docs for the project's purpose, domain rules, deliberate trade-offs, and constraints from outside the repo, such as partner APIs or compliance.
   - Risk-zone candidates: paths owned in `CODEOWNERS` (root, `.github/`, or `docs/`; skip a catch-all `*` entry), directories named for high-stakes work such as `auth`, `billing`, or `migrations`, and paths with a CI job of their own, such as a migration check or a deploy step. A `paths:` filter that only scopes the main build doesn't count. Mark a candidate red when a mistake there loses data, money, or access, or can't be reverted. Mark it yellow otherwise. Record each candidate's source. When more than 10 candidates qualify, keep the first 10, ranked red before yellow, then by the most sources, then by `CODEOWNERS` order. List the rest in the step 5 report.
   For large repos, dispatch `Explore` subagents with `model: "sonnet"` rather than reading everything into the main context.
2. **Write CLAUDE.md** from the survey. Read `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md` and use it as the structure. Replace each `[...]` placeholder and HTML comment with what the survey found. Keep the `## Risk zones` rule paragraph word for word. When step 1 found no risk-zone candidates, keep that heading and paragraph and list no zones. Show each candidate with its level and source before step 4. If CLAUDE.md already exists, don't overwrite it — report the gaps against the template and offer to fill them. When nobody can answer (a headless run), leave the existing file unchanged and list the gaps and proposed risk zones in the step 5 report.
3. **Permissions allowlist**: propose a `permissions.allow` list derived from the toolchain found in step 1 — read-only git, the verified build/test/lint commands, the package manager's run and install. Show the list before writing anything.
4. **Ask before writing** — one AskUserQuestion call with two questions:
   - **Visibility**:
     - **Shared**: CLAUDE.md committed for the team; permissions go in `.claude/settings.json`.
     - **Local-only**: add `/CLAUDE.md` and `/.claude/` to `.git/info/exclude` (personal ignore, invisible to the repo's .gitignore) so the tooling leaves no footprint in the shared repo; permissions go in `.claude/settings.local.json`.
   - **Risk zones**: confirm the candidates as listed, or keep them `proposed`. An answer typed under Other edits the list. Skip this question when step 1 found no candidates.

   When nobody can answer (a headless run), take Local-only for a CLAUDE.md that step 2 created: add `/CLAUDE.md` to `.git/info/exclude`. Add no `.claude/` entry and write no settings file, because step 3 promises a human sees the allowlist first. Mark every risk zone `(proposed)`, such as `- yellow (proposed): …`.
5. **Report**: what was created and the next step — write code, then `/ship`. After a headless run, name the defaults it took: CLAUDE.md Local-only when the run created it, risk zones left `proposed`, and no settings file. Print the proposed allowlist so a human can apply it later. When CLAUDE.md already existed, list its gaps and the proposed risk zones.
