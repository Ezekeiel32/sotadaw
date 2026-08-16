#!/usr/bin/env python3
"""TRANSLATION BATTERY — proves THE TRANSLATION COURTS (wave 22; R-7
119/190/191/232). Synthetic masters, deterministic."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import translation_court as TC  # noqa: E402

SR = 44100
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def pink_like(secs, tilt_db_per_oct=-6.0, seed=7):
    """Noise with a chosen spectral tilt (dB/oct), deterministic."""
    rng = np.random.default_rng(seed)
    n = int(secs * SR)
    white = rng.standard_normal(n)
    spec = np.fft.rfft(white)
    f = np.fft.rfftfreq(n, 1.0 / SR)
    f[0] = f[1]
    # power tilt: amplitude gain = 10^(tilt/20 * log2(f/100)); clamp the
    # sub-30Hz skirt so extreme tilts don't dump all power below audio
    gain = 10 ** ((tilt_db_per_oct / 20.0) * np.log2(np.maximum(f, 30.0)
                                                     / 100.0))
    y = np.fft.irfft(spec * gain, n)
    return y / (np.abs(y).max() + 1e-9) * 0.5


# --------------------------------------------------------------- kernels
y = pink_like(6.0, -6.0)
_, _, slope = TC.ltas(y, SR)
check("ltas: planted -6dB/oct measures within +-1", abs(slope + 6) < 1.0,
      str(slope))
y = pink_like(6.0, -12.0)
_, _, s2 = TC.ltas(y, SR)
check("ltas: planted -12dB/oct measures darker", s2 < slope - 3, str(s2))
b = TC.bands5(pink_like(6.0, -18.0), SR)
check("bands5: very dark noise = low-heavy", b["low"] > 60, str(b))
br_dark = TC.brightness(pink_like(6.0, -15.0), SR)
br_brt = TC.brightness(pink_like(6.0, -2.5), SR)
check("brightness (232): roll-off separates dark from bright",
      br_brt["rolloff_85_hz"] > br_dark["rolloff_85_hz"] * 3,
      f"{br_dark} vs {br_brt}")

# ------------------------------------------------------------- tilt court
v = TC.court_tilt(None, "techno", measured=-7.0)
check("tilt: corpus-typical -7 passes", v["ok"] and not v["advisories"],
      str(v))
v = TC.court_tilt(None, "techno", measured=-1.0)
check("tilt: -1dB/oct (thin/harsh) CONVICTED beyond the corpus span",
      not v["ok"] and v["flags"][0]["kind"] == "tilt_extreme", str(v))
v = TC.court_tilt(None, "rock", measured=-12.5)
check("tilt: -12.5 inside hard band but off the live family = advisory",
      v["ok"] and v["advisories"] and
      v["advisories"][0]["kind"] == "tilt_offfamily", str(v))
song = {"master": [{"id": "fx_truepeak", "params": {}}]}
edits = TC.heal_tilt(song, TC.court_tilt(None, "", measured=-16.0))
check("tilt heal: too-dark master gets +2dB mid_high shelf PRE-WALL",
      edits and song["master"][0]["id"] == "fx_ms_eq" and
      song["master"][0]["params"]["mid_high"] == 2.0 and
      song["master"][1]["id"] == "fx_truepeak", str(song["master"]))
song = {"master": []}
edits = TC.heal_tilt(song, TC.court_tilt(None, "", measured=-1.0))
check("tilt heal: too-bright master tilts down",
      edits and song["master"][0]["params"]["mid_high"] == -2.0)

# ------------------------------------------------------------ bands court
v = TC.court_bands(None, "house", measured={"sub2050": 5, "low": 80,
                                            "lowmid": 15, "highmid": 4.5,
                                            "high": 0.5})
check("bands: corpus-typical house passes clean",
      v["ok"] and not v["advisories"], str(v))
v = TC.court_bands(None, "house", measured={"sub2050": 1, "low": 30,
                                            "lowmid": 40, "highmid": 26,
                                            "high": 4})
check("bands: 26% high-mid flood CONVICTED",
      not v["ok"] and v["flags"][0]["kind"] == "highmid_flood", str(v))
v = TC.court_bands(None, "drill", measured={"sub2050": 10, "low": 55,
                                            "lowmid": 38, "highmid": 6,
                                            "high": 1})
check("bands: 55% low in the deep_bass family = off-family advisory",
      v["ok"] and any(a["kind"] == "low_offfamily"
                      for a in v["advisories"]), str(v))

# --------------------------------------------------- width master court
import soundfile as sf  # noqa: E402
import tempfile  # noqa: E402
tmp = tempfile.mkdtemp(prefix="transl_")
t = np.arange(int(4 * SR)) / SR
sig = np.sin(2 * np.pi * 440 * t) * 0.4 + np.sin(2 * np.pi * 220 * t) * 0.3


def wav(name, l, r):
    p = os.path.join(tmp, name + ".wav")
    sf.write(p, np.stack([l, r], axis=1), SR)
    return p


v = TC.court_width_master(wav("mono", sig, sig))
check("width: mono-coherent master passes", v["ok"] and not v["advisories"],
      str(v))
v = TC.court_width_master(wav("flip", sig, -sig))
check("width: phase-flipped master CONVICTED",
      not v["ok"] and v["flags"][0]["kind"] == "phase_flip", str(v))
song = {"master": [{"id": "fx_widen", "params": {}},
                   {"id": "fx_truepeak", "params": {}}]}
edits = TC.heal_width_master(song, v)
check("width heal: master widener stripped",
      edits and all(f["id"] != "fx_widen" for f in song["master"]),
      str(song["master"]))

# ------------------------------------------------------------- aggregate
p = wav("agg", pink_like(4.0, -7.0), pink_like(4.0, -7.0, seed=7))
v = TC.court_translation(p, {"master": []}, "techno")
check("aggregate: lawful master fully ok + brightness rides",
      v["ok"] and "rolloff_85_hz" in v["brightness"], str(v)[:200])

import shutil
shutil.rmtree(tmp, ignore_errors=True)

print()
if FAILS:
    print(f"translation_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("translation_battery: ALL GREEN")
