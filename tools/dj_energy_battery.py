#!/usr/bin/env python3
"""DJ ENERGY + TRANSITION-CATALOG BATTERY (wave 50; items 164/165).
Pure — synthetic signals, no renders."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import dj_listener as DL  # noqa: E402
import dj_set as DS  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


SR = 22050


def peak_deck(sec=20):
    """Loud, dense (4 hits/s), sub-heavy, bright — peak-techno-shaped."""
    t = np.arange(int(SR * sec)) / SR
    x = 0.28 * np.sin(2 * np.pi * 55 * t)              # sub floor
    x += 0.05 * np.random.RandomState(7).randn(len(t))  # bright bed
    for h in np.arange(0.0, sec, 0.25):                 # 4/s transient hits
        i = int(h * SR)
        n = int(0.03 * SR)
        if i + n < len(x):
            x[i:i + n] += 0.5 * np.exp(-np.arange(n) / (0.004 * SR))
    return np.clip(x, -1, 1)


def melodic_deck(sec=20):
    """Quiet, sparse, mid-register sine pad — melodic-house-shaped."""
    t = np.arange(int(SR * sec)) / SR
    x = 0.06 * np.sin(2 * np.pi * 440 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.25 * t))
    return x


# ------------------------------------------------- 164 the energy ear
e_hi = DL.deck_energy(peak_deck(), SR)
e_lo = DL.deck_energy(melodic_deck(), SR)
check("energy: peak deck outranks melodic deck by >=3 (same 'bpm')",
      e_hi is not None and e_lo is not None and e_hi - e_lo >= 3,
      f"peak={e_hi} melodic={e_lo}")
check("energy: scores live on the 1-10 ladder",
      1 <= e_lo <= 10 and 1 <= e_hi <= 10, f"{e_lo},{e_hi}")
check("energy: silence/too-short = None (never a fake number)",
      DL.deck_energy(np.zeros(SR * 4), SR) is None and
      DL.deck_energy(np.zeros(100), SR) is None)

check("MIK parse: '2A - Energy 7' is authoritative",
      DL.parse_mik_energy("2A - Energy 7") == 7)
check("MIK parse: clamps to 1-10, absent = None",
      DL.parse_mik_energy("energy 14") == 10 and
      DL.parse_mik_energy("8A") is None and
      DL.parse_mik_energy(None) is None)

# --------------------------------------- 164 planning decouples from BPM
# three decks, SAME bpm, energies force the arc: peak wants the 9 late
items = [(128.0, "8A", 1.0), (128.0, "8A", 1.0), (128.0, "8A", 1.0)]
order, _ = DS.plan_order(items, "peak", energies=[9, 3, 6])
check("plan: same-bpm decks ORDER BY ENERGY on a peak arc (3->6->9)",
      [9, 3, 6][order[-1]] == 9 and [9, 3, 6][order[0]] == 3, str(order))
order2, _ = DS.plan_order(items, "peak", energies=None)
check("plan: no energies = bpm fallback (identical items -> identity)",
      order2 == [0, 1, 2], str(order2))

# ------------------------------------------------- 165 the catalog
check("catalog: house<->house = long layered blend (32 bars)",
      DS.choose_transition("deep house", "funky house")[0] == "blend" and
      DS.choose_transition("deep house", "funky house")[1] == 32)
check("catalog: trance<->trance carries the breakdown-to-breakdown note",
      "breakdown" in DS.choose_transition("psytrance", "goa trance")[2])
check("catalog: dnb<->dnb switches SHORT (8 bars)",
      DS.choose_transition("jungle", "dnb")[1] == 8)
check("catalog: open-format cuts hard (echo_out, 4 bars)",
      DS.choose_transition("hip hop", "trap")[0] == "echo_out")
check("catalog: cross-family default = echo-out cut",
      DS.choose_transition("techno", "drill")[0] == "echo_out")
check("catalog: unknown genre = None -> tempo law holds",
      DS.choose_transition(None, "house") is None and
      DS.choose_transition("zzz", "house") is None)
check("family: words route (uk garage->house, schranz->techno, "
      "halftime->dnb)",
      DS._family("uk garage") == "house" and
      DS._family("schranz") == "techno" and
      DS._family("halftime") == "dnb")

# ------------------------------------------------ w80 phrase cuts (038)
check("phrase(038): _snap_cut prefers the real seam inside the window",
      DS._snap_cut(112.0, [64.0], 128.0, window_beats=64) == (64.0, 64.0))
check("phrase: no seam in window = blind math stands (fail-open)",
      DS._snap_cut(112.0, [8.0], 128.0) == (112.0, None) and
      DS._snap_cut(112.0, [], 128.0) == (112.0, None))
check("phrase: seams past the deck end never cut",
      DS._snap_cut(112.0, [200.0], 128.0) == (112.0, None))

print()
if FAILS:
    print(f"dj_energy_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("dj_energy_battery: ALL GREEN")
