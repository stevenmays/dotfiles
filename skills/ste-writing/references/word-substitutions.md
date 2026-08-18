# Word substitutions and the one-meaning glossary

How to use this file: when writing fresh text, skim "Bloat" and "Requirement words". When rewriting existing text, do a full pass — scan the original against every table here.

Sources: the Google developer documentation style guide word list, plus software-specific entries this skill adds.

## Bloat → plain

| Avoid | Write |
|---|---|
| utilize, leverage, employ | use |
| allows you to | lets you |
| in order to, for the purpose of | to |
| prior to | before |
| subsequent to, following | after |
| subsequently | then, later |
| previously | before, earlier |
| currently, at this time, at this point in time | now, or delete (see Time-anchored words) |
| going forward | from now on, or delete |
| commence, initiate | start |
| terminate | stop, end (keep it only for signal semantics: `SIGTERM` terminates) |
| attempt, endeavor | try |
| facilitate | help, allow, or delete |
| accomplish | do, finish |
| demonstrate | show |
| indicate | show, mean |
| ensure (in an instruction) | make sure (as a claim, see Marketing words) |
| obtain, acquire | get |
| possess | have |
| retain | keep |
| necessitate | require |
| assist | help |
| comprise, constitute | consist of, include, contain |
| desire, desired | want, need |
| approximately | about |
| additional | more, another |
| numerous, multiple | many — or the number |
| sufficient / insufficient | enough / not enough |
| erroneous | wrong, incorrect |
| optimal | best |
| appropriate | correct, right — or name the specific thing |
| aforementioned | this, that — or repeat the name |
| respectively | rewrite so each value sits next to its name |
| the former / the latter | repeat the names |
| upon | on, when |
| whilst, amongst | while, among |
| towards | toward |
| in the event that, in the case where | if |
| with regard to, regarding | about |
| due to the fact that, as a consequence of | because, because of |
| in conjunction with | with |
| as per | per, following |
| as (meaning because) | because — "as" also means "while" |
| once (meaning after) | after — "once" also means "one time" |
| in a timely manner | on time, or within N minutes/days |
| it should be noted that, please note that | delete, or "Note:" |
| please (in an instruction) | delete — a command is not impolite |
| let's | delete — name the actor or use the imperative |
| i.e. | that is |
| e.g. | for example |
| etc., and so on | finish the list, bound it, or open with "for example" |
| aka | also known as |
| via | through, by, or the specific mechanism |
| functionality | feature, behavior, capability — or say what it does |
| methodology | method |
| utilization | use |
| modification | change |
| has the capability to | can |
| execute (a command) | run |
| in some cases | sometimes — or the actual condition |

## Marketing words → the actual property

These words praise without informing. Replace each with the specific, checkable property it gestures at. Superlatives and guarantees ("best", "fastest", "always", "never", "guarantees", "prevents", "ensures that no…") are claims — make one only when it is literally, durably true, and cite the source of any number. "Helps prevent X" survives an incident; "prevents X" does not.

| Avoid | Write instead |
|---|---|
| robust | what it survives: "handles broker restarts without data loss" |
| seamless | what the user does not do: "no re-login needed" |
| performant | the number: "serves 2k req/s at p95 under 100 ms" |
| scalable | the tested limit: "tested to 10k concurrent connections" |
| streamline | simplify, shorten |
| holistic | complete |
| powerful, cutting-edge, state-of-the-art | delete, or state the capability |
| best-in-class, world-class | delete |
| -agnostic | -independent: "platform-independent" |
| actionable | what to do with it: "a list you can act on" |
| simply, just, easily, quickly | delete |
| basically, essentially, actually | delete |
| very, really, quite, extremely | delete, or quantify |

## Smothered verbs

A verb buried inside "perform/make/conduct + noun" is weaker and longer than the verb alone.

| Avoid | Write |
|---|---|
| perform validation of | validate |
| perform an analysis of | analyze |
| conduct an investigation | investigate |
| make a decision | decide |
| make a modification to | change |
| provide a description of | describe |
| take into consideration | consider |
| carry out testing of | test |
| perform a comparison | compare |
| issue a notification | notify |
| perform a migration of | migrate |
| make an assumption | assume |
| reach a conclusion | conclude |
| provide support for | support |
| have a dependency on | depend on |
| make use of | use |

## Vague → specific

| Avoid | Write |
|---|---|
| several, some, a few, many | the number, or a bound: "at most 5" |
| recently | the date or the version |
| soon | the date — or "not yet scheduled" |
| often, sometimes, rarely | the rate: "about 1 in 200 requests" |
| large, small, fast, slow | the measurement, when it matters |
| significantly, dramatically | the delta |
| 10x, 3x | 10 times, 3 times |
| a long time | the duration |
| intermittently | the observed frequency and trigger, if known |
| may or may not | "might" — or state both branches |
| key (adjective), crucial | why it matters, in a clause |

## Time-anchored words

These date the document the day it ships. In docs, READMEs, and runbooks, replace each with the version or date, or delete. They are fine in inherently time-bound artifacts: release notes, incident updates, status reports, Slack.

| Avoid in docs | Write |
|---|---|
| currently, now, at present, as of this writing | delete, or state the version: "in v3.2" |
| new, newer | delete — everything was new once |
| old, older (version) | earlier |
| higher / lower (version) | later / earlier |
| latest | the version number |
| soon, eventually, in the future | the date, or delete |
| does not yet | does not |
| will (for current behavior) | present tense |

## Requirement words

Contract language. Use each word for exactly one thing.

