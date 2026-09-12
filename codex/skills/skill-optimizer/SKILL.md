---
name: skill-optimizer
description: Benchmark and improve an existing skill through bounded experiments when the user requests skill optimization or evaluation.
---

# Skill optimizer

Keep changes only when they improve observed outcomes or preserve quality with less instruction overhead. Preserve the original skill until the user authorizes applying the result.

Establish the target, representative inputs, observable success criteria, model, and execution budget. Reuse details already supplied. A request to review a skill does not authorize running hundreds of model calls. When the execution budget is unspecified, propose a concrete small batch and its call count before launching paid experiments; continue preparing inputs and checks meanwhile.

Use at least three training inputs and a separate held-out input for a meaningful optimization run. Prefer checks of task outcomes over word counts, required headings, or self-assigned scores. For subjective criteria, use a blind assessment that sees the task and output without the variant label or mutation history.

Run in an isolated temporary workspace. Keep baseline and candidate copies, inputs, outputs, per-case results, and a short change log. Do not place experiment artifacts in the target repository.

For CLI execution and isolation requirements, read [references/codex-runs.md](references/codex-runs.md). Keep the model, reasoning effort, tool access, fixtures, and host instructions constant across comparisons. A change to any of these creates a new baseline.

Measure the original first. Change one hypothesis at a time: remove redundant instructions, narrow a trigger, clarify a decision boundary, or add missing domain information. Compare matched inputs. Repeat uncertain results within the agreed budget; do not call a one-run difference a reliability gain.

Keep improvements and revert regressions in the candidate copy. Test the final candidate on the held-out input. Stop at the agreed budget, on user interruption, or when further experiments no longer add useful evidence. Report incomplete or contaminated runs honestly.

Deliver the candidate diff, baseline and candidate outcomes, held-out result, total calls, and remaining failures. Apply the candidate if the request already authorized implementation; otherwise leave the original intact and provide the reviewable files.
