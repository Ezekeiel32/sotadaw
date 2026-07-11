---
name: techno-arrangement
version: 3
kind: genre
tags: [techno, house, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 128-136; set the song key (suggested: A minor).
  - Mix: clipped_samples == 0, LUFS -12..-7, band order low>lowmid>mid.
  - FOUR ON FLOOR is non-negotiable: kick every beat; openhat on offbeat 8ths
  - LOUDNESS RECOVERY is non-negotiable: FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims.
  - RUMBLE KICK is non-negotiable: kick tail feeds a send reverb lowpassed into a rolling rumble
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Techno arrangement (graph-compiled)

Techno is a child of **house** — its groove laws apply unless overridden below.

## The pocket — techno_grid
relentless kick, offbeat hats, one stab varied by automation, 16-bar arcs  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **four on floor** (w1.0): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **loudness recovery** (w0.95): FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims. *(eval:phonk+psytrance 2026-07-02 (clean but 2-3dB under LUFS window))*
- **rumble kick** (w0.92): kick tail feeds a send reverb lowpassed into a rolling rumble *(curated:claude/2026-07-02)*
- **gain staged saturation** (w0.9): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*
- **modular stab** (w0.84): single dark stab/chord repeated with filter automation variation *(curated:claude/2026-07-02)*
- **filter build** (w0.76): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*
- **pump sidechain** (w0.68): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*

## Inherited from house
- offbeat bass: bass hits on the 8th between kicks

## Sound recipes (this palette, these moves)
- **techno rumble**: kick_punch + send to verb bus (size 6+) with fx_filter cutoff 150 on the bus return
- **techno stab**: keys_dark single chord, fx_filter + automate cutoff per 4 bars, fx_delay dotted
- **supersaw wall**: supersaw_fat (7-voice detune, zones cutoff/spread/sub): trance/edm pads+leads; automate cutoff for builds; spread 0.7+ on hooks
- **psy kick tight**: kick_psy (zones punch/decay): psy/techno kick — punch 10-16 hard styles, decay 0.2-0.3 tight; ALWAYS dry

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -12..-7, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
