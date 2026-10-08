---
name: html-artifact
description: Build a self-contained local HTML page from one of 11 interactive templates (plan for review and approval, build checklist, PR review, ticket triage, incident timeline, flag rollout, module map, weekly status, design tokens, animation tuning, or a three-option tradeoff). The agent edits only the embedded JSON, opens the file in a browser, and reads back edits the user saves. Use when the user asks for an HTML artifact, an HTML plan, or an interactive page, or says "show me this as HTML". Not for a product's own UI; frontend-craft covers that. For a claude.ai page or a shareable link, use the Artifact tool instead.
---

# HTML artifact

Build a page when the reader scans, compares, filters, or edits the content. When the answer fits in 5 bullets, answer in text instead; this limit needs judgment.

This skill makes local files only. For a claude.ai page or a shareable link, use the `Artifact` tool.

## Pick a template

Each template is 1 HTML file with inline CSS and JS. The 6 templates with Save write in-page edits back to disk.

| Job | Template | In-page actions | Save |
|---|---|---|---|
| Plan that the reader reads top to bottom and approves | `templates/plan-document.html` | anchor nav, light and dark toggle, Copy as JSON, Print | no |
| Checklist that tracks a plan during the build, with phases, mockups, risks, and decisions | `templates/implementation-plan.html` | tabs, item checkboxes | yes |
| Compare 3 options and recommend 1 | `templates/three-approaches.html` | tabs | no |
| Sort tickets into Now, Next, Later, and Cut | `templates/ticket-triage.html` | drag cards, keys `1` to `4`, owner and label filters | yes |
| Plan feature-flag values and rollouts | `templates/feature-flag-editor.html` | toggles, rollout sliders, reset | yes |
| Map modules, dependencies, and a hot path | `templates/module-map.html` | pan, zoom, select node, tabs | no |
| Review a PR diff with inline findings | `templates/annotated-pr.html` | jump list, checklist, tabs | yes |
| Document design tokens and components | `templates/living-design-system.html` | tabs, copy tokens | no |
| Tune a CSS animation | `templates/animation-sandbox.html` | duration and delay sliders, easing, play, loop, copy CSS | yes |
| Weekly digest of shipped, slipping, and blocked work | `templates/weekly-status.html` | tabs | no |
| Incident timeline and postmortem | `templates/incident-timeline.html` | action-item checkboxes, tabs | yes |

Use `plan-document` for a plan at an approval or review gate. Use `implementation-plan` for a checklist during the build. Never compress a plan to fit the tracker. A `plan-document` page also works unchanged when you publish it with the `Artifact` tool. It opens in light mode.

When no template fits, build 1 new file under the page rules and reuse the CSS tokens of the closest template.

## Build the page

