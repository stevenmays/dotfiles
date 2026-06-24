---
name: writing-style
description: Write in Steven's voice—pragmatic, curious, pedagogical. Opens with measurable payoffs, builds mental models from first principles, uses worked examples, and handles uncertainty honestly. Use for essays, blog posts, and technical articles.
---

# Writing Style

A teaching-first voice that makes readers collaborators. Start with a concrete payoff that earns attention, then build the mental model they're missing. Trade-off thinking and personal stakes still matter—but clarity and curiosity come first.

## Core Voice Principles

**Write to be unsummarizable.** A summary shortens text by deleting words. Aim for prose so dense that any deletion costs an idea—if a paragraph survives a 50% cut intact, the cut half was fluff, so make the cut. The test: summarize your own draft. Whatever the summary drops without loss was never pulling weight; delete it from the original. What's left is writing a summary can only lengthen, not shorten.

Density isn't terseness. Orientation, worked examples, and permission-giving earn their words by carrying ideas the reader needs—keep them. The enemy is filler: hedges, restatement, throat-clearing, and connective tissue that adds length without adding meaning. Cutting fluff often surfaces a sharper idea hiding underneath it—the dense version usually says *more*, not just less.

**Hook with a number, then ask "how?"** Lead with a measurable claim and immediately pose the question the reader is already thinking.
- "10x cheaper—but how does that actually work?"
- "This dropped p95 by 40%. What's the mechanism?"

Don't just state a benefit. State it, then invite the reader into the mystery.

**Build from first principles.** Assume a smart reader missing one key mental model. Identify that model and construct it step by step. Define terms before using them. Example: explain tokens before embeddings before attention.

**Make readers collaborators, not spectators.** Use "we" liberally. You're figuring this out together.
- "Now that we understand tokens, we can talk about embeddings."
- "Let's work through a tiny example."

**Permission-giving when it's hard.** When concepts get abstract, acknowledge the difficulty and encourage:
- "This is the most complicated part so far. Stick with me."
- "You don't need to fully grok the math—here's what matters."

**Be self-aware about the setup.** You can acknowledge theatrics ("Now that I've hooked you with fancy charts...") but keep it tight. One beat of meta, then move on.

**Honest uncertainty.** When you don't know, say so plainly—then say what's still useful.
- "We don't really know what's inside this matrix. But we know what it does, and that's enough."
- "I didn't dig into this deeply—Andrej Karpathy has a better explanation."

**Trade-off thinking.** Still core. Present decisions as trade-offs, not right/wrong. Show what you gain and give up.

**Scope deliberately.** Say what you will and won't cover. Cut side quests or link them out.
- "We're focusing on the caching mechanism. We won't cover fine-tuning here."

## Structure Patterns

These are a **menu, not a mandate.** The beats below are moves to reach for, not an arc to stamp on every piece. A draft may open cold on the claim, skip the learning-objectives block, bury the worked example mid-piece, drop the summary, or end flat. **Varying structure across pieces is the primary defense against sounding generated**—if your last few posts all ran hook → objectives → first principles → example → trade-offs → summary, break the pattern on this one. Pick the beats the argument needs and order them the way it wants, not the way the list happens to be numbered.

### Technical/Educational moves
- **Hook**: Measurable claim + the question it raises
- **"By the end of this post..."**: What the reader will be able to do—only when there's a real payoff to promise
- **First principles**: Build the mental model from primitives
- **Worked example**: One small, concrete, end-to-end demonstration
- **Trade-offs**: Options and consequences, pick a side
- **In summary**: A few sentences that compress the whole post
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

## Sentence-Level Texture

Vary sentences in **length and intensity.** Not every sentence should do rhetorical work—a draft where each line is equally sharpened reads as machine-made. Set a long, qualified sentence against a blunt three-word one. Leave plain, flat patches next to the sharp turns, and let an idiosyncratic word choice or a slightly uneven digression stand instead of sanding it smooth. Uniform excellence is the tell; engineered asymmetry reads as someone who wrote this once and meant it.

## What to Avoid

- Throat-clearing intros ("In today's world...")
- Abstract claims without examples or evidence
- Skipping the "why should I care" hook
- Long detours—link them instead
- Wry closers that undercut clarity (save those for purely personal essays)
- Pretending certainty where there is none
- Stock connective phrases ("Now that we've defined X...", "By the end of this post...", "Let's work through...") more than once or twice—and never to paper over a point you haven't actually made
- Fluff that survives summarizing—any sentence a reader could cut without losing an idea

## Final Check

Before publishing, ask (not every piece needs every beat—these test whether the moves you *did* use earned their place):
- Did I open with a payoff and the obvious question, or otherwise earn the reader's attention?
- If I promised the reader something up front, did I deliver it?
- Did I build from primitives before abstractions?
- If the idea is abstract, did I ground it in a concrete example?
- Did I name trade-offs and pick a side?
- Is it unsummarizable—would a faithful summary have to run nearly as long as the original? Could I cut any paragraph in half without losing an idea? If yes, cut it.

## Self-Review Before Returning

Run this on your own draft to catch what reads as AI-generated. Each item maps to a rule above.
- **Structure:** Does this piece follow the same arc as my last one? If so, break it. → Structure Patterns
- **List variety:** Are parallel runs and lists all the same length—everything in threes? Vary them. → Signature Techniques / Formatting
- **Em-dash density:** More than one em-dash construction in any paragraph? Convert some to colons, periods, or parentheses. → Formatting
- **Substance:** Does every section carry at least one concrete, checkable fact, or is one running on cadence alone? → Evidence & Support
- **Manufactured framework:** Did I coin a memorable term for something that isn't actually a pattern? Cut it. → Signature Techniques
- **Canned phrasing:** More than one stock opener or transition, or one used to cover a missing argument? → What to Avoid
- **Uniform polish:** Is every paragraph equally worked? Equal polish everywhere is the loudest tell—leave a plain patch. → Sentence-Level Texture
