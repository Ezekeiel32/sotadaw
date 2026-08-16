---
name: timbre-words
version: 1
description: "LLM2Fx law (w79, r-28 item 167): open-vocabulary timbre asks resolve through MEASURED features + param code + these few-shots — never embedding cosine, never a guess from the word alone"
---

# TIMBRE WORDS — the LLM2Fx pattern

The ask says "warmer", "glassy", "vintage". The WRONG move is mapping the
word straight to parameters (or to an embedding neighbor). The LAW:

1. **MEASURE FIRST** — `analyze_wav` on the current render (or the lane's
   stem). You now hold centroid, band shares, LUFS, crest.
2. **CONDITION the move on the measurement.** "Warmer" on a take whose
   lowmid is already 28% means LESS than on one at 12%. Every few-shot
   below states its precondition.
3. **PARAM CODE, small moves, source-first.** One or two fx edits at a
   time; re-measure after. Never fix at the master what a lane caused.

## The few-shot table (word -> measured precondition -> the move)

- **warm / warmer** — if centroid > 1800Hz or air% > 18: `fx_filter`
  cutoff 8500-9500 on the bright lane + `fx_saturate` {drive 4, tone 3200,
  mix 0.18} on the bus. If lowmid% < 14: `fx_bell` {freq 320, gain +2, q 1.1}.
- **dark / moodier** — `fx_filter` cutoff 4500-6500 on leads/pads (NEVER a
  parked dark filter on the master — the doctor's X3 trap); drop hat/cym
  velocities 15%.
- **bright / airy / sparkle** — if air% < 8: `fx_bell` {freq 11000, gain +2.5,
  q 0.8} on the lead/master; raise hat velocities 10%; consider `fx_widen`
  on pads (>150Hz content only).
- **glassy** — bell +3dB @ 8-12k with LOW drive anywhere in the chain
  (glass = clean highs; saturation is the enemy here); attack 2-6ms on keys.
- **vintage / lofi / tape** — `fx_crush` {srate 22050-28000, bits 12, mix
  0.25-0.4}; `fx_filter` cutoff 7500; slow pitch drift via the analog pass
  (voice_character.analogize) beats wow-flutter fakes.
- **fat / thick** — if the lane is mono-thin: the birth-doubling twin
  (X/XR, pan ±0.7) beats any widener; `fx_saturate` {drive 5, mix 0.25};
  sub support only if lowend% < 20 (fx_bass_grit keeps the sub clean).
- **crunchy / gritty** — `fx_saturate` {drive 8-10, tone 4500, mix 0.35} on
  drums bus; or `fx_crush` {bits 10, mix 0.2} on the break only.
- **muddy -> clean it** — `fx_hipass` 120-180 on pads/keys/verb returns
  (never kick/bass/808); `fx_bell` {freq 350, gain -3, q 1.4} on the
  crowded lane (the masking court names it).
- **harsh -> smooth it** — if 2-5k% > 26: `fx_bell` {freq 3200, gain -2.5,
  q 1.6} on the offender; deess the vocal FIRST in its chain; lower
  supersaw detune before EQing it.
- **thin** — if lowmid% < 10: octave-down double of the lead at vel 0.6;
  `fx_bell` {freq 250, gain +2, q 1.0}; check the HPFs aren't stacked.
- **wide** — `fx_widen` on >150Hz lanes only (mono law); the wide choir
  pair (±0.8 unisons) beats wideners on vocals; check mono-fold after.
- **punchy** — `fx_transient` {attack +6..9} on kick/snare; ensure the
  pre-wall clipper isn't shaving the transient (drop drive 1 step);
  sidechain pump depth +10%.

## The receipt

After the move: `analyze_wav` again and SAY the delta ("centroid 2100 ->
1750Hz, lowmid 12 -> 16%"). The word was the ask; the measurement is the
proof it landed.
