---
name: morna-arrangement
version: 1
kind: genre
tags: [morna, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 55-90; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -18..-13, band order lowmid>mid>low.
  - SODADE BALLAD LILT is non-negotiable: morna's habanera-leaning lilt: the bass leans on 1 and the and-of-2, arpeggios fill — unhurried, the voice sits BEHIND the beat
  - CAVAQUINHO VIOLAO WEAVE is non-negotiable: cavaquinho (bright, high strums/arpeggios) weaves over violao (fingered arpeggios + bassline) — the two-guitar morna bed
  - DIMINISHED PASSING COLOR is non-negotiable: minor ii-V-i motion sweetened with chromatic passing diminished chords — the sodade harmonic signature
---
# Morna arrangement (graph-compiled)

## The pocket — sodade
Morna (~68 BPM, habanera-leaning lilt, essentially percussionless): violao lays fingered arpeggios + a soft bass leaning on 1 and the and-of-2; cavaquinho weaves bright arpeggios above; minor ii-V-i with chromatic passing diminished color; the voice sits BEHIND the beat (rubato). Drumless grid (fado precedent). Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **sodade ballad lilt** (w1.0): morna's habanera-leaning lilt: the bass leans on 1 and the and-of-2, arpeggios fill — unhurried, the voice sits BEHIND the beat *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **cavaquinho violao weave** (w0.92): cavaquinho (bright, high strums/arpeggios) weaves over violao (fingered arpeggios + bassline) — the two-guitar morna bed *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **diminished passing color** (w0.84): minor ii-V-i motion sweetened with chromatic passing diminished chords — the sodade harmonic signature *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **saudade rubato** (w0.76): the voice sings with expressive RUBATO (pulling and pushing the tempo, held phrase-ends) over a steady accompaniment — longing (saudade) made rhythmic freedom *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*
- **percussionless intimacy** (w0.68): NO drums: the pulse lives entirely in the strummed viola and the singer's phrasing; arrangement is voice + two guitars, intimate and dynamic *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **morna duo**: violao = pluck2 fingered arpeggios + bassline; cavaquinho = pluck bright above; upright_bass soft; accordion/violin color answering the voice; intimate room, very dynamic, voice behind the beat (never quantize)

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -18..-13, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
