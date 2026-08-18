# Mechanics: punctuation, numbers, dates, and formatting

How to use this file: read it when writing documentation, a README, a runbook, or anything document-length. For short artifacts (Slack, review comments, commits), the Mechanics section of SKILL.md is enough.

Source: the Google developer documentation style guide, trimmed to what applies to engineering prose.

## Punctuation

- Serial comma always: "the scheduler, the worker, and the queue".
- Comma after an introductory phrase: "After the deploy, check the dashboard."
- Two independent clauses joined by and/but/or/so get a comma before the conjunction — unless both are very short ("Type your ID and click OK").
- Conjunctive adverbs (otherwise, however, therefore) take a semicolon or period before and a comma after: "The variable must have a value; otherwise, the server returns an error."
- Em dash (—) with no spaces marks a break: "Enter a name — for example, `my-instance-99`." Never use an en dash; use a hyphen or the word "to".
- Term-definition pairs use a colon, never a dash: "`--dry-run`: prints the plan without applying it."
- The text before a colon that introduces a list is a complete sentence: "The command takes the following flags:", not "The flags are:".
- Lowercase after a colon mid-sentence, unless what follows is a proper noun, a heading, or a quotation.
- Semicolons: avoid, except to join two closely related independent clauses or to separate list items that contain commas.
- Parentheses: avoid for anything load-bearing — readers skip them. Prefer commas, a dash, or a second sentence. A full sentence inside parentheses keeps its period inside; a fragment's period goes outside.
- Straight quotes and apostrophes only, never curly.
- Periods and commas go inside quotation marks — except for literal strings and keywords, where punctuation goes outside (or better, use code font and skip the quotes).
- No slash alternatives: not "view and/or edit", not "the request/response". Write "view and edit", "view or edit", or "A, B, or both". Slashes stay in paths, URLs, and code.
- No exclamation points in technical text. A completed step ends with a period: "The VM is created."
- Ellipses: don't use them in your own prose. In quoted output, `...` alone on a line marks omitted lines.
- Avoid footnotes; use a note or a parenthetical instead.

## Hyphens

- Hyphenate compound modifiers before a noun: "a well-designed app", "a 64-bit system", "a five-minute wait".
- Don't hyphenate the same compound after the verb: "the app is well designed", "runs in real time".
- Never hyphenate after an -ly adverb: "publicly available API".
- Don't hyphenate abbreviated units as modifiers: "a 200 GB disk".
- Compound modifiers longer than two words: rewrite instead — "test cases specific to the 2023 edition", not "edition-2023-specific test cases".
- Prefixes close up (preprocessing, metadata, subcommand) except before a capital or a number (non-Google, post-2000), with self-/cross- (self-hosted, cross-region), or to prevent misreading (re-sign vs. resign).
- Suspended hyphens share a base: "one- or two-hour intervals".
- Always-hyphenated regardless of position: on-premises, add-on, user-facing, customer-facing.

## Numbers

- Spell out zero through nine; numerals for 10 and up.
- Exceptions — always numerals: versions ("version 3"), numbers with units or technical quantities ("6 queries per second", "8 CPUs"), step/page numbers, prices, and any number sitting next to a ≥10 number in the same context ("15 workers but 6 of them").
- Never start a sentence with a numeral — spell it out or rewrite.
- Spell out ordinals: "first", "21st" never appears as "1st".
- "10 times faster", never "10x faster".
- Percentages: numeral plus %, no space: "40%". Spelled out only at a sentence start: "Forty percent…".
- Decimals under one lead with a zero: "0.3 s", never ".3 s".
- Four or more digits get comma separators: "1,532,784 bytes".
- Ranges use a hyphen with no spaces ("8-20 files") or, when a hyphen could read as minus or subtraction, "from 8 to 20". With units, repeat the unit and use "to": "-40 °C to 85 °C".
- Nonbreaking space between number and unit: "64 GB", "50 Mbps". No space for %, °, and currency.
- Dimensions use a lowercase x with no spaces: "192x192".
- kB/MB/GB are powers of 1000; KiB/MiB/GiB are powers of 1024. Write the one the system actually uses.
- "55k requests per day" — lowercase k, no space, and always name what is counted.
- Prefer "per" over a slash: "requests per day" (established abbreviations like Mbps are fine).
- Approximate quantities use words honestly — "thousands of rows" — never fake precision.

## Dates and times

- Numeric dates are ISO 8601: `2026-08-17`. In examples, pick a day above 12 so month and day can't be confused.
- Prose dates spell out the month: "August 17, 2026"; month and year alone take no comma: "January 2017". A full date mid-sentence gets a comma after the year.
- Never use seasons ("in the fall") — hemispheres disagree. Name the month or quarter.
- 12-hour clock with capitalized AM/PM: "3:45 PM", "3 PM".
- Time zones: name plus UTC offset — "Pacific Standard Time (UTC-8)". Never a bare abbreviation like PST.
- Time ranges: "5-10 minutes".

## Capitalization

- Sentence case everywhere: headings, table headers, list items, captions, labels.
- Never rely on capitalization to distinguish meaning ("Pod" vs. "pod").
- No all-caps or camelCase except literal code and official names.
- A spelled-out acronym is lowercase unless it's a proper noun: "data manipulation language (DML)".
- Don't name casing styles in prose; show the format: "no spaces, first letter of each word capitalized — for example, `AssertionAccount`".

