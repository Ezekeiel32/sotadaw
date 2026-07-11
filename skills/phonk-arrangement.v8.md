---
name: phonk-arrangement
version: 8
kind: genre
tags: [phonk, trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-145; set the song key (suggested: C# minor).
  - Mix: clipped_samples == 0, LUFS -16..-8, band order low>lowmid>mid>himid>high.
  - COWBELL LEAD is non-negotiable: saturated cowbell/bell riff as THE melodic hook, minor pentatonic
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - GAIN STAGED SATURATION is non-negotiable: saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims).
  - MEMPHIS CHANT is non-negotiable: dark chopped vocal stab as rhythmic texture (sample kit / choir low)
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Phonk arrangement (graph-compiled)

Phonk is a child of **trap** — its groove laws apply unless overridden below.

## The pocket — phonk_drums
trap pocket but denser hats; kick doubles before snare; everything saturated  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **cowbell lead** (w1.0): saturated cowbell/bell riff as THE melodic hook, minor pentatonic *(curated:claude/2026-07-02)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **gain staged saturation** (w0.95): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **memphis chant** (w0.92): dark chopped vocal stab as rhythmic texture (sample kit / choir low) *(curated:claude/2026-07-02)*
- **loudness recovery** (w0.85): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **tape saturation** (w0.84): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*
- **halftime groove** (w0.76): snare on beat 3 (not 2&4); space is the instrument *(skill:trap-arrangement@v2)*
- **unmask escalation ladder** (w0.75): unmask in escalating precision, stop at the first rung that works: 1) static complementary EQ; 2) wideband sidechain duck (whole voice, when trigger plays); 3) dynamic-EQ/multiband duck (ONLY the masked band, ONLY when the trigger hits) — never pay more transparency than the collision costs [MASK] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **parallel thwack attack** (w0.7): on the parallel crush bus the ATTACK chooses the transient's character: 25-30 ms = 'thwack'; 30-100 ms = heavier kick punch; 10-30 ms = sharp snap — then blend under the dry until it's felt not heard [PARA] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **808 glide** (w0.68): long overlapping 808 notes walking the scale; tune to key *(skill:faust-808@v1)*
- **hat rolls** (w0.6): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **cadence VI i fall** (w0.6): VI->i fall: subdominant slide home — melancholic loop-closer (trance/dnb/phonk) *(curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*
- **two chord vamp** (w0.6): two-chord vamp: harmony as texture, motion lives in the beat (dnb/dub/phonk/ambient) *(curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*
- **swing 16th** (w0.52): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*

## Inherited from trap
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- layered kick: sample kick transient + faust 808 body, body -6 to -12 under
- layered snare: sample clap + synth snare body at -12 to -18
- groove boombap 56: apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities.
- tempo map motion: tempoMap on any song: halftime drops, ritardando outros (curve 0), section tempo switches — beats, warped audio, automation all follow
- curve shaped automation: automation point curve -1..1 shapes the leaving segment: >0 late-bloom (THE build shape into drops), <0 early-jump (post-drop settle). Linear builds feel early/flat.
- complementary eq unmask: two voices collide in one band (kick/bass is the classic): BOOST that band slightly in the priority voice and CUT the same band in the other — one collision, two opposite small moves; stem_callouts finds the pair, this is the fix [MASK]

## Sound recipes (this palette, these moves)
- **phonk cowbell**: hat_metal detuned low (source.decay up) OR gm_drums cowbell key 56, through fx_saturate drive 10
- **phonk chant**: choir kit low register, short notes on offbeats, fx_reverb small dark
- **phonk 808**: kick_808 with 808_glide walking C#1, fx_saturate on the 808 ALLOWED here (genre exception)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **kick 808 zones**: kick_808 knobs: glide 0-8 (boom drop depth), decay 0.2-3s (sub tail), drive 0.5-5 (tanh fatness). decay 1.5-2.5 = the long trap 808; automate decay per section for verse/drop contrast.
- **keys dark zones**: keys_dark knobs: cutoff 200-3000 + sweep 0-6000 (filter env range), sub 0-1 (octave-down weight), detune/vibrato 0-0.02. Trap bell-keys = cutoff 1500 sub 0.8; automate cutoff for section builds.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-8, band order low>lowmid>mid>himid>high. If a filter build was used, centroid_by_quarter must RISE into the drop.
