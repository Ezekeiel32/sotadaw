---
name: plugg-arrangement
version: 2
kind: genre
tags: [plugg, trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 65-78; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - PLUGG BELL PALETTE is non-negotiable: airy FM glass bells, synth flutes and soft plucks carry the melody — spacey, toy-like, LOW-PASSED soft; the beat feels weightless over hard 808s
  - MUFFLED CLAP 3 is non-negotiable: the plugg backbeat: ONE muffled, low-passed clap/snare on beat 3 (half-time), tucked under the melody instead of cracking over it
  - BEAT SKIP DROPOUT is non-negotiable: whole-beat DROPOUTS: the kick/808 skips a beat (or a whole bar goes drumless) so the loop breathes — the skip IS the hook
---
# Plugg arrangement (graph-compiled)

Plugg is a child of **trap** — its groove laws apply unless overridden below.

## The pocket — plugg_float
Plugg (~140 BPM, half-time, straight-ish): sparse syncopated kick doubling gliding 808s; ONE muffled low-passed clap on beat 3; lazy straight-8th hats; airy FM bells/flutes float the melody; a whole beat DROPS OUT every few bars so the loop breathes. Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **plugg bell palette** (w1.0): airy FM glass bells, synth flutes and soft plucks carry the melody — spacey, toy-like, LOW-PASSED soft; the beat feels weightless over hard 808s *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **muffled clap 3** (w0.92): the plugg backbeat: ONE muffled, low-passed clap/snare on beat 3 (half-time), tucked under the melody instead of cracking over it *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **beat skip dropout** (w0.84): whole-beat DROPOUTS: the kick/808 skips a beat (or a whole bar goes drumless) so the loop breathes — the skip IS the hook *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **gliding 808 melody** (w0.76): the 808 voice-leads (root -> third/fifth glides) under the chords — bass as the counter-melody, portamento audible *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*
- **pitched vocal topline** (w0.68): Auto-Tuned melodic rap-sung topline, often pitched up, doubled in octaves — the voice is an instrument riding the loop *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

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
- **plugg bells**: airy FM glass bells (fmbell) + synth flute (flute_lead) low-passed SOFT; kick_808/sub_clean gliding melodically; the clap muffled (low-pass fx_filter on the snare track); space is the luxury — leave dropout bars

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='trap_grid', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (trap IS the quantize grid: zero offsets, hat-roll velocity waves, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
