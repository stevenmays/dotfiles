#!/usr/bin/env python3
"""Validate, edit, and schedule a teach-me learning ledger."""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path

RESULTS = ("learned", "solid", "shaky", "miss")
SEVERITY = {"solid": 1, "shaky": 2, "miss": 3}
DUE_ORDER = {"miss": 0, "shaky": 1, "solid": 2}
START_EASE = Fraction(5, 2)
MIN_EASE = Fraction(13, 10)
SHAKY_PENALTY = Fraction(15, 100)
MISS_PENALTY = Fraction(20, 100)
CREDIT_MIN_EASE = Fraction(22, 10)
MAX_INTERVAL = 365
MAX_COVERS = 5
COMING_UP_DAYS = 7

ID = r"[a-z0-9][a-z0-9-]*"
ID_RE = re.compile(ID)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
TOPIC_RE = re.compile(rf"### ({ID})(?: — (\S.*))?")
KP_RE = re.compile(rf"- ({ID}): (\S.*)")
BUILDS_ON_RE = re.compile(r"(.*?) \(builds on: ([^()]*)\)")
LOG_RE = re.compile(r"- (\S+) (\S+) (\S+)(.*)")
SECTIONS = {"## Knowledge points": "kp", "## Log": "log"}
LOG_HEADING = "## Log"

SKELETON = """# Learning ledger

<!-- teach-me ledger v1. Change it with scripts/ledger.py so the format stays parseable. -->

## Knowledge points

## Log
"""


class LedgerError(Exception):
    def __init__(self, messages):
        super().__init__("\n".join(messages))
        self.messages = messages


class UsageError(Exception):
    pass


@dataclass
class Topic:
    id: str
    title: str | None
    line: int


@dataclass
class KnowledgePoint:
    id: str
    topic: str
    statement: str
    builds_on: list[str]
    line: int


@dataclass
class Event:
    day: date
    kp: str
    result: str
    note: str | None
    line: int


@dataclass
class Ledger:
    lines: list[str]
    topics: dict[str, Topic] = field(default_factory=dict)
    kps: dict[str, KnowledgePoint] = field(default_factory=dict)
    events: list[Event] = field(default_factory=list)
    section_end: dict[str, int] = field(default_factory=dict)
    topic_end: dict[str, int] = field(default_factory=dict)


@dataclass
class State:
    learned: bool = False
    ease: Fraction = START_EASE
    interval: int = 0
    last_review: date | None = None
    due: date | None = None
    open_gap: bool = False
    lapses: int = 0
    last_result: str | None = None
    implicit_credits: int = 0
    explicit_reviews: int = 0
    gap_day: date | None = None
    gap_note: str | None = None


@dataclass
class Schedule:
    states: dict[str, State]
    reviews: list[str]


def rhu(x):
    return math.floor(x + Fraction(1, 2))


def round_ease(ease):
    return Fraction(rhu(ease * 100), 100)


