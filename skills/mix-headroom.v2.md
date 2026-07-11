---
name: mix-headroom
version: 2
kind: mixing
tags: [always, mix, gain-staging]
hard_constraints:
  - Always end the master chain with the limiter: "master": [{"type": "limiter", "params": {"ceiling": -1.0}}].
  - Convergence signal is clipped_samples — drive it to 0. peak_dbfs saturates at 0.0 and shows NO gradient; never iterate on peak alone.
  - Final render targets: clipped_samples == 0, peak_dbfs in [-6, -0.5], lufs_integrated in [-18, -9].
  - Fix balance at the source (track gainDb / velocities); use masterGainDb (-2..-5) for bus-level headroom; the limiter catches transient stacks.
---
# Gain staging + the analysis loop (v2 — post agent_beat forensics)

What we learned the hard way: bar-downbeat transients from multiple tracks land sample-aligned and
sum past full scale even when every track is individually clean. Per-track cuts play whack-a-mole.
The bus is where that battle is won: `masterGainDb` for level, the **limiter** for the last 1-2 dB
of transient stack.

Starting points that work: 808/kick 0 to -3 dB (the anchor), sampled drums -4 to -8 (GM samples are
hot), snare -4, hats -8 to -14, melodic/pads -8 to -14, masterGainDb -3, limiter ceiling -1.

Read analyze_wav like this:
- clipped_samples > 0 -> reduce masterGainDb by 2 OR confirm the limiter is last in master[]; re-render.
  (This number falls as you improve — trust its gradient.)
- peak_p999_dbfs near 0 but clipped_samples == 0 -> healthy loud master; done.
- lufs_integrated < -20 -> raise masterGainDb toward -1, keep limiter.
- band balance for dark genres: low > lowmid > mid; if high rivals mid, sampled hats/crash too hot.
- One change per iteration. Stop when hard targets above are met — typically 1-2 iterations now.
