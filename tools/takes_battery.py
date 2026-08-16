#!/usr/bin/env python3
"""THE TAKES CONTRACT battery — loop-record passes and the comp meet here.

The 0.160 STUDIO wave (2026-07-24) taught the app to bank loop-record passes
as track takes[] (engine-native MIDI takes; mergeRecordings flips under the
loop brace; harvestRecording banks passes 1..n-1, the LAST pass plays). This
battery proves the DATA CONTRACT both sides rely on, in the harvest's exact
shape:
  A) takes[] round-trip the C++ engine resave VERBATIM (the undroppable var,
     exercised with the real harvest shape, not a synthetic field)
  B) comp_take consumes them: by index, by name, span-exact (in-span replaced,
     out-of-span kept, history untouched), receipted
The live pass-segmentation half (real MIDI in over a looping transport) is a
hands-on proof — this battery pins the contract so neither side can drift.

Run: python3 tools/takes_battery.py    (needs the m1 binary for A)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "agent"))
IPC = tempfile.mkdtemp(prefix="takes_ipc_")
os.environ["SOTADAW_IPC"] = IPC

import daw_mcp

M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
SONGS = os.path.join(ROOT, "songs")
NAME = "_takes_bat"

N = {"pass": 0, "fail": 0}


def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def note(s, l, p, v):
    return {"start": s, "len": l, "pitch": p, "vel": v}


song = {"version": 2, "bpm": 120, "key": "A minor", "lengthBars": 4,
        "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
        "tracks": [{
            "name": "keys", "source": {"kind": "faust", "id": "rhodes"}, "gainDb": -6,
            # live notes = "pass 3" (the last pass plays, harvest convention)
            "notes": [note(0.0, 0.5, 69, 0.8), note(4.0, 0.5, 72, 0.8),
                      note(8.0, 0.5, 76, 0.8), note(12.0, 0.5, 81, 0.8)],
            # takes[] in the HARVEST'S EXACT SHAPE (name + notes, rec suffix)
            "takes": [
                {"name": "take 1 (rec)",
                 "notes": [note(0.0, 0.5, 60, 0.7), note(4.0, 0.5, 64, 0.7),
                           note(8.0, 0.5, 67, 0.7), note(12.0, 0.5, 71, 0.7)]},
                {"name": "take 2 (rec)",
                 "notes": [note(0.0, 0.5, 57, 0.9), note(4.0, 0.5, 59, 0.9),
                           note(8.0, 0.5, 62, 0.9), note(12.0, 0.5, 65, 0.9)]}]}]}

sp = os.path.join(SONGS, f"{NAME}.json")
json.dump(song, open(sp, "w"), indent=1)
try:
    # ---- A) the engine resave keeps takes[] byte-meaningful
    back = os.path.join(IPC, "back.json")
    r = subprocess.run([M1, "resave", sp, back], capture_output=True, text=True, timeout=120)
    check("A1 engine parses a takes-carrying song", r.returncode == 0 and os.path.exists(back),
          (r.stderr or r.stdout)[-120:])
    if os.path.exists(back):
        b = json.load(open(back))
        bt = b["tracks"][0].get("takes")
        check("A2 takes[] survive the resave verbatim", bt == song["tracks"][0]["takes"])
        check("A3 live notes untouched by the round-trip",
              len(b["tracks"][0]["notes"]) == 4)

    # ---- B) comp_take consumes the harvest shape (bars 1-INDEXED inclusive —
    # the seam was silently 0-based while get_song_region documented 1-based;
    # this battery pins the unified dialect)
    r = daw_mcp.TOOLS["comp_take"][0]({"song": NAME, "track": "keys",
                                       "take": 1, "from_bar": 2, "to_bar": 2})
    d = json.load(open(sp))
    live = d["tracks"][0]["notes"]
    bar2 = [n for n in live if 4.0 <= n["start"] < 8.0]
    check("B1 comp by INDEX: bar 2 (1-indexed) speaks take 1", [n["pitch"] for n in bar2] == [64],
          str([n["pitch"] for n in bar2]))
    check("B2 out-of-span notes kept", [n["pitch"] for n in live if n["start"] < 4.0] == [69]
          and [n["pitch"] for n in live if n["start"] >= 8.0] == [76, 81])
    check("B3 history untouched", d["tracks"][0]["takes"] == song["tracks"][0]["takes"])

    r = daw_mcp.TOOLS["comp_take"][0]({"song": NAME, "track": "keys",
                                       "take": "take 2 (rec)", "from_bar": 3, "to_bar": 3})
    d = json.load(open(sp))
    bar3 = [n for n in d["tracks"][0]["notes"] if 8.0 <= n["start"] < 12.0]
    check("B4 comp by NAME lands bar 3 from the named take", [n["pitch"] for n in bar3] == [62],
          str([n["pitch"] for n in bar3]))

    rl = os.path.join(IPC, "receipts.jsonl")
    rc = [json.loads(l) for l in open(rl)] if os.path.exists(rl) else []
    check("B5 both comps receipted", sum(1 for x in rc if x.get("tool") == "comp_take") == 2,
          str(len(rc)))
finally:
    for f in (sp,):
        if os.path.exists(f):
            os.remove(f)
    shutil.rmtree(IPC, ignore_errors=True)

print(f"takes battery: {N['pass']}/{N['pass'] + N['fail']}"
      + (" clean" if not N["fail"] else " RED"))
sys.exit(1 if N["fail"] else 0)
