---
title: "Momo's One Kind Word"
genre: "kids bedtime song"
length_seconds: 85
format: "9:16"
route: "local-16gb"
voice: "voiceover"
song_model: "ACE-Step 1.5"
status: "Worked example. Original episode: https://youtu.be/V-PmF7g5i2o (Ember Hills)"
---

# Momo's One Kind Word

A worked example. The original Ember Hills episode was made with H3 clips through an API,
where Momo sings on screen in shots 1, 3, 4 and 5. This copy rebuilds the stills and clips
with this package on a 16 GB card (Flux.2 Klein 9B stills, Wan 2.2 clips), so every mouth
stays closed and the song plays as a voiceover. On the 24 GB or fal route, use the
`*-sing` clip workflows for shots 1, 3, 4 and 5 instead.

## Story

It is late in a warm wooden library aisle and Momo is still up, standing under one small
lamp. A knitted blanket lies folded on a shelf, so she wraps it round her own shoulders. A
cushion sits alone on the floor and she hugs it. A wide rocking chair waits in the lamp glow,
and she climbs in and rocks herself slowly. She tucks a thick quilt round her own feet and
reads for a while. She pulls one book on the shelf, a trap door opens in the floor and her
bed rises up to meet her. One warm word stays in her head, and she falls asleep.

## Characters and references

| Name | Reference image | Things you can count |
|---|---|---|
| Momo | momo-reference.png | one purple felt bulldog; two short folded ears with pink insides; cream muzzle with a black nose; closed mouth, no teeth; green floral kimono, mustard sash with a rose cord, navy floral short jacket, green shorts; two arms, two short legs |

Prompt sentence for Momo, used word for word: "the purple felt bulldog from image 1, in her
green floral kimono with a mustard sash, a navy floral short jacket and green shorts, closed
mouth with no teeth".

## Lyric

1. Momo stays up late tonight.
2. One small lamp is shining bright.
3. One blanket lies on a shelf.
4. Momo wraps it round herself.
5. One small cushion sits alone.
6. Momo holds it as her own.
7. One wide chair waits in the glow.
8. Momo rocks herself so slow.
9. One thick quilt lies on a seat.
10. Momo tucks it round her feet.
11. Momo helps her friends all day.
12. Now she helps herself this way.
13. Momo takes her time to rest.
14. Slow and soft is what is best.
15. One warm word stays in her head.
16. 'You are kind.' Then off to bed.

## Song plan

- Song: `song.mp3`, the original episode's song (ACE-Step 1.5), 85 s, mastered.
- To make a new one: workflows/local/song-ace-step15.api.json with `prompts/song-style.txt`
  and `prompts/song-lyrics.txt`, 117 BPM, C major, 4 takes with fixed seeds; keep the take
  that `scripts/slots.py` hears completely.

## Shot plan

| # | Lines | Beat | Still | Movement | Sings |
|---|---|---|---|---|---|
| 1 | 1-2 | Still awake | Wide. Momo stands small in the middle of the wooden aisle, full body, facing the camera, eyes open. One small lamp on a low table at the left throws warm light across her; tall shelves of plain books stay dim on both sides. | The camera pushes in slowly toward Momo. | no |
| 2 | 3-4 | Blanket | Medium. Momo at a shelf on the right, three-quarters to camera, one knitted blanket half over her shoulder, the rest still on the shelf. | Her arms draw the blanket round her shoulders. | no |
| 3 | 5-6 | Cushion | Medium, low angle. Momo kneels on the floorboards with the blanket round her shoulders, hugging one small coral cushion against her chest, eyes soft. | The camera pushes in slowly; she stays still and blinks. | no |
| 4 | 7-8 | Rocking chair | Medium wide. Momo sits back in one wide wooden rocking chair, blanket round her shoulders, cushion held to her chest, feet off the floor. | The chair rocks slowly back and forward. | no |
| 5 | 9-10 | Quilt | Closer, slightly high angle. Momo in the chair, one thick turquoise quilt folded on her lap with its edge over her toes. | Her paws pat the quilt down over her feet. | no |
| 6 | 11-12 | Reading | Wide from the aisle. Momo in the rocking chair under the quilt, reading one open book; the shelf fills the top of the frame, lamp low at the left. | She reads, then looks up at the camera with a small closed smile. | no |
| 7 | 13-14 | The secret book | Medium wide, full body. Momo stands in the aisle holding the book she pulled from the shelf; in front of her a wooden box bed with a turquoise mattress and a coral cushion has risen out of a trap door and sits level with the floor. | The camera pushes in slowly; she stays still and blinks. | no |
| 8 | 15-16 | Asleep | Medium, high angle. Momo asleep in the wooden box bed, eyes closed, head on the coral cushion, quilt over her feet, blanket round her shoulders; the lamp on the floor beside the bed. | The camera pushes in slowly; her eyes stay closed. | no |

## Never in any shot

Teeth, an open mouth, speaking, extra limbs, a second tail, a second Momo or a mirror, any
other character, human hands, text or lettering, readable book titles, logos, cropping.

## Decisions

- Story, lyric and shot plan: from the original episode.
- Stills, clips and cut: rebuilt with this package; see README.md in this folder.
- Shots 3 and 7 changed during the rebuild. In shot 3, Wan 2.2 opened Momo's mouth and
  showed teeth whenever she lifted the cushion (2 of 2 takes, even with the closed-mouth
  negative prompt). In shot 7, the rising bed flipped over in 2 of 2 takes. Following the
  rule "the still owns the story beat", both stills now show the finished action and only
  the camera moves.
