#!/usr/bin/env bash
# Run a task on a non-Claude model — GPT through the Codex CLI, or Grok through the
# Cursor CLI — so it cannot hang the calling session.
#
# Neither `codex exec` nor `cursor-agent -p` has a timeout of its own. A run that reaches
# for web search, a browser tool, or an MCP server can block forever with no output. This
# wrapper streams JSONL events, kills the run when it stops producing them, and salvages
# whatever arrived before the stall.
#
# Usage:
#   external-run.sh --prompt <file> --out <file> [--engine auto|codex|cursor]
#                   [--idle 300] [--hard 1800] [--cd DIR] [--model SLUG]
#                   [--effort low|medium|high|xhigh|max]
#                   [--sandbox read-only|workspace-write] [--label run]
#
# --engine defaults to $EXTERNAL_SUBAGENT_ENGINE, else auto: codex, else cursor-agent. Each
# engine runs the first binary on PATH whose `--version` exits 0 within 10s, so a shim that
# cannot run is skipped for the next match.
#
# The model is always pinned. An unpinned codex run inherits ~/.codex/config.toml, which
# follows whatever model the user last picked in the TUI.
#   codex:  --model, else $CODEX_SUBAGENT_MODEL, else gpt-6-astra.
#           --effort, else $CODEX_SUBAGENT_EFFORT, else high.
#   cursor: --model, else $CURSOR_SUBAGENT_MODEL, else the highest Grok version that
#           `cursor-agent models` lists, at --effort (default high). A pinned slug already
#           carries its effort, so --effort applies only to the resolved one.
#
# --sandbox defaults to read-only, which is what a plan or review wants. workspace-write lets
# the run edit the repo. Both engines run non-interactively, so nothing blocks on a prompt.
# Point a workspace-write run at a feature branch only: this wrapper never stages, commits,
# or reverts anything.
#
# Exit codes:
#   0    completed normally
#   124  hard timeout   — total budget exceeded
#   125  idle stall     — no output for --idle seconds
#   126  engine failed  — nonzero exit, or a cursor result event with is_error
#   2    bad usage, no runnable external engine, or no usable Grok model on cursor
#
# --out always exists on return. A partial result is marked in its header. After a
# workspace-write run the real artifact is the working tree — read `git diff`, and
# treat --out as the run's own account of what it did.

set -uo pipefail

IDLE=300
HARD=1800
# 1s: a finished run returns within a second instead of waiting out a longer poll.
POLL=1
WORKDIR="$PWD"
PROMPT=""
OUT=""
ENGINE="${EXTERNAL_SUBAGENT_ENGINE:-auto}"
MODEL=""
EFFORT=""
SANDBOX="read-only"
LABEL="run"

while [ $# -gt 0 ]; do
  case "$1" in
    --prompt|--out|--engine|--idle|--hard|--cd|--model|--effort|--sandbox|--label)
      # Guard before expanding $2: under `set -u` a trailing flag aborts with a raw
      # bash error and exit 1, not the exit 2 this script documents.
      [ $# -ge 2 ] || { echo "external-run: $1 requires a value" >&2; exit 2; }
      case "$1" in
        --prompt)  PROMPT="$2" ;;
        --out)     OUT="$2" ;;
        --engine)  ENGINE="$2" ;;
        --idle)    IDLE="$2" ;;
        --hard)    HARD="$2" ;;
        --cd)      WORKDIR="$2" ;;
        --model)   MODEL="$2" ;;
        --effort)  EFFORT="$2" ;;
        --sandbox) SANDBOX="$2" ;;
        --label)   LABEL="$2" ;;
      esac
      shift 2 ;;
    *) echo "external-run: unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$PROMPT" ] && [ -n "$OUT" ] || { echo "usage: external-run.sh --prompt <file> --out <file> [--engine auto|codex|cursor] [--idle N] [--hard N] [--cd DIR] [--model SLUG] [--effort LEVEL] [--sandbox MODE] [--label NAME]" >&2; exit 2; }
case "$SANDBOX" in
  read-only|workspace-write) ;;
  *) echo "external-run: --sandbox must be read-only or workspace-write, got: $SANDBOX" >&2; exit 2 ;;
esac
[ -r "$PROMPT" ] || { echo "external-run: prompt file not readable: $PROMPT" >&2; exit 2; }

