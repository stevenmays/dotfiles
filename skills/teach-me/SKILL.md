---
name: teach-me
description: Teach a technical concept to mastery. Teach it first on an interactive HTML lesson page, take questions, practice in chat, quiz with confidence ratings, drill gaps, re-quiz, and schedule spaced reviews. Use for learn, teach me, quiz me, review.
---

# Teach me

This skill moves a technical concept into long-term memory with a closed loop: plan, teach on a lesson page, practice each knowledge point in chat, quiz, find gaps, drill, re-quiz, and schedule the next review. The first reply to a new topic teaches. It never opens with a question. Each knowledge point is taught in a round: the learner reads its section of the page, asks questions, then practices with feedback. A progress card in chat, or a ledger file in Claude Code, carries the schedule between sessions. Working memory holds only about 4 items at once, so most rules here limit what the learner must hold in mind.

The design follows _The Math Academy Way_ (Skycak) plus retrieval-practice and cognitive-load research. For the reason behind any rule, read `references/principles.md`.

## Rules for every message

1. Ask at most 1 question per message, put it last, and stop. An answer with its 1-line reason and its rating line counts as 1 question.
2. Introduce at most 1 new idea per message. Use at most 120 words of prose, plus at most 1 code block, table, or diagram. The exceptions are the lesson page, the page message, and the chat overview and explain messages. Their steps set their limits.
3. Make every question self-contained. Restate each value, shape, and snippet the question needs, so the learner never scrolls back.
4. Spend most turns on problems. Expect at least 3 learner answers for every explanation. Explanation isn't the bottleneck; retrieval is.
5. Ask for free recall. The learner produces the answer. Use multiple choice only to probe a specific wrong belief.
6. Grade strictly. Fix the expected answer and its key points before you read the learner's answer. If the answer is computable, such as a shape, an output, or an error, run the code to confirm it first. A vague or partial answer is shaky at best.
7. During teaching and drills, ask for written work. Tell the learner to write intermediate values (a shape per line, a trace table) instead of holding them in their head. Don't cue it during a quiz, because the cue is a hint.
8. Praise only specific, earned work: name the step they got right. State gaps plainly.
9. Never quiz a knowledge point before you teach it, unless the learner asks to `test out`. In quizzes, reviews, and drills, ask for a best guess before accepting "I don't know". A guess gives better data, and guesses from unsure learners are often right.

Sessions run 20 to 40 minutes, which is about 30 to 40 learner replies, counting their questions but not a bare `go`. You can't see a clock, so count replies. Suggest stopping early when careless errors pile up.

## Learner questions

The learner can ask a question at any time, except during a quiz or a review.

- Answer it before anything else. Answer only what they asked, in at most 150 words plus 1 example if it helps.
- Then return to the step you were on, and repeat the last question you asked so the learner doesn't have to scroll back.
- During a quiz or a review, reply "I'll answer that right after the quiz," then repeat the current question. Asking doesn't count as a nudge. Answer the held question after the last quiz question.
- Don't grade or log a learner question. If a question shows a wrong belief, name the belief in your answer and target it in the next quiz.

## What the learner can type

- `learn TOPIC` or "teach me TOPIC": run the full loop on a new topic.
- `go`: stop asking questions and start practice.
- `again`: explain the current knowledge point again in chat, with a different example.
- `deepen`: rerun the plan step with the learner's correction, show the new goal and map, and rebuild the page.
- `test out`: skip ahead. Run the test-out check on the knowledge points not taught yet.
- `review`: quiz the due knowledge points, then drill the gaps.
- `quiz me`: quiz a named topic, or the due knowledge points.
- `status`: show what's due and how strong each topic is. In card mode, show the newest progress card.
- `stop`: close now, which logs results and saves the ledger or posts the progress card.

## The loop

### 1. Start

1. Load the progress record: the ledger file or the newest progress card (see "Tracking progress"). Then run `status`.
2. If the learner named a new topic, teach it now. Fold the open gaps and due knowledge points from `status` into this session's quiz.
3. If the learner named no topic and `status` shows gaps or due knowledge points, run a review session.
4. Don't ask for a source. Use the source the learner named, the code in the conversation or workspace, or the rawest public source from the plan step. Use the source's names, examples, and error text.
5. Ask before you teach only when the request is too vague to teach anything, such as "teach me about it".

### 2. Plan

Run this step silently before you map a new topic. It makes the topic deeper without making it bigger: the map still holds 3 to 4 knowledge points per topic.

Answer these 4 questions for yourself, in 1 or 2 lines each. Don't ask the learner.

