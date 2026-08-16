#!/usr/bin/env python3
"""LAYER BATTERY — proves THE LAYER COURT (wave 37; R-18 item 022).
Synthetic one-shots, pure numpy."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layer_court as LY  # noqa: E402

SR = 44100
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def shot(f, decay_s, secs=0.6, noise=0.0, hp=False, delay_ms=0.0):
    n = int(secs * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(5)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / decay_s)
    if noise > 0:
        nz = rng.standard_normal(n) * np.exp(-t / decay_s) * noise
        if hp:
            spec = np.fft.rfft(nz)
            fr = np.fft.rfftfreq(n, 1 / SR)
            spec[fr < 2000] = 0
            nz = np.fft.irfft(spec, n)
        y = y + nz
    k = int(delay_ms * SR / 1000.0)
    if k:
        y = np.concatenate([np.zeros(k), y[:-k]])
    return y * 0.7


sub = shot(50, 0.4)                                 # sub boom
click = shot(3000, 0.01, noise=0.8, hp=True)        # click/top layer
v = LY.compat(sub, click, SR)
check("compat: sub boom + click = COMPLEMENT (each owns its band)",
      v["verdict"] == "complement" and v["owned_a"] == "sub" and
      v["owned_b"] in ("himid", "air"), str(v))
v = LY.compat(sub, shot(52, 0.4), SR)
check("compat: two subs = FIGHT (same band, same transient)",
      v["verdict"] == "fight" and v["overlap"] > 0.8 and
      v["attack_sim"] > 0.6, str(v))
body = shot(150, 0.12)
v = LY.compat(sub, body, SR)
check("compat: sub + body land in the middle (carve-then-stack class)",
      v["verdict"] in ("workable", "complement"), str(v))
tau = LY.transient_align(sub, shot(50, 0.4, delay_ms=5.0), SR)
check("align: a 5ms-late layer measures ~+5ms", 3.5 <= tau <= 6.5,
      str(tau))
fa = LY.band_fractions(sub, SR)
check("bands: fractions sum to 1 and the sub owns band 1",
      abs(float(fa.sum()) - 1.0) < 1e-6 and int(np.argmax(fa)) == 0,
      str([round(float(x), 3) for x in fa]))
check("compat: too-short shot skipped",
      LY.compat(np.zeros(64), sub, SR).get("skipped", "").startswith("one"))
check("one-resolver: the count law stays groove_court's (not re-encoded)",
      "court_layering" not in open(os.path.join(
          os.path.dirname(os.path.abspath(__file__)),
          "layer_court.py")).read().replace(
          "groove_court.court_layering", ""))
check("determinism", LY.compat(sub, click, SR) == LY.compat(sub, click, SR))

print()
if FAILS:
    print(f"layer_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("layer_battery: ALL GREEN")
