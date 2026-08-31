---
name: deslop
description: Clean up AI slop in existing code — measure complexity with real tools, delete dead and redundant code, refactor the worst hotspots first, and prove behavior is unchanged. Use when the user asks to clean up slop, deslop, reduce complexity, untangle spaghetti, simplify a god function, or make AI-generated code maintainable. Not a review skill — extreme-code-quality-review covers review; this one changes the code.
---

# Deslop

AI-generated code often works but branches like a jungle and hoards code nobody asked for. This skill measures the mess, deletes what shouldn't exist, and restructures what should.

## Scope

- Asked to deslop a branch, PR, or "what I just wrote": target only code this branch introduced — `git diff main...HEAD` (or the repo's default branch). Leave pre-existing slop alone unless asked.
- Asked to deslop files, a directory, or "the codebase": target those files whole.

## Measure first

Run a complexity tool on every target file before touching anything. Prefer, in order:

- Python: `radon cc -s -a <path>`
- JS/TS: eslint `complexity` rule
- Go: `gocyclo`
- Any language: `lizard <path>` (`pip install lizard` into a venv if missing)
- No tool possible: count manually — CC = decision points + 1 (`if`, `case`, loops, `catch`, ternary, `&&`, `||`).

The project's own linter threshold wins if one is configured. Otherwise use these soft defaults — they inform judgment, they don't replace it:

| Signal | Fine | Refactor when touching | Fix now |
|--------|------|------------------------|---------|
| CC per function | ≤ 10 | 11–15 | > 15 |
| Nesting depth | ≤ 2 | 3 | ≥ 4 |
| Lines per file | ≤ 500 | 500–1000 | > 1000 |

Rank all functions by CC descending. Report the hotspot table with numbers **before** editing anything.

## The slop checklist

Hunt these in every target file. Each is a deletion or merge, not a rewrite:

- **Dead code**: unused functions, unreachable branches, commented-out blocks, unused imports/params. Delete.
- **Redundant code**: near-duplicate helpers, copy-pasted blocks, a bespoke helper where the codebase has a canonical one. Merge into one.
- **Speculative abstraction**: interface with one implementation, factory for one product, config for a value that never changes, wrapper that only forwards. Inline it.
- **`any` / `unknown` / bare casts**: replace with the real type. `unknown` survives only at a true trust boundary, immediately narrowed.
- **Comment noise**: comments that restate the code, narrate the diff, or don't match the file's existing comment density. Delete; keep only why/invariant/warning comments.
- **Abnormal defensiveness**: try/catch, null checks, or fallbacks on paths the codebase already trusts or validates upstream. Delete; a guard belongs at the trust boundary, once.
- **Style drift**: naming, idiom, or structure inconsistent with the rest of the file. Match the file.

## Delete before you restructure

Before refactoring a function, climb this ladder and stop at the first rung that holds:

1. Does this code need to exist at all? Speculative = delete, say so in one line.
2. Does an existing helper, stdlib call, or platform feature already do it? Replace the code with the call.
3. Only then: restructure.

## Refactor tactics, in order of preference

1. **Guard clauses** — invert conditions, return early, kill nesting.
2. **Extract function** — the name says *what*, not *how*; a name that needs "and" means split again.
3. **Lookup table / map** instead of if-else or switch chains.
4. **Named predicates** — `isEligibleForRefund(order)` beats four-clause boolean soup.
5. **Polymorphism / strategy** for switch-on-type, only when the same switch appears in 2+ places.
6. **Flatten loops** — extract the body, `continue` instead of nested if.

Do not game the metric. A dense one-liner hiding six branches is worse than the if-chain it replaced. Complexity moves into well-named units; it doesn't vanish into cleverness.

## Hard rules

- **Preserve behavior.** Run the tests before and after every function you touch.
- **No tests? Add one first.** Write a minimal characterization test file for the current behavior of each hotspot before refactoring it, and refactor conservatively. The test file is a deliverable — leave it in the project; a throwaway verification script you delete afterward does not count. Complex and untested is the highest-risk quadrant — never make it complex, untested, *and* freshly rewritten.
- **Exported symbols**: before deleting or changing an exported/public signature, grep for consumers. None found → delete it and flag the export change in the report. Consumers exist, or you can't tell → keep the export and ask. Never stall the rest of the cleanup on this question — finish everything internal either way.
- One responsibility per function. Small functions with clear names beat few functions with section comments.

## Workflow

1. Measure all target files; rank functions by CC descending.
2. Report the hotspot table before touching anything.
3. Sweep the slop checklist — deletions first; they often dissolve hotspots for free.
4. Refactor the worst remaining hotspot. One function at a time. Test after each.
5. Re-measure. Repeat until targets hold or remaining hotspots are justified.

## Output format

End with:

```
## Deslop report
| Function | CC before | CC after |
|----------|-----------|----------|
| parseOrder | 18 | 4 |

Deleted: 120 lines (dead: retryLegacy, duplicate: formatDate2)
Extracted: validateHeader, resolveDiscount
Types fixed: 3 `any` → typed
Behavior verified: <test command and result>
```

Keep prose minimal. Numbers and diffs do the talking.
