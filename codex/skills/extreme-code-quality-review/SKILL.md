---
name: extreme-code-quality-review
description: Audit a branch for structural complexity and missed simplifications when an unusually strict maintainability review is requested.
---

# Extreme code quality review

Find changes that preserve behavior while deleting unnecessary concepts, branches, or layers. Review and report; edit only when the request includes fixes.

Establish the requested diff and its base. Read changed implementations and relevant callers far enough to understand ownership and behavior. Include working-tree changes when they are part of the request. Do not assume the default branch is named `main`.

Apply these standards:

- Treat a file crossing 1,000 lines as a presumptive blocker unless its structure justifies the size. Files above 500 lines warrant attention, not automatic splitting.
- Flag scattered special cases, repeated conditions, duplicated helpers, and feature logic leaking into shared layers.
- Prefer deleting a layer or simplifying the state model over moving the same complexity into more files.
- Question wrappers, casts, optional modes, and generic mechanisms when they obscure a concrete invariant. Keep validation at real trust boundaries.
- Identify related updates that can leave partial state, and unnecessary serialization when independent work can safely run together.
- Use existing complexity tools when they add evidence. A changed function above the project's threshold, or complexity 15 without a configured threshold, deserves inspection; the number alone is not a finding.

Base each finding on a demonstrated consequence and a concrete remedy. Distinguish observed regressions from possible improvements. A clean review can have no findings; do not manufacture blockers to satisfy the strict tone.

Return the highest-impact findings first, each with a file and line, the problem, its consequence, and the proposed simplification. State coverage limits and any checks run. Keep comments readable without requiring another writing skill. An advisory verdict is not permission to submit a review or publish comments.

Completion means the requested changes have been assessed and actionable findings delivered. When fixes are authorized, continue through implementation and relevant validation rather than pausing after the report.

Adapted from the repository's original rubric and [Cursor's code-quality review](https://github.com/cursor/plugins/blob/3347cbab5b54136f6fba0994c3a01a56f7fb7fca/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md).
