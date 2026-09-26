#!/usr/bin/env bash
# Generate or edit a raster image with Nano Banana through the Antigravity CLI's generate_image tool.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: generate.sh --prompt TEXT --output PATH [--aspect RATIO] [--reference IMG]...
                   [--model SLUG] [--timeout SECONDS] [--open]

  --prompt     Image description. Quote exact in-image text inside the prompt.
  --output     Path ending in .jpg, .jpeg, or .png. Parent directory is created; an existing file is never replaced.
  --aspect     One of 1:1 2:3 3:2 3:4 4:3 9:16 16:9 (default: 1:1).
  --reference  Image to edit, blend, or use as a style reference. Repeatable, at most 3.
  --model      agy driver model that calls generate_image (default: gemini-3.8-flash-low).
  --timeout    Seconds agy may run before it gives up (default: 240).
  --open       Open the result in the default viewer when it verifies.
USAGE
}

prompt="" output="" aspect="1:1" model="gemini-3.8-flash-low" timeout=240 open_result=0
refs=()
while [ $# -gt 0 ]; do
  case "$1" in
    --prompt|--output|--aspect|--reference|--model|--timeout)
      [ $# -ge 2 ] || { echo "$1 needs a value" >&2; exit 2; } ;;
  esac
  case "$1" in
    --prompt) prompt="$2"; shift 2 ;;
    --output) output="$2"; shift 2 ;;
    --aspect) aspect="$2"; shift 2 ;;
    --reference) refs+=("$2"); shift 2 ;;
    --model) model="$2"; shift 2 ;;
    --timeout) timeout="$2"; shift 2 ;;
    --open) open_result=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[ -n "$prompt" ] && [ -n "$output" ] || { usage >&2; exit 2; }

case "$(printf '%s' "${output##*.}" | tr '[:upper:]' '[:lower:]')" in
  jpg|jpeg) want=jpeg ;;
  png) want=png ;;
  *) echo "--output must end in .jpg, .jpeg, or .png: $output" >&2; exit 2 ;;
esac
case "$aspect" in
  1:1|2:3|3:2|3:4|4:3|9:16|16:9) ;;
  *) echo "--aspect must be one of 1:1 2:3 3:2 3:4 4:3 9:16 16:9, got: $aspect" >&2; exit 2 ;;
esac
case "$timeout" in
  ''|*[!0-9]*) echo "--timeout must be a whole number of seconds, got: $timeout" >&2; exit 2 ;;
esac
[ "${#refs[@]}" -le 3 ] || { echo "generate_image accepts at most 3 references, got ${#refs[@]}" >&2; exit 2; }
ref_paths=()
for ref in "${refs[@]+"${refs[@]}"}"; do
  [ -f "$ref" ] || { echo "Reference image not found: $ref" >&2; exit 2; }
  ref_paths+=("$(cd "$(dirname "$ref")" && pwd)/$(basename "$ref")")
done
[ ! -e "$output" ] || {
  echo "$output already exists; pick a sibling name such as ${output%.*}-v2.${output##*.}" >&2
  exit 2
}

command -v agy >/dev/null || { echo "agy (Antigravity CLI) not found on PATH" >&2; exit 3; }
command -v jq >/dev/null || { echo "jq not found on PATH; the script needs it to read agy's JSON result" >&2; exit 3; }

mkdir -p "$(dirname "$output")"
output="$(cd "$(dirname "$output")" && pwd)/$(basename "$output")"
workdir="$(dirname "$output")"
log="$(mktemp -t gemini-image)"

# generate_image requires ImageName to be lowercase with at most 3 underscore-separated words.
stem="${output##*/}"
image_name="$(printf '%s' "${stem%.*}" | LC_ALL=C tr '[:upper:]' '[:lower:]' | LC_ALL=C tr -cs 'a-z0-9' '_' \
  | sed 's/^_*//; s/_*$//' | cut -d_ -f1-3)"
[ -n "$image_name" ] || image_name=image

params="AspectRatio $aspect and ImageName $image_name"
if [ "${#ref_paths[@]}" -gt 0 ]; then
  params="AspectRatio $aspect, ImageName $image_name, and ImagePaths $(jq -cn '$ARGS.positional' --args "${ref_paths[@]}")"
fi
# Without the explicit tool name the driver reaches for run_command, which headless agy denies.
task="Use your generate_image tool (never run_command or any shell) with $params to generate: $prompt
Reply with only the absolute path of the saved image file."

start=$(date +%s)
(cd "$workdir" && agy -p "$task" --model "$model" --output-format json --print-timeout "${timeout}s" </dev/null) \
  >"$log" 2>&1 || {
  status=$?
  echo "agy exited $status; log: $log" >&2
  tail -20 "$log" >&2
  exit 4
}
elapsed=$(( $(date +%s) - start ))

# The log mixes agy's stderr notices with its one-line JSON result, so parse only lines that are JSON objects.
conversation="$(jq -rR 'fromjson? | objects | .conversation_id // empty' "$log" | tail -1)"
denied="$(jq -rRn '[inputs | fromjson? | objects | .denied_actions[]? | "\(.display_name // .action) (\(.action))"]
  | join(", ")' "$log")"
[ -z "$denied" ] || echo "warning: agy denied $denied in headless mode; a denied run usually leaves no image" >&2
[ -n "$conversation" ] || { echo "agy returned no conversation_id; log: $log" >&2; tail -20 "$log" >&2; exit 5; }

# Tests point ANTIGRAVITY_CLI_HOME at a temp dir.
brain="${ANTIGRAVITY_CLI_HOME:-$HOME/.gemini/antigravity-cli}/brain/$conversation"
src=""
for candidate in "$brain/$image_name"_*.jpg "$brain/$image_name"_*.jpeg "$brain/$image_name"_*.png; do
  [ -f "$candidate" ] || continue
  if [ -z "$src" ] || [ "$candidate" -nt "$src" ]; then src="$candidate"; fi
done
[ -n "$src" ] || { echo "No ${image_name}_* image in $brain; log: $log" >&2; tail -20 "$log" >&2; exit 5; }

src_kind="$(file -b "$src")"
case "$src_kind" in
  JPEG*) have=jpeg ;;
  PNG*) have=png ;;
  *) have=other ;;
esac
note=""
if [ "$have" = "$want" ]; then
  cp "$src" "$output"
else
  command -v sips >/dev/null || { echo "sips not found; cannot convert $src to $want" >&2; exit 3; }
  sips -s format "$want" "$src" --out "$output" >>"$log" 2>&1 \
    || { echo "sips could not convert $src to $want; log: $log" >&2; exit 5; }
  note=", converted from ${src_kind%% *} source"
fi

kind="$(file -b "$output" 2>/dev/null || true)"
case "$kind" in
  *"image data"*) ;;
  *) echo "No image at $output ($kind); log: $log" >&2; exit 5 ;;
esac

echo "$output"
echo "$kind, $(stat -f %z "$output" 2>/dev/null || stat -c %s "$output") bytes, ${elapsed}s, driver $model, conversation $conversation$note"
if [ "$open_result" -eq 1 ]; then open "$output"; fi
exit 0
