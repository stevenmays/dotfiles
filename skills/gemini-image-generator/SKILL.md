---
name: gemini-image-generator
description: Generate or edit raster images with Google's Nano Banana model through the Antigravity CLI's built-in generate_image tool, run in a subagent. Use when the user names Gemini, Nano Banana, or Antigravity. Not for SVG, icons, or code diagrams. The default image path is codex-image-generator.
---

# Gemini image generator

The Antigravity CLI (`agy`) has a built-in `generate_image` tool backed by Google's Nano Banana model. This skill wraps one headless `agy` call around that tool, copies the image out of the Antigravity brain directory, and verifies the file. No API key is needed; `agy` uses its own Antigravity login.

## Run it

Delegate the run to a `general-purpose` subagent pinned to `model: "sonnet"`. A run takes about 15 to 30 seconds and the result is a file check, so the session must not block on it. Give the subagent the exact command and the exit codes below.

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/gemini-image-generator/scripts/generate.sh" \
  --prompt "<image description>" \
  --output <path>.jpg \
  [--aspect 16:9] [--reference <image>]... [--open]
```

- `--prompt`: describe subject, composition, action, location, and style. The Prompting section lists Google's guidance.
- `--output`: the final path, ending in `.jpg`, `.jpeg`, or `.png`. The script creates the parent directory and refuses to replace an existing file.
- `--aspect`: one of `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `9:16`, or `16:9`. The default is `1:1`.
- `--reference`: passes a local image to edit, blend, or use as a style reference. Repeat it up to 3 times. Say in the prompt which role each reference plays and what must stay unchanged. In testing, a color-only edit kept the composition, background, and aspect ratio.
- `--model`: the `agy` driver model that calls `generate_image`. The default `gemini-3.8-flash-low` is the cheapest slug and drives the tool in about 15 seconds. The driver never changes the image model.
- `--timeout`: seconds before `agy` gives up. The default is `240`.
- `--open`: opens the verified image in Preview. Use it for one-off requests so the user sees the result. Skip it for assets that code consumes.

The script prints the absolute path on line 1. Line 2 holds the `file` description, byte size, elapsed seconds, driver model, and `agy` conversation ID. The exit codes are:

- `2`: bad usage, a missing reference, a fourth reference, or an existing file at `--output`.
- `3`: `agy` or `jq` is missing from `PATH`, or `sips` is missing when a format conversion is needed.
- `4`: `agy` exited nonzero. Stderr holds the log path and its last 20 lines.
- `5`: `agy` finished without leaving an image. A `warning: agy denied` line on stderr means headless mode blocked a tool that the driver tried instead of `generate_image`.

## What this path can and cannot produce

The `generate_image` tool takes only a prompt, an image name, an aspect ratio, and reference paths. It has no resolution, format, or model parameter, so asking for "4K" or "transparent PNG" in the prompt changes nothing.

| | This skill (`agy`) | Direct Gemini API (not wrapped) |
|---|---|---|
| Model | Nano Banana 2 (`gemini-3.1-flash-image`); Nano Banana Pro (`gemini-3-pro-image`) where the account has it; no choice | Flash or Pro, chosen per call |
| Resolution | 1K tier only: 1024x1024 at `1:1`, 1264x848 at `3:2`, 1376x768 at `16:9` | Flash 0.5K, 1K, 2K, 4K; Pro 1K, 2K, 4K |
| Format | Always JPEG (JFIF, 300 DPI) | PNG or JPEG |
| Transparency | None | None |
| Aspect ratios | 7: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `9:16`, `16:9` | 10: adds `21:9`, `5:4`, `4:5` |
| References | Up to 3 | Up to 14 |
| Cost | Nothing per image; Antigravity login and quota; no API key | Flash $0.067 at 1K, $0.101 at 2K, $0.151 at 4K; Pro $0.134 at 1K or 2K, $0.24 at 4K |
| Watermark | SynthID, cannot be disabled | SynthID, cannot be disabled |

2K and 4K output, PNG output, the `21:9`, `5:4`, and `4:5` ratios, and more than 3 references need the direct Gemini API. This skill does not wrap that API. When a request needs one of them, tell the user the per-image price from the table before you switch paths.

A `.png` output is a container conversion by `sips` from the JPEG source. The conversion adds no alpha channel. When the user needs real transparency, offer `codex-image-generator`, which accepts a transparent-background request.

Reference images can be PNG, JPEG, or WebP. Gemini scales each one down to at most 3072x3072.

The tool saves under `~/.gemini/antigravity-cli/brain/<conversation_id>/`. That directory is ephemeral, so only the copy at `--output` is durable.

Sources: [Antigravity models](https://antigravity.google/docs/models/), [Nano Banana Pro in Antigravity](https://antigravity.google/blog/nano-banana-pro), [Gemini API image generation](https://ai.google.dev/gemini-api/docs/image-generation), [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing), [Firebase AI Logic input file requirements](https://firebase.google.com/docs/ai-logic/input-file-requirements), [Antigravity agent skills: image generation](https://dev.to/googleai/elevating-antigravity-agent-skills-part-2-image-generation-2jno).

## Prompting

Google's guidance for Nano Banana:

- Open with "Create an image of", then describe the subject, composition, action, location, and style.
- Describe what you want in positive terms: "an empty street", not "no cars".
- Use camera language for framing, such as wide-angle, macro, or low-angle.
- Quote in-image text verbatim and name the font or type style. Nano Banana Pro renders text best.
- For a cutout, ask for a solid chroma-key green (`#00FF00`) background with flat lighting and sharp edges. Then key out the green in a separate step.
- For an edit, name the change and list every element that must stay unchanged.

Sources: [Gemini API image generation](https://ai.google.dev/gemini-api/docs/image-generation), [Gemini image prompt guide](https://deepmind.google/models/gemini-image/prompt-guide/).

## Rules

- One asset per call. For variants or a set, run the script once per asset with distinct prompts.
- Never overwrite an existing asset the user did not ask to replace. Use a sibling name such as `hero-v2.jpg`.
- Report the saved path and the final prompt. Do not paste the image into chat.
- If `agy` is missing or not logged in, say so and stop.
- Pin the driver model. Keep `gemini-3.8-flash-low` unless the user names another slug from `agy models`.
- Never pass `--dangerously-skip-permissions` to `agy`. The `generate_image` tool needs no permission.
- Use a `.png` output only when a consumer needs the PNG container, because the conversion adds no alpha.
