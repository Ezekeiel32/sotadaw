---
name: psytrance-arrangement
version: 3
kind: genre
tags: [psytrance, techno, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 140-148; set the song key (suggested: E minor).
  - Mix: clipped_samples == 0, LUFS -14..-8, band order low>lowmid>mid.
  - ROLLING OFFBEAT BASS is non-negotiable: THE psy engine: kick on each beat, bass 16ths at +0.25/+0.5/+0.75 of EVERY beat (k-b-b-b gallop), short (~0.2) same-root notes for 8-16 bars; root follows the key
  - LOUDNESS RECOVERY is non-negotiable: FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims.
  - JOURNEY STRUCTURE is non-negotiable: 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown
---
# Psytrance arrangement (graph-compiled)

Psytrance is a child of **techno** — its groove laws apply unless overridden below.

## The pocket — psy_fullon
kick 1/2/3/4 dry+punchy; bass gallop fills every beat's offbeat 16ths; hats drive 16ths; NO swing (grid is the trance)  *(source: curated:claude/2026-07-02)*

## Techniques (weight order — the top ones DEFINE the genre)
- **rolling offbeat bass** (w1.0): THE psy engine: kick on each beat, bass 16ths at +0.25/+0.5/+0.75 of EVERY beat (k-b-b-b gallop), short (~0.2) same-root notes for 8-16 bars; root follows the key *(curated:claude/2026-07-02)*
- **loudness recovery** (w0.95): FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims. *(eval:techno/2026-07-02 score 0.57 (clipped_ok+lufs_in_range+true_peak_ok failed) via factory_advisor)*
- **journey structure** (w0.93): 6-8 min arc: intro(no bass) -> build -> peak -> BREAKDOWN at ~60% (kick+bass OUT, pads/leads breathe, 8-16 bars) -> filter rebuild -> peak2 -> outro. Use duplicate_bars to stamp sections, clear_bars to carve the breakdown *(curated:claude/2026-07-02)*
- **groove psy straight** (w0.9): apply_groove('psy_straight', amount 1.0) - machine grid with accented offbeat 8ths; psytrance/techno want NO drag, only accent shape. *(curated:claude/2026-07-03 (groove engine profiles -> graph))*
- **acid squelch lead** (w0.86): resonant 303-style line (acid303), cutoff automated per phrase, res 2-4; THE lead voice *(curated:claude/2026-07-02)*
- **psy hat drive** (w0.79): closed hats straight 16ths vel ~0.5 with offbeat-8th accents ~0.8; open hat on the offbeat *(curated:claude/2026-07-02)*
- **four on floor** (w0.72): kick every beat; openhat on offbeat 8ths *(skill:house-arrangement@v1)*
- **riser throws** (w0.65): before each section change: reverb-send throw or 2-bar filter riser (automate cutoff up) *(curated:claude/2026-07-02)*
- **filter build** (w0.58): fx_filter cutoff automated 250->9000 over 4-8 bars, lands ON the drop *(skill:automation-motion@v1)*
- **gain staged saturation** (w0.51): saturation adds LEVEL: after set_track_fx with fx_saturate, trim that track's gainDb by 4-6 dB (drive is tone, gain is level). Get LOUD the clean way: masterGainDb +2..+4 INTO the master limiter (ceiling -1). Verify: clipped_samples 0 AND true_peak_dbtp <= -1 AND LUFS inside the genre window — if LUFS too low, raise masterGainDb (never remove the trims). *(eval:phonk 2026-07-02 (score 0.571 x2: clipped+dBTP over, LUFS under))*

## Inherited from techno
- pump sidechain: fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums
- rumble kick: kick tail feeds a send reverb lowpassed into a rolling rumble
- modular stab: single dark stab/chord repeated with filter automation variation
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).

## Sound recipes (this palette, these moves)
- **psy bass sound**: sub_clean or reese LOW notes 0.2 len through fx_filter cutoff ~900 + fx_saturate drive 4 (then trim gain -4); DRY (no sends)
- **psy kick sound**: kick_punch dry, gain ~-4; NEVER widened
- **supersaw wall**: supersaw_fat (7-voice detune, zones cutoff/spread/sub): trance/edm pads+leads; automate cutoff for builds; spread 0.7+ on hooks
- **psy kick tight**: kick_psy (zones punch/decay): psy/techno kick — punch 10-16 hard styles, decay 0.2-0.3 tight; ALWAYS dry

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -14..-8, band order low>lowmid>mid. If a filter build was used, centroid_by_quarter must RISE into the drop.
