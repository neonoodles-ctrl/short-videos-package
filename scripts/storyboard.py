#!/usr/bin/env python3
"""Build an Obsidian storyboard canvas from an episode.md shot table.

Each shot becomes a card with its lines, beat, still description and movement, plus the
still and the clip once they exist (stills/shot-01.png, clips/shot-01.mp4 ...). Run it again
after every render to refresh the board. Obsidian is optional; the canvas is plain JSON.

Example (run from the folder you opened as your Obsidian vault)
  python scripts/storyboard.py examples/momos-one-kind-word/episode.md \
      --stills examples/momos-one-kind-word/stills --clips output/momo/clips \
      --out examples/momos-one-kind-word/storyboard.canvas
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

CARD_W, TEXT_H, GAP = 520, 420, 60


def parse(path: Path):
    text = path.read_text(encoding="utf-8")
    title = re.search(r'^title:\s*"?(.*?)"?\s*$', text, re.M)
    lyric = re.search(r"^## Lyric.*?$(.*?)(?=^## )", text, re.S | re.M)
    lines = {}
    if lyric:
        for row in lyric.group(1).splitlines():
            m = re.match(r"\s*(\d+)[.)]\s+(.*)", row)
            if m:
                lines[int(m.group(1))] = m.group(2).strip()
    shots, header = [], None
    for row in text.splitlines():
        if not row.strip().startswith("|"):
            header = None if not row.strip() else header
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if header is None:
            low = [c.lower() for c in cells]
            if ("#" in low or "shot" in low) and any("still" in c or "composition" in c for c in low):
                header = low
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        shots.append({h: cells[i] if i < len(cells) else "" for i, h in enumerate(header)})
    return (title.group(1) if title else path.parent.name), lines, shots


def col(shot: dict, *names: str) -> str:
    for key, value in shot.items():
        if any(n in key for n in names):
            return value
    return ""


def media(folder: Path | None, number: int, exts: tuple[str, ...]) -> Path | None:
    if not folder or not folder.is_dir():
        return None
    pat = re.compile(rf"^shot-0*{number}\.({'|'.join(exts)})$", re.I)
    hits = sorted(p for p in folder.iterdir() if pat.match(p.name))
    return hits[0] if hits else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode", type=Path)
    ap.add_argument("--stills", type=Path, help="folder with shot-01.png ...")
    ap.add_argument("--clips", type=Path, help="folder with shot-01.mp4 ...")
    ap.add_argument("--vault", type=Path, default=Path("."), help="your Obsidian vault folder (default: here)")
    ap.add_argument("--columns", type=int, default=4)
    ap.add_argument("--still-height", type=int, default=0, help="card picture height (default: from the first still)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    title, lines, shots = parse(a.episode)
    if not shots:
        raise SystemExit(f"{a.episode}: no shot table with '#' and 'Still' columns (see templates/episode.md)")
    vault = a.vault.resolve()

    def rel(p: Path) -> str:
        return os.path.relpath(p.resolve(), vault).replace(os.sep, "/")

    pic_h = a.still_height or 300
    first = media(a.stills, 1, ("png", "jpg", "jpeg", "webp"))
    if first and not a.still_height:
        try:
            import struct
            with open(first, "rb") as f:
                head = f.read(24)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                w, h = struct.unpack(">II", head[16:24])
                pic_h = round(CARD_W * h / w)
        except OSError:
            pass

    nodes, edges = [], []
    nodes.append({"id": "title", "type": "text", "x": 0, "y": -220, "width": CARD_W * 2, "height": 160,
                  "text": f"# {title}\n\nStoryboard from `{a.episode.name}`. Re-run scripts/storyboard.py after each render."})
    cell_h = TEXT_H + pic_h * 2 + GAP * 3
    for k, shot in enumerate(shots):
        num_txt = col(shot, "#", "shot") or str(k + 1)
        number = int(re.sub(r"\D", "", num_txt) or k + 1)
        x = (k % a.columns) * (CARD_W + GAP * 2)
        y = (k // a.columns) * (cell_h + GAP)
        rng = col(shot, "lines")
        nums = [int(n) for n in re.findall(r"\d+", rng)]
        sung = [f"{n}. {lines[n]}" for n in range(nums[0], nums[-1] + 1) if n in lines] if nums else []
        body = [f"## Shot {number}: {col(shot, 'beat')}", ""]
        if sung:
            body += ["> " + "\n> ".join(sung), ""]
        body += [f"**Still:** {col(shot, 'still', 'composition')}", "", f"**Movement:** {col(shot, 'motion', 'movement')}"]
        if col(shot, "sings"):
            body += ["", f"**Sings on screen:** {col(shot, 'sings')}"]
        gid = f"shot-{number:02d}"
        nodes.append({"id": gid, "type": "group", "label": f"Shot {number}", "x": x - GAP // 2, "y": y - GAP // 2,
                      "width": CARD_W + GAP, "height": cell_h})
        nodes.append({"id": f"{gid}-text", "type": "text", "x": x, "y": y, "width": CARD_W, "height": TEXT_H,
                      "text": "\n".join(body)})
        still = media(a.stills, number, ("png", "jpg", "jpeg", "webp"))
        clip = media(a.clips, number, ("mp4", "webm", "mov"))
        for j, (item, label) in enumerate(((still, "still"), (clip, "clip"))):
            ny = y + TEXT_H + GAP + j * (pic_h + GAP)
            if item:
                nodes.append({"id": f"{gid}-{label}", "type": "file", "file": rel(item),
                              "x": x, "y": ny, "width": CARD_W, "height": pic_h})
            else:
                nodes.append({"id": f"{gid}-{label}", "type": "text", "x": x, "y": ny, "width": CARD_W, "height": pic_h,
                              "text": f"*No {label} yet* (shot-{number:02d})", "color": "4"})
        if k:
            edges.append({"id": f"e-{k}", "fromNode": f"shot-{prev:02d}", "fromSide": "right",
                          "toNode": gid, "toSide": "left"})
        prev = number
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"nodes": nodes, "edges": edges}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{a.out}: {len(shots)} shots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
