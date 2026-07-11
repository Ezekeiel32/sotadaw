---
name: mix-headroom
version: 8
kind: mixing
tags: [always, mix, gain-staging, loudness, mastering, verdict]
hard_constraints:
  - "AUTO-FIRST (v7): when asked to master / finish / make it loud, call auto_master(song, genre) BEFORE hand-tuning — it normalizes the chain and converges trims/ceiling/band moves in 2-7 renders, returning moves + before/after + the full verdict. Reference mastering: auto_master(song, reference=<wav>) sits the track in THAT record's LUFS window and tilt."
  - "THE VERDICT LOOP: after auto_master (or any hand edit), master_report(song, genre) is the ship gate — fix the fix_first check using its hint, repeat until pass:true. auto_master failures are SOURCE problems by construction (it exhausts the legal bus moves): fix track gains/notes/parts, then re-run."
  - "MASTER CHAIN LAW (v8 — the release wall): end every master with fx_truepeak: \"master\": [..., {\"id\": \"fx_truepeak\", \"params\": {\"ceiling\": -1.2}}]. ceiling means OUTPUT dBTP (4x-oversampled BS.1770 detector; measured: music lands -1.27 dBTP at -1.2 stated, and it refunds ~+2 LUFS vs the old -3.0 sample-ceiling insurance). fx_brickwall is ISP-blind LEGACY — finish()/auto_master upgrade it in place. NEVER type \"limiter\" (master_limiter's ceiling is non-functional - floats sail past 0 dBFS and clip at the file write)."
  - "masterGainDb stays 0. It runs AFTER the whole master chain (post-limiter gain re-opens the headroom you just limited). ALL level staging happens INSIDE the chain with fx_trim: {\"id\": \"fx_trim\", \"params\": {\"level\": <dB>}}."
  - "SUB-DOMINANT LAW (amapiano vignette 2026-07-03): genres whose energy lives in the sub need deeper true-peak headroom — use fx_truepeak ceiling -1.5 to -2.0 when the low band dominates (auto_master applies this automatically)."
  - "QUIET-LANE LAW (ambient vignette 2026-07): on sparse/quiet masters (genre window top <= -12 LUFS) fx_saturate LOWPASSES the master and eats gain — recover with trim -> makeup trim -> fx_truepeak, no saturator. auto_master applies this automatically."
  - "Loudness recovery on a clean-but-quiet DENSE master: fx_trim (input, +dB) -> fx_saturate (density; mix 1.0 FULL WET - a partial dry path leaks uncompressed transients around the tanh) -> fx_trim (makeup) -> fx_truepeak. Iterate the trims, never the ceiling."
  - Convergence signal is clipped_samples - drive it to 0. peak_dbfs saturates at 0.0 and shows NO gradient; never iterate on peak alone.
  - Saturation adds LEVEL - after adding fx_saturate to a track, trim that track's gainDb by 4-6 dB.
---
# Gain staging + mastering (v8 - the release wall)

v4 lesson: the old master_limiter never limited; masterGainDb runs POST-chain.
v6 made the judge a tool (master_report). v7 made the mastering engineer a tool.
**v8 names the wall honestly: fx_truepeak IS the release wall** — its ceiling is
OUTPUT dBTP, so you stop paying the -3.0 "insurance" a sample-blind brickwall
demanded and get the loudness back (+2 LUFS measured on the battery). Chains that
still end in fx_brickwall are legacy-ok: finish() and auto_master upgrade them
in place; you never have to hand-migrate.

`auto_master(song, genre)` — deterministic closed loop, no model in the numeric path:
1. Chain normalized: character inserts preserved in place, legacy limiters killed,
   masterGainDb folded into the input trim, trim->saturate->trim->truepeak tail
   ensured (saturator skipped on quiet lanes; adopted brickwalls upgraded).
2. Iterates render->measure->adjust: ceiling from true peak + sub-dominant law; makeup
   trim walks LUFS into the genre window (excess spills into input trim = density);
   band order gets capped +/-3 dB eq nudges, then an on-genre DARK FILTER walk
   (2500 -> 900 -> 350 Hz — the recorded ambient fix) when the target is led by
   low/lowmid.
3. Stops at pass or when legal bus moves are exhausted — the note + report hints then
   name the SOURCE fixes (track gains, note density, part brightness). Never fakes
   balance at the bus beyond the caps.

The division of labor: auto_master owns the BUS. You own the SOURCES and the taste —
character inserts (one per song section, see fx-usage), the arrangement's motion,
what the hints tell you to change in the tracks. After sources change, re-run
auto_master (idempotent: it adopts its own managed eq/filter and re-tunes them).

`auto_master(song, reference="path/to/record.wav")` = "make it sit like THIS":
LUFS window +/-1.5 LU around the record, band order read off its spectrum.

Ship gate: master_report pass:true, then hear (structure) for the parts numbers
can't judge. Starting track gains still apply: 808/kick 0..-3 (anchor), sampled
drums -4..-8, snare -4, hats -8..-14, melodic/pads -8..-14.