# Runs a command in its own process group with output to a file, and kills the group after
# a bound. Sets BOUNDED_RC, 124 on a kill. Never call it inside $(...): job control there is unreliable.
run_bounded() {
  local secs="$1" out="$2" pid ticks=0
  shift 2
  set -m
  "$@" < /dev/null > "$out" 2>&1 &
  pid=$!
  set +m
  while kill -0 "$pid" 2>/dev/null && [ "$ticks" -lt $((secs * 10)) ]; do sleep 0.1; ticks=$((ticks + 1)); done
  if kill -0 "$pid" 2>/dev/null; then
    exec 3>&2 2>/dev/null   # hide bash's async "Killed" job notice
    kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
    wait "$pid"; exec 2>&3 3>&-; BOUNDED_RC=124
  else
    wait "$pid"; BOUNDED_RC=$?
  fi
}

# Sets BIN to the first $1 on PATH whose `--version` exits 0. `command -v` alone would pick
# a shim that cannot run, such as a cmux shim ahead of the real binary.
find_runnable() {
  local candidate
  BIN=""
  while IFS= read -r candidate; do
    [ -n "$candidate" ] || continue
    run_bounded 10 /dev/null "$candidate" --version
    if [ "$BOUNDED_RC" -eq 0 ]; then BIN="$candidate"; return 0; fi
    echo "external-run: skipping $candidate: --version exited $BOUNDED_RC" >&2
  done <<< "$(type -aP "$1")"
  return 1
}

case "$ENGINE" in
  auto)
    if find_runnable codex; then ENGINE=codex
    elif find_runnable cursor-agent; then ENGINE=cursor
    else echo "external-run: no external engine: no codex or cursor-agent on PATH passes \`--version\`. Install one, or fix a path skipped above." >&2; exit 2
    fi ;;
  codex)  find_runnable codex || { echo "external-run: no runnable codex: none on PATH passes \`--version\`" >&2; exit 2; } ;;
  cursor) find_runnable cursor-agent || { echo "external-run: no runnable cursor-agent: none on PATH passes \`--version\`" >&2; exit 2; } ;;
  *) echo "external-run: --engine must be auto, codex, or cursor, got: $ENGINE" >&2; exit 2 ;;
esac

JSONL="${OUT%.md}.jsonl"
ERRLOG="${OUT%.md}.stderr"

if [ "$ENGINE" = codex ]; then
  ENGINE_NAME="Codex"
  MODEL="${MODEL:-${CODEX_SUBAGENT_MODEL:-gpt-6-astra}}"
  EFFORT="${EFFORT:-${CODEX_SUBAGENT_EFFORT:-high}}"
else
  ENGINE_NAME="Cursor"
  MODEL="${MODEL:-${CURSOR_SUBAGENT_MODEL:-}}"
  if [ -n "$MODEL" ]; then
    EFFORT="n/a"
  else
    EFFORT="${EFFORT:-high}"
    MODELS="${OUT%.md}.models"
    # `cursor-agent models` reaches the network, so it gets a 30s bound like every other call.
    run_bounded 30 "$MODELS" "$BIN" models
    MODELS_RC=$BOUNDED_RC
    # Parse whole tokens, not columns: the listing format is not documented. The full match
    # drops -fast (the same model on a faster tier at double the price), -mini, and
    # unnumbered slugs such as grok-code-fast-1. At the highest version a grok- slug beats
    # cursor-grok-; the effort falls back to the base slug, then to -high.
    if [ "$MODELS_RC" -eq 0 ]; then
      CANDIDATES=$(grep -oE '[A-Za-z0-9._-]+' "$MODELS" | sed 's/[.-]*$//' \
        | grep -xE '(cursor-)?grok-[0-9]+(\.[0-9]+)*(-(low|medium|high|xhigh))?' | sort -u)
      TOP=$(sed -E 's/^(cursor-)?grok-([0-9.]+).*/\2/' <<< "$CANDIDATES" | sort -V | tail -1)
      PREFIX="cursor-grok-"
      for SLUG in $CANDIDATES; do
        case "$SLUG" in "grok-$TOP"|"grok-$TOP"-*) PREFIX="grok-" ;; esac
      done
      for PICK in "$EFFORT" "" high; do
        SLUG="$PREFIX$TOP${PICK:+-$PICK}"
        if [ -n "$TOP" ] && grep -qxF "$SLUG" <<< "$CANDIDATES"; then MODEL="$SLUG"; EFFORT="${PICK:-model default}"; break; fi
      done
    fi
    [ -n "$MODEL" ] || { echo "external-run: no usable Grok model from \`cursor-agent models\` (exit ${MODELS_RC}; output in $MODELS). Run \`cursor-agent login\`, or set CURSOR_SUBAGENT_MODEL to a Grok slug." >&2; exit 2; }
  fi
  # Cursor also serves Claude and `auto`, and either would make the second opinion same-family.
  case "$MODEL" in
    *[Gg][Rr][Oo][Kk]*) ;;
    *) echo "external-run: the cursor engine runs Grok models only, got: $MODEL" >&2; exit 2 ;;
  esac
