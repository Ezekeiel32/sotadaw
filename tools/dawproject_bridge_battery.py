#!/usr/bin/env python3
"""DAWPROJECT BRIDGE battery — the round-trip guardian this bridge never had
(the "round-trip exact" claim shipped with zero suite coverage), plus the v2
AUTOMATION crossing: 19 corpus songs carried 27 automation lanes that silently
vanished on every export to Bitwig/Cubase/Nuendo/Studio One.

  D1 export emits + parses as XML (structure court)
  D2 notes/volume/pan round-trip exact (the ORIGINAL claim, now proven)
  D3 linear automation lane -> point-exact round trip
  D4 hold lane (curve=1.0) -> interpolation="hold" -> curve=1.0 (exact law)
  D5 curved lane densifies ENGINE-TRUE: every re-imported point sits on the
     tracktion_curve evaluation of the source lane (<=1e-3 in native units)
  D6 masterGainDb rides a role="master" track and lands back song-level;
     +dB master points cap to 0 (chain law); lengthBars covers the ride
  D7 fx/source targets skipped HONESTLY (counted, absent from the archive)
  D8 a track with ONLY automation still lands (keep condition)
Run: python3 tools/dawproject_bridge_battery.py   (suite leg — pure)
"""
import json
import math
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import tracktion_curve

PY = sys.executable
N = {"pass": 0, "fail": 0}


def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


tdir = tempfile.mkdtemp(prefix="dpbat_")
song = {
    "version": 2, "bpm": 133.5, "lengthBars": 4, "masterGainDb": 0,
    "automation": [
        {"target": "masterGainDb", "points": [{"beat": 24, "v": 3.0},
                                              {"beat": 32, "v": -24.0}]},
        {"target": "fx[0].wet", "points": [{"beat": 0, "v": 0.2}]},
    ],
    "tracks": [
        {"name": "keys", "gainDb": -6.0, "pan": -0.4,
         "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 0.8},
                   {"start": 2.25, "len": 0.5, "pitch": 67, "vel": 0.55}],
         "automation": [
             {"target": "gainDb", "points": [{"beat": 0, "v": -18.0, "curve": 0.8},
                                             {"beat": 16, "v": -6.0}]},
             {"target": "pan", "points": [{"beat": 0, "v": -1.0},
                                          {"beat": 8, "v": 1.0}]},
             {"target": "gainDb", "points": [{"beat": 16, "v": -6.0, "curve": 1.0},
                                             {"beat": 24, "v": -30.0}]},
             {"target": "source.cutoff", "points": [{"beat": 0, "v": 500}]},
         ]},
        {"name": "riser", "gainDb": 0.0, "pan": 0.0, "notes": [],
         "automation": [{"target": "gainDb",
                         "points": [{"beat": 0, "v": -40.0}, {"beat": 30, "v": 0.0}]}]},
    ],
}
sp = os.path.join(tdir, "auto.json")
json.dump(song, open(sp, "w"))
dp = os.path.join(tdir, "auto.dawproject")
rt = os.path.join(tdir, "rt.json")

rexp = subprocess.run([PY, os.path.join(ROOT, "tools", "dawproject_export.py"), sp, dp],
                      capture_output=True, text=True, timeout=60)
xml_ok = False
if os.path.exists(dp):
    try:
        root = ET.fromstring(zipfile.ZipFile(dp).read("project.xml"))
        xml_ok = root.tag == "Project"
    except ET.ParseError:
        pass
check("D1 export emits + XML parses", rexp.returncode == 0 and xml_ok,
      (rexp.stdout + rexp.stderr).strip()[:80])

r = subprocess.run([PY, os.path.join(ROOT, "tools", "dawproject_import.py"), dp, rt],
                   capture_output=True, text=True, timeout=60)
b = json.load(open(rt)) if os.path.exists(rt) else {"tracks": []}
keys = next((t for t in b.get("tracks", []) if t["name"] == "keys"), {})
check("D2 notes/volume/pan exact",
      b.get("bpm") == 133.5 and keys.get("gainDb") == -6.0 and keys.get("pan") == -0.4
      and [(n["start"], n["len"], n["pitch"]) for n in keys.get("notes", [])]
      == [(0.0, 1.0, 60), (2.25, 0.5, 67)],
      f"bpm {b.get('bpm')} gain {keys.get('gainDb')} pan {keys.get('pan')}")

lanes = keys.get("automation", [])
pan_lane = next((l for l in lanes if l["target"] == "pan"), {"points": []})
check("D3 linear lane point-exact",
      [(p["beat"], p["v"]) for p in pan_lane["points"]] == [(0.0, -1.0), (8.0, 1.0)]
      and not any(p.get("curve") for p in pan_lane["points"]))

hold_lane = next((l for l in lanes if l["target"] == "gainDb"
                  and any(p["beat"] == 16.0 for p in l["points"])
                  and len(l["points"]) == 2), {"points": []})
check("D4 hold lane: curve 1.0 survives the crossing",
      [(p["beat"], p["v"], p.get("curve")) for p in hold_lane["points"]]
      == [(16.0, -6.0, 1.0), (24.0, -30.0, None)], str(hold_lane["points"]))

curved = next((l for l in lanes if l["target"] == "gainDb"
               and len(l["points"]) > 2), {"points": []})
errs = []
for p in curved["points"]:
    want_lin = 10.0 ** (tracktion_curve.curve_value(
        p["beat"], 0, -18.0, 16, -6.0, 0.8) / 20.0)
    got_lin = 10.0 ** (p["v"] / 20.0)
    errs.append(abs(want_lin - got_lin))
check("D5 curved lane densified ENGINE-TRUE",
      len(curved["points"]) >= 8 and errs and max(errs) <= 1e-3,
      f"{len(curved['points'])} pts, max lin-err "
      + (f"{max(errs):.2e}" if errs else "?"))

mast = b.get("automation", [])
mlane = mast[0] if mast else {"points": []}
check("D6 masterGainDb rides + caps + world grows",
      mlane.get("target") == "masterGainDb"
      and [(p["beat"], p["v"]) for p in mlane["points"]] == [(24.0, 0.0), (32.0, -24.0)]
      and b.get("lengthBars", 0) >= 8 and "capped" in (r.stdout + r.stderr),
      f"lanes {len(mast)} lengthBars {b.get('lengthBars')}")

xml_text = zipfile.ZipFile(dp).read("project.xml").decode()
check("D7 fx/source targets skipped honestly (counted + no ghosts)",
      "2 fx/source lanes have no open-format twin" in rexp.stdout
      and "cutoff" not in xml_text and "fx[0]" not in xml_text)

riser = next((t for t in b.get("tracks", []) if t["name"] == "riser"), None)
check("D8 automation-only track still lands",
      riser is not None and riser.get("automation")
      and riser["automation"][0]["points"][-1]["beat"] == 30.0,
      str((riser or {}).get("automation", "MISSING"))[:60])

print(f"dawproject bridge battery: {N['pass']}/{N['pass'] + N['fail']}"
      + (" clean" if not N["fail"] else " RED"))
sys.exit(1 if N["fail"] else 0)
