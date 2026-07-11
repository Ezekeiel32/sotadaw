---
name: hardstyle-arrangement
version: 2
kind: genre
tags: [hardstyle, trance, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 150-160; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -11..-6, band order low>lowmid>mid.
  - HARDSTYLE KICK is non-negotiable: distorted kick with tonal tail (kick_psy punch 18+ through fx_saturate drive 12; tail pitched to key)
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - RISER THROWS is non-negotiable: before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up)
---
# Hardstyle arrangement (graph-compiled)

Hardstyle is a child of **trance** — its groove laws apply unless overridden below.

## The pocket — hard_pocket
kick IS the bass (tonal tail); offbeat screech leads; halftime breakdowns  *(source: curated:claude/2026-07-03)*

## Techniques (weight order — the top ones DEFINE the genre)
- **hardstyle kick** (w1.0): distorted kick with tonal tail (kick_psy punch 18+ through fx_saturate drive 12; tail pitched to key) *(curated:claude/2026-07-03)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **riser throws** (w0.93): before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up) *(curated:claude/2026-07-02)*
- **supersaw uplift** (w0.86): trance: supersaw_fat layered octaves, long chords, cutoff rises 8-16 bars, sidechain pump throughout *(curated:claude/2026-07-03)*
- **gain staged saturation** (w0.79): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*

## Inherited from trance
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- four on floor: kick every beat; openhat on offbeat 8ths
- loudness recovery: FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims.

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
