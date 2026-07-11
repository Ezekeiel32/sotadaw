---
name: electro-arrangement
version: 2
kind: genre
tags: [electro, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 125-135; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -11..-7, band order low>mid>lowmid.
  - ELECTRO BOOGIE is non-negotiable: Detroit/Miami electro: 808 boogie syncopation, crisp machine snares on 2+4 with syncopated claps, vocoder hooks — robotic funk, no 4-floor
  - 808 GLIDE is non-negotiable: long overlapping 808 notes walking the scale; tune to key
  - NEON BASS is non-negotiable: 8th-note bass locked to the kick root, slightly saturated
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Electro arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **electro boogie** (w0.95): Detroit/Miami electro: 808 boogie syncopation, crisp machine snares on 2+4 with syncopated claps, vocoder hooks — robotic funk, no 4-floor *(curated:claude/2026-07-03)*
- **808 glide** (w0.6): long overlapping 808 notes walking the scale; tune to key *(skill:faust-808@v1)*
- **neon bass** (w0.6): 8th-note bass locked to the kick root, slightly saturated *(curated:claude/2026-07-02)*
- **cowbell lead** (w0.5): saturated cowbell/bell riff as THE melodic hook, minor pentatonic *(curated:claude/2026-07-02)*
- **vocal chops** (w0.4): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **tal analog bass**: TAL-NoiseMaker as the analog bass/lead: source {kind:'vst3', id:'TAL-NoiseMaker', params:{'Filter Cutoff':0.2-0.5,'Filter Resonance':0.2-0.5,'Filter Contour':0.3+}} — params fuzzy-match by NAME; automate any of its 93 knobs via set_track_param/automate

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-7, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
