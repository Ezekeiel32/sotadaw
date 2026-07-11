---
name: gabber-arrangement
version: 1
kind: genre
tags: [gabber, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 150-190; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -8..-5, band order low>mid>lowmid.
  - GABBER KICK is non-negotiable: overdriven 909 kick: distorted till the tail becomes the bassline (single saturated kick = kick+bass in one), 150-190bpm
  - HOOVER STAB is non-negotiable: the hoover/mentasm stab (detuned saw scream) — hardcore/gabber riffs, also rave-era breakbeat; pitch it in minor riffs
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
---
# Gabber arrangement (graph-compiled)

## Techniques (weight order — the top ones DEFINE the genre)
- **gabber kick** (w0.95): overdriven 909 kick: distorted till the tail becomes the bassline (single saturated kick = kick+bass in one), 150-190bpm *(curated:claude/2026-07-03)*
- **hoover stab** (w0.85): the hoover/mentasm stab (detuned saw scream) — hardcore/gabber riffs, also rave-era breakbeat; pitch it in minor riffs *(curated:claude/2026-07-03)*
- **four on floor** (w0.8): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **brickwall mastering** (w0.8): master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain). *(autonomy-cycle:techno/2026-07-03 (0.571->0.714 after loudness lesson; residual lufs/dbtp fails traced to broken master_limiter era))*
- **loudness recovery** (w0.6): FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims. *(eval:techno/2026-07-02 score 0.57 (clipped_ok+lufs_in_range+true_peak_ok failed) via factory_advisor)*

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -8..-5, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
