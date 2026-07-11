---
name: neurofunk-arrangement
version: 1
kind: genre
tags: [neurofunk, dnb, arrangement]
compiled_from: knowledge-graph (tools/skill_compiler.py; provenance per fact below)
hard_constraints:
  - BPM 170-176; set the song key (suggested: F# minor).
  - Mix: clipped_samples == 0, LUFS -10..-6, band order low>mid>lowmid.
  - REESE BASS is non-negotiable: detuned saw stack, movement via slow LFO on filter
  - LAYERED KICK is non-negotiable: sample kick transient + faust 808 body, body -6 to -12 under
  - AMEN CHOPS is non-negotiable: jungle: breakbeat chopped/reordered per bar (duplicate_bars+clear_bars micro-edits of a 1-bar break), 160-175
  - FORBIDDEN: widen low end — fx_widen on 808/kick/sub — FORBIDDEN
---
# Neurofunk arrangement (graph-compiled)

Neurofunk is a child of **dnb** — its groove laws apply unless overridden below.

## Techniques (weight order — the top ones DEFINE the genre)
- **reese bass** (w0.95): detuned saw stack, movement via slow LFO on filter *(skill:faust-reese@v1)*
- **layered kick** (w0.7): sample kick transient + faust 808 body, body -6 to -12 under *(skill:sound-palette@v2)*
- **amen chops** (w0.6): jungle: breakbeat chopped/reordered per bar (duplicate_bars+clear_bars micro-edits of a 1-bar break), 160-175 *(curated:claude/2026-07-03)*
- **curve shaped automation** (w0.6): automation point curve -1..1 shapes the leaving segment: >0 late-bloom (THE build shape into drops), <0 early-jump (post-drop settle). Linear builds feel early/flat. *(skill:automation-motion@v2 (2026-07-03, engine-verified))*
- **pump sidechain** (w0.5): fx_pump rate=bpm/60 on pads/keys, depth 0.5-0.8; never on drums *(skill:fx-usage@v1)*

## Inherited from dnb
- ghost notes: low-velocity (0.25-0.45) off-grid hits between main hits
- breakbeat chop: kick 0/2.5, snare 1/3 at 170+; ghost kicks vary per bar
- loudness recovery: FINAL MASTERING STEP, always: after the mix is clean (clipped 0, dBTP <= -1), compare LUFS to the genre window. If below, raise masterGainDb by (window_mid - LUFS) dB — up to +6 — INTO the master limiter (ceiling -1 makes this safe) and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing track trims.
- brickwall mastering: master chain law: fx_trim (input stage) -> fx_saturate (density, FULL WET on hot mixes) -> fx_brickwall (TRUE 5ms-lookahead limiter, ceiling -1.2). NEVER type 'limiter' (master_limiter ceiling is non-functional). masterGainDb stays 0 (it runs POST-chain).
- warp beatmatch: beat-match by sourceBpm warp onto ONE grid — never nudge notes; transparent to ~+/-8% tempo distance
- phrase aligned blend: transitions start on a 4-bar boundary of the outgoing deck; dance music breathes in 4/8/16-bar phrases
- bass swap: ONE bass at a time: incoming deck rides fx_djfilter knob +0.5..0.7 until the swap beat, then lows change hands in 0.25 beat
- filter transition: fx_djfilter bipolar knob: LP sweep out the old deck / HP hold the new — the one-knob DJ mixer filter
- tempo map motion: tempoMap on any song: halftime drops, ritardando outros (curve 0), section tempo switches — beats, warped audio, automation all follow

## Verify (the ears will check)
After render: analyze_wav must show clipped_samples 0, LUFS in -10..-6, band order low>mid>lowmid. If a filter build was used, centroid_by_quarter must RISE into the drop.
