# Writing Style Examples

Annotated examples demonstrating key techniques. Split into two modes: **Educational/Technical** (the default for most posts) and **Personal Essays** (for opinion pieces and life topics).

---

## Educational/Technical Style

The teaching-first voice. Open on what happened, build mental models, use worked examples.

### Openings: Start With What Happened

**What broke:**
> Our p95 latency jumped from 140ms to 2.3s the week we added request logging. The logger serialized every response body before the handler returned, including the 4 MB ones.

*A real event with its numbers, told the way you'd tell a teammate. The number leads because the number is the news.*

**What you were trying to do:**
> I wanted to know whether prompt caching would help a support bot that answers 2,000 questions a day. The docs promised up to 90% off input tokens. Our first week saved 4%.

*Starts from the writer's real question. The gap between the promise and the result makes the reader curious, so no rhetorical question is needed.*

### Density: Write to Be Unsummarizable

**Fluffy → dense (cutting words surfaces a sharper idea):**

> *Before:* In this section, we're going to take a look at how caching actually works under the hood. It's important to understand that caching is a technique that can be useful in a lot of different situations. Essentially, the basic idea behind caching is that you store the results of expensive computations so you don't have to redo them later.

> *After:* Caching stores the result of an expensive computation so you never pay for it twice. That's the whole idea—the rest is deciding what counts as "the same computation."

*The "before" summarizes down to one sentence with no loss—proof it was mostly filler. The "after" can't be shortened without losing the punchline ("the rest is deciding what counts as the same computation"), and it's the shorter of the two. Density added an idea, it didn't just cut words.*

### Learning Objectives Block

