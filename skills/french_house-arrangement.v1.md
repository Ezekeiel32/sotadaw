---
name: french_house-arrangement
version: 1
kind: genre
tags: [french_house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 118-126; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>lowmid>mid.
  - FILTER DISCO LOOP is non-negotiable: french house: loop 2-4 bars of disco (or self-sampled equivalent) and RIDE a lowpass over 8-16 bars with sidechain pump — the filter ride IS the arrangement
  - PUMP SIDECHAIN is non-negotiable: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
  - FOUR FLOOR DISCO is non-negotiable: disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria
---
# French_House arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **filter disco loop** (w0.95): french house: loop 2-4 bars of disco (or self-sampled equivalent) and RIDE a lowpass over 8-16 bars with sidechain pump — the filter ride IS the arrangement *(curated:claude/2026-07-03-w10)*
- **pump sidechain** (w0.9): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*
- **four floor disco** (w0.7): disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria *(curated:claude/2026-07-03-w5)*
- **tape saturation** (w0.6): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
