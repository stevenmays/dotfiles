#!/usr/bin/env bash
# Generate a raster image through the Codex CLI's built-in image_gen tool.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: generate.sh --prompt TEXT --output PATH [--model MODEL] [--reference IMG]... [--open]

  --prompt     Image description. Quote exact in-image text inside the prompt.
  --output     Absolute or relative path for the PNG. Parent directory is created.
  --model      Codex model that drives image_gen (default: gpt-5.6-sol).
  --reference  Attach an image as a style, composition, or edit reference. Repeatable.
  --open       Open the result in the default viewer when it verifies.
USAGE
}

prompt="" output="" model="gpt-5.6-sol" open_result=0
refs=()
while [ $# -gt 0 ]; do
  case "$1" in
    --prompt) prompt="$2"; shift 2 ;;
    --output) output="$2"; shift 2 ;;
    --model) model="$2"; shift 2 ;;
    --reference) refs+=("$2"); shift 2 ;;
    --open) open_result=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[ -n "$prompt" ] && [ -n "$output" ] || { usage >&2; exit 2; }
command -v codex >/dev/null || { echo "codex CLI not found on PATH" >&2; exit 3; }

mkdir -p "$(dirname "$output")"
output="$(cd "$(dirname "$output")" && pwd)/$(basename "$output")"
workdir="$(dirname "$output")"
log="$(mktemp -t codex-image).log"

image_args=()
for ref in "${refs[@]+"${refs[@]}"}"; do
  [ -f "$ref" ] || { echo "Reference image not found: $ref" >&2; exit 2; }
  image_args+=("--image=$ref")
done

task="Use the built-in image_gen tool to generate this image: $prompt
Save the final PNG to exactly $output (copy it there from \$CODEX_HOME/generated_images if needed).
Reply with only the absolute path of the saved file."

start=$(date +%s)
codex exec -m "$model" -C "$workdir" --sandbox workspace-write --skip-git-repo-check \
  --ephemeral "${image_args[@]+"${image_args[@]}"}" "$task" >"$log" 2>&1 \
  || { echo "codex exec failed; log: $log" >&2; tail -20 "$log" >&2; exit 4; }
elapsed=$(( $(date +%s) - start ))

kind="$(file -b "$output" 2>/dev/null || true)"
case "$kind" in
  *"image data"*) ;;
  *) echo "No image at $output ($kind); log: $log" >&2; tail -20 "$log" >&2; exit 5 ;;
esac

echo "$output"
echo "$kind, $(stat -f %z "$output") bytes, ${elapsed}s, model $model"
[ "$open_result" -eq 1 ] && open "$output"
exit 0