**Near the top of a technical post:**
> By the end of this post, you'll understand:
> - How LLMs process text as tokens, not characters
> - Why attention is O(n²) and what that means for long contexts
> - When prompt caching helps (and when it doesn't)

*Specific outcomes. The reader knows what they're signing up for.*

### First Principles Building

**Define before you use:**
> A model never sees words. It sees tokens: chunks of text that it treats as single units. "unhappiness" might become two tokens, "un" and "happiness". The model then turns each token into a list of numbers called an embedding.

*Defines tokens before embeddings. The new term, "embedding", arrives at the end of the paragraph, where the next one picks it up. No "now that we understand" bridge is needed.*

**Layered explanation:**
> An embedding places a token at a point in a space with hundreds of dimensions. Tokens with similar meanings land near each other: "king" sits close to "queen" and far from "banana". The model learns those positions during training.

*Gives the mental model first. The last sentence names the next topic, training, so the reader knows where the piece goes.*

### Permission-Giving

**When it gets hard:**
> The attention math is the hardest part of this post, and you can skip it. You need one fact from it: when the model reads a token, attention lets it weigh every other token in the prompt to decide what that token means.

*Says the part is hard, gives permission to skip it, and hands over the one fact the rest of the post needs.*

**Telling the reader what they have:**
> You now have the whole forward pass: tokens in, embeddings, attention, and a prediction out. Everything after this section makes that pass cheaper.

*Names what the reader now holds in concrete terms instead of praising them or inventing a percentage.*

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

**Carry the reader from the last topic to the next:**
> Those token IDs are all the model ever sees. The next step turns each ID into a vector.

> So far we've assumed unlimited memory. A 70B-parameter model needs about 140 GB for its weights at 16-bit precision, so it doesn't fit on one 80 GB GPU.

*Each transition starts from what the reader just learned and ends on the next topic. It carries a fact, not a teaser like "this is where it gets interesting".*

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

## Clarity Lessons

Each lesson takes a weak draft, runs one test from "How to Write a Piece", and shows the revision. The drafts are what a first pass, human or model, usually produces. Copy the method, not the sentences.

### Lesson 1: One Paragraph Through Every Step

**Draft:**
> In today's world of distributed systems, observability is crucial. The implementation of structured logging across our services resulted in a significant reduction in the time required for incident investigation. There was a recognition by the team that the previous approach, which relied on free-text log lines, which were difficult to search, was a contributing factor to prolonged outages. It's worth noting that the adoption of a consistent schema was also key, ensuring that queries could be reused across services.

**Step 1, the three lines:**
- Situation: our March outage took six hours to diagnose, mostly spent grepping logs.
- Point: one shared log schema lets one query follow a request through every service.
- Reader's question: is the migration worth it?

**Step 4, the passes:**
- *Subjects:* "observability", "the implementation of structured logging", "a recognition", "the adoption of a consistent schema". All four are abstractions. The characters are hiding in the objects: we, the services, the logs.
- *Verbs:* implementation, reduction, investigation, recognition, and adoption are each an action with a doer. We implemented, we cut, we diagnosed, we realized, we adopted.
- *Order:* the draft opens sentences on new abstractions and ends them on vague phrases ("prolonged outages", "across services").
- *Sprawl:* "which relied… which were difficult" chains two clauses. "Ensuring that…" trails an abstract "-ing" phrase.

**Step 5, the cuts:** the throat-clearing first sentence, "significant" with no number, "it's worth noting", and "also key".

**Revision:**
> Our March outage took six hours to diagnose, and we spent most of those hours grepping free-text logs across eight services. Each service wrote its own format, so a search that matched an event on one service missed it on the next. We moved all eight to structured JSON logs that share one schema. Now one query follows a request through every service, and our last two incidents took under 40 minutes to diagnose.

*Every subject is a character: the outage, the services, we, one query. Each sentence starts from the end of the one before it ("eight services" → "Each service" → "all eight"). The paragraph ends on the result. The numbers replace "significant".*

### Lesson 2: Hold the Topic String

**Draft:**
> Cold starts were the main source of our p99 latency. A 400 ms penalty comes from loading JVM classes. Memory allocation also affects how long initialization takes. SnapStart was eventually adopted by the team, and the results were good.

**Test:** list the subjects. "Cold starts", "a 400 ms penalty", "memory allocation", "SnapStart", "the results". That's five subjects for four sentences, so the reader keeps changing what the paragraph is about.

**Revision:**
> Our Lambda functions missed their p99 target because of cold starts. Each cold function spent about 400 ms loading JVM classes, and functions with less memory took longer, because Lambda gives them less CPU. We turned on SnapStart, which restores each function from a snapshot taken after initialization. The functions' p99 dropped from 1.9 s to 420 ms.

*The functions are the character, so they hold the subject position. "The results were good" became a number.*

### Lesson 3: Old Before New

**Draft:**
> Write-ahead logging, an append-only record that Postgres flushes to disk before it changes a data page, is why a crash doesn't corrupt your tables.

**Test:** where does the new term appear? Here it's the first two words. The reader meets the jargon and its definition before learning why either matters.

**Revision:**
> A crash in the middle of a write doesn't corrupt your Postgres tables. Before Postgres changes a data page, it appends a record of the change to a file on disk. That file is the write-ahead log. On restart, Postgres replays it to redo every change the log recorded.

*It starts from what the reader cares about, a crash, and builds to the term. "That file" links back, and "the write-ahead log" lands at the end of its sentence, where new terms belong.*

### Lesson 4: End on the News

**Draft:**
> Shared backoff schedules can turn a short blip into a full outage, at least in our experience. We cut retry storms by adding jitter, which helped a lot. The fix took one line of code, surprisingly.

**Test:** read the last few words of each sentence: "in our experience", "helped a lot", "surprisingly". A hedge, a vague tag, and an aside sit where the reader expects the point.

**Revision:**
> In our experience, shared backoff schedules turn a short blip into a full outage. When we added jitter to the backoff, the retry storms stopped. The whole fix was one line.

*The hedge moved to the front, where it qualifies without stealing the ending. Each sentence now ends on its news.*

### Lesson 5: Section Openers That Make the Argument

**Draft, the first sentence of each section:**
1. In week one, we added Redis in front of the orders API.
2. In week two, we started reading the database's query log.
3. In week three, we found the N+1 query.

**Test:** read them alone. They make a diary, not an argument. The point doesn't arrive until the third section.

**Revision:**
1. The orders page was slow because of one N+1 query: one query for the order list, then one more per order for its items.
2. Redis hid the N+1 query for a week, because cached pages never reached the database.
3. One join replaced 51 queries, and the page now loads in 180 ms without the cache.

*Read alone, these three sentences carry the whole post. The weekly story can still appear inside each section as evidence.*

### Lesson 6: Cut Hedges, Pairs, and Talk About the Writing

**Draft:**
> It's worth noting that the new scheduler is fast and efficient, and it seems that it could possibly reduce costs somewhat. Clearly, this is a robust and reliable approach that completely eliminates each and every race condition.

**Test:** mark every word that doesn't carry a fact. "It's worth noting that" talks about the writing. "Fast and efficient" and "robust and reliable" are doubled pairs. "Seems… could possibly… somewhat" stacks three hedges on one claim. "Clearly" is an intensifier. "Completely" and "each and every" are implied by "eliminates" and "every".

**Revision:**
> The new scheduler eliminates every race condition we could reproduce. It will probably cut our compute bill, because it packs jobs onto fewer nodes, but we haven't measured that yet.

*One hedge, "probably", sits on the one claim we can't prove, and the reason comes with it. The certain claim gets no hedge, but it's scoped to what we tested.*

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
