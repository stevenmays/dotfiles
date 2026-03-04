# Deep Memory: qmd + Claude Code

Persistent, searchable memory across Claude Code sessions and repos.

## The Problem

Claude Code sessions are ephemeral. You discover a gnarly gotcha, debug for 30 minutes, land on the fix — and next session, that knowledge is gone. Auto-memory helps but it's shallow and automatic. You can't search it, structure it, or share it across repos.

## How It Works

```
You say /remember or /take-notes
  → Claude writes to .claude/notes/ (gitignored, local)
  → Claude runs qmd update (indexes for BM25 keyword search)
  → qmd MCP server makes notes searchable from any Claude session
  → qmd embed (run manually) adds vector search for semantic recall
```

Two search modes:
- **BM25 keyword search** — fast, always up to date after `qmd update`, good for exact terms
- **Vector similarity search** — needs `qmd embed` to refresh, good for "find things related to X"

## Daily Workflow

### Starting a new repo

```
/repo-init
```

Creates `.claude/notes/`, adds gitignore entries, registers qmd collections, and indexes any existing `agent_docs/`.

### Quick capture during work

When you hit a gotcha, make a decision, or discover something non-obvious:

```
/remember
```

Tell Claude what to remember. It appends a timestamped entry to `.claude/notes/remember.md`. Examples:

- "The Astro build breaks if you import .tsx files from content collections"
- "We decided to use server-side redirects instead of client-side for SEO"
- "TimescaleDB continuous aggregates can't use DISTINCT in the view definition"

### Deep documentation

After a significant investigation or discovery:

```
/take-notes
```

Claude writes a structured markdown file to `.claude/notes/{feature}.md` with context, findings, gotchas, and code examples.

### Searching your notes

Claude automatically has access to qmd search via MCP. Just ask naturally:

- "What do my notes say about Astro build issues?"
- "Have I documented anything about TimescaleDB gotchas?"
- "Search my notes for authentication decisions"

You can also search from the terminal:

```bash
qmd search "astro build"          # BM25 keyword search
qmd query "things that break builds"  # vector similarity (needs qmd embed)
```

### Keeping search fresh

BM25 index updates happen automatically via `/remember` and `/take-notes` (they run `qmd update`).

Vector embeddings need a manual refresh:

```bash
qmd embed    # run periodically, or after a batch of new notes
```

### Session continuity (unchanged)

```
/scratchpad
```

Still works the same — ephemeral session state, NOT indexed by qmd. Use this for tracking in-progress work within a session, not for persistent memory.

## What Lives Where

| Location | Purpose | Indexed? | Committed? |
|----------|---------|----------|------------|
| `.claude/notes/remember.md` | Quick captures | Yes (qmd) | No |
| `.claude/notes/{feature}.md` | Deep investigations | Yes (qmd) | No |
| `.claude/scratchpad.md` | Session state | No | No |
| `.claude/agent_docs/` | Repo coding standards | Yes (qmd) | Yes |
| `~/.claude/projects/.../memory/` | Auto-memory | No (Claude internal) | No |

## Managing Collections

```bash
qmd collection list              # see all indexed collections
qmd collection remove mays.co-notes  # remove a collection
qmd context list                 # see context descriptions
qmd status                       # overall index health
```

## Setup for a New Machine

```bash
# 1. Clone dotfiles, run sync
cd ~/Git/dotfiles && bash ai/claude/sync.sh

# 2. In each repo you want memory for:
cd ~/Git/my-repo
# Then in Claude: /repo-init

# 3. Build vectors (optional, for semantic search)
qmd embed
```

## Architecture

```
Per-repo:                          Global:
.claude/notes/                     ~/.cache/qmd/index.sqlite
  remember.md      ──index──>       collection: {repo}-notes
  {feature}.md     ──index──>       collection: {repo}-docs
.claude/agent_docs/──index──>
                                   qmd MCP server (stdio)
                                     └─> Claude searches all repos
```

The qmd MCP server runs as a stdio process managed by Claude Code. It's configured in `~/.claude/settings.json` and starts automatically. No daemon, no ports, no background process.
