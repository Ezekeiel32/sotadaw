---
name: future_bass-arrangement
version: 2
kind: genre
tags: [future_bass, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 140-160; set the song key (suggested: D major).
  - Mix: clipped_samples == 0, LUFS -9..-6, band order low>mid>lowmid.
  - FUTURE CHORD PUMP is non-negotiable: future bass signature: supersaw CHORDS pitch-bent between voicings, volume pumped by a free-running LFO (not kick sidechain) — the chord itself wobbles; brightness follows the pump
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
  - HALF TIME 140 is non-negotiable: dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge
---
# Future_Bass arrangement (graph-compiled)

## The pocket — futurebass_half
halftime bounce, roll into the 3  *(source: curated:claude/2026-07-03-patterns-w2 (executable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **future chord pump** (w0.95): future bass signature: supersaw CHORDS pitch-bent between voicings, volume pumped by a free-running LFO (not kick sidechain) — the chord itself wobbles; brightness follows the pump *(curated:claude/2026-07-03-w6)*
- **vocal chops** (w0.85): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **half time 140** (w0.8): dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge *(curated:claude/2026-07-03)*
- **supersaw pads** (w0.7): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*
- **hat rolls** (w0.6): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*

## Sound recipes (this palette, these moves)
- **odin modular lead**: Odin2 (263 named params: Osc1-3 wavetable/analog/FM, dual filters, 3 envs) as the big lead/pad synth: source {kind:'vst3', id:'Odin2'} + params by name ('Osc1 Wavetble Position', 'Filter1 Freq'...) — design leads for trance/hardwave/dubstep beyond the faust palette

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
