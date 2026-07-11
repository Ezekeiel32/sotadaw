---
name: trap-arrangement
version: 8
kind: genre
tags: [trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-160; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -18..-9, band order low>lowmid>mid>himid>high.
  - HALFTIME GROOVE is non-negotiable: snare on beat 3 (not 2&4); space is the instrument
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - SWING 16TH is non-negotiable: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
  - GROOVE BOOMBAP 56 is non-negotiable: apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities.
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Trap arrangement (graph-compiled)

## The pocket — trap_drums
kick sparse+syncopated; snare beat 3; hats 8th/16th w/ rolls  *(source: curated:claude/2026-07-04 (wave21 fills — loop_gen stamps bar-4 turnarounds))*

## Techniques (weight order — the top ones DEFINE the genre)
- **halftime groove** (w1.0): snare on beat 3 (not 2&4); space is the instrument *(skill:trap-arrangement@v2)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **swing 16th** (w0.92): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*
- **groove boombap 56** (w0.9): apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **ghost notes** (w0.84): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*
- **loudness recovery** (w0.8): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **hat rolls** (w0.76): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **curve shaped automation** (w0.7): automation point curve -1..1 shapes the leaving segment: >0 late-bloom (THE build shape into drops), <0 early-jump (post-drop settle). Linear builds feel early/flat. *(skill:automation-motion@v2 (2026-07-03, engine-verified))*
- **808 glide** (w0.68): long overlapping 808 notes walking the scale; tune to key *(skill:faust-808@v1)*
- **layered kick** (w0.6): sample kick transient + faust 808 body, body -6 to -12 under *(skill:sound-palette@v2)*
- **tempo map motion** (w0.6): tempoMap on any song: halftime drops, ritardando outros (curve 0), section tempo switches — beats, warped audio, automation all follow *(skill:dj-blend@v2 (2026-07-03))*
- **layered snare** (w0.52): sample clap + synth snare body at -12 to -18 *(skill:sound-palette@v2)*

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **flute topline**: faust flute_lead: breathy flute w/ late vibrato — jazz/bossa heads, trap-flute toplines, highlife runs; legato lines (len ~0.9 of gap), short notes read as tonguing
- **kick 808 zones**: kick_808 knobs: glide 0-8 (boom drop depth), decay 0.2-3s (sub tail), drive 0.5-5 (tanh fatness). decay 1.5-2.5 = the long trap 808; automate decay per section for verse/drop contrast.
- **snare zones**: snare knobs: body 0-1.5 (tonal level), snap 0-1.5 (noise crack), tone 0.5-2 (pitch scale), decay 0.3-3 (envelope scale). snap up + body down = tight trap crack; tone 0.7 + decay 1.5 = fat lo-fi snare.
- **keys dark zones**: keys_dark knobs: cutoff 200-3000 + sweep 0-6000 (filter env range), sub 0-1 (octave-down weight), detune/vibrato 0-0.02. Trap bell-keys = cutoff 1500 sub 0.8; automate cutoff for section builds.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-9, band order low>lowmid>mid>himid>high. If a filter build was used, centroid_by_quarter must RISE into the drop.
