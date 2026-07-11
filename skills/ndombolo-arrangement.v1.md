---
name: ndombolo-arrangement
version: 1
kind: genre
tags: [ndombolo, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 96-120; set the song key (suggested: G major).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - DANSE SEQUENCE is non-negotiable: the ndombolo drop: the song strips to kick + percussion + shouts while the seben guitar cycles — a named dance section, not a breakdown
  - INTERLOCKING GUITARS is non-negotiable: three guitars in distinct registers (lead, mi-solo mid, rhythm) weave complementary cyclic riffs — no one plays chords, the interlock is the harmony
  - ATALAKU ANIMATION is non-negotiable: an animateur's rhythmic shouts and crowd-cries punctuate the sebene, cueing the dancers and lifting the energy
---
# Ndombolo arrangement (graph-compiled)

## The pocket — ndombolo_danse
Ndombolo (~108 BPM): heavier kick than soukous (1, 2&, 3), cavacha-derived snare churn; seben guitars cycle bright interlocks; THE DANSE SEQUENCE — the song strips to kick + perc + atalaku shouts while one guitar cycles, then the band slams back. Swing 0.53 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **danse sequence** (w1.0): the ndombolo drop: the song strips to kick + percussion + shouts while the seben guitar cycles — a named dance section, not a breakdown *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **interlocking guitars** (w0.92): three guitars in distinct registers (lead, mi-solo mid, rhythm) weave complementary cyclic riffs — no one plays chords, the interlock is the harmony *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **atalaku animation** (w0.84): an animateur's rhythmic shouts and crowd-cries punctuate the sebene, cueing the dancers and lifting the energy *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **cavacha churn** (w0.76): the cavacha drum pattern: a continuous ghosted-16th snare/hi-hat churn with the backbeat on 2 & 4 and a near-every-beat kick — the rolling engine of Congolese dance music *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **ndombolo band**: seben guitars = pluck + pluck2 interlock (soukous inheritance, graph edge); kick_punch heavier than soukous; shouts = formant_vox stabs; the danse sequence = arrangement mute-to-percussion law

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
