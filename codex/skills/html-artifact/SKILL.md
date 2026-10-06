---
name: html-artifact
description: Build a self-contained local HTML page from 10 interactive templates (plans, PR reviews, triage boards, incidents, flag rollouts, module maps, status digests, design tokens, animations, tradeoffs) when the user asks for an HTML artifact or an interactive page. Skip short text answers.
---

# HTML artifact

Deliver 1 self-contained HTML file built from a template, opened in a browser or with its absolute path reported. Build a page when the reader scans, compares, filters, or edits the content. When the answer fits in 5 bullets, answer in text instead.

Pick the template that matches the job. Template paths resolve relative to the directory of this `SKILL.md`. The 6 templates marked Save write in-page edits back to disk.

- [implementation-plan](templates/implementation-plan.html): phased build plan with checklists, mockups, risks, and decisions. Save.
- [three-approaches](templates/three-approaches.html): compare 3 options and recommend 1. No Save.
- [ticket-triage](templates/ticket-triage.html): sort tickets into Now, Next, Later, and Cut by drag or keys `1` to `4`. Save.
- [feature-flag-editor](templates/feature-flag-editor.html): flag toggles and rollout sliders. Save.
- [module-map](templates/module-map.html): modules, dependencies, and a hot path, with pan and zoom. No Save.
- [annotated-pr](templates/annotated-pr.html): PR diff with inline findings and a review checklist. Save.
- [living-design-system](templates/living-design-system.html): design tokens and components. No Save.
- [animation-sandbox](templates/animation-sandbox.html): tune a CSS animation with sliders and easing. Save.
- [weekly-status](templates/weekly-status.html): digest of shipped, slipping, and blocked work. No Save.
- [incident-timeline](templates/incident-timeline.html): incident timeline, postmortem, and action items. Save.

When no template fits, build 1 new file under the page rules and reuse the CSS tokens of the closest template.

A path the user names wins. Otherwise write `${TMPDIR:-/tmp}/html-artifact/<slug>.html`, where the slug is the page title in kebab-case. Keep the file outside the repository unless the user asks. Never write a new page to an existing path; use the first unused `<slug>-vN.html`, with N counting from 2. Copy a template only to a path that doesn't exist, with `mkdir -p "$(dirname "$OUT")"` and then `command cp "<skill-dir>/templates/<name>.html" "$OUT"`. `command` bypasses an interactive `cp -i` alias.

Replace only the JSON inside `<script type="application/json" id="plan-data">`. Its keys and value shapes are the contract. The page's script reads every key, and a key you add renders nowhere. Replace every sample value, and leave the markup, CSS, JS, and license comment unchanged. The Data flow tab in `implementation-plan` is static SVG, so redraw it for the real system or delete its tab button and its panel together.

Write strict JSON, with no comments and no trailing commas. Write every `<` inside the block as `\u003c`, the same escape that Save writes, because a raw `<` can open a comment or a tag that keeps the block from closing. `JSON.parse` turns `\u003c` back into `<`, so `html` fields still render as markup. From Python, write the block with `json.dumps(data, indent=2).replace("<", "\\u003c")`. Fields named `html` (mockups and components) render as raw HTML. Put only markup you wrote there, never text copied from a PR, ticket, log, or web page.

Check the block with this command, which exits 0 when the JSON parses and holds no raw `<`:

```bash
python3 -c 'import json,re,sys; b=re.search(r"id=\"plan-data\">(.*?)</script>", open(sys.argv[1]).read(), re.S).group(1); json.loads(b); assert "<" not in b, "write < as \\u003c"' "$OUT"
```

A bad block shows "plan-data JSON could not be parsed" in 9 templates. `animation-sandbox` shows no error message, so the check is its only guard. Open the file with `open` on macOS or `xdg-open` on Linux. If the command fails or the sandbox blocks it, report the absolute path. Don't request extra permissions only to open a file. When the path is under `$TMPDIR` or `/tmp`, tell the user that the file is temporary and offer to move it.

Save keeps the open file's name, and `<stem>` means the file name of `$OUT` without `.html`. In Chromium, the first Save click opens a save picker with that name filled in. Picking the original path overwrites it, and later clicks overwrite the same file. Firefox and Safari download a copy to `~/Downloads/<stem>.html`. A repeat download gets a number, and the format depends on the browser: `<stem> (1).html`, `<stem>(1).html`, or `<stem>-1.html`. The 4 templates without Save lose in-page changes on reload; their Copy as JSON button exports the state.

When the user says they saved, read the data block from the path they name. Otherwise read the newest file by modification time among `$OUT`, `~/Downloads/<stem>.html`, `~/Downloads/<stem> (N).html`, `~/Downloads/<stem>(N).html`, and `~/Downloads/<stem>-N.html`, where N is digits only. A `<stem>-vN.html` file is a different page. Use a candidate other than `$OUT` only when its data block has the same `template` and `plan_title` as `$OUT`, because a page named `<stem>-19.html` also matches `<stem>-N.html`. Report the exact file you read.

Edit an existing page only when the user asks you to update it, by name or as the page from earlier in this conversation. Start from the newest saved copy that the read-back rules find, so saved edits survive. If that copy isn't `$OUT`, copy it over `$OUT` with `command cp`. Then change its data block and check it. Before you open it again, tell the user to close the old tab of the page, because Save in that tab overwrites the update with the old state.

When you extend a template or build a new page, ship 1 file with inline `<style>` and `<script>`, with no external scripts, stylesheets, web fonts, or remote URLs. Draw diagrams as inline SVG. Use `system-ui` for text and `ui-monospace` for data. Use 1 accent color, no gradients, corner radii of 0 to 4 px, and borders before shadows. Prefer tables to cards and density to whitespace. Support light and dark mode through `prefers-color-scheme`, and respect `prefers-reduced-motion`. Provide a skip link, `:focus-visible` outlines, and ARIA labels on controls. Animate only a state change that the user caused. Keep the inline script near 400 lines and the file under 40 KB unless the content needs more.

Finish with the absolute path, the template name, and the in-page actions that persist through Save.
