---
name: drill-arrangement
version: 5
kind: genre
tags: [drill, trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 138-146; set the song key (suggested: C# minor).
  - Mix: clipped_samples == 0, LUFS -18..-9, band order low>lowmid>mid>himid>high.
  - SLIDING 808 is non-negotiable: 808 pitch slides between roots (overlapping notes)
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - GHOST SNARE DRILL is non-negotiable: extra snares at 3.75/4.25 around the main pocket
---
# Drill arrangement (graph-compiled)

Drill is a child of **trap** — its groove laws apply unless overridden below.

## The pocket — drill_drums
UK drill pocket: snare 3, ghosts 3.75/4.25, sliding 808  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## Techniques (weight order — the top ones DEFINE the genre)
- **sliding 808** (w1.0): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **ghost snare drill** (w0.92): extra snares at 3.75/4.25 around the main pocket *(skill:drill-arrangement@v1)*
- **halftime groove** (w0.84): snare on beat 3 (not 2&4); space is the instrument *(skill:trap-arrangement@v2)*
- **hat rolls** (w0.76): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **tempo map motion** (w0.6): tempoMap on any song: halftime drops, ritardando outros (curve 0), section tempo switches — beats, warped audio, automation all follow *(skill:dj-blend@v2 (2026-07-03))*
- **true peak safety** (w0.6): master to <=-1 dBTP TRUE peak, not sample peak — Spotify/Apple/EBU R128 all specify -1 dBTP; inter-sample peaks reconstruct ~1-1.4dB higher than sample peaks (up to 1.81dB on drill 808s) and clip after lossy codec transcoding. A sample-domain limiter alone cannot guarantee it. *(curated:claude/2026-07-05-w38-mastering (firings 80-83, research-cited + ears-verified across 14 genres))*
- **streaming loudness target** (w0.6): the 2026 universal streaming target is -14 LUFS integrated (Spotify/YouTube/Tidal/Amazon all normalize to -14; Apple/Facebook -16). Do not chase loudness past it — platforms normalize DOWN. Master to -14 LUFS / <=-1 dBTP and it plays everywhere. *(curated:claude/2026-07-05-w38-mastering (firings 80-83, research-cited + ears-verified across 14 genres))*
- **softclip pre limiter** (w0.6): a TRANSPARENT soft clipper (pure tanh, no de-emphasis tone filter) before the final limiter shaves the sharpest 1-3dB of transients so the limiter works less hard = more loudness that still breathes. fx_saturate is the WRONG tool (its tone filter darkens 19-33%); use fx_softclip. The standard trap/drill loudness move. *(curated:claude/2026-07-05-w38-mastering (firings 80-83, research-cited + ears-verified across 14 genres))*
- **inter sample headroom by genre** (w0.6): dense 808/kick material (drill, house four-on-floor) generates the most inter-sample overshoot (~1.4-1.8dB); sparse material (ambient) almost none. A fixed sample ceiling of -3.0 lands all 14 tested genres <=-1 dBTP at ~0.3dB loudness cost (the ceiling clips transient PEAKS, not sustained level). Oversampled (4x/8x) true-peak limiting is the textbook fix. *(curated:claude/2026-07-05-w38-mastering (firings 80-83, research-cited + ears-verified across 14 genres))*

## Inherited from trap
- swing 16th: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- 808 glide: long overlapping 808 notes walking the scale; tune to key
- layered kick: sample kick transient + faust 808 body, body -6 to -12 under
- layered snare: sample clap + synth snare body at -12 to -18
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- groove boombap 56: apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities.
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
- tension and release: the core arrangement arc: build energy + anticipation (risers, filter opens, added layers, strategic PAUSE) then release it dramatically at the drop. A track without a tension curve is a loop. (composes with transitions risers/impacts + automation builds)
- section contrast: adjacent sections MUST differ to keep engagement — the chorus/drop stands out from the verse by altering melody, harmony, rhythm OR instrumentation; the bridge/break introduces new material. Sameness across sections = the doctor A2 breathe failure.
- energy contour: shape dynamics across the song. THE KEY LAW: impact comes from CONTRAST, not pushing the limiter — if the build is already loud+full, the drop has nowhere to go. So make a drop hit harder by SOFTENING the section before it (intensify build -) AND hardening the drop (intensify drop +): louder hits + more 16th hats + more layers. Keep the sub OUT of the build so the drop bass lands. Density+velocity+layer-count are the energy dial.
- strategic pause: a beat of silence or a filter-swept gap right BEFORE the release amplifies its impact — the ear resolves the held breath. The downlifter + a 1-beat drum cut sells the drop.

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **kick 808 zones**: kick_808 knobs: glide 0-8 (boom drop depth), decay 0.2-3s (sub tail), drive 0.5-5 (tanh fatness). decay 1.5-2.5 = the long trap 808; automate decay per section for verse/drop contrast.
- **keys dark zones**: keys_dark knobs: cutoff 200-3000 + sweep 0-6000 (filter env range), sub 0-1 (octave-down weight), detune/vibrato 0-0.02. Trap bell-keys = cutoff 1500 sub 0.8; automate cutoff for section builds.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-9, band order low>lowmid>mid>himid>high. If a filter build was used, centroid_by_quarter must RISE into the drop.