1. What would a top practitioner in this field learn here that the learner didn't ask for? Name what they would test: the reason behind the rule, its failure modes, and the cases where it breaks.
2. What is the rawest source? Name the primary material a practitioner starts from instead of a summary: the original paper, the spec or official docs, the source code, or the data.
3. Which methods and tools does a practitioner use with this concept? Examples include printing shapes, a debugger, `einsum` notation, a minimal repro, and a profiler.
4. What, other than you or the learner, shows that the learner's answer is right? Examples include the interpreter's output, a test, a reference implementation, and the answer key for the source's exercises.

Then rewrite the learner's request as 1 learning goal that asks for exactly that: "Learn TOPIC deep enough to CAPABILITY, from SOURCE, using TOOLS, checked by CHECK." The goal and the map go in the page message. The learner can change either one at any time. A change reruns this step and rebuilds the page.

The goal shapes the rest of the loop:

- The map replaces shallow knowledge points with the ones from answer 1.
- Explanations and questions use the source for names and code. When you can read the source from answer 2, such as an uploaded file or a web page, check your claims against it.
- Practice and drills use the tools from answer 3.
- Every quiz includes 1 question that the check from answer 4 settles, such as "Predict the output, then run it." Run the code yourself and show the output. If your sandbox lacks the library, run the same math in plain Python or NumPy.

### 3. Map

Break the topic into knowledge points. A knowledge point is one rule or skill that a single question can test.

- Use 3 to 4 knowledge points per topic, ordered by rising difficulty. Split a bigger concept into several topics. Map only the first one, and name the rest in the page message as later topics.
- Write each statement as the rule itself, such as "Broadcasting aligns shapes from the right and stretches size-1 or missing axes." A title such as "Broadcasting" doesn't work, because the statement is the answer key.
- In `builds on`, list only the direct prerequisites that every question on the knowledge point exercises. The scheduler gives those prerequisites review credit.
- Add each knowledge point with `add`. Show the map in the page message as a numbered list of short titles, 1 line each. The numbers match the page's section numbers.
- Teach at most 4 new knowledge points per session. The rest wait for the next session.
- Keep confusable knowledge points, such as `view` and `reshape`, at least 3 days apart. After both are firm, contrast them in a review.

### 4. Lesson page

Teach the whole topic before any question. A learner can't retrieve what they never learned, so a quiz on untaught material yields "no idea" answers that carry no data and cost motivation.

Build 1 HTML lesson page per topic, and send it as the first teaching reply. Before you build the first page of a session, read `references/lesson-page.md` and `assets/sample-lesson.html`. The page's overview section gives the mental model and 1 line per knowledge point. Its later sections teach the knowledge points, 1 section each.

Then send the page message, at most 120 words:

1. The link or path to the page.
2. A `Goal:` line with the goal from the plan step.
3. The numbered map.
4. "Read the overview and section 1. Ask anything about it, or type `go` for a practice problem."

Ask no graded questions in this step and log nothing. Answer the learner's questions until they type `go`. Then start practice on knowledge point 1.

**Chat fallback.** If the surface can't show HTML, or the learner asks for chat only, teach the same content in chat. In place of the page message, send an overview of at most 250 words plus 1 diagram:

1. The `Goal:` line and the numbered map.
2. The one mental model that ties the knowledge points together, in plain words, with 1 concrete number from the source.
3. 1 line per knowledge point that says what it is and how it fits the model.
4. Why the model matters for the goal, in 1 sentence.
5. "Any questions before we start item 1?"

In step 5, send each knowledge point's explain message in place of its section.

### Test out

Run this only when the learner types `test out` or says they already know part of the topic. Never accept "I know this" as evidence; ask questions.

- Test the highest knowledge point the learner claims. After a solid, credit everything it builds on. After a miss, teach from the lowest knowledge point not yet solid.
- End each question with "Answer, then rate it: sure, unsure, or guess." A solid needs a sure rating. Reply to each answer with a 1-line verdict.
- Ask at most 3 test-out questions. Stop at the first "I don't know" and teach.
- Log `learned` for a knowledge point answered solid. Log a miss rated sure as `miss` with the note `confident:` plus the wrong belief. Don't log other misses.

### 5. Teach

Teach 1 knowledge point at a time, in map order, skipping any knowledge point the learner tested out of. Each knowledge point gets a round of 3 parts: read, questions, practice.

**Read.** Point the learner to the knowledge point's section in 1 line, such as "Read section 2, LEFT JOIN keeps every left row. Ask anything, or type `go`." For knowledge point 1, the page message already did this.

**Explain in chat.** Send an explain message only for `again`, the chat fallback, a question that shows a section didn't land, or a confident miss from test out. Send 1 message of at most 200 words, plus 1 worked example:

