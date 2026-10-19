# Question design

Read this before you write the first quiz of a session. A good question makes the learner produce an answer you can check, and its reason shows whether a correct answer was luck.

## Question types

The following types work for technical concepts:

| Type        | Prompt shape                                    | Example                                                                                        |
| ----------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Predict     | What does this print, return, or produce?       | "`x` is `[8, 4, 256]` and `p` is `[4, 256]`. What's the shape of `x + p`?"                     |
| Explain why | Why does this happen? Answer in 1 line.         | "Why does `nn.Embedding` reject a `float` tensor of IDs?"                                      |
| Debug       | This fails with ERROR. Why, and what's the fix? | "`a @ b` raises `RuntimeError: mat1 and mat2 shapes cannot be multiplied (4x3 and 4x3)`. Why?" |
| Produce     | Write the 1 line that does X.                   | "Write the call that builds position IDs for a context of 6 tokens."                           |
| Reverse     | The output is Y. What input produced it?        | "The result has shape `[8, 4, 4]`. What shapes could `q` and `k` have had?"                    |
| Choose      | Which rule applies here, A or B, and why?       | "Do you need `view` or `reshape` after this `transpose`?"                                      |
| Transfer    | Same rule, new setting.                         | "Broadcasting in NumPy: what's the shape of `[3, 1] + [1, 5]`?"                                |
| Estimate    | About how big is X?                             | "About how many trainable floats does `nn.Embedding(50257, 768)` hold?"                        |
| Recall      | State the rule or fact.                         | "Which side do shapes align from when PyTorch broadcasts?"                                     |

Use Recall only for discrete facts such as syntax, names, and definitions. Use Choose only after both options are firm, because it trains the learner to tell them apart.

## Types by phase

- Test out: Predict, with the simplest question that exercises every prerequisite of the knowledge point. Run it only when the learner asks to test out.
- Teach: Predict or Produce. Mirror the worked example first, then change the surface details.
- Quiz and review: Predict, Debug, Explain why, and Choose. Require a 1-line reason. Include 1 question that combines 2 or more knowledge points, and 1 question that the goal's check settles, such as "Predict the output, then run it."
- Drill: start with the type the learner missed, then switch to a different type on the same knowledge point.
- After a knowledge point is firm: Transfer and Reverse, which test whether the learner holds the rule or only the example.

## Rules for writing a question

- Make it self-contained. Include every value, shape, and line of code the learner needs.
- Give it 1 checkable answer: a shape, an output, a line of code, or a 1-sentence reason.
- Change the surface details every time: names, sizes, numbers, and setting. The learner must apply the rule, not recall the last answer. Never repeat a question within a session.
- Avoid the easiest variant, which gives false credit, and the hardest variant, which invites silly mistakes.
- Use small numbers unless arithmetic is the skill, so arithmetic doesn't use up working memory.
- Keep code snippets to at most 8 lines.
- Use real API names and real error text from the learner's source.
- For multiple choice, make each wrong option a specific wrong belief, and still ask for the reason. Give every option the same length and form, and vary the correct option's position, so the format gives no clue.

## Grading

Before you read the learner's answer, fix 3 things:

1. The expected answer. If it's computable, run the code to confirm it.
2. The 1 or 2 key points that a correct reason must contain.
3. The likely wrong answers, and the wrong belief behind each one.

Then classify the answer as solid, shaky, miss, or confident miss, using the definitions in `SKILL.md`. These cases come up often:

- Right answer with a wrong reason: shaky. Drill the reason.
- Right answer in different but equivalent notation: solid.
- Right method with an arithmetic or typing slip: miss, without a `confident:` note, because no wrong belief caused it. Silly mistakes often hide a gap. If the learner names the slip in the drill, 2 correct in a row close it without a re-teach. If slips recur on the same step, give that step quick repetitions until it's fluent.
- The learner checked notes or scrolled back during a quiz: miss.
- "I don't know" after a best-guess prompt: miss.
- An ambiguous question: the question is at fault. Don't log it. Ask a clearer question.

## Confident misses across sessions

Log a confident miss with the note `confident:` plus the wrong belief, such as `confident: aligns shapes from the left`. When that knowledge point next comes up for review, read its log notes and ask a question that the same wrong belief would get wrong.
