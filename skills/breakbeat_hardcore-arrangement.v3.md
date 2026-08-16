---
name: breakbeat_hardcore-arrangement
version: 3
kind: genre
tags: [breakbeat_hardcore, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 140-155; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -10..-7, band order low>lowmid>mid.
  - AMEN CHOPS is non-negotiable: jungle: breakbeat chopped/reordered per bar (duplicate_bars+clear_bars micro-edits of a 1-bar break), 160-175
  - HOOVER STAB is non-negotiable: the hoover/mentasm stab (detuned saw scream) — hardcore/gabber riffs, also rave-era breakbeat; pitch it in minor riffs
  - PIANO HOUSE STAB is non-negotiable: rave/eurodance piano: octave-doubled minor piano stabs on the offbeats (M1-organ lineage), 8-bar hooks, verse rap / sung chorus contrast
---
# Breakbeat_Hardcore arrangement (graph-compiled)

## The pocket — hardcore_breaks
breakbeat_hardcore loop DNA (wave18) Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending) +1 more)*

## Techniques (weight order — the top ones DEFINE the genre)
- **amen chops** (w0.9): jungle: breakbeat chopped/reordered per bar (duplicate_bars+clear_bars micro-edits of a 1-bar break), 160-175 *(curated:claude/2026-07-03)*
- **hoover stab** (w0.85): the hoover/mentasm stab (detuned saw scream) — hardcore/gabber riffs, also rave-era breakbeat; pitch it in minor riffs *(curated:claude/2026-07-03)*
- **piano house stab** (w0.8): rave/eurodance piano: octave-doubled minor piano stabs on the offbeats (M1-organ lineage), 8-bar hooks, verse rap / sung chorus contrast *(curated:claude/2026-07-03-w6)*
- **riser throws** (w0.6): before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up) *(curated:claude/2026-07-02)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='dnb_roll', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (rolling break at 170+: tight grid, ghost 16ths a hair early, 2&4 spine full))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
