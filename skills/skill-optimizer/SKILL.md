---
name: skill-optimizer
description: Use when optimizing, benchmarking, or improving an existing skill that works but is inconsistent — runs an autonomous mutation-and-scoring loop with binary evals, keeps improvements, discards regressions, and produces a changelog. Triggers include "optimize this skill", "improve this skill", "benchmark skill", "run evals on skill", "make this skill more reliable", "tighten this skill", "this skill works but is flaky". Not for creating skills from scratch — skill-creator covers that.
---

# Skill Optimizer

Take a skill that works but is inconsistent and push it from ~70% to ~95% reliability through an autonomous experiment loop.

**This is NOT for creating skills from scratch.** Use skill-creator for that. This picks up after the skill exists and mostly works, but fails too often. This finds out why and fixes it.

## Core Loop

```
measure baseline → analyze failures → hypothesize one change → mutate → re-measure → keep or revert → repeat
```

One change at a time. If the score goes up, keep it. If not, revert. That's it.

## Before Starting: Gather Context

**Do not run experiments until all fields are confirmed with the user.**

1. **Target skill** — Path to the SKILL.md to optimize
2. **Test inputs** — 3-5 prompts that cover different use cases (variety prevents overfitting to one scenario)
3. **Eval criteria** — 3-6 binary yes/no checks that define "good output" (see Writing Good Evals section below)
4. **Runs per experiment** — How many times to run the skill per mutation. Default: 5
5. **Budget cap** — Max experiment cycles before stopping. Default: 10. Hard max: 25.

Before the user confirms, state the cost: roughly `(budget cap + 1) × runs × inputs` isolated `claude -p` calls, plus grading calls. At the defaults that is 150-250 full skill executions. Let the user shrink the run count or cap if that's more than the skill is worth.

Reserve one of the test inputs as **held-out**: never score it during the loop, never let it inform a mutation. It's the overfitting check in Step 6. Gather at least 4 inputs total so the loop still covers 3+ use cases, and count only loop inputs in the cost formula.

### Eval Rules

Every eval must be a binary yes/no question. No scales. No vibes.

For code/technical skills, prefer objective evals that don't require self-grading:

| Eval type | Example | Reliability |
|-----------|---------|-------------|
| **Execution** | Does the code run without errors? | High — actually run it |
| **Lint/typecheck** | Zero lint warnings? Zero type errors? | High — run the tool |
| **Test pass** | Do the generated tests pass? | High — run them |
| **Structural** | Does output contain required sections? | Medium — grep/parse |
| **Absence** | Zero TODOs or placeholder comments? | Medium — grep |
| **Subjective** | Is the code well-organized? | Low — self-grading bias |

**Prefer evals in the top half of this table.** Every eval you can check by running a command is worth three you check by reading the output.

If you must use subjective evals, acknowledge the bias: the same model grading its own output will systematically over-rate it. Mitigate two ways: make criteria as specific as possible, and grade with a separate `claude -p` call that sees only the eval question and the output — never the skill text or the experiment history.

See the **Writing Good Evals** section below for detailed guidance.

## Step 1: Read the Skill

Read the full SKILL.md and any referenced files. Understand the core job, process steps, output format, and existing quality checks before changing anything.

## Step 2: Set Up Working Directory

Create the workspace **outside the skill's repo** — in the session scratchpad or a temp directory — so experiment artifacts never end up committed:

```
optimizer-[skill-name]/
├── optimized.md          # working copy — all mutations happen here
├── baseline.md           # original skill, untouched (revert target)
├── previous.md           # last KEPT version (revert target for the current experiment)
├── inputs/               # test inputs as files, one per input — experiments must be reproducible
│   ├── input1.txt
│   └── heldout.txt       # never scored during the loop
├── results.tsv           # aggregate score log, one row per experiment
├── scores/               # per-experiment matrix: one row per (input, run), one column per eval, 0/1 cells
│   └── exp0.tsv
├── changelog.md          # mutation log (the most valuable artifact)
└── outputs/              # saved outputs from each experiment
    ├── exp0-run1.txt
    ├── exp0-run2.txt
    └── ...
```

The `scores/` matrices are what make failure analysis possible: "which evals fail most, on which inputs" is a column/row sum, not a re-read of every output. Fill them in as you grade.

**Copy the original SKILL.md to `optimized.md`, `baseline.md`, and `previous.md`. NEVER edit the original.**

Initialize `results.tsv`:
```
experiment	score	max_score	pass_rate	status	description
```

