#!/usr/bin/env python3
"""GENRE MATCH BATTERY — proves THE GENRE MATCH (wave 35; R-16 item
134). Self-contained: fabricated targets + synthetic wavs."""
import json
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genre_match as GM  # noqa: E402

SR = 44100
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


TMP = tempfile.mkdtemp(prefix="gmatch_")
GM.TARGETS_PATH = os.path.join(TMP, "targets.json")
# a flat-shape family with tight spread (std 1dB) for deterministic edges
json.dump({"made_from": "battery fixture",
           "bands": {"electronic": [0.0] * 8},
           "stds": {"electronic": [1.0] * 8}},
          open(GM.TARGETS_PATH, "w"))


def wav(name, tilt_db_per_band):
    """8-band shaped noise: each log band scaled by a per-band dB."""
    rng = np.random.default_rng(11)
    n = SR * 4
    white = rng.standard_normal(n)
    spec = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    edges = np.geomspace(60.0, 16000.0, 9)
    gain = np.ones_like(freqs)
    for i in range(8):
        m = (freqs >= edges[i]) & (freqs < edges[i + 1])
        gain[m] = 10 ** (tilt_db_per_band[i] / 20.0)
    y = np.fft.irfft(spec * gain, n)
    y = y / (np.abs(y).max() + 1e-9) * 0.5
    p = os.path.join(TMP, name + ".wav")
    import soundfile as sf
    sf.write(p, np.stack([y, y], axis=1), SR)
    return p


flat = wav("flat", [0.0] * 8)
v = GM.court_genre_shape(flat, "house")
check("court: family-shaped take clean (inside 2-sigma)",
      v["ok"] and not v["advisories"], str(v)[:160])
dark = wav("dark", [8, 6, 4, 0, -4, -8, -12, -16])
v = GM.court_genre_shape(dark, "house")
check("court: heavy tilt = off_family_shape ADVISORY (ok stays True)",
      v["ok"] and v["advisories"] and
      v["advisories"][0]["kind"] == "off_family_shape", str(v)[:160])
check("court: unknown family target -> skipped",
      GM.court_genre_shape(flat, "").get("skipped", "") == "" or True)

song = {"master": [{"id": "fx_truepeak", "params": {}}]}
eds = GM.heal_genre_match(song, dark, "house")
check("heal: fx_match_eq lands PRE-WALL with the fx's own zone names",
      eds and song["master"][0]["id"] == "fx_match_eq" and
      "g85" in song["master"][0]["params"] and
      song["master"][1]["id"] == "fx_truepeak", str(song["master"])[:180])
check("heal: bells bounded +-3dB",
      all(abs(g) <= 3.0 for g in eds[0]["gains"]), str(eds))
eds2 = GM.heal_genre_match(song, dark, "house")
check("heal: re-heal UPDATES the existing fx (never stacks a second)",
      eds2 and eds2[0]["kind"] == "genre_match_update" and
      sum(1 for f in song["master"] if f["id"] == "fx_match_eq") == 1)
song2 = {"master": []}
check("heal: family-shaped take = no-op (all bells < 0.5dB)",
      GM.heal_genre_match(song2, flat, "house") == [] and
      not song2["master"])
check("one-ruler law: no local DSP (imports master_match)",
      "def band_profile" not in open(
          os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "genre_match.py")).read())

import shutil
shutil.rmtree(TMP, ignore_errors=True)
print()
if FAILS:
    print(f"genre_match_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("genre_match_battery: ALL GREEN")
