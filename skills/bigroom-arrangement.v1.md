---
name: bigroom-arrangement
version: 1
kind: genre
tags: [bigroom, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 126-130; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>mid>lowmid.
  - FESTIVAL DROP is non-negotiable: big-room drop: pitched kick + offbeat FM/saw stab in unison, white-noise risers 8 bars before, HALF the elements you think you need
  - RISER THROWS is non-negotiable: before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up)
  - PUMP SIDECHAIN is non-negotiable: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
---
# Bigroom arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **festival drop** (w0.95): big-room drop: pitched kick + offbeat FM/saw stab in unison, white-noise risers 8 bars before, HALF the elements you think you need *(curated:claude/2026-07-03-w5)*
- **riser throws** (w0.85): before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up) *(curated:claude/2026-07-02)*
- **pump sidechain** (w0.8): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*
- **brickwall mastering** (w0.8): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **supersaw pads** (w0.7): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
