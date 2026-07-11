---
name: mix-headroom
version: 6
kind: mixing
tags: [always, mix, gain-staging, loudness, mastering, verdict]
hard_constraints:
  - "THE VERDICT LOOP (v6): finishing = iterate master_report, not vibes. edit -> master_report(song, genre) -> fix the fix_first check using its hint -> repeat until pass:true. It renders (if stale), measures, and judges vs the genre's KG MixTarget in ONE call; every failing check carries a SOURCE-FIX hint. analyze_wav is for raw numbers mid-flight; master_report is the ship gate."
  - "MASTER CHAIN LAW (gate-forensics 2026-07-03): end every master with fx_brickwall: \"master\": [..., {\"id\": \"fx_brickwall\", \"params\": {\"ceiling\": -1.2}}]. NEVER type \"limiter\" (master_limiter's ceiling is non-functional - floats sail past 0 dBFS and clip at the file write)."
  - "masterGainDb stays 0. It runs AFTER the whole master chain (post-limiter gain re-opens the headroom you just limited). ALL level staging happens INSIDE the chain with fx_trim: {\"id\": \"fx_trim\", \"params\": {\"level\": <dB>}}."
  - "SUB-DOMINANT LAW (amapiano vignette 2026-07-03): genres whose energy lives in the sub (amapiano/3step/gqom/dub/848-heavy trap) overshoot the sample ceiling by >1dB in TRUE peak — fx_brickwall is sample-peak, inter-sample reconstruction sails past it (measured: ceiling -1.0 -> dBTP +0.14 on log_drum+kick; ceiling -1.5 -> dBTP -0.36). Use ceiling -1.5 to -2.0 when the low band dominates."
  - "Loudness recovery on a clean-but-quiet master: fx_trim (input, +dB) -> fx_saturate (density; mix 1.0 FULL WET on hot mixes - a partial dry path leaks uncompressed transients around the tanh) -> fx_trim (makeup) -> fx_brickwall. Iterate the trims, never the ceiling."
  - Convergence signal is clipped_samples - drive it to 0. peak_dbfs saturates at 0.0 and shows NO gradient; never iterate on peak alone.
  - true_peak_dbtp must be <= -1.0 on the final render.
  - Saturation adds LEVEL - after adding fx_saturate to a track, trim that track's gainDb by 4-6 dB.
  - Final render targets = master_report pass:true (clipped 0, dBTP <= -1.0, LUFS in the genre window, band order + floors intact).
---
# Gain staging + mastering (v6 - the verdict era)

v2 lesson: bar-downbeat transient stacks sum past full scale even when each track is clean.
v3 lesson: agents trimmed so well they shipped QUIET - recover loudness at the bus.
v4 lesson (THE 0.020 GATE forensics): the old master_limiter never limited (broken ceiling),
and masterGainDb runs POST-chain - so "push gain into the limiter" was pushing gain PAST it.
**v6: the judge is a tool now.** master_report(song, genre) returns
`{pass, score, fix_first, checks:[{name, ok, got, want, hint}]}` — the same engine behind the
UI's MASTER CHECK button and the eval gauntlet. Trust its ordering: fix `fix_first` first
(clipped -> true_peak -> lufs -> band_order -> floors), one move per iteration, re-check.

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
(sets how hard the brickwall works). Character on the master is legal now too — vst3
inserts ({"id": "vst3:<name>", "preset": <blob>}) work in master[] like anywhere else;
keep them BEFORE the final trim+wall pair, and A/B them honestly with "bypass": true
(created but disabled — settings survive) instead of deleting.

Band-order or floor failures are SOURCE problems: track gains, note density, an EQ bell
on the offender ({"type":"eq"}) — never master-bus makeup. The report's hints name the move.

Starting track gains still apply: 808/kick 0..-3 (anchor), sampled drums -4..-8,
snare -4, hats -8..-14, melodic/pads -8..-14.
