---
name: onboard-repo
description: Bootstrap repository guidance for Codex by creating or improving AGENTS.md when onboarding is requested.
---

# Onboard a repository

Create concise repository instructions based on observed project facts. Inspect manifests, CI, existing guidance, and enough implementation to identify the stack, useful commands, boundaries, and non-obvious constraints.

Write or update the repository's `AGENTS.md`. Preserve existing user-authored guidance and resolve conflicts using the applicable instruction hierarchy. Include only facts that change how an agent works: verified commands, important ownership boundaries, conventions, and actual gotchas. Link detailed docs with conditions for reading them instead of requiring a full documentation tour before every edit.

Check command names against manifests and CI. Distinguish a command whose definition was verified from one you actually ran. Do not invent a test command or run deployment scripts to verify their names.

Use a tracked root `AGENTS.md` by default, without staging or committing it. If the user requested local-only guidance, use the appropriate local exclusion mechanism and report it. Do not overwrite existing instruction files or change repository visibility policies silently.

Record which local checks use disposable fixtures when the repository establishes that fact. Do not assert that tests are safe merely because they are called tests.

Permissions are configured by the host. If permission setup is requested, inspect the installed Codex CLI and current official documentation, then prepare narrow rules for review. Never translate another agent's permission schema into Codex config by guesswork or grant broad command access as a side effect of onboarding.

Finish with the guidance file, the commands verified or run, and any missing project facts. Creating the requested guidance is the deliverable; installing personal global settings or publishing changes requires a separate request.
