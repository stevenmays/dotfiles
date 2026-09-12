---
name: gemini-image-generator
description: Generate images with Google Gemini. Use only when the user names Gemini or asks for a Gemini image. For every other image request use codex-image-generator, the default path.
---

# gemini-image-generator

## Instructions

Use this skill only when the user asks for Gemini by name. `codex-image-generator` is the default for image requests that name no provider.

The skill supports:
- Text-to-image generation from prompts
- Image-to-image generation with a reference image
- Multiple output sizes (1K, 2K, 4K)
- Custom output paths

The API key must be set via the `GEMINI_API_KEY` environment variable.

## Parameters

- `--prompt` (required): The text prompt describing the image to generate
- `--output` (required): Output file path for the generated image
- `--reference`: Optional reference image for style/content guidance
- `--size`: Image size - "1K", "2K", or "4K" (default: 4K)

## Examples

### Basic text-to-image generation
```bash
./scripts/generate.py --prompt "A serene mountain landscape at sunset" --output images/landscape.png
```

### With reference image for style guidance
```bash
./scripts/generate.py --prompt "Same character but wearing a party hat" --reference images/character.png --output images/party.png
```

### Different output size
```bash
./scripts/generate.py --prompt "Abstract art" --output art.png --size 2K
```

## Setup

Set your API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

Requires [uv](https://docs.astral.sh/uv/) - dependencies are managed inline via PEP 723.
