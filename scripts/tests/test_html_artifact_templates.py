"""Static checks for the html-artifact templates in the Claude and Codex trees."""

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = {"claude": ROOT / "skills/html-artifact", "codex": ROOT / "codex/skills/html-artifact"}
SAVE = ("implementation-plan", "annotated-pr", "feature-flag-editor",
        "incident-timeline", "animation-sandbox", "ticket-triage")
DISPLAY = ("living-design-system", "module-map", "three-approaches", "weekly-status")
NAMES = SAVE + DISPLAY

COPYRIGHT = "Copyright (c) 2026 Ahmad Othman Ammar Adi"
PERMISSION = "Permission is hereby granted"
# The notice sits inside <html> because Save serializes documentElement.outerHTML.
NOTICE = re.compile(r"\A(<!doctype html>\s*<html[^>]*>\s*)<!--(.*?)-->", re.S | re.I)
DATA = re.compile(r'<script type="application/json" id="plan-data">(.*?)</script>', re.S)
INLINE_SCRIPT = re.compile(r'<script(?![^>]*type="application/json")[^>]*>(.*?)</script>', re.S)
EXTERNAL = (r"<script[^>]+src", r"<link[^>]+stylesheet", r'(src|href)\s*=\s*"https?://',
            r"@import", r"@font-face", r"(?<![.\w])(eval\s*\(|new\s+Function\s*\()")
RESIDUE = re.compile(r"plan-it|plan\.html|/plan-|attest|integrity|sha-?256|CLAUDE_PLUGIN_ROOT|othman|\badi@",
                     re.I)
PHASE_KEYS = {"id", "title", "status", "items", "milestones"}
FRONTMATTER = re.compile(r"\A---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n")
CHECK_COMMAND = re.compile(r"^ *(python3 -c '.*' \"\$OUT\")$", re.M)
HTTP_GUARD = "/^https?:\\/\\//i.test("
HREF_SINK = re.compile(r'href="\$\{[^}]*?\b(\w+\.\w+)|\.href = (\w+\.\w+)|setAttribute\("href", (\w+\.\w+)')
# Statements that must run at load, at the IIFE's top level, because Save serializes the live DOM.
LOAD_RESETS = {
    "animation-sandbox": ('styleEl.textContent = "";', 'target.removeAttribute("style");',
                          'loopBtn.setAttribute("aria-pressed", "false");', "cssSnippet.hidden = true;",
                          'showCssBtn.setAttribute("aria-pressed", "false");', 'toastEl.classList.remove("show");'),
    "ticket-triage": ("liveStatus.dataset.hint = liveStatus.dataset.hint || liveStatus.innerHTML;",
                      "liveStatus.innerHTML = liveStatus.dataset.hint;"),
}


def pages():
    for tree, skill in SKILLS.items():
        for name in NAMES:
            yield tree, name, (skill / "templates" / f"{name}.html").read_text()


def listing(directory):
    return sorted(p for p in directory.iterdir() if not p.name.startswith("."))


def script(text):
    return "\n".join(INLINE_SCRIPT.findall(text[DATA.search(text).end():]))


