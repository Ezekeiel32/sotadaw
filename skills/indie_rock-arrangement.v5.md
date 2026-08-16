---
name: indie_rock-arrangement
version: 5
kind: genre
tags: [indie_rock, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-145; set the song key (suggested: G major).
  - Mix: clipped_samples == 0, LUFS -13..-9, band order lowmid>mid>low.
  - JANGLE STRUM is non-negotiable: indie jangle: clean/lightly-chorused OPEN chords strummed 8ths, doubled L/R with different voicings; the midrange shimmer is the pad — no synths needed
  - SINGER SONGWRITER SCHEMA is non-negotiable: vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas]
  - VERSE POSITION LAW is non-negotiable: pop physiology from 912 human structures: verses live EARLY and die by the final third (1221/773/185); bridges never open a song (11/701 first third); the pop 'break' is early and SHORT (9s vs 21s chorus); outros 420/421 final-third — place sections where the population puts them [Harmonix label grammar, MIT data, mined locally]
---
# Indie_Rock arrangement (graph-compiled)

## The pocket — indie_loose
indie_rock loop DNA (wave16) Swing 0.51 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: OMT2 'Four-Chord Schemas' degrees -> archetype chord DNA via curated:claude/2026-07-05 (wave29b))*

## Techniques (weight order — the top ones DEFINE the genre)
- **jangle strum** (w0.9): indie jangle: clean/lightly-chorused OPEN chords strummed 8ths, doubled L/R with different voicings; the midrange shimmer is the pad — no synths needed *(curated:claude/2026-07-03-w9)*
- **singer songwriter schema** (w0.85): vi-IV-I-V (Am-F-C-G) or its rotation I-V-vi-IV: THE four-chord pop engine since the mid-90s; relative-minor reading i-VI-III-VII is equally valid [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **verse position law** (w0.7): pop physiology from 912 human structures: verses live EARLY and die by the final third (1221/773/185); bridges never open a song (11/701 first third); the pop 'break' is early and SHORT (9s vs 21s chorus); outros 420/421 final-third — place sections where the population puts them [Harmonix label grammar, MIT data, mined locally] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **plagal shuttle** (w0.65): I<->IV oscillation (the 'amen' motion) — harmonic warmth without dominant tension; loops forever without demanding a cadence [Popular music: harmonic schemas] *(OMT2 (Open Music Theory v2, open textbook) via curated:claude/2026-07-05 (wave27))*
- **tape saturation** (w0.6): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*
- **huge space** (w0.6): bus reverb at maximum size, generous sends — the room is the instrument *(curated:claude/2026-07-02)*
- **power chords** (w0.6): rock rhythm guitar: root-5 power chords, palm-muted 8ths into open chorus hits — energy = dynamics contrast, not density *(curated:claude/2026-07-03-w5)*

## Sound recipes (this palette, these moves)
- **grit guitar**: faust guitar_grit: Karplus-Strong string -> tanh drive -> 2.9k cab presence; play power chords as NOTES (root-5-oct); drive 0..1 clean twang -> full grit; string chokes on release

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='rock_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (8th-note push a hair ahead, heavy 2&4 — motorik/punk/indie engine))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
