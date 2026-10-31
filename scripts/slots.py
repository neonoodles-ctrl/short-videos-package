#!/usr/bin/env python3
"""Time every lyric line in a finished song, then turn the lines into shot slots.

Whisper (faster-whisper) hears the song, the heard words are matched to the written
lyric, and each shot gets a start and end so every cut lands just before a line. It also
tells you which lines the singer skipped, so you can reject a bad take before making clips.

Needs: pip install faster-whisper   (see requirements.txt)

Examples
  # lyric and shot plan both read from the episode file (its "## Lyric" list and shot table)
  python scripts/slots.py output/song/song-take-03.flac --episode episodes/my-clip/episode.md \
      --out episodes/my-clip/slots.json

  # plain lyric file, two lines per shot
  python scripts/slots.py song.flac --lyrics lyrics.txt --lines-per-shot 2 --out slots.json

Lyric files: one sung line per line. Blank lines and [Section] tags are ignored.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import wave
from pathlib import Path


def norm(word: str) -> str:
    return re.sub(r"[^a-z0-9']", "", word.lower().replace("’", "'")).strip("'")


def lyric_lines_from_text(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or (line.startswith("[") and line.endswith("]")):
            continue
        lines.append(re.sub(r"^\d+[.)]\s+", "", line))
    return lines


def read_episode(path: Path) -> tuple[list[str], list[tuple[int, int]]]:
    """Return (lyric lines, shot line ranges) from an episode.md made from templates/episode.md."""
    text = path.read_text(encoding="utf-8")
    lyric = re.search(r"^## Lyric.*?$(.*?)(?=^## )", text, re.S | re.M)
    if not lyric:
        raise SystemExit(f"{path}: no '## Lyric' section")
    lines = [re.sub(r"^\d+[.)]\s+", "", l.strip()) for l in lyric.group(1).splitlines() if re.match(r"\s*\d+[.)]\s+", l)]
    shots = []
    header = None
    for row in text.splitlines():
        if not row.strip().startswith("|"):
            header = None if not row.strip() else header
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if header is None:
            low = [c.lower() for c in cells]
            if "lines" in low and ("#" in low or "shot" in low):
                header = low
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        rng = cells[header.index("lines")]
        m = re.match(r"(\d+)\s*[-–]\s*(\d+)", rng) or re.match(r"(\d+)", rng)
        if m:
            a = int(m.group(1))
            shots.append((a, int(m.group(2)) if m.lastindex == 2 else a))
    if not shots:
        raise SystemExit(f"{path}: no shot table with a 'Lines' column")
    return lines, shots


def shots_from_spec(spec: str) -> list[tuple[int, int]]:
    out = []
    for part in spec.split(","):
        a, _, b = part.strip().partition("-")
        out.append((int(a), int(b or a)))
    return out


def audio_seconds(path: Path) -> float:
    try:
        with wave.open(str(path)) as w:
            return w.getnframes() / w.getframerate()
    except (wave.Error, EOFError):
        import subprocess
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                             capture_output=True, text=True, check=True).stdout
        return float(out.strip())


def transcribe(path: Path, prompt: str, model: str, device: str) -> tuple[list[dict], list[dict]]:
    """Two passes: with the lyric as a hint (better timing) and without it (an honest check,
    because a hint can make Whisper 'hear' lines that were never sung)."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise SystemExit("faster-whisper is not installed: pip install -r requirements.txt") from None
    import subprocess
    import numpy as np
    # decode with ffmpeg: some PyAV versions break faster-whisper's own decoder
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, dtype=np.float32)

    def run(dev: str) -> list[list[dict]]:
        wm = WhisperModel(model, device=dev, compute_type="int8" if dev == "cpu" else "default")
        passes = []
        for hint in (prompt[:800], None):
            segments, _ = wm.transcribe(audio, language="en", word_timestamps=True, initial_prompt=hint,
                                        condition_on_previous_text=False, vad_filter=False)
            words = []
            for seg in segments:
                for w in seg.words or []:
                    if norm(w.word):
                        words.append({"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)})
            passes.append(words)
        return passes

    try:
        passes = run(device)
    except (RuntimeError, OSError, ValueError) as err:
        # faster-whisper's GPU build needs CUDA 12 cuBLAS/cuDNN; machines with only CUDA 13 (or
        # none) fail during transcription, not at load. The CPU is slower but gives the same words.
        if device == "cpu":
            raise
        print(f"GPU transcription failed ({str(err).splitlines()[0]}); using the CPU instead.", file=sys.stderr)
        passes = run("cpu")
    return passes[0], passes[1]


def align(lines: list[str], words: list[dict]) -> list[dict]:
    lyric = [(i, norm(w)) for i, line in enumerate(lines) for w in line.split() if norm(w)]
    heard = [norm(w["word"]) for w in words]
    sm = difflib.SequenceMatcher(a=[w for _, w in lyric], b=heard, autojunk=False)
    hit = {}
    for block in sm.get_matching_blocks():
        for k in range(block.size):
            hit[block.a + k] = block.b + k
    out = []
    for i, line in enumerate(lines):
        idx = [j for j, (li, _) in enumerate(lyric) if li == i]
        times = [words[hit[j]] for j in idx if j in hit]
        out.append({"line": i + 1, "text": line, "words": len(idx), "heard": len(times),
                    "start": times[0]["start"] if times else None, "end": times[-1]["end"] if times else None})
    # fill unheard lines between their neighbours so the shot plan still works; they stay flagged
    for i, row in enumerate(out):
        if row["start"] is None:
            prev = next((r["end"] for r in reversed(out[:i]) if r["end"] is not None), 0.0)
            nxt = next((r["start"] for r in out[i + 1:] if r["start"] is not None), prev + 2.0)
            row["start"], row["end"], row["guessed"] = prev, nxt, True
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("song", type=Path)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--episode", type=Path, help="episode.md with a '## Lyric' list and a shot table")
    src.add_argument("--lyrics", type=Path, help="plain lyric file")
    ap.add_argument("--shots", help="line ranges per shot, e.g. 1-2,3-4,5-6 (default: from --episode)")
    ap.add_argument("--lines-per-shot", type=int, default=2)
    ap.add_argument("--lead", type=float, default=0.25, help="cut this many seconds before a shot's first word")
    ap.add_argument("--model", default="medium.en", help="Whisper model (default %(default)s)")
    ap.add_argument("--device", default="auto", help="cpu, cuda or auto (auto falls back to the CPU if the GPU fails)")
    ap.add_argument("--out", type=Path, default=Path("slots.json"))
    args = ap.parse_args()

    if args.episode:
        lines, shots = read_episode(args.episode)
    else:
        lines, shots = lyric_lines_from_text(args.lyrics.read_text(encoding="utf-8")), []
    if args.shots:
        shots = shots_from_spec(args.shots)
    if not shots:
        n = args.lines_per_shot
        shots = [(a, min(a + n - 1, len(lines))) for a in range(1, len(lines) + 1, n)]

    duration = audio_seconds(args.song)
    words, plain = transcribe(args.song, " ".join(lines), args.model, args.device)
    timed = align(lines, words)
    check = align(lines, plain)
    for row, c in zip(timed, check):
        row["heard_without_hint"] = c["heard"]

    slots = []
    for k, (a, b) in enumerate(shots):
        start = 0.0 if k == 0 else max(0.0, timed[a - 1]["start"] - args.lead)
        slots.append({"shot": k + 1, "lines": [a, b], "start": round(start, 3)})
    for k, s in enumerate(slots):
        s["end"] = slots[k + 1]["start"] if k + 1 < len(slots) else round(duration, 3)
        s["duration"] = round(s["end"] - s["start"], 3)

    missing = [r["line"] for r in timed if r["heard_without_hint"] < max(1, round(r["words"] * 0.6))]
    heard = sum(r["heard"] for r in timed)
    plain_heard = sum(r["heard_without_hint"] for r in timed)
    total = sum(r["words"] for r in timed)
    result = {"song": str(args.song), "song_seconds": round(duration, 3), "words_heard": f"{heard}/{total}",
              "words_heard_without_hint": f"{plain_heard}/{total}", "missing_lines": missing,
              "lines": timed, "shots": slots}
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{args.out}: {len(slots)} shots, song {duration:.1f} s, words heard {heard}/{total} "
          f"({plain_heard}/{total} without the lyric as a hint)")
    for s in slots:
        print(f"  shot {s['shot']:>2}  lines {s['lines'][0]}-{s['lines'][1]}  {s['start']:7.2f} -> {s['end']:7.2f}  ({s['duration']:.2f} s)")
    if missing:
        print(f"WARNING: lines sung badly or skipped: {missing}. Listen, and consider another take.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