def parse_day(text):
    if not DATE_RE.fullmatch(text):
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def split_lines(text):
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def parse(text):
    ledger = Ledger(split_lines(text))
    errors = []
    section = None
    topic = None
    comment_from = None

    for index, raw in enumerate(ledger.lines):
        number = index + 1
        line = raw.rstrip()
        if comment_from is not None:
            if section in SECTIONS.values():
                ledger.section_end[section] = index
            if "-->" in line:
                comment_from = None
            continue
        if not line:
            continue
        if line.lstrip().startswith("<!--"):
            if "-->" not in line.lstrip()[4:]:
                comment_from = number
            if section in SECTIONS.values():
                ledger.section_end[section] = index
            continue
        if line in SECTIONS:
            key = SECTIONS[line]
            if key in ledger.section_end:
                errors.append((number, f"duplicate section heading '{line}'"))
            section, topic = key, None
            ledger.section_end[key] = index
            continue
        if line.startswith("## "):
            errors.append((number, f"unknown section heading '{line}'; expected '## Knowledge points' or '## Log'"))
            section = "unknown"
            continue
        if section == "unknown":
            continue
        if section is None:
            if not line.startswith("# "):
                errors.append((number, "unexpected line before '## Knowledge points'"))
            continue
        ledger.section_end[section] = index
        if section == "log":
            event = parse_event(line, number, errors)
            if event:
                ledger.events.append(event)
        elif line.startswith("#"):
            match = TOPIC_RE.fullmatch(line)
            if not match:
                errors.append((number, "malformed topic heading; expected '### TOPIC_ID' or '### TOPIC_ID — TITLE'"))
                topic = ""
                continue
            topic, title = match.groups()
            if topic in ledger.topics:
                errors.append((number, f"duplicate topic id '{topic}' (first on line {ledger.topics[topic].line})"))
            else:
                ledger.topics[topic] = Topic(topic, title, number)
            ledger.topic_end[topic] = index
        elif line.startswith("- "):
            if topic is None:
                errors.append((number, "knowledge point before any '### TOPIC_ID' heading"))
                continue
            kp = parse_kp(line, number, topic, errors)
            if kp is None:
                continue
            if kp.id in ledger.kps:
                errors.append((number, f"duplicate knowledge point id '{kp.id}' (first on line {ledger.kps[kp.id].line})"))
            else:
                ledger.kps[kp.id] = kp
            ledger.topic_end[topic] = index
        else:
            errors.append((number, "expected a '### TOPIC_ID' heading or a '- KP_ID: STATEMENT' line"))

    if comment_from is not None:
        errors.append((comment_from, "HTML comment is never closed with '-->'"))
    for heading, key in SECTIONS.items():
        if key not in ledger.section_end:
            errors.append((0, f"missing section heading '{heading}'"))
    for kp in ledger.kps.values():
        for ref in kp.builds_on:
            if ID_RE.fullmatch(ref) and ref not in ledger.kps:
                errors.append((kp.line, f"'{kp.id}' builds on unknown id '{ref}'"))
    errors.extend(find_cycles(ledger.kps))
    for event in ledger.events:
        if event.kp not in ledger.kps:
            errors.append((event.line, f"unknown knowledge point '{event.kp}'"))
    if errors:
        errors.sort(key=lambda error: error[0])
        raise LedgerError([f"line {n}: {message}" if n else message for n, message in errors])
    return ledger


def parse_kp(line, number, topic, errors):
    match = KP_RE.fullmatch(line)
    if not match:
        errors.append((number, "malformed knowledge point; expected '- KP_ID: STATEMENT' with an optional ' (builds on: id1, id2)'"))
        return None
    kp_id, statement = match.groups()
    builds_on = []
    suffix = BUILDS_ON_RE.fullmatch(statement)
    if suffix:
        statement, refs = suffix.groups()
        builds_on = [ref.strip() for ref in refs.split(",")]
        bad = [ref for ref in builds_on if not ID_RE.fullmatch(ref)]
        if bad:
            errors.append((number, f"bad id '{bad[0]}' in '(builds on: ...)'"))
            return None
    if "(builds on" in statement:
        errors.append((number, "malformed '(builds on: id1, id2)'; it must end the line"))
        return None
    return KnowledgePoint(kp_id, topic, statement, builds_on, number)


def parse_event(line, number, errors):
    match = LOG_RE.fullmatch(line)
    if not match:
        errors.append((number, "malformed log line; expected '- YYYY-MM-DD KP_ID RESULT' with an optional ' — NOTE'"))
        return None
    day_text, kp_id, result, rest = match.groups()
    day = parse_day(day_text)
    if day is None:
        errors.append((number, f"bad date '{day_text}'; expected a real date as YYYY-MM-DD"))
    elif result not in RESULTS:
        errors.append((number, f"bad result '{result}'; expected learned, solid, shaky, or miss"))
    elif rest and not (rest.startswith(" — ") and rest[3:].strip()):
        errors.append((number, "malformed log line; a note must follow ' — '"))
    else:
        return Event(day, kp_id, result, rest[3:].strip() or None, number)
    return None


def find_cycles(kps):
    errors = []
    visiting, done = set(), set()

    def visit(kp_id, path):
        visiting.add(kp_id)
        path.append(kp_id)
        for ref in kps[kp_id].builds_on:
            if ref not in kps or ref in done:
                continue
            if ref in visiting:
                cycle = path[path.index(ref):] + [ref]
                errors.append((kps[ref].line, f"builds-on cycle: {' -> '.join(cycle)}"))
            else:
                visit(ref, path)
        path.pop()
        visiting.discard(kp_id)
        done.add(kp_id)

    for kp_id in kps:
        if kp_id not in done:
            visit(kp_id, [])
    return errors