## Step 3: Establish Baseline (Experiment 0)

Run the skill as-is before changing anything.

### Claude Code (preferred)

Use `claude -p` for each run to get isolated execution with no memory between runs. Inject the skill via `--append-system-prompt` — that approximates how a triggered skill lands in context, while the task stays in the user turn:

```bash
claude -p "$(cat inputs/input1.txt)" \
  --append-system-prompt "$(cat optimized.md)" \
  --model <same model every experiment> \
  > outputs/exp0-run1.txt 2>&1
```

Pin `--model` for the whole optimization run. A model change mid-loop makes every score before it incomparable to every score after it.

Runs are independent — launch them in parallel (background them, collect as they finish) rather than waiting on each one serially.

Run [N] times across the test inputs. Score every output against every eval.

For execution-based evals, actually run the generated code:
```bash
# Save generated code to temp file, execute it, check exit code
node outputs/exp0-run1.js 2>&1
echo "Exit code: $?"
```

### Claude.ai (fallback)

Without `claude -p`, you run the skill sequentially in the same context window. This means:
- **Contamination risk**: Later runs are influenced by earlier outputs. Acknowledge this in results.
- **Mitigation**: Vary the test input order across experiments. Start each run with a clean framing: "Forget previous outputs. Apply the skill fresh to this input."
- **Reduced run count**: 3 runs per experiment instead of 5 (contamination makes more runs less useful, not more).

### Record Baseline

Log to `results.tsv`:
```
0	14	20	70.0%	baseline	original skill — no changes
```

**Confirm baseline with user before proceeding.** If already 90%+, ask if optimization is worth pursuing.

## Step 4: Run the Experiment Loop

Once the user confirms, run autonomously.

### Each Cycle

**1. Analyze failures.** Read the actual failing outputs. Which evals fail most? What pattern causes the failure — missing instruction, ambiguous wording, wrong priority?

**2. Hypothesize one change.** Pick ONE thing to change. Not five.

Good mutations:
- Add a specific instruction addressing the most common failure mode
- Reword an ambiguous instruction to be explicit
- Add an anti-pattern for a recurring mistake
- Move a buried instruction higher (position = priority)
- Add or improve a worked example showing correct behavior
- Remove an instruction that causes over-optimization for one eval at the expense of others
- Simplify — fewer words that say the same thing

