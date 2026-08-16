---
name: balkan_brass-arrangement
version: 2
kind: genre
tags: [balkan_brass, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-210; set the song key (suggested: D Phrygian dominant (Hijaz)).
  - Mix: clipped_samples == 0, LUFS -11..-7, band order mid>lowmid>low.
  - AKSAK METER is non-negotiable: asymmetric 'limping' meter: 9/8 as 2+2+2+3 (cocek), 7/8 as 2+2+3, 11/8 as 2+2+2+2+3; accents on each subgroup head so the closing long '3' cell gives the trademark stumble
  - HIJAZ RUN is non-negotiable: a Phrygian-dominant / Hijaz melodic run (1 b2 3 4 5 b6 b7, augmented 2nd between b2 and 3) tremolo-ornamented with grace notes, mordents and chromatic slides
  - OOM PAH ENGINE is non-negotiable: tuba 'oom' on each aksak cell downbeat + alto/tenor horns chugging offbeat 'pah' chords between — the relentless propulsion under the trumpet
---
# Balkan_Brass arrangement (graph-compiled)

## The pocket — aksak_oompah
Balkan brass (aksak 9/8 as 2+2+2+3 approximated on a driving 4/4 read, ~140 BPM): tuba 'oom' on each cell downbeat, horns chug offbeat 'pah', davul booms the cell heads + snare cracks, a virtuoso trumpet tears a Hijaz (Phrygian-dominant) run on top; band answers each phrase with a tutti stab; the whole thing accelerates. [encode true 9/8 via section time-sig / tempoMap; add an accelerando ramp for the climax.]  *(source: curated:claude (genre-expansion/world-grid waves; see tools/kg_seed_genre_expansion.py + kg_seed_meter.py) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **aksak meter** (w1.0): asymmetric 'limping' meter: 9/8 as 2+2+2+3 (cocek), 7/8 as 2+2+3, 11/8 as 2+2+2+2+3; accents on each subgroup head so the closing long '3' cell gives the trademark stumble *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **hijaz run** (w0.92): a Phrygian-dominant / Hijaz melodic run (1 b2 3 4 5 b6 b7, augmented 2nd between b2 and 3) tremolo-ornamented with grace notes, mordents and chromatic slides *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **oom pah engine** (w0.84): tuba 'oom' on each aksak cell downbeat + alto/tenor horns chugging offbeat 'pah' chords between — the relentless propulsion under the trumpet *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **davul boom** (w0.76): the double-headed davul: heavy beater booms the head of each cell (deep pitched sine, fast pitch-drop) + a thin switch ticks the offbeats and the long '3' cell *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **brass tutti answer** (w0.68): the full band answers the solo trumpet's phrase with a harmonized fortissimo tutti stab — call-and-response as arrangement *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **accelerando drive** (w0.6): a continuous tempo push toward a frenzied climax (encode as a tempoMap ramp), the band getting faster and hotter until the final hit *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **overblown brass**: bright brash overblown brass: brass_stab/cine_brass/sax_section detuned-stacked for the ensemble mass, driven with fx_saturate (more drive = more overblown upper partials), bandpass ~1.2 kHz brass formant + 2-4 kHz air; the reedy lead can use `zurna`. Tuba = bass_warm octave-down staccato. Finish with tape saturation + light room.
- **davul**: davul boom = a pitched sine 55-90 Hz with a fast pitch-drop (hardkick/timpani) + a noise-burst switch tick (hat)

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-7, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
