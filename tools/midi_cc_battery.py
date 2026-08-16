#!/usr/bin/env python3
"""MIDI CC battery — mixer rides cross the .mid bridge (v2 automation).

MIDI CC is a step function: curve=+1.0 (hold-then-step) is its NATIVE
semantic and must cross in exactly 2 events; every other curve densifies
through the engine's own bezier (tools/tracktion_curve). The value maps
(GM 40*log10 volume taper, 64-center pan) are exact inverses, so the
bridge's byte-idempotence law survives automation.

  C1 export emits CC7/CC10 on the right channels
  C2 hold lane -> exactly 2 CC7 events, values exact
  C3 curved lane -> engine-true steps (every event equals the bezier
     sample through the SAME conversion; >=8 distinct steps)
  C4 round trip: lanes land back (targets, hold points, exact-inverse
     values), CC-only track survives, world covers the ride
  C5 byte-idempotence after the first pass (m2 == m3) WITH automation
  C6 pan law: -1/0/+1 <-> cc 0/64/127
  C7 no-automation songs emit zero CC (opt-in, no regression)
Run: python3 tools/midi_cc_battery.py   (suite leg — pure)
"""
import json
import os
import struct
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import midi_bridge
import tracktion_curve

N = {"pass": 0, "fail": 0}


def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def parse_cc(mid_path):
    """[(track_index, tick, ch, cc, val)] via a minimal SMF walk."""
    data = open(mid_path, "rb").read()
    _, fmt, ntrks, division = struct.unpack(">IHHH", data[4:14])
    out, i = [], 14
    for ti in range(ntrks):
        length = struct.unpack(">I", data[i + 4:i + 8])[0]
        end = i + 8 + length
        j, tick, running = i + 8, 0, None
        while j < end:
            delta, j = midi_bridge.read_vlq(data, j)
            tick += delta
            b0 = data[j]
            if b0 == 0xFF:
                mlen, k = midi_bridge.read_vlq(data, j + 2)
                j = k + mlen
                continue
            if b0 in (0xF0, 0xF7):
                mlen, k = midi_bridge.read_vlq(data, j + 1)
                j = k + mlen
                continue
            if b0 & 0x80:
                running = b0
                j += 1
            status = running
            hi = status & 0xF0
            if hi in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                d1, d2 = data[j], data[j + 1]
                j += 2
            elif hi in (0xC0, 0xD0):
                j += 1
                continue
            else:
                j += 1
                continue
            if hi == 0xB0:
                out.append((ti, tick, status & 0x0F, d1, d2))
        i = end
    return out, division


tdir = tempfile.mkdtemp(prefix="ccbat_")
song = {
    "version": 2, "bpm": 120, "lengthBars": 4,
    "tracks": [
        {"name": "keys", "source": {"kind": "sample", "kit": "piano"}, "gainDb": -6,
         "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 0.8}],
         "automation": [
             {"target": "gainDb", "points": [{"beat": 0, "v": -6.0, "curve": 1.0},
                                             {"beat": 8, "v": -30.0}]},
             {"target": "pan", "points": [{"beat": 0, "v": -1.0},
                                          {"beat": 4, "v": 0.0},
                                          {"beat": 8, "v": 1.0}]},
             {"target": "fx[0].wet", "points": [{"beat": 0, "v": 0.5}]}]},
        {"name": "swell", "source": {"kind": "sample", "kit": "piano"}, "gainDb": 0,
         "notes": [],
         "automation": [{"target": "gainDb",
                         "points": [{"beat": 0, "v": -40.0, "curve": 0.6},
                                    {"beat": 32, "v": 0.0}]}]},
    ],
}
sp = os.path.join(tdir, "cc.json")
json.dump(song, open(sp, "w"))
m1 = os.path.join(tdir, "cc.mid")
msg = midi_bridge.export_midi(sp, m1)

