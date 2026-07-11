---
name: dj-blend
version: 2
kind: performance
tags: [dj, blend, transition, warp, beat-match, set-building]
hard_constraints:
  - "Beat-match by WARP, never by nudging notes: every deck's audioClips carry sourceBpm; the engine time-stretches all decks onto ONE song bpm grid. Two decks at two tempos in one song.json without sourceBpm on both is a train wreck by construction."
  - "Phrase-align every transition: blends start on a 4-bar (16-beat) boundary of the OUTGOING deck. Dance music breathes in 4/8/16-bar phrases; a mid-phrase blend sounds like a mistake even when beat-matched."
  - "ONE bass at a time. Until the swap beat the incoming deck rides fx_djfilter knob at +0.5..+0.7 (highpass side, lows killed). At the swap: incoming knob -> 0 within 0.25 beat and outgoing knob -> +0.4..+0.6. Two full low ends stacked = mud and brickwall pumping."
  - "Tempo distance law: warp is transparent to about +/-8% (soundtouch). Within 8% blend at either tempo; 8-16% pick the midpoint grid or accept audible artifacts; beyond 16% do a cut/echo-out transition, not a long blend."
  - "THE GRID TRAVELS: tempoMap [{bar,bpm,curve?}] re-anchors the song tempo mid-set (curve 1 = hold-then-step at the point, DEFAULT; 0 = linear ramp; <0 = early jump). Put each step AT the bass-swap bar of its transition. All beats and warped clips follow — engine-proven to 0.1ms."
---
# DJ blending (v1 — the beat-matched transition)

The DAW is the DJ. `dj_blend(deck_a, deck_b, song)` builds one transition;
`dj_set(tracks[], song)` builds a WHOLE SET: N warped decks on a traveling grid
(a tempoMap step at every bass-swap bar re-anchors the tempo to the incoming deck
— the classic 128→132→136 energy arc), phrase-aligned crossfades, bass swaps.
Everything is one song.json: every move is visible automation you (or the user)
can drag afterwards.

## The transition recipe (what dj_blend writes, so you can edit or hand-roll it)
- Decks: one track per song, `source {"kind":"audio"}`, `audioClips[{file, startBeat, sourceBpm}]`,
  `fx[0] = fx_djfilter (knob 0, res 1.1)`.
- Grid: song bpm = deck A's bpm by default. Deck B enters at `b_start` =
  last 4-bar boundary that leaves `blend_bars` before A ends.
- Gains (linear-in-dB is fine at these lengths): A `0 → -60` across the blend;
  B `-27 → 0` across the blend.
- Bass swap at the blend midpoint (bar-snapped): B's knob `0.62 → 0` in a 0.25-beat step;
  A's knob `0 → 0.5` right after. The low end changes hands in one beat — that is the
  moment the crowd feels.

## Reading the energy (choosing the swap bar)
- Swap INTO a downbeat that starts a phrase of deck B (its intro bars usually work:
  offsetSec 0 is fine for v1; for a mid-song entry set the clip offsetSec so `b_start`
  lands on a phrase start of B).
- Long blend (8-16 bars): melodic/progressive material, compatible keys.
- Short blend (4 bars) or cut: clashing keys, vocal-heavy decks, or >16% tempo distance.
- Keys a fifth apart or relative major/minor blend clean; a semitone apart clashes —
  shorten the blend or filter one deck hard (knob ±0.7) throughout.

## Set building
- `dj_set` is the native move (no intermediate renders): each transition steps the
  tempoMap to the incoming deck's natural bpm at the swap bar, so every deck plays
  at (or within warp-transparency of) its own tempo in its solo region.
- Tempo arcs beyond DJing: tempoMap works on ANY song — halftime drops
  ({"bar": 32, "bpm": 70}), ritardando outros (curve 0 = linear ramp), tempo switches
  between sections. Warped audio, notes, automation and lyrics all follow.
- Verify every blend numerically before trusting your ears: render and check
  clipped_samples == 0 (two decks + swap can overshoot; fx_brickwall -1.0 is in the
  master by default) and that the blend region's LUFS does not dip >2 dB below the
  surrounding sections (energy hole = gain curves crossing too early).
