---
name: ste-writing
description: Simplified Technical English (ASD-STE100) adapted for software engineering, plus economy rules that curtail verbose drafts. Use whenever writing or rewriting technical prose for other people — documentation, READMEs, runbooks, code comments, PR descriptions, PR review comments, commit messages, release notes, incident updates, Slack messages, status reports — and whenever explaining anything technical, even if the user doesn't name a format. Also use when asked to simplify, shorten, condense, tighten, clarify, or "plain English" existing technical text. Not for essays or blog posts — writing-style covers those.
---

# Simplified Technical English for Software

ASD-STE100 is the controlled language aerospace has used since the 1980s so that maintenance instructions cannot be misread. It has two parts: a small set of writing rules, and a dictionary where every word has exactly one meaning. This skill keeps the rules, swaps the aerospace dictionary for software conventions, and adds economy rules for the failure STE never faced: too many sentences.

The audiences match. Engineering text is read by on-call responders at 3 a.m., non-native English speakers, new hires without context, and people skimming Slack on a phone. Write for the least-rested, lowest-context reader — everyone else benefits too.

## The contract

Every rule below serves two goals: a reader who parses a sentence once arrives at exactly one meaning, and never reads a sentence they do not need.

- One word has one meaning.
- One sentence carries one idea — or one instruction.
- One paragraph covers one topic.
- Every sentence is necessary — delete any sentence and the reader loses a fact or an action.

## Economy rules

The rules in the rest of this skill govern how to write a sentence. These rules govern which sentences exist. Compress by deleting sentences and ideas, never by deleting words inside a sentence you keep.

**Answer first, within a budget.** Decide the reader's question and answer it in 1–3 sentences or at most 5 bullets. The budget is a default, not a cap — exceed it only when the extra sentences change what the reader does. Context the reader will not act on gets deleted, not summarized.

**Collapse each paragraph to its consequence.** Most explanatory paragraphs are one fact plus restatements of it. Write the fact once, fused with its effect: "The cache key ignores the lockfile, so deploys reuse stale builds." Two paragraphs in, one sentence out.

**Cut detail from the bottom.** Order detail as effect, then cause, then mechanism. Mechanism survives only when the reader will act on it.

**No scaffolding.** Delete preamble ("This PR introduces…"), recaps, "note that", "importantly", and narration of your own structure. The first sentence carries content.

Before — a typical first draft:

> This PR makes some improvements to how we handle configuration loading. Previously, the configuration was loaded eagerly at startup, which meant that any error in an unused section would prevent the application from starting entirely. This was problematic because teams often have partial configurations in development environments.
>
> To address this, the loading logic has been refactored to be lazy. Each section is now parsed only when it is first accessed, so errors surface at the point of use rather than at startup. Additionally, error messages now include the file and line of the failing section.

After:

> - Config sections now parse on first access, not at startup, so an error in an unused section no longer blocks boot.
> - Parse errors now name the file and line.

The dev-environment motivation dropped out because it changes nothing the reader does. Every actionable fact survived — the fact list is the guard, not the word count.

## Down-level by one

Write for one level of expertise below the actual audience. A PR read by senior engineers is written so that QA or a new hire without context can follow it. This is not audience matching — it is a compression mechanism. To drop a level you must first collapse the concept into simpler terms, and that collapse is where complexity dies.

Boundaries:

- Facts stay exact. Technical names, numbers, and versions never get dumbed down.
- The text still names the real mechanism, in plainer terms. No parables.

At-level: "Memoize the selector to avoid re-renders caused by referential inequality in the subscription."

One level down: "The selector returns a new object on every call, so React thinks the data changed and re-renders. Memoizing returns the same object when nothing changed."

The test: a reader one ring outside the context — QA for a PR, support for a runbook, a new hire for a design doc — can act on the text without a follow-up question.

## Word rules

**Pick one name per concept and never vary it.** Elegant variation is for fiction. If the doc calls it "the worker", that process is never later "the daemon", "the service", or "the consumer" — a new name makes the reader ask whether you mean a new thing. When two names are entrenched, pick one and state the alias once: "the ingest worker (deployed as `queue-consumer`)".

