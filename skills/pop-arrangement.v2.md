---
name: pop-arrangement
version: 2
kind: genre
tags: [pop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-122; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>lowmid>mid.
  - TOPLINE FIRST is non-negotiable: pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses
  - PRECHORUS LIFT is non-negotiable: the pre-chorus LIFTS into the chorus: harmony climbs (IV-V or bVI-bVII), drums thin out (drop the kick or go half-time) for 2-4 bars, then the chorus slams full-arrangement on the 1
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
---
# Pop arrangement (graph-compiled)

## The pocket — pop_four
clean four + clap, straight 8th hats  *(source: curated:claude/2026-07-03-patterns-w2 (executable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **topline first** (w0.95): pop law: the melody IS the product — a hook every 2 bars, sections exist to frame the topline; if a part fights the vocal melody, the part loses *(curated:claude/2026-07-03-w9)*
- **prechorus lift** (w0.9): the pre-chorus LIFTS into the chorus: harmony climbs (IV-V or bVI-bVII), drums thin out (drop the kick or go half-time) for 2-4 bars, then the chorus slams full-arrangement on the 1 *(curated:claude/2026-07-03-w9)*
- **brickwall mastering** (w0.7): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **pump sidechain** (w0.6): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*
- **vocal chops** (w0.6): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