class TemplateChecks(unittest.TestCase):
    def test_template_set(self):
        expected = {f"{name}.html" for name in NAMES} | {"LICENSE"}
        for tree, skill in SKILLS.items():
            with self.subTest(tree=tree):
                self.assertEqual({p.name for p in listing(skill / "templates")}, expected)

    def test_trees_identical(self):
        claude, codex = (SKILLS[tree] / "templates" for tree in ("claude", "codex"))
        for path in listing(claude):
            with self.subTest(file=path.name):
                self.assertEqual(path.read_bytes(), (codex / path.name).read_bytes())

    def test_license_notice(self):
        for skill in SKILLS.values():
            text = (skill / "templates/LICENSE").read_text()
            self.assertIn(COPYRIGHT, text)
            self.assertIn(PERMISSION, text)
        for tree, name, text in pages():
            with self.subTest(tree=tree, page=name):
                notice = NOTICE.match(text)
                self.assertIsNotNone(notice, "MIT notice comment must open the <html> element")
                self.assertIn(COPYRIGHT, notice.group(2))
                self.assertIn(PERMISSION, notice.group(2))

    def test_page_shell(self):
        for tree, name, text in pages():
            with self.subTest(tree=tree, page=name):
                self.assertTrue(text.lower().startswith("<!doctype html"))
                self.assertIn('<html lang="en"', text)
                self.assertIn('<meta name="viewport"', text)
                self.assertRegex(text, r"<title>[^<]+</title>")
                self.assertIn("skip-link", text)

    def test_self_contained(self):
        for tree, name, text in pages():
            for pattern in EXTERNAL:
                with self.subTest(tree=tree, page=name, pattern=pattern):
                    self.assertNotRegex(text, pattern)

    def test_no_plan_it_residue(self):
        for tree, name, text in pages():
            with self.subTest(tree=tree, page=name):
                body = NOTICE.sub(r"\1", text, count=1)
                self.assertEqual(sorted({m.group(0) for m in RESIDUE.finditer(body)}), [])

    def test_data_block(self):
        for tree, name, text in pages():
            with self.subTest(tree=tree, page=name):
                blocks = DATA.findall(text)
                self.assertEqual(len(blocks), 1)
                data = json.loads(blocks[0])
                self.assertIsInstance(data, dict)
                # A raw "<" can open a comment or script tag that keeps the block from closing.
                self.assertNotIn("<", blocks[0], "write < as \\u003c inside the data block")
                code = script(text)
                # The key detector only sees dotted reads, so forbid every other access form.
                self.assertNotRegex(code, r"\bplan\[")
                self.assertNotRegex(code, r"Object\.(keys|values|entries)\(plan\b")
                self.assertEqual(set(re.findall(r"\bplan\.(\w+)", code)), set(data))
                if name == "implementation-plan":
                    for phase in data["phases"]:
                        self.assertLessEqual(set(phase), PHASE_KEYS)

    def test_script_blocks_close_once(self):
        for tree, name, text in pages():
            with self.subTest(tree=tree, page=name):
                openers = list(re.finditer(r"<script\b[^>]*>", text, re.I))
                self.assertEqual(len(openers), len(re.findall(r"</script", text, re.I)))
                for opener in openers:
                    close = re.search(r"</script", text[opener.end():], re.I)
                    self.assertRegex(text[opener.end() + close.start():], r"\A</script\s*>")

    def test_tabs_pair_with_panels(self):
        for tree, name, text in pages():
            with self.subTest(tree=tree, page=name):
                # The tab script pairs each tab with the panel at the same index.
                tabs = re.findall(r'<button[^>]*role="tab"[^>]*>', text)
                panels = re.findall(r'<section[^>]*role="tabpanel"[^>]*>', text)
                controls = [re.search(r'aria-controls="([^"]+)"', tab).group(1) for tab in tabs]
                self.assertEqual(controls, [re.search(r'\bid="([^"]+)"', p).group(1) for p in panels])

    def test_save_contract(self):
        for tree, name, text in pages():
            with self.subTest(tree=tree, page=name):
                if name in DISPLAY:
                    self.assertNotIn('id="btn-save"', text)
                    self.assertNotIn("showSaveFilePicker", text)
                    continue
                self.assertIn('id="btn-save"', text)
                self.assertLess(text.index("showSaveFilePicker"), text.index("createObjectURL"))
                self.assertIn("dataEl.textContent = JSON.stringify(plan", text)
                self.assertIn('.replace(/</g, "\\\\u003c")', text)
                self.assertRegex(text, r"const fileName = [^;\n]*location\.pathname")
                self.assertIn("suggestedName: fileName", text)
                self.assertIn("a.download = fileName", text)

    def test_save_clears_render_roots(self):
        # Save serializes the rendered DOM, so a root that is not cleared doubles on reopen.
        for tree, name, text in pages():
            if name in DISPLAY:
                continue
            for declaration in re.finditer(r"const (\w+) = document\.getElementById\(", text):
                root, rest = declaration.group(1), text[declaration.end():]
                append = re.search(rf"\b{root}\.appendChild\(", rest)
                if append:
                    with self.subTest(tree=tree, page=name, root=root):
                        clear = re.search(rf'\b{root}\.(replaceChildren\(|innerHTML = ""|'
                                          rf'textContent = ""|length = 1)', rest)
                        self.assertTrue(clear and clear.start() < append.start(), "clear before first append")

    def test_innerhtml_interpolations_escaped(self):
        for tree, name, text in pages():
            for literal in re.findall(r"innerHTML\s*=\s*`([^`]*)`", text):
                with self.subTest(tree=tree, page=name):
                    self.assertNotRegex(literal, r"\$\{\s*\w+\.\w+\s*(\}|\|\||\?\?)")
            if name == "module-map":
                with self.subTest(tree=tree, page=name):
                    self.assertIn("function escapeHtml(", script(text))

    def test_data_links_require_http(self):
        for tree, name, text in pages():
            code = script(text)
            sinks = list(HREF_SINK.finditer(code))
            if name in ("annotated-pr", "weekly-status"):
                self.assertTrue(sinks, f"{name} lost its data-fed link")
            for sink in sinks:
                source = next(group for group in sink.groups() if group)
                with self.subTest(tree=tree, page=name, source=source):
                    window = code[max(0, sink.start() - 300):sink.start()]
                    self.assertIn(HTTP_GUARD + source, window)
                    self.assertNotRegex(window, r"!\s*\(?\s*" + re.escape(HTTP_GUARD + source))

    def test_reopen_resets_runtime_state(self):
        for tree, name, text in pages():
            code = script(text)
            found = {}
            for statement in LOAD_RESETS.get(name, ()):
                with self.subTest(tree=tree, page=name, statement=statement):
                    match = re.search(rf"\n  {re.escape(statement)}\n", code)
                    self.assertIsNotNone(match)
                    found[statement] = match.start()
                    variable = statement.split(".")[0]
                    declaration = re.search(rf"\b(?:const|let|var) {variable}\b", code)
                    self.assertTrue(declaration and declaration.start() < match.start(), f"{variable} not declared first")
            if name == "ticket-triage" and len(found) == 2:
                with self.subTest(tree=tree, page=name, check="capture before restore"):
                    capture, restore = LOAD_RESETS[name]
                    self.assertLess(found[capture], found[restore])

    def test_animation_save_strips_runtime_state(self):
        # The runtime style holds raw property values, so Save must serialize a clone without it.
        for tree, name, text in pages():
            if name != "animation-sandbox":
                continue
            with self.subTest(tree=tree):
                save = re.search(r"async function savePlanHtml\(\) \{(.*?)\n  \}\n", script(text), re.S).group(1)
                self.assertIn("const doc = document.documentElement.cloneNode(true);", save)
                self.assertLess(save.index("dataEl.textContent ="), save.index("cloneNode(true)"))
                serialize = save.index('"<!doctype html>\\n" + doc.outerHTML')
                for sanitizer in ('doc.querySelector("#" + STYLE_ID).textContent = "";',
                                  'doc.querySelector("#target").removeAttribute("style");'):
                    self.assertIn(sanitizer, save)
                    self.assertLess(save.index("cloneNode(true)"), save.index(sanitizer))
                    self.assertLess(save.index(sanitizer), serialize)
                self.assertNotIn("document.documentElement.outerHTML", save)

    def test_skill_pickers_list_every_template(self):
        for tree, skill in SKILLS.items():
            with self.subTest(tree=tree):
                path = skill / "SKILL.md"
                self.assertTrue(path.is_file(), f"missing {path}")
                text = path.read_text()
                frontmatter = FRONTMATTER.match(text)
                self.assertIsNotNone(frontmatter)
                self.assertEqual(frontmatter.group(1), "html-artifact")
                self.assertNotIn(": ", frontmatter.group(2))
                for name in NAMES:
                    self.assertIn(f"templates/{name}.html", text)

    def test_skill_check_command(self):
        # The documented check must pass a fresh copy of every template and reject a raw "<" in the block.
        with tempfile.TemporaryDirectory() as temp:
            bad = Path(temp) / "bad.html"
            bad.write_text('<script type="application/json" id="plan-data">{"html": "<b>x</b>"}</script>')
            for tree, skill in SKILLS.items():
                command = CHECK_COMMAND.search((skill / "SKILL.md").read_text()).group(1)
                cases = [(page, 0) for page in listing(skill / "templates") if page.suffix == ".html"]
                for path, expected in cases + [(bad, 1)]:
                    with self.subTest(tree=tree, page=path.name):
                        result = subprocess.run(["sh", "-c", command], env={**os.environ, "OUT": str(path)},
                                                capture_output=True)
                        self.assertEqual(result.returncode != 0, bool(expected), result.stderr.decode())


if __name__ == "__main__":
    unittest.main()
