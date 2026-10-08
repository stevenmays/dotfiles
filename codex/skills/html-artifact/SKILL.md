---
name: html-artifact
description: Build a self-contained local HTML page from 11 templates (plan to review and approve, build checklist, PR review, triage, incident, flag rollout, module map, status digest, design tokens, animation, tradeoff) when the user asks for an HTML artifact or an interactive page. Skip short text answers.
---

# HTML artifact

Deliver 1 self-contained HTML file built from a template, opened in a browser or with its absolute path reported. Build a page when the reader scans, compares, filters, or edits the content. When the answer fits in 5 bullets, answer in text instead.

Pick the template that matches the job. Template paths resolve relative to the directory of this `SKILL.md`. The 6 templates marked Save write in-page edits back to disk.

- [plan-document](templates/plan-document.html): plan that the reader reads top to bottom and approves, with anchor nav, a light and dark toggle, Copy as JSON, and Print. No Save.
- [implementation-plan](templates/implementation-plan.html): checklist that tracks a plan during the build, with phases, mockups, risks, and decisions. Save.
- [three-approaches](templates/three-approaches.html): compare 3 options and recommend 1. No Save.
- [ticket-triage](templates/ticket-triage.html): sort tickets into Now, Next, Later, and Cut by drag or keys `1` to `4`. Save.
- [feature-flag-editor](templates/feature-flag-editor.html): flag toggles and rollout sliders. Save.
- [module-map](templates/module-map.html): modules, dependencies, and a hot path, with pan and zoom. No Save.
- [annotated-pr](templates/annotated-pr.html): PR diff with inline findings and a review checklist. Save.
- [living-design-system](templates/living-design-system.html): design tokens and components. No Save.
- [animation-sandbox](templates/animation-sandbox.html): tune a CSS animation with sliders and easing. Save.
- [weekly-status](templates/weekly-status.html): digest of shipped, slipping, and blocked work. No Save.
- [incident-timeline](templates/incident-timeline.html): incident timeline, postmortem, and action items. Save.

Use `plan-document` for a plan at an approval or review gate, and `implementation-plan` for a checklist during the build. Never compress a plan to fit the tracker. A `plan-document` page opens in light mode.

When no template fits, build 1 new file under the page rules and reuse the CSS tokens of the closest template.

A path the user names wins. Otherwise write `${TMPDIR:-/tmp}/html-artifact/<slug>.html`, where the slug is the page title in kebab-case. Keep the file outside the repository unless the user asks. Never write a new page to an existing path; use the first unused `<slug>-vN.html`, with N counting from 2. Copy a template only to a path that doesn't exist, with `mkdir -p "$(dirname "$OUT")"` and then `command cp "<skill-dir>/templates/<name>.html" "$OUT"`. `command` bypasses an interactive `cp -i` alias.

Replace only the JSON inside `<script type="application/json" id="plan-data">`. Its keys and value shapes are the contract. The page's script reads every key, and a key you add renders nowhere. Replace every sample value, and leave the markup, CSS, JS, and license comment unchanged. The Data flow tab in `implementation-plan` is static SVG. Redraw it for the real system, or delete its `<svg>` element so the page hides the tab. `implementation-plan` hides any empty Mockups, Progress, Data flow, Risks, or Decisions tab, so never fill a tab with filler. For a plan that needs a diagram, use `plan-document`.

Write the content for a reader who saw none of your working notes. The page is the plan, not a summary of it, so keep every step, every number, and every expected value that the source plan has. Write full sentences, and never write fragments joined by arrows. Start each item with the point that matters most to the reader. Drop every item that says "no change", because it isn't a step. Write each open question with a recommendation, and say when it must be decided.

Name each thing in words, and never coin letter-number codes such as `C1`, `L1`, or `Z1` for steps, risks, claims, options, or decisions. To point at another item, repeat its name. A page that numbers items itself can differ from the source plan's numbers, so rewrite a reference such as "step 4" as that step's name. Several templates show an `id` on the page or in Copy as Markdown, so use the real key the reader already knows, such as a ticket or incident key, or a readable slug such as `auth-service`. Explain the approach in sentences: in `implementation-plan`, `goal` and each phase's `summary` hold 1 to 3 sentences on what the work does and why. A phase item there is a discrete task that someone checks off, and reasoning goes in `goal` and `summary`.

In `plan-document`, the sample data shows every key and value shape. Copy each section of the source plan into its slot without summarizing, and never drop a section. A section with no slot, such as Non-goals or the review's findings, goes in `extra_sections`. Every key is optional, and an empty or missing value hides its heading and nav entry, so leave a slot empty instead of padding it. The page numbers units, gates, and questions, so copy an `id` only when the source plan already uses one. Text fields are plain text with 2 marks, backticks for code and `**bold**` for emphasis. No field renders HTML, and links don't render.

