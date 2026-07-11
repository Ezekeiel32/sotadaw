---
name: benga-arrangement
version: 1
kind: genre
tags: [benga, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-140; set the song key (suggested: D major).
  - Mix: clipped_samples == 0, LUFS -12..-9, band order lowmid>mid>low.
  - BENGA RUNNING BASS is non-negotiable: THE benga marker: the bass GALLOPS — fast melodic running lines (nyatiti-derived) that lead the band like a second guitar; write the bassline as a melody, not roots
  - PARALLEL THIRDS VOCAL is non-negotiable: verses sung in sweet parallel thirds — two voices moving together
  - DRY SNAP KIT is non-negotiable: a dry, tight, snappy kit — no reverb wash; the speed needs air
---
# Benga arrangement (graph-compiled)

## The pocket — benga_gallop
Benga (~124 BPM): THE BASS LEADS — a galloping melodic running bassline (nyatiti-derived) written as a melody; bright interlocking guitars answer; light four-square kick, dry snappy snare 2&4; major I-IV-V at speed; vocals in parallel thirds. ⚠BPM range flagged for eval verification.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **benga running bass** (w1.0): THE benga marker: the bass GALLOPS — fast melodic running lines (nyatiti-derived) that lead the band like a second guitar; write the bassline as a melody, not roots *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **parallel thirds vocal** (w0.92): verses sung in sweet parallel thirds — two voices moving together *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **dry snap kit** (w0.84): a dry, tight, snappy kit — no reverb wash; the speed needs air *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **interlocking guitars** (w0.76): three guitars in distinct registers (lead, mi-solo mid, rhythm) weave complementary cyclic riffs — no one plays chords, the interlock is the harmony *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **benga band**: the bass = bass_warm playing MELODIC running lines (walking style, fast); two bright plucks interlocking; DRY snappy kit (no wash); sunny, fast, guitar-forward

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
