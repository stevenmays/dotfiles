---
name: writing-style
description: Write in Steven's voice—pragmatic, curious, pedagogical. Opens on what actually happened, builds mental models from first principles, uses worked examples, and handles uncertainty honestly. Use for essays, blog posts, and technical articles.
---

# Writing Style

A teaching-first voice that makes readers collaborators. Start with the real situation that made you write, then build the mental model they're missing. Trade-off thinking and personal stakes still matter—but clarity and curiosity come first.

## How to Write a Piece

Follow these steps in order. The later sections say what good looks like; these steps say when to apply each rule.

1. **Before you draft, write three lines for yourself.** The situation that made you write. Your point, in one sentence a colleague could repeat. The question your reader brings. If you can't state the point yet, draft to find it, then come back to this step.
2. **Draft for yourself.** Get the argument down in the order it comes to you. Don't polish sentences yet, because most of them will change.
3. **Revise the structure.** Move your point to the end of the introduction. Rewrite the first sentence of each section as that section's point. Read those sentences alone, in order. If they don't make the argument, reorder or cut sections until they do.
4. **Revise each paragraph in four passes.** Run them in this order, because each pass changes what the next one sees:
   1. *Subjects.* List the subject of every sentence. Choose the one to three characters the paragraph is about, and make them the subjects.
   2. *Verbs.* Circle each -tion, -ment, -ance, -ence, and -ity noun. Where you can name who acts, turn the noun back into a verb with that actor as its subject.
   3. *Order.* Start each sentence with what the reader already has, and end it on what's new.
   4. *Sprawl.* Split any sentence that chains two "which" clauses or trails an "-ing" phrase.
5. **Cut.** Delete doubled words, stacked hedges, intensifiers, and sentences about the writing.
6. **Read it aloud.** Rewrite any sentence you wouldn't say to a colleague. Then run the Final Check and the Self-Review.

Before you revise, read the Clarity Lessons in [writing-style-examples.md](writing-style-examples.md). They run these steps on real drafts, so you can see what each fix looks like.

## Core Voice Principles

**Write to be unsummarizable.** A summary shortens text by deleting words. Aim for prose so dense that any deletion costs an idea—if a paragraph survives a 50% cut intact, the cut half was fluff, so make the cut. The test: summarize your own draft. Whatever the summary drops without loss was never pulling weight; delete it from the original. What's left is writing a summary can only lengthen, not shorten.

Density isn't terseness. Orientation, worked examples, permission-giving, and an aside that carries the voice earn their words by carrying ideas the reader needs—keep them. The enemy is filler: stacked hedges, restatement, throat-clearing, and connective tissue that adds length without adding meaning. Cutting fluff often surfaces a sharper idea hiding underneath it—the dense version usually says *more*, not just less.

Never buy density by turning verbs into nouns. "Pool exhaustion causes request failure" is short and opaque. "When the pool runs out of connections, requests fail" is longer and clearer.

**Open on what actually happened.** Start with the specific thing that made you write: what broke, what you measured, what surprised you, what you were trying to do. Or open cold on the claim itself, stated plainly. Tell it the way you'd tell a colleague. Then say plainly why it matters to the reader, and get to your point early. A number belongs in the first line only when the number is the news.

> Our API bill doubled in March, and it took us two weeks to find out why. We had moved a timestamp to the top of the prompt, so prompt caching never matched. If you use caching, put the static content first.

Never open with a hook formula. Readers now recognize these as generated:
- a statistic followed by a rhetorical question ("10x cheaper. But how?")
- "Most people think X. But…"
- "Here's the thing" or "What if I told you"
- a one-line paragraph that exists to build suspense

The test: read the first paragraph aloud. If you wouldn't say it that way to someone at work, rewrite it as what happened.

**Build from first principles.** Assume a smart reader missing one key mental model. Identify that model and construct it step by step. Define terms before using them. Example: explain tokens before embeddings before attention.

**Make readers collaborators, not spectators.** Use "we" for reasoning you and the reader do together. You're figuring this out together.
- "Now that we understand tokens, we can talk about embeddings."
- "Let's work through a tiny example."

"We" never stands in for a real actor. If the library hashes the key, write "the library hashes the key", not "we hash the key". Own your opinions in first person: "I think most teams split into microservices too early", not "it can be argued that teams adopt microservices prematurely".

**Permission-giving when it's hard.** When concepts get abstract, acknowledge the difficulty and encourage:
- "This is the most complicated part so far. Stick with me."
- "You don't need to fully grok the math—here's what matters."

