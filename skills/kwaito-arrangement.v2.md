---
name: kwaito-arrangement
version: 2
kind: genre
tags: [kwaito, house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 95-112; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - SLOWED HOUSE BOUNCE is non-negotiable: house slowed to ~100-110 BPM: four-on-the-floor kick with a lazy, swung, half-speed-feeling bounce — the space and the slow-motion groove are the point
  - KWAITO DEEP BASSLINE is non-negotiable: a deep, simple, repeating synth/DX bassline (M1/DX7 era) locked to the kick — round sub, minimal notes, the low-end hook
  - M1 ORGAN STAB is non-negotiable: the Korg M1 'organ'/'piano' house stab: a bright plucky chord stab on the offbeats — the melodic signature of kwaito and its house lineage
---
# Kwaito arrangement (graph-compiled)

Kwaito is a child of **house** — its groove laws apply unless overridden below.

## The pocket — kwaito_bounce
Kwaito (~105 BPM, slowed-house bounce, swing ~55%): four-on-the-floor kick with a lazy half-speed feel, clap/snare on 2 & 4, loosely-swung offbeat hats; a deep simple synth bassline locked to the kick; a bright M1-organ chord stab on the offbeats; laid-back chanted township vocals riding the pocket. Space and slow-motion groove are the point. Swing 0.55 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **slowed house bounce** (w1.0): house slowed to ~100-110 BPM: four-on-the-floor kick with a lazy, swung, half-speed-feeling bounce — the space and the slow-motion groove are the point *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **kwaito deep bassline** (w0.92): a deep, simple, repeating synth/DX bassline (M1/DX7 era) locked to the kick — round sub, minimal notes, the low-end hook *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **m1 organ stab** (w0.84): the Korg M1 'organ'/'piano' house stab: a bright plucky chord stab on the offbeats — the melodic signature of kwaito and its house lineage *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **chanted township vocal** (w0.76): laid-back, repetitive chanted/spoken vocals in township slang, call-and-response, riding the pocket rather than singing over it *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **loose swing hats** (w0.68): offbeat hats with a loose human swing (not quantized) giving the slow groove its lilt and shuffle *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Inherited from house
- filter build: fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- four on floor: kick every beat; openhat on offbeat 8ths
- offbeat bass: bass hits on the 8th between kicks
- loudness recovery: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- groove ukg shuffle: THE pocket move: apply_groove(track='hats', groove='ukg_shuffle', amount=0.85) after writing on-grid hats - hard 16th swing + ghosted e/a. Quantized-dead hats fail this genre.
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- ...and from the house skill itself: phrase aligned blend, bass swap, filter transition, tempo map motion, curve shaped automation, vst factory presets, sentence phrase, one change per section, glue comp grip, cadence modal VII i, andalusian descent, singer songwriter schema, tonal ambiguity dual tonic, schema rotation, complementary eq unmask, unmask escalation ladder, sidechain unmask bass, acapella bridge, structure inheritance, auxiliary sections law, mono below 120, mono check law, mono sub stereo body, riser into drop, impact downbeat, seam connects law, downlifter drain, symbolic unmask, true peak safety, streaming loudness target, softclip pre limiter, inter sample headroom by genre, tension and release, section contrast, energy contour, strategic pause

## Sound recipes (this palette, these moves)
- **kwaito kit**: M1-organ/piano stab = organ_soul/hammond_organ on the offbeats; deep round bassline = sub_clean/bass_warm (DX7 character) locked to the kick; clap_909 + kick_808/kick_punch for the slowed-house kit; loose swing (not quantized).

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='house_shuffle', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (classic house ~56%: pushed e/a 16ths, offbeat-8th open-hat accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
