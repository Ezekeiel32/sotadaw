---
name: rage-arrangement
version: 2
kind: genre
tags: [rage, trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 150-170; set the song key (suggested: F minor (Phrygian)).
  - Mix: clipped_samples == 0, LUFS -8..-5, band order low>lowmid>mid.
  - GLIDING 808 is non-negotiable: a distorted, portamento-GLIDING 808 that slides between notes as the bassline AND the melody — overdriven so it fuzzes, the defining rage low end
  - DETUNED RAGE LEAD is non-negotiable: a heavily detuned super-saw / bell / brass synth stab (slightly out-of-tune on purpose), often layered and pitched high — the aggressive, queasy rage topline
  - TRIPLET HAT ROLL is non-negotiable: trap hats with fast triplet/roll bursts and stutters over a straight grid, snare/clap on beat 3 (half-time feel) at a hot ~140-155 BPM
---
# Rage arrangement (graph-compiled)

Rage is a child of **trap** — its groove laws apply unless overridden below.

## The pocket — rage_grid
Rage / opium (~145 BPM sweet-spot — 155 runs hot; 4/4, triplet hats): a distorted, portamento-GLIDING 808 is bass AND melody, sliding between notes overdriven so it fuzzes; snare/clap on beat 3 (half-time feel); triplet hat rolls and stutters; a heavily DETUNED super-saw/bell stab screams high; single static minor/Phrygian vamp; the whole drum+808 bus soft-clipped into one aggressive wall.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **gliding 808** (w1.0): a distorted, portamento-GLIDING 808 that slides between notes as the bassline AND the melody — overdriven so it fuzzes, the defining rage low end *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **detuned rage lead** (w0.92): a heavily detuned super-saw / bell / brass synth stab (slightly out-of-tune on purpose), often layered and pitched high — the aggressive, queasy rage topline *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **triplet hat roll** (w0.84): trap hats with fast triplet/roll bursts and stutters over a straight grid, snare/clap on beat 3 (half-time feel) at a hot ~140-155 BPM *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **distorted drum bus** (w0.76): the whole drum + 808 bus pushed into overdrive/soft-clip so it distorts and glues into one aggressive, saturated wall (opium/Carti aesthetic) *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **minimal vamp energy** (w0.68): harmony is a single static minor/Phrygian vamp; the song is ENERGY and texture (screamed ad-libs, distortion, space) not chord movement *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Inherited from trap
- halftime groove: snare on beat 3 (not 2&4); space is the instrument
- swing 16th: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- hat rolls: 16th->32nd bursts at phrase ends; velocity ramps
- 808 glide: long overlapping 808 notes walking the scale; tune to key
- layered kick: sample kick transient + faust 808 body, body -6 to -12 under
- layered snare: sample clap + synth snare body at -12 to -18
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- ...and from the trap skill itself: brickwall mastering, groove boombap 56, tempo map motion, curve shaped automation, cadence VI i fall, two chord vamp, complementary eq unmask, unmask escalation ladder, parallel thwack attack, mono below 120, riser into drop, impact downbeat, seam connects law, true peak safety, streaming loudness target, softclip pre limiter, inter sample headroom by genre, tension and release, section contrast, energy contour, strategic pause

## Sound recipes (this palette, these moves)
- **rage 808**: gliding distorted 808 = sub_clean/kick_808 with portamento + HEAVY fx_saturate/fx_softclip; detuned lead = supersaw_fat/reese/fmbell pitched high, layered and slightly out of tune ON PURPOSE; hardkick + triplet hats; push the drum bus into fx_softclip for the wall. Loud and aggressive but keep clipped_samples=0 (soft-clip, don't hard-clip).

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='trap_grid', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (trap IS the quantize grid: zero offsets, hat-roll velocity waves, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-5, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
