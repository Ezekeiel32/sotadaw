---
name: hardstyle-arrangement
version: 6
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
kick IS the bass (tonal tail); offbeat screech leads; halftime breakdowns  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending))*

## Techniques (weight order — the top ones DEFINE the genre)
- **hardstyle kick** (w1.0): distorted kick with tonal tail (kick_psy punch 18+ through fx_saturate drive 12; tail pitched to key) *(curated:claude/2026-07-03)*
- **brickwall mastering** (w0.97): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **riser throws** (w0.93): before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up) *(curated:claude/2026-07-02)*
- **supersaw uplift** (w0.86): trance: supersaw_fat layered octaves, long chords, cutoff rises 8-16 bars, sidechain pump throughout *(curated:claude/2026-07-03)*
- **loudness recovery** (w0.85): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **gain staged saturation** (w0.79): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*

## Inherited from trance
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- four on floor: kick every beat; openhat on offbeat 8ths
- groove psy straight: apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape.
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- phrase aligned blend: transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases
- bass swap: ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat
- filter transition: fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter
- ...and from the trance skill itself: tempo map motion, curve shaped automation, vst factory presets, vst fx presets, synth param maps, sentence phrase, pedal point, long form patience, one change per section, filter journey layers, one root lattice, glue comp grip, bass hp discipline, cadence modal VII i, singer songwriter schema, tonal ambiguity dual tonic, sidechain unmask bass, mono check law, mid side width control, haas caution, riser into drop, impact downbeat, seam connects law, downlifter drain, symbolic unmask, tension and release, section contrast, energy contour, strategic pause

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='techno_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
