---
name: rebetiko-arrangement
version: 2
kind: genre
tags: [rebetiko, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-130; set the song key (suggested: D Phrygian (Ousak)).
  - Mix: clipped_samples == 0, LUFS -15..-11, band order mid>lowmid>low.
  - ZEIBEKIKO 9 4 is non-negotiable: THE rebetiko meter: zeibekiko 9/4 felt as 2+2+2+3 (the aksak family) at a heavy ~60-90 — a solo man's slow limping dance; encode via section time-sig/tempoMap, accent the long cell
  - BOUZOUKI TREMOLO DROMOI is non-negotiable: double-course bouzouki tremolo lead in the dromoi (Hijaz, Ousak=Phrygian, Rast) with taximi (free rubato intro) before the song
  - BAGLAMAS CHIRP is non-negotiable: the tiny baglamas doubles the bouzouki an octave up, chirping offbeat chords
---
# Rebetiko arrangement (graph-compiled)

## The pocket — zeibekiko
Rebetiko zeibekiko (9/4 as 2+2+2+3 — the aksak cousin — at a heavy ~72; the 16-grid approximates one 9/4 bar, accent the cell heads and give the last cell its extra length via the final quarter): bouzouki tremolo leads in Ousak/Hijaz dromoi, baglamas chirps offbeat octaves, one guitar chugs i-V; open with a free taximi. Hasapiko variant = straight 2/4 ~120.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies) +2 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **zeibekiko 9 4** (w1.0): THE rebetiko meter: zeibekiko 9/4 felt as 2+2+2+3 (the aksak family) at a heavy ~60-90 — a solo man's slow limping dance; encode via section time-sig/tempoMap, accent the long cell *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **bouzouki tremolo dromoi** (w0.92): double-course bouzouki tremolo lead in the dromoi (Hijaz, Ousak=Phrygian, Rast) with taximi (free rubato intro) before the song *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **baglamas chirp** (w0.84): the tiny baglamas doubles the bouzouki an octave up, chirping offbeat chords *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **saudade rubato** (w0.76): the voice sings with expressive RUBATO (pulling and pushing the tempo, held phrase-ends) over a steady accompaniment — longing (saudade) made rhythmic freedom *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **rebetiko trio**: bouzouki = pluck2 double-course tremolo (write tremolo as repeated 16ths) in Hijaz/Ousak; baglamas = pluck octave up, offbeat chirps; viola-strum guitar chugs; intimate taverna room, very dynamic; encode TRUE 9/4 via section time-sig/tempoMap

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -15..-11, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
