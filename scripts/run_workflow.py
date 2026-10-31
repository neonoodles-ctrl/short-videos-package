#!/usr/bin/env python3
"""Send one workflow from workflows/ to a running ComfyUI, wait, and download the result.

Standard library only. Nodes are found by their title (the UPPER CASE names in each
workflow) or by node id.

Examples
  # check that this ComfyUI has every node and model the workflow needs (renders nothing)
  python scripts/run_workflow.py workflows/local/still-klein9b.api.json --check

  # one still from a character reference
  python scripts/run_workflow.py workflows/local/still-klein9b.api.json \
      --image REFERENCE=characters/momo.png --text PROMPT=prompts/shot-01.txt \
      --size 1472x832 --seed 101 --out output/stills --name shot-01

  # one clip from an approved still
  python scripts/run_workflow.py workflows/local/clip-wan22-i2v.api.json \
      --image START_FRAME=output/stills/shot-01.png --set PROMPT.text="The camera pushes in slowly." \
      --seconds 5 --seed 7 --out output/clips --name shot-01

Options that take TITLE.input=value accept JSON values (numbers, true/false, lists);
anything that is not valid JSON is sent as a string.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

SEED_INPUTS = ("seed", "noise_seed")


def http(method: str, url: str, data: bytes | None = None, headers: dict | None = None, timeout: float = 60):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", "replace")
        raise SystemExit(f"ComfyUI answered {err.code} for {url}:\n{body[:4000]}") from None
    except urllib.error.URLError as err:
        raise SystemExit(f"Cannot reach ComfyUI at {url}: {err.reason}. Is it running? Check --server.") from None


def get_json(server: str, path: str):
    return json.loads(http("GET", server + path))


def find_nodes(graph: dict, key: str) -> list[str]:
    if key in graph:
        return [key]
    hits = [nid for nid, n in graph.items() if n.get("_meta", {}).get("title") == key]
    if not hits:
        titles = sorted({n.get("_meta", {}).get("title", "") for n in graph.values()})
        raise SystemExit(f"No node titled {key!r}. Titles in this workflow: {', '.join(t for t in titles if t)}")
    return hits


def parse_value(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def split_assignment(item: str) -> tuple[str, str, str]:
    if "=" not in item or "." not in item.split("=", 1)[0]:
        raise SystemExit(f"Expected TITLE.input=value, got {item!r}")
    target, value = item.split("=", 1)
    title, inp = target.rsplit(".", 1)
    return title, inp, value


def set_input(graph: dict, title: str, inp: str, value) -> None:
    for nid in find_nodes(graph, title):
        graph[nid]["inputs"][inp] = value


def upload(server: str, path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"File not found: {path}")
    boundary = uuid.uuid4().hex
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{path.name}\"\r\n"
        f"Content-Type: {mime}\r\n\r\n".encode(), path.read_bytes(), b"\r\n",
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n".encode(),
        f"--{boundary}--\r\n".encode(),
    ])
    reply = json.loads(http("POST", server + "/upload/image", body,
                            {"Content-Type": f"multipart/form-data; boundary={boundary}"}, timeout=600))
    return f"{reply['subfolder']}/{reply['name']}" if reply.get("subfolder") else reply["name"]


def wan_frames(seconds: float) -> int:  # Wan 2.2: 16 fps, 4k+1 frames
    frames = max(5, round(seconds * 16))
    return frames + (1 - frames % 4) % 4


def h3_frames(seconds: float) -> int:  # MiniMax H3: 24 fps, 17k+5 frames
    frames = max(5, round(seconds * 24))
    return frames + (5 - frames % 17) % 17


def apply_seconds(graph: dict, seconds: float) -> None:
    for n in graph.values():
        cls, inp = n["class_type"], n["inputs"]
        if cls == "WanImageToVideo":
            inp["length"] = wan_frames(seconds)
        elif cls == "MiniMaxH3ImageToVideo":
            inp["length"] = h3_frames(seconds)
        elif cls.startswith("FalAPI_minimax-h3") and "duration" in inp:
            inp["duration"] = max(5, min(15, round(seconds)))
        elif cls in ("FalAPI_minimax-music-3", "FalAPI_fal-ai-ace-step") and "duration" in inp:
            inp["duration"] = float(seconds)
        elif cls == "MiniMaxMusic3TextEncode":
            inp["max_duration"] = float(seconds)
        if n.get("_meta", {}).get("title") == "SECONDS":
            inp["value"] = float(seconds)


def apply_size(graph: dict, width: int, height: int) -> None:
    for n in graph.values():
        inp, title = n["inputs"], n.get("_meta", {}).get("title")
        if title == "WIDTH":
            inp["value"] = width
        elif title == "HEIGHT":
            inp["value"] = height
        if not isinstance(inp.get("width"), list) and "width" in inp and "height" in inp \
                and not isinstance(inp.get("height"), list):
            inp["width"], inp["height"] = width, height
        if n["class_type"] == "FalAnyEndpoint_fal":
            args = json.loads(inp["arguments_json"])
            if "image_size" in args:
                args["image_size"] = {"width": width, "height": height}
                inp["arguments_json"] = json.dumps(args, ensure_ascii=False)


def apply_seed(graph: dict, seed: int) -> None:
    for n in graph.values():
        inp = n["inputs"]
        if n.get("_meta", {}).get("title") == "SEED" and "value" in inp:
            inp["value"] = seed
        for key in SEED_INPUTS:
            if key in inp and not isinstance(inp[key], list):
                inp[key] = seed


def check(server: str, graph: dict) -> int:
    info = get_json(server, "/object_info")
    problems = []
    for nid, n in graph.items():
        cls = n["class_type"]
        if cls not in info:
            problems.append(f"node {nid} ({n.get('_meta', {}).get('title', cls)}): ComfyUI has no node class {cls!r}."
                            " Install the custom node pack that provides it (see docs/MODELS.md).")
            continue
        spec = info[cls]["input"]
        for name, s in spec.get("required", {}).items():
            if name not in n["inputs"] and not any(k.startswith(name + ".") for k in n["inputs"]):
                problems.append(f"node {nid} ({cls}): required input {name!r} is missing")
        for name, value in n["inputs"].items():
            s = spec.get("required", {}).get(name) or spec.get("optional", {}).get(name)
            if not s or isinstance(value, list):
                continue
            options = s[0] if isinstance(s[0], list) else (s[1].get("options") if s[0] == "COMBO" and len(s) > 1 else None)
            if options and value not in options and cls not in ("LoadImage", "LoadAudio"):
                kind = "model file" if name.endswith(("_name", "name1", "name2")) else "value"
                same = [o for o in options if isinstance(o, str) and o.replace("\\", "/").rsplit("/", 1)[-1] == value]
                hint = f" It is installed as {same[0]!r}: add --set {nid}.{name}={same[0]}" if same else ""
                problems.append(f"node {nid} ({cls}): {kind} {value!r} for {name!r} is not installed or not allowed.{hint}")
    for p in problems:
        print("PROBLEM", p)
    print("OK: every node and model is present." if not problems else f"{len(problems)} problem(s).")
    return 1 if problems else 0


def wait(server: str, prompt_id: str, timeout_min: float) -> dict:
    deadline = time.time() + timeout_min * 60
    while time.time() < deadline:
        hist = get_json(server, f"/history/{prompt_id}")
        if prompt_id in hist:
            entry = hist[prompt_id]
            status = entry.get("status", {})
            if status.get("status_str") == "error":
                for msg in status.get("messages", []):
                    if msg[0] == "execution_error":
                        e = msg[1]
                        raise SystemExit(f"ComfyUI error in node {e.get('node_id')} ({e.get('node_type')}): "
                                         f"{e.get('exception_message', '').strip()}")
                raise SystemExit("ComfyUI reported an error; see the ComfyUI console.")
            if status.get("completed", True):
                return entry
        time.sleep(3)
    raise SystemExit(f"Timed out after {timeout_min} min. The job may still be running in ComfyUI ({prompt_id}).")


def download(server: str, entry: dict, out_dir: Path, name: str | None) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for node_out in entry.get("outputs", {}).values():
        for items in node_out.values():
            if not isinstance(items, list):
                continue
            for item in items:
                if not (isinstance(item, dict) and item.get("filename")) or item.get("type") == "temp":
                    continue
                query = urllib.parse.urlencode({k: item.get(k, "") for k in ("filename", "subfolder", "type")})
                data = http("GET", f"{server}/view?{query}", timeout=600)
                suffix = Path(item["filename"]).suffix
                target = out_dir / (f"{name}{'-' + str(len(saved)) if saved else ''}{suffix}" if name else item["filename"])
                target.write_bytes(data)
                saved.append(str(target))
    return saved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workflow", type=Path, help="an .api.json file from workflows/")
    ap.add_argument("--server", default="http://127.0.0.1:8188", help="ComfyUI address (default %(default)s)")
    ap.add_argument("--set", action="append", default=[], metavar="TITLE.input=value")
    ap.add_argument("--text", action="append", default=[], metavar="TITLE[.input]=file",
                    help="read a long text (prompt, lyrics) from a file; input defaults to text/prompt/lyrics")
    ap.add_argument("--image", action="append", default=[], metavar="TITLE=path", help="upload an image to a LoadImage node")
    ap.add_argument("--audio", action="append", default=[], metavar="TITLE=path", help="upload audio to a LoadAudio node")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--size", metavar="WxH", help="output size, e.g. 1472x832")
    ap.add_argument("--seconds", type=float, help="clip or song length; converted to frames per model")
    ap.add_argument("--out", type=Path, default=Path("output"), help="download folder (default %(default)s)")
    ap.add_argument("--name", help="file name for the result, without extension")
    ap.add_argument("--timeout", type=float, default=60, help="minutes to wait (default %(default)s)")
    ap.add_argument("--check", action="store_true", help="only check nodes and models against this ComfyUI")
    ap.add_argument("--dry-run", action="store_true", help="print the final graph instead of sending it")
    args = ap.parse_args()

    server = args.server.rstrip("/")
    graph = json.loads(args.workflow.read_text())
    if args.check:
        return check(server, graph)

    if args.seconds is not None:
        apply_seconds(graph, args.seconds)
    if args.size:
        w, h = (int(x) for x in args.size.lower().split("x"))
        apply_size(graph, w, h)
    if args.seed is not None:
        apply_seed(graph, args.seed)
    for item in args.text:
        target, path = item.split("=", 1)
        title, _, inp = target.partition(".")
        text = Path(path).read_text().strip()
        for nid in find_nodes(graph, title):
            inputs = graph[nid]["inputs"]
            keys = [inp] if inp else [k for k in ("text", "prompt", "tags", "caption") if k in inputs][:1]
            if not keys and "arguments_json" in inputs:  # fal Any Endpoint node: the prompt lives in its JSON
                fal_args = json.loads(inputs["arguments_json"])
                fal_args["prompt"] = text
                inputs["arguments_json"] = json.dumps(fal_args, ensure_ascii=False)
                continue
            if not keys:
                raise SystemExit(f"Say which input of {title} to fill, e.g. {title}.lyrics=file")
            graph[nid]["inputs"][keys[0]] = text
    for item in args.set:
        title, inp, value = split_assignment(item)
        set_input(graph, title, inp, parse_value(value))
    if args.dry_run:
        print(json.dumps(graph, indent=2, ensure_ascii=False))
        return 0
    for item, key in [(i, "image") for i in args.image] + [(a, "audio") for a in args.audio]:
        title, path = item.split("=", 1)
        set_input(graph, title, key, upload(server, Path(path)))

    started = time.time()
    reply = json.loads(http("POST", server + "/prompt",
                            json.dumps({"prompt": graph, "client_id": uuid.uuid4().hex}).encode(),
                            {"Content-Type": "application/json"}))
    if reply.get("node_errors"):
        raise SystemExit("ComfyUI rejected the workflow:\n" + json.dumps(reply["node_errors"], indent=2))
    prompt_id = reply["prompt_id"]
    print(f"queued {prompt_id}", file=sys.stderr)
    entry = wait(server, prompt_id, args.timeout)
    files = download(server, entry, args.out, args.name)
    print(json.dumps({"prompt_id": prompt_id, "files": files, "seconds": round(time.time() - started, 1)}, indent=2))
    return 0 if files else 1


if __name__ == "__main__":
    sys.exit(main())
