# Port validation, 2026-09-12

The Codex package excludes `ste-writing` and `gemini-image-generator`. Its installed skill catalog contains eight native entries and no migrated Claude commands. These checks support the package migration; they do not establish a general model-performance improvement.

## Package checks

- The official plugin validator and all eight official skill validators passed.
- `make check` passed, including ten tests covering valid packages, invalid manifests, metadata, wrong marketplace roots, duplicate identities, stale shared resources, missing references, escaping links, and symlinks.
- The installed cache contained only the intended skills and no Claude manifest or commands directory.
- Claude's strict-review invocation flag remains in its frontmatter. Codex carries the equivalent existing explicit-only policy in its own `agents/openai.yaml`.
- The optional personal template was not installed into global user configuration. Host permissions were not relaxed and Claude hook parity is not claimed.

## Writing comparison

Four fresh CLI calls requested `gpt-6-astra` with `model_reasoning_effort="high"`, one run per prompt and variant. Both variants received the same task and were told to answer without tools or other writing skills. The baseline prompt additionally included the original 6,276-word `ste-writing` entrypoint; the port arm had no writing instructions beyond the task and evaluation framing.

The CLI used `--ephemeral`, `--ignore-user-config`, a read-only sandbox, disabled the `mays` plugin for these calls, and set `project_doc_max_bytes=0`. This is a prompt-level comparison, not a clean-room test of every host instruction or of automatic skill discovery. No tool calls or clarification questions occurred; all four calls exited successfully.

| Task | With original STE guidance | Without STE guidance | Assessment |
|---|---|---|---|
| Explain a duplicate-job race to a developer new to concurrency | 60 words; concrete example and atomic claim | 210 words; interleaving example, SQL claim, and crash/retry caveat | Both understandable; the longer answer supplies useful detail and a limit of the proposed solution |
| Report an implemented timeout fix, 12 passing tests, and expired deploy token | 31 words; three labeled lines | 29 words; two sentences | Both preserve all facts and invent no ETA; neither is flowery |

The status update without STE was:

> The timeout fix is implemented, and all 12 affected tests pass. Staging deployment is blocked by an expired deploy token; the owner must rotate it before deployment can proceed.

Leave STE excluded as requested. The samples show no need for its full rule set, but two prompts cannot establish that Astra never needs writing guidance. The longer explanation also shows that deactivation does not always shorten an answer. Add narrow preferences only for observed problems.

Raw prompts, outputs, JSON events, and partial timing metadata were saved outside the repo at `/private/tmp/codex-writing-eval-v45nf4gn`. These temporary artifacts are local to this validation session. Usage varies with host context and caching; no cost or latency improvement is claimed.

## Independent workflow tests

A separate agent executed the actual ported skills in disposable repositories:

- **Onboarding passed.** It preserved an existing user note, added guidance grounded in the Python project and Makefile, and ran the one-test suite. Only `AGENTS.md` changed, unstaged.
- **Conflict resolution passed.** It combined compatible changes from both branches, passed three tests and a combined-behavior assertion, cleared unmerged index entries, preserved an unrelated staged file byte-for-byte, and left the merge pending with unchanged HEAD as requested.

Neither workflow introduced an unexpected approval pause. The report and fixtures were saved at `/private/tmp/codex-skill-forward.MyBRrA`.

## Coverage limits

The remaining cases in [cases.json](cases.json) are a reusable evaluation backlog, not reported passes. Automatic routing, full frontend rendering and media generation, broad strict-review quality, rebase and binary conflicts, live AWS behavior, and the optimizer's full experiment loop were not exercised. No production resources or external image APIs were used.