fi

: > "$JSONL"; : > "$ERRLOG"

mtime() { stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null || echo 0; }

# Runs touch the repository and nothing else. Every network-reaching tool the engine lets us
# switch off is off: those are the calls that hang, and neither a review nor an edit needs one.
set -m
if [ "$ENGINE" = codex ]; then
  # No --approve-for-me here: it is mutually exclusive with -s, and `codex exec` already
  # auto-approves anything the sandbox permits, so workspace-write alone is enough.
  "$BIN" exec \
    --json \
    -s "$SANDBOX" \
    -C "$WORKDIR" \
    -m "$MODEL" \
    -c "model_reasoning_effort=\"$EFFORT\"" \
    -c 'tools.web_search=false' \
    -c 'mcp_servers={}' \
    --disable browser_use \
    --disable browser_use_external \
    --disable computer_use \
    - < "$PROMPT" > "$JSONL" 2> "$ERRLOG" &
else
  # Without --force, cursor-agent proposes edits and applies none. Never pass --approve-mcps
  # or --browser: those tools are the ones that hang. Web search has no per-run switch.
  # The prompt goes on stdin, because argv caps its size at the OS argument limit. A regular
  # file is not a terminal, so the background process group never stops on a terminal read.
  # A new workspace otherwise stops a headless run at a trust prompt; --force already implies trust.
  if [ "$SANDBOX" = read-only ]; then MODE_ARGS=(--mode ask --trust); else MODE_ARGS=(--force); fi
  "$BIN" -p \
    --output-format stream-json \
    --model "$MODEL" \
    --workspace "$WORKDIR" \
    --sandbox enabled \
    "${MODE_ARGS[@]}" < "$PROMPT" > "$JSONL" 2> "$ERRLOG" &
fi
PID=$!
set +m

START=$(date +%s)
REASON="done"
while kill -0 "$PID" 2>/dev/null; do
  sleep "$POLL"
  NOW=$(date +%s)
  if [ $((NOW - $(mtime "$JSONL"))) -ge "$IDLE" ]; then REASON="idle"; break; fi
  if [ $((NOW - START)) -ge "$HARD" ]; then REASON="hard"; break; fi
done

if [ "$REASON" = "done" ]; then
  wait "$PID"; RUN_RC=$?
else
  exec 3>&2 2>/dev/null   # hide bash's async "Terminated" job notice
  kill -TERM -"$PID" 2>/dev/null || kill -TERM "$PID" 2>/dev/null
  for _ in 1 2 3; do kill -0 "$PID" 2>/dev/null || break; sleep 1; done
  kill -KILL -"$PID" 2>/dev/null || kill -KILL "$PID" 2>/dev/null
  wait "$PID"; exec 2>&3 3>&-; RUN_RC=137
fi
ELAPSED=$(( $(date +%s) - START ))

# Codex's event stream never names the model, so this line is the only record of which
# model produced a run's output.
PROVENANCE="Engine: ${ENGINE} · Model: ${MODEL} · effort ${EFFORT}"

# Salvage: the run's own text first, then reasoning summaries, then the last tool call
# so a stalled run still names what it was doing when it died.
MESSAGES=""; REASONING=""; LASTCALL=""; RESULT_ERROR=""
if ! command -v jq >/dev/null; then
  MESSAGES="jq is not installed, so findings could not be extracted. Read the events directly: $JSONL"
  echo "external-run: jq missing; raw events at $JSONL" >&2
