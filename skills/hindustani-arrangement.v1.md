---
name: hindustani-arrangement
version: 1
kind: genre
tags: [hindustani, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 60-140; set the song key (suggested: D major (raga-modal)).
  - Mix: clipped_samples == 0, LUFS -16..-12, band order mid>lowmid>low.
  - TEENTAL 16 is non-negotiable: teental: a 16-beat cycle = one 16-slot bar; SAM (strongest) on slot 0, KHALI (empty — tabla skips the bass) on slot 8, claps 0/4/12 — the whole form breathes in 16s
  - TABLA THEKA BOLS is non-negotiable: the tabla theka speaks bols (dha dhin dhin dha ...): bass dagga strokes on the tali beats, dry treble ticks between, bass SILENT at khali
  - ALAP FREE INTRO is non-negotiable: alap: a free-time drumless raga exploration BEFORE the pulse enters — open every piece with a rubato drone+melody section
---
# Hindustani arrangement (graph-compiled)

## The pocket — teental_gat
Hindustani gat in teental (~96 BPM): the 16-beat cycle IS the 16-slot bar — SAM heavy on slot 0, tali marked at 4/12, KHALI at slot 8 (tabla bass SILENT there, ticks continue); sitar states the bandish, doubles into jhala; tanpura drone forever; open free (alap) before the theka enters.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **teental 16** (w1.0): teental: a 16-beat cycle = one 16-slot bar; SAM (strongest) on slot 0, KHALI (empty — tabla skips the bass) on slot 8, claps 0/4/12 — the whole form breathes in 16s *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **tabla theka bols** (w0.92): the tabla theka speaks bols (dha dhin dhin dha ...): bass dagga strokes on the tali beats, dry treble ticks between, bass SILENT at khali *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **alap free intro** (w0.84): alap: a free-time drumless raga exploration BEFORE the pulse enters — open every piece with a rubato drone+melody section *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **tanpura eternal drone** (w0.76): the tanpura tonic-fifth drone runs the ENTIRE piece — nothing modulates, the raga lives against the drone *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **melodic shadowing** (w0.68): the accompanying melody instrument SHADOWS the lead a moment behind, echoing each phrase — heterophony, not harmony *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Sound recipes (this palette, these moves)
- **hindustani trio**: sitar = pluck (bright, long ring, meend written as pitch-neighbor motion); tabla = dhol with the BEND zone for dagga speech + a dry tick lane (khali law: no bass at slot 8); tanpura_drone; alap first, theka enters late; never quantize the lead hard

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -16..-12, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