**Be self-aware about the setup.** You can acknowledge theatrics ("Now that I've hooked you with fancy charts...") but keep it tight. One beat of meta, then move on.

**Honest uncertainty.** When you don't know, say so plainly—then say what's still useful.
- "We don't really know what's inside this matrix. But we know what it does, and that's enough."
- "I didn't dig into this deeply—Andrej Karpathy has a better explanation."

Hedge once, on the claim you can't fully back, and say why: "Pool size probably explains the stalls; we tested one host." Stacked hedges ("it seems this could possibly") read as evasion. A claim with no hedge where doubt exists reads as overreach. Intensifiers ("clearly", "obviously", "of course") read as their opposite: delete them.

**Name who broke it.** When you report a failure, make the responsible actor the subject, especially when that actor is you. Write "I skipped the dry run, so our migration script deleted 1,400 records", not "some records were inadvertently affected during the migration". The test: would you accept the sentence if someone wrote it to you about your own loss?

**Trade-off thinking.** Still core. Present decisions as trade-offs, not right/wrong. Show what you gain and give up.

**Scope deliberately.** Say what you will and won't cover. Cut side quests or link them out.
- "We're focusing on the caching mechanism. We won't cover fine-tuning here."

## Structure Patterns

Two things hold in every piece:
- **The introduction ends on the point.** By its last sentence, the reader knows the problem and your answer, or a promise that names the themes ahead. A personal essay may hold its point until the end, but its opening still poses the question.
- **Each section opens with its point.** Read the first one or two sentences of every section in order. They must read as an outline of the argument. Move a point up when it appears only at the end of its section.

Order sections by claim, not by the order you discovered things. "Week 1: Redis" and "Week 2: The N+1 query" become "The N+1 query" and "Why caching hid it".

Everything else is a **menu, not a mandate.** The beats below are moves to reach for, not an arc to stamp on every piece. A draft may open cold on the claim, skip the learning-objectives block, bury the worked example mid-piece, drop the summary, or end flat. **Varying structure across pieces is the primary defense against sounding generated**—if your last few posts all ran hook → objectives → first principles → example → trade-offs → summary, break the pattern on this one. Pick the beats the argument needs and order them the way it wants, not the way the list happens to be numbered.

### Technical/Educational moves
- **Opening**: What happened and why it matters, in plain words
- **"By the end of this post..."**: What the reader will be able to do—only when there's a real payoff to promise
- **First principles**: Build the mental model from primitives
- **Worked example**: One small, concrete, end-to-end demonstration
- **Trade-offs**: Options and consequences, pick a side
- **In summary**: A few sentences that compress the whole post
- **Open question**: One thing you still can't answer, stated concretely ("We can't yet predict how fast warm prefixes get evicted")
- **Resources/Further reading**: Links for going deeper

### Essay/Personal moves
- **Personal context** — A real constraint (time, money, family, risk)
- **Practical question** — "What's actually happening?" or "What do you do about it?"
- **Build the model** — First principles, evidence, trade-offs
- **Operating principle** — Concrete, not moralistic

## Signature Techniques

Reach for these when they do real work, not to hit a quota. A technique slotted in because the template expects it—an objectives block over thin content, a trade-off table with a single real axis, a transition the reader didn't need—is exactly the manufactured polish that reads as generated.

**Learning objectives block.** Near the top, state what the reader will get:
- "By the end of this post, you'll understand the mechanism behind prompt caching and know when to use it."

**Worked micro-examples.** One tiny, repeating example that threads through the piece. Use the same tokens, the same 5-step flow, the same toy dataset. This creates continuity and lets readers track transformations.

**Pseudocode before real code.** Show the algorithm in plain pseudocode first. Then show real code if needed. Lower the barrier.

**"In summary" compressions.** One paragraph that restates the core model in plain language. If you can't summarize it, you don't understand it yet.

**Transitions that orient.** When the reader genuinely needs reorientation, tell them where they are—one or two per piece, not a stock phrase after every section:
- "Now that we've defined X, we can finally talk about Y."
- "That's the theory. Let's see it in practice."

**Name a pattern only when it's real.** Coining a memorable term—a label, an acronym, a "the X principle"—manufactures the feeling of insight, so it's the highest-risk move here. Do it only when the thing named is a genuine, defensible pattern you could point at twice. Never to fill a slot or make a thin point feel sticky.

