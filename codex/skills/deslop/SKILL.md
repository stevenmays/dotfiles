---
name: deslop
description: Remove redundant code and simplify complex implementations when the user asks to deslop or refactor for maintainability. Changes code.
---

# Deslop

Preserve observable behavior while removing unnecessary complexity in the requested scope. A branch cleanup covers the branch's changes; a file or directory cleanup covers that target. Establish the actual base before using a branch diff.

Look for dead code, duplicate helpers, speculative abstractions, pass-through wrappers, comments that restate code, and checks already enforced at an upstream boundary. Preserve guards at external boundaries and compatibility required by real consumers.

Delete unnecessary code first. Reuse an existing implementation next. Restructure only the complexity that remains. Prefer clear control flow and cohesive functions over compressed expressions or extra indirection.

Use the project's complexity tooling when useful. Without configured limits, complexity above 15, nesting of four levels, and files approaching 1,000 lines are investigation signals. Report measured values as measurements; label estimates. Do not install a tool solely to assign numbers to a trivial deletion.

Before changing public signatures, inspect consumers and compatibility commitments. A missing local caller does not prove that an exported API has no users. Preserve the contract unless its change is authorized; continue independent internal cleanup if that decision needs clarification.

Choose checks that can detect behavior changes in the affected paths. For risky untested logic, add focused characterization tests before restructuring. Run affected tests after a coherent change, and complete required project checks. Repeat or broaden validation when failures or new changes justify it.

Finish with the main simplification, relevant measurements if collected, checks and results, and any unresolved risk. Continue until the requested cleanup and validation are complete; do not turn the initial assessment into an approval checkpoint.
