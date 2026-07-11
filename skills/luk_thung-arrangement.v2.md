---
name: luk_thung-arrangement
version: 2
kind: genre
tags: [luk_thung, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-110; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -13..-10, band order lowmid>mid>low.
  - LUKTHUNG CROON BEND is non-negotiable: luk thung vocal: crooned country phrasing with deep note-bending vibrato (luk khrua) over langorous two-chord minor vamps
  - UPBEAT BRASS STAB is non-negotiable: brass/organ stabs on the upbeats push the sway — Thai country's backbeat shimmer
  - DORIAN MIN7 VAMP is non-negotiable: Dorian min7/min9 two-chord vamps (i7-IV7) — funk harmony smoothed for the roller rink
---
# Luk_Thung arrangement (graph-compiled)

## The pocket — lukthung_sway
Luk thung (~88 BPM sway): kick 1&3, snare soft 2&4, brass/organ stabs on the UPBEATS; a langorous two-chord minor vamp; the crooned lead bends deep into notes (write approach-note slides); string pads swell behind. [BPM verified inline 2026-07-06, see doc addendum.]  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **lukthung croon bend** (w1.0): luk thung vocal: crooned country phrasing with deep note-bending vibrato (luk khrua) over langorous two-chord minor vamps *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **upbeat brass stab** (w0.92): brass/organ stabs on the upbeats push the sway — Thai country's backbeat shimmer *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **dorian min7 vamp** (w0.84): Dorian min7/min9 two-chord vamps (i7-IV7) — funk harmony smoothed for the roller rink *(curated:claude/2026-07-06 (coverage-expansion wave 2, session genre-scout; researched + adversarially verified, sources in docs/research_genre_expansion_w2.md))*

## Sound recipes (this palette, these moves)
- **lukthung band**: crooning lead = flute_lead/pluck with slow approach bends; organ_soul + brass_stab upbeat stabs; strings_disco pads; warm vintage master, dynamic

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -13..-10, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
