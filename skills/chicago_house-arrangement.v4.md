---
name: chicago_house-arrangement
version: 4
kind: genre
tags: [chicago_house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 118-126; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -11..-8, band order low>lowmid>mid.
  - JACK GROOVE is non-negotiable: chicago house: the raw 909 JACK — swung 16th hats against a pumping 4-floor, off-kilter clap placement, one vamping bass/organ riff; imperfection is the funk
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - OFFBEAT BASS is non-negotiable: bass hits on the 8th between kicks
---
# Chicago_House arrangement (graph-compiled)

## The pocket — chicago_jack
chicago_house loop DNA (wave15) Swing 0.53 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## Techniques (weight order — the top ones DEFINE the genre)
- **jack groove** (w0.95): chicago house: the raw 909 JACK — swung 16th hats against a pumping 4-floor, off-kilter clap placement, one vamping bass/organ riff; imperfection is the funk *(curated:claude/2026-07-03-w11)*
- **four on floor** (w0.9): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **offbeat bass** (w0.7): bass hits on the 8th between kicks *(skill:house-arrangement@v1)*
- **vocal chops** (w0.5): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='house_shuffle', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (classic house ~56%: pushed e/a 16ths, offbeat-8th open-hat accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -11..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
