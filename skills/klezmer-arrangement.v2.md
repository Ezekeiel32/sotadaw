---
name: klezmer-arrangement
version: 2
kind: genre
tags: [klezmer, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 110-140; set the song key (suggested: D major).
  - Mix: clipped_samples == 0, LUFS -14..-10, band order lowmid>mid>low.
  - KLEZMER FREYGISH is non-negotiable: klezmer: freygish (phrygian dominant) melody with grace-note sobs (krekhts), oom-pah bass, simcha tempo — joy and grief in the same phrase
  - CALL RESPONSE MELODY is non-negotiable: 2-bar call, 2-bar answer; melody talks to itself
  - SWING 16TH is non-negotiable: shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk
---
# Klezmer arrangement (graph-compiled)

## The pocket — freylekh_bounce
klezmer loop DNA (wave20) Swing 0.54 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-04 + grid:curated (wave20 machine-readable loop DNA — map complete))*

## Techniques (weight order — the top ones DEFINE the genre)
- **klezmer freygish** (w0.95): klezmer: freygish (phrygian dominant) melody with grace-note sobs (krekhts), oom-pah bass, simcha tempo — joy and grief in the same phrase *(curated:claude/2026-07-03-w13)*
- **call response melody** (w0.7): 2-bar call, 2-bar answer; melody talks to itself *(curated:claude/2026-07-02)*
- **swing 16th** (w0.5): shift odd 16ths late; 0.54-0.58 gentle, 0.60-0.65 drunk *(skill:trap-arrangement@v2)*

## Sound recipes (this palette, these moves)
- **squeeze box**: faust accordion: musette detuned reeds, bellows swell — forró leads, cumbia riffs, tango sighs (slow attack, long phrases), klezmer oom-pah color

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-10, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
