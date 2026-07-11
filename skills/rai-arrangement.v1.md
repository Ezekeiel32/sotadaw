---
name: rai-arrangement
version: 1
kind: genre
tags: [rai, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-130; set the song key (suggested: E Phrygian (Bayati color)).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - DERBOUKA DUM TEK is non-negotiable: derbouka engine: deep DUM on 1 and the and-of-2, dry TEK splashes on the offbeats, bendir frame-drum roll under — the Maghreb pocket
  - MELISMA MAQAM VOCAL is non-negotiable: melismatic vocal in Bayati/Hijaz color sliding between phrases — the raï cry, answered by a synth line
  - POP RAI SYNTH STAB is non-negotiable: cheap bright 80s synth stabs + string-machine pads riding the derbouka — the Oran cabaret-to-club sound
---
# Rai arrangement (graph-compiled)

## The pocket — rai_pocket
Raï (~116 BPM): derbouka engine — deep DUM on 1 and the and-of-2 (slot 6), dry TEK splashing offbeats, bendir roll under; 80s pop-raï synth stabs answer the melismatic Bayati/Hijaz vocal; modern raï lays a four-floor kick beneath the derbouka. Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **derbouka dum tek** (w1.0): derbouka engine: deep DUM on 1 and the and-of-2, dry TEK splashes on the offbeats, bendir frame-drum roll under — the Maghreb pocket *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **melisma maqam vocal** (w0.92): melismatic vocal in Bayati/Hijaz color sliding between phrases — the raï cry, answered by a synth line *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **pop rai synth stab** (w0.84): cheap bright 80s synth stabs + string-machine pads riding the derbouka — the Oran cabaret-to-club sound *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **four on floor club layer** (w0.76): modern UK/club bhangra lays a four-on-the-floor kick + synth bass UNDER the acoustic dhol/tumbi — folk on a dancefloor engine *(curated:claude/2026-07-06 (coverage-expansion wave, session genre-scout; deep-research DNA + adversarial verify, sources in docs/research_genre_expansion_sota.md))*

## Sound recipes (this palette, these moves)
- **rai rig**: derbouka = dhol tight (dum) + tick lane (tek); synth stabs = supersaw/accordion bright; strings pads; the vocal line slides between phrases (write chromatic approach bends); modern layer = kick_punch four-floor

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
