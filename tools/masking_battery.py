#!/usr/bin/env python3
"""MASKING BATTERY — proves THE MASKING COURT (wave 21; R-6
052/053/054). Synthetic stems mirror the reference implementation's
self-tests: two tones inside 1 Bark must trip RED; an octave apart must
read GREEN; the persistence gate must pardon momentary overlaps."""
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import masking_court as MK  # noqa: E402

SR = 44100
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def tone(f, secs, amp, gate=None):
    t = np.arange(int(secs * SR)) / SR
    y = amp * np.sin(2 * np.pi * f * t)
    if gate is not None:
        on = (np.floor(t / gate) % 2) == 0
        y = y * on
    return y


# ---------------------------------------------------------- kernel sanity
check("bark: 1kHz ~ 8.5 Bark", abs(float(MK.bark(1000)) - 8.5) < 0.4,
      str(float(MK.bark(1000))))
up = float(MK.schroeder_spread(np.array([1.0]))[0])
down = float(MK.schroeder_spread(np.array([-1.0]))[0])
check("schroeder: upward spread gentler than downward (asymmetry law)",
      up > down, f"+1Bark {up:.1f} vs -1Bark {down:.1f}")
check("terhardt: quiet threshold dips near 3-4kHz",
      float(MK.terhardt_tq_db(3500)) < float(MK.terhardt_tq_db(200)))

# ---------------------------------------------------- MSR pair (item 052)
loud = tone(1000, 3.0, 0.5)
buried = tone(1080, 3.0, 0.01)          # inside 1 Bark, 34dB under
r = MK.msr_pair(buried, loud, SR)
check("msr: tone buried inside 1 Bark = heavy mask",
      r["mask_norm"] >= MK.MASK_RED and r["red_bands"], str(r))
free = tone(2000, 3.0, 0.25)            # octave up, healthy level
r2 = MK.msr_pair(free, loud, SR)
check("msr: octave-separated healthy tone = GREEN",
      r2["mask_norm"] < MK.MASK_AMBER, str(r2))
gated = tone(1080, 3.0, 0.01)
loud_gated = tone(1000, 3.0, 0.5, gate=0.15)   # masker only half the time
r3 = MK.msr_pair(gated, loud_gated, SR)
check("msr: intermittent masker -> persistence gate holds red bands down",
      len(r3["red_bands"]) <= len(r["red_bands"]), f"{r3} vs {r}")

# --------------------------------------------------- stems court + grades
tmp = tempfile.mkdtemp(prefix="mask_bat_")


def wav(name, y):
    import soundfile as sf
    sf.write(os.path.join(tmp, name + ".wav"),
             np.stack([y, y], axis=1), SR)


wav("pad_wall", tone(1000, 3.0, 0.5) + tone(1500, 3.0, 0.4)
    + tone(2200, 3.0, 0.3))
wav("lead_buried", tone(1080, 3.0, 0.012))
wav("bass_free", tone(110, 3.0, 0.3))
v = MK.court_masking_stems(tmp)
check("stems court: buried lead CONVICTED",
      not v["ok"] and any(f["track"] == "lead_buried"
                          for f in v["flags"]), str(v)[:220])
check("stems court: free bass not convicted",
      all(f["track"] != "bass_free" for f in v["flags"]))

# ------------------------------------------------------ heal ladder (053)
song = {"tracks": [
    {"name": "pad_wall", "gainDb": 0.0, "pan": 0.0, "notes": []},
    {"name": "lead_buried", "gainDb": 0.0, "pan": 0.0, "notes": []},
    {"name": "bass_free", "gainDb": 0.0, "notes": []}]}
edits = MK.heal_masking(song, v, tmp)
kinds = [e["kind"] for e in edits]
check("heal: ladder = level + pan + bell (source-first order)",
      kinds and kinds[0] == "level" and "bell_cut" in kinds and
      "pan_split" in kinds, str(edits))
pad = song["tracks"][0]
check("heal: masker ducked -2dB, bounded", pad["gainDb"] == -2.0)
bells = [f for f in pad.get("fx", []) if f["id"] == "fx_bell"]
tot = sum(abs(f["params"]["gain"]) for f in bells)
check("heal: bell cuts capped (<=3 bells, <=6dB total, q=2)",
      0 < len(bells) <= 3 and tot <= 6.0 and
      all(f["params"]["q"] == 2.0 for f in bells),
      f"{len(bells)} bells, {tot}dB")
check("heal: cuts land near the collision (~1080Hz)",
      any(800 <= f["params"]["freq"] <= 1400 for f in bells),
      str([f["params"]["freq"] for f in bells]))
song2 = {"tracks": [{"name": "pad_wall", "gainDb": 0.0, "pan": 0.0},
                    {"name": "lead_buried", "gainDb": 0.0, "pan": 0.0}]}
MK.heal_masking(song2, v, tmp)
check("heal: pan rung splits a centered pair",
      song2["tracks"][0].get("pan") == -0.2 and
      song2["tracks"][1].get("pan") == 0.2)

# ------------------------------------------- compose-time court (054)
def lane(name, pitch, n=16, vel=0.8, start0=0.0):
    return {"name": name, "notes": [
        {"start": start0 + i, "len": 0.9, "pitch": pitch, "vel": vel}
        for i in range(n)]}


# mud zone = 250-500Hz ~ MIDI 59-71; four lanes piled in = crowding
mud = {"lengthBars": 4, "tracks": [
    lane("pad", 60), lane("chords", 64), lane("organ", 62),
    lane("strings", 67)]}
v = MK.court_compose_masking(mud)
check("compose: FOUR lanes piled into 250-500Hz = mud_crowding advisory",
      any(a["kind"] == "mud_crowding" for a in v["advisories"]), str(v))
check("compose: advisory carries the register map",
      any("20-60" in a["why"] for a in v["advisories"]))
three = {"lengthBars": 4, "tracks": [
    lane("pad", 60), lane("chords", 64), lane("organ", 62)]}
check("compose: THREE lanes = the organ-form idiom, clean (corpus law)",
      not MK.court_compose_masking(three)["advisories"])
spread = {"lengthBars": 4, "tracks": [
    lane("bass", 40), lane("pad", 60), lane("lead", 76),
    lane("air", 88)]}
check("compose: four lanes SPREAD across registers clean",
      not MK.court_compose_masking(spread)["advisories"])
drums = {"lengthBars": 4, "tracks": [
    lane("kick", 60), lane("snare", 62), lane("hat", 64),
    lane("perc", 66)]}
check("compose: broadband drum lanes exempt",
      not MK.court_compose_masking(drums)["advisories"])

import shutil
shutil.rmtree(tmp, ignore_errors=True)

print()
if FAILS:
    print(f"masking_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("masking_battery: ALL GREEN")
