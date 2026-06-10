#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-genai",
#     "Pillow",
# ]
# ///
import argparse
import base64
import io
import os
import sys
from google import genai
from google.genai import types
from PIL import Image


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Google Gemini.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --prompt "A cat in space" --output cat.png
  %(prog)s --prompt "Same style but blue" --reference input.png --output blue.png
  %(prog)s --prompt "Abstract art" --output art.png --size 2K
        """
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Text prompt describing the image to generate"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path for the generated image"
    )
    parser.add_argument(
        "--reference",
        help="Optional reference image path for style/content guidance"
    )
    parser.add_argument(
        "--size",
        default="4K",
        choices=["1K", "2K", "4K"],
        help="Output image size (default: 4K)"
    )
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        print("Set it with: export GEMINI_API_KEY='your-api-key'", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    contents = [args.prompt]

    if args.reference:
        try:
            reference_image = Image.open(args.reference)
            contents.append(reference_image)
            print(f"Using reference image: {args.reference}")
        except FileNotFoundError:
            print(f"Error: Reference image '{args.reference}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error loading reference image: {e}", file=sys.stderr)
            sys.exit(1)

    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    print(f"Generating image with size: {args.size}...")

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["Text", "Image"],
            )
        )
    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)

    image_saved = False
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(f"Model response: {part.text}")
        elif part.inline_data is not None:
            image_data = base64.b64decode(part.inline_data.data)
            generated_image = Image.open(io.BytesIO(image_data))
            generated_image.save(args.output)
            print(f"Image saved to: {args.output}")
            image_saved = True

    if not image_saved:
        print("Warning: No image was generated in the response.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
