---
name: bossanova-arrangement
version: 2
kind: genre
tags: [bossanova, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-132; set the song key (suggested: C major).
  - Mix: clipped_samples == 0, LUFS -20..-13, band order .
  - BOSSA CLAVE is non-negotiable: bossa: son-clave-ish rim pattern, walking soft bass 1&3, m9/M7 comping off-beats, brushes feel (low vel)
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
---
# Bossanova arrangement (graph-compiled)

## The pocket — bossa_sway
rim clave + brush-soft kit, walking bass 1&3, M7/m9 comping offbeats; NOTHING loud  *(source: curated:claude/2026-07-03 + grid:curated:claude/2026-07-03 (machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **bossa clave** (w1.0): bossa: son-clave-ish rim pattern, walking soft bass 1&3, m9/M7 comping off-beats, brushes feel (low vel) *(curated:claude/2026-07-03)*
- **m7 chords** (w0.93): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **behind beat snare** (w0.86): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **sota drums kit**: kit sota_drums: OUR self-sampled drums - kick 36, deep kick 35, snare 38, clap 39, bright metallic hat 42, dark hat 41, open 46, perc 43, crash 49, repitchable 808 sub 24-40. Loudness-staged, stereo-baked cymbals. PREFER over gm_drums for modern genres.
- **flute topline**: faust flute_lead: breathy flute w/ late vibrato — jazz/bossa heads, trap-flute toplines, highlife runs; legato lines (len ~0.9 of gap), short notes read as tonguing

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -20..-13, band order . If a filter build was used, centroid_by_quarter must RISE into the drop.