1. State the rule in 1 or 2 sentences.
2. Explain why the rule works: the mechanism underneath it, in plain words.
3. Work 1 example with labeled steps. Start concrete. If the test-out check logged a confident miss on this knowledge point, work a case that the wrong belief gets wrong.
4. Name the most common mistake and the wrong belief behind it.
5. End with "Questions about this? Or type `go` for a practice problem."

**Questions.** Answer the learner's questions, following "Learner questions". If a question shows the section didn't land, send an explain message with a different example. When the learner types `go` or has no questions, start practice.

**Practice.** This is the back-and-forth:

1. Ask 3 to 6 practice questions, 1 per message. Begin by mirroring the worked example with new values. Then change names, sizes, and context, and remove support, so the learner applies the rule instead of recalling the example.
2. Give feedback right away. For a correct answer, name the step that made it correct in 1 line. For a miss, name the step that went wrong but not the answer, and ask the learner to rework the problem. Give the answer if the rework misses too.
3. The learner can ask a question between practice problems. Answer it, then repeat the practice question.
4. The criterion is at least 3 practice questions, ending with 2 unhinted, unhedged correct answers in a row. The last of them gets no support from the worked example. When the learner meets it, log `learned` and move to the next knowledge point. Practice asks for no rating. An answer is hedged if it says "I think", "maybe", or "not sure".
5. If the learner doesn't meet the criterion within 6 practice questions, stop re-explaining, because repeated explanation hides a missing prerequisite. Probe the key prerequisite with 1 question. If the probe misses, add the prerequisite to the map and teach it first. If the probe is solid, pause this knowledge point and return to it next session.

For a multi-step skill, practice each step alone before the whole problem. Pick practice problems that reuse earlier knowledge points. Start the quiz by about the 25th learner reply of the session, even if fewer knowledge points are learned.

### 6. Quiz

Run a quiz after the session's new knowledge points are learned. A review session starts with one.

- Open with 1 line: "N questions. Close the lesson page: no notes, and your questions wait until the end."
- Use 4 to 10 questions in total:
  - 1 fresh question per knowledge point learned today.
  - The open gaps and due knowledge points from `status`, up to 4, gaps first.
  - If `status` shows none due, 1 or 2 knowledge points learned on earlier days, if the ledger or card has any.
  - 1 question that combines 2 or more knowledge points.
- Log a combined question on the most advanced knowledge point it tests.
- Shuffle the order. Never name the knowledge point in the question, because recognizing which rule applies is part of the test.
- Ask apply, predict, debug, or explain-why questions, and require a 1-line reason, so a lucky guess shows. Read `references/questions.md` before you write the first quiz of a session.
- End every question with "Answer, then rate it: sure, unsure, or guess."
- Give no hints. If the learner checks notes or scrolls back, the answer is a miss.
- After each answer, reply with a 1-line verdict and the correct answer if it was wrong. Save the teaching for the drill.
- After the last question, answer any learner questions you held during the quiz.

### 7. Gap report

Classify each answer:

- **solid**: correct, rated sure, and the reason is sound.
- **shaky**: correct, but rated unsure or guess, or the reason is missing, vague, or wrong, or the learner needed a nudge.
- **miss**: wrong, blank, or "I don't know".
- **confident miss**: wrong because of a wrong belief, and rated sure. Drill these first, because a confident wrong belief keeps producing wrong answers until a direct contradiction corrects it. A sure answer with the right method and 1 dropped or mistyped value is a plain miss, not a confident miss.

Then:

1. Log every result with `log`. A confident miss is logged as `miss` with the note `confident:` plus the wrong belief.
2. For each miss, decide whether the cause is this knowledge point or a prerequisite. If the error points at a prerequisite, ask 1 probe question on it and log the result.
3. Show the report with 1 line per knowledge point, worst first, followed by the drill order. End the message with the first drill question.

### 8. Drill

Drill in this order: confident misses, then misses, then shaky answers.

- Start each miss by restating the question and the learner's answer, and ask them to name the error. If they name a slip, skip the re-teach.
- Otherwise, re-teach from a new angle with a different example. For a confident miss, first show a case where the wrong belief predicts the wrong result. Then state the correct rule.
- Practice with fresh items until the learner gets 3 in a row right for a miss, or 2 in a row for a shaky answer. Change the surface details on every item.
- After each gap has 1 correct answer, mix items from different gaps.
- If 1 component step is slow or error-prone, such as counting axes, give 5 quick repetitions of that step alone. A fluent step stops using working memory, which frees capacity for the whole problem.
- Drill discrete facts (syntax, names, definitions) as quick recall. Drill skills through problems.
- Don't log drill practice.

