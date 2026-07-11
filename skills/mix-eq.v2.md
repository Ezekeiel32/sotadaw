---
name: mix-eq
version: 2
kind: mixing
tags: [always, eq, comp, mix]
hard_constraints:
  - EQ is a set_track_fx entry with NO id - {"type":"eq","params":{...}} - and master[] accepts it too.
  - COMPRESSION is fx_comp (faust insert). {"type":"comp"} is DEAD WIRING - its native ratio clamps every friendly value to 1:1, zero GR (render-verified 2026-07-10) - never write it.
  - eq params (real units) - loFreq/loGain (low shelf), hiFreq/hiGain (high shelf), midFreq/midGain/midQ (bell 1), midFreq2/midGain2/midQ2 (bell 2). Gains in dB (+-9 sane), freqs in Hz.
  - fx_comp params - thresh (dB), ratio (honest N:1), attack (ms), release (ms), makeup (dB). Stereo-linked peak detector; ratio 1 = bypass.
  - Cut before boost. Never boost lows on two low-end tracks at once (pick the anchor).
---
# EQ + compression recipes (agent-ready)

- **Kick vs 808 carve**: on the 808, eq bell midFreq 60-80, midGain -3, midQ 2 where the kick thumps;
  kick keeps the click (no high cut).
- **Mud cut**: pads/keys/chants - bell midFreq 250-350, midGain -3..-5, midQ 1.2. The #1 clarity move.
- **Air**: lead/hats bus - hiFreq 8000-10000, hiGain +2..+4. Never on the master AND a track at once.
- **De-boom**: sampled kits - loFreq 90, loGain -2 on non-drum tracks that leak low end.
- **Glue comp** (bus or busy track): fx_comp thresh -18..-24, ratio 2-3, attack 10-30 (let transients pass),
  release 100-200, makeup = roughly half of what you're compressing away.
- **Snare crack comp**: fx_comp thresh -20, ratio 4, attack 5, release 80, makeup +3-6
  (or shape attack/tail directly with fx_transient — no threshold to tune).
- Verify with analyze_wav bands: the move should SHOW in band_energy_pct; if it doesn't, it wasn't real.
