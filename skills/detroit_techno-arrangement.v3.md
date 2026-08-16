---
name: detroit_techno-arrangement
version: 3
kind: genre
tags: [detroit_techno, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 120-135; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order low>lowmid>mid.
  - DETROIT STRINGS is non-negotiable: detroit techno: hi-tech soul — minor 9th/11th STRING-machine stabs over machine funk; melancholy chords, futurist optimism; the strings answer the bassline
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
---
# Detroit_Techno arrangement (graph-compiled)

## The pocket — detroit_pulse
detroit_techno loop DNA (wave14)  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **detroit strings** (w0.95): detroit techno: hi-tech soul — minor 9th/11th STRING-machine stabs over machine funk; melancholy chords, futurist optimism; the strings answer the bassline *(curated:claude/2026-07-03-w11)*
- **four on floor** (w0.85): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **m7 chords** (w0.6): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **electro boogie** (w0.6): Detroit/Miami electro: 808 boogie syncopation, crisp machine snares on 2+4 with syncopated claps, vocoder hooks — robotic funk, no 4-floor *(curated:claude/2026-07-03)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='house_shuffle', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (classic house ~56%: pushed e/a 16ths, offbeat-8th open-hat accents))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
