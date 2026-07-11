---
name: mor_lam-arrangement
version: 2
kind: genre
tags: [mor_lam, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-145; set the song key (suggested: G major (pentatonic)).
  - Mix: clipped_samples == 0, LUFS -12..-9, band order mid>lowmid>low.
  - KHAEN DRONE RIFF is non-negotiable: the khaen mouth organ holds chordal drones AND riffs simultaneously (free-reed clusters) — sustained harmonica-family chords driving the lam
  - PHIN INTERLOCK is non-negotiable: the phin lute picks a bright cyclic pentatonic riff interlocking with the khaen — Isan's twin engine
  - LAM SPEECH SONG is non-negotiable: lam vocal: rapid semi-spoken pentatonic patter that resolves to sung tones at phrase ends
---
# Mor_Lam arrangement (graph-compiled)

## The pocket — lam_drive
Mor lam (~126 BPM drive): kick four-square-ish (1, 3, 3.5), snare 2&4, light running hats; the KHAEN (mouth organ) holds chordal drone-riffs while the phin lute picks a bright pentatonic interlock; lam vocal = rapid speech-song resolving to sung tones. [BPM verified inline 2026-07-06, see doc addendum.] Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **khaen drone riff** (w1.0): the khaen mouth organ holds chordal drones AND riffs simultaneously (free-reed clusters) — sustained harmonica-family chords driving the lam *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **phin interlock** (w0.92): the phin lute picks a bright cyclic pentatonic riff interlocking with the khaen — Isan's twin engine *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **lam speech song** (w0.84): lam vocal: rapid semi-spoken pentatonic patter that resolves to sung tones at phrase ends *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **dry snap kit** (w0.76): a dry, tight, snappy kit — no reverb wash; the speed needs air *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Sound recipes (this palette, these moves)
- **isan engine**: khaen = harmonica (free-reed twin) holding chord drones + riffs; phin = pluck bright cyclic pentatonic; dry snappy kit; modern lam sing = hotter, add bass_warm driving

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-9, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
