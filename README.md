# AI image generators

Small, dependency-free Python CLIs (Python 3.8+) that turn text prompts into images:

- `qwen_image.py` — **Qwen-Image** via Alibaba Cloud Model Studio / DashScope
- `gemini_image.py` — **Gemini** image models (Nano Banana) via the Gemini API (see [Gemini](#gemini) below)

## Qwen

### Setup

1. Create an API key at <https://modelstudio.console.alibabacloud.com/> (international) and enable the `qwen-image` model.
2. Export it:
   ```bash
   export DASHSCOPE_API_KEY=sk-...
   # Only if your key is for the mainland China (Beijing) region:
   # export DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com
   ```

### Usage

```bash
python qwen_image.py "a cozy cabin in snowy mountains at dusk, cinematic lighting"
python qwen_image.py "poster that says 'Hello Nepal' in bold letters" -s 928*1664 -n 2 -o out/
```

Options: `-m/--model` (`qwen-image`, `qwen-image-plus`), `-s/--size` (`1328*1328`, `1664*928`, `928*1664`, `1472*1140`, `1140*1472`), `-n`, `--negative`, `--no-extend`, `--watermark`.

Images are saved to `images/` by default (the API's own URLs expire after about 24 hours).

### Use from Python

```python
from qwen_image import generate
urls = generate("a red panda drinking tea, watercolor", api_key="sk-...")
```

## Gemini

### Setup

1. Create an API key at <https://aistudio.google.com/apikey>. Image models require billing to be enabled on the key's Google Cloud project.
2. `export GEMINI_API_KEY=...`

### Usage

```bash
python gemini_image.py "a cozy cabin in snowy mountains at dusk, cinematic lighting" -a 16:9
python gemini_image.py "turn this photo into a Studio Ghibli style painting" -i photo.jpg
```

Options: `-m/--model` (default `gemini-2.5-flash-image`; override with `-m` or `GEMINI_IMAGE_MODEL`, e.g. `gemini-3-pro-image-preview`), `-a/--aspect-ratio` (`1:1`, `16:9`, `9:16`, ...), `-i/--input` (reference image to edit; repeatable), `-o/--out-dir`.

### Using it from Claude Code

Claude Code can run this script for you. Give it the key and ask for an image in plain words, e.g. "make an image of a mountain sunrise".

- **Local CLI / desktop:** `export GEMINI_API_KEY=...` in the shell before you start `claude`.
- **Claude Code on the web (cloud sessions):** add `GEMINI_API_KEY` as an environment variable in the cloud environment's settings, then start a new session. `generativelanguage.googleapis.com` must be allowed by the environment's network access.
