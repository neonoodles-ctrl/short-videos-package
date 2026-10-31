#!/usr/bin/env python3
"""Write the lyric as subtitles (.srt), timed from slots.json.

One subtitle per sung line, from its first word to its last word plus a short hold. Lines
that Whisper could not hear are still written but listed, so you can check them by ear.

Example
  python scripts/captions.py episodes/my-clip/slots.json --out output/final/my-clip.srt --notes
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def stamp(t: float) -> str:
    ms = max(0, round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slots", type=Path, help="slots.json from scripts/slots.py")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--hold", type=float, default=0.6, help="seconds a line stays up after its last word")
    ap.add_argument("--notes", action="store_true", help="wrap sung lines in ♪ ... ♪")
    ap.add_argument("--offset", type=float, default=0.0, help="shift every subtitle (e.g. if you add an intro)")
    a = ap.parse_args()

    lines = json.loads(a.slots.read_text(encoding="utf-8"))["lines"]
    cues, unsure = [], []
    for i, line in enumerate(lines):
        start = line["start"] + a.offset
        end = line["end"] + a.hold + a.offset
        if i + 1 < len(lines):
            end = min(end, lines[i + 1]["start"] + a.offset - 0.05)
        text = f"♪ {line['text']} ♪" if a.notes else line["text"]
        cues.append(f"{len(cues) + 1}\n{stamp(start)} --> {stamp(max(end, start + 0.5))}\n{text}\n")
        if line.get("guessed") or line.get("heard_without_hint", line["words"]) < line["words"]:
            unsure.append(line["line"])
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text("\n".join(cues), encoding="utf-8")
    print(f"{a.out}: {len(cues)} subtitles")
    if unsure:
        print(f"check these lines by ear (not every word was heard): {unsure}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
