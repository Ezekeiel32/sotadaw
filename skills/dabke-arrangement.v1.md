---
name: dabke-arrangement
version: 1
kind: genre
tags: [dabke, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-140; set the song key (suggested: D Phrygian (Bayati/Hijaz)).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order mid>lowmid>low.
  - DABKE GALLOP is non-negotiable: the dabke derbouka gallop: DUM on 1 then a dum-tek gallop through the bar, tabl reinforcing, line-dance stomps on downbeats
  - ZURNA HIJAZ LEAD is non-negotiable: a piercing double-reed (zurna/mijwiz) lead wailing Hijaz/Bayati lines with trills and long holds — the outdoor-celebration voice
  - MELISMA MAQAM VOCAL is non-negotiable: melismatic vocal in Bayati/Hijaz color sliding between phrases — the raï cry, answered by a synth line
---
# Dabke arrangement (graph-compiled)

## The pocket — dabke_line
Dabke (~124 BPM): the derbouka gallop — DUM on 1, dum-tek galloping through (slots 0,3,4,7,8,11,12), tabl deep on 1&3, stomps on downbeats; the ZURNA wails Hijaz lines with trills over the line-dance drive; accelerate toward the end (tempoMap). Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*

## Techniques (weight order — the top ones DEFINE the genre)
- **dabke gallop** (w1.0): the dabke derbouka gallop: DUM on 1 then a dum-tek gallop through the bar, tabl reinforcing, line-dance stomps on downbeats *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **zurna hijaz lead** (w0.92): a piercing double-reed (zurna/mijwiz) lead wailing Hijaz/Bayati lines with trills and long holds — the outdoor-celebration voice *(curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md))*
- **melisma maqam vocal** (w0.84): melismatic vocal in Bayati/Hijaz color sliding between phrases — the raï cry, answered by a synth line *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **accelerando drive** (w0.76): a continuous tempo push toward a frenzied climax (encode as a tempoMap ramp), the band getting faster and hotter until the final hit *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **dabke party**: zurna lead (EXISTS — trills + long holds in Hijaz); derbouka = dhol tight + tick gallop; tabl = kick_punch deep; stomps = layered low hits on downbeats; Omar Souleyman electrified variant = add supersaw drone stabs

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order mid>lowmid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
