---
name: rage-arrangement
version: 1
kind: genre
tags: [rage, trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-170; set the song key (suggested: F minor (Phrygian)).
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
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- groove boombap 56: apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities.
- tempo map motion: tempoMap on any song: halftime drops, ritardando outros (curve 0), section tempo switches — beats, warped audio, automation all follow
- curve shaped automation: automation point curve -1..1 shapes the leaving segment: >0 late-bloom (THE build shape into drops), <0 early-jump (post-drop settle). Linear builds feel early/flat.
- cadence VI i fall: VI->i fall: subdominant slide home — melancholic loop-closer (trance/dnb/phonk)
- two chord vamp: two-chord vamp: harmony as texture, motion lives in the beat (dnb/dub/phonk/ambient)
- complementary eq unmask: two voices collide in one band (kick/bass is the classic): BOOST that band slightly in the priority voice and CUT the same band in the other — one collision, two opposite small moves; stem_callouts finds the pair, this is the fix [MASK]
- unmask escalation ladder: unmask in escalating precision, stop at the first rung that works: 1) static complementary EQ; 2) wideband sidechain duck (whole voice, when trigger plays); 3) dynamic-EQ/multiband duck (ONLY the masked band, ONLY when the trigger hits) — never pay more transparency than the collision costs [MASK]
- parallel thwack attack: on the parallel crush bus the ATTACK chooses the transient's character: 25-30 ms = 'thwack'; 30-100 ms = heavier kick punch; 10-30 ms = sharp snap — then blend under the dry until it's felt not heard [PARA]
- mono below 120: keep everything below ~120Hz CENTERED — a stereo/out-of-phase sub cancels on mono club subs and phone speakers and eats headroom; the single most important width rule. fx_widen with a low-cut on the side, or simply pan/write bass + kick dead center [mono-compatibility law]
- riser into drop: the build-up riser: a bandpass-swept noise tension line in the 1-2 bars before a drop, gain late-blooming (env^2) to land EXACTLY on the downbeat — the single most universal EDM/pop transition; place at every low->high section seam, never drop->drop
- impact downbeat: a single low sub-boom ON the drop downbeat (the counterpart to the riser): marks the arrival, fills the sub the riser vacated as it peaks — cheap, essential, one note
- seam connects law: sections must CONNECT, not just abut: after each part breathes per-section (density), the boundary INTO a lift wants a build (riser/fill/filter-open) and the arrival wants a mark (impact/crash) — the glue is what separates an arrangement from a playlist of loops
- true peak safety: master to <=-1 dBTP TRUE peak, not sample peak — Spotify/Apple/EBU R128 all specify -1 dBTP; inter-sample peaks reconstruct ~1-1.4dB higher than sample peaks (up to 1.81dB on drill 808s) and clip after lossy codec transcoding. A sample-domain limiter alone cannot guarantee it.
- streaming loudness target: the 2026 universal streaming target is -14 LUFS integrated (Spotify/YouTube/Tidal/Amazon all normalize to -14; Apple/Facebook -16). Do not chase loudness past it — platforms normalize DOWN. Master to -14 LUFS / <=-1 dBTP and it plays everywhere.
- softclip pre limiter: a TRANSPARENT soft clipper (pure tanh, no de-emphasis tone filter) before the final limiter shaves the sharpest 1-3dB of transients so the limiter works less hard = more loudness that still breathes. fx_saturate is the WRONG tool (its tone filter darkens 19-33%); use fx_softclip. The standard trap/drill loudness move.
- inter sample headroom by genre: dense 808/kick material (drill, house four-on-floor) generates the most inter-sample overshoot (~1.4-1.8dB); sparse material (ambient) almost none. A fixed sample ceiling of -3.0 lands all 14 tested genres <=-1 dBTP at ~0.3dB loudness cost (the ceiling clips transient PEAKS, not sustained level). Oversampled (4x/8x) true-peak limiting is the textbook fix.
- tension and release: the core arrangement arc: build energy + anticipation (risers, filter opens, added layers, strategic PAUSE) then release it dramatically at the drop. A track without a tension curve is a loop. (composes with transitions risers/impacts + automation builds)
- section contrast: adjacent sections MUST differ to keep engagement — the chorus/drop stands out from the verse by altering melody, harmony, rhythm OR instrumentation; the bridge/break introduces new material. Sameness across sections = the doctor A2 breathe failure.
- energy contour: shape dynamics across the song. THE KEY LAW: impact comes from CONTRAST, not pushing the limiter — if the build is already loud+full, the drop has nowhere to go. So make a drop hit harder by SOFTENING the section before it (intensify build -) AND hardening the drop (intensify drop +): louder hits + more 16th hats + more layers. Keep the sub OUT of the build so the drop bass lands. Density+velocity+layer-count are the energy dial.
- strategic pause: a beat of silence or a filter-swept gap right BEFORE the release amplifies its impact — the ear resolves the held breath. The downlifter + a 1-beat drum cut sells the drop.

## Sound recipes (this palette, these moves)
- **rage 808**: gliding distorted 808 = sub_clean/kick_808 with portamento + HEAVY fx_saturate/fx_softclip; detuned lead = supersaw_fat/reese/fmbell pitched high, layered and slightly out of tune ON PURPOSE; hardkick + triplet hats; push the drum bus into fx_softclip for the wall. Loud and aggressive but keep clipped_samples=0 (soft-clip, don't hard-clip).

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-5, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
