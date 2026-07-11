---
name: carnatic-arrangement
version: 1
kind: genre
tags: [carnatic, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-120; set the song key (suggested: C major (shankarabharanam)).
  - Mix: clipped_samples == 0, LUFS -16..-12, band order mid>lowmid>low.
  - GAMAKA ORNAMENT is non-negotiable: Carnatic gamaka: pitches OSCILLATE — write melodies as neighbor-note oscillations around the target tone, never plain held notes
  - ADI TALA CYCLE is non-negotiable: adi tala: an 8-beat cycle (2 bars of 4/4) with the cadence (korvai) landing on beat 1 of the NEXT cycle — phrase across the barline, resolve on sam
  - MELODIC SHADOWING is non-negotiable: the accompanying melody instrument SHADOWS the lead a moment behind, echoing each phrase — heterophony, not harmony
---
# Carnatic arrangement (graph-compiled)

## The pocket — adi_tala
Carnatic (adi tala: 8-beat cycle = 2 bars 4/4, ~84 BPM): mridangam theka — bass strokes anchor beats 1/5/7 with dry ticks between; NO backbeat; the melody OSCILLATES (gamaka) around raga tones over the tanpura drone; violin/flute shadows a beat behind; cadences (korvai) land on the NEXT cycle's beat 1.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **gamaka ornament** (w1.0): Carnatic gamaka: pitches OSCILLATE — write melodies as neighbor-note oscillations around the target tone, never plain held notes *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **adi tala cycle** (w0.92): adi tala: an 8-beat cycle (2 bars of 4/4) with the cadence (korvai) landing on beat 1 of the NEXT cycle — phrase across the barline, resolve on sam *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **melodic shadowing** (w0.84): the accompanying melody instrument SHADOWS the lead a moment behind, echoing each phrase — heterophony, not harmony *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **tanpura eternal drone** (w0.76): the tanpura tonic-fifth drone runs the ENTIRE piece — nothing modulates, the raga lives against the drone *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **alap free intro** (w0.68): alap: a free-time drumless raga exploration BEFORE the pulse enters — open every piece with a rubato drone+melody section *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Sound recipes (this palette, these moves)
- **carnatic ensemble**: Carnatic flute (flute_lead) or veena (pluck, long ring) with gamaka written as neighbor-note oscillation; mridangam = dhol (low, short) + tick lane; tanpura_drone eternal; open with a FREE drumless alap section; room-intimate, very dynamic

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-12, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
