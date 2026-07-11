---
name: rnb-arrangement
version: 3
kind: genre
tags: [rnb, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 65-95; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -12..-8, band order low>lowmid>mid.
  - FINGER SNAP BEAT is non-negotiable: modern R&B pocket: halftime 808 + finger-snap backbeat on 3, huge space for the topline; hats whisper 16ths at vel 0.2-0.35, one fill per 8 bars
  - M7 CHORDS is non-negotiable: minor 7th / extended chords, mid register, soft velocity
  - BEHIND BEAT SNARE is non-negotiable: snare 0.02-0.05 beats late = laid-back head-nod
---
# Rnb arrangement (graph-compiled)

## The pocket — rnb_snap
halftime snap: space is the pocket Swing 0.52 rides the 16th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-03-patterns-w2 (executable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **finger snap beat** (w0.9): modern R&B pocket: halftime 808 + finger-snap backbeat on 3, huge space for the topline; hats whisper 16ths at vel 0.2-0.35, one fill per 8 bars *(curated:claude/2026-07-03-w6)*
- **m7 chords** (w0.85): minor 7th / extended chords, mid register, soft velocity *(skill:lofi-arrangement@v1)*
- **behind beat snare** (w0.7): snare 0.02-0.05 beats late = laid-back head-nod *(skill:lofi-arrangement@v1)*
- **send reverb** (w0.6): reverb on a BUS at mix 1.0, balance via send level; kick/808 DRY *(skill:fx-usage@v1)*
- **sliding 808** (w0.6): 808 pitch slides between roots (overlapping notes) *(skill:drill-arrangement@v1)*

## Sound recipes (this palette, these moves)
- **gliss harp**: faust harp: plucked string, bright pluck into warm ring — glissandi as fast runs into downbeats, arpeggios under cinematic beds; jazz ballad color
- **organ soul zones**: organ_soul is a real drawbar organ now: sub/body/sparkle 0-2 (drawbar GROUP levels: 16' | 8'+5.33'+4' | 2.66'+2'+1'), perc 0-1 (Hammond percussion), rotary 0-0.5 + speed 0.5-8Hz. Gospel shout = sparkle 1.5 + perc 0.6 + speed 7 (fast Leslie); ballad = sparkle 0.4 + speed 0.8.
- **rhodes zones**: rhodes knobs: bell 0-3 (FM strike brightness), bark 0.05-1s (how long the bright attack lasts), decay 0.4-3s, sustain 0-0.8. Dilla keys = bell 0.8 + short bark; gospel chords = sustain 0.5 + decay 2.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
