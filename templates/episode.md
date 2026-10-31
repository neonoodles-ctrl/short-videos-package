---
title: "Working title"
genre: "kids song / music video / comedy / horror / explainer / ..."
length_seconds: 120          # 90 to 180
format: "16:9"               # 16:9 (1920x1080) or 9:16 (1080x1920)
route: "local-16gb"          # local-16gb, local-24gb or fal (see docs/MODELS.md)
voice: "voiceover"           # voiceover (works everywhere) or on-screen singing (local-24gb or fal)
song_model: "ACE-Step 1.5"   # ACE-Step 1.5 or MiniMax Music 3
status: "Gate 1 not approved"
---

# Working title

<!-- Copy this file to episodes/<slug>/episode.md and fill every section before any picture
is made. The scripts read the '## Lyric' list and the shot table, so keep their shape. -->

## Story

Three to six sentences. Who is in it, where it happens, what changes from the first shot to
the last one. Every story beat must be something a single still picture can show.

## Characters and references

| Name | Reference image | Things you can count |
|---|---|---|
| Momo | characters/momo.png | two short folded ears, one green kimono, one mustard sash, no teeth |

Describe each character with counts and colours, not adjectives ("exactly two ear tufts",
"three freckles on each cheek"). Fill one templates/character.md per character.

## Lyric

<!-- One sung line per numbered line. Rhyming couplets work best: one couplet per shot.
For a song model, copy these lines into a lyric file with bare section tags such as
[Verse 1] and [Chorus]. Never put directions inside the tags: models sing them. -->

1. First line of the song.
2. Second line, which rhymes with the first.
3. ...
4. ...

## Song plan

- Model and workflow: workflows/local/song-ace-step15.api.json (or song-minimax-music3, or the fal versions)
- Style text: genre, tempo (BPM), key, mood, voice, instruments, how it builds and ends
- Length: about N seconds. Make 3 to 4 full takes with fixed seeds and keep one whole take.
  Never splice two takes. The video is as long as the song.

## Shot plan

<!-- One row per shot. The still holds the whole story beat: every prop, place and person
the clip needs must already be in the still. The clip may move ONE thing that is already
visible, or the camera. Sings = yes only on the 24 GB or fal route. -->

| # | Lines | Beat | Still | Movement | Sings |
|---|---|---|---|---|---|
| 1 | 1-2 | Opening | Wide. Describe the whole picture: place, light, where each character stands, what they hold. | The camera pushes in slowly. | no |
| 2 | 3-4 | ... | ... | ... | no |

## Never in any shot

Write the list of things that must never appear (for example: teeth, extra limbs, text or
lettering, extra characters, cropping). Check every still and every clip against it.

## Decisions

Record each approval here with the date: story and lyric (Gate 1), stills (Gate 2), song
(Gate 3), clips (Gate 4), final cut (Gate 5).
