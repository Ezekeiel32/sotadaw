---
name: gabber-arrangement
version: 3
kind: genre
tags: [gabber, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 150-190; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -8..-5, band order low>mid>lowmid.
  - GABBER KICK is non-negotiable: overdriven 909 kick: distorted till the tail becomes the bassline (single saturated kick = kick+bass in one), 150-190bpm
  - LOUDNESS RECOVERY is non-negotiable: CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL.
  - HOOVER STAB is non-negotiable: the hoover/mentasm stab (detuned saw scream) — hardcore/gabber riffs, also rave-era breakbeat; pitch it in minor riffs
---
# Gabber arrangement (graph-compiled)

## The pocket — gabber_four
gabber loop DNA (wave15)  *(source: curated:claude/2026-07-06 (wave36 canon harmony; cumbia/bachata canon own-search f146; Andalusian/royal-road/pop-four/12-bar = textbook commons))*

## Techniques (weight order — the top ones DEFINE the genre)
- **gabber kick** (w0.95): overdriven 909 kick: distorted till the tail becomes the bassline (single saturated kick = kick+bass in one), 150-190bpm *(curated:claude/2026-07-03)*
- **loudness recovery** (w0.9): CLOSING STEP, numeric: after the mix is clean (clipped 0, dbtp <= -1), if lufs_integrated < the genre window's LOW bound, raise the makeup fx_trim (the one before fx_brickwall) by (low_bound - lufs) dB, re-render, re-check. Quiet-but-clean is still a FAIL. *(eval:2026-07-03 (techno -14.99, grime -12.92 vs windows — recurring clean-but-quiet residual))*
- **hoover stab** (w0.85): the hoover/mentasm stab (detuned saw scream) — hardcore/gabber riffs, also rave-era breakbeat; pitch it in minor riffs *(curated:claude/2026-07-03)*
- **four on floor** (w0.8): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **brickwall mastering** (w0.8): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*

## Sound recipes (this palette, these moves)
- **kick punch zones**: kick_punch now has knobs (source.params or automate): punch 0-1.5 (click level), drop 0-8 (pitch-env depth), decay 0.05-1.2s (body), tail 0-1, drive 0.2-4 (pre-tanh). Defaults = the classic sound. Longer decay 0.6-0.9 = room-shaking house kick; drive 2+ = distorted techno.

## The groove (timing DNA — apply it, don't fake it)
- PREFER apply_groove(track='drums'-like tracks, name='techno_drive', amount 0.8-1.0) OVER the global swing object: swing{} is a uniform shuffle, the named profile carries this genre's per-slot micro-timing AND ghost-velocity shape. Write on-grid notes first, then apply. *(curated:claude/2026-07-09 (machine straight, hard offbeat-8th accent wave — the warehouse pulse))*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-5, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
