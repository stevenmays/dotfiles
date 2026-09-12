# Isolated Codex runs

Check `codex exec --help` for the installed CLI before constructing a run. Use a fresh disposable fixture for each execution and pin the chosen model and reasoning effort. For analysis-only cases, use the read-only sandbox; allow writes only in a disposable workspace for implementation cases. Do not bypass sandboxing or approval controls to make an evaluation pass.

On a CLI with these options, a single analysis run can use:

```sh
codex exec --ephemeral --ignore-user-config --skip-git-repo-check \
  --sandbox read-only --model MODEL \
  -c 'model_reasoning_effort="medium"' \
  --cd FIXTURE --json --output-last-message OUTPUT - < PROMPT
```

Replace `MODEL`, `FIXTURE`, `OUTPUT`, and `PROMPT` with the pinned model and absolute paths for that run. Supply prompts through files or standard input, not shell interpolation of task text.

`--ephemeral` avoids persistent session files; it does not isolate credentials, globally installed skills, plugins, or all host instructions. `--ignore-user-config` alone is not a complete clean-room environment. Inspect the loaded catalog and settings. Use a dedicated evaluation home with authorized authentication when isolation requires it, or record the remaining contamination. Do not copy credentials into outputs or committed fixtures.

For an execution comparison, install only the selected skill variant in the fixture's `.agents/skills/` and explicitly invoke it. Install needed resources with it. For trigger comparisons, expose the intended catalog and give the natural task without naming a skill. Record actual skill reads as well as the final outcome; asking the model which skill it would choose is only a routing probe.

Capture JSON events and the final output. Record exit status, completed outcome checks, tool calls, clarification pauses, elapsed time, and usage when the CLI reports it. A successful process exit alone does not mean the task succeeded.

Keep model-call budgets explicit. For two variants, four inputs, and two repeats, the execution budget is 16 calls before grading. Include any grader calls in the total. Do not reuse a conversation between variants or claim a statistically established improvement from a small smoke test.
