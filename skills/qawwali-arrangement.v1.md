---
name: qawwali-arrangement
version: 1
kind: genre
tags: [qawwali, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 70-140; set the song key (suggested: D major (raga-modal)).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order lowmid>mid>low.
  - QAWWALI TAKRAR is non-negotiable: ecstatic REPETITION: the hook phrase repeats and intensifies (takrar) while the lead inserts girah (couplets) and sargam runs — the arc climbs in waves, never resets
  - PARTY CLAP RESPONSE is non-negotiable: the qawwali party claps HARD on 2 & 4 and answers every lead phrase in unison — call-and-response as the engine
  - HARMONIUM SHADOW is non-negotiable: the harmonium doubles the vocal line in real time (slightly behind, ornamented) over a tonic drone — melody and accompaniment are ONE voice
---
# Qawwali arrangement (graph-compiled)

## The pocket — qawwali_arc
Qawwali (~104 BPM rising, keherwa-family 4/4, swing ~0.54): tabla/dholak bass on 1 + the pickup, dry ticks between; the PARTY claps HARD on 2&4; harmonium shadows the vocal over an eternal tanpura drone; the hook repeats and INTENSIFIES (takrar) — build with tempoMap acceleration and layer-adds, never reset. Swing 0.54 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Techniques (weight order — the top ones DEFINE the genre)
- **qawwali takrar** (w1.0): ecstatic REPETITION: the hook phrase repeats and intensifies (takrar) while the lead inserts girah (couplets) and sargam runs — the arc climbs in waves, never resets *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **party clap response** (w0.92): the qawwali party claps HARD on 2 & 4 and answers every lead phrase in unison — call-and-response as the engine *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **harmonium shadow** (w0.84): the harmonium doubles the vocal line in real time (slightly behind, ornamented) over a tonic drone — melody and accompaniment are ONE voice *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **accelerating arc** (w0.76): the performance accelerates across sections (tempoMap ramps ~70 -> ~140) with intensity, not a fixed tempo *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*
- **tanpura eternal drone** (w0.68): the tanpura tonic-fifth drone runs the ENTIRE piece — nothing modulates, the raga lives against the drone *(curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies))*

## Sound recipes (this palette, these moves)
- **qawwali party**: harmonium = accordion shadowing the lead melody; tabla/dholak = dhol (bass, bend for the dagga) + tight tick snare; claps STACKED (clap_909 layered, human-loose) on 2&4; tanpura_drone under everything; build = tempoMap ramp + adding clap/voice layers

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
