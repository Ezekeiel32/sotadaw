#!/usr/bin/env python3
"""METAL MIX-HEAL BATTERY — wave 58 (r-23 item 153). Pure."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metal_heal as MH  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def gtr(name, pan=0.0, fx=None):
    return {"name": name, "pan": pan, "fx": fx or [],
            "notes": [{"start": float(b), "len": 0.5, "pitch": 38,
                       "vel": 110} for b in range(16)]}


# ------------------------------------------------------------ the court
song = {"bpm": 150, "lengthBars": 8, "tracks": [gtr("rhythm_guitar")]}
v = MH.court_metal_mix(song, "metalcore")
kinds = {a["kind"] for a in v["advisories"]}
check("court: a centered un-doubled rhythm guitar flags",
      "undoubled_rhythm_guitar" in kinds, str(v))
check("court: a guitar with no HPF flags (drop-tuned flood)",
      "unfiltered_low_guitar" in kinds)
check("court: non-metal genre = skipped (genre-conditional)",
      MH.court_metal_mix(song, "gospel").get("skipped") and
      MH.court_metal_mix(song, "citypop").get("skipped"))

scooped = {"bpm": 150, "lengthBars": 8,
           "master": [{"id": "fx_bell",
                       "params": {"freq": 1000, "gain": -9, "q": 1.0}}],
           "tracks": [gtr("gtr_L", -0.85)]}
v2 = MH.court_metal_mix(scooped, "thrash metal")
check("court: THE SCOOP TRAP — a -9dB cut at 1kHz on the master flags "
      "(the grind IS the genre)",
      any(a["kind"] == "grind_scoop_trap" and a["owner"] == "master"
          for a in v2["advisories"]), str(v2["advisories"]))
gentle = {"bpm": 150, "lengthBars": 8,
          "master": [{"id": "fx_bell",
                      "params": {"freq": 1000, "gain": -3, "q": 2.0}}],
          "tracks": [gtr("gtr_L", -0.85, fx=[
              {"id": "fx_hipass", "params": {"cutoff": 120}}])]}
gv = MH.court_metal_mix(gentle, "metal")
check("court: a gentle -3dB shape + HPF'd hard-panned guitar passes "
      "(only the doubled twin is asked)",
      {a["kind"] for a in gv["advisories"]} <= {"undoubled_rhythm_guitar"},
      str(gv))

# ------------------------------------------------------------ the heal
song3 = {"bpm": 150, "lengthBars": 8, "tracks": [gtr("rhythm_guitar")]}
v3 = MH.court_metal_mix(song3, "djent")
eds = MH.heal_metal_mix(song3, v3, "djent")
names = {t["name"]: t for t in song3["tracks"]}
check("heal: the twin is MINTED — rhythm_guitarR, panned -0.85/+0.85 "
      "(the birth-doubling convention)",
      "rhythm_guitarR" in names and
      names["rhythm_guitar"]["pan"] == -0.85 and
      names["rhythm_guitarR"]["pan"] == 0.85 and
      len(names["rhythm_guitarR"]["notes"]) == 16, str(eds))
check("heal: fx_hipass 120 lands first in the chain",
      names["rhythm_guitar"]["fx"][0]["id"] == "fx_hipass")
check("heal: the standard chain lands ONCE (pocket dip 950 + fizz "
      "notch 6.5k, metal_chain marker)",
      any(f["id"] == "fx_bell" and f["params"]["freq"] == 950.0
          for f in names["rhythm_guitar"]["fx"]) and
      names["rhythm_guitar"].get("metal_chain") and
      not MH.heal_metal_mix(song3, MH.court_metal_mix(song3, "djent"),
                            "djent"))

s4 = {"bpm": 150, "lengthBars": 8,
      "master": [{"id": "fx_bell",
                  "params": {"freq": 1100, "gain": -8, "q": 1.0}}],
      "tracks": []}
MH.heal_metal_mix(s4, MH.court_metal_mix(s4, "metal"), "metal")
check("heal: the scoop CLAMPS to -3dB, never deleted (shape it, "
      "don't gut it)", s4["master"][0]["params"]["gain"] == -3.0)

check("law: empty song never crashes",
      MH.court_metal_mix({}, "metal")["ok"] and
      MH.heal_metal_mix({}, None, "metal") == [])

print()
if FAILS:
    print(f"metal_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("metal_battery: ALL GREEN")
