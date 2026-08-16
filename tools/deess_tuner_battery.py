#!/usr/bin/env python3
"""DE-ESS TUNER BATTERY — proves THE DE-ESS TUNER (wave 42; R-12 item
129). Synthetic voice: vowel hums + fricative bursts at a KNOWN center.
(deess_battery.py, Jul 10, proves the FX itself through m1 — this
proves the AIMING kernel.)"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deess_tuner as DT  # noqa: E402

SR = 44100
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def voice(s_center=6500.0, secs=6.0, s_every=0.5, s_len=0.12):
    """Alternating vowel tone (220Hz + partials) and band-noise esses."""
    rng = np.random.default_rng(9)
    n = int(secs * SR)
    t = np.arange(n) / SR
    y = 0.3 * np.sin(2 * np.pi * 220 * t) + \
        0.15 * np.sin(2 * np.pi * 440 * t) + \
        0.08 * np.sin(2 * np.pi * 660 * t)
    k = 0.0
    while k + s_len < secs:
        i0, i1 = int(k * SR), int((k + s_len) * SR)
        nz = rng.standard_normal(i1 - i0)
        spec = np.fft.rfft(nz)
        fr = np.fft.rfftfreq(i1 - i0, 1 / SR)
        spec[np.abs(fr - s_center) > 900] = 0
        burst = np.fft.irfft(spec, i1 - i0)
        burst = burst / (np.abs(burst).max() + 1e-9) * 0.5
        y[i0:i1] = burst                     # the ess replaces the vowel
        k += s_every
    return y


v = DT.sibilant_center(voice(6500.0), SR)
check("kernel: 6.5kHz esses measure ~6.5kHz",
      abs(v.get("center_hz", 0) - 6500) < 400, str(v))
check("kernel: sibilant fraction sane (esses are ~24% of time)",
      0.1 <= v.get("frac", 0) <= 0.45, str(v))
v = DT.sibilant_center(voice(8000.0), SR)
check("kernel: an 8kHz voice measures high (the female class)",
      abs(v.get("center_hz", 0) - 8000) < 450, str(v))
check("kernel: pure vowels = no sibilant frames",
      DT.sibilant_center(
          0.3 * np.sin(2 * np.pi * 220 *
                       np.arange(SR * 4) / SR), SR)
      .get("skipped", "").startswith("no sibilant"))

import soundfile as sf  # noqa: E402
import tempfile  # noqa: E402
TMP = tempfile.mkdtemp(prefix="deess_tune_")
wav = os.path.join(TMP, "vox.wav")
y = voice(7200.0)
sf.write(wav, np.stack([y, y], axis=1), SR)

song = {"tracks": [{"name": "lead_vocals",
                    "fx": [{"id": "fx_deess",
                            "params": {"freq": 5500, "thresh": -30}}],
                    "notes": [{"start": 0}]}]}
v = DT.court_deess(song, wav)
check("court: 5.5kHz aim vs a 7.2kHz voice CONVICTED (mis-aimed)",
      not v["ok"] and v["flags"][0]["kind"] == "deess_misaimed", str(v))
eds = DT.heal_deess(song, v)
check("heal: fx_deess re-aimed at the measured center",
      eds and abs(song["tracks"][0]["fx"][0]["params"]["freq"] - 7200)
      < 450 and DT.court_deess(song, wav)["ok"], str(eds))
song2 = {"tracks": [{"name": "vox", "notes": [{"start": 0}]}]}
v = DT.court_deess(song2, wav)
check("court: sibilant stem with NO deess = chain-order advisory",
      v["ok"] and v["advisories"] and
      v["advisories"][0]["kind"] == "no_deess", str(v))
check("court: no vocal lane -> skipped",
      DT.court_deess({"tracks": [{"name": "kick"}]}, wav)
      .get("skipped", "").startswith("no vocal"))

import shutil
shutil.rmtree(TMP, ignore_errors=True)
print()
if FAILS:
    print(f"deess_tuner_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("deess_tuner_battery: ALL GREEN")
