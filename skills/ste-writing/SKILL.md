---
name: ste-writing
description: Google developer documentation style fused with Simplified Technical English (ASD-STE100) discipline, adapted for software engineering, plus economy rules that curtail verbose drafts. Use whenever writing or rewriting technical prose for any reader — including the user you are answering right now. Covers documentation, READMEs, runbooks, code comments, PR descriptions, PR review comments, commit messages, tickets and bug reports, release notes, incident updates, Slack messages, status reports, chat answers, reports, plans, and artifacts — and any technical explanation, even when the user doesn't name a format. Also use when asked to simplify, shorten, condense, tighten, clarify, or "plain English" existing technical text. Not for essays or blog posts — writing-style covers those.
---

# Technical writing for software

The base of this skill is the Google developer documentation style guide — the house rules Google's writers use so documentation survives skimming, translation, screen readers, and time. On top of it sit two survivals from ASD-STE100, the aerospace controlled language: one word has one meaning, and one sentence carries one idea. And on top of both sit economy rules for the failure neither guide fights hard enough: too many sentences.

The audiences match. Engineering text is read by on-call responders at 3 a.m., non-native English speakers, new hires without context, and people skimming Slack on a phone. Write for the least-rested, lowest-context reader — everyone else benefits too.

The reader is a human, never an AI. An AI ingests an exhaustive dump at no cost; a human pays for every sentence and abandons text that wastes them. A draft that reads like context for a model — complete, thorough, self-contained — has failed a human reader.

## The contract

Every rule below serves two goals: a reader who parses a sentence once arrives at exactly one meaning, and never reads a sentence they do not need.

- One word has one meaning.
- One sentence carries one idea — or one instruction.
- One paragraph covers one topic, and its first sentence carries the point.
- Every sentence is necessary — delete any sentence and the reader loses a fact or an action.
- The artifact fits its budget (see Format guides). Over budget is a defect, the same as an ambiguous sentence.

## Economy rules

The rules in the rest of this skill govern how to write a sentence. These rules govern which sentences exist. Compress by deleting sentences and ideas, never by deleting words inside a sentence you keep.

**Answer first, within a budget.** Decide the reader's question and answer it in 1–3 sentences or at most 5 bullets. Context the reader will not act on gets deleted, not summarized.

**List facts before words.** For any artifact with a budget, list the facts the reader acts on, then write each one once. Do not draft long and trim — the long draft anchors you, and the trim always spares too much.

**Collapse each paragraph to its consequence.** Most explanatory paragraphs are one fact plus restatements of it. Write the fact once, fused with its effect: "The cache key ignores the lockfile, so deploys reuse stale builds." Two paragraphs in, one sentence out.

**Cut detail from the bottom.** Order detail as effect, then cause, then mechanism. Mechanism survives only when the reader will act on it.

**Record what the reader must know, not what you did to learn it.** The investigation is not the artifact. Your verification runs, ruled-out hypotheses, and measurements belong in a PR comment or a thread — never in the ticket the fixer reads. Ship the conclusion and the facts the reader acts on; the journey stays in your notes.

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

## Voice and tone

**Conversational, not frivolous.** The target register sits between "Dude, this API is awesome!" and "The API documented herein may enable acquisition of data pertaining to user preferences." Write: "This API lets you collect data about what your users like."

**Speak to the reader as "you"; write instructions as bare commands.** "Run the migration" — not "the migration should be run", "please run", "let's run", or "the user should run". "Please" belongs only where you ask a real favor. Reserve "the user" for the people who use the reader's software. "We" is legitimate only with a concrete antecedent — the team or the org: "we recommend", "we deploy on Tuesdays".

**Use contractions — especially negative ones.** Skimming readers miss a standalone "not"; nobody misses "don't". Write "don't", "isn't", "can't". Never invent contractions ("the config's broken" meaning is).

**Software is not a person.** It doesn't want, think, know, see, or complain — it requires, processes, detects, reports. "The scheduler detects the stale lock", not "the scheduler notices the lock is stale". Anthropomorphism reads as precision to you and as ambiguity to a translator and a debugger.

**No exclamation points, no humor in docs.** Humor and idiom die in translation and in the middle of an incident. Slack keeps your personality; documentation keeps only your meaning.

## Word rules

