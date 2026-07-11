---
name: mix-eq
version: 1
kind: mixing
tags: [always, eq, comp, mix]
hard_constraints:
  - EQ and compression are set_track_fx entries with NO id, just type - {"type":"eq","params":{...}} / {"type":"comp","params":{...}} - and master[] accepts the same types.
  - eq params (real units) - loFreq/loGain (low shelf), hiFreq/hiGain (high shelf), midFreq/midGain/midQ (bell 1), midFreq2/midGain2/midQ2 (bell 2). Gains in dB (+-9 sane), freqs in Hz.
  - comp params - threshold (dB), ratio, attack (ms), release (ms), outputDb (makeup).
  - Cut before boost. Never boost lows on two low-end tracks at once (pick the anchor).
---
# EQ + compression recipes (the built-ins, agent-ready)

- **Kick vs 808 carve**: on the 808, eq bell midFreq 60-80, midGain -3, midQ 2 where the kick thumps;
  kick keeps the click (no high cut).
- **Mud cut**: pads/keys/chants - bell midFreq 250-350, midGain -3..-5, midQ 1.2. The #1 clarity move.
- **Air**: lead/hats bus - hiFreq 8000-10000, hiGain +2..+4. Never on the master AND a track at once.
- **De-boom**: sampled kits - loFreq 90, loGain -2 on non-drum tracks that leak low end.
- **Glue comp** (bus or busy track): threshold -18..-24, ratio 2-3, attack 10-30ms (let transients pass),
  release 100-200ms, outputDb = roughly half of what you're compressing away.
- **Snare crack comp**: threshold -20, ratio 4, attack 5ms, release 80ms, outputDb +3-6.
- Verify with analyze_wav bands: the move should SHOW in band_energy_pct; if it doesn't, it wasn't real.
