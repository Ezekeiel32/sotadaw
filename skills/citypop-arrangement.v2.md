---
name: citypop-arrangement
version: 2
kind: genre
tags: [citypop, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 100-115; set the song key (suggested: Ab major).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order lowmid>low>mid.
  - MAJ7 GLOSS is non-negotiable: citypop/yacht harmony: maj7/9 chords, chorused clean keys/guitar, walking disco bass — glossy nostalgia; brightness lives in the chord color not the master EQ
  - DOTTED8 DELAY is non-negotiable: delay time = 45000/bpm*1.5 ms, feedback <=0.45, on leads
  - OFFBEAT BASS is non-negotiable: bass hits on the 8th between kicks
---
# Citypop arrangement (graph-compiled)

## The pocket — citypop_gloss
citypop loop DNA (wave16)  *(source: curated:claude/2026-07-04 + grid:curated (wave16 machine-readable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **maj7 gloss** (w0.95): citypop/yacht harmony: maj7/9 chords, chorused clean keys/guitar, walking disco bass — glossy nostalgia; brightness lives in the chord color not the master EQ *(curated:claude/2026-07-03)*
- **dotted8 delay** (w0.6): delay time = 45000/bpm*1.5 ms, feedback <=0.45, on leads *(skill:fx-usage@v1)*
- **offbeat bass** (w0.6): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **tape saturation** (w0.5): heavy fx_saturate drive 8-14 over the whole beat bus = grit *(curated:claude/2026-07-02)*
- **gated reverb snare** (w0.5): big snare through short bright reverb (mix 0.4-0.5, small size) — 80s exception to the dry-drums law *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **solina strings**: faust strings_disco: detuned saw ensemble through dual LFO chorus, slow attack — octave pads for disco euphoria, swells into choruses

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order lowmid>low>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
