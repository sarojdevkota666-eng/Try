# Qwen image generator

Small CLI that connects to **Qwen-Image** (Alibaba Cloud Model Studio / DashScope) to turn text prompts into images. No dependencies beyond Python 3.8+.

## Setup

1. Create an API key at <https://modelstudio.console.alibabacloud.com/> (international) and enable the `qwen-image` model.
2. Export it:
   ```bash
   export DASHSCOPE_API_KEY=sk-...
   # Only if your key is for the mainland China (Beijing) region:
   # export DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com
   ```

## Usage

```bash
python qwen_image.py "a cozy cabin in snowy mountains at dusk, cinematic lighting"
python qwen_image.py "poster that says 'Hello Nepal' in bold letters" -s 928*1664 -n 2 -o out/
```

Options: `-m/--model` (`qwen-image`, `qwen-image-plus`), `-s/--size` (`1328*1328`, `1664*928`, `928*1664`, `1472*1140`, `1140*1472`), `-n`, `--negative`, `--no-extend`, `--watermark`.

Images are saved to `images/` by default (the API's own URLs expire after about 24 hours).

## Use from Python

```python
from qwen_image import generate
urls = generate("a red panda drinking tea, watercolor", api_key="sk-...")
```