- **must** — a requirement; violating it breaks something. ("You need to" is an acceptable softer form.)
- **must not** — a prohibition.
- **should** — ambiguous; do not use. Choose "must" or "we recommend".
- **can** — ability or permission.
- **cannot** — impossibility. (Prohibition is "must not".)
- **might** — possibility.
- **may** — formal permission in policy or legal text only; elsewhere use "can" or "might".
- **will** — a real future event, not a requirement and not current behavior.
- **shall** — never.
- **would** — never for hypothetical behavior ("the server would then…"); describe what the software does.
- "The value should be true" hides an actor. Write "Set the value to `true`", "The server sets the value to `true`", or "If the value is `false`, …".

## Inclusive replacements

Use the plain replacement everywhere new. When the old term is entrenched, name the new term first and gloss the old one once: "the allowlist (sometimes called a whitelist)". When the old term is a literal identifier, keep it in code font and out of prose: "the primary branch (named `master` in this repo)".

| Avoid | Write |
|---|---|
| whitelist / blacklist | allowlist / denylist (or blocklist) |
| master / slave | primary / replica; main; controller / worker |
| sanity check | final check, confidence check, smoke test |
| grandfathered | exempt, legacy |
| man-hours, manpower | person-hours, staff |
| man-in-the-middle | on-path attacker |
| first-class citizen | fully supported, built-in |
| native (feature) | built-in |
| hang, hung | stop responding, not responding |
| crazy, insane (results) | baffling, unexpected |
| cripples | slows, degrades |
| kill, nuke, abort | stop, end, cancel (except signal semantics: `SIGKILL` kills) |
| grayed out, disabled (UI) | unavailable |
| hit (a key, an endpoint) | press, call |
| dummy value | placeholder |
| he, she, he/she | they — or repeat the role: "the on-call engineer" |
| guys | everyone, folks |
| blackhat / whitehat | name the act: "attackers", "security researchers" |

## Jargon ladder

For a term of art the reader may not share ("blast radius", "shift left", "back-of-the-envelope"), take the first rung that works:

1. Write around it in plain language.
2. Swap in a specific plain term ("affected services" for "blast radius").
3. Used once? Gloss it in parentheses or link a definition.
4. Used throughout? Define it at first use, then use it consistently.
5. It's a literal code token? Code font, tied to the command it appears in.

Keep jargon the audience genuinely searches for (an SRE doc can say "error budget").

## One meaning per document

Software reuses words. Within one document, each of these gets exactly one meaning — qualify on first use if the reader could pick the wrong one.

- **deprecated vs. removed** — deprecated still works but is discouraged; removed is gone. Never use "deprecated" for gone.
- **update vs. upgrade** — pick a split and hold it, e.g. update changes data, upgrade changes the version.
- **parameter vs. argument** — parameter in the definition, argument at the call site.
- **error / exception / failure** — pick one word for each distinct thing; don't rotate them for variety.
- **flag vs. argument** — the named option vs. the value passed to it.
- **server** — the process or the machine? Say "the API server process" or "the host" once, then keep the term.
- **build** — the job or the artifact? Disambiguate with a noun: "the build job failed", "the build artifact is 400 MB".
- **release** — the tag, the deploy, or the announcement? Define once.
- **sync** — one-way copy or two-way merge? Say which, and which direction.
- **migrate** — name the object: the schema, the data, or the platform.
- **instance** — a VM, a container, or an object in memory? Qualify on first use.
- **client** — the person or the calling software? Qualify.
- **authentication vs. authorization** — a user is authenticated; a request is authorized. Never shorten both to "auth" where the difference matters; never "authN/authZ".
- **latest** — a moving tag or "most recent at time of writing"? Give the version number instead.
- **legacy** — name the actual system once ("the legacy biller, `invoicer-v1`"), then use the name.
- **job / task / worker** — pick which word means the unit of work and which means the process that runs it; never swap.
- **data** — singular mass noun: "the data is", "less data".
- **impact** — noun only; the verb is "affect".
- **whether vs. if** — "whether" introduces alternatives; "if" introduces a condition.
- **page / dialog / pane** — pick per UI element and hold it; a "dialog" is not a "popup".
- **exploit** — security contexts only; the neutral verb is "use".
- **secret** — in auth contexts, a credential; don't also use it loosely.

## Spelling: one word, two words, or hyphen

Closed (one word): backend, frontend, codebase, filename, hostname, username, namespace, runtime, lifecycle, standalone, workflow, workaround, webhook, website, webpage, datastore, dataset, subcommand, subdomain, subnet, superuser, microservices, hardcoded, email, checkbox, plaintext (crypto only — otherwise "plain text").

Open (two words): data center, data type, file system, source code, name server, time zone, plain text, third party (noun).

Hyphenated: third-party (modifier), real-time (modifier), high-availability (modifier), key-value pair, on-premises (always; never "on-prem" in docs), right-click, double-click, pre-shared key, self-service, blue-green.

## Verb / noun spelling pairs

Two words as a verb, one word as a noun or adjective. Prefer "sign in" over "log in" as the verb unless the product's own UI says otherwise.

| Verb (two words) | Noun / adjective (one word) |
|---|---|
| sign in / sign out | sign-in / sign-out |
| log in | login |
| set up | setup |
| back up | backup |
| roll back | rollback |
| roll out | rollout |
| shut down | shutdown |
| start up | startup |
| sign up | signup |
| fall back | fallback |
| hand off | handoff |
| lock out | lockout |
| time out | timeout |
| clean up | cleanup |
| check out | checkout |
| opt in | opt-in |
| plug in | plugin |
| work around | workaround |
