---
name: grime-arrangement
version: 2
kind: genre
tags: [grime, ukgarage, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 138-142; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -11..-7, band order low>mid>lowmid.
  - ESKI SQUARE BASS is non-negotiable: grime's eskibeat DNA: raw square-wave bass stabs (Pulse-style), icy and hollow — 140bpm, space between hits is the aggression
  - LOUDNESS RECOVERY is non-negotiable: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
  - HALF TIME 140 is non-negotiable: dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge
---
# Grime arrangement (graph-compiled)

Grime is a child of **ukgarage** — its groove laws apply unless overridden below.

## Techniques (weight order — the top ones DEFINE the genre)
- **eski square bass** (w0.95): grime's eskibeat DNA: raw square-wave bass stabs (Pulse-style), icy and hollow — 140bpm, space between hits is the aggression *(curated:claude/2026-07-03)*
- **loudness recovery** (w0.85): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **half time 140** (w0.8): dubstep pocket: 140bpm, snare ONLY on 3, kick sparse 1(+syncop), everything huge *(curated:claude/2026-07-03)*
- **brickwall mastering** (w0.7): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **call response melody** (w0.6): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **ghost snare drill** (w0.5): extra snares at 3.75/4.25 around the main pocket *(skill:drill-arrangement@v1)*

## Inherited from ukgarage
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- send reverb: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
- shuffle swing: hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt
- two step kick: NO four-on-floor: kick on 1 and ~2.75 (vary per bar); the hole IS the groove
- chopped chords: short m7/9 chord stabs (0.2-0.4 beats) on syncopated 16ths, filtered warm
- vocal chops: short pitched vocal stabs (choir kit, high keys) placed rhythmically
- groove ukg shuffle: THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre.
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- phrase aligned blend: transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases
- bass swap: ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat
- filter transition: fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-7, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
