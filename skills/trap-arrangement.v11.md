---
name: trap-arrangement
version: 11
kind: genre
tags: [trap, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-160; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid>himid>high.
  - HALFTIME GROOVE is non-negotiable: snare on beat 3 (not 2&4); space is the instrument
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - SWING 16TH is non-negotiable: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
  - GROOVE BOOMBAP 56 is non-negotiable: apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities.
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Trap arrangement (graph-compiled)

## The pocket — trap_drums
kick sparse+syncopated; snare beat 3; hats 8th/16th w/ rolls  *(source: curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9))*

## Techniques (weight order — the top ones DEFINE the genre)
- **halftime groove** (w1.0): snare on beat 3 (not 2&4); space is the instrument *(skill:trap-arrangement@v2)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **swing 16th** (w0.92): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*
- **groove boombap 56** (w0.9): apply_groove('boombap_56', amount 0.8-1.0) - 56% swing + heavy backbeat velocities. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **mono below 120** (w0.85): keep everything below ~120Hz CENTERED — a stereo/out-of-phase sub cancels on mono club subs and phone speakers and eats headroom; the single most important width rule. fx_widen with a low-cut on the side, or simply pan/write bass + kick dead center [mono-compatibility law] *(iZotope Learn (mid/side processing; 8 mid/side mistakes) + Weapon/NI/Mastering-The-Mix corroboration, read 2026-07-05 via curated:claude (wave34 space lane))*
- **ghost notes** (w0.84): low-velocity (0.25-0.45) off-grid hits between main hits *(skill:trap-arrangement@v2)*
- **loudness recovery** (w0.8): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **complementary eq unmask** (w0.8): two voices collide in one band (kick/bass is the classic): BOOST that band slightly in the priority voice and CUT the same band in the other — one collision, two opposite small moves; stem_callouts finds the pair, this is the fix [MASK] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **hat rolls** (w0.76): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*
- **unmask escalation ladder** (w0.75): unmask in escalating precision, stop at the first rung that works: 1) static complementary EQ; 2) wideband sidechain duck (whole voice, when trigger plays); 3) dynamic-EQ/multiband duck (ONLY the masked band, ONLY when the trigger hits) — never pay more transparency than the collision costs [MASK] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- **curve shaped automation** (w0.7): automation point curve -1..1 shapes the leaving segment: >0 late-bloom (THE build shape into drops), <0 early-jump (post-drop settle). Linear builds feel early/flat. *(skill:automation-motion@v2 (2026-07-03, engine-verified))*
- **parallel thwack attack** (w0.7): on the parallel crush bus the ATTACK chooses the transient's character: 25-30 ms = 'thwack'; 30-100 ms = heavier kick punch; 10-30 ms = sharp snap — then blend under the dry until it's felt not heard [PARA] *(iZotope Learn (what-is-frequency-masking / 16-common-eq-mistakes / parallel-compression-mistakes / mixing-vocals-space), read at source, via curated:claude/2026-07-05 (wave30 mix-wisdom))*
- also in this genre's DNA (lower weight): 808 glide, tension and release, section contrast, energy contour, strategic pause, layered kick, tempo map motion, cadence VI i fall, two chord vamp, riser into drop, impact downbeat, seam connects law, true peak safety, streaming loudness target, softclip pre limiter, inter sample headroom by genre, layered snare

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **flute topline**: faust flute_lead: breathy flute w/ late vibrato — jazz/bossa heads, trap-flute toplines, highlife runs; legato lines (len ~0.9 of gap), short notes read as tonguing
- **kick 808 zones**: kick_808 knobs: glide 0-8 (boom drop depth), decay 0.2-3s (sub tail), drive 0.5-5 (tanh fatness). decay 1.5-2.5 = the long trap 808; automate decay per section for verse/drop contrast.
- **snare zones**: snare knobs: body 0-1.5 (tonal level), snap 0-1.5 (noise crack), tone 0.5-2 (pitch scale), decay 0.3-3 (envelope scale). snap up + body down = tight trap crack; tone 0.7 + decay 1.5 = fat lo-fi snare.
- **keys dark zones**: keys_dark knobs: cutoff 200-3000 + sweep 0-6000 (filter env range), sub 0-1 (octave-down weight), detune/vibrato 0-0.02. Trap bell-keys = cutoff 1500 sub 0.8; automate cutoff for section builds.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='trap_grid', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (trap IS the quantize grid: zero offsets, hat-roll velocity waves, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid>himid>high. If a filter build was used, centroid_by_quarter must RISE into the drop.
