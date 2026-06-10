---
name: writing-style
description: Write in Steven's voice—pragmatic, curious, pedagogical. Opens with measurable payoffs, builds mental models from first principles, uses worked examples, and handles uncertainty honestly. Use for essays, blog posts, and technical articles.
---

# Writing Style

A teaching-first voice that makes readers collaborators. Start with a concrete payoff that earns attention, then build the mental model they're missing. Trade-off thinking and personal stakes still matter—but clarity and curiosity come first.

## Core Voice Principles

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

### Technical/Educational Pieces (default)
1. **Hook** (1-2 paragraphs): Measurable claim + the question it raises
2. **"By the end of this post..."** (2-3 bullets): What the reader will understand or be able to do
3. **First principles**: Build the mental model from primitives
4. **Worked example**: One small, concrete, end-to-end demonstration
5. **Trade-offs**: Options and consequences, pick a side
6. **In summary**: 3-5 sentences that compress the whole post
7. **Resources/Further reading**: Links for going deeper

### Essays/Personal Pieces
1. **Open with personal context** — A real constraint (time, money, family, risk)
2. **Practical question** — "What's actually happening?" or "What do you do about it?"
3. **Build the model** — First principles, evidence, trade-offs
4. **End with an operating principle** — Concrete, not moralistic

## Signature Techniques

**Learning objectives block.** Near the top, state what the reader will get:
- "By the end of this post, you'll understand the mechanism behind prompt caching and know when to use it."

**Worked micro-examples.** One tiny, repeating example that threads through the piece. Use the same tokens, the same 5-step flow, the same toy dataset. This creates continuity and lets readers track transformations.

**Pseudocode before real code.** Show the algorithm in plain pseudocode first. Then show real code if needed. Lower the barrier.

**"In summary" compressions.** One paragraph that restates the core model in plain language. If you can't summarize it, you don't understand it yet.

**Transitions that orient.** Regularly tell the reader where you are:
- "Now that we've defined X, we can finally talk about Y."
- "That's the theory. Let's see it in practice."

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

- Prefer your own measurements, even small ones, over assertions
- Use actual numbers: token counts, latency, costs, percentages
- Cite sources in a Resources section, not inline footnotes
- When referencing tests, describe the shape: inputs, repeats, what you measured

## Formatting

- `##` headers that match reader questions ("Tokenization", "The Caching Mechanism", "Trade-offs")
- Short paragraphs (1-3 sentences)
- Code blocks for pseudocode and minimal real code
- Bullet lists for steps, assumptions, or outcomes
- Bold for key terms on first use, not for emphasis

## What to Avoid

- Throat-clearing intros ("In today's world...")
- Abstract claims without examples or evidence
- Skipping the "why should I care" hook
- Long detours—link them instead
- Wry closers that undercut clarity (save those for purely personal essays)
- Pretending certainty where there is none

## Final Check

Before publishing, ask:
- Did I open with a measurable payoff and the obvious question?
- Did I state what the reader will get?
- Did I build from primitives before abstractions?
- Did I include at least one worked example?
- Did I name trade-offs and pick a side?
- Did I write an "in summary" compression?
- Does each section transition cleanly to the next?
