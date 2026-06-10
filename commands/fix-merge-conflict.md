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
git status --porcelain | cat
```

Collect files with:
- U statuses (unmerged)
- Conflict markers: `<<<<<<<` / `=======` / `>>>>>>>`

### 2. Resolve Conflicts Per File

Open each conflicting file and remove conflict markers. Merge both sides logically when feasible.

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

### 3. Validate

**Node/TypeScript/JS:**
- Install deps if manifests changed (allow lockfile updates)
- Run lint, typecheck, build, tests if available

**Other ecosystems (Python, Go, etc.):**
- Run standard build/tests when available

### 4. Finalize

```bash
git add -A
git commit -m "chore: resolve merge conflicts"
```

Output summary of files touched and notable resolution choices.

## Resolution Guidelines

- If ambiguous and blocks build/tests, prefer the variant that compiles and green-tests
- If file still contains conflict markers after first pass, revisit before proceeding
- For large refactors: keep consistent imports, types, and module boundaries
- Use exhaustive switch guards in TypeScript
- Keep edits minimal; avoid reformatting unrelated code

## Deliverables

- Clean working tree with all conflicts resolved
- Successful build/tests where applicable
- One local commit containing the resolutions
