---
description: Root-cause a bug methodically — build a red-capable repro loop first, then bisect, hypothesize, fix, and lock it down with a regression test
argument-hint: "[bug description, error message, or failing command]"
---

# Diagnose Bug

Root-cause an unclear bug with a tight feedback loop instead of code-staring and guesswork. For a test suite that is already red with a known cause, use `/test-and-fix`; this command is for bugs where the cause is unknown.

## Steps

1. **Build a feedback loop — this is the skill.** Before reading code to build any theory, construct one command that goes red on this exact bug and will go green when it is fixed: a failing test at whatever seam reaches the bug, a curl against the dev server, a CLI run with a fixture input, a replayed captured payload, or a throwaway harness around the suspect path. Then tighten it: seconds not minutes, deterministic (pin time, seed RNG), asserting the user's exact symptom — not "didn't crash".
   - Intermittent bug: don't chase a clean repro — raise the reproduction rate (loop the trigger 100×, add stress, narrow timing) until it fails often enough to debug against.
   - Genuinely can't build one: stop and say so. List what was tried and ask for a captured artifact (log dump, HAR, payload) or repro access. Never proceed to hypotheses without a loop.
2. **Minimize**: shrink the repro to the smallest scenario that still goes red, cutting inputs, config, and steps one at a time. Done when removing any remaining element turns the loop green — a minimal repro shrinks the hypothesis space and becomes the regression test.
3. **Isolate**: if the bug appeared between two known states, `git bisect run <loop command>` finds the commit mechanically. Otherwise binary-search by layer — API vs data vs logic — re-running the loop after each cut.
4. **Hypothesize — 3–5 ranked and falsifiable** — before testing any of them; a single hypothesis anchors on the first plausible idea. Each must state its prediction: "if X is the cause, changing Y turns the loop green." No prediction means it's a vibe — sharpen or discard it. Show the ranked list to the user (domain knowledge re-ranks instantly), but proceed with your ranking if they're away.
5. **Probe**: one probe per prediction, one variable at a time. Prefer a breakpoint or REPL over logs; when logging, tag every line with one unique prefix (e.g. `[DBG-a4f2]`) so cleanup is a single grep. Never log-everything-and-grep. For performance regressions, logs are the wrong tool: measure a baseline first, then bisect the measurement.
6. **Fix with a regression test first**: turn the minimized repro into a failing test at a seam that exercises the real bug pattern — watch it fail, apply the fix, watch it pass, then re-run the original unminimized loop. If no seam can express the bug honestly (the trigger chain can't be replicated there), that is itself a finding — document it instead of writing a false-confidence test.
7. **Clean up and report**: grep out the tagged instrumentation, delete throwaway harnesses, and state the confirmed hypothesis — and the ruled-out ones — so the fix commit records the why. Then ask what would have prevented the bug: if the answer is structural (no honest test seam, hidden coupling), point at `/extreme-code-quality-review`; if it's a rule a review could check, offer to record it in `.claude/standards.md` `## Manual`.

## Guidelines

- Never guess-and-edit: every code change in this flow is either a probe mapped to a prediction or the fix itself.
- Fix the root cause, not the symptom the loop happens to show.
- If a hypothesis survives 2–3 probes without confirmation, step back to isolation — don't keep poking the same theory.

## Source

Merged from `diagnosing-bugs` in mattpocock/skills and `systematic-debugging` in spencerpauly/awesome-cursor-skills.