1. **Choose the output path.**
   - A path the user names wins.
   - Otherwise, write `<scratchpad>/<slug>.html` when the session lists a scratchpad directory, or `${TMPDIR:-/tmp}/html-artifact/<slug>.html` when it doesn't. The slug is the page title in kebab-case.
   - Don't write into the repository unless the user asks. An untracked HTML file invites an accidental commit.
   - Never write a new page to an existing path. Use the first unused `<slug>-vN.html`, with N counting from 2.
   - To change a page that already exists, follow [Update a page](#update-a-page) instead.
2. **Copy the template.** Run this command only when `$OUT` doesn't exist:

   ```bash
   mkdir -p "$(dirname "$OUT")"
   command cp "${CLAUDE_PLUGIN_ROOT}/skills/html-artifact/templates/<name>.html" "$OUT"
   ```

   `command` bypasses a `cp -i` alias, which otherwise waits for input.
3. **Read only the data block.** Find it with `grep -n 'id="plan-data"' "$OUT"`. Its keys and value shapes are the contract. The page's script reads every key, and a key you add renders nowhere. The `plan-data` id is historical; keep it.
4. **Replace the sample data.** Replace every sample value. Don't edit the markup, CSS, JS, or license comment. One exception: the Data flow tab in `implementation-plan` is static SVG. Redraw it for the real system. Otherwise, delete its `<svg>` element, and the page hides the tab. `implementation-plan` hides any empty Mockups, Progress, Data flow, Risks, or Decisions tab, so never fill a tab with filler. For a plan that needs a diagram, use `plan-document`. Write the replacement data by the rules in [Write for the reader](#write-for-the-reader) and [Write the content](#write-the-content).
5. **Follow the JSON rules.**
   - Write strict JSON, with no comments and no trailing commas.
   - Write every `<` inside the block as `\u003c`, the same escape that Save writes. A raw `<` can open a comment or a tag that keeps the block from closing. `JSON.parse` turns `\u003c` back into `<`, so `html` fields still render as markup.
   - To write the block from Python, use `json.dumps(data, indent=2).replace("<", "\\u003c")`.
   - Fields named `html` (mockups and components) render as raw HTML. Put only markup you wrote there, never text copied from a PR, ticket, log, or web page.
6. **Check the JSON.** Run this command, which exits 0 when the block parses and holds no raw `<`:

   ```bash
   python3 -c 'import json,re,sys; b=re.search(r"id=\"plan-data\">(.*?)</script>", open(sys.argv[1]).read(), re.S).group(1); json.loads(b); assert "<" not in b, "write < as \\u003c"' "$OUT"
   ```

   A bad block shows "plan-data JSON could not be parsed" in 10 templates. `animation-sandbox` shows no error message, so this check is its only guard.
7. **Open the page.** Run `open "$OUT"` on macOS or `xdg-open "$OUT"` on Linux. Report the absolute path and the template name. When the path is in the scratchpad or `$TMPDIR`, tell the user that the file is temporary and offer to move it.

## Write for the reader

Write the page for a reader who saw none of your working notes. The page is the plan, not a summary of it.

- Write full sentences. Never write fragments joined by arrows.
- Start each item with the point that matters most to the reader.
- Keep every step, every number, and every expected value that the source plan has.
- Drop every item that says "no change". It isn't a step, so the previous rule doesn't keep it.
- Write each open question with a recommendation, and say when it must be decided.
- Name each thing in words. Never coin letter-number codes such as `C1`, `L1`, or `Z1` for steps, risks, claims, options, or decisions. To point at another item, repeat its name.
- The page numbers items itself, so its numbers can differ from the source plan's. Rewrite a reference such as "step 4" as that step's name.

## Write the content

Apply these rules to the data:

- Several templates show an `id` on the page or in Copy as Markdown. Use the real key the reader already knows, such as a ticket or incident key, or a readable slug such as `auth-service`. Never invent a code for an id.
- Explain the approach in sentences. In `implementation-plan`, `goal` and each phase's `summary` hold 1 to 3 sentences on what the work does and why.
- In `implementation-plan`, a phase item is a discrete task that someone checks off. Reasoning and tradeoffs go in `goal` and `summary`, not in items.

In `plan-document`, the sample data shows every key and value shape, and these rules cover the rest:

- Copy each section of the source plan into its slot without summarizing. A section with no slot, such as Non-goals or the review's findings, goes in `extra_sections`. Never drop a section.
- Every key is optional. An empty or missing value hides its heading and its nav entry, so leave a slot empty instead of padding it.
- An `id` on a unit, gate, or question is optional, because the page numbers each item. Copy an id only when the source plan already uses one.
- Text fields are plain text with 2 marks: backticks for code and `**bold**` for emphasis. No field renders HTML, and links don't render.
- Write the diagram as `nodes` and `edges`. The page lays it out and draws inline SVG, so never write SVG into the data block.
- Set `diagram.kind` to `flow`, `state`, or `systems`. Set a node's `kind` to `step`, `terminal`, `error`, or `external`.
- Mark an error path or an async path with `dashed: true`.
- When the source plan has no diagram, draw one from its components if it helps the reader. Otherwise, set `diagram` to `null`.
- Copy the `CLAIMS:` line from `claims-verification` into `verdicts.claims`, verbatim.
- Add 1 round to `verdicts.rounds` per review, with each model family's verdict: `approve`, `revise`, or `block`. When `adversarial-review` returns `proceed`, write `approve`.
- Set `verdicts.status` to where the plan stands after its fixes, such as "Ready for approval".
- Put every option that the plan or a review rejected in `approach.rejected`. It takes 1 object or a list of them.
- Write each unit as 1 sentence. Mark a unit that ships on its own with `separable: true`.
- Write each runbook step as 1 gate. A 5-step runbook becomes 5 gates. Copy each step's expected result. When a step has none, write the result that the plan implies, and never invent a number.
- Give each question a `recommendation` and a `decide_by`. Use `before build`, `before canary`, or `later` when one fits. Otherwise, name the gate, such as `before the backfill`.
- Fill `provenance` with the repo, branch, commit, revision, date, and plan path that the plan was written against. Leave an unknown field empty instead of guessing.

## Read edits back

Save keeps the open file's name. In the following rules, `<stem>` is the file name of `$OUT` without `.html`.

- In Chromium, the first Save click opens a save picker in the browser's default folder, with the open file's name filled in. Pick the original path to overwrite it. Later clicks overwrite the same file.
- Firefox and Safari download a copy to `~/Downloads/<stem>.html`. A repeat download gets a number, and the format depends on the browser: `<stem> (1).html`, `<stem>(1).html`, or `<stem>-1.html`.
- When the user says they saved, read the JSON block from the path they name. Otherwise, read the newest file by modification time among `$OUT`, `~/Downloads/<stem>.html`, `~/Downloads/<stem> (N).html`, `~/Downloads/<stem>(N).html`, and `~/Downloads/<stem>-N.html`, where N is digits only. A `<stem>-vN.html` file is a different page.
- Use a candidate other than `$OUT` only when its data block has the same `template` and `plan_title` as `$OUT`. A page named `<stem>-19.html` also matches `<stem>-N.html`.
- Report the exact file you read.
- The 5 templates without Save keep no in-page changes after a reload. Their Copy as JSON button exports the current state.
- `plan-document` has no in-page changes. To change it, change the source plan, then follow [Update a page](#update-a-page).

## Update a page

Edit an existing page only when the user asks you to update it, by name or as the page from earlier in this conversation. Otherwise, build a new page.

1. Find the newest saved copy with the rules in [Read edits back](#read-edits-back), so saved edits survive.
2. If that copy isn't `$OUT`, copy it over `$OUT` with `command cp`.
3. Change the data in the JSON block of `$OUT`, then run steps 5 and 6 of [Build the page](#build-the-page).
4. Tell the user to close the old tab of the page, because Save in that tab overwrites the update with the old state. Then reopen the page with step 7.

## Page rules

Apply these rules when you extend a template or build a new page:

- Ship 1 file with inline `<style>` and `<script>`. Use no `<script src>`, no stylesheet `<link>`, no web fonts, and no remote URLs. Draw diagrams as inline SVG.
- Use `system-ui` for body text, `ui-monospace` for data, and `ui-serif` for headings if you want contrast.
- Use 1 accent color and no gradients. Keep corner radii at 0 to 4 px. Use borders before shadows.
- Prefer tables to cards and density to whitespace: 1.5 line height and 12 to 16 px between sections.
- Support light and dark mode through `prefers-color-scheme`, and respect `prefers-reduced-motion`.
- Provide a skip link, `:focus-visible` outlines, and ARIA labels on controls.
- Animate only a state change that the user caused.
- Hide a section and its nav entry, or a tab and its panel, when its data is empty.
- Keep the inline script near 400 lines and the file under 40 KB. Exceed these soft limits when the content or the layout code needs it.
