---
name: eurodance-arrangement
version: 2
kind: genre
tags: [eurodance, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 130-140; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - PIANO HOUSE STAB is non-negotiable: rave/eurodance piano: octave-doubled minor piano stabs on the offbeats (M1-organ lineage), 8-bar hooks, verse rap / sung chorus contrast
  - OFFBEAT BASS is non-negotiable: bass hits on the 8th between kicks
---
# Eurodance arrangement (graph-compiled)

## The pocket — eurodance_stomp
4-floor stomp, offbeat opens, clap 2&4  *(source: curated:claude/2026-07-03-patterns-w2 (executable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **four on floor** (w0.9): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **piano house stab** (w0.9): rave/eurodance piano: octave-doubled minor piano stabs on the offbeats (M1-organ lineage), 8-bar hooks, verse rap / sung chorus contrast *(curated:claude/2026-07-03-w6)*
- **offbeat bass** (w0.7): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **supersaw pads** (w0.7): wide detuned saw chords, whole/half notes, fx_widen — the neon wall *(curated:claude/2026-07-02)*
- **riser throws** (w0.6): before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up) *(curated:claude/2026-07-02)*

## Sound recipes (this palette, these moves)
- **pluck zones**: pluck knobs: decay 0.05-2s (squared env - snappy), color 1-12 (pitch-tracking LP multiple: 2 = dark koto, 10 = open). Dance plucks = color 6-8 decay 0.3; automate color rising into a drop.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