def replay(ledger):
    states = {kp_id: State() for kp_id in ledger.kps}
    dependents = defaultdict(list)
    for kp in ledger.kps.values():
        for prereq in kp.builds_on:
            dependents[prereq].append(kp.id)
    days = defaultdict(dict)
    for event in ledger.events:
        days[event.day].setdefault(event.kp, []).append(event)
    reviews = []

    for day in sorted(days):
        graded_today, positive, missed = set(), [], []
        for kp_id, events in days[day].items():
            state = states[kp_id]
            graded = [event.result for event in events if event.result != "learned"]
            worst = max(graded, key=SEVERITY.__getitem__) if graded else None
            last = events[-1]
            if state.learned:
                review(state, day, worst, last)
                if worst:
                    reviews.append(worst)
            else:
                learn(state, day, last)
            state.last_result = worst or "learned"
            if worst:
                graded_today.add(kp_id)
            if worst in (None, "solid"):
                positive.append(kp_id)
            if worst == "miss":
                missed.append(kp_id)

        def untouched(kp_id):
            state = states[kp_id]
            return state.learned and not state.open_gap and kp_id not in graded_today

        penalized = {x: None for p in missed for x in dependents[p] if untouched(x)}
        for kp_id in positive:
            for prereq in ledger.kps[kp_id].builds_on:
                state = states[prereq]
                if untouched(prereq) and prereq not in penalized and state.due <= day and takes_credit(state):
                    credit(state, day)
        for kp_id in penalized:
            states[kp_id].due = min(states[kp_id].due, day + timedelta(days=1))

    return Schedule(states, reviews)


# A shaky, missed, or never-reviewed point needs its own explicit question, so credit can't stand in for it.
def takes_credit(state):
    return state.explicit_reviews > 0 and state.last_result == "solid" and state.ease >= CREDIT_MIN_EASE


def questions_for(state):
    return 2 if state.open_gap or state.last_result in ("shaky", "miss") else 1


def mark_gap(state, day, last):
    state.open_gap = True
    state.due = day
    state.gap_day = day
    state.gap_note = last.note


def learn(state, day, last):
    if last.result == "miss":
        mark_gap(state, day, last)
        return
    state.learned = True
    state.interval = 1
    state.last_review = day
    state.due = day + timedelta(days=1)
    state.open_gap = False


def review(state, day, worst, last):
    late = max(0, (day - state.due).days)
    if worst == "solid":
        if day < state.due:
            elapsed = (day - state.last_review).days
            new = max(state.interval, rhu(elapsed * state.ease))
        else:
            new = max(state.interval + 1, rhu((state.interval + Fraction(late, 2)) * state.ease))
    elif worst == "shaky":
        state.ease = round_ease(max(MIN_EASE, state.ease - SHAKY_PENALTY))
        new = 1
    elif worst == "miss":
        state.ease = round_ease(max(MIN_EASE, state.ease - MISS_PENALTY))
        state.lapses += 1
        new = 1
    else:
        new = 1
    if worst:
        state.explicit_reviews += 1
    state.interval = min(new, MAX_INTERVAL)
    state.last_review = day
    if worst == "miss" and last.result == "miss":
        mark_gap(state, day, last)
    else:
        state.open_gap = False
        state.due = day + timedelta(days=state.interval)


def credit(state, day):
    late = (day - state.due).days
    factor = 1 + (state.ease - 1) / 2
    new = max(state.interval + 1, rhu((state.interval + Fraction(late, 2)) * factor))
    state.interval = min(new, MAX_INTERVAL)
    state.last_review = day
    state.due = day + timedelta(days=state.interval)
    state.implicit_credits += 1


def count(n, noun):
    return f"{n} {noun}" + ("" if n == 1 else "s")


def strength(interval):
    if interval < 7:
        return "fragile"
    return "firm" if interval < 30 else "long-term"