Bad mutations:
- Rewriting the entire skill
- Adding multiple rules at once (can't attribute improvement)
- Adding vague instructions ("be more careful", "improve quality")
- Making the skill longer without targeting a specific failure

**3. Edit `optimized.md`** with the one change.

**4. Run the skill** [N] times with the same test inputs.

**5. Score every output** against every eval. Record the 0/1 matrix in `scores/exp[N].tsv`. Grade subjective evals blind: the grader call sees the eval question and the output, never which experiment produced it — a grader that knows "this is the improved version" finds improvement.

**6. Keep or revert.** Small deltas are noise: on 5 runs, a single flipped eval is within run-to-run variance. If the delta is within ±1 eval of the previous score, re-run the experiment once and use the combined tally before deciding.
- Score improved beyond noise → **KEEP.** Copy `optimized.md` over `previous.md`. This is the new baseline.
- Score unchanged → **REVERT** — unless the change was a pure simplification (shorter skill, same score). Keep those: same reliability at lower context cost is a win. Every keep — simplifications included — copies `optimized.md` over `previous.md`, or the next revert erases it.
- Score decreased → **REVERT.** Copy `previous.md` over `optimized.md`.

**7. Log to `results.tsv` and `changelog.md`.**

**8. Repeat** from step 1 of the loop.

### Stopping Conditions

Stop when ANY of these hit:
- Budget cap reached (default 10 experiments)
- 95%+ pass rate for 3 consecutive experiments
- User manually stops you

**Do not run indefinitely.** The budget cap exists to prevent runaway API costs. If you hit the cap and haven't reached 95%, deliver what you have and let the user decide whether to continue.

### When You're Stuck

If the last 3 experiments were all reverted:
- Re-read the failing outputs with fresh eyes
- Try combining two previous near-miss mutations
- Try removing instructions instead of adding them
- Try a completely different approach to the same failure
- If nothing works after 3 more attempts, stop and report — the remaining failures may require a structural change the user should decide on

## Step 5: Write the Changelog

After each experiment (kept or reverted), append to `changelog.md`:

```markdown
## Experiment [N] — [KEEP/REVERT]

**Score:** [X]/[max] ([percent]%)
**Change:** [One sentence describing what was changed]
**Hypothesis:** [Why this was expected to help]
**Result:** [Which evals improved/declined]
**Remaining failures:** [What still fails, if anything]
```

**The changelog is the most valuable output.** It's a research log that any future agent (or smarter model) can pick up and continue from. Write it for someone who hasn't seen the skill before.

## Step 6: Validate and Deliver Results

**Held-out check first.** Run the final `optimized.md` on the held-out input [N] times and score it. If its pass rate roughly matches the loop's final rate, the improvement generalizes. If it collapses, you overfit — report both numbers and flag which kept mutations look input-specific; don't quietly present the loop score as the result.

Then present:

1. **Score trajectory:** Baseline → Final (percent improvement), plus the held-out pass rate
2. **Experiments:** Total run, kept, reverted
3. **Top changes that helped** (from changelog)
4. **Remaining failure patterns** (what the skill still gets wrong)
5. **Location of `optimized.md`** — the improved skill (original is untouched)
6. **Location of `changelog.md` and `results.tsv`** for reference

**Do NOT overwrite the original SKILL.md.** The user reviews the diff and applies changes manually.

## The Test

A good optimization run:

1. Started with a baseline before changing anything
2. Used binary evals only — no scales, no subjective ratings
3. Changed one thing at a time
4. Kept a complete changelog
5. Measurably improved the score
6. Didn't overfit — the held-out input confirms the skill got better at the job, not just at passing specific test inputs
7. Stayed within budget

If the skill passes all evals but output quality hasn't actually improved — the evals are bad. Go back and write better evals.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Too many evals (7+) | Skill games the evals instead of improving. Use 3-6. |
| All subjective evals | Self-grading bias inflates scores. Add execution-based evals. |
| No budget cap | Runaway API costs. Always set a cap. |
| Multiple changes per experiment | Can't attribute improvement. One change at a time. |
| Never reverting | If nothing gets reverted, your evals might be too easy. |
| Treating ±1 as signal | On 5 runs, one flipped eval is noise. Re-run before keep/revert. |
| Skipping baseline | You can't measure improvement without a starting point. |
| Overfitting to test inputs | Use varied inputs and a held-out input. If loop score is 95% but held-out collapses, the mutations are input-specific — remove the most targeted ones and re-measure. |
| Grader sees experiment context | A grader that knows which version it's grading finds improvement. Grade blind: eval question + output only. |

## Writing Good Evals

### The Golden Rule

Every eval must be a yes/no question. Not a scale. Not a vibe check. Binary. Scales compound variability and give unreliable signal.

### Examples by Skill Type

**Code/technical skills:**
- "Does the code run without errors?" (execute it — check exit code)
- "Does it pass linting with zero warnings?" (run the linter)
- "Does the output contain zero TODO or placeholder comments?" (grep)
- "Does the code include error handling for all external calls?" (structural)
- "Does the generated test suite pass when run against the generated code?" (execute both)

**Text/copy skills:**
- "Does the output contain zero phrases from this banned list: [list them]?" (greppable)
- "Does the opening sentence reference a specific time, place, or sensory detail?" (checkable)
- "Is the output between 150-400 words?" (measurable)

**Document skills:**
- "Does the document contain all required sections: [list them]?" (structural)
- "Is every claim backed by a specific number, date, or source?" (checkable)
- "Does the executive summary fit in 3 sentences or fewer?" (countable)

### Eval Pitfalls

- **Too many evals (7+):** Skill games them instead of improving. Use 3-6.
- **Too narrow:** "Must contain exactly 3 bullet points" creates stilted output. Check qualities, not arbitrary constraints.
- **Overlapping:** If eval 1 is "grammatically correct" and eval 4 is "no spelling errors," you're double-counting. Each eval should test something distinct.
- **Unmeasurable:** "Would a human find this engaging?" — an agent will say "yes" every time. Translate to observable signals: "Does the first sentence contain a specific claim, story, or question?"

### The 3-Question Test

Before finalizing any eval:

1. **Could two different agents score the same output and agree?** If not, too subjective. Rewrite.
2. **Could a skill game this eval without actually improving?** If yes, too narrow. Broaden.
3. **Does this eval test something the user actually cares about?** If not, drop it.

### Eval Template

```
EVAL [N]: [Short name]
Question: [Yes/no question]
Pass: [What "yes" looks like — one sentence]
Fail: [What triggers "no" — one sentence]
Check method: [How to verify — execute, grep, parse, or read]
```
