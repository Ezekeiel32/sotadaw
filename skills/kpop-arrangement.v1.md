---
name: kpop-arrangement
version: 1
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

## Techniques (weight order — the top ones DEFINE the genre)
- **section morph** (w0.95): kpop production: SECTIONS CHANGE GENRE — trap verse, house chorus, R&B bridge; the whiplash is the aesthetic. Keep key or tempo as the single thread so it reads as one song *(curated:claude/2026-07-03-w9)*
- **topline first** (w0.85): pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses *(curated:claude/2026-07-03-w9)*
- **brickwall mastering** (w0.8): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **prechorus lift** (w0.8): the pre-chorus LIFTS into the chorus: harmony climbs (IV-V or bVI-bVII), drums thin out (drop the kick or go half-time) for 2-4 bars, then the chorus slams full-arrangement on the 1 *(curated:claude/2026-07-03-w9)*
- **supersaw pads** (w0.6): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -7..-5, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
