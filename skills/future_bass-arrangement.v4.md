---
name: future_bass-arrangement
version: 4
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
halftime bounce, roll into the 3  *(source: OMT2 'Four-Chord Schemas' degrees -> archetype chord DNA via curated:claude/2026-07-05 (wave29b) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **future chord pump** (w0.95): future bass signature: supersaw CHORDS pitch-bent between voicings, volume pumped by a free-running LFO (not kick sidechain) — the chord itself wobbles; brightness follows the pump *(curated:claude/2026-07-03-w6)*
- **vocal chops** (w0.85): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **half time 140** (w0.8): dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge *(curated:claude/2026-07-03)*
- **supersaw pads** (w0.7): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*
- **mono sub stereo body** (w0.7): the techno bass trick: split the bass — a MONO sub (sine, dead center, <120Hz) carries the weight; a STEREO body (harmonics, saturated, widened above ~150Hz) carries the character. Club-safe AND wide [Weapon/NI law] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **hat rolls** (w0.6): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **hopscotch schema** (w0.6): IV-V-vi-I: the post-2010 pop schema (OMT2's newest named cycle); minor reading VI-VII-i-III; variation VI-V-i-III (V subs VII in minor) [Popular music: four-chord schemas] *(OMT2 'Four-Chord Schemas' + 'Blues Harmony' (Hughes & Lavengood, Open Music Theory v2, CC BY-SA, viva.pressbooks.pub/openmusictheory) via curated:claude/2026-07-05 (wave29))*
- **riser into drop** (w0.6): the build-up riser: a bandpass-swept noise tension line in the 1-2 bars before a drop, gain late-blooming (env^2) to land EXACTLY on the downbeat — the single most universal EDM/pop transition; place at every low->high section seam, never drop->drop *(engine-witnessed transitions.py (firing 58: solo-render -33->-17->-13dB late-bloom into the drop) via curated:claude/2026-07-05 (wave35 glue))*
- **impact downbeat** (w0.6): a single low sub-boom ON the drop downbeat (the counterpart to the riser): marks the arrival, fills the sub the riser vacated as it peaks — cheap, essential, one note *(engine-witnessed transitions.py (firing 58: solo-render -33->-17->-13dB late-bloom into the drop) via curated:claude/2026-07-05 (wave35 glue))*
- **seam connects law** (w0.6): sections must CONNECT, not just abut: after each part breathes per-section (density), the boundary INTO a lift wants a build (riser/fill/filter-open) and the arrival wants a mark (impact/crash) — the glue is what separates an arrangement from a playlist of loops *(engine-witnessed transitions.py (firing 58: solo-render -33->-17->-13dB late-bloom into the drop) via curated:claude/2026-07-05 (wave35 glue))*
- **haas caution** (w0.5): the Haas trick (10-40ms delay on one side = instant width) is a MONO TRAP: the delay comb-filters on the fold. Use it on throwaway ear-candy, NEVER the bass, kick, or lead — and always fold-check [width without phase, the caveat] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*

## Sound recipes (this palette, these moves)
- **odin modular lead**: Odin2 (263 named params: Osc1-3 wavetable/analog/FM, dual filters, 3 envs) as the big lead/pad synth: source {kind:'vst3', id:'Odin2'} + params by name ('Osc1 Wavetble Position', 'Filter1 Freq'...) — design leads for trance/hardwave/dubstep beyond the faust palette
- **pluck zones**: pluck knobs: decay 0.05-2s (squared env - snappy), color 1-12 (pitch-tracking LP multiple: 2 = dark koto, 10 = open). Dance plucks = color 6-8 decay 0.3; automate color rising into a drop.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='trap_grid', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (trap IS the quantize grid: zero offsets, hat-roll velocity waves, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -9..-6, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
