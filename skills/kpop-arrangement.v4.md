---
name: kpop-arrangement
version: 4
kind: genre
tags: [kpop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-140; set the song key (suggested: Ab major).
  - Mix: clipped_samples == 0, LUFS -7..-5, band order low>mid>lowmid.
  - SECTION MORPH is non-negotiable: kpop production: SECTIONS CHANGE GENRE — trap verse, house chorus, R&B bridge; the whiplash is the aesthetic. Keep key or tempo as the single thread so it reads as one song
  - TOPLINE FIRST is non-negotiable: pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
---
# Kpop arrangement (graph-compiled)

## The pocket — kpop_hybrid
kpop loop DNA (wave19)  *(source: OMT2 'Four-Chord Schemas' degrees -> archetype chord DNA via curated:claude/2026-07-05 (wave29b) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **section morph** (w0.95): kpop production: SECTIONS CHANGE GENRE — trap verse, house chorus, R&B bridge; the whiplash is the aesthetic. Keep key or tempo as the single thread so it reads as one song *(curated:claude/2026-07-03-w9)*
- **topline first** (w0.85): pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses *(curated:claude/2026-07-03-w9)*
- **brickwall mastering** (w0.8): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **prechorus lift** (w0.8): the pre-chorus LIFTS into the chorus: harmony climbs (IV-V or bVI-bVII), drums thin out (drop the kick or go half-time) for 2-4 bars, then the chorus slams full-arrangement on the 1 *(curated:claude/2026-07-03-w9)*
- **verse position law** (w0.7): pop physiology from 912 human structures: verses live EARLY and die by the final third (1221/773/185); bridges never open a song (11/701 first third); the pop 'break' is early and SHORT (9s vs 21s chorus); outros 420/421 final-third — place sections where the population puts them [Harmonix label grammar, MIT data, mined locally] *(campaign batteries 2026-07-05 (firings 24-38: solo-render proofs, 912-song grammar, flip verification chain) via curated:claude (wave33))*
- **supersaw pads** (w0.6): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*
- **hopscotch schema** (w0.6): IV-V-vi-I: the post-2010 pop schema (OMT2's newest named cycle); minor reading VI-VII-i-III; variation VI-V-i-III (V subs VII in minor) [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*

## Sound recipes (this palette, these moves)
- **string ostinato**: faust strings_stacc: spiccato section, bow bite + no sustain — THE ostinato engine: 8th/16th cells (same 1-2 pitches per bar) under cine_brass swells + timpani hits; also disco/funk stabs

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='trap_grid', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (trap IS the quantize grid: zero offsets, hat-roll velocity waves, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -7..-5, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
