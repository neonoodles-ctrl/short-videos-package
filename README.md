# short-videos-package

Make 90-second to 3-minute AI videos of any genre with ComfyUI: a character reference,
one still per shot, a full song, an animated clip per shot, and a finished cut with
subtitles. Locally on your own graphics card, or through fal.ai with your own key.

It is the method behind the [Ember Hills](https://www.youtube.com/@ember-hills) kids' song
channel, written down so any agent can follow it, for kids' songs or anything else: music
videos, comedy, horror, explainers.

## Start here

1. Open this folder in your coding agent (Claude Code, Codex, Cursor, opencode, Aider ...).
2. Paste the prompt from [`SETUP-PROMPT.md`](SETUP-PROMPT.md).
3. The agent checks your computer, asks whether you want local, API or both, installs
   ComfyUI and the right models (outside this folder), asks whether you want Obsidian for the
   storyboard and how you want to review work (for example
   [Agent Previewer](https://github.com/neonoodles-ctrl/agent-previewer)), and runs one test
   of each workflow.
4. Then ask it to make a video. It follows [`AGENTS.md`](AGENTS.md).

ComfyUI, the models and Obsidian are not in this repository: it holds links, instructions,
workflows and five small scripts.

## What you need

| Route | Your computer | Stills | Clips | Song | Singing on screen |
|---|---|---|---|---|---|
| local-16gb | GPU with up to 16 GB | Flux.2 Klein 9B | Wan 2.2 I2V A14B | ACE-Step 1.5 | no: the song is a voiceover |
| local-24gb | GPU with 24 GB or more | Flux.2 Klein 9B | MiniMax H3 | ACE-Step 1.5 or MiniMax Music 3 | yes |
| fal | any computer, fal.ai key | Klein 9B | H3 Max | MiniMax Music 3 or ACE-Step | yes |

Plus Python 3.10 or newer, ffmpeg, and disk space for the models (about 76 GB for
local-16gb). Downloads, sizes, prices and licences: [`docs/MODELS.md`](docs/MODELS.md).

## How a video gets made

```
idea -> episode.md (story, lyric, shot plan)        a person approves
     -> character reference + one still per shot    a person approves
     -> 3-4 song takes, slots.py hears each one     a person picks one take, used whole
     -> slots.json: when each shot starts and ends
     -> one clip (or a chain) per shot              a person approves
     -> cut.py: clips on the song's timeline, -14 LUFS master, captions.py subtitles
```

The rules that make it work are in `AGENTS.md`. The three that matter most:

- **The still owns the story.** Everything a shot needs is already in its still; the clip
  only moves one thing, or the camera.
- **Describe characters in counts** (two ears, three freckles, one scarf), not adjectives.
- **The song is used whole and sets the length.** Never splice takes or cut the song to fit.

## Folders

```
SETUP-PROMPT.md       paste into your agent to set everything up
AGENTS.md             how an agent makes a video, step by step, with the gates
docs/MODELS.md        routes, model downloads, prices, licences
workflows/local/      ComfyUI workflows for your own GPU (editor .json + API .api.json)
workflows/fal/        the same jobs through fal.ai
scripts/              run_workflow.py, slots.py, cut.py, captions.py, storyboard.py
templates/            episode.md and character.md to copy for a new video
examples/             a complete worked example: Momo's One Kind Word
```

## The scripts

| Script | Does |
|---|---|
| `run_workflow.py` | sends a workflow to ComfyUI with your images, prompt, size, seed and length; downloads the result; `--check` lists missing nodes and models |
| `slots.py` | hears a finished song with Whisper, times every lyric line, flags skipped lines, and writes when each shot starts and ends |
| `cut.py` | cuts song slices for singing shots, saves a clip's last frame for chaining, and assembles the final video (scale and pad, never crop; crossfades; -14 LUFS) |
| `captions.py` | writes the lyric as an `.srt` subtitle file |
| `storyboard.py` | builds an Obsidian canvas: one card per shot with its lines, still and clip |

## Worked example

[`examples/momos-one-kind-word/`](examples/momos-one-kind-word/): an Ember Hills episode
([original video](https://youtu.be/V-PmF7g5i2o)) rebuilt with this package on a 16 GB card:
its episode file, reference image, song, prompts, the 8 stills and the shot timings.

## Licence

MIT for everything in this repository. Each model has its own licence; see
`docs/MODELS.md` before you publish or sell videos.
