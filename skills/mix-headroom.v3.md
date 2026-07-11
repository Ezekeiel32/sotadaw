---
name: mix-headroom
version: 3
kind: mixing
tags: [always, mix, gain-staging, loudness]
hard_constraints:
  - Always end the master chain with the limiter: "master": [{"type": "limiter", "params": {"ceiling": -1.0}}].
  - Convergence signal is clipped_samples — drive it to 0. peak_dbfs saturates at 0.0 and shows NO gradient; never iterate on peak alone.
  - true_peak_dbtp must be <= -1.0 on the final render (inter-sample overs distort on real converters).
  - THE LOUDNESS-RECOVERY LAW (final step, always) — after the mix is CLEAN (clipped 0, dBTP <= -1), compare lufs_integrated to the genre window; if below, raise masterGainDb by (window_mid - LUFS) dB, up to +6, INTO the limiter and re-render. A clean-but-quiet master FAILS the genre. Never fix loudness by removing per-track trims.
  - Saturation adds LEVEL — after adding fx_saturate to a track, trim that track's gainDb by 4-6 dB (drive is tone, gain is level).
  - Final render targets: clipped_samples == 0, true_peak_dbtp <= -1.0, lufs_integrated inside the genre window (default [-16, -9] when no genre skill specifies).
---
# Gain staging + the analysis loop (v3 — adds the loudness-recovery law, eval-derived)

v2 lesson (agent_beat forensics): bar-downbeat transients from multiple tracks sum past full
scale even when each track is clean. The bus wins that battle: `masterGainDb` for level, the
**limiter** for the last 1-2 dB of transient stack.

v3 lesson (phonk+psytrance evals, 2026-07-02): agents learned to trim so well they shipped
QUIET — clean masters 2-3 dB under the genre LUFS window. Loudness is recovered at the BUS,
never by undoing trims: push masterGainDb INTO the limiter (ceiling -1 makes it safe),
re-render, re-measure. That's how records get loud without clipping.

Starting points that work: 808/kick 0 to -3 dB (the anchor), sampled drums -4 to -8, snare -4,
hats -8 to -14, melodic/pads -8 to -14, masterGainDb -3, limiter ceiling -1. After fx_saturate
anywhere: that track -4 to -6.

Read analyze_wav like this:
- clipped_samples > 0 -> reduce masterGainDb by 2 OR confirm the limiter is last; re-render.
- true_peak_dbtp > -1 -> same treatment as clipping (it IS clipping, downstream).
- CLEAN but lufs below window -> masterGainDb += (window_mid - LUFS), cap +6, re-render (THE LAW).
- band balance for dark genres: low > lowmid > mid; if high rivals mid, sampled hats/crash too hot.
- rms_by_quarter / centroid_by_quarter: confirm your automation MOVES (flat gradient = curve didn't land).
- One change per iteration; typically 2-3 iterations to loud-and-clean.
