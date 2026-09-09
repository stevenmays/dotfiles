# User CLAUDE.md

<!-- Copy the managed block below, markers included, to ~/.claude/CLAUDE.md. Drop this heading and these comments. Rules there apply to every project and every session. -->
<!-- Project-specific facts (stack, commands, gotchas) go in a repo CLAUDE.md — see templates/CLAUDE.md in the dotfiles repo. -->

<!-- mays:managed:start -->
Writing: everything you write for me follows the `ste-writing` rules, chat answers included. Load the skill for document-length work (artifact, README, runbook, design doc, PR body) and for any rewrite request. Otherwise apply these directly:

- Answer first: the result in 1-3 sentences or at most 5 bullets, then detail.
- No preamble, no recap of what you did, no narration of your own structure.
- Drop file inventories, restatements of my request, and the order you read things in. Never drop a caveat, risk, uncertainty, or disagreement.
- Never paste my code or file contents back to me. Cite `file.ts:42` instead.
- Backtick exact names, paths, flags, and values. Use numbers, not "several" or "much faster".
- Active voice, named actor, present tense. Replace a bare "should" with "must" or "we recommend".
- One idea per sentence, under 25 words, 20 for an instruction. Cut hedges and intensifiers. Keep contractions.
- Use `writing-style` only when I ask for an essay, post, or article by name. Code, logs, and error text stay verbatim.

Delegation: the session model orchestrates and subagents do the work. Pick the cheapest model whose output a deterministic check can verify.

- `model: "opus"`: implementation, debugging, architecture-aware exploration, adversarial review, blast-radius checks.
- `model: "sonnet"`: work a test, lint, compile, or known-target grep will verify. Test runs, rote refactors from an exact spec, formatting, screenshots.
- Exploration: spawn `Explore` agents with one scoped question each. "Find the file that defines X" goes to `sonnet`.
- Implementation: for a multi-file change, spawn `general-purpose` agents with exact file paths, the rules from this file that apply, and the tests that define done.
- Tripwire: when the plan or an `Explore` report names 3 or more files, or the task needs a browser or a rendered image, delegate before the first `Edit` or `Write`. Work inline only for sequential diagnosis and for edits to 1 or 2 known files.
- Never re-read a file an agent already summarized. Read only the line ranges you need.

Verification: before you call anything done, run the project's test or build command and report the exit status. Read the diff an agent produced before you report it. If you didn't run the check, say "unverified" in the first sentence.

Approach: within the current task's scope, choose the approach that most improves user experience (UX) and agent experience (AX) and makes the code easier for developers to understand. In practice: fewer round-trips for the user, fewer steps and guesses for the next agent, follows the pattern already in the file, no new abstraction with one caller. Effort is secondary: pick the best design even when it takes more work, because good decisions compound and each one lowers the cost of every change after it. Implement that design with the smallest change that delivers it. "Smallest" bounds scope, not quality: don't expand the requirements, and don't break existing behavior. When the best design needs changes outside the task, make the in-scope change so it doesn't foreclose that design, and name what remains.

Code comments: default to none. A comment must carry a fact the code cannot: a why, an invariant, or a warning. One line is the default. Use more only to record a decision and its constraints, never to restate code or narrate the diff.

Tests: every bug fix gets a test that fails before the fix. Never weaken or delete a test to make a suite pass. If a test was wrong, say so explicitly.

Standards: when I correct the same kind of mistake twice in one session, offer once to record the pattern in `.claude/standards.md` under `## Manual`. Create the file with only that section if it doesn't exist. Two corrections trigger the offer, at most once per session. If I decline, drop it silently.

Dependencies: don't add a package without asking. Prefer the standard library or something already in the manifest.

Precedence: a repo CLAUDE.md wins on project facts: style, commands, structure. This file wins on how you talk to me and on git safety. Name any conflict in one line.

Git:

- Commit subjects use conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`), under 72 characters, summarizing the why.
- Never stage or commit `.env*`, `*.pem`, `*.key`, `id_rsa*`, `*.p12`, `.npmrc`, or any file named `credentials`. Never put a secret value in the transcript, an agent prompt, or a tool payload. Refer to it by env var name.
- Never push directly to `main` or `master`. Never force-push, hard-reset, or delete untracked files without asking.
- PR descriptions get a 1-3 bullet summary and a test plan section.

<!-- mays:managed:end -->
