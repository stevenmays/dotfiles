---
name: fix-merge-conflict
description: Resolve an active Git merge or rebase conflict and validate the combined behavior when conflict resolution is requested.
---

# Resolve merge conflicts

Inspect Git status and determine whether a merge, rebase, cherry-pick, or ordinary working-tree edit is in progress. Identify unmerged paths through Git's index, then inspect their conflict markers and surrounding implementation. Text containing marker-like examples alone is not an unresolved Git conflict.

Understand both sides using the index stages, relevant commits, and surrounding callers. During a rebase, do not assume that `ours` means the user's topic branch. Preserve compatible intent from both sides. If a binary conflict or mutually exclusive behavior needs a user decision, explain the alternatives and continue independent resolutions.

Resolve source and configuration before regenerating tracked outputs with the project's own tools. Reconcile the dependency manifest before regenerating its lockfile. Preserve required configuration; do not blindly union incompatible settings or discard generated files because they are generated.

Run the checks that exercise the combined behavior and complete required project validation. Verify that resolved files contain no unintended markers and that the index has no remaining unmerged entries. Report pre-existing failures separately.

Stage only resolved paths. Preserve unrelated staged and unstaged work. Do not use `git add -A` as a shortcut. Complete the local Git operation when that is included in the request, using the appropriate continuation command; otherwise leave the resolutions ready and state the operation still pending. Do not create a generic merge commit during a rebase.

Do not push, force-push, reset, abort the operation, or delete unrelated files as a side effect. Finish with resolution decisions, validation results, and the resulting Git state.
