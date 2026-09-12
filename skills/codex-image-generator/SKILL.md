---
name: codex-image-generator
description: Default image generation path. Generate or edit raster images (hero images, illustrations, textures, product shots, mockups, transparent cutouts) through the Codex CLI's built-in image_gen tool, run in a subagent. Use whenever the user asks for an image, picture, illustration, or visual asset and does not name a provider. Not for SVG, icons, or diagrams that belong in code. When the user names Gemini, use gemini-image-generator instead.
---

# Codex image generator

Codex CLI ships an `image_gen` tool and a bundled `imagegen` skill that shapes prompts, saves under `$CODEX_HOME/generated_images/`, and copies the result to a requested path. This skill wraps one `codex exec` call around that tool and verifies the file. No API key is needed; Codex uses its own login.

## Run it

Delegate the run to a `general-purpose` subagent pinned to `model: "sonnet"`. A Codex run takes about 50 seconds and the result is a file check, so the session must not block on it. Give the subagent the exact command and the verification rule below.

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/codex-image-generator/scripts/generate.sh" \
  --prompt "<image description>" \
  --output <path>.png \
  [--reference <image>]... [--model gpt-6-astra] [--open]
```

- `--prompt`: describe scene, subject, style, composition, and lighting. Quote exact in-image text verbatim. Ask for a transparent background when the asset must sit on the page's color.
- `--output`: the final PNG path. The script creates the parent directory and rejects a run that leaves no image there.
- `--reference`: attaches an image to the Codex prompt. Use it for style guidance or to edit an existing image; say in the prompt which role each reference plays and what must stay unchanged. Edits drift: in testing a sky-only change also altered style, aspect ratio, and background detail, so list every invariant and check the result.
- `--model`: defaults to `gpt-5.6-sol`. `gpt-6-astra` produces the same image quality at higher cost, so use it only when the user asks.
- `--open`: opens the verified image in Preview. Use it for one-off requests so the user sees the result. Skip it for assets that code consumes.

The script prints the absolute path, then the `file` description, byte size, elapsed seconds, and model. Exit code 5 means Codex finished without leaving an image at the path; the log path in stderr shows what Codex did.

## Rules

- One asset per call. For variants or a set, run the script once per asset with distinct prompts.
- Never overwrite an existing asset the user did not ask to replace. Use a sibling name such as `hero-v2.png`.
- Report the saved path and the final prompt. Do not paste the image into chat.
- If `codex` is missing or not logged in, say so and stop. Do not fall back to Gemini unless the user asks for it.
