# Project Guidelines

## Project Overview

- **Name**: [Project name]
- **Purpose**: [Brief description]
- **Stack**: [Stack]

## Commands

<!-- Verified commands only: build, test, lint, and typecheck where they exist. Check each one against the manifest, Makefile, or CI config; never invent one. Put them in a bash block, each with a one-line comment. -->

## Facts the code can't show

<!-- Domain rules, deliberate trade-offs that look wrong, and constraints from outside the repo, each with its source. Agents read the directory tree themselves; never copy it here. Operational traps go in Gotchas. -->

## Risk zones

Red: a mistake here loses data, money, or access, or can't be reverted. Yellow: a mistake here breaks other code but reverts cleanly. A change in a red zone never skips review. A zone marked `proposed` has no human confirmation yet and counts as red.

<!-- One line per zone: - red: `<path glob>` — <what a mistake there breaks>, or the same with yellow. Write red (proposed) or yellow (proposed) until a human confirms the zone. -->

## Conventions

<!-- Only conventions a reviewer would flag: naming, error handling, testing expectations. -->

## Gotchas

<!-- Non-obvious constraints found in docs, CI, or code: required env vars, flaky tests, ordering requirements, things that fail silently. -->
