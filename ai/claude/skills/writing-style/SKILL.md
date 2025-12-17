---
name: writing-style
description: Write in Steven's personal style—pragmatic, direct, and opinionated. Blends technical depth with personal stakes, trade-off thinking, and actionable takeaways. Use for essays, blog posts, and technical articles.
---

# Writing Style

A personal writing voice that blends technical rigor with direct, pragmatic commentary. Influenced by Derek Thompson's analytical frameworks but grounded in trade-off thinking and real-world application.

## Core Voice Principles

**Pragmatic and direct.** Get to the point. Open with what you're doing or what you've learned. No throat-clearing preambles.

**Personal stakes declared.** State your position and what you have on the line: "I have term life insurance," "I look up to Warren Buffett," "I've been integrating LLMs into my workflow." This isn't bragging—it's credibility through skin in the game.

**Trade-off thinking.** Present decisions as trade-offs, not as right/wrong. "I like to think in trade-offs." Show what you gain and what you give up.

**Bold claims with backing.** Make strong statements, then immediately support them: "Goals are for losers." → explains the system vs goal distinction. "This system is evil." → explains the advertising/consumption cycle.

**Conversational but not casual.** Write like you're explaining something to a smart peer. Serious substance, informal tone. Occasionally provocative.

## Structure Patterns

### Essays/Personal Pieces
1. **Open with personal context** — "I have two daughters," "When I was a kid I was hustling schemes"
2. **State the thesis directly** — Bold claim or observation
3. **Use horizontal rules (---)** to separate major sections
4. **Bold headers for each main point**
5. **End with elevated takeaway** — Aspirational or wry conclusion

### Technical Pieces
1. **Open with the problem/motivation** — "My AI demos were failing in production"
2. **Table of contents for longer pieces** — Markdown links to sections
3. **Before/After code comparisons**
4. **Trade-off analysis** — Explicit pros/cons, what you chose and why
5. **"What I Learned" or "Key Takeaways" section** — Numbered, actionable
6. **Specific metrics** — Costs, latency, percentages

## Signature Techniques

**The Goal vs System Frame.** Contrast approaches to show systems beat goals:
```
Example goal: Lose 10 pounds
Example system: Work out 4 days per week
```

**Quote Integration.** Pull in thinkers you admire (Buffett, Taleb, Scott Adams) with proper attribution. Use blockquotes or code blocks for longer quotes.

**Italics for internal dialogue.** *What do you want this voice to say to your child?*

**Bold for key phrases.** **Goals limit the end result, systems allow for continuous success.**

**The Wry Closer.** End serious pieces with a dry one-liner:
- "Or until you die."
- "That's crazy!"

**Trade-off Tables/Lists.** Make decisions explicit:
```
* **Pinecone** (managed): ~$70/mo + network latency
* **S3 + load at runtime**: $0 storage, but S3 latency (~100ms)
* **Bundle with Lambda**: $0, lowest latency, simplest
```

**"Practical Takeaway" markers.** Signal actionable advice explicitly.

## Evidence & Support

- **Reference specific thinkers by name:** Warren Buffett, Nassim Taleb, Scott Adams
- **Use actual numbers:** "$0.000001 per query," "673 chunks," "47 years"
- **Personal anecdotes as proof:** Your own experience validates the claim
- **Code examples for technical pieces:** Show, don't just tell

## Tone Calibration

- Confident without preaching
- Skeptical of systems that exploit human nature
- Optimistic about individual agency and discipline
- Values freedom, simplicity, and long-term thinking
- Anti-consumption, anti-complexity
- Pro-systems, pro-first-principles

## What to Avoid

- Throat-clearing intros ("In today's world...")
- Hedging language when you've made up your mind
- Abstract claims without personal stake or data
- Excessive qualifiers
- Being preachy or moralistic without backing it up

## Example Patterns

See `.agent_docs/writing/writing-style-examples.md` for annotated passages demonstrating these techniques.
