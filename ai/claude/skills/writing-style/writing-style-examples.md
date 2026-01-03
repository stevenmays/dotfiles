# Writing Style Examples

Annotated examples demonstrating key techniques. Split into two modes: **Educational/Technical** (the default for most posts) and **Personal Essays** (for opinion pieces and life topics).

---

## Educational/Technical Style

The teaching-first voice. Hook with a measurable claim, build mental models, use worked examples.

### Measurable Hooks with "How?"

**Number + question:**
> Prompt caching can cut your LLM costs by 10x. But how does it actually work? What's being cached, and why does it only help sometimes?

*States the payoff, then immediately asks what the reader is thinking.*

**Latency hook:**
> This change dropped our p95 from 2.3s to 140ms. The mechanism isn't obvious—it's not about faster hardware or better algorithms. It's about what we stopped computing.

*Concrete numbers, then invites curiosity about the "why."*

### Learning Objectives Block

**Near the top of a technical post:**
> By the end of this post, you'll understand:
> - How LLMs process text as tokens, not characters
> - Why attention is O(n²) and what that means for long contexts
> - When prompt caching helps (and when it doesn't)

*Specific outcomes. The reader knows what they're signing up for.*

### First Principles Building

**Define before you use:**
> Before we talk about embeddings, we need to understand tokens. A token isn't a word—it's a chunk of text that the model treats as a single unit. "unhappiness" might be three tokens: "un", "happiness", and potentially a space.
>
> Now that we understand tokens, we can talk about what the model does with them.

*Builds the concept, then explicitly transitions.*

**Layered explanation:**
> An embedding is just a list of numbers—a position in high-dimensional space. Similar words end up near each other. "king" and "queen" are close. "king" and "banana" are far apart.
>
> That's the intuition. Now let's see how it's computed.

*Gives the mental model first, then goes deeper.*

### Permission-Giving

**When it gets hard:**
> This is the most abstract part of the whole system. The math looks intimidating, but you don't need to fully understand matrix multiplication to get the key insight. Here's what matters: attention lets the model look at all the other tokens when deciding what a token means.

*Acknowledges difficulty, gives permission to skim, extracts the core insight.*

**Encouraging the reader:**
> If you've followed along this far, you already understand 80% of how transformers work. The remaining 20% is optimization tricks.

*Validates progress, reduces intimidation.*

### Worked Micro-Examples

**Threading one example through:**
> Let's use a tiny example: "The cat sat."
>
> First, tokenization: `["The", " cat", " sat", "."]` → `[464, 3797, 3332, 13]`
>
> Next, embeddings. Each token ID maps to a vector. Token 464 ("The") becomes `[0.12, -0.34, 0.56, ...]`—a point in 768-dimensional space.
>
> Now attention. When processing "sat", the model looks back at "The" and "cat" to understand context...

*Same tokens, same sentence, carried through each concept.*

### Pseudocode Before Real Code

**Lower the barrier:**
> Here's the attention mechanism in pseudocode:
> ```
> for each token in sequence:
>     look at all previous tokens
>     compute relevance score for each
>     weighted average = new representation
> ```
>
> In PyTorch, this becomes:
> ```python
> scores = query @ key.T / sqrt(d_k)
> weights = softmax(scores)
> output = weights @ value
> ```

*Plain language first, real code second.*

### "In Summary" Compressions

**End-of-post compression:**
> **In summary:** Prompt caching works by storing the computed key-value pairs from your prompt. When you send a new request with the same prefix, the model skips recomputing those pairs and starts from the cached state. This saves compute (and money) proportional to how much of your prompt stays constant. It doesn't help if your prompts vary significantly, and it requires the provider to support it.

*One paragraph that captures the whole mechanism. If you only read this, you'd still get it.*

### Orienting Transitions

**Tell the reader where you are:**
> That's tokenization. Now let's see what happens to these token IDs.

> We've covered the forward pass. But training is where it gets interesting.

> So far we've assumed unlimited memory. In practice, there's a constraint.

*Short, explicit, moves the reader forward.*

### Honest Uncertainty

**When you don't know:**
> We don't really know what's encoded in each dimension of the embedding. Researchers have found that some dimensions correlate with concepts like "royalty" or "gender," but most are uninterpretable. What we do know is that the geometry works—similar meanings cluster together.

*States the unknown plainly, then says what's still useful.*

**Deferring to better sources:**
> I won't go deep on backpropagation here—Andrej Karpathy's "micrograd" video does it better than I could. What matters for our purposes is...

*Links out instead of doing a worse job.*

### Trade-off Tables (Technical)

**Comparing approaches:**
> | Approach | Latency | Cost | Complexity |
> |----------|---------|------|------------|
> | Recompute every request | High | High | Low |
> | Cache full responses | Low | Low | High (invalidation) |
> | Cache KV pairs (prompt caching) | Medium | Medium | Medium |
>
> We're using KV caching because our prompts share a long system message but vary in user input.

*Shows the landscape, then picks a side with reasoning.*

---

## Personal Essay Style

For opinion pieces, life topics, and posts where personal stakes drive the argument. Personal experience establishes credibility. Trade-off thinking still applies. Wry closers are allowed here.

### Opening Hooks

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

### Bold Claims with Backing

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

### Trade-off Analysis

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

### Personal Stakes & Credibility

**Declare what you do/have:**
> I have term life insurance. If I die prematurely, within the policy term my family gets a payout. I pay a monthly premium, and if I don't pass away within the term, there's no payout - a deal which I will take every single time.

*Personal stake makes the advice credible.*

**Reference your experience:**
> I've been integrating large language models (LLMs) into my coding workflow for quite some time now, and they've fundamentally transformed how I approach software engineering tasks.

*Establishes authority through practice, not credentials.*

### Quote Integration

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

### Technical Structure

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

### Closings

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

### Formatting Patterns

- **Bold** for key phrases and takeaways
- *Italics* for internal dialogue or emphasis
- `---` horizontal rules between major sections
- Headers for each main point in non-technical pieces
- Code blocks for technical examples with comments
- Bulleted lists for options/comparisons
- Numbered lists for sequences or ranked items
