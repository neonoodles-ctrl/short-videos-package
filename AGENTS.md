# AGENTS.md: making a video with short-videos-package

This file is for AI coding agents. It explains how to turn an idea into a finished 90-second
to 3-minute video with the workflows and scripts in this repository. If the machine is not
set up yet, follow `SETUP-PROMPT.md` first. If `AGENTS.local.md` exists, read it too: it holds
this user's route, ComfyUI address and review tool.

## The five gates

A person approves each gate. Describing an image or a video is not approving it: show the
files in the user's review tool (Agent Previewer, their own choice, or the `output/` folder)
and wait for their answer.

| Gate | What you hand over | What the person decides |
|---|---|---|
| 1. Story | `episodes/<slug>/episode.md` from `templates/episode.md`: story, lyric, shot plan, never-list | The words and the plan, before any picture exists |
| 2. Stills | One approved still per shot, plus character references | Every character, prop and composition |
| 3. Song | 3 or 4 full takes; your pick with `scripts/slots.py` results | The take that is used whole |
| 4. Clips | One clip (or a chain of clips) per shot | Movement, faces, hands, anything invented |
| 5. Cut | The mastered video and its `.srt` subtitles | Release |

Record each decision with its date in the episode's `## Decisions` section. Never overwrite
an approved file: a retry is a new version (`shot-03-v002.png`). Make approved files read-only.

## Folder layout for a project

```
episodes/<slug>/episode.md        story, lyric, shot plan (the scripts read it)
episodes/<slug>/characters/       one approved reference image per character
episodes/<slug>/prompts/          shot-01.txt (still), shot-01-move.txt (movement), song files
episodes/<slug>/stills/           approved stills: shot-01.png, shot-02.png ...
episodes/<slug>/slots.json        from scripts/slots.py
output/<slug>/                    every render, take and cut (git-ignored)
```

## Step by step

1. **Story (gate 1).** Fill `templates/episode.md`. One rhyming couplet per shot works well;
   90 s needs about 8 shots, 3 minutes about 20. Every beat must be visible in a single
   still. Fill `templates/character.md` for each character, with things you can count.
2. **Character reference.** Make 4 candidates with `workflows/*/still-klein9b*` on a plain
   background. The person picks one. It is the REFERENCE image for every still.
3. **Stills (gate 2).** One `prompts/shot-NN.txt` per shot, then
   `scripts/run_workflow.py workflows/local/still-klein9b.api.json --image REFERENCE=... --text PROMPT=... --size 1472x832 --seed N`.
   Make 2 seeds per shot and look at every one at full size. Fix a single defect with
   `edit-klein9b` (image 1 = the still, image 2 = the reference) instead of re-rolling.
4. **Song (gate 3).** Write the lyric with bare section tags (`[Verse 1]`, `[Chorus]`) and
   the style text (genre, BPM, key, voice, instruments, how it ends). Render 3 or 4 takes with
   fixed seeds. Run `scripts/slots.py <take> --episode episodes/<slug>/episode.md` on each;
   reject takes with `missing_lines`, then listen. Keep one take whole; never splice takes.
5. **Slots.** `slots.json` from the chosen take gives each shot a start and an end. The
   video is exactly as long as the song; never cut the song to fit the pictures.
6. **Clips (gate 4).** One clip per shot from its approved still. Clip models make about
   5 seconds; for a longer slot, chain clips: `scripts/cut.py lastframe` saves the end of one
   clip as the start of the next (`shot-03.mp4`, `shot-03b.mp4` ...).
   - `local-16gb`: `clip-wan22-i2v`. Mouths closed; the song is a voiceover.
   - `local-24gb` or `fal`: `clip-h3` / `clip-h3-fal`. For a character singing on screen,
     cut that shot's piece of the song with `scripts/cut.py slice` and use the `*-sing`
     workflow with it as SONG_SLICE.
7. **Cut (gate 5).**
   `scripts/cut.py assemble --slots slots.json --clips <folder> --song <take> --size 1920x1080 --out output/<slug>/final/<slug>-master.mp4`
   then `scripts/captions.py slots.json --out ...srt`. Refresh the storyboard with
   `scripts/storyboard.py` if the user uses Obsidian.

## Rules for pictures and clips

- **The still owns the story beat.** Every prop, place and person a clip needs must already
  be in the still. The clip moves ONE thing that is already visible, or the camera.
- **Describe in counts.** "Exactly two ears, three freckles on each cheek, one red scarf",
  not "cute". Every drift you fight is a count you did not write down.
- **Name the place in every prompt.** Close-ups without a named place copy the reference
  image's background.
- **Never name things that should be absent** in a shared style sentence ("no hat" puts a
  hat in). List them in the never-list and check for them instead.
- **Use plain colour words.** A colour named after a thing gets drawn as that thing:
  "sunflower-yellow cushion" became a sunflower. Write "plain bright yellow".
- **Never crop to change shape.** Scale and pad. Make stills in the shape of the final video
  (1472x832 or 832x1472 local; 1664x960 or 960x1664 for fal H3, whose 480P output is 832x480).
- **Keep tags in lyrics bare.** Text inside `[ ]` gets sung.
- **Closed mouths need the negative prompt.** "Her mouth stays closed" in the prompt is not
  enough for Wan 2.2: it opens mouths and shows teeth when a character lifts or hugs
  something. For every shot where nobody sings, add `open mouth, teeth, tongue, talking,
  singing` to the end of NEGATIVE. If the mouth still opens in 2 takes, put the finished
  action in the still (the cushion already hugged) and move only the camera.
- **A still camera on H3 needs the tripod sentence**: "locked off on a tripod: no zoom, no
  push-in, no dolly". "The camera does not move" alone still zooms.
- **If a defect repeats in 2 takes, stop re-rolling.** Change the still, the framing or the
  action instead.

## Checking your own work before a person sees it

- Every still at full size: count fingers, limbs, ears, eyes and props; look for text,
  extra characters and anything on the never-list.
- Every clip: a contact sheet at 3 frames per second (`ffmpeg -i clip.mp4 -vf fps=3,scale=240:-1,tile=8x3 sheet.jpg`).
  Look for invented people, hands, objects and characters that change design. For singing
  shots, crop the mouth every 0.25 s and look for teeth.
- Every song: `slots.py` must hear every line without the lyric hint; then listen.
- The cut: its length must equal the song; play it from start to end.
- Say plainly what you could not check (you may not be able to hear or watch in real time).

## Paid API renders (fal)

Before any paid render, tell the user what it is for, its exact cost (from fal's price per
second or per megapixel), and wait for an OK. Render one take before any batch. If the same
defect appears in 2 takes, stop re-rolling and change the still, the framing or the action.

## Review tool

If the user chose Agent Previewer, submit each candidate, for example:
`previewer submit output/<slug>/final/<slug>-master.mp4 --project-run-id <slug> --title "<slug> cut v001" --kind video --expected-result "<what they should see>"`
Wait until the encode has finished before submitting, and only report items whose
verification status is ready.