**Technical names are exact and literal.** Commands, flags, paths, error strings, API names, and config keys go in backticks with exact spelling and casing, never paraphrased. Readers grep for them. Write "the `ECONNRESET` error", not "a connection reset issue".

**Expand an uncommon acronym at first use.** "Time to first byte (TTFB)", then TTFB alone. Acronyms every reader knows — API, CPU, URL — need no expansion.

**Replace bloated words with plain ones.** The high-frequency offenders:

| Avoid | Write |
|---|---|
| utilize, leverage | use |
| in order to | to |
| prior to | before |
| ensure | make sure |
| perform/execute an X | the verb itself: validate, query, test |
| functionality | feature, behavior |
| in the event that | if |
| due to the fact that | because |
| currently | now, or delete |
| please note that | delete, or "Note:" |

The full table — plus smothered verbs, vague quantities, and software words with two meanings — is in `references/word-substitutions.md`. Read it whenever you rewrite existing text or draft anything longer than a few paragraphs.

**Requirement words carry contract weight.** "Must" is a requirement; "must not" is a prohibition; "can" is ability or permission; "might" is possibility. "Should" is the ambiguous one — the reader cannot tell requirement from suggestion. Replace it with "must" or "we recommend".

**Verb and noun spellings differ.** You log in through the login page. Back up the database to make a backup; roll back the deploy with a rollback. Full pair list in the reference file.

**Quantify.** "Several times" → "3 times". "Recently" → "since v2.31". "Much faster" → "p95 fell from 480 ms to 120 ms". If you lack the number, say what you know: "faster in our tests; not yet measured".

**Delete intensifiers and difficulty words.** "Very", "really", and "quite" add no information. "Simply", "just", and "easily" insult the reader the moment the step fails for them.

## Sentence rules

**Length limits: 20 words for an instruction, 25 for everything else.** This is a defect detector, not a style preference — a sentence over the limit almost always carries two ideas. Split it; don't compress it into telegraphic fragments.

**One instruction per sentence.** "Run the migration and restart the workers after checking that the queue is empty" hides three actions and leaves the order ambiguous. Write:

1. Make sure the queue is empty.
2. Run the migration.
3. Restart the workers.

**Active voice with a named actor.** Passive voice hides the actor, and in software the actor is the component you will debug. "The job will be retried" — by whom? Write "The scheduler retries the job 3 times, then moves it to the dead-letter queue." Passive is acceptable only when the actor is genuinely irrelevant, which is rare.

**Speak to the reader as "you"; write instructions as bare commands.** "Run the migration" — not "the migration should be run", "please run", or "the user should run". "Please" pads without informing. Reserve "the user" for the people who use the reader's software.

**Present tense for behavior; simple tenses for everything.** Software behavior is not a future event: "the API returns 403", not "the API will return 403". Save the future for real future events. Perfect and progressive tenses blur time: "has been deprecated" hides the date — "was deprecated in v3.2" demands one; "is being rolled out" → "the rollout started Monday and finishes Friday".

**Keep the small words.** Telegraphic style ("Update config before restart") saves you two words and costs every reader a parse: is "restart" a noun or a command? Write "Update the config file before you restart the service." Articles are load-bearing, especially for non-native speakers. Commit subjects are exempt — the 50-character target wins there.

**No more than three nouns in a row.** "The webhook retry queue consumer lag alert" makes the reader reverse-engineer the grammar. Unstack with prepositions: "the alert for consumer lag on the webhook retry queue". An established proper name may stay clustered — format it as a technical name.

**Condition before instruction.** Readers execute as they read. "Restart the worker if lag exceeds 1,000" risks a restart before the condition is read. Write "If lag exceeds 1,000, restart the worker."

## Paragraph rules

- At most 6 sentences per paragraph, one topic, and the first sentence states the topic.
- More than about 3 parallel items in a sentence? Use a vertical list.
- List items use parallel grammar and carry one idea each.

