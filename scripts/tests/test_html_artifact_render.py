"""Render html-artifact templates in headless Chrome and check the DOM after their scripts run."""

from collections import Counter
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "skills/html-artifact/templates"
DATA = re.compile(r'(<script type="application/json" id="plan-data">)(.*?)(</script>)', re.S)
MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def find_chrome():
    candidates = [os.environ.get("CHROME"), *map(shutil.which, ("google-chrome", "chromium", "chromium-browser")),
                  MAC_CHROME]
    return next((c for c in candidates if c and Path(c).is_file()), None)


CHROME = find_chrome()


def sample(template):
    return json.loads(DATA.search((TEMPLATES / f"{template}.html").read_text()).group(2))


def dump_dom(path):
    with tempfile.TemporaryDirectory() as profile:
        # Without --incognito, Chrome on macOS prints the DOM and then hangs while shutting down the profile.
        result = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
                                 "--no-default-browser-check", "--incognito", f"--user-data-dir={profile}",
                                 "--enable-logging=stderr", "--v=0", "--dump-dom", path.as_uri()],
                                capture_output=True, text=True, timeout=60, check=True)
    return result.stdout, result.stderr


def render(template, data=None, edits=()):
    """Render a copy of a template with `data` as its data block and each (pattern, replacement) edit applied once."""
    text = (TEMPLATES / f"{template}.html").read_text()
    if data is not None:
        block = json.dumps(data, indent=2).replace("<", "\\u003c")
        text = DATA.sub(lambda m: f"{m.group(1)}\n{block}\n{m.group(3)}", text, count=1)
    for pattern, replacement in edits:
        text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f"edit pattern not found in {template}: {pattern}")
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / f"{template}.html"
        path.write_text(text)
        return dump_dom(path)


class Tabs(HTMLParser):
    """Attributes of each tab button and tab panel, keyed by the panel id."""

    def __init__(self, dom):
        super().__init__()
        self.buttons, self.panels = {}, {}
        self.feed(dom)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("role") == "tab":
            self.buttons[attrs["aria-controls"]] = attrs
        elif attrs.get("role") == "tabpanel":
            self.panels[attrs["id"]] = attrs

    def hidden_buttons(self):
        return {panel for panel, attrs in self.buttons.items() if "hidden" in attrs}

    def selected(self):
        return [panel for panel, attrs in self.buttons.items() if attrs.get("aria-selected") == "true"]

    def shown_panels(self):
        return [panel for panel, attrs in self.panels.items() if "hidden" not in attrs]


class Outline(HTMLParser):
    """Section headings, table-of-contents labels, counts of each tag and class, and attributes by id."""

    def __init__(self, dom):
        super().__init__()
        self.headings, self.toc, self.tags, self.classes = [], [], Counter(), Counter()
        self.attrs = {}
        self._in_toc, self._capture = False, None
        self.feed(dom)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags[tag] += 1
        self.classes.update((attrs.get("class") or "").split())
        if tag == "html" or "id" in attrs:
            self.attrs[attrs.get("id", tag)] = attrs
        if tag == "nav" and attrs.get("id") == "toc":
            self._in_toc = True
        if tag == "h2" or (tag == "a" and self._in_toc):
            self._capture = (tag, [])

    def handle_endtag(self, tag):
        if tag == "nav":
            self._in_toc = False
        if self._capture and tag == self._capture[0]:
            (self.headings if tag == "h2" else self.toc).append("".join(self._capture[1]).strip())
            self._capture = None

    def handle_data(self, data):
        if self._capture:
            self._capture[1].append(data)