def render_status(ledger, schedule, today, show_all=False):
    kps, states = ledger.kps, schedule.states
    out = [f"Ledger: {count(len(kps), 'knowledge point')} in {count(len(ledger.topics), 'topic')}. Today: {today}."]
    reviews = schedule.reviews
    if reviews:
        solid = reviews.count("solid")
        percent = rhu(Fraction(100 * solid, len(reviews)))
        out.append(f"Retention (reviews after the learning day): {solid} of {len(reviews)} solid ({percent}%).")
    else:
        out.append("Retention (reviews after the learning day): none yet.")
    scheduled = {k: max(s.due, today) for k, s in states.items() if s.due and (s.open_gap or s.learned)}
    if scheduled:
        next_day = min(scheduled.values())
        batch = [k for k, day in scheduled.items() if day == next_day]
        questions = sum(questions_for(states[k]) for k in batch)
        out.append(f"Next review: {next_day}, {count(len(batch), 'knowledge point')}, about {count(questions, 'question')}.")

    body = []
    gaps = sorted((k for k in kps if states[k].open_gap), key=lambda k: states[k].gap_day)
    if gaps:
        body.append("Open gaps (missed, not yet relearned):")
        for k in gaps:
            note = f" — {states[k].gap_note}" if states[k].gap_note else ""
            body.append(f"  {k} [{kps[k].topic}] missed {states[k].gap_day}{note}")

    active = [k for k in kps if states[k].learned and not states[k].open_gap]
    due = [k for k in active if states[k].due <= today]
    due.sort(key=lambda k: (-Fraction((today - states[k].due).days, states[k].interval), DUE_ORDER.get(states[k].last_result, 3)))
    if due:
        body.append("Due now (most overdue first):")
        for k in due:
            s = states[k]
            late = (today - s.due).days
            lateness = f"{count(late, 'day')} late" if late else "on time"
            body.append(f"  {k} [{kps[k].topic}] due {s.due}, {lateness}, last {s.last_result}, interval {s.interval}d")

    creditable = {k for k in due if takes_credit(states[k])}
    covers = [(x, [p for p in kps[x].builds_on if p in creditable]) for x in active]
    covers = sorted((c for c in covers if c[1]), key=lambda c: (-len(c[1]), c[0] not in due))
    for x, prereqs in covers[:MAX_COVERS]:
        body.append(f"Covers: a solid on {x} also credits due {', '.join(prereqs)}.")

    not_learned = [k for k in kps if not states[k].learned and not states[k].open_gap]
    if not_learned:
        body.append(f"Not learned yet: {', '.join(not_learned)}")

    upcoming = Counter(states[k].due for k in active if states[k].due > today)
    if upcoming:
        days = sorted(upcoming)[:COMING_UP_DAYS]
        body.append("Coming up: " + ", ".join(f"{d} ({upcoming[d]})" for d in days))

    if active:
        buckets = Counter(strength(states[k].interval) for k in active)
        body.append(
            f"Strength: {buckets['fragile']} fragile (under 7d), {buckets['firm']} firm (7-29d), "
            f"{buckets['long-term']} long-term (30d+)"
        )

    if show_all:
        body.extend(["", *render_table(ledger, states)] if body else render_table(ledger, states))
    return "\n".join(out + ([""] + body if body else []))


def render_table(ledger, states):
    rows = [("id", "topic", "state", "interval", "ease", "last", "due", "lapses")]
    for kp_id, kp in ledger.kps.items():
        s = states[kp_id]
        if s.open_gap:
            state = "open gap"
        elif not s.learned:
            state = "not learned"
        else:
            state = strength(s.interval)
        rows.append((
            kp_id,
            kp.topic,
            state,
            f"{s.interval}d" if s.learned else "-",
            f"{float(s.ease):.2f}",
            s.last_result or "-",
            str(s.due) if s.due else "-",
            str(s.lapses),
        ))
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    return ["All knowledge points:"] + ["  " + "  ".join(c.ljust(w) for c, w in zip(row, widths)).rstrip() for row in rows]


def insert(lines, at, block, gap_before):
    new = ([""] if gap_before else []) + block
    if at < len(lines) and lines[at].strip():
        new.append("")
    lines[at:at] = new


def read(path):
    try:
        return path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise UsageError(f"no ledger at {path}; create one with 'init'") from None
    except OSError as error:
        raise UsageError(f"cannot read {path}: {error.strerror}") from None


