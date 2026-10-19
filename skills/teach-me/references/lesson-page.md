# The lesson page

Read this before you build the first lesson page of a session. Build 1 page per topic. The page teaches the topic before any question, and later it serves as the topic's reference. Graded practice happens in chat, never on the page.

## Before you build

The plan step in `SKILL.md` gives you the goal, the source, and the knowledge points. If you can fetch the source, check each claim against it, and link the section that backs each rule.

## Structure

Build these sections, in this order:

1. **Header.** An eyebrow names the source and its section. The h1 states the mental model as a claim, not a topic name, such as "A join pairs rows that match" or "A tensor is a grid of numbers with a shape". A lede of at most 80 words says what to forget, gives the model, and says why it matters for the goal.
2. **Overview.** Show the mental model with 1 diagram and 1 concrete number from the source. Add 1 line per knowledge point, numbered to match the map in chat.
3. **1 section per knowledge point, in map order.** Each section holds these parts:
   - An eyebrow with the knowledge point's number and the source section.
   - An h2 that states the knowledge point's rule as a claim.
   - At most 150 words of prose that give the rule and why it works.
   - A worked example with labeled steps, on small data from the source.
   - 1 live widget.
   - The common mistake and the wrong belief behind it.
4. **Optional: a synthesis widget.** When the knowledge points form a pipeline, add 1 widget that runs the whole chain, like the shape tracker in the sample.
5. **Keep these.** List 4 to 7 rules: the knowledge point statements plus the practitioner points from the plan step.
6. **Sources.** Name the rawest source, with a link to each section where possible.
7. **Footer.** End with "Back in chat: ask anything about this page, or type `go` for a practice problem."

## Widgets

Each knowledge point section gets 1 widget. The learner changes an input, such as a slider, a toggle, a clickable cell, or an editable value, and sees the real result. The widget recomputes that result in plain JS from the same data as the worked example. Show the computed output as text under the visual.

A widget has no graded questions, no answer reveals, and no scores.

These widgets fit 3 common kinds of topic:

- Joins: 2 tables of 4 rows each. The learner picks the join type and sees the matched pairs and the output row count.
- Shapes: sliders that recompute each shape.
- An algorithm: a step button that walks through its state.

## Visual system

Reuse the sample's layout CSS: the reading column of at most 760px, the eyebrow, the panel, the note, the legend, and the controls. Shared CSS makes every lesson read as part of one course.

Give each core concept 1 color token, and keep that color across prose, diagrams, and code. Color carries meaning, never decoration. Define a light and a dark value for every token, as the sample does.

## Content

- Use the source's names, examples, numbers, and error text.
- Keep data small: about 6 rows or 20 tokens at most.
- Compute every number and output on the page by running code before you publish, for example with `sqlite3` or Python.
- Put the concrete case before the abstract rule.
- Leave out filler, decorative images, and marketing tone.
- Keep the reading time to about 10 minutes at most.

## Mechanics

- Write 1 self-contained HTML file with inline CSS and JS. The Google Fonts stylesheet from the sample is fine.
- Load no library unless the concept needs one. Then load 1 CDN script, pinned to an exact version.
- Make the page work at 375px width with no horizontal page scroll. Tables and `pre` blocks scroll inside themselves.
- Label every input, keep focus visible, and support reduced motion.
- Where the platform's artifact rules are stricter, follow them.

## Delivery

Publish the page with the first option that applies:

1. In claude.ai, create an HTML artifact.
2. In Claude Code, publish the page with the Artifact tool when that tool exists.
3. Otherwise, write the page to `~/claude/learning-lessons/NNNN-TOPIC_ID.html` and open it. `NNNN` is the next 4-digit number in that folder, such as `0001`, and `TOPIC_ID` is the topic's ID in the ledger.

Put the link or the path in the page message.

## Changes

`deepen` or a goal change rebuilds the page. When a learner question exposes a gap, answer it in chat. Don't rebuild the page mid-session.

## The sample

`assets/sample-lesson.html` sets the quality bar for structure, density, and widget style. Don't copy its topic content. Where the sample and this file differ, follow this file.
