---
name: chimurenga-arrangement
version: 2
kind: genre
tags: [chimurenga, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-130; set the song key (suggested: A minor (mbira wheel)).
  - Mix: clipped_samples == 0, LUFS -14..-11, band order mid>lowmid>low.
  - MBIRA KUSHAURA KUTSINHIRA is non-negotiable: two interlocking mbira parts: kushaura leads, kutsinhira answers OFFSET (a pulse behind/ahead) — together they weave the wheel; write two kalimba tracks offset
  - HOSHO TRIPLET DRIVE is non-negotiable: the hosho shaker drives the 3-pulse (12/8) with a sharp chick on each group — the clave of chimurenga
  - FOUR PHRASE WHEEL is non-negotiable: the harmony is a 4-phrase wheel (48-pulse cycles, the i-VII-VI-VII family) that turns forever — form = texture change over the wheel
---
# Chimurenga arrangement (graph-compiled)

## The pocket — mbira_wheel
Chimurenga (~120 BPM, 12/8 — swing 0.66 approximates the triplet wheel): TWO kalimba (mbira) parts interlock — kushaura leads, kutsinhira answers offset; the hosho shaker chicks the 3-pulse; kick breathes 1 & the 4th triplet group; the 4-phrase harmonic wheel (i-VII-VI-VII family) turns forever; texture evolves, the wheel never stops. Swing 0.66 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude (genre-expansion wave) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **mbira kushaura kutsinhira** (w1.0): two interlocking mbira parts: kushaura leads, kutsinhira answers OFFSET (a pulse behind/ahead) — together they weave the wheel; write two kalimba tracks offset *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **hosho triplet drive** (w0.92): the hosho shaker drives the 3-pulse (12/8) with a sharp chick on each group — the clave of chimurenga *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **four phrase wheel** (w0.84): the harmony is a 4-phrase wheel (48-pulse cycles, the i-VII-VI-VII family) that turns forever — form = texture change over the wheel *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **hypnotic repetition** (w0.76): an identical bar cycled for minutes to induce trance — the variation lives in the TEXTURE on top (krautrock, black metal, stoner, doom) *(curated:claude/2026-07-06 (bands+jazz wave, session genre-forge; deep-research DNA, sources in docs/research_bands_jazz_sota.md))*

## Sound recipes (this palette, these moves)
- **mbira pair**: TWO kalimba tracks (kushaura + kutsinhira OFFSET by a pulse — write the second track shifted); hosho = hat triplet chicks; soft kit underneath; guitar may double the mbira line (pluck); hypnotic — let the wheel turn 16+ cycles

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='afro_lilt', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (afrobeats/afro-house anticipation: pushed a-of-beat, 3-2 bell lean))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-11, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
