#!/usr/bin/env bash
# Run a task on a Gemini model through the Antigravity CLI (`agy`) so it cannot hang the
# calling session. It mirrors external-run.sh: the same flags, exit codes, and --out contract.
#
# `agy` has no per-run switch for its network-reaching tools (search_web, read_url_content,
# browser_*, call_mcp_tool, open_browser_url), and a run that reaches for one can block with
# no output. This wrapper streams NDJSON events, kills the run when it stops producing them,
# and salvages whatever arrived before the stall.
#
# Usage:
#   gemini-run.sh --prompt <file> --out <file> [--model SLUG] [--idle 300] [--hard 1800]
#                 [--cd DIR] [--sandbox read-only|workspace-write] [--label run]
#
# The model is always pinned: --model, else $GEMINI_SUBAGENT_MODEL, else gemini-3.1-pro-high.
# The slug carries the effort in its -low|-medium|-high suffix, so there is no --effort.
#
# --sandbox defaults to read-only: headless agy then auto-denies every file write and shell
# command. workspace-write allows file writes but still denies shell commands, so the caller
# runs the tests and reads `git diff` afterwards. Point a workspace-write run at a feature
# branch only: this wrapper never stages, commits, or reverts anything.
#
# Exit codes:
#   0    completed normally; denied tool calls are listed in --out, not treated as a failure
#   124  hard timeout: total budget exceeded
#   125  idle stall: no output for --idle seconds
#   126  engine failed: nonzero exit, or a result event whose status is not SUCCESS
#   2    bad usage, agy not on PATH, or a non-Gemini model
#
# --out always exists on return. A partial result is marked in its header. After a
# workspace-write run the real artifact is the working tree: read `git diff`, and
# treat --out as the run's own account of what it did.

set -uo pipefail

IDLE=300
HARD=1800
# 1s: a finished run returns within a second instead of waiting out a longer poll.
POLL=1
WORKDIR="$PWD"
PROMPT=""
OUT=""
MODEL=""
SANDBOX="read-only"
LABEL="run"

while [ $# -gt 0 ]; do
  case "$1" in
    --prompt|--out|--model|--idle|--hard|--cd|--sandbox|--label)
      # Guard before expanding $2: under `set -u` a trailing flag aborts with a raw
      # bash error and exit 1, not the exit 2 this script documents.
      [ $# -ge 2 ] || { echo "gemini-run: $1 requires a value" >&2; exit 2; }
      case "$1" in
        --prompt)  PROMPT="$2" ;;
        --out)     OUT="$2" ;;
        --model)   MODEL="$2" ;;
        --idle)    IDLE="$2" ;;
        --hard)    HARD="$2" ;;
        --cd)      WORKDIR="$2" ;;
        --sandbox) SANDBOX="$2" ;;
        --label)   LABEL="$2" ;;
      esac
      shift 2 ;;
    *) echo "gemini-run: unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$PROMPT" ] && [ -n "$OUT" ] || { echo "usage: gemini-run.sh --prompt <file> --out <file> [--model SLUG] [--idle N] [--hard N] [--cd DIR] [--sandbox MODE] [--label NAME]" >&2; exit 2; }
case "$SANDBOX" in
  read-only|workspace-write) ;;
  *) echo "gemini-run: --sandbox must be read-only or workspace-write, got: $SANDBOX" >&2; exit 2 ;;
esac
[ -r "$PROMPT" ] || { echo "gemini-run: prompt file not readable: $PROMPT" >&2; exit 2; }
[ -d "$WORKDIR" ] || { echo "gemini-run: --cd directory not found: $WORKDIR" >&2; exit 2; }
command -v agy >/dev/null || { echo "gemini-run: agy not on PATH: install the Antigravity CLI" >&2; exit 2; }

MODEL="${MODEL:-${GEMINI_SUBAGENT_MODEL:-gemini-3.1-pro-high}}"
# agy also serves Claude and GPT-OSS models, and either would defeat the point of a second
# model family.
case "$MODEL" in
  *[Gg][Ee][Mm][Ii][Nn][Ii]*) ;;
  *) echo "gemini-run: runs Gemini models only, got: $MODEL" >&2; exit 2 ;;
esac
case "$MODEL" in
  *-low)    EFFORT="low" ;;
  *-medium) EFFORT="medium" ;;
  *-high)   EFFORT="high" ;;
  *)        EFFORT="model default" ;;
esac

JSONL="${OUT%.md}.jsonl"
ERRLOG="${OUT%.md}.stderr"
: > "$JSONL"; : > "$ERRLOG"

mtime() { stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null || echo 0; }

# Headless agy auto-denies any tool it would have to ask about: with no --mode, every file
# write and shell command; with accept-edits, shell commands only. Never pass
# --dangerously-skip-permissions: the user's policy forbids it.
MODE_ARGS=""
[ "$SANDBOX" = workspace-write ] && MODE_ARGS="--mode accept-edits"
# Read before the cd below, which would break a relative --prompt path. The prompt travels as
# an argument, so the OS argument limit (`getconf ARG_MAX`) caps its size.
PROMPT_TEXT=$(cat "$PROMPT")

