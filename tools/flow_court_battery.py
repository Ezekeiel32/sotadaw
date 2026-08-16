#!/usr/bin/env python3
"""FLOW COURT BATTERY — proves THE FLOW COURT (wave 49, the holes
decree: "PEER MODELS MAKE SONGS WITH HOLES! NO FLOW THROUGHPUT!").
Pure, no renders."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flow_court as FC  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def bar_notes(bar, n=4, pitch=36, vel=100, ln=0.5):
    return [{"start": bar * 4 + i, "len": ln, "pitch": pitch, "vel": vel}
            for i in range(n)]


def song_with(tracks, bars=16):
    return {"bpm": 120, "lengthBars": bars, "tracks": tracks}


# ------------------------------------------------- the crime (screenshot)
kick = {"name": "kick", "notes": []}
pad = {"name": "pad", "notes": []}
for b in list(range(0, 4)) + list(range(8, 16)):
    kick["notes"] += bar_notes(b)
    pad["notes"] += bar_notes(b, n=1, pitch=60, ln=4.0)
s = song_with([kick, pad])
v = FC.court_flow(s)
check("crime: 4-bar full-band hole (bars 4-8) CONVICTS",
      not v["ok"] and v["convictions"] and
      v["convictions"][0]["kind"] == "dead_air" and
      v["convictions"][0]["fromBar"] == 4 and
      v["convictions"][0]["toBar"] == 8, str(v["convictions"]))

# the heal bridges it from the song's OWN material (pad = sustained donor,
# least dense at the leading edge)
acts = FC.heal_flow(s, v)
check("heal: bridge lands on the sustained lane at reduced velocity",
      acts and acts[0]["kind"] == "flow_bridge" and
      acts[0]["lane"] == "pad" and acts[0]["notes_added"] == 4 and
      all(n["vel"] == 75 for n in s["tracks"][1]["notes"]
          if 16 <= n["start"] < 32), str(acts))
check("heal: re-court CLEAN (idempotent by construction)",
      FC.court_flow(s)["ok"])

# ------------------------------------------------------------ pardons
kick2 = {"name": "kick", "notes": []}
for b in list(range(0, 8)) + list(range(9, 16)):
    kick2["notes"] += bar_notes(b)
v = FC.court_flow(song_with([kick2]))
check("pardon: the 1-bar CUT resolving into the next downbeat passes",
      v["ok"] and not v["convictions"], str(v["convictions"]))

# breakdown = something still breathes -> never a hole
kick3 = {"name": "kick", "notes": []}
for b in list(range(0, 4)) + list(range(12, 16)):
    kick3["notes"] += bar_notes(b)
pad3 = {"name": "pad", "notes": []}
for b in range(0, 16):
    pad3["notes"] += bar_notes(b, n=1, pitch=57, ln=4.0)
check("pardon: a breakdown (pad carries 8 bars alone) is NOT a hole",
      FC.court_flow(song_with([kick3, pad3]))["ok"])

# leading/trailing silence = THE WORLD GROWS, never convicts
kick4 = {"name": "kick", "notes": []}
for b in range(4, 12):
    kick4["notes"] += bar_notes(b)
v = FC.court_flow(song_with([kick4], bars=24))
check("pardon: leading + trailing silence never convicts (tails by design)",
      v["ok"] and v["first_bar"] == 4 and v["last_bar"] == 11, str(v))

# muted lanes cannot fill a hole
kickm = {"name": "kick", "notes": []}
for b in list(range(0, 4)) + list(range(8, 16)):
    kickm["notes"] += bar_notes(b)
padm = {"name": "pad", "muted": True,
        "notes": [{"start": 0, "len": 64.0, "pitch": 60, "vel": 90}]}
check("law: a MUTED lane cannot fill dead air",
      not FC.court_flow(song_with([kickm, padm]))["ok"])

# audio clips count as coverage
kicka = {"name": "kick", "notes": []}
for b in list(range(0, 4)) + list(range(8, 16)):
    kicka["notes"] += bar_notes(b)
loop = {"name": "loop", "audioClips": [
    {"file": "x.wav", "startBeat": 16.0, "lengthBeats": 16.0}]}
check("law: an audio clip IS coverage",
      FC.court_flow(song_with([kicka, loop]))["ok"])

# stutter: >=3 pardoned 1-bar cuts = advisory
kick5 = {"name": "kick", "notes": []}
for b in [0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 14, 15]:
    kick5["notes"] += bar_notes(b)
v = FC.court_flow(song_with([kick5]))
check("advisory: swiss-cheese (>=3 one-bar cuts) flags stutter_flow",
      v["ok"] and v["advisories"] and
      v["advisories"][0]["kind"] == "stutter_flow", str(v["advisories"]))

# pre-echo: nothing MIDI sounds before the hole (audio-only leading
# edge) -> the INCOMING bar bridges at vel x0.6; audio lanes never tile
lead = {"name": "lead", "notes": []}
for b in range(6, 10):
    lead["notes"] += bar_notes(b, n=2, pitch=72, vel=100)
s2 = song_with([{"name": "tex", "audioClips": [
    {"file": "y.wav", "startBeat": 0.0, "lengthBeats": 8.0}]}, lead],
    bars=10)
v2 = FC.court_flow(s2)
acts2 = FC.heal_flow(s2, v2)
check("heal: audio-only leading edge -> PRE-ECHO of the incoming bar "
      "(vel x0.6)",
      acts2 and acts2[0]["lane"] == "lead" and
      any(n["vel"] == 60 for n in s2["tracks"][1]["notes"]), str(acts2))

# empties never crash, never convict
check("law: empty song = skipped",
      FC.court_flow({})["ok"] and
      bool(FC.court_flow({"lengthBars": 8, "tracks": []}).get("skipped")))

print()
if FAILS:
    print(f"flow_court_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("flow_court_battery: ALL GREEN")
