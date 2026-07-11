---
name: mix-headroom
version: 4
kind: mixing
tags: [always, mix, gain-staging, loudness, mastering]
hard_constraints:
  - "MASTER CHAIN LAW (gate-forensics 2026-07-03): end every master with fx_brickwall: \"master\": [..., {\"id\": \"fx_brickwall\", \"params\": {\"ceiling\": -1.2}}]. NEVER type \"limiter\" (master_limiter's ceiling is non-functional - floats sail past 0 dBFS and clip at the file write)."
  - "masterGainDb stays 0. It runs AFTER the whole master chain (post-limiter gain re-opens the headroom you just limited). ALL level staging happens INSIDE the chain with fx_trim: {\"id\": \"fx_trim\", \"params\": {\"level\": <dB>}}."
  - "Loudness recovery on a clean-but-quiet master: fx_trim (input, +dB) -> fx_saturate (density; mix 1.0 FULL WET on hot mixes - a partial dry path leaks uncompressed transients around the tanh) -> fx_trim (makeup) -> fx_brickwall. Iterate the trims, never the ceiling."
  - Convergence signal is clipped_samples - drive it to 0. peak_dbfs saturates at 0.0 and shows NO gradient; never iterate on peak alone.
  - true_peak_dbtp must be <= -1.0 on the final render.
  - Saturation adds LEVEL - after adding fx_saturate to a track, trim that track's gainDb by 4-6 dB.
  - Final render targets: clipped_samples == 0, true_peak_dbtp <= -1.0, lufs_integrated inside the genre window (default [-16, -9]).
---
# Gain staging + mastering (v4 - the working brickwall era)

v2 lesson: bar-downbeat transient stacks sum past full scale even when each track is clean.
v3 lesson: agents trimmed so well they shipped QUIET - recover loudness at the bus.
**v4 lesson (THE 0.020 GATE forensics)**: the old master_limiter never limited (broken ceiling),
and masterGainDb runs POST-chain - so "push gain into the limiter" was pushing gain PAST it.

The master chain that measures right, every time:

```json
"masterGainDb": 0,
"master": [
  {"id": "fx_trim",      "params": {"level": -12}},          // stage the hot float mix down
  {"id": "fx_saturate",  "params": {"drive": 5, "mix": 1.0}}, // density; FULL WET
  {"id": "fx_trim",      "params": {"level": 6}},            // makeup into the wall
  {"id": "fx_brickwall", "params": {"ceiling": -1.2}}         // TRUE 5ms-lookahead limiter
]
```

Calibrate with two knobs only: input trim (more = louder + denser) and makeup trim
(sets how hard the brickwall works). Verify each render: clipped 0, dBTP <= -1,
LUFS in the genre window. The gate track landed -13.9 LUFS / -1.19 dBTP / 0 clipped
with exactly this shape.

Starting track gains still apply: 808/kick 0..-3 (anchor), sampled drums -4..-8,
snare -4, hats -8..-14, melodic/pads -8..-14.
