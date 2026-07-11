---
name: acid_house-arrangement
version: 1
kind: genre
tags: [acid_house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 118-128; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - ACID SQUELCH LEAD is non-negotiable: resonant 303-style line (acid303), cutoff automated per phrase, res 2-4; THE lead voice
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - JACK GROOVE is non-negotiable: chicago house: the raw 909 JACK — swung 16th hats against a pumping 4-floor, off-kilter clap placement, one vamping bass/organ riff; imperfection is the funk
---
# Acid_House arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **acid squelch lead** (w0.95): resonant 303-style line (acid303), cutoff automated per phrase, res 2-4; THE lead voice *(curated:claude/2026-07-02)*
- **four on floor** (w0.9): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **jack groove** (w0.8): chicago house: the raw 909 JACK — swung 16th hats against a pumping 4-floor, off-kilter clap placement, one vamping bass/organ riff; imperfection is the funk *(curated:claude/2026-07-03-w11)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
