---
description: Resolve all merge conflicts non-interactively, then build and test
---

# Fix Merge Conflicts

Resolve all merge conflicts on the current Git branch non-interactively and make the repo buildable and tested.

## Constraints

- Operate from repository root. If not in a Git repo, stop and report.
- No user input. Choose sensible defaults and explain decisions.
- Prefer minimal, correct changes that preserve both sides' intent.
- Use non-interactive flags for all tools.
- Do not push or tag; only commit locally.

## Process

### 1. Detect Conflicts

```bash
git status --porcelain
```

Collect files with:
- U statuses (unmerged)
- Conflict markers: `<<<<<<<` / `=======` / `>>>>>>>`

### 2. Investigate Intent

"Preserve both sides' intent" requires knowing the intent. Before resolving, look up why each side changed:

```bash
git log --oneline MERGE_HEAD..HEAD -- <file>   # our side's commits touching the file
git log --oneline HEAD..MERGE_HEAD -- <file>   # their side's commits
git log -1 --format=%B <sha>                   # full message for the commits behind the conflicting hunks
```

During a rebase, use `REBASE_HEAD` in place of `MERGE_HEAD`. When a commit message references a PR or issue, fetch its description (`gh pr view` / `gh issue view`) — skip silently if there is no GitHub remote. Two changes that conflict textually often serve compatible intents; knowing both lets you merge them instead of picking a side.

### 3. Resolve Conflicts Per File

Open each conflicting file and remove conflict markers. Merge both sides logically when feasible, guided by the intent found in step 2.

**Resolution priority** (when mutually exclusive):
1. Pick the variant that compiles and passes type checks
2. Preserve existing public APIs and behavior

**Language-aware strategies:**

| File Type | Strategy |
|-----------|----------|
| `package.json` | Merge keys conservatively; run install to regenerate lockfile |
| Lock files (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) | Regenerate via package manager, don't edit manually |
| Generated/build artifacts | Prefer keeping out of VCS; otherwise prefer ours |
| Config files | Preserve union of safe settings; don't delete required fields |
| Text/markdown | Include both unique content; deduplicate headings |
| Binary files | Prefer current branch (ours) |

### 4. Validate

**Node/TypeScript/JS:**
- Install deps if manifests changed (allow lockfile updates)
- Run lint, typecheck, build, tests if available

**Other ecosystems (Python, Go, etc.):**
- Run standard build/tests when available

### 5. Finalize

```bash
git add -A
git commit -m "chore: resolve merge conflicts"
```

Output summary of files touched and notable resolution choices.

## Resolution Guidelines

- If ambiguous and blocks build/tests, prefer the variant that compiles and green-tests
- If file still contains conflict markers after first pass, revisit before proceeding
- For large refactors: keep consistent imports, types, and module boundaries
- Keep edits minimal; avoid reformatting unrelated code
