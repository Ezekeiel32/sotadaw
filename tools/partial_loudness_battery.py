#!/usr/bin/env python3
"""PARTIAL LOUDNESS BATTERY — wave 81 (item 189). Synthetic, pure."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import partial_loudness as PL  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


SR = 22050
t = np.arange(SR * 3) / SR
rng = np.random.RandomState(9)


def bandnoise(lo, hi, level=0.3):
    n = rng.randn(len(t))
    S = np.fft.rfft(n)
    f = np.fft.rfftfreq(len(t), 1 / SR)
    S[(f < lo) | (f > hi)] = 0
    x = np.fft.irfft(S, len(t)).real
    return x / max(np.abs(x).max(), 1e-9) * level


vocal = bandnoise(800, 3200, 0.3)
r = PL.mur(vocal, np.zeros_like(vocal), SR)
check("no masker: the stem reads full (MUR > 0.95)", r["mur"] > 0.95,
      str(r["mur"]))
r_b = PL.mur(vocal, bandnoise(50, 10000, 0.9) * 3.0, SR)
check("loud broadband masker: heavy loss (MUR < 0.35)",
      r_b["mur"] < 0.35, str(r_b["mur"]))
r_c = PL.mur(vocal, bandnoise(30, 150, 0.9) * 3.0, SR)
check("FREQUENCY SELECTIVITY: a sub-only masker leaves the 1-3k vocal "
      "readable (MUR > 0.6, and >> broadband)",
      r_c["mur"] > 0.6 and r_c["mur"] > r_b["mur"] + 0.3,
      f"sub {r_c['mur']} vs broad {r_b['mur']}")
r_d = PL.mur(vocal, bandnoise(900, 2800, 0.9) * 2.0, SR)
check("band_loss NAMES the collision zone (inside the vocal's band)",
      any(700 <= b["band_hz"][0] <= 3500 for b in r_d["band_loss"]),
      str(r_d["band_loss"][:2]))
r_e = PL.mur(vocal, bandnoise(50, 10000, 0.9) * 30.0, SR)
check("the 10% red line: an overwhelming masker goes RED",
      r_e["red"] and r_e["mur"] < PL.RED_LINE, str(r_e["mur"]))
check("empty target: no fake number",
      PL.mur(np.zeros(SR), vocal[:SR], SR)["mur"] in (None, 0.0))

print()
if FAILS:
    print(f"partial_loudness_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("partial_loudness_battery: ALL GREEN")
