# Writing Style Examples

Annotated examples demonstrating key techniques from actual blog posts.

## Opening Hooks

**Personal context + problem statement:**
> I've been curious about RAG (Retrieval-Augmented Generation) for a while. Reading about a technology and actually shipping it are very different. I wanted to feel the real friction—parsing, chunking, embeddings, latency, cost, quality—and see the upside. I like to think in trade-offs.

*Opens with personal motivation, then immediately frames the piece around trade-offs.*

**Autobiographical hook:**
> When I was a kid I was always hustling together some little scheme to make money - some of them skirted the edges of legality. One of my most profitable operations was running a loan sharking operation where I used my Christmas money to make loans to the tenants at my grandmother's boarding house and charged 25% interest.

*Specific, memorable, slightly provocative. Establishes credibility through experience.*

**Direct problem statement (technical):**
> My AI demos were failing in production. Not always—just enough to be frustrating. Users would get CORS errors, 504 timeouts, or watch the loading spinner run for 35 seconds before giving up.

*Immediately states the problem. No setup needed.*

**Personal stake + thesis:**
> I have two daughters. My oldest is 2, and the youngest is a newborn. They will remember none of what they have experienced so far throughout their life.

*Grounds the piece in lived experience before making the larger point.*

## Bold Claims with Backing

**Provocative statement → immediate explanation:**
> Most successful people do not set goals, they establish systems.
>
> **Example goal**: Lose 10 pounds
> **Example system**: Work out 4 days per week
>
> Notice that the example system looks a lot like a goal? Systems generally have an implicit goal, otherwise why waste the time. The distinction between a goal and a system is a goal is just a result whereas a system contains a strategy for achieving a result.

*Makes the bold claim, provides concrete examples, then explains the distinction.*

**Strong moral claim + backing:**
> **This system is evil, as it preys upon human nature to perpetuate its own existence.** You are bombarded with advertising every time you turn on your TV or go on the internet. Your inbox is filled with offers for exciting new ways to separate you from your money.

*Uses bold formatting for the claim, then stacks evidence.*

## Trade-off Analysis

**Explicit options with trade-offs:**
> Options for vector storage:
> * **Pinecone** (managed): ~$70/mo + network latency
> * **S3 + load at runtime**: $0 storage, but S3 latency (~100ms) per cold start
> * **Bundle with Lambda**: $0, lowest latency, simplest
>
> I chose **bundled embeddings**

*Lists options with costs/benefits, then states the choice.*

**Before/After with reasoning:**
> **Before:** $0.00/request (Gemini free tier)
> **After:** ~$0.01-0.02/request (OpenAI gpt-4o-mini)
>
> For a demo/portfolio site, this is negligible. More importantly, it's **reliable**. Users don't care that I saved $0.01 if the tool doesn't work.

*Shows the trade-off, then explains why the cost is worth it.*

## Personal Stakes & Credibility

**Declare what you do/have:**
> I have term life insurance. If I die prematurely, within the policy term my family gets a payout. I pay a monthly premium, and if I don't pass away within the term, there's no payout - a deal which I will take every single time.

*Personal stake makes the advice credible.*

**Reference your experience:**
> I've been integrating large language models (LLMs) into my coding workflow for quite some time now, and they've fundamentally transformed how I approach software engineering tasks.

*Establishes authority through practice, not credentials.*

## Quote Integration

**Block quote with commentary:**
> This fight club quote resonates with me:
> ```
> Man, I see in Fight Club the strongest and smartest men who've ever lived. I see all this potential, and I see it squandered...
> ```
>
> Ain't that the truth.

*Uses code block for longer quote, then adds personal reaction.*

**Inline thinker reference:**
> Warren Buffett once said "It's only when the tide goes out that you learn who's been swimming naked."

*Quick attribution, relevant quote, no over-explanation.*

## Technical Structure

**Table of contents for navigation:**
```markdown
- [Understanding the Capabilities (and Limitations) of LLMs](#understanding-the-capabilities)
- [Account for Training Cut-Off Dates](#training-cut-off)
- [Give Clear and Specific Instructions](#clear-instructions)
```

**"What I Learned" sections:**
> ## What I Learned
>
> 1. **"Simple + fast" beats "complex + fancy."** Bundled vectors are underrated for medium corpora.
> 2. **Data > model.** I spent more time on parsing and chunking than on embedding models—and it paid off.
> 3. **Costs can round to zero.** Free-tier Gemini + bundled vectors + serverless is a cheat code.

*Numbered, bold key insight, brief explanation.*

## Closings

**Elevated/aspirational:**
> In these early years, while they may not remember the specifics, they will carry the feeling, the unspoken message: *I am worthy, I am capable, I am loved.* And that is the voice I hope will guide them through life.

*Shifts to lyrical, uses italics for the key message.*

**Wry/punchy:**
> **Goals are short term. Systems last forever.**
>
> Or until you die.

*Strong statement, then undercuts with dark humor.*

**Practical call to action:**
> Financial independence is about freedom. Once your economic shackles have been ripped off, you're free to do what you want to do instead of what you have to do. You can still work and earn money, but it's on **your** terms.

*Restates the thesis, emphasizes freedom/agency.*

## Formatting Patterns

- **Bold** for key phrases and takeaways
- *Italics* for internal dialogue or emphasis
- `---` horizontal rules between major sections
- Headers for each main point in non-technical pieces
- Code blocks for technical examples with comments
- Bulleted lists for options/comparisons
- Numbered lists for sequences or ranked items