**Pick one name per concept and never vary it.** Elegant variation is for fiction. If the doc calls it "the worker", that process is never later "the daemon", "the service", or "the consumer" — a new name makes the reader ask whether you mean a new thing. When two names are entrenched, pick one and state the alias once: "the ingest worker (deployed as `queue-consumer`)".

**Technical names are exact, literal, and never inflected.** Commands, flags, paths, error strings, API names, and config keys go in backticks with exact spelling and casing, never paraphrased — readers grep for them. Write "the `ECONNRESET` error", not "a connection reset issue". And never bend a code item into English grammar: "send a `POST` request", not "`POST` the data"; "`Intent` objects", not "`Intent`s"; "connect over SSH", not "ssh into"; "extract the zip file", not "unzip it".

**Expand an uncommon acronym at first use.** "Time to first byte (TTFB)", then TTFB alone. Acronyms every reader knows — API, CPU, URL — need no expansion. Never "i.e.", "e.g.", or "etc." — write "that is", "for example", and finish or bound the list.

**Replace bloated words with plain ones.** The high-frequency offenders:

| Avoid | Write |
|---|---|
| utilize, leverage | use |
| in order to | to |
| prior to | before |
| allows you to | lets you |
| perform/execute an X | the verb itself: validate, query, test |
| functionality | feature, behavior |
| in the event that | if |
| due to the fact that | because |
| i.e. / e.g. | that is / for example |
| please note that | delete, or "Note:" |

The full tables — plus smothered verbs, vague quantities, spelling decisions, and software words with two meanings — are in `references/word-substitutions.md`. Read it whenever you rewrite existing text or draft anything longer than a few paragraphs.

**Requirement words carry contract weight.** "Must" is a requirement; "must not" is a prohibition; "can" is ability or permission; "might" is possibility. "Should" is the ambiguous one — the reader cannot tell requirement from suggestion; replace it with "must" or "we recommend". "May" belongs only in policy or legal text. Never "shall"; never a hypothetical "would" — say what the software does. "The value should be true" hides the actor: write "Set the value to `true`" or "The server sets the value to `true`".

**Quantify, and own your numbers.** "Several times" → "3 times". "Recently" → "since v2.31". "Much faster" → "p95 fell from 480 ms to 120 ms". "10x" → "10 times". If you lack the number, say what you know: "faster in our tests; not yet measured". A performance or security claim is a promise: "helps prevent replay attacks" survives an incident, "prevents replay attacks" does not. Superlatives — best, fastest, always, never — only when literally true.

**Don't anchor docs to today.** "Currently", "new", "soon", "latest", "does not yet" date a document the day it ships. Name the version or date instead — "since v3.2", not "currently". Time words are fine where time is the subject: release notes, incident updates, status reports.

**Delete intensifiers and difficulty words.** "Very", "really", and "quite" add no information. "Simply", "just", and "easily" insult the reader the moment the step fails for them.

**Use inclusive terms.** Allowlist/denylist, primary/replica, "final check" not "sanity check", "stops responding" not "hangs", singular "they", "person-hours". When the old term is a literal identifier, keep it in code font and out of prose: "the primary branch (named `master` in this repo)". Full table in the reference file.

**Climb the jargon ladder.** For a term of art the reader may not share: write around it; or swap in a plain term; or gloss it once in parentheses; or define it at first use and then use it consistently. Keep jargon the audience genuinely searches for.

## Sentence rules

**Length limits: 20 words for an instruction, 25 for everything else.** This is a defect detector, not a style preference — a sentence over the limit almost always carries two ideas. Split it; don't compress it into telegraphic fragments.

**One instruction per sentence.** "Run the migration and restart the workers after checking that the queue is empty" hides three actions and leaves the order ambiguous. Write:

1. Make sure the queue is empty.
2. Run the migration.
3. Restart the workers.

**Active voice with a named actor.** Passive voice hides the actor, and in software the actor is the component you will debug. "The job will be retried" — by whom? Write "The scheduler retries the job 3 times, then moves it to the dead-letter queue." Passive earns its place in exactly two cases: the actor is genuinely irrelevant ("the database was purged in January"), or naming the actor would blame the reader ("50 conflicts were found in the file", not "you created 50 conflicts").