## Mechanics

- Headings use sentence case. A task heading starts with a verb: "Configure the worker", not "Worker configuration".
- Link text names its destination: "see the retry policy", never "click here" or "this doc".
- Use the serial comma — "the scheduler, the worker, and the queue" — so the last two items cannot read as one.
- No idioms or cultural references. "Out of the box", "grandfathered in", and sports metaphors fail for translated and non-native readers. Say the literal thing.

## Warnings

State the consequence before the reader can act on the command — never after it, never in a trailing parenthesis.

Bad:

> Run `terraform destroy` to tear down the stack (note: this also deletes the database).

Good:

> **Warning:** The next command permanently deletes the database, including its backups. There is no undo.
>
> Run `terraform destroy` to tear down the stack.

## Format guides

### Documentation and runbooks

- Prerequisites first, as a list.
- Numbered steps when order matters; one instruction per step.
- After a consequential step, state the expected result: "Run `make check`. The output ends with `plugin OK`."
- Conditions and warnings go before the step they govern.

### Commit messages

Git shows the subject line alone almost everywhere — `git log --oneline`, rebase, shortlog, GitHub — truncated if long, stripped of its body. Write the subject to stand alone; write the body for the reader who runs `git show` a year from now.

Subject:

- Shape: `type: imperative summary`, lowercase after the prefix (feat, fix, chore, docs, refactor, test). Target 50 characters; never exceed 72. No trailing period.
- Imperative mood. The test: the summary completes "If applied, this commit will …". "fix retry race in the queue worker" passes; "fixed" and "fixes" fail.
- Summarize the effect or the why, not the mechanics — the diff already shows the mechanics.

Body:

- Separate it from the subject with one blank line. Tools misparse the message without it.
- Explain what changed and why, never how. The body carries what the diff cannot: the problem, why this approach, side effects.
- Wrap lines at 72 characters — `git log` indents but never wraps.
- Bullets are fine. A change whose subject says everything needs no body.

### PR descriptions

Keep the house shape — a 1–3 bullet summary plus a test plan — and write it in STE:

- Each bullet states one change and its why, in at most 20 words, active voice.
- Test plan steps are commands a reviewer can run, each with its expected result.

Example bullet: "Retry token refresh once on 401, so clock skew no longer logs the user out."

### Code comments

The default is no comment. Code already says what it does; a comment earns its place only by carrying a fact the code cannot.

- One line is the default — a soft limit, not a cap. A comment that runs long explaining *what the code does* is a signal to rename, split, or retype the code instead. A comment that runs long recording a *decision* — the constraint, the trade-off, the alternative that was rejected — is doing its job; keep it.
- Never restate what the reader's eyes just parsed. `if flags.new_checkout:` needs zero lines of comment — the flag name is the comment.
- What earns a line: a non-obvious why ("retry once — the vendor 401s on clock skew"), an invariant the code cannot express ("caller holds the lock"), a warning ("flush before close, or data is lost"), code that looks wrong but isn't, or the URL of the copied snippet, spec, or bug that forced this shape.
- Write for the next reader of the file, never the reviewer of this diff: no "added X", "changed to Y", "per feedback".
- TODO carries an owner or an issue: `TODO(#4821): remove after the flag ships.`
- The deletion test: remove the comment. If the reader loses no fact, it stays removed.

### PR review comments

The author reads this in a queue of twenty, on someone else's schedule. Two sentences: the defect, then the fix. A third exists only when the author cannot act without it — a rule citation, the condition that reproduces the defect, or why the obvious fix is wrong.

- Backtick the exact name, line, or value — the author greps for it.
- Open with the defect. Delete "I noticed that", "It looks like", "Consider that", "Just a thought" — the comment's existence is the flag.
- Never restate the code. The author wrote it and is looking at it.
- State the fix as a bare command: "Await `flush()` before returning", not "you might want to consider awaiting".
- Give the consequence, not the lecture. "so the response returns before the write lands" earns its place; a paragraph on the event loop does not.
- One defect per comment. Two defects on one line are two comments.
- Hedging is a decision, not a tone. If you are unsure, label it `question`; if you are sure, drop "possibly", "perhaps", and "might want to".

