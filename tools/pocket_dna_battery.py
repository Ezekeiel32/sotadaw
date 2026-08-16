#!/usr/bin/env python3
"""POCKET DNA battery (P13/R-3) — the measured-feel kernel holds its studies.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pocket_dna as PD  # noqa: E402
import groove as GR  # noqa: E402

N = [0]


def ok(cond, msg):
    N[0] += 1
    if not cond:
        print(f"FAIL #{N[0]}: {msg}")
        sys.exit(1)


# the interpolation passes THROUGH the cited corpus points (the r-3 agent's
# own linear formula contradicted them — the points are the law)
ok(PD.swing_ratio_jazz(100) == 3.5, "jazz 3.5:1 at 100")
ok(abs(PD.swing_ratio_jazz(132) - 2.38) < 1e-9, "jazz 2.38:1 at 132 (cited)")
ok(abs(PD.swing_ratio_jazz(150) - 2.0) < 1e-9, "jazz 2:1 at 150 (cited)")
ok(abs(PD.swing_ratio_jazz(200) - 1.5) < 1e-9, "jazz 1.5:1 at 200 (cited)")
ok(PD.swing_ratio_jazz(300) == 1.0, "jazz 1:1 by 300")
ok(PD.swing_ratio_jazz(90) == 3.5, "clamped slow")
for a, b in zip(range(90, 290, 10), range(100, 300, 10)):
    ok(PD.swing_ratio_jazz(a) >= PD.swing_ratio_jazz(b), f"monotone {a}->{b}")

# MPC swing conversions (58% @120bpm = +20ms = 0.04 beats; 50% = straight)
ok(PD.mpc_offset_beats(50) == 0.0, "50% straight")
ok(abs(PD.mpc_offset_beats(58) - 0.04) < 1e-9, "58% = 0.04 beats")
ok(abs(PD.ms_to_beats(PD.mpc_offset_beats(58) / PD.ms_to_beats(1, 120), 120)
       - PD.mpc_offset_beats(58)) < 1e-9, "ms/beats round-trip")
ok(abs(PD.swing_ratio_to_pct(2.0) - 66.666) < 0.01, "2:1 = 66.7%")
ok(PD.swing_ratio_to_pct(1.0) == 50.0, "1:1 = 50%")

# role timing: funk kick AHEAD (on top), dilla snare DRAGS, dilla bass anticipates
ok(PD.role_timing_beats("funk", "kick", 100) < 0, "funk kick on top (ahead)")
ok(PD.role_timing_beats("dilla", "snare", 92) > 0.05, "dilla snare drags")
ok(PD.role_timing_beats("dilla", "bass", 92) < -0.1, "dilla bass anticipates ~32nd")
ok(PD.role_timing_beats("nope", "kick", 120) == 0.0, "unknown family = grid")

# velocity grammar in researched MIDI windows
ok(0.15 <= PD.ghost_vel(0.0) <= 0.36 and 0.15 <= PD.ghost_vel(1.0) <= 0.36,
   "ghosts 20-45 MIDI")
ok(0.78 <= PD.backbeat_vel() <= 0.88, "backbeat 100-110")
ok(PD.accent_vel() >= 0.94, "accents 120+")
ok(0.03 <= PD.hat_spread() <= 0.09, "subtle hat spread 5-10")

# THE CEILING LAW: humanize = 40-60% of natural SD, never more
h = PD.humanize_sd_beats("funk", 120, scale=0.9)   # asked too much
ok(h <= PD.ms_to_beats(16.0 * 0.6, 120) + 1e-9, "ceiling clamps at 60%")
ok(PD.humanize_sd_beats("jazz", 150) > PD.humanize_sd_beats("funk", 150),
   "jazz natural SD > funk (27 vs 16 ms)")

# samba: 3rd and 4th 16ths AHEAD, long-fourth pattern
so = PD.samba_offsets_beats()
ok(so[0] == 0.0 and so[2] < so[1] < 0 and so[3] < so[2], f"samba lilt {so}")

# jembe ternary onsets inside one beat, ordered
jo = PD.jembe_onsets_beats()
ok(jo[0] == 0.0 and 0 < jo[1] < jo[2] < 1.0, f"jembe ternary {jo}")

# research profiles landed in the groove atlas, well-formed + stamped
for name in ("funk_ontop", "samba_16th", "neosoul_drag"):
    g = GR.GROOVES[name]
    ok(len(g["off"]) == 16 and len(g["vel"]) == 16, f"{name} 16 slots")
    ok(g["prov"].startswith("research:R-3"), f"{name} provenance stamped")
    ok(all(abs(o) < 0.2 for o in g["off"]), f"{name} offsets sane")
ok(GR.GROOVES["samba_16th"]["off"][3] == -0.056, "samba long-fourth exact")
ok(GR.GROOVES["neosoul_drag"]["off"][4] > 0.06, "neosoul backbeat drag")

print(f"POCKET DNA BATTERY PASS — {N[0]} checks green")
