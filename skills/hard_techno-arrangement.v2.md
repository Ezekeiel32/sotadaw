---
name: hard_techno-arrangement
version: 2
kind: genre
tags: [hard_techno, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 145-160; set the song key (suggested: F minor).
  - Mix: clipped_samples == 0, LUFS -7..-5, band order low>mid>lowmid.
  - RUMBLE KICK is non-negotiable: kick tail feeds a send reverb lowpassed into a rolling rumble
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - BRICKWALL MASTERING is non-negotiable: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Hard_Techno arrangement (graph-compiled)

## The pocket — hardtechno_drive
relentless 4-floor + industrial off-hats  *(source: curated:claude/2026-07-03-patterns-w2 (executable loop DNA))*

## Techniques (weight order — the top ones DEFINE the genre)
- **rumble kick** (w0.95): kick tail feeds a send reverb lowpassed into a rolling rumble *(curated:claude/2026-07-02)*
- **four on floor** (w0.9): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **brickwall mastering** (w0.8): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **filter build** (w0.7): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*
- **hoover stab** (w0.6): the hoover/mentasm stab (detuned saw scream) — hardcore/gabber riffs, also rave-era breakbeat; pitch it in minor riffs *(curated:claude/2026-07-03)*

## Sound recipes (this palette, these moves)
- **kick punch zones**: kick_punch now has knobs (source.params or automate): punch 0-1.5 (click level), drop 0-8 (pitch-env depth), decay 0.05-1.2s (body), tail 0-1, drive 0.2-4 (pre-tanh). Defaults = the classic sound. Longer decay 0.6-0.9 = room-shaking house kick; drive 2+ = distorted techno.

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -7..-5, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