**Present tense for behavior; simple tenses for everything.** Software behavior is not a future event: "the API returns 403", not "the API will return 403". "Will" is for events genuinely later than the sentence — "add the file to the list; it will be archived on the next backup run" — never for current behavior and never as hypothetical "would". Perfect and progressive tenses blur time: "has been deprecated" hides the date — "was deprecated in v3.2" demands one; "is being rolled out" → "the rollout started Monday and finishes Friday". Conditionals stay present on both sides: "If you send an unsubscribe message, the server removes you."

**Keep the small words.** Telegraphic style ("Update config before restart") saves you two words and costs every reader a parse: is "restart" a noun or a command? Write "Update the config file before you restart the service." Articles are load-bearing, especially for non-native speakers — so are the optional helpers: keep "that" ("confirm that the job finished"), keep "then" after "if", repeat "if" for a second condition. Commit subjects are exempt — the 50-character target wins there.

**Every pronoun has one possible noun.** If "it", "this", or "these" could point at two things, repeat the noun. "This" and "these" never stand alone: "set this value to `true`", not "set this to `true`". Use "that" for restrictive clauses, comma-plus-"which" for asides, and "who" for people.

**"Only" hugs the word it limits.** "Request only one token", not "Only request one token" — the second might mean "don't do anything else".

**State it in the positive.** "You can continue without a path", not "a missing path won't prevent you from continuing". Double negatives and exceptions-to-exceptions make the reader solve logic puzzles.

**No more than three nouns in a row.** "The webhook retry queue consumer lag alert" makes the reader reverse-engineer the grammar. Unstack with prepositions: "the alert for consumer lag on the webhook retry queue". An established proper name may stay clustered — format it as a technical name.

**Condition, context, and goal come before the action.** Readers execute as they read. "If lag exceeds 1,000, restart the worker" — never the reverse. "In the `deploy` directory, run `make plan`" — location first. "To reset the cache, restart the worker" — goal first, so the reader who doesn't want that outcome skips the step. Same shape for references: "For more information, see the retry policy", not "See the retry policy for more information."

## Paragraph rules

- At most 6 sentences per paragraph, one topic, and the first sentence carries the paragraph's most important fact — readers skim first sentences and skip the rest.
- A single-sentence paragraph is fine. Splitting a long paragraph beats compressing its sentences.
- More than about 3 parallel items in a sentence? Use a vertical list.
- List items use parallel grammar and carry one idea each.
- Never bury a load-bearing fact in parentheses — readers skip them.

## Structure

**Headings.** Sentence case, no trailing period. A task heading is a bare imperative: "Configure the worker" — never "Configuring the worker" or "Worker configuration". A concept heading is a noun phrase. Don't skip levels, don't leave a heading with nothing under it, and prefix optional sections with "Optional:".

**Lists.** Introduce every list with a complete sentence ending in a colon. Numbered means order matters; bulleted means it doesn't; term-plus-colon pairs for definitions ("`--dry-run`: prints the plan"). Sentences in items get periods, fragments get nothing — consistently. Say whether the list is complete ("the following three flags") or samples ("flags such as").

**Links.** Link text names its destination — the target's title or a descriptive phrase with the important words first. Never "click here", "this doc", or a bare URL. The standing pattern: "For more information about retries, see Configuring retry policy." Say when a link downloads a file or leaves the doc set.

**No directional language.** "The preceding table", "the following command" — never "above", "below", or "the panel on the left". Layout reflows, screen readers linearize, and translations reorder.

## Mechanics

The rules that come up in every artifact:

- Use the serial comma — "the scheduler, the worker, and the queue" — so the last two items cannot read as one.
- Em dash with no spaces for a break; never an en dash — use a hyphen or "to" for ranges.
- Straight quotes; punctuation inside them, except after a literal string or keyword (better: backticks, no quotes).
- No "and/or" and no slash alternatives: "A, B, or both" — slashes live in paths and code.
- Spell out zero through nine; numerals for 10+, for anything with a unit, and for versions. Never open a sentence with a numeral. Decimals lead with a zero.
- Numeric dates are ISO 8601: `2026-08-17`. No seasons — name the month or quarter.
- Hyphenate compound modifiers before a noun ("a well-designed app"), never after an -ly adverb.
- No idioms or cultural references. "Out of the box", "grandfathered in", and sports metaphors fail for translated and non-native readers. Say the literal thing.