cc, div = parse_cc(m1)
cc7 = [e for e in cc if e[3] == 7]
cc10 = [e for e in cc if e[3] == 10]
check("C1 CC7/CC10 emitted", bool(cc7) and bool(cc10)
      and "automation lanes as CC7/CC10" in msg and "no SMF form" in msg,
      msg[:90])

k7 = [e for e in cc7 if e[0] == 1]          # track chunk 1 = keys
check("C2 hold lane = exactly 2 events, exact values",
      [(t, v) for _, t, _, _, v in k7] == [(0, midi_bridge._db_to_cc(-6.0)),
                                           (8 * 480, midi_bridge._db_to_cc(-30.0))],
      str([(t, v) for _, t, _, _, v in k7]))

s7 = [e for e in cc7 if e[0] == 2]          # track chunk 2 = swell (curved)
eng_ok = all(v == midi_bridge._db_to_cc(tracktion_curve.curve_value(
    t / 480.0, 0, -40.0, 32, 0.0, 0.6)) for _, t, _, _, v in s7)
check("C3 curved lane engine-true steps", len(s7) >= 8 and eng_ok,
      f"{len(s7)} steps")

rt = os.path.join(tdir, "rt.json")
midi_bridge.import_midi(m1, rt)
b = json.load(open(rt))
keys = next((t for t in b["tracks"] if t["name"] == "keys"), {})
kg = next((l for l in keys.get("automation", []) if l["target"] == "gainDb"), {"points": []})
kp = next((l for l in keys.get("automation", []) if l["target"] == "pan"), {"points": []})
swell = next((t for t in b["tracks"] if t["name"] == "swell"), None)
check("C4 round trip: lanes land, hold semantics, CC-only track, world",
      [(p["beat"], round(p["v"])) for p in kg["points"]] == [(0.0, -6), (8.0, -30)]
      and all(p.get("curve") == 1.0 for p in kg["points"][:-1])
      and "curve" not in kg["points"][-1]
      and len(kp["points"]) >= 3
      and swell is not None and bool(swell.get("automation"))
      and b.get("lengthBars", 0) >= 8,
      f"kg {kg['points'][:2]} bars {b.get('lengthBars')}")

m2 = os.path.join(tdir, "m2.mid")
rt2 = os.path.join(tdir, "rt2.json")
m3 = os.path.join(tdir, "m3.mid")
midi_bridge.export_midi(rt, m2)
midi_bridge.import_midi(m2, rt2)
midi_bridge.export_midi(rt2, m3)
check("C5 byte-idempotent after pass one (with automation)",
      open(m2, "rb").read() == open(m3, "rb").read())

check("C6 pan law: -1/0/+1 -> cc 0/64/127, inverses stable",
      [midi_bridge._pan_to_cc(v) for v in (-1.0, 0.0, 1.0)] == [0, 64, 127]
      and midi_bridge._cc_to_pan(64) == 0.0
      and midi_bridge._pan_to_cc(midi_bridge._cc_to_pan(0)) == 0
      and midi_bridge._pan_to_cc(midi_bridge._cc_to_pan(127)) == 127)

plain = {"version": 2, "bpm": 120, "lengthBars": 1,
         "tracks": [{"name": "kick", "source": {"kind": "sample", "kit": "gm_drums"},
                     "notes": [{"start": 0, "len": 0.25, "pitch": 36, "vel": 0.9}]}]}
pp = os.path.join(tdir, "plain.json")
json.dump(plain, open(pp, "w"))
pm = os.path.join(tdir, "plain.mid")
midi_bridge.export_midi(pp, pm)
pcc, _ = parse_cc(pm)
check("C7 no-automation song emits zero CC", pcc == [])

import shutil
shutil.rmtree(tdir, ignore_errors=True)
print(f"midi cc battery: {N['pass']}/{N['pass'] + N['fail']}"
      + (" clean" if not N["fail"] else " RED"))
sys.exit(1 if N["fail"] else 0)
