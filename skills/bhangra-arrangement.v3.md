---
name: bhangra-arrangement
version: 3
kind: genre
tags: [bhangra, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 90-165; set the song key (suggested: G major (club: minor)).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order lowmid>low>mid.
  - CHAAL RHYTHM is non-negotiable: the dhol CHAAL: Dha-Na-Na-Na / Na-Dha-Dha-Dha — the bass 'dagga' head hits the downbeat + push while the treble 'tilli' stick fills the eighths; THE bhangra pulse
  - DHOL DAGGA TILLI is non-negotiable: the double-headed dhol: a deep bass 'dagga' side (booming, pitch-dropping) + a bright thin 'tilli' side (fast ticking treble) — program them as two separate percussion voices
  - TUMBI RIFF is non-negotiable: the tumbi: a single high-pitched string plucked as a fast repeating ostinato riff — the piercing melodic hook that says 'bhangra' instantly
---
# Bhangra arrangement (graph-compiled)

## The pocket — dhol_chaal
The dhol CHAAL (4/4, ~100 BPM straight): bass 'dagga' on the downbeat + a push (slots 0,3,8,11), bright 'tilli' treble ticking the eighths, a piercing tumbi ostinato riff on top; modern club bhangra lays a four-on-the-floor kick + synth bass UNDER the acoustic dhol for dancefloor weight; boliyan call-response vocals.  *(source: curated:claude (genre-expansion/world waves) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **chaal rhythm** (w1.0): the dhol CHAAL: Dha-Na-Na-Na / Na-Dha-Dha-Dha — the bass 'dagga' head hits the downbeat + push while the treble 'tilli' stick fills the eighths; THE bhangra pulse *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **dhol dagga tilli** (w0.92): the double-headed dhol: a deep bass 'dagga' side (booming, pitch-dropping) + a bright thin 'tilli' side (fast ticking treble) — program them as two separate percussion voices *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **tumbi riff** (w0.84): the tumbi: a single high-pitched string plucked as a fast repeating ostinato riff — the piercing melodic hook that says 'bhangra' instantly *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **boliyan call response** (w0.76): call-and-response folk vocals (boliyan) traded over the groove; hooky, chant-like, energetic *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **four on floor club layer** (w0.68): modern UK/club bhangra lays a four-on-the-floor kick + synth bass UNDER the acoustic dhol/tumbi — folk on a dancefloor engine *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **dhol**: faust dhol: THE dagga (bass head) — deep booming membrane with the STRONG strike pitch-drop (knobs: decay, bend, slap). Pair it with a tight snare/hat tick as the 'tilli' treble head so the chaal reads as two hands.
- **tumbi**: tumbi = a single bright high plucked string (pluck) as a fast repeating ostinato — the instant-bhangra hook; dholak/tabla for the acoustic bed

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='shuffle_blues', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (66% shuffle — deeper than jazz_swing's 64%, heavy backbeat))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
