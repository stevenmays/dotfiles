# Mays for Codex

This package contains independently maintained Codex instructions. The repository root remains the Claude package. The Codex marketplace targets this directory so Claude commands, agents, and hooks cannot enter the package through default discovery.

The eight skills cover strict maintainability review, deslop, frontend craft, skill optimization, long-form writing, serverless AWS, onboarding, and merge conflicts. Strict review preserves its explicit-only invocation policy. Other skills use concise descriptions for normal discovery.

`ste-writing` is excluded. Routine writing uses the model's default behavior; the optional [personal template](templates/AGENTS.user.md) adds only brief plain-language preferences. The `writing-style` skill applies to requested essays and articles in Steven's voice. Gemini image generation is also excluded; frontend craft uses the session's built-in image capability when available.

## Develop and install

From the repository root, run `make sync-codex` after changing a resource listed in [shared-resources.json](shared-resources.json). Commit the copied resources so the installed package works without access to parent directories. `make check` detects stale copies, missing resources, duplicate skill identities, and legacy package leakage. Skill entrypoints are never synchronized between platforms.

Install from a local checkout:

```sh
codex plugin marketplace add /absolute/path/to/dotfiles
codex plugin add mays@dotfiles
```

When iterating, update the Codex version cachebuster with the plugin-creator helper, then reinstall. Start a new thread to load the changed catalog. The old root Codex manifest is retired; never reinstall the repository root as a Claude compatibility import into Codex.

The personal template is opt-in: merge desired preferences into your user `AGENTS.md`. Installing this plugin does not overwrite global instructions or host permissions.

## Validate behavior

[evals/cases.json](evals/cases.json) records positive and negative routing cases and observable outcomes. Compare matched tasks on a pinned model and reasoning effort, with equivalent tools and fresh fixtures. Save raw outputs outside the repository. Record loaded skills, checks, pauses, tool calls, usage when available, and failures. Use separate held-out cases before claiming reliability improvements.

The [initial validation results](evals/RESULTS.md) include package checks, four writing samples, and two independent workflow executions, with untested cases identified explicitly.

Writing comparisons must include an arm without `ste-writing`; a smaller prompt alone does not prove clearer writing. A short smoke test can detect obvious regressions but cannot establish that Astra never needs writing guidance. Preserve useful preferences only when actual outputs justify them.

## Safety and compatibility

Claude's hooks stay in the Claude package. This port does not claim equivalent enforcement: Codex's host sandbox and approvals govern execution, and these skills grant no additional permissions. Git instructions preserve unrelated changes and distinguish merge from rebase continuation. A dedicated native hook port needs its own enforcement tests before advertising parity.

The serverless skill preserves the domain constraints without copying examples that assume a single-record SQS batch or process-local deduplication. The Gemini helper is not bundled, so its old SDK and model assumptions do not affect this package.

The split follows OpenAI's guidance on [focused skills and selective context](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) and [skill discovery](https://learn.chatgpt.com/docs/build-skills). Astra's [writing guidance](https://developers.openai.com/api/docs/guides/latest-model) notes verbosity and recurring phrasing; the decision to omit the large writing skill is a user preference to evaluate in practice.
