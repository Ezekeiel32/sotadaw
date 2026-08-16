---
name: bassline-arrangement
version: 4
kind: genre
tags: [bassline, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 135-142; set the song key (suggested: F# minor).
  - Mix: clipped_samples == 0, LUFS -8..-6, band order low>lowmid>mid.
  - WARPED BASSLINE is non-negotiable: speed garage/bassline: the pitch-WARPED sub 'wow' (detuned reese, filter+pitch bend per note) under a 4x4 garage shuffle; organ stabs on the offbeat
  - VOCAL CHOPS is non-negotiable: short pitched vocal stabs (choir kit, high keys) placed rhythmically
  - TWO STEP KICK is non-negotiable: NO four-on-floor: kick on 1 and ~2.75 (vary per bar); the hole IS the groove
---
# Bassline arrangement (graph-compiled)

## The pocket — bassline_niche
4x4 with the warped-sub bounce Swing 0.56 rides the 8th grid — keep swing.grid matched to where the hats live.  *(source: curated:claude/2026-07-06 (wave37 hiphop/bass/club canon; drill i-VI own-search f147))*

## Techniques (weight order — the top ones DEFINE the genre)
- **warped bassline** (w0.95): speed garage/bassline: the pitch-WARPED sub 'wow' (detuned reese, filter+pitch bend per note) under a 4x4 garage shuffle; organ stabs on the offbeat *(curated:claude/2026-07-03-w8)*
- **vocal chops** (w0.7): short pitched vocal stabs (choir kit, high keys) placed rhythmically *(curated:claude/2026-07-02)*
- **two step kick** (w0.6): NO four-on-floor: kick on 1 and ~2.75 (vary per bar); the hole IS the groove *(curated:claude/2026-07-02)*
- **hat rolls** (w0.5): 16th->32nd bursts at phrase ends; velocity ramps *(skill:trap-arrangement@v2)*

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='ukg_shuffle', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-03 (2-step: hard 16th swing, ghosted e/a))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-6, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