**Trade-off tables.** When comparing options:
```
| Option | Cost | Latency | Complexity |
|--------|------|---------|------------|
| Pinecone | $70/mo | High | Low |
| S3 at runtime | $0 | ~100ms | Medium |
| Bundle in Lambda | $0 | Lowest | Lowest |
→ We chose bundling.
```

**Personal stakes where relevant.** "I've been integrating LLMs into my workflow" or "I tested this on my own API" still establishes credibility—just don't let it overshadow the teaching.

## Evidence & Support

- **Every section needs at least one concrete, checkable fact**—a real figure, a named source and its finding, a dated event—not merely the *shape* of evidence. A passage with the cadence of measurement but no number in it fails; "studies show," "significantly faster," and "many teams" are the tells. If you can't name a number or a source, you're asserting, not supporting.
- Prefer your own measurements, even small ones, over assertions
- Use actual numbers: token counts, latency, costs, percentages
- Cite sources in a Resources section, not inline footnotes
- When referencing tests, describe the shape: inputs, repeats, what you measured

## Formatting

- `##` headers that match reader questions ("Tokenization", "The Caching Mechanism", "Trade-offs")
- Short paragraphs (1-3 sentences)
- Code blocks for pseudocode and minimal real code
- Bullet lists for steps, assumptions, or outcomes—vary their length; not everything comes in threes
- Bold for key terms on first use, not for emphasis
- **Ration em-dashes.** They're a rhythm tool, not a default connector: roughly one em-dash construction per paragraph at most. Rotate in colons, periods, parentheses, and semicolons. Each em-dash aside must carry something the main clause genuinely can't—if a comma or period would do, use it.
- **A colon follows a complete clause.** It means "that is" or "for example". Write "The fix needs three things: a lock, a retry, and a timeout", not "The fix needs: a lock, a retry, and a timeout".

## Sentence Clarity

A reader understands a sentence fastest when its subject names a character and its verb names the action. Writers can't judge their own clarity by rereading, because they already know what they meant. So each rule here comes with a mechanical test.

**Make the main character the subject.** A character is whoever acts: a team, a component, a user, you. Skip any short opener and read the first 7–8 words of each sentence. If the subject is an abstraction, or no verb appears in that span, rewrite.
- Before: "The introduction of a write-ahead log by the storage team eliminated torn writes."
- After: "The storage team added a write-ahead log, so a crash can no longer tear a write."

An abstraction can still be the subject when its verb is literal: "the scheduler retries the job" is fine. A figurative verb is the defect: "complexity dies here".

**Put actions in verbs, not nouns.** A nominalization is a verb turned into a noun: "evaluation", "failure", "reliance". Circle each noun that ends in -tion, -ment, -ance, -ence, or -ity, and ask who does it. If you can name the doer, make the doer the subject and the noun a verb. Watch for "there is a need for", "conduct a migration", and chains like "the cause of the failure of the deployment".
- Before: "There was a need for a reevaluation of our retry policy after the discovery of duplicate charges."
- After: "Once we found duplicate charges, we had to rethink how we retry."

Keep a nominalization when it refers back to the previous sentence ("This change…"), names a thing ("the request"), or is a term of art ("garbage collection").

**Join cause and effect with conjunctions.** "Led to", "resulted in", "due to", and "in the presence of" hide the logic inside nouns. Write "because", "when", "if", or "although", and tell events in the order they happened.
- Before: "The cache's introduction led to stale reads in the presence of concurrent writes."
- After: "When two requests write the same key at once, the cache returns the older value."

**Hold a topic string.** Keep a paragraph's subjects on one to three recurring characters. List the subject of each sentence. If the list wanders, choose the paragraph's character and rebuild the sentences around it. Vary sentence form, never the subject, for variety.

**Put old information first and new information last.** Open each sentence with something the reader already has: the end of the previous sentence, or the paragraph's character. Introduce a new term at the end of a sentence, then explain it at the start of the next one. The end of a sentence carries its stress, so put the most important new words there. Read the last four words of each sentence. If they're a hedge, an attribution, a time phrase, or a tag ("in our experience", "as well"), move them to the front.
- Before: "Shared backoff schedules turn a blip into an outage, in our experience."
- After: "In our experience, shared backoff schedules turn a blip into an outage."

**Use the passive voice when it passes a test.** The passive is right when the doer is unknown or obvious, when it moves a long new phrase to the end, or when it keeps the paragraph's character as the subject. A passive that passes none of these tests becomes active.

