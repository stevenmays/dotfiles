# Word substitutions and the one-meaning glossary

How to use this file: when writing fresh text, skim "Bloat" and "Requirement words". When rewriting existing text, do a full pass — scan the original against every table here.

## Bloat → plain

| Avoid | Write |
|---|---|
| utilize, leverage, employ | use |
| in order to, for the purpose of | to |
| prior to | before |
| subsequent to, following | after |
| subsequently | then, later |
| previously | before, earlier |
| currently, at this time, at this point in time | now, or delete |
| going forward | from now on, or delete |
| commence, initiate | start |
| terminate | stop, end (keep it only when naming signal semantics, e.g. SIGTERM) |
| attempt, endeavor | try |
| facilitate | help, allow, or delete |
| accomplish | do, finish |
| demonstrate | show |
| indicate | show, mean |
| ensure | make sure |
| obtain, acquire | get |
| possess | have |
| retain | keep |
| necessitate | require |
| assist | help |
| comprise, constitute | include, contain, form |
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
| in the event that, in the case where | if |
| with regard to, regarding | about |
| due to the fact that, as a consequence of | because, because of |
| in conjunction with | with |
| as per | per, following |
| in a timely manner | on time, or within N minutes/days |
| it should be noted that | delete |
| please note that | delete, or "Note:" |
| please (in an instruction) | delete — a command is not impolite |
| functionality | feature, behavior — or say what it does |
| methodology | method |
| utilization | use |
| modification | change |
| has the capability to | can |

## Marketing words → the actual property

These words praise without informing. Replace each with the specific, checkable property it gestures at.

| Avoid | Write instead |
|---|---|
| robust | what it survives: "handles broker restarts without data loss" |
| seamless | what the user does not do: "no re-login needed" |
| performant | the number: "serves 2k req/s at p95 under 100 ms" |
| scalable | the tested limit: "tested to 10k concurrent connections" |
| streamline | simplify, shorten |
| holistic | complete |
| powerful, cutting-edge, state-of-the-art | delete, or state the capability |
| simply, just, easily | delete |
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

## Vague → specific

| Avoid | Write |
|---|---|
| several, some, a few, many | the number, or a bound: "at most 5" |
| recently | the date or the version |
| soon | the date — or "not yet scheduled" |
| often, sometimes, rarely | the rate: "about 1 in 200 requests" |
| large, small, fast, slow | the measurement, when it matters |
| significantly, dramatically | the delta |
| a long time | the duration |
| intermittently | the observed frequency and trigger, if known |
| may or may not | "might" — or state both branches |
| etc., and so on | finish the list, bound it ("and the other S3 events"), or open with "for example" |

## Requirement words

These words are contract language. Use each for exactly one thing.

- **must** — a requirement; violating it breaks something.
- **must not** — a prohibition.
- **should** — ambiguous; do not use. Choose "must" or "we recommend".
- **can** — ability or permission.
- **cannot** — impossibility. (Prohibition is "must not".)
- **might** — possibility.
- **may** — ambiguous between permission and possibility; prefer "can" or "might".
- **will** — a future fact, not a requirement.

## One meaning per document

Software reuses words. Within one document, each of these gets exactly one meaning — qualify on first use if the reader could pick the wrong one.

- **deprecated vs. removed** — deprecated still works but is discouraged; removed is gone. Never use "deprecated" for gone.
- **update vs. upgrade** — pick a split and hold it, e.g. update changes data, upgrade changes the version.
- **parameter vs. argument** — parameter in the definition, argument at the call site.
- **error / exception / failure** — pick one word for each distinct thing; don't rotate them for variety.
- **server** — the process or the machine? Say "the API server process" or "the host" once, then keep the term.
- **build** — the job or the artifact? Disambiguate with a noun: "the build job failed", "the build artifact is 400 MB".
- **release** — the tag, the deploy, or the announcement? Define once.
- **sync** — one-way copy or two-way merge? Say which, and which direction.
- **migrate** — name the object: the schema, the data, or the platform.
- **instance** — a VM, a container, or an object in memory? Qualify on first use.
- **client** — the person or the calling software? Qualify.
- **authentication vs. authorization** — never shorten both to "auth" in a document where the difference matters.
- **latest** — a moving tag or "most recent at time of writing"? Give the version number instead.
- **legacy** — name the actual system once ("the legacy biller, `invoicer-v1`"), then use the name.
- **job / task / worker** — pick which word means the unit of work and which means the process that runs it; never swap.

## Verb / noun spelling pairs

Two words as a verb, one word as a noun or adjective.

| Verb (two words) | Noun / adjective (one word) |
|---|---|
| log in | login |
| set up | setup |
| back up | backup |
| roll back | rollback |
| shut down | shutdown |
| start up | startup |
| sign up | signup |
| fall back | fallback |
| hand off | handoff |
| lock out | lockout |
| time out | timeout |
| clean up | cleanup |
| work around | workaround |
