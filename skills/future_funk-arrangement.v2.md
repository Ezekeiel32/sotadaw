---
name: future_funk-arrangement
version: 2
kind: genre
tags: [future_funk, french_house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-128; set the song key (suggested: D minor (maj7 color)).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order mid>low>lowmid.
  - SAMPLE CHOP STAB is non-negotiable: chop a 70s/80s city-pop or disco record into short pitched STABS and re-sequence them into a new syncopated hook — the sampled chops are the melody
  - SIDECHAIN PUMP FF is non-negotiable: heavy sidechain compression ducking everything to the four-on-the-floor kick so the whole mix breathes/pumps on each beat — the French-house 'whomp'
  - FRENCH FILTER SWEEP is non-negotiable: an automated resonant band/low-pass filter opens across 8-16 bars into the drop (Daft-Punk 'filter house') — the build IS a filter sweep on the sampled loop
---
# Future_Funk arrangement (graph-compiled)

Future_Funk is a child of **french_house** — its groove laws apply unless overridden below.

## The pocket — chop_pump
Future funk (~120 BPM, 4/4, heavy sidechain): four-on-the-floor kick with the WHOLE mix pumping/ducking to it; claps on 2 & 4, offbeat open hats; chopped 70s/80s city-pop stabs re-sequenced as the syncopated hook (bright maj7/m9 color); an automated resonant filter opens across 8-16 bars into the drop; disco-string + supersaw stabs punctuate. Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **sample chop stab** (w1.0): chop a 70s/80s city-pop or disco record into short pitched STABS and re-sequence them into a new syncopated hook — the sampled chops are the melody *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **sidechain pump ff** (w0.92): heavy sidechain compression ducking everything to the four-on-the-floor kick so the whole mix breathes/pumps on each beat — the French-house 'whomp' *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **french filter sweep** (w0.84): an automated resonant band/low-pass filter opens across 8-16 bars into the drop (Daft-Punk 'filter house') — the build IS a filter sweep on the sampled loop *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **disco string stab** (w0.76): lush unison disco-string and brass stabs punctuate the groove; four-on-the-floor kick, offbeat open hats, claps on 2 & 4 *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **citypop maj7 color** (w0.68): bright maj7 / m9 city-pop harmony kept in the chops — sunny, nostalgic, slightly wistful chord color *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Inherited from french_house
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- tape saturation: heavy fx_saturate drive 8-14 over the whole beat bus = grit
- four floor disco: disco four-on-floor: live kick + open-hat on the offbeat 8ths + 16th hi-hat ride; strings/octave bass carry euphoria
- filter disco loop: french house: loop 2-4 bars of disco (or self-sampled equivalent) and RIDE a lowpass over 8-16 bars with sidechain pump — the filter ride IS the arrangement

## Sound recipes (this palette, these moves)
- **ff chops**: chopped city-pop sample stabs (use supersaw/strings_disco + pluck as synth stand-ins, or sample-chop a source) with heavy fx_pump sidechain to the kick; bass_warm French-house bass; strings_disco stabs; fx_djfilter/fx_filter sweep opening into the drop. Bright, glossy, pumping.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='disco_roll', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (subtle ~53% swing, offbeat-8th hat barks, strong quarter pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order mid>low>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
