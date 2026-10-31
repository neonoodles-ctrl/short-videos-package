# Worked example: Momo's One Kind Word

An 85-second kids' bedtime song from the Ember Hills channel
([original episode](https://youtu.be/V-PmF7g5i2o)), rebuilt with this package on the
`local-16gb` route: Flux.2 Klein 9B stills and Wan 2.2 clips on one 16 GB RTX 4080, with the
original song as a voiceover.

| File | What it is |
|---|---|
| `episode.md` | story, 16-line lyric, shot plan, never-list (the scripts read it) |
| `momo-reference.png` | the character reference used for every still (metadata removed) |
| `song.mp3` | the original episode's song, mastered, 85 s |
| `slots.json` | `scripts/slots.py` on `song.mp3`: every line timed, 8 shot slots |
| `prompts/` | `shot-NN.txt` still prompts, `shot-NN-move.txt` movements, song style and lyric |
| `stills/` | the 8 stills used for the clips |
| `storyboard.canvas` | `scripts/storyboard.py` output; open it in Obsidian with this repository as the vault |

## How it was made

Commands as run (model file names on your machine may differ; `--check` tells you):

```bash
# 1. Time the song and make the shot slots (Whisper heard 92 of 97 words, no line missing)
python scripts/slots.py examples/momos-one-kind-word/song.mp3 \
    --episode examples/momos-one-kind-word/episode.md --out examples/momos-one-kind-word/slots.json

# 2. Stills: 2 seeds per shot, the better one kept (6-15 s each on the RTX 4080)
python scripts/run_workflow.py workflows/local/still-klein9b.api.json \
    --image REFERENCE=examples/momos-one-kind-word/momo-reference.png \
    --text PROMPT=examples/momos-one-kind-word/prompts/shot-01.txt \
    --size 832x1472 --seed 3300111 --out output/momo/stills --name shot-01

# 3. Clips: Wan 2.2 makes 5 s; long slots are chains, each clip starting from the last frame
#    of the one before (70-80 s per clip). NEGATIVE gets the closed-mouth words (AGENTS.md).
python scripts/run_workflow.py workflows/local/clip-wan22-i2v.api.json \
    --image START_FRAME=examples/momos-one-kind-word/stills/shot-01.png \
    --set PROMPT.text="$(cat examples/momos-one-kind-word/prompts/shot-01-move.txt)" \
    --size 480x848 --seconds 5 --seed 330010 --out output/momo/clips --name shot-01
python scripts/cut.py lastframe output/momo/clips/shot-01.mp4 --out output/momo/frames/shot-01-end.png
# ... shot-01b.mp4 from shot-01-end.png, and so on

# 4. Cut, master and subtitles
python scripts/cut.py assemble --slots examples/momos-one-kind-word/slots.json \
    --clips output/momo/clips --song examples/momos-one-kind-word/song.mp3 \
    --size 1080x1920 --out output/momo/final/momos-one-kind-word-master.mp4
python scripts/captions.py examples/momos-one-kind-word/slots.json --notes \
    --out output/momo/final/momos-one-kind-word-master.srt
```

## What went wrong, and what fixed it

- **Teeth on a closed-mouth character.** Wan 2.2 opened Momo's mouth and showed teeth when
  she lifted a cushion (shot 3) and when she looked up from her book (shot 6), although the
  prompt said her mouth stays closed. Adding `open mouth, teeth, tongue, talking, singing,
  grin` to NEGATIVE fixed shot 6. Shot 3 still opened its mouth in a second take, so its
  still now shows the cushion already hugged and only the camera moves.
- **A rising bed that flips.** The bed in shot 7 tipped over while rising in 2 of 2 takes.
  The still now shows the bed already level with the floor; only the camera moves.
- **Chained push-ins keep pushing.** Four chained "camera pushes in" clips in shot 1 end on
  a very close face. Write "the camera holds still" for the later clips of a chain.

All of this is the method in `AGENTS.md`: check every clip at 3 frames per second, and when a
defect repeats in two takes, change the still or the action instead of re-rolling.