def write(path, lines):
    with open(path, "w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines) + "\n")


def cmd_init(args):
    if args.path.exists():
        raise UsageError(f"{args.path} already exists; init never overwrites a ledger")
    try:
        with open(args.path, "x", encoding="utf-8", newline="\n") as file:
            file.write(SKELETON)
    except OSError as error:
        raise UsageError(f"cannot create {args.path}: {error.strerror}") from None
    return f"Created {args.path}."


def cmd_add(args):
    ledger = parse(read(args.path))
    statement = " ".join(" ".join(args.statement).split())
    title = " ".join((args.title or "").split())
    builds_on = [ref.strip() for ref in (args.builds_on or "").split(",") if ref.strip()]
    errors = []
    if not ID_RE.fullmatch(args.topic_id):
        errors.append(f"topic id '{args.topic_id}' must match [a-z0-9][a-z0-9-]*")
    if not ID_RE.fullmatch(args.kp_id):
        errors.append(f"knowledge point id '{args.kp_id}' must match [a-z0-9][a-z0-9-]*")
    elif args.kp_id in ledger.kps:
        errors.append(f"knowledge point id '{args.kp_id}' already exists on line {ledger.kps[args.kp_id].line}")
    if not statement:
        errors.append("statement is empty")
    elif "(builds on" in statement:
        errors.append("statement must not contain '(builds on'; use --builds-on")
    for ref in builds_on:
        if ref == args.kp_id:
            errors.append(f"'{ref}' cannot build on itself")
        elif ref not in ledger.kps:
            errors.append(f"--builds-on names unknown knowledge point '{ref}'")
    if errors:
        raise LedgerError(errors)

    kp_line = f"- {args.kp_id}: {statement}"
    if builds_on:
        kp_line += f" (builds on: {', '.join(builds_on)})"
    lines = list(ledger.lines)
    if args.topic_id in ledger.topics:
        insert(lines, ledger.topic_end[args.topic_id] + 1, [kp_line], gap_before=False)
        message = f"Added {args.kp_id} to topic {args.topic_id}."
    else:
        heading = f"### {args.topic_id}" + (f" — {title}" if title else "")
        insert(lines, ledger.section_end["kp"] + 1, [heading, kp_line], gap_before=True)
        message = f"Added {args.kp_id} to new topic {args.topic_id}."
    parse("\n".join(lines))
    write(args.path, lines)
    return message


def cmd_log(args):
    ledger = parse(read(args.path))
    day = args.date or date.today()
    new_lines, errors = [], []
    for number, entry in enumerate(args.entries, 1):
        words = entry.split()
        if len(words) < 2:
            errors.append(f"entry {number} '{entry}': expected 'KP_ID RESULT [NOTE words...]'")
            continue
        kp_id, result, *note = words
        if kp_id not in ledger.kps:
            errors.append(f"entry {number} '{entry}': unknown knowledge point '{kp_id}'")
        if result not in RESULTS:
            errors.append(f"entry {number} '{entry}': bad result '{result}'; expected learned, solid, shaky, or miss")
        if note and note[0] in ("—", "–", "-", "--"):
            note = note[1:]
        new_lines.append(f"- {day} {kp_id} {result}" + (f" — {' '.join(note)}" if note else ""))
    if errors:
        raise LedgerError(errors)

    lines = list(ledger.lines)
    end = ledger.section_end["log"]
    insert(lines, end + 1, new_lines, gap_before=lines[end].rstrip() == LOG_HEADING)
    updated = parse("\n".join(lines))
    write(args.path, lines)
    return render_status(updated, replay(updated), day)


def cmd_status(args):
    ledger = parse(read(args.path))
    return render_status(ledger, replay(ledger), args.today or date.today(), args.all)


def date_arg(text):
    day = parse_day(text)
    if day is None:
        raise argparse.ArgumentTypeError(f"'{text}' is not a real date as YYYY-MM-DD")
    return day


def build_parser():
    parser = argparse.ArgumentParser(prog="ledger.py", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create an empty ledger")
    init.add_argument("path", type=Path)
    init.set_defaults(run=cmd_init)

    add = commands.add_parser("add", help="add a knowledge point to a topic")
    add.add_argument("path", type=Path)
    add.add_argument("topic_id")
    add.add_argument("kp_id")
    add.add_argument("statement", nargs="+")
    add.add_argument("--title", help="topic title, used only when the topic is new")
    add.add_argument("--builds-on", help="comma-separated prerequisite KP ids")
    add.set_defaults(run=cmd_add)

    log = commands.add_parser("log", help="append results, then print status")
    log.add_argument("path", type=Path)
    log.add_argument("entries", nargs="+", metavar="ENTRY", help='"KP_ID RESULT [NOTE words...]"')
    log.add_argument("--date", type=date_arg, help="log date, YYYY-MM-DD (default: today)")
    log.set_defaults(run=cmd_log)

    status = commands.add_parser("status", help="print what is due and how strong each point is")
    status.add_argument("path", type=Path)
    status.add_argument("--date", "--today", dest="today", type=date_arg, help="YYYY-MM-DD (default: today)")
    status.add_argument("--all", action="store_true", help="add a table with one row per knowledge point")
    status.set_defaults(run=cmd_status)
    return parser


def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exit:
        return exit.code if isinstance(exit.code, int) else 2
    try:
        output = args.run(args)
    except UsageError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except LedgerError as error:
        for message in error.messages:
            print(f"error: {message}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