@unittest.skipUnless(CHROME, "needs Chrome or Chromium; set CHROME to its path")
class ImplementationPlanTabs(unittest.TestCase):
    ALL = {"tab-phases", "tab-mockups", "tab-dataflow", "tab-risks", "tab-decisions", "tab-progress"}

    def tabs(self, data=None, edits=()):
        dom, stderr = render("implementation-plan", data, edits)
        self.assertNotIn("Uncaught", stderr)
        tabs = Tabs(dom)
        self.assertEqual(set(tabs.buttons), self.ALL)
        return tabs

    def test_sample_hides_only_progress(self):
        tabs = self.tabs()
        self.assertEqual(tabs.hidden_buttons(), {"tab-progress"})
        self.assertIn("hidden", tabs.panels["tab-progress"])
        self.assertEqual(tabs.selected(), ["tab-phases"])
        self.assertEqual(tabs.shown_panels(), ["tab-phases"])

    def test_empty_plan_shows_only_phases(self):
        data = {**sample("implementation-plan"), "mockups": [], "risks": [], "decisions": [], "progress_log": []}
        tabs = self.tabs(data, edits=[(r"<svg\b.*?</svg>", "")])
        self.assertEqual(tabs.hidden_buttons(), self.ALL - {"tab-phases"})
        self.assertEqual(tabs.selected(), ["tab-phases"])
        self.assertEqual(tabs.shown_panels(), ["tab-phases"])

    def test_saved_on_empty_tab_reopens_on_phases(self):
        # Save serializes the live DOM, so a file saved on Progress carries that selection in its markup.
        saved_on_progress = [
            (r'aria-selected="true" id="tab-phases-btn"', 'aria-selected="false" id="tab-phases-btn"'),
            (r'aria-selected="false" id="tab-progress-btn"', 'aria-selected="true" id="tab-progress-btn"'),
            (r'aria-labelledby="tab-phases-btn">', 'aria-labelledby="tab-phases-btn" hidden>'),
            (r'aria-labelledby="tab-progress-btn" hidden>', 'aria-labelledby="tab-progress-btn">'),
            (r'id="tab-mockups-btn"', 'id="tab-mockups-btn" hidden'),
        ]
        tabs = self.tabs(edits=saved_on_progress)
        self.assertEqual(tabs.selected(), ["tab-phases"])
        self.assertEqual(tabs.hidden_buttons(), {"tab-progress"})
        self.assertIn("hidden", tabs.panels["tab-progress"])
        self.assertEqual(tabs.shown_panels(), ["tab-phases"])

    def test_arrow_keys_skip_hidden_tabs(self):
        press_left = (r"</body>", '<script>document.getElementById("tab-phases-btn").dispatchEvent('
                                  'new KeyboardEvent("keydown", {key: "ArrowLeft"}));</script></body>')
        tabs = self.tabs(edits=[press_left])
        self.assertEqual(tabs.selected(), ["tab-decisions"])
        self.assertEqual(tabs.shown_panels(), ["tab-decisions"])


@unittest.skipUnless(CHROME, "needs Chrome or Chromium; set CHROME to its path")
class PlanDocument(unittest.TestCase):
    # (section heading, table-of-contents label) for the shipped sample, in page order.
    SECTIONS = [("Review verdicts", "Review"), ("Problem", "Problem"), ("How it works", "How it works"),
                ("State machine", "State machine"), ("Behavior changes", "Behavior"), ("Approach", "Approach"),
                ("Changes in build order", "Changes"), ("Gates you run, in order", "Gates"),
                ("Acceptance criteria", "Acceptance"), ("Test plan", "Test plan"), ("Open questions", "Questions"),
                ("Risks and rollback", "Risks"), ("Non-goals", "Non-goals")]
    XSS = "<img src=x onerror=alert(1)>"

    def outline(self, data=None, edits=()):
        dom, stderr = render("plan-document", data, edits)
        self.assertNotIn("Uncaught", stderr)
        return dom, Outline(dom)

    def assertSections(self, outline, sections):
        self.assertEqual(outline.headings, [heading for heading, _ in sections])
        self.assertEqual(outline.toc, [label for _, label in sections])

    def test_sample_shows_every_section(self):
        _, outline = self.outline()
        self.assertSections(outline, self.SECTIONS)
        self.assertEqual(outline.classes["dg-node"], 12)

    def test_empty_keys_drop_their_sections(self):
        data = {**sample("plan-document"), "diagram": None, "questions": [], "gates": [], "extra_sections": []}
        _, outline = self.outline(data)
        emptied = {"State machine", "Gates you run, in order", "Open questions", "Non-goals"}
        self.assertSections(outline, [s for s in self.SECTIONS if s[0] not in emptied])
        self.assertEqual(outline.classes["dg-node"], 0)

    def test_markup_in_data_renders_as_text(self):
        data = sample("plan-document")
        data["plan_title"] = f"title {self.XSS}"
        data["problem"][0] = f"problem {self.XSS}"
        data["units"][0]["text"] = f"unit {self.XSS}"
        data["risks"][0]["text"] = f"risk **{self.XSS}**"
        data["gates"][0]["step"] = f"gate `{self.XSS}`"
        node = data["diagram"]["nodes"][0]
        node["label"] = self.XSS
        # An injected onerror alert would block headless Chrome until the timeout, so make alert a no-op.
        dom, outline = self.outline(data, edits=[(r"<head>", "<head><script>window.alert = () => {};</script>")])
        self.assertEqual(outline.tags["img"], 0)
        self.assertNotIn("<img", dom)
        text = escape(self.XSS, quote=False)
        for fragment in (f"title {text}", f"problem {text}", f"unit {text}", f"<strong>{text}</strong>",
                         f"<code>{text}</code>", f"<title>{text}, {node['sub']}</title>"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, dom)

    def test_opens_light_and_toggle_switches_to_dark(self):
        click = (r"</body>", '<script>document.getElementById("btn-theme").click();</script></body>')
        for edits, theme, pressed in (((), "light", "false"), ((click,), "dark", "true")):
            with self.subTest(theme=theme):
                dom, outline = self.outline(edits=edits)
                self.assertEqual(outline.attrs["html"]["data-theme"], theme)
                self.assertEqual(outline.attrs["btn-theme"]["aria-pressed"], pressed)
                # aria-pressed carries the state, so the label never changes.
                self.assertRegex(dom, r'id="btn-theme"[^>]*>Dark mode</button>')


if __name__ == "__main__":
    unittest.main()
