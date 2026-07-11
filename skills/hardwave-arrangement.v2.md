---
name: hardwave-arrangement
version: 2
kind: genre
tags: [hardwave, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 140-160; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>mid>lowmid.
  - HARDWAVE LEAD is non-negotiable: hardwave: mournful detuned supersaw lead melodies over trap-pattern drums, enormous reverb/space; emotional minor toplines at halftime feel
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
  - HALF TIME 140 is non-negotiable: dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge
---
# Hardwave arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **hardwave lead** (w0.95): hardwave: mournful detuned supersaw lead melodies over trap-pattern drums, enormous reverb/space; emotional minor toplines at halftime feel *(curated:claude/2026-07-03-w11)*
- **send reverb** (w0.8): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **half time 140** (w0.8): dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge *(curated:claude/2026-07-03)*
- **sliding 808** (w0.6): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **odin modular lead**: Odin2 (263 named params: Osc1-3 wavetable/analog/FM, dual filters, 3 envs) as the big lead/pad synth: source {kind:'vst3', id:'Odin2'} + params by name ('Osc1 Wavetble Position', 'Filter1 Freq'...) — design leads for trance/hardwave/dubstep beyond the faust palette

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