The full rules — punctuation, hyphenation, numbers, dates, capitalization, abbreviations, code in prose, placeholders, example data, UI wording — are in `references/mechanics.md`. Read it before writing documentation, a README, a runbook, or anything document-length.

## Warnings and notices

State the consequence before the reader can act on the command — never after it, never in a trailing parenthesis.

Bad:

> Run `terraform destroy` to tear down the stack (note: this also deletes the database).

Good:

> **Warning:** The next command permanently deletes the database, including its backups. There is no undo.
>
> Run `terraform destroy` to tear down the stack.

Three levels, by what's at stake: **Note** for useful asides the reader may skip, **Caution** for proceed-carefully, **Warning** for irreversible damage — data loss, security, money. A notice is never a prerequisite, a step, or a cross-reference; those go in the body, before the step they govern. Never stack two notices — if everything is highlighted, nothing is.

## Placeholders and example data

- Placeholders are descriptive `UPPER_SNAKE_CASE`: `PROJECT_ID`, `REGION` — never `foo`, `xx`, or `MY_PROJECT`. After a command with several, write "Replace the following:" and one bullet per placeholder, in order.
- A copy-paste command must run unedited — no `[optional]` or `{a|b}` syntax inside a copyable block.
- Example data is fictional by construction: `example.com`, RFC 5737 IPs (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`), phone numbers `800-555-01xx`. Never real people, emails, or credentials.
- Example resource names describe the reader's world: `prod-orders-queue`, not `test1`.

## Format guides

Every artifact has a word or line budget — a hard cap, not a target. A number is enforceable where "be concise" is not. Count before you deliver; over budget means cut more, not apologize. One rare exception: when facts the reader must act on truly cannot fit, keep the facts and flag the overrun to the reader with its reason. A silent overrun is never an option. Budgets cut narrative, never caveats or risks — those change what the reader does, so they always fit.

| Artifact | Budget |
|---|---|
| Commit subject | 50 characters target; 72 hard max |
| Commit body | ≤ 10 lines |
| PR description | ≤ 10 lines beyond the template |
| Ticket or bug report body | ≤ 200 words |
| Code comment | 1 line |
| PR review comment | a phrase; 1 sentence ceiling |
| Slack message | ≤ 4 sentences; detail goes to the thread |
| Status update | 3 lines: done, next, blocked |
| Answer to the user | 1–3 sentences or ≤ 5 bullets before any detail |
| Runbook intro | ≤ 3 sentences before the prerequisites |

Each guide's section list is closed: write the listed sections and no others. A new section earns its place only if the reader acts differently without it.

### Documentation and runbooks

- At most 3 sentences of intro before the prerequisites.
- Prerequisites first, as a list — never buried in a note halfway down.
- Numbered steps when order matters; one instruction and one reader decision per step.
- Each step: condition, then location, then action, then result — "If the queue is empty, in the `deploy` directory run `make check`. The output ends with `plugin OK`."
- Document one way to do the task — the shortest accessible one — not every way. Alternatives get their own section or a link.
- Prefix optional steps with "Optional:".
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
- State only facts you can cite. Never add a date or number the source doesn't give — "last week" stays "last week".
- Wrap lines at 72 characters — `git log` indents but never wraps.
- Bullets are fine. A change whose subject says everything needs no body.

### PR descriptions

Keep the house shape — a 1–3 bullet summary plus a test plan — and write it in this style. Budget: 10 lines beyond the template.

- Each bullet states one change and its why, in at most 20 words, active voice.
- Test plan steps are commands a reviewer can run, each with its expected result.

Example bullet: "Retry token refresh once on 401, so clock skew no longer logs the user out."

### Tickets and bug reports

The reader is the engineer who fixes it, not the one who found it. Body budget: 200 words. The sections, closed:

1. Title: the defect, not the investigation — "`GET /orders` 500s on an expired `cursor`", not "Investigate order API errors".
2. Impact: who hits it and how often.
3. Repro: numbered steps, one instruction each, ending with expected vs. actual.
4. Cause, if known, in at most 2 sentences. "Unknown" is a valid entry.

The diagnosis narrative — verification runs, ruled-out hypotheses, measurements — goes in a ticket comment, never the body. The fixer reads the body; the curious read the comments.

### Code comments and docstrings

The default is no comment. Code already says what it does; a comment earns its place only by carrying a fact the code cannot.

- One line is the default — a soft limit, not a cap. A comment that runs long explaining *what the code does* is a signal to rename, split, or retype the code instead. A comment that runs long recording a *decision* — the constraint, the trade-off, the alternative that was rejected — is doing its job; keep it.
- Never restate what the reader's eyes just parsed. `if flags.new_checkout:` needs zero lines of comment — the flag name is the comment.
- What earns a line: a non-obvious why ("retry once — the vendor 401s on clock skew"), an invariant the code cannot express ("caller holds the lock"), a warning ("flush before close, or data is lost"), code that looks wrong but isn't, or the URL of the copied snippet, spec, or bug that forced this shape.
- Write for the next reader of the file, never the reviewer of this diff: no "added X", "changed to Y", "per feedback".
- TODO carries an owner or an issue: `TODO(#4821): remove after the flag ships.`
- Docstrings and API descriptions use third-person present, not imperative: "Returns the parsed config", "Creates a task on the given list". The first sentence states the purpose without repeating the name; a boolean parameter reads "If true, X. If false, Y."; a deprecation names the replacement and the version in its first sentence.
- The deletion test: remove the comment. If the reader loses no fact, it stays removed.

### PR review comments

The author reads this in a queue of twenty, on someone else's schedule. The default is a phrase, not a sentence: the fix as a bare command, or the defect named in a few words — "Await `flushBuffer()`", "typo: `recieve`", "dead code — delete". Add one sentence only when the author cannot act on the phrase alone: the consequence, the condition that reproduces the defect, or a rule citation. That sentence is the ceiling — a paragraph in a review comment is itself a defect.

- Backtick the exact name, line, or value — the author greps for it.
- Open with the defect or the fix. Delete "I noticed that", "It looks like", "Consider that", "Just a thought" — the comment's existence is the flag.
- Never restate the code. The author wrote it and is looking at it.
- State the fix as a bare command: "Await `flush()` before returning", not "you might want to consider awaiting".
- Consequence only when the fix is not self-evident; never a lecture. "or the response returns before the write lands" earns its place; a paragraph on the event loop does not.
- One defect per comment. Two defects on one line are two comments.
- Hedging is a decision, not a tone. If you are unsure, label it `question`; if you are sure, drop "possibly", "perhaps", and "might want to".

Before:

> I noticed that in the `handleUpload` function on line 42, the call to `flushBuffer()` is not being awaited. This is a common issue with async code — since `flushBuffer` returns a Promise, execution continues immediately without waiting for the flush to complete. This could potentially lead to a race condition where the response is sent before the data is fully written, which might cause intermittent data loss that would be hard to debug. It would probably be a good idea to add an `await` here.

After:

> **issue (blocking):** Await `flushBuffer()` — the response can return before the write lands.

Every fact the author acts on survived. The Promise tutorial, the "hard to debug" aside, and the hedges did not. The consequence stayed because "add await" alone does not tell the author why it blocks the merge.

### Slack messages and status updates

- Budget: 4 sentences. The thread absorbs everything else.
- The first sentence carries the point: the answer, the ask, or the status. Details follow or go in the thread.
- One message, one topic. Two topics are two messages.
- If you need action, name the person and the deadline.
- Status updates follow the shape: done, next, blocked.

Bad: "Hey, so I was looking into the deploy thing from yesterday and there might be some issues with how the pipeline handles caching, happy to go into detail but wanted to flag it."

Good: "Found the deploy bug: the pipeline reuses the old build artifact because the cache key ignores the lockfile. One-line fix — I can ship it today unless anyone objects."

### Answers to the user

The reader is the person who asked, mid-task, watching a terminal. They have the code open and they know what they asked for.

- Budget: the answer in 1–3 sentences or 5 bullets. Detail after only when the reader acts on it. Fitting the budget by packing two facts into one sentence is a defect — spend a bullet per fact instead.
- Lead with the answer, the result, or the blocker. Never with what you are about to say.
- Report a finished change by its effect and where it lives: "`retry.ts:88` now backs off with jitter." No tour of the diff.
- Cite `file.ts:42`; do not paste code the user already has. Paste only what they cannot see: an error string, a test failure, a command's real output.
- One line per changed file beats a paragraph per changed file.
- Bad news goes first and plainly: what failed, what you skipped, what you are unsure of. Compression never eats a caveat, a risk, a disagreement, or a number — absolute values and dates survive, and a delta never replaces its endpoints.
- No closing summary that repeats the opening. No "let me know if you'd like me to…" when you have already offered.

Bad: "Great question! I've gone ahead and made some updates to the retry logic. Let me walk you through what I did. First, I looked at the existing implementation…"

Good: "Retries now jitter — `retry.ts:88`. The fixed 200 ms backoff had every client retrying in lockstep after an outage. Tests pass; I did not touch the circuit breaker."

### Explanations

- Define each term before you first use it.
- Introduce one new concept per paragraph.
- Ground the explanation in the reader's concrete world: real file names, real commands, real error text.
- Analogies are welcome; after the analogy, state the literal mechanism.

## What this is not

- **Not a tone flattener.** Greetings, contractions, and humor stay in Slack and chat. In documentation, personality yields to translatability — the style removes ambiguity everywhere and jokes only where the reader chose to chat.
- **Not telegraphy.** Brevity comes from fewer sentences, never from dropping articles or actors in a sentence you keep. A kept sentence stays fully formed.
- **Not for voice-driven prose.** Essays and blog posts use the writing-style skill.
- **Not for quoted material.** Code, log output, error messages, and other people's words stay verbatim.

## Rewriting existing text

When asked to simplify or clarify a text:

1. Read `references/word-substitutions.md`; for document-length text, read `references/mechanics.md` too.
2. List every technical fact in the original: names, numbers, conditions, caveats.
3. Strike the restatements — most drafts state each fact more than once. Only the fact list survives.
4. Rewrite by the rules above. Expect the result to be shorter: two paragraphs usually collapse to one or two sentences, or a few bullets.
5. Check the rewrite against the fact list. A rewrite that drops a caveat is worse than the bloated original.

## Self-check

Document level first — these catch what sentence fixes cannot:

- Count the words or lines against the budget table. Over? Cut sections, then sentences, and count again. Deliver over budget only with a flagged reason.
- Would deleting any section change what the reader does? If not, delete the section.
- Any sentence that records what you did to learn, not what the reader must know? Move it to a comment or thread.
- Does every paragraph lead with its point? Does the document?

Then sentence level — each one is countable:

- A sentence over 25 words (20 for an instruction)? Split it.
- A paragraph over 6 sentences? Split it.
- More than 3 nouns in a row? Unstack it.
- Passive voice hiding a debuggable actor? Name the actor — unless naming it blames the reader.
- Software wanting, seeing, or knowing? Give it a technical verb.
- Perfect or progressive tense? Use simple past, present, or future — and add the date or version it was hiding.
- "Will" or "would" describing what the software does today? Use the present.
- A bare "this" or an "it" with two possible antecedents? Add the noun.
- An "only" far from the word it limits? Move it next door.
- A negative the reader must invert ("won't prevent")? State the positive.
- "Please" in an instruction, "let's", or "the user" meaning the reader? Write the bare command to "you".
- A condition, location, or goal after its instruction? Move it before.
- Link text that does not name its destination, or "above"/"below" as a pointer? Name it.

Then word level:

- A code item pluralized, verbed, or paraphrased? Backtick the exact literal and rebuild the sentence around it.
- The same thing under two names? Unify them.
- A bare "should", a casual "may", a hypothetical "would"? Decide: "must", "we recommend", "can", or "might".
- A word from the substitution tables — bloat, vague, time-anchored, non-inclusive? Substitute it.
- A superlative or guarantee you cannot prove? Scope it: "helps", the number, or delete.
- A vague quantity where a number exists? Use the number.
- Missing articles or a dropped "that"? Restore them.
- `foo`, `test1`, or a real email in an example? Use descriptive placeholders and reserved example data.
- A commit subject over 50 characters, non-imperative, or run into the body with no blank line? Fix it.
- A code comment that restates the code? Delete it, or fix the code it apologizes for.
- A review comment past one sentence, opening with a hedge, or quoting the author's code back? Cut to a phrase.
- A sentence whose deletion changes nothing the reader does? Delete it.
- Would a reader one level down (QA, support, a new hire) need a follow-up question? Down-level it.