# agy has no working-directory flag, so the subshell cds and then execs agy; $! stays the agy
# process group. stdin is /dev/null because a background process group that reads the
# terminal stops. --print-timeout makes agy stop itself at the same hard budget.
set -m
# MODE_ARGS is unquoted on purpose: read-only passes no --mode at all, and an empty array
# trips `set -u` on macOS's bash 3.2.
( cd "$WORKDIR" && exec agy \
    -p "$PROMPT_TEXT" \
    --model "$MODEL" \
    --output-format stream-json \
    --print-timeout "${HARD}s" \
    $MODE_ARGS ) < /dev/null > "$JSONL" 2> "$ERRLOG" &
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
# agy's own --print-timeout can end the run just before the watchdog notices. That is still
# the hard budget running out, not an engine failure.
[ "$REASON" = "done" ] && [ "$ELAPSED" -ge "$HARD" ] && REASON="hard"

PROVENANCE="Engine: gemini · Model: ${MODEL} · effort ${EFFORT}"

# Salvage: the result's response first, then the streamed text, then the last tool call so a
# stalled run still names what it was doing when it died.
MESSAGES=""; LASTCALL=""; DENIED=""; RESULT_ERROR=""
if ! command -v jq >/dev/null; then
  MESSAGES="jq is not installed, so findings could not be extracted. Read the events directly: $JSONL"
  echo "gemini-run: jq missing; raw events at $JSONL" >&2
else
  MESSAGES=$(jq -r 'select(.event=="result") | .result.response // empty' "$JSONL" 2>/dev/null)
  # Response text streams as fragments that split mid-word, so they join with no separator.
  [ -n "$MESSAGES" ] || MESSAGES=$(jq -j 'select(.event=="step_update") | .step_update | select(.step_type=="agent_response") | .text_delta // empty' "$JSONL" 2>/dev/null)
  # Parameter names vary per tool (AbsolutePath, TargetFile, Prompt), so take the first value.
  LASTCALL=$(jq -r 'select(.event=="step_update") | .step_update | select(.step_type=="tool") | .tool_name + ": " + ((.tool_info.parameters // {} | to_entries | .[0].value // "") | tostring | gsub("\n"; " "))' "$JSONL" 2>/dev/null | tail -1)
  REPORTED=$(jq -r 'select(.event=="init") | .init.model // empty' "$JSONL" 2>/dev/null | head -1)
  [ -n "$REPORTED" ] && [ "$REPORTED" != "$MODEL" ] && PROVENANCE="${PROVENANCE} · agy reported model: ${REPORTED}"
  DENIED=$(jq -r 'select(.event=="result") | [.result.denied_actions[]?.action] | unique | join(", ")' "$JSONL" 2>/dev/null | tail -1)
  STATUS=$(jq -r 'select(.event=="result") | .result.status // empty' "$JSONL" 2>/dev/null | tail -1)
  [ -n "$STATUS" ] && [ "$STATUS" != "SUCCESS" ] && RESULT_ERROR="result status ${STATUS}"
fi

FAIL_WHY=""
if [ "$REASON" = "done" ]; then
  if [ "$RUN_RC" -ne 0 ]; then FAIL_WHY="exit ${RUN_RC}"; else FAIL_WHY="$RESULT_ERROR"; fi
fi

{
  case "$REASON" in
    done) [ -z "$FAIL_WHY" ] \
            && echo "# Gemini ${LABEL} — complete (${ELAPSED}s)" \
            || echo "# Gemini ${LABEL} — FAILED, ${FAIL_WHY} (${ELAPSED}s). Output below is partial." ;;
    idle) echo "# Gemini ${LABEL} — PARTIAL: stalled, no output for ${IDLE}s, killed at ${ELAPSED}s." ;;
    hard) echo "# Gemini ${LABEL} — PARTIAL: hard timeout at ${HARD}s." ;;
  esac
  echo "$PROVENANCE"
  # Not a failure: headless agy cannot ask, so it refuses the tool and the run carries on.
  [ -n "$DENIED" ] && echo "Denied in headless mode: ${DENIED}"
  [ "$REASON" != "done" ] && [ -n "$LASTCALL" ] && printf '\nLast tool call before the kill: `%s`\n' "$LASTCALL"
  echo
  echo "${MESSAGES:-_No completed findings._}"
  if [ -n "$FAIL_WHY" ]; then echo; echo "## stderr"; echo '```'; tail -20 "$ERRLOG"; echo '```'; fi
} > "$OUT"

case "$REASON" in
  idle) echo "gemini-run: STALLED after ${ELAPSED}s (idle ${IDLE}s). Partial results in $OUT" >&2; exit 125 ;;
  hard) echo "gemini-run: HARD TIMEOUT at ${ELAPSED}s. Partial results in $OUT" >&2; exit 124 ;;
esac
[ -z "$FAIL_WHY" ] || { echo "gemini-run: agy failed (${FAIL_WHY}) after ${ELAPSED}s. See $OUT and $ERRLOG" >&2; exit 126; }
echo "gemini-run: complete in ${ELAPSED}s → $OUT"