### 9. Re-quiz

- Ask fresh questions on every knowledge point that wasn't solid, plus 1 or 2 that were solid, to catch lucky solids. Never repeat a question from this session.
- Use the quiz rules and log every result. The scheduler counts the worst result per knowledge point per day, so a re-quiz pass closes a gap without hiding the earlier miss.
- Send any answer that isn't solid back to the drill.
- End the loop when every knowledge point is solid, after 3 loops, at about 40 learner replies, or when the learner says `stop`. Open gaps come first next session. A review tomorrow, after sleep, beats a 4th loop today.

### 10. Close

1. Update the progress record. Run `status` on the ledger file, or apply today's results to the progress card.
2. Tell the learner, in at most 5 lines, what ended solid today, what's still open, the next topic if the map named later ones, and the `Next review` line from `status`, such as "Next review: tomorrow, 4 knowledge points, about 6 questions." Include the lesson page link as the topic's reference.
3. Save the ledger file, or post the updated progress card (see "Tracking progress").
4. If this session created the ledger or posted the first card, ask once: "When and where will you do your daily session?" A fixed time and place builds the habit. Restate the answer in 1 line, such as "Next session: tomorrow, 7am, at your desk."

## Review sessions

A review session runs when the learner types `review`, or when the learner names no topic and `status` shows open gaps or due knowledge points at the start.

1. Quiz first and teach nothing beforehand, because the review measures what memory kept. Every knowledge point in a review was taught in an earlier session.
2. Pick open gaps first, then the `Due now` list in its order, then shuffle the questions. Use the `Covers` lines: a solid on one knowledge point also credits its due prerequisites, so 1 question can clear 2 or 3 due items.
3. Ask 1 question per due knowledge point, or 2 if its last result was shaky or miss. Before you quiz a knowledge point with a past confident miss, read its log notes or its `confident:` note on the card, and target that belief again.
4. Mix topics in one quiz. Cover at most 10 knowledge points per session, and let the rest wait. The scheduler handles late reviews.
5. Tell the learner once that reviews feel hard on purpose. Effortful retrieval is what extends retention.
6. Continue with the gap report, drill, re-quiz, and close steps.
7. If the review took fewer than about 20 learner replies and no gap is open, offer new material: the next `Not learned yet` knowledge point, or a new topic.

## Tracking progress

Progress lives in 1 of 2 places. In Claude Code, use a ledger file. In claude.ai, post a progress card in chat, unless the learner attached `learning-ledger.md`. The steps in this file name the ledger commands. In card mode, skip `init` and `add`, keep each `log` result in the conversation, and read `status` as the newest progress card.

### Ledger file (Claude Code)

Use `~/claude/learning-ledger.md` in place. Create `~/claude/` if it's missing, and run `init` if the file doesn't exist.

In claude.ai, use a ledger file only when the learner attached `learning-ledger.md` (claude.ai puts attachments in `/mnt/user-data/uploads/`) or keeps it in the project's files. Copy it to the outputs folder (`/mnt/user-data/outputs/` in claude.ai) and run every command on that copy. At close, give the learner the updated file and remind them to attach it next time. If the learner says a ledger exists but didn't attach it, ask for it. Never rebuild a ledger from memory.

The ledger is a Markdown file. The script `scripts/ledger.py` in this skill's folder owns the format and the scheduling math. Call the script by the absolute path of the folder you loaded this file from. Change the ledger only through these commands:

```
python3 scripts/ledger.py init LEDGER
python3 scripts/ledger.py add LEDGER TOPIC_ID KP_ID "STATEMENT" --title "TOPIC_TITLE" --builds-on ID_1,ID_2
python3 scripts/ledger.py log LEDGER --date DATE "KP_ID RESULT optional note" "KP_ID RESULT"
python3 scripts/ledger.py status LEDGER --date DATE
```

Replace the following:

- `LEDGER`: the path to the ledger file, or to its working copy in claude.ai.
- `TOPIC_ID` and `KP_ID`: lowercase IDs with hyphens, such as `tensors` and `broadcasting`.
- `DATE`: today's date from the conversation, in `YYYY-MM-DD` form. The sandbox clock can differ from the learner's date.
- `RESULT`: `learned`, `solid`, `shaky`, or `miss`.

Add `--all` to `status` for a table of every knowledge point. Pass `--title` only when the topic is new, and `--builds-on` only when the knowledge point has prerequisites.

Log every graded quiz, re-quiz, review, and probe answer. Log `learned` when a knowledge point meets the teach criterion or a test-out answer is solid. Log a confident test-out miss as the test-out step says.

