# Repo Init

Bootstrap qmd memory for the current repo. Idempotent — safe to run multiple times.

## Steps

1. `mkdir -p .claude/notes`
2. Add `.claude/notes/` and `.claude/scratchpad.md` to `.gitignore` (if not already present)
3. `qmd collection add .claude/notes --name {repo-basename}-notes --mask "*.md"`
4. If `.claude/agent_docs/` exists: `qmd collection add .claude/agent_docs --name {repo-basename}-docs --mask "*.md"`
5. `qmd context add .claude/notes "{repo-basename} project notes and decisions"`
6. `qmd update`
7. Report what was created

## Notes

- `{repo-basename}` is the name of the current repo directory (e.g., `mays.co`, `dotfiles`)
- If a collection already exists, `qmd collection add` will report that — this is fine
- Do not commit `.claude/notes/` — it should be gitignored
