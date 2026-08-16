---
name: idm-arrangement
version: 3
kind: genre
tags: [idm, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 80-160; set the song key (suggested: C minor).
  - Mix: clipped_samples == 0, LUFS -14..-9, band order lowmid>mid>low.
  - IDM MICROEDIT is non-negotiable: IDM drum programming: no bar repeats 1:1 — retrigger/reverse/bitcrush/half-gate single hits per pass; melody = detuned melancholy pads drifting over the broken grid
  - EVOLVING PADS is non-negotiable: 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush
  - SEND REVERB is non-negotiable: reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY
---
# Idm arrangement (graph-compiled)

## The pocket — broken_grid
idm loop DNA (wave16)  *(source: curated:claude/2026-07-06 (wave38 world/anthem canon; freygish+bigroom-vamp+levels-anthem cited f148; afro_pocket i-VII = canon-prior, cite pending))*

## Techniques (weight order — the top ones DEFINE the genre)
- **idm microedit** (w0.95): IDM drum programming: no bar repeats 1:1 — retrigger/reverse/bitcrush/half-gate single hits per pass; melody = detuned melancholy pads drifting over the broken grid *(curated:claude/2026-07-03-w8)*
- **evolving pads** (w0.8): 8-16 beat overlapping pad notes; voices enter/leave; no silence, no rush *(curated:claude/2026-07-02)*
- **send reverb** (w0.6): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **fm metallic arps** (w0.6): FM bell/metallic 16th arps in phrygian/harmonic minor — the goa melodic signature *(curated:claude/2026-07-02)*
- **chance operations** (w0.6): probability on scene transitions (followChance 0.6-0.8): the build advances when the die says so, else runs another pass — organic, never-identical performances from one grid; the aleatoric lineage (Cage's chance operations -> Eno's generative systems -> the Turing-machine module) as a LAUNCHER primitive *(engine-witnessed weighted follow actions (firing 49: trackNext w0.7 +1 more)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-9, band order lowmid>mid>low. If a filter build was used, centroid_by_quarter must RISE into the drop.