**Stop sprawl after the main clause.** Two "which" or "that" clauses chained after the main verb lose the reader. A trailing "-ing" phrase built on an abstract verb ("ensuring", "highlighting", "enabling", "underscoring") is sprawl too. Split the sentence, or end it with a short noun phrase that sums up the clause before it.
- Before: "We moved sessions to Redis, which is an in-memory store that keeps keys in RAM, which means login no longer times out."
- After: "We moved sessions to Redis, a change that ended the login timeouts."

**Cut doubled words and implied modifiers.** Keep one word of a synonym pair ("fast and efficient", "robust and reliable"). Delete a modifier the head word already implies: "end result", "past history", "completely eliminate", "each and every".

## Sentence-Level Texture

Vary sentences in **length and intensity.** Not every sentence should do rhetorical work—a draft where each line is equally sharpened reads as machine-made. Set a long, qualified sentence against a blunt three-word one. Leave plain, flat patches next to the sharp turns, and let an idiosyncratic word choice or a slightly uneven digression stand instead of sanding it smooth. Uniform excellence is the tell; engineered asymmetry reads as someone who wrote this once and meant it.

Change length where the content turns: a short sentence after a long run lands the point. Ration flourishes. A balanced pair, a reversal, or an echoed phrase gets at most one use per piece. Build it from the piece's own words, and use it only to close an argument the piece actually made.

## What to Avoid

- Throat-clearing intros ("In today's world...")
- Abstract claims without examples or evidence
- Leaving the reader to guess why the piece matters to them
- Long detours—link them instead
- Wry closers that undercut clarity (save those for purely personal essays)
- Pretending certainty where there is none
- Stock connective phrases ("Now that we've defined X...", "By the end of this post...", "Let's work through...") more than once or twice—and never to paper over a point you haven't actually made
- Fluff that survives summarizing—any sentence a reader could cut without losing an idea
- Writing about the writing: "it's worth noting", "interestingly", "as we'll see", "it has been observed that". State the claim.
- Additive connectives ("moreover", "additionally", "furthermore"). Use "but" for a real contrast and "so" for a real consequence. If deleting a connective breaks the passage, the reasoning has a gap: fix the reasoning.
- Obeying folklore rules. Starting a sentence with "And", "But", or "Because", splitting an infinitive, and ending on a preposition are all correct. Avoiding them makes prose stiff.

## Final Check

Before publishing, ask (not every piece needs every beat—these test whether the moves you *did* use earned their place):
- Does the opening say what happened the way I'd say it to a colleague, with no hook formula?
- Does the introduction say why the problem matters to the reader, and end on the point?
- Read the first one or two sentences of each section in order. Do they form an outline of the argument?
- If I promised the reader something up front, did I deliver it?
- Did I build from primitives before abstractions?
- If the idea is abstract, did I ground it in a concrete example?
- Did I name trade-offs and pick a side?
- Is it unsummarizable—would a faithful summary have to run nearly as long as the original? Could I cut any paragraph in half without losing an idea? If yes, cut it.

## Self-Review Before Returning

Run this on your own draft to catch what reads as AI-generated or unclear. Each item maps to a rule above.
- **Subjects:** In the first 7–8 words of each sentence, is the subject a character, and does a verb appear? Do each paragraph's subjects stay on one to three characters? → Sentence Clarity
- **Nominalizations:** Can you name who does each -tion, -ment, or -ity noun? Make the doer the subject and the noun a verb. → Sentence Clarity
- **Endings:** Do the last four words of each sentence carry new, important information, not a hedge or a tag? → Sentence Clarity
- **Hedges:** More than one hedge on a claim, or any "clearly" or "obviously"? → Core Voice Principles
- **Structure:** Does this piece follow the same arc as my last one? If so, break it. → Structure Patterns
- **List variety:** Are parallel runs and lists all the same length—everything in threes? Vary them. → Signature Techniques / Formatting
- **Em-dash density:** More than one em-dash construction in any paragraph? Convert some to colons, periods, or parentheses. → Formatting
- **Substance:** Does every section carry at least one concrete, checkable fact, or is one running on cadence alone? → Evidence & Support
- **Manufactured framework:** Did I coin a memorable term for something that isn't actually a pattern? Cut it. → Signature Techniques
- **Canned phrasing:** More than one stock opener or transition, or one used to cover a missing argument? → What to Avoid
- **Uniform polish:** Is every paragraph equally worked? Equal polish everywhere is the loudest tell—leave a plain patch. → Sentence-Level Texture
