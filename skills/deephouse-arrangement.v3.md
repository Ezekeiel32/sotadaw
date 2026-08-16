---
name: deephouse-arrangement
version: 3
kind: genre
tags: [deephouse, house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 118-124; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -13..-8, band order low>lowmid>mid.
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - CHOPPED CHORDS is non-negotiable: short m7/9 chord stabs (0.2-0.4 beats) on syncopated 16ths, filtered warm
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
---
# Deephouse arrangement (graph-compiled)

Deephouse is a child of **house** — its groove laws apply unless overridden below.

## The pocket — deep_shuffle
deephouse loop DNA (wave15) Swing 0.56 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## Techniques (weight order — the top ones DEFINE the genre)
- **four on floor** (w0.9): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **chopped chords** (w0.9): short m7/9 chord stabs (0.2-0.4 beats) on syncopated 16ths, filtered warm *(curated:claude/2026-07-02)*
- **m7 chords** (w0.85): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **shuffle swing** (w0.7): hard 16th swing 0.60-0.66 with ghost hats in the gaps — the UKG lilt *(curated:claude/2026-07-02)*
- **send reverb** (w0.6): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*

## Inherited from house
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- offbeat bass: bass hits on the 8th between kicks
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- groove ukg shuffle: THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre.
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- phrase aligned blend: transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases
- ...and from the house skill itself: bass swap, filter transition, tempo map motion, curve shaped automation, vst factory presets, sentence phrase, one change per section, glue comp grip, cadence modal VII i, andalusian descent, singer songwriter schema, tonal ambiguity dual tonic, schema rotation, complementary eq unmask, unmask escalation ladder, sidechain unmask bass, acapella bridge, structure inheritance, auxiliary sections law, mono below 120, mono check law, mono sub stereo body, riser into drop, impact downbeat, seam connects law, downlifter drain, symbolic unmask, true peak safety, streaming loudness target, softclip pre limiter, inter sample headroom by genre, tension and release, section contrast, energy contour, strategic pause

## Sound recipes (this palette, these moves)
- **dh organ stab**: VA organ-stab color (M1-organ lineage); TAL bright-VA lane

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='house_shuffle', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (classic house ~56%: pushed e/a 16ths, offbeat-8th open-hat accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
