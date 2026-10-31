# Workflows

Every workflow comes in two files with the same name:

- `name.json`: open it in ComfyUI (drag it onto the canvas, or Workflow > Open). Each loader
  carries its model's download link, so ComfyUI offers to fetch missing models, and a note
  at the top explains the inputs.
- `name.api.json`: the same graph in ComfyUI's API format, for `scripts/run_workflow.py`.

Nodes with CAPITAL titles are the inputs you change: `PROMPT`, `REFERENCE`, `IMAGE`,
`START_FRAME`, `SONG_SLICE`, `SONG`, `SEED`, `WIDTH`, `HEIGHT`, `SECONDS`, `VIDEO_SIZE`.
The local workflows use only nodes built into ComfyUI. The fal workflows need the
ComfyUI-fal-API custom nodes and a `FAL_KEY`.

## local

| Workflow | What it does | Main settings (from ComfyUI's official templates) | Tested |
|---|---|---|---|
| still-klein9b | Still from a text prompt and one reference image | Flux.2 Klein 9B fp8, 4 steps, euler, cfg 1, reference latent | RTX 4080 16 GB: 832x1472 in 6-15 s (27 s with model load) |
| edit-klein9b | Change one thing in a still; image 2 is the reference | Same as above; output keeps the size of image 1 | RTX 4080: 832x1472 in 30 s; only the asked-for change |
| clip-wan22-i2v | 5 s clip from a still, no sound | Wan 2.2 I2V A14B fp8 high/low + lightx2v 4-step LoRAs, 4 steps (2+2), cfg 1, euler/simple, shift 5, 16 fps | RTX 4080: 480x848, 81 frames in 70-82 s |
| clip-h3 | Clip from a still with H3's own sound | MiniMax H3 FL2VA int8 + turbo LoRA for the pruned model, 6 steps, res_multistep, 24 fps | RTX 3090 24 GB: 768x1344, 5 s in 4.5 min |
| clip-h3-sing | The same, guided by a slice of your song, so the mouth follows it | adds MiniMaxH3AddGuide with the song slice; the slice is kept as the sound | RTX 3090: 768x1344, 5 s in 4.6 min; mouth opens on the words, no teeth; soundtrack equals the slice |
| song-ace-step15 | Full song from style text and lyric | ACE-Step 1.5 XL SFT, 50 steps, cfg 7, euler/simple, shift 3 | RTX 4080: 90 s song in 81 s; Whisper heard 96 of 97 words |
| song-minimax-music3 | Full song from a three-part caption and lyric | MiniMax Music 3 fp16 + pruned int8 text encoder, 30 steps, cfg 1.7 | RTX 3090: 86 s song in 102 s; Whisper heard 92 of 97 words |

The H3 tests ran with a copy of the turbo LoRA saved under another file name. Its 416
tensors have the same names, shapes and offsets as the linked file's, and 60 of 60 random
64 KB pieces of the weights are identical.

Clip lengths: Wan 2.2 is made for 81 frames (5 s at 16 fps). H3 takes 24 fps frame counts
on a 17k+5 grid: 73 = 3 s, 124 = 5 s, 192 = 8 s, 243 = 10 s. `run_workflow.py --seconds`
converts for you. For a longer shot, chain clips with `scripts/cut.py lastframe`.

## fal

| Workflow | fal endpoint | Tested on 2026-10-31 |
|---|---|---|
| still-klein9b-fal | fal-ai/flux-2/klein/9b/edit | 960x1664 in 9 s, about USD 0.03 |
| edit-klein9b-fal | fal-ai/flux-2/klein/9b/edit (two images, through the Any Endpoint node) | 832x1472 in 12 s, about USD 0.04; only the cushion changed colour (3.4% of pixels changed) |
| clip-h3-fal | minimax/h3-max/image-to-video, 480P | 5.2 s clip, 480x832 with sound, in 21 s, about USD 0.17 |
| clip-h3-sing-fal | the same with your song slice as target audio | 5.2 s clip, 480x832, in 15 s, about USD 0.17; mouth opens on the words, no teeth; soundtrack equals the slice |
| song-minimax-music3-fal | minimax/music-3 | 90 s song in 3 min, about USD 0.18; Whisper heard 92 of 97 words |
| song-ace-step-fal | fal-ai/ace-step (ACE-Step v1) | 90 s song in 12 s, about USD 0.02; Whisper heard only 56 of 97 words, so check every take |

`prompt_expansion_mode` on the H3 node is `balanced` (fal's default: fal rewrites your
prompt a little). Set it to `disabled` to send your prompt word for word.
