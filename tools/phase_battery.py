#!/usr/bin/env python3
"""PHASE BATTERY — proves THE PHASE INTERLOCK (wave 36; R-5 item 254).
Synthetic stems, deterministic, pure numpy (~seconds)."""
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phase_court as PC  # noqa: E402

SR = 44100
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def boom(f, secs=6.0, bpm=120, amp=0.5, pol=1, shift_ms=0.0):
    n = int(secs * SR)
    y = np.zeros(n)
    t = np.arange(int(1.2 * SR)) / SR
    hit = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.5) * amp * pol
    k0 = int(shift_ms * SR / 1000.0)
    for b in range(0, 10):
        i = int(b * (60.0 / bpm) * SR) + k0
        if 0 <= i and i + len(hit) <= n:
            y[i:i + len(hit)] += hit
    return y


kick = boom(55.0, amp=0.6)

# constructive pair: in phase — the sum GAINS
r = PC.interlock(kick, boom(55.0, amp=0.5), SR)
check("kernel: in-phase pair gains (loss_db > 0)", r["loss_db"] > 3.0,
      str(r))
# destructive pair: inverted 808 — the sum LOSES, the flip recovers
r = PC.interlock(kick, boom(55.0, amp=0.5, pol=-1), SR)
check("kernel: inverted 808 = destructive (loss < -1dB)",
      r["loss_db"] < -1.0, str(r))
check("kernel: recovery finds the POLARITY flip",
      r["best"]["polarity"] == -1 and r["best"]["gain_db"] > 4.0, str(r))
# half-period shift at 55Hz ~ 9ms is out of the 1ms grid; a 0.5ms comb
# in-band still prefers a corrective offset
r = PC.interlock(kick, boom(55.0, amp=0.5, shift_ms=0.5), SR)
check("kernel: 0.5ms-shifted pair — the grid finds a better offset",
      abs(r["best"]["offset_ms"]) >= 0.1 and r["best"]["gain_db"] > 0.0,
      str(r))
check("kernel: silence overlap -> skipped",
      PC.interlock(kick, np.zeros(len(kick)), SR).get("skipped") ==
      "no overlap")

# ------------------------------------------------- stems court + the heal
TMP = tempfile.mkdtemp(prefix="phase_")
import soundfile as sf  # noqa: E402
sf.write(os.path.join(TMP, "00_kick.wav"),
         np.stack([kick, kick], axis=1), SR)
inv = boom(55.0, amp=0.5, pol=-1)
sf.write(os.path.join(TMP, "01_808.wav"), np.stack([inv, inv], axis=1), SR)
v = PC.court_phase(TMP)
check("court: destructive stems CONVICTED",
      not v["ok"] and v["flags"][0]["kind"] == "destructive_sum", str(v))
song = {"bpm": 120, "tracks": [
    {"name": "kick", "notes": [{"start": float(b), "len": 0.5,
                                "pitch": 36, "vel": 0.9}
                               for b in range(8)]},
    {"name": "808", "notes": [{"start": float(b), "len": 1.0, "pitch": 33,
                               "vel": 0.85} for b in range(8)]}]}
eds = PC.heal_phase(song, v)
check("heal: fx_polarity flip lands on the 808 lane",
      any(e["kind"] == "polarity_flip" for e in eds) and
      song["tracks"][1]["fx"][0]["id"] == "fx_polarity", str(eds))
check("heal: once per lane (phase_healed marker)",
      PC.heal_phase(song, v) == [])
ok_pair = boom(55.0, amp=0.5)
sf.write(os.path.join(TMP, "01_808.wav"),
         np.stack([ok_pair, ok_pair], axis=1), SR)
check("court: constructive stems pass", PC.court_phase(TMP)["ok"])
check("court: missing stems -> skipped",
      PC.court_phase(tempfile.mkdtemp(prefix="empty_"))
      .get("skipped", "").startswith("needs"))

# nudge path: verdict wanting only an offset moves notes by <=1ms
v2 = {"ok": False, "flags": [{"kind": "destructive_sum"}],
      "best": {"offset_ms": 0.5, "polarity": 1, "gain_db": 1.0}}
song2 = {"bpm": 120, "tracks": [
    {"name": "sub_808", "notes": [{"start": 0.0, "len": 1, "pitch": 33,
                                   "vel": 0.9}]}]}
eds = PC.heal_phase(song2, v2)
check("heal: offset-only recovery nudges notes (0.5ms -> 0.001 beats)",
      eds and eds[0]["kind"] == "nudge" and
      abs(song2["tracks"][0]["notes"][0]["start"] - 0.001) < 1e-6,
      str(eds))

import shutil
shutil.rmtree(TMP, ignore_errors=True)
print()
if FAILS:
    print(f"phase_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("phase_battery: ALL GREEN")