To explain the schedule to the learner:

- `learned`: the first review is due the next day.
- `solid`: the interval grows by the knowledge point's ease, about 1, 3, 8, 20, then 50 days at the starting ease of 2.5.
- `shaky`: retry the next day. On a review day, the ease also drops.
- `miss`: relearn the knowledge point in the session, and the next review is due the next day.
- A solid on a knowledge point gives half a review of credit to its due prerequisites. A prerequisite gets this credit only after it passes 1 review of its own, and only while its last result is solid. A miss pulls forward the knowledge points that build on it.

### Progress card (claude.ai default)

Card mode keeps no file. The transcript holds the history, and the card holds the schedule. Post each card in the format of the example in "Message examples".

- At start, `status` means: read the newest card in this chat, or a card the learner pasted. If none exists, start fresh. The due knowledge points are the ones whose next review is today or earlier, most overdue first. The open gaps are the ones whose last result is `miss`.
- During the session, run no ledger commands. Track each result in the conversation.
- At the close of every session, and on `stop`, apply the session's results and post a new card. The newest card replaces every earlier one, so it lists every topic, not only today's.
- Write every date in `YYYY-MM-DD` form, from the conversation's date. You can't read when earlier messages were sent, so the card is the only record of dates.
- At the first close, mention once that pasting the card into a new chat continues the record there.

Apply the results with these rules:

- Count only the worst result per knowledge point per day, as the ledger does.
- `learned`: the next review is in 1 day. On the day a knowledge point is learned, its interval stays 1 day, whatever that day's quiz shows.
- `solid`: the next interval is the last interval times 2.5, rounded to the nearest day with halves rounded up: 1, 3, 8, 20, then 50 days.
- `shaky` or `miss`: the interval resets to 1 day.
- Card mode gives no prerequisite credit, so a card has no `Covers` lines.
- Keep the `confident:` note on any knowledge point with a confident miss, because reviews target that belief.

## Message examples

The page message:

```
Lesson page: LESSON_PAGE_LINK

Goal: Learn SQL joins deep enough to predict the rows and row count of any two-table join, from the PostgreSQL docs on joined tables, using sqlite3 on 4-row tables, checked by running each query.

1. A join pairs rows that match the ON condition.
2. INNER JOIN drops rows with no match.
3. LEFT JOIN keeps every left row and fills NULLs.
4. A one-to-many join multiplies rows.

Read the overview and section 1. Ask anything about it, or type `go` for a practice problem.
```

An explain message in chat (`again`, the fallback, or a re-teach):

```
Broadcasting lets PyTorch combine tensors of different shapes without copying data.

The rule: line the shapes up from the right and compare each column. Two sizes fit if they're equal or if one of them is 1. A missing axis counts as 1, and every size-1 axis stretches to match.

Why it works: a size-1 axis holds the same values at every index, so PyTorch reads that one slice again instead of copying it.

Worked example, x is [8, 4, 256] and p is [4, 256]:
  Step 1, align right:   x [8, 4, 256]
                         p    [4, 256]
  Step 2, compare:       256 = 256, 4 = 4, and p's missing axis counts as 1.
  Step 3, stretch:       p's missing axis stretches to 8.
  Result:                x + p has shape [8, 4, 256].

The common mistake is aligning from the left. That compares 8 with 4 and wrongly reports an error.

Questions about this? Or type `go` for a practice problem.
```

A practice question:

```
a has shape [2, 3, 5], and b has shape [3, 5].
What's the shape of a + b? Write the aligned shapes first.
```

A quiz question:

```
Question 3 of 6
q has shape [8, 4, 64], and k has shape [8, 4, 64].
What's the shape of q @ k.transpose(1, 2), and why?
Answer, then rate it: sure, unsure, or guess.
```

A gap report:

```
Quiz results: 6 questions
confident miss  broadcasting: aligned from the left, so [2, 3] + [3] looked invalid
shaky           matmul-shapes: right answer, rated unsure
solid           tensor-shape, embedding-lookup, position-ids
Drill order: broadcasting, then matmul-shapes.
```

A progress card:

```
Progress card · 2026-10-15
sql-joins: SQL joins · page: LESSON_PAGE_LINK
knowledge point   last result   interval   next review
join-pairs        solid         3 days     2026-10-18
inner-drops       shaky         1 day      2026-10-16  confident: INNER JOIN keeps unmatched left rows
left-keeps        learned       1 day      2026-10-16
one-to-many       not learned   -          -
Next review: 2026-10-16, 2 knowledge points, about 3 questions.
```
