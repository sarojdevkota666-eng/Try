#!/usr/bin/env python3
"""Generate images with Qwen-Image via Alibaba Cloud DashScope (Model Studio).

Usage:
    export DASHSCOPE_API_KEY=sk-...
    python qwen_image.py "a red panda drinking tea, watercolor" -o images/

Uses only the Python standard library.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

# International region by default; set DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com
# for the mainland China (Beijing) region. API keys are region-specific.
BASE_URL = os.environ.get("DASHSCOPE_BASE_URL", "https://dashscope-intl.aliyuncs.com").rstrip("/")
SUBMIT_PATH = "/api/v1/services/aigc/text2image/image-synthesis"
TASK_PATH = "/api/v1/tasks/"

SIZES = ["1328*1328", "1664*928", "928*1664", "1472*1140", "1140*1472"]


def _request(method, url, api_key, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')}") from None


def generate(prompt, api_key, model="qwen-image", size="1328*1328", n=1,
             negative_prompt=None, prompt_extend=True, watermark=False,
             poll_interval=3, timeout=300):
    """Submit a text-to-image task and return the list of image URLs."""
    params = {"size": size, "n": n, "prompt_extend": prompt_extend, "watermark": watermark}
    body = {"model": model, "input": {"prompt": prompt}, "parameters": params}
    if negative_prompt:
        body["input"]["negative_prompt"] = negative_prompt

    resp = _request("POST", BASE_URL + SUBMIT_PATH, api_key, body,
                    headers={"X-DashScope-Async": "enable"})
    task_id = resp["output"]["task_id"]

    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(poll_interval)
        output = _request("GET", BASE_URL + TASK_PATH + task_id, api_key)["output"]
        status = output["task_status"]
        if status == "SUCCEEDED":
            return [r["url"] for r in output.get("results", []) if "url" in r]
        if status in ("FAILED", "CANCELED", "UNKNOWN"):
            raise RuntimeError(f"Task {task_id} {status}: {output.get('message', output)}")
    raise TimeoutError(f"Task {task_id} did not finish within {timeout}s")


def download(url, path):
    with urllib.request.urlopen(url, timeout=120) as resp, open(path, "wb") as f:
        f.write(resp.read())


def main():
    p = argparse.ArgumentParser(description="Generate images with Qwen-Image (DashScope).")
    p.add_argument("prompt")
    p.add_argument("-o", "--out-dir", default="images")
    p.add_argument("-m", "--model", default="qwen-image", help="e.g. qwen-image, qwen-image-plus")
    p.add_argument("-s", "--size", default="1328*1328", choices=SIZES)
    p.add_argument("-n", type=int, default=1, help="number of images")
    p.add_argument("--negative", help="negative prompt")
    p.add_argument("--no-extend", action="store_true", help="disable automatic prompt rewriting")
    p.add_argument("--watermark", action="store_true")
    args = p.parse_args()

    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        sys.exit("Set DASHSCOPE_API_KEY (get one at https://modelstudio.console.alibabacloud.com/)")

    urls = generate(args.prompt, api_key, model=args.model, size=args.size, n=args.n,
                    negative_prompt=args.negative, prompt_extend=not args.no_extend,
                    watermark=args.watermark)
    os.makedirs(args.out_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for i, url in enumerate(urls):
        path = os.path.join(args.out_dir, f"qwen-{stamp}-{i}.png")
        download(url, path)  # result URLs expire after ~24h, so save locally
        print(path)


if __name__ == "__main__":
    main()