elif [ "$ENGINE" = codex ]; then
  MESSAGES=$(jq -r 'select(.type=="item.completed") | .item | select(.type=="agent_message") | .text' "$JSONL" 2>/dev/null)
  REASONING=$(jq -r 'select(.type=="item.completed") | .item | select(.type=="reasoning") | (.text // .summary // empty)' "$JSONL" 2>/dev/null)
  LASTCALL=$(jq -r 'select(.type=="item.completed") | .item | select(.type!="agent_message" and .type!="reasoning") | .type + ": " + ((.command // .query // .name // "") | tostring)' "$JSONL" 2>/dev/null | tail -1)
else
  # .result joins every assistant message with no separator, narration included, so the
  # findings are the assistant text after the last tool call. -R with fromjson? drops the
  # truncated last line a killed run can leave, which would fail a slurp of the whole file.
  MESSAGES=$(jq -Rrn '
    def text: [.message.content[]? | select(.type == "text") | .text] | join("");
    [inputs | fromjson? // empty | select(.type == "assistant" or .type == "tool_call")]
    | ((map(.type) | rindex("tool_call")) // -1) as $last
    | ([.[$last + 1:][] | select(.type == "assistant") | text | select(. != "")] | join("\n\n")) as $final
    | if $final != "" then $final
      else [.[] | select(.type == "assistant") | text | select(. != "")] | join("\n") end' "$JSONL" 2>/dev/null)
  LASTCALL=$(jq -r 'select(.type=="tool_call") | .tool_call | to_entries[0] | .key + ": " + ((.value.args.path // .value.args.command // "") | tostring)' "$JSONL" 2>/dev/null | tail -1)
  REPORTED=$(jq -r 'select(.type=="system" and .subtype=="init") | .model // empty' "$JSONL" 2>/dev/null | head -1)
  [ -n "$REPORTED" ] && [ "$REPORTED" != "$MODEL" ] && PROVENANCE="${PROVENANCE} · Cursor reported model: ${REPORTED}"
  [ "$(jq -r 'select(.type=="result") | .is_error' "$JSONL" 2>/dev/null | tail -1)" = "true" ] && RESULT_ERROR="result event has is_error"
fi

FAIL_WHY=""
if [ "$REASON" = "done" ]; then
  if [ "$RUN_RC" -ne 0 ]; then FAIL_WHY="exit ${RUN_RC}"; else FAIL_WHY="$RESULT_ERROR"; fi
fi

{
  case "$REASON" in
    done) [ -z "$FAIL_WHY" ] \
            && echo "# ${ENGINE_NAME} ${LABEL} — complete (${ELAPSED}s)" \
            || echo "# ${ENGINE_NAME} ${LABEL} — FAILED, ${FAIL_WHY} (${ELAPSED}s). Output below is partial." ;;
    idle) echo "# ${ENGINE_NAME} ${LABEL} — PARTIAL: stalled, no output for ${IDLE}s, killed at ${ELAPSED}s." ;;
    hard) echo "# ${ENGINE_NAME} ${LABEL} — PARTIAL: hard timeout at ${HARD}s." ;;
  esac
  echo "$PROVENANCE"
  [ "$REASON" != "done" ] && [ -n "$LASTCALL" ] && echo -e "\nLast tool call before the kill: \`${LASTCALL}\`"
  echo
  if [ -n "$MESSAGES" ]; then echo "$MESSAGES"; else
    echo "_No completed findings. Reasoning captured before the stall:_"; echo
    echo "${REASONING:-(nothing)}"
  fi
  if [ -n "$FAIL_WHY" ]; then echo; echo "## stderr"; echo '```'; tail -20 "$ERRLOG"; echo '```'; fi
} > "$OUT"

case "$REASON" in
  idle) echo "external-run: STALLED after ${ELAPSED}s (idle ${IDLE}s). Partial results in $OUT" >&2; exit 125 ;;
  hard) echo "external-run: HARD TIMEOUT at ${ELAPSED}s. Partial results in $OUT" >&2; exit 124 ;;
esac
[ -z "$FAIL_WHY" ] || { echo "external-run: ${ENGINE} failed (${FAIL_WHY}) after ${ELAPSED}s. See $OUT and $ERRLOG" >&2; exit 126; }
echo "external-run: complete in ${ELAPSED}s → $OUT"
