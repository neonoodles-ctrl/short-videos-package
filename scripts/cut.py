#!/usr/bin/env python3
"""Cut the finished video: song slices for singing shots, last frames, and the final assembly.

Needs ffmpeg and ffprobe on PATH. No Python packages.

  slice     cut the song for one shot (feed it to a *-sing workflow)
  lastframe save a clip's last frame as a PNG (start the next clip of a long shot from it)
  assemble  put every shot's clips on the song's timeline, crossfade, master the sound

Examples
  python scripts/cut.py slice song.flac --slots slots.json --shot 5 --out output/slices/shot-05.wav
  python scripts/cut.py lastframe output/clips/shot-01.mp4 --out output/stills/shot-01-end.png
  python scripts/cut.py assemble --slots slots.json --clips output/clips --song song.flac \
      --size 1080x1920 --out output/final/my-clip-master.mp4

Clip names for assemble: shot-01.mp4, shot-01b.mp4, shot-02.mp4 ... Clips of one shot are
played in name order. The video is exactly as long as the song. A shot's clips are trimmed
to its slot; if they are too short the last frame is held. Clips are never slowed down or
sped up, and never cropped: anything that does not match the frame is scaled to fit and padded.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode:
        raise SystemExit(f"command failed: {' '.join(cmd[:8])} ...\n{proc.stderr[-3000:]}")
    return proc.stdout + proc.stderr


def seconds(path: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(out.strip().splitlines()[0])


def load_slots(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["shots"]


def cmd_slice(a) -> int:
    start, end = a.start, a.end
    if a.slots:
        shots = load_slots(a.slots)
        shot = next((s for s in shots if s["shot"] == a.shot), None)
        if shot is None:
            raise SystemExit(f"{a.slots} has no shot {a.shot}; its shots are {', '.join(str(s['shot']) for s in shots)}")
        start, end = shot["start"], shot["end"]
    if start is None or end is None:
        raise SystemExit("give --slots and --shot, or --start and --end")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(a.song),
         "-ac", "2", "-ar", "48000", str(a.out)])
    print(f"{a.out}: {end - start:.2f} s from {start:.2f} s")
    return 0


def cmd_lastframe(a) -> int:
    a.out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.5", "-i", str(a.clip), "-update", "1", "-q:v", "1", str(a.out)])
    print(a.out)
    return 0


def shot_clips(folder: Path, shot: int) -> list[Path]:
    pat = re.compile(rf"^shot-0*{shot}([a-z]?)\.(mp4|mov|webm|mkv)$", re.I)
    return sorted((p for p in folder.iterdir() if pat.match(p.name)), key=lambda p: p.name.lower())


def render_segment(clips: list[Path], length: float, w: int, h: int, fps: int, out: Path) -> None:
    fit = (f"scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,"
           f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={fps},format=yuv420p")
    inputs, chains = [], []
    for i, clip in enumerate(clips):
        inputs += ["-i", str(clip)]
        chains.append(f"[{i}:v]{fit}[v{i}]")
    joined = "".join(f"[v{i}]" for i in range(len(clips)))
    graph = ";".join(chains) + f";{joined}concat=n={len(clips)}:v=1:a=0[c];" \
            f"[c]tpad=stop_mode=clone:stop_duration={length:.3f},trim=duration={length:.3f},setpts=PTS-STARTPTS[out]"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph, "-map", "[out]", "-an",
         "-c:v", "libx264", "-crf", "14", "-preset", "medium", str(out)])


def loudness(song: Path, lufs: float, tp: float) -> str:
    out = run(["ffmpeg", "-hide_banner", "-i", str(song), "-af",
               f"loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json", "-f", "null", "-"])
    m = json.loads(out[out.rindex("{"):out.rindex("}") + 1])
    return (f"loudnorm=I={lufs}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")


def cmd_assemble(a) -> int:
    shots = load_slots(a.slots)
    w, h = (int(x) for x in a.size.lower().split("x"))
    work = a.out.with_suffix(".parts")
    work.mkdir(parents=True, exist_ok=True)
    segs = []
    for k, s in enumerate(shots):
        clips = shot_clips(a.clips, s["shot"])
        if not clips:
            raise SystemExit(f"no clip for shot {s['shot']} in {a.clips} (expected shot-{s['shot']:02d}.mp4)")
        extra = a.xfade if k + 1 < len(shots) else 0.0
        have = sum(seconds(c) for c in clips)
        if have + 0.05 < s["duration"] + extra:
            print(f"  shot {s['shot']}: clips give {have:.2f} s for a {s['duration'] + extra:.2f} s slot; "
                  f"holding the last frame {s['duration'] + extra - have:.2f} s")
        seg = work / f"seg-{s['shot']:02d}.mp4"
        render_segment(clips, s["duration"] + extra, w, h, a.fps, seg)
        segs.append(seg)

    silent = work / "picture.mp4"
    if a.xfade > 0 and len(segs) > 1:
        inputs = sum((["-i", str(p)] for p in segs), [])
        parts, prev = [], "[0:v]"
        for k in range(1, len(segs)):
            label = f"[x{k}]" if k + 1 < len(segs) else "[out]"
            parts.append(f"{prev}[{k}:v]xfade=transition=fade:duration={a.xfade}:offset={shots[k]['start']:.3f}{label}")
            prev = label
        run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(parts), "-map", "[out]",
             "-c:v", "libx264", "-crf", "14", "-preset", "medium", str(silent)])
    else:
        lst = work / "list.txt"
        lst.write_text("".join(f"file '{p.resolve()}'\n" for p in segs), encoding="utf-8")
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])

    a.out.parent.mkdir(parents=True, exist_ok=True)
    af = loudness(a.song, a.lufs, -1.0)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(a.song), "-map", "0:v", "-map", "1:a",
         "-af", af, "-ar", "48000", "-c:v", "libx264", "-crf", str(a.crf), "-preset", "slow",
         "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(a.out)])
    if not a.keep_parts:
        shutil.rmtree(work)
    print(f"{a.out}: {seconds(a.out):.2f} s (song {seconds(a.song):.2f} s), {w}x{h} {a.fps} fps, "
          f"sound mastered to {a.lufs} LUFS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("slice", help="cut the song for one shot")
    p.add_argument("song", type=Path)
    p.add_argument("--slots", type=Path)
    p.add_argument("--shot", type=int)
    p.add_argument("--start", type=float)
    p.add_argument("--end", type=float)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(fn=cmd_slice)

    p = sub.add_parser("lastframe", help="save a clip's last frame")
    p.add_argument("clip", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(fn=cmd_lastframe)

    p = sub.add_parser("assemble", help="build the finished video on the song's timeline")
    p.add_argument("--slots", type=Path, required=True)
    p.add_argument("--clips", type=Path, required=True, help="folder with shot-01.mp4, shot-02.mp4 ...")
    p.add_argument("--song", type=Path, required=True)
    p.add_argument("--size", default="1920x1080", help="delivery size, e.g. 1920x1080 or 1080x1920")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--xfade", type=float, default=0.4, help="crossfade seconds between shots (0 = hard cuts)")
    p.add_argument("--lufs", type=float, default=-14.0)
    p.add_argument("--crf", type=int, default=16)
    p.add_argument("--keep-parts", action="store_true")
    p.add_argument("--out", type=Path, required=True)
    p.set_defaults(fn=cmd_assemble)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