Before:

> I noticed that in the `handleUpload` function on line 42, the call to `flushBuffer()` is not being awaited. This is a common issue with async code — since `flushBuffer` returns a Promise, execution continues immediately without waiting for the flush to complete. This could potentially lead to a race condition where the response is sent before the data is fully written, which might cause intermittent data loss that would be hard to debug. It would probably be a good idea to add an `await` here.

After:

> **issue (blocking):** `upload.ts:42` — `flushBuffer()` is not awaited, so the response can return before the write lands and the upload is lost. Add `await`.

Every fact the author acts on survived. The Promise tutorial, the "hard to debug" aside, and the hedges did not.

### Slack messages and status updates

- The first sentence carries the point: the answer, the ask, or the status. Details follow or go in the thread.
- One message, one topic. Two topics are two messages.
- If you need action, name the person and the deadline.
- Status updates follow the shape: done, next, blocked.

Bad: "Hey, so I was looking into the deploy thing from yesterday and there might be some issues with how the pipeline handles caching, happy to go into detail but wanted to flag it."

Good: "Found the deploy bug: the pipeline reuses the old build artifact because the cache key ignores the lockfile. One-line fix — I can ship it today unless anyone objects."

### Explanations

- Define each term before you first use it.
- Introduce one new concept per paragraph.
- Ground the explanation in the reader's concrete world: real file names, real commands, real error text.
- Analogies are welcome; after the analogy, state the literal mechanism.

## What this is not

- **Not a tone flattener.** Greetings, contractions, and humor stay, especially in Slack. STE removes ambiguity, not personality.
- **Not telegraphy.** Brevity comes from fewer sentences, never from dropping articles or actors in a sentence you keep. A kept sentence stays fully formed.
- **Not for voice-driven prose.** Essays and blog posts use the writing-style skill.
- **Not for quoted material.** Code, log output, error messages, and other people's words stay verbatim.

## Rewriting existing text

When asked to simplify or clarify a text:

1. Read `references/word-substitutions.md`.
2. List every technical fact in the original: names, numbers, conditions, caveats.
3. Strike the restatements — most drafts state each fact more than once. Only the fact list survives.
4. Rewrite by the rules above. Expect the result to be shorter: two paragraphs usually collapse to one or two sentences, or a few bullets.
5. Check the rewrite against the fact list. A rewrite that drops a caveat is worse than the bloated original.

## Self-check

Before returning any text, scan for these — each one is countable:

- A sentence over 25 words (20 for an instruction)? Split it.
- A paragraph over 6 sentences? Split it.
- More than 3 nouns in a row? Unstack it.
- Passive voice hiding a debuggable actor? Name the actor.
- Perfect or progressive tense? Use simple past, present, or future — and add the date or version it was hiding.
- "Will" describing what the software does today? Use the present.
- "Please" in an instruction, or "the user" meaning the reader? Write the bare command to "you".
- Link text that does not name its destination? Name it.
- A commit subject over 50 characters, non-imperative, or run into the body with no blank line? Fix it.
- A code comment that restates the code? Delete it, or fix the code it apologizes for. Multi-line is fine only when every line records a decision or constraint.
- A review comment past 2 sentences, opening with a hedge, or quoting the author's code back? Cut to defect, then fix.
- The same thing under two names? Unify them.
- A bare "should"? Decide: "must" or "we recommend".
- A word from the substitution table? Substitute it.
- A condition or warning after its instruction? Move it before.
- A vague quantity where a number exists? Use the number.
- Missing articles? Restore them.
- A sentence whose deletion changes nothing the reader does? Delete it.
- A paragraph that collapses to one sentence or 3 bullets with no fact lost? Collapse it.
- Would a reader one level down (QA, support, a new hire) need a follow-up question? Down-level it.
