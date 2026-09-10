---
name: frontend-craft
description: Process for pushing AI-built UI past generic output — seed-string variety, an independent design-critic loop with screenshots, generated images and video instead of CSS-only visuals, and a subtraction pass that removes AI tells. Use with the frontend-design skill, not instead of it, whenever building or reworking a landing page, app screen, marketing page, or component library and the user wants it to look distinctive and polished. Skip it for a single-component tweak or a change frontend-design alone covers. Triggers include "make this look less AI", "polish the UI", "improve the design", "design critic", "explore design directions", "this looks generic".
---

# Frontend craft

Models pick the most probable design choice at every token, so unguided UI converges on the same layouts, palettes, and effects. This skill supplies what the model can't: outside randomness, an independent critic, real imagery, and a push to delete.

Load `frontend-design` (the Anthropic plugin skill) first. It owns the design plan: subject, palette, type, layout, signature element, and copy. This skill owns the process around that plan. Don't restate its rules; run them.

## Roles

Both roles run in a fresh context with a small input, so the strongest model is affordable in each. The session stays out of the code.

- **Critic**: the strong model, `model:` unset. Sees only screenshots. Never sees code, past critiques, or the implementer's rationale.
- **Implementer**: the strong model, `model:` unset. One fresh context per round holds the brief, the critic's gap list, and the file paths. Never a fork. `sonnet` is fine for rote iterations once the direction is fixed and the change is spelled out.
- **You (session)**: run the loop, run validation, hold the stopping rule, report scores.

## Discover: widen the search before you commit

Run this stage when the user hasn't fixed a visual direction. Skip it when the brief already names one; the brief's words win.

**Seed string.** Asking for "unique" or "random" doesn't work; the model predicts what randomness sounds like. Bring entropy from outside:

1. Generate a 64-character random alphanumeric string in the shell (`LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 64`).
2. Derive the creative direction from the string: palette, layout, typography, signature element. Read subpatterns, repeated characters, and digit runs as prompts, not as a lookup table.
3. Build the direction with judgment. Don't reveal the string in the design or the copy.

Two runs with different seeds produce different designs. When the user wants options, produce 3 seeded directions as one-paragraph plans plus a token set each, and let the user pick before any code.

**Ambitious brief.** A vivid, specific brief beats a random one. Run this loop with the user only when they ask for options or have offered taste. Otherwise run it in your thinking and show 1 or 2 sharpened directions:

1. List 15 or more design-language ideas in one line each. Go broad, not deep.
2. The user reacts. Capture what they liked, what felt tacky, and what needs texture or restraint.
3. Sharpen the 1 or 2 survivors into a concise build prompt: inspiration, materials, what to avoid, one risk to take.

Ideas that sound wrong are worth one attempt. Keep the prompt of a failed attempt; a later model may land it.

## Define: iterate with an independent critic

The implementer still self-critiques as `frontend-design` requires, but a self-review reads its own reasoning. Add a critic that sees only pixels.

Each iteration:

1. Screenshot the current design at 1440 px and 390 px wide. Use the browser tooling available (Chrome MCP, Playwright, or the `run` skill). Save PNGs to the scratchpad. If no browser tooling exists, skip the critic loop, run the subtraction pass alone, and report no scores rather than invented ones.
2. Spawn the critic in a fresh context with only the screenshots, the one-sentence aesthetic brief, and the prompt in the following section. Same prompt every round.
3. Hand the critic's gap list to a fresh implementer each round as the change spec. Fix the biggest gap first.
4. Record the score. Repeat.

Critic prompt:

```
You are reviewing a UI design from screenshots only. The design is going for: BRIEF.

1. Describe the aesthetic the design is attempting.
2. Imagine how a top design studio would execute that same aesthetic.
3. List the biggest gaps between this design and that execution. Cover composition and structure first, then fine detail: type scale, spacing rhythm, alignment, color discipline, motion, copy.
4. Penalize anything overdone, excessive, or recognizable as AI-generated. Name each instance.
5. Score the design out of 10 against the studio bar.

Be specific and opinionated. Name the element, the problem, and the fix. No general praise, no vague prose.
```

