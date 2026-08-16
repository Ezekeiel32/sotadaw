#!/usr/bin/env python3
"""AD-LIB BATTERY — proves THE AD-LIB LANE (wave 43; R-12 item 130).
Pure, deterministic (KG fail-open to seed presets)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adlib_op as AD  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def hook_song():
    """Lead phrases with real gaps inside the hook."""
    lead = []
    for base in (8.0, 12.0):                       # two hook phrases
        for k in range(4):
            lead.append({"start": base + k * 0.5, "len": 0.45,
                         "pitch": 62 + k, "vel": 0.85})
        # phrase ends at base+2.0; next starts base+4 -> a 2-beat gap
    verse = [{"start": float(i), "len": 0.9, "pitch": 60, "vel": 0.8}
             for i in range(8)]
    return {"bpm": 140, "lengthBars": 4,
            "sections": [{"name": "verse", "startBar": 0},
                         {"name": "hook", "startBar": 2}],
            "lyrics": [{"beat": float(i), "text": f"w{i}"}
                       for i in range(8)],
            "tracks": [{"name": "lead_vocals",
                        "source": {"id": "formant_vox"},
                        "notes": verse + lead}]}


gaps = AD.find_gaps(hook_song()["tracks"][0]["notes"], 8.0, 16.0)
check("gaps: phrase-end gaps found inside the hook",
      len(gaps) >= 2 and all(g[1] >= 1.0 for g in gaps), str(gaps))

s = hook_song()
led = AD.place_adlibs(s, "trap", seed=0)
check("place: ad-libs land (trap vocab, capped)",
      led and 1 <= led[0]["placed"] <= 3, str(led))
lane = next(t for t in s["tracks"] if t["name"] == "adlibs")
check("place: call-and-response (every ad-lib sits in a lead gap)",
      all(not (8.0 <= n["start"] < 10.0) or n["start"] >= 10.0
          for n in lane["notes"]) and
      all(n["start"] >= 8.0 for n in lane["notes"]), str(lane["notes"]))
check("place: octave-up proxy on the lead's own voice",
      lane["source"] == {"id": "formant_vox"} and
      all(n["pitch"] >= 72 for n in lane["notes"]))
check("place: lyrics entries ride the same beats (the words will sing)",
      all(any(abs(float(l["beat"]) - n["start"]) < 1e-6
              for l in s["lyrics"]) for n in lane["notes"]))
n1 = len(lane["notes"])
AD.place_adlibs(s, "trap", seed=0)
check("place: idempotent (refresh, never stack)",
      len(next(t for t in s["tracks"]
               if t["name"] == "adlibs")["notes"]) == n1)
check("place: folk policy (per_section 0) lands nothing",
      AD.place_adlibs(hook_song(), "folk") == [])
check("place: no sections = nothing",
      AD.place_adlibs({"bpm": 140, "tracks": [
          {"name": "lead", "notes": [{"start": 0, "len": 1,
                                      "pitch": 60, "vel": 0.8}]}]},
          "trap") == [])

mud = hook_song()
mud["tracks"].append({"name": "adlibs", "notes": [
    {"start": 8.0 + i * 0.5, "len": 0.4, "pitch": 74, "vel": 0.7}
    for i in range(6)]})
v = AD.court_adlibs(mud, "trap")
check("court: 6 ad-libs in one hook = MUD advisory (2-3 max)",
      v["ok"] and v["advisories"] and
      v["advisories"][0]["kind"] == "adlib_mud", str(v))
check("court: no lane -> skipped",
      AD.court_adlibs(hook_song(), "trap").get("skipped", "")
      .startswith("no ad-lib"))

print()
if FAILS:
    print(f"adlib_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("adlib_battery: ALL GREEN")
