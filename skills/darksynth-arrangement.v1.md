---
name: darksynth-arrangement
version: 1
kind: genre
tags: [darksynth, synthwave, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-150; set the song key (suggested: D minor (Phrygian)).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - REESE ARP OSTINATO is non-negotiable: a distorted reese/saw bass ARP running straight 16ths as the engine — the John Carpenter pulse weaponized
  - GATED REVERB SNARE is non-negotiable: the 80s gated-reverb snare on 2 & 4 — huge splash, hard cut; the retro-horror backbeat
  - CARPENTER PAD is non-negotiable: detuned-saw / minor-triad synth pads holding long Aeolian/Phrygian tones — the horror-score bed
---
# Darksynth arrangement (graph-compiled)

Darksynth is a child of **synthwave** — its groove laws apply unless overridden below.

## The pocket — carpenter_engine
Darksynth (~125 BPM, machine-straight): four-on-the-floor kick + huge GATED-REVERB snare on 2&4; a distorted reese/saw bass arp runs straight 16ths (the Carpenter pulse); detuned minor pads hold dread above; audible sidechain pump; half-time menace breaks (kick 1, snare 3) between club sections.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **reese arp ostinato** (w1.0): a distorted reese/saw bass ARP running straight 16ths as the engine — the John Carpenter pulse weaponized *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **gated reverb snare** (w0.92): the 80s gated-reverb snare on 2 & 4 — huge splash, hard cut; the retro-horror backbeat *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **carpenter pad** (w0.84): detuned-saw / minor-triad synth pads holding long Aeolian/Phrygian tones — the horror-score bed *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **sidechain menace** (w0.76): audible sidechain pump on pads/bass to a four-on-the-floor kick — breathing dread *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **halftime menace break** (w0.68): the half-time variant: kick 1, snare 3, everything darker and slower — menace between club sections *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Inherited from synthwave
- width bloom: fx_widen width 0.6 verse -> 1.4-1.7 hook; never on low end
- supersaw pads: wide detuned saw chords, whole/half notes, fx_widen — the neon wall
- arp 8th: relentless 8th/16th arpeggio (pluck) outlining the chord, fx_delay dotted
- neon bass: 8th-note bass locked to the kick root, slightly saturated
- vst factory presets: factory sounds FIRST for synth-genre leads/pads/basses — ONE CALL: vst_presets(query='PAD'|'BASS'|'LEAD'|..., mode='get', song=<song>, track=<track>) APPLIES the sound directly (source set, or fx appended for Surge XT Effects) — no params to copy. Browse first with mode='list'. Then write notes on the track and reshape 2-5 named knobs per synth-maps. Faust voices are for drums/percussion/utility
- synth param maps: presets are STARTING POINTS: after vst_presets get, reshape with the synth-maps skill — Odin2 big-five (Filter1 Frequency 20-20k log, AmpEnv ADSR 0.001-10s log, Filter1 Envelope Amount ±1, Osc volumes -60..12dB, LFO1 0.05-100Hz) and TAL 0..1 equivalents; values in NATURAL units; log knobs move multiplicatively (half/double); automate any of them for motion
- cadence modal VII i: the modal cadence: bVII -> i (no leading tone; THE loop-closer of minor-modal electronic music)
- mid side width control: width is DYNAMIC, not a static knob: compressing/boosting the MID makes loud center sounds read wider by contrast; side-only processing adds air that vanishes in mono (acceptable IF it only sweetens the stereo image) — treat mid and side as two mixes [mid/side processing]
- width by arrangement: the widest mixes earn it in the WRITE, not the widener: hard-pan doubled parts (two takes L/R), spread a stereo pad wide UNDER a centered lead, keep the focal element (lead/vocal/kick) center — width is contrast, and a wall of wide reads as narrow [arrangement-first width]
- haas caution: the Haas trick (10-40ms delay on one side = instant width) is a MONO TRAP: the delay comb-filters on the fold. Use it on throwaway ear-candy, NEVER the bass, kick, or lead — and always fold-check [width without phase, the caveat]
- riser into drop: the build-up riser: a bandpass-swept noise tension line in the 1-2 bars before a drop, gain late-blooming (env^2) to land EXACTLY on the downbeat — the single most universal EDM/pop transition; place at every low->high section seam, never drop->drop
- impact downbeat: a single low sub-boom ON the drop downbeat (the counterpart to the riser): marks the arrival, fills the sub the riser vacated as it peaks — cheap, essential, one note
- seam connects law: sections must CONNECT, not just abut: after each part breathes per-section (density), the boundary INTO a lift wants a build (riser/fill/filter-open) and the arrival wants a mark (impact/crash) — the glue is what separates an arrangement from a playlist of loops

## Sound recipes (this palette, these moves)
- **carpenter rig**: distorted reese 16th-arp (reese + fx_saturate) = the engine; supersaw/pad_motion detuned minor pads; gated snare = snare + short fx_reverb hard-cut; fx_pump sidechain audible on pads; keys_dark stabs for the stingers

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