Stopping rule, held by you and never given to the critic:

- Run 2 iterations before judging convergence. A flat first pair isn't a stop: rewrite the change spec yourself instead of resending the critic's list, then run a third.
- Stop when the critic scores 9 or higher, when the score fails to rise for 2 consecutive rounds, or after 5 rounds.
- Report the score history and the round the design stopped improving.

Sharpen the critic when the brief allows it. Ranking beats scoring: give the critic 3 or 4 reference screenshots plus the current design and ask for a ranking by polish and taste. Reference images are a moodboard, not a target; tell the critic to penalize copying.

## Define: replace CSS-only visuals with generated media

Gradients, blobs, and geometric shapes are what a model reaches for instead of an image, and readers recognize them. When the design needs a hero visual, texture, or illustration, generate one.

- **Images**: use the `mays:gemini-image-generator` skill. It reads `GEMINI_API_KEY` from the environment. Generate on a solid background when the image must sit on the page's color, or ask for a transparent-friendly composition and mask it.
- **Video**: for motion that code can't fake (refraction, physics, material), generate a looping clip through fal.ai with `FAL_KEY` from the environment. Look up current text-to-video and video-matting model ids in the fal.ai docs at run time, and name the ids you chose in the report. Render the clip over the page background so refraction bakes in, then remove the background with a matting model. For state transitions, generate keyframe images for each state and interpolate between them; play the clip on the action, or scrub it on scroll.
- Verify every generated asset in the browser at both widths before you move on. Check the loop seam on video.

Keys stay in the environment and are referred to by name only, never by value. Before writing a `.env.agents` file, confirm that `.gitignore` contains `.env*` and add the line first. If a key is missing, skip the media step, say so in the report, and ask the user to export the variable. Never ask them to paste a key into chat. Adding a dependency for video needs the user's approval first.

## Deliver: subtract, then remove AI tells

Models add and rarely remove. Restraint reads as premium, so the final pass deletes. For each element, ask what breaks if it disappears. Nothing breaks: delete it.

Delete on sight:

- Glows, gradients, and backdrop blurs that don't carry the aesthetic.
- Accent colors and highlights on text that don't encode meaning.
- Labels that repeat what an image or the layout already says.
- Containers, cards, and dividers that group nothing.
- Custom controls that look worse than the platform's native ones. Prefer native form controls and, on iOS and macOS, system components.
- Copy that explains the product instead of naming what the reader does next.

Then screen for AI tells. Each is countable; find one, fix it:

- Purple-to-blue gradient, text left with a graphic right, or a three-column icon-card feature row.
- The three default looks the `frontend-design` skill names: cream plus serif plus terracotta, near-black plus one acid accent, broadsheet hairlines. Keep one when the brief asked for it or the subject earned it; delete it when a free axis landed there by default.
- Numbered markers on content that isn't a sequence.
- Emoji as icons, sparkle glyphs, or decorative blobs.
- Uniform `rounded-2xl` corners with soft drop shadows on every surface.
- Hover-lift, fade-in on scroll, or a count-up stat applied to everything.
- Fake metrics, testimonials, or logos.
- Copy with "Unleash", "Elevate", "Seamless", "Supercharge", or a headline that ends in a period for effect.

Run the critic once more after the subtraction pass. A design that loses points here lost something that carried the aesthetic; put that one element back. Putting an element back ends the loop; don't re-score it.

## Report

End with:

```
## Frontend craft report
Direction: <one line: seed-derived | brief-derived | user-fixed>
Critic scores: 5 → 7 → 8.5 → 9 (stopped: score ≥ 9)
Generated media: 2 images (hero, texture), 0 video (FAL_KEY unset)
Removed in subtraction pass: 7 elements (list the notable ones)
Screenshots: <paths at 1440 px and 390 px>
Open: <gaps the critic still names, or none>
```
