#!/usr/bin/env python3
"""Generate or edit images with Google Gemini (Nano Banana) image models.

Usage:
    export GEMINI_API_KEY=...
    python gemini_image.py "a red panda drinking tea, watercolor" -o images/
    python gemini_image.py "make the sky purple" -i photo.jpg      # edit an image

Uses only the Python standard library.
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


def generate(prompt, api_key, model=DEFAULT_MODEL, aspect_ratio=None, input_images=()):
    """Return (list of (mime_type, bytes), text) for the prompt and optional input images."""
    parts = [{"text": prompt}]
    for path in input_images:
        mime = mimetypes.guess_type(path)[0] or "image/png"
        with open(path, "rb") as f:
            parts.append({"inlineData": {"mimeType": mime, "data": base64.b64encode(f.read()).decode()}})

    config = {"responseModalities": ["TEXT", "IMAGE"]}
    if aspect_ratio:
        config["imageConfig"] = {"aspectRatio": aspect_ratio}
    body = {"contents": [{"parts": parts}], "generationConfig": config}

    req = urllib.request.Request(API_URL.format(model=model), data=json.dumps(body).encode(), method="POST")
    req.add_header("x-goog-api-key", api_key)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')}") from None

    images, texts = [], []
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            if "inlineData" in part:
                images.append((part["inlineData"].get("mimeType", "image/png"),
                               base64.b64decode(part["inlineData"]["data"])))
            elif "text" in part:
                texts.append(part["text"])
    if not images:
        raise RuntimeError(f"No image returned: {' '.join(texts) or json.dumps(data)[:500]}")
    return images, "\n".join(texts)


def main():
    p = argparse.ArgumentParser(description="Generate images with Gemini.")
    p.add_argument("prompt")
    p.add_argument("-o", "--out-dir", default="images")
    p.add_argument("-m", "--model", default=DEFAULT_MODEL,
                   help="e.g. gemini-2.5-flash-image, gemini-3-pro-image-preview")
    p.add_argument("-a", "--aspect-ratio", choices=ASPECT_RATIOS)
    p.add_argument("-i", "--input", action="append", default=[], help="reference image to edit (repeatable)")
    args = p.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        sys.exit("Set GEMINI_API_KEY (get one at https://aistudio.google.com/apikey)")

    images, text = generate(args.prompt, api_key, model=args.model,
                            aspect_ratio=args.aspect_ratio, input_images=args.input)
    if text:
        print(text, file=sys.stderr)
    os.makedirs(args.out_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for i, (mime, blob) in enumerate(images):
        path = os.path.join(args.out_dir, f"gemini-{stamp}-{i}{EXTENSIONS.get(mime, '.png')}")
        with open(path, "wb") as f:
            f.write(blob)
        print(path)


if __name__ == "__main__":
    main()