## Abbreviations

- First use: spelled-out form, then the abbreviation in parentheses — "time to first byte (TTFB)". Skip the expansion for API, CPU, URL, HTML, REST, RAM, and similar universals.
- If the term appears only once, use the spelled-out form alone.
- In a heading, use the abbreviation; define it in the first paragraph after.
- Never use an abbreviation as a verb: "connect over SSH", not "ssh into".
- Pluralize without an apostrophe: "APIs", "IDEs", "OSes".
- Choose a/an by the spoken sound: "an SLA", "a URL", "a SQL query".
- No "i.e." or "e.g." — write "that is" and "for example". No "etc." — finish the list, bound it, or open with "for example". No internet slang (tl;dr, IMO) in docs.

## Headings

- Task headings are bare imperatives: "Create an instance". Concept headings are noun phrases: "Migration to Google Cloud". Never open a heading with an -ing word.
- No trailing period. No links inside headings. No bare code as a heading — add a noun: "The `retry` block".
- Don't skip levels (no h4 under an h2); no heading with nothing under it.
- Prefix optional sections with "Optional:".
- When renaming a heading that has an anchor, keep the old anchor ID so inbound links survive.

## Lists

- Introduce every list with a complete sentence ending in a colon (or a period if text intervenes).
- Numbered list = order matters. Bulleted list = it doesn't. Term + description list for pairs.
- One idea per item; parallel grammar across items.
- Items that are sentences get periods; single words or fragments get nothing. Don't mix — if one item needs a period, give them all one.
- No single-item lists. A single step is a sentence or a bullet, not "1.".
- Make explicit whether the list is exhaustive ("the following flags") or examples ("flags such as the following").

## Links and cross-references

- Link text is the target's title or a short description with the important words first: "see [Configuring retries]", never "click here", "this doc", or a bare URL.
- The standing pattern: "For more information about X, see Y." Use "about", not "on"; use "see", not "check out" or "refer to".
- Include the abbreviation inside the link text: "[Service Level Objective (SLO) monitoring]".
- Say when a link does something unexpected: downloads a file (name the format), opens email, or jumps within the same page.
- Punctuation goes outside the link text.
- Don't re-document what a linked standard or vendor doc already covers — link it.
- Prefer text on the page over a link when a term needs only a sentence of definition.
- No positional references: "the following table", "the preceding command" — never "the table above" or "below". Layout reflows; "above" doesn't survive it. Refer to figures and tables by number.

## Code in prose

- Code font (backticks): commands, flags, filenames and paths, class/method/function names, env vars, keywords, literal values, ports, IPs, HTTP status codes, query parameters, error strings, anything the reader types or the system prints.
- Not code font: product names, org names, domain names in prose, URLs meant for the browser.
- Never inflect a code item as English: "send a `POST` request", not "`POST` the data"; "`Intent` objects", not "`Intent`s"; "after `close` returns", not "after `close`ing".
- HTTP status codes read as "the `400 Bad Request` status code"; ranges as `2xx`.
- File types by formal name, not extension: "a YAML file", not "a `.yaml` file". Don't verb them: "extract the zip file", not "unzip".
- Method names drop the class prefix unless ambiguous: "call `get`", not "call `Animal.get`".
- Possessives never attach to code font: "the `wordCount` method's return value" or rewrite — never "`wordCount`'s".
- Introduce every code block with a sentence: colon if the block follows immediately, period if text intervenes.
- Mark omitted code with a comment in the sample's language, not "…".
- Command output: show it only when the reader verifies against it or copies from it; introduce with "The output is similar to the following:".
- Multi-line commands wrap before 80 characters with `\` continuations and 4-space indents.

## Placeholders and example data

- Placeholders are descriptive `UPPER_SNAKE_CASE`: `PROJECT_ID`, `REGION`. Never `foo`, `bar`, `xx`, `myValue`, or possessives like `MY_PROJECT`.
- One placeholder: "Replace `PROJECT_ID` with the project's ID." Several: after the command, write "Replace the following:" and one bullet per placeholder, in the order they appear.
- A copy-paste command must run unedited — no `[optional]`, `{a|b}`, or `...` syntax inside a copyable block. Show variants as separate blocks.
- Example domains: `example.com`, `example.org`, `example.net`. Example IPv4: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`. IPv6: `2001:db8::/32`. US phone numbers: `800-555-0100` through `800-555-0199`.
- Never real people, real emails, real IPs, or real credentials — even expired ones.
- Example resource names describe the reader's world: `prod-orders-queue`, not `test1` or `mydb`.

## UI instructions

For the rare runbook step that drives a UI:

- Name the control by its visible label, bold: "Click **Save**" — never "click the disk icon" or "the button on the left".
- Menu paths chain with >: "Click **View > Tools > Developer Tools**."
- Checkboxes are selected and cleared, never checked/unchecked. "Click" is for a mouse, "tap" for touch, "press" for keys ("press Control+S", modifiers spelled out).
- State the location, then the action: "In the **Alerts** pane, click **Create policy**."
- Prefer the task over the click when either works: "Refresh the page", not "Click the refresh button".

## Unix signal verbs

One verb per signal, never a synonym: `SIGKILL` kills, `SIGTERM` terminates, `SIGQUIT` quits, `SIGINT` interrupts, `SIGSTOP` stops. Don't write "kill the process with `SIGTERM`".
