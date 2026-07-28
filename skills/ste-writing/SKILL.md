---
name: ste-writing
description: Simplified Technical English (ASD-STE100) adapted for software engineering. Use whenever writing or rewriting technical prose for other people — documentation, READMEs, runbooks, PR descriptions, commit bodies, release notes, incident updates, Slack messages, status reports — and whenever explaining anything technical, even if the user doesn't name a format. Also use when asked to simplify, tighten, clarify, or "plain English" existing technical text. Not for essays or blog posts — writing-style covers those.
---

# Simplified Technical English for Software

ASD-STE100 is the controlled language aerospace has used since the 1980s so that maintenance instructions cannot be misread. It has two parts: a small set of writing rules, and a dictionary where every word has exactly one meaning. This skill keeps the rules and swaps the aerospace dictionary for software conventions.

The audiences match. Engineering text is read by on-call responders at 3 a.m., non-native English speakers, new hires without context, and people skimming Slack on a phone. Write for the least-rested, lowest-context reader — everyone else benefits too.

## The contract

Every rule below serves one goal: a reader who parses a sentence once arrives at exactly one meaning.

- One word has one meaning.
- One sentence carries one idea — or one instruction.
- One paragraph covers one topic.

## Word rules

**Pick one name per concept and never vary it.** Elegant variation is for fiction. If the doc calls it "the worker", that process is never later "the daemon", "the service", or "the consumer" — a new name makes the reader ask whether you mean a new thing. When two names are entrenched, pick one and state the alias once: "the ingest worker (deployed as `queue-consumer`)".

**Technical names are exact and literal.** Commands, flags, paths, error strings, API names, and config keys go in backticks with exact spelling and casing, never paraphrased. Readers grep for them. Write "the `ECONNRESET` error", not "a connection reset issue".

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

**Simple tenses only: past, present, future.** Perfect and progressive tenses blur time. "Has been deprecated" hides the date — "was deprecated in v3.2" demands one. "Is being rolled out" → "the rollout started Monday and finishes Friday".

**Keep the small words.** Telegraphic style ("Update config before restart") saves you two words and costs every reader a parse: is "restart" a noun or a command? Write "Update the config file before you restart the service." Articles are load-bearing, especially for non-native speakers. Commit subjects are exempt — the 72-character limit wins there.

**No more than three nouns in a row.** "The webhook retry queue consumer lag alert" makes the reader reverse-engineer the grammar. Unstack with prepositions: "the alert for consumer lag on the webhook retry queue". An established proper name may stay clustered — format it as a technical name.

**Condition before instruction.** Readers execute as they read. "Restart the worker if lag exceeds 1,000" risks a restart before the condition is read. Write "If lag exceeds 1,000, restart the worker."

## Paragraph rules

- At most 6 sentences per paragraph, one topic, and the first sentence states the topic.
- More than about 3 parallel items in a sentence? Use a vertical list.
- List items use parallel grammar and carry one idea each.

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

### PR descriptions

Keep the house shape — a 1–3 bullet summary plus a test plan — and write it in STE:

- Each bullet states one change and its why, in at most 20 words, active voice.
- Test plan steps are commands a reviewer can run, each with its expected result.

Example bullet: "Retry token refresh once on 401, so clock skew no longer logs the user out."

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
- **Not compression.** Restored articles and named actors sometimes make text longer. Shortness is a side effect; clarity is the goal.
- **Not for voice-driven prose.** Essays and blog posts use the writing-style skill.
- **Not for quoted material.** Code, log output, error messages, and other people's words stay verbatim.

## Rewriting existing text

When asked to simplify or clarify a text:

1. Read `references/word-substitutions.md`.
2. List every technical fact in the original: names, numbers, conditions, caveats.
3. Rewrite by the rules above.
4. Check the rewrite against the fact list. A rewrite that drops a caveat is worse than the bloated original.

## Self-check

Before returning any text, scan for these — each one is countable:

- A sentence over 25 words (20 for an instruction)? Split it.
- A paragraph over 6 sentences? Split it.
- More than 3 nouns in a row? Unstack it.
- Passive voice hiding a debuggable actor? Name the actor.
- Perfect or progressive tense? Use simple past, present, or future — and add the date or version it was hiding.
- The same thing under two names? Unify them.
- A bare "should"? Decide: "must" or "we recommend".
- A word from the substitution table? Substitute it.
- A condition or warning after its instruction? Move it before.
- A vague quantity where a number exists? Use the number.
- Missing articles? Restore them.