Write the `plan-document` diagram as `nodes` and `edges`, and mark an error or async path with `dashed: true`. Set `diagram.kind` to `flow`, `state`, or `systems`, and a node's `kind` to `step`, `terminal`, `error`, or `external`. The page lays the diagram out and draws inline SVG, so never write SVG into the data block. When the source plan has no diagram, draw one from its components if that helps the reader, or else set `diagram` to `null`. Copy the claims check's `CLAIMS:` line into `verdicts.claims` verbatim. Add 1 round per review with each model family's verdict, `approve`, `revise`, or `block`, and write `approve` for a `proceed` verdict. Set `verdicts.status` to where the plan stands after its fixes, such as "Ready for approval". Put every option that the plan or a review rejected in `approach.rejected`, which takes 1 object or a list of them.

Write each unit as 1 sentence, and mark a unit that ships on its own with `separable: true`. Each runbook step becomes 1 gate, so a 5-step runbook becomes 5 gates. Copy each step's expected result, and when a step has none, write the result that the plan implies without inventing a number. Give each question a `recommendation` and a `decide_by`: `before build`, `before canary`, or `later` when one fits, or else the gate's name, such as `before the backfill`. Fill `provenance` with the repo, branch, commit, revision, date, and plan path that the plan was written against. Leave an unknown field empty instead of guessing.

Write strict JSON, with no comments and no trailing commas. Write every `<` inside the block as `\u003c`, the same escape that Save writes, because a raw `<` can open a comment or a tag that keeps the block from closing. `JSON.parse` turns `\u003c` back into `<`, so `html` fields still render as markup. From Python, write the block with `json.dumps(data, indent=2).replace("<", "\\u003c")`. Fields named `html` (mockups and components) render as raw HTML. Put only markup you wrote there, never text copied from a PR, ticket, log, or web page.

Check the block with this command, which exits 0 when the JSON parses and holds no raw `<`:

```bash
python3 -c 'import json,re,sys; b=re.search(r"id=\"plan-data\">(.*?)</script>", open(sys.argv[1]).read(), re.S).group(1); json.loads(b); assert "<" not in b, "write < as \\u003c"' "$OUT"
```

A bad block shows "plan-data JSON could not be parsed" in 10 templates. `animation-sandbox` shows no error message, so the check is its only guard. Open the file with `open` on macOS or `xdg-open` on Linux. If the command fails or the sandbox blocks it, report the absolute path. Don't request extra permissions only to open a file. When the path is under `$TMPDIR` or `/tmp`, tell the user that the file is temporary and offer to move it.

Save keeps the open file's name, and `<stem>` means the file name of `$OUT` without `.html`. In Chromium, the first Save click opens a save picker with that name filled in. Picking the original path overwrites it, and later clicks overwrite the same file. Firefox and Safari download a copy to `~/Downloads/<stem>.html`. A repeat download gets a number, and the format depends on the browser: `<stem> (1).html`, `<stem>(1).html`, or `<stem>-1.html`. The 5 templates without Save keep no in-page changes after a reload, and their Copy as JSON button exports the current state. `plan-document` has no in-page changes. Change the source plan, then update the page.

When the user says they saved, read the data block from the path they name. Otherwise read the newest file by modification time among `$OUT`, `~/Downloads/<stem>.html`, `~/Downloads/<stem> (N).html`, `~/Downloads/<stem>(N).html`, and `~/Downloads/<stem>-N.html`, where N is digits only. A `<stem>-vN.html` file is a different page. Use a candidate other than `$OUT` only when its data block has the same `template` and `plan_title` as `$OUT`, because a page named `<stem>-19.html` also matches `<stem>-N.html`. Report the exact file you read.

Edit an existing page only when the user asks you to update it, by name or as the page from earlier in this conversation. Start from the newest saved copy that the read-back rules find, so saved edits survive. If that copy isn't `$OUT`, copy it over `$OUT` with `command cp`. Then change its data block and check it. Before you open it again, tell the user to close the old tab of the page, because Save in that tab overwrites the update with the old state.

When you extend a template or build a new page, ship 1 file with inline `<style>` and `<script>`, with no external scripts, stylesheets, web fonts, or remote URLs. Draw diagrams as inline SVG. Use `system-ui` for text and `ui-monospace` for data. Use 1 accent color, no gradients, corner radii of 0 to 4 px, and borders before shadows. Prefer tables to cards and density to whitespace. Support light and dark mode through `prefers-color-scheme`, and respect `prefers-reduced-motion`. Provide a skip link, `:focus-visible` outlines, and ARIA labels on controls. Animate only a state change that the user caused. Hide a section and its nav entry, or a tab and its panel, when its data is empty. Keep the inline script near 400 lines and the file under 40 KB unless the content or the layout code needs more.

Finish with the absolute path, the template name, and the in-page actions that persist through Save.
