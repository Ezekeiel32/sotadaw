#!/usr/bin/env python3
"""DUB BUS + EMOTION PRIOR BATTERY (wave 47; items 098/086). Pure."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dub_bus as DB  # noqa: E402
import emotion_prior as EP  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


# ------------------------------------------------------ 098 the dub bus
spec = DB.build_dub_bus(120.0, "psy")
check("dub: dotted-8th law (0.75*60000/120 = 375ms)",
      spec["fx"][0]["id"] == "fx_dubdelay" and
      spec["fx"][0]["params"]["time"] == 375.0, str(spec["fx"][0]))
check("dub: feedback inside the 30-80% window",
      0.3 <= spec["fx"][0]["params"]["feedback"] <= 0.8)
dt = DB.build_dub_bus(124.0, "dub_techno")
check("dub techno: the 5/16 layer + low-decay verb ride",
      len(dt["fx"]) == 3 and
      abs(dt["fx"][1]["params"]["time"]
          - (5 / 16) * 4 * 60000 / 124) < 0.5 and
      dt["fx"][2]["id"] == "fx_reverb" and
      dt["fx"][2]["params"]["decay"] <= 1.0, str(dt["fx"][1:]))

song = {"bpm": 145, "tracks": [
    {"name": "kick", "notes": [{"start": 0}]},
    {"name": "psy_lead", "notes": [{"start": 0}]},
    {"name": "perc_loop", "notes": [{"start": 0}]}]}
led = DB.apply_dub_bus(song, "psytrance")
check("dub apply: bus + perc/lead sends land (kick never feeds)",
      led and set(led[0]["feeds"]) == {"psy_lead", "perc_loop"} and
      any(b["name"] == "dub_delay" for b in song["buses"]), str(led))
check("dub apply: idempotent", DB.apply_dub_bus(song, "psytrance") == [])
v = DB.court_dub_presence({"bpm": 145, "tracks": []}, "goa")
check("dub court: dry goa take = presence advisory with the recipe",
      v["ok"] and v["advisories"] and
      v["advisories"][0]["kind"] == "no_dub_aux" and
      "310ms" in v["advisories"][0]["why"], str(v))
check("dub court: the applied take passes",
      not DB.court_dub_presence(song, "psytrance")["advisories"])
check("dub court: non-dub genre skipped",
      DB.court_dub_presence({}, "folk").get("skipped", "")
      .startswith("not a dub"))

# --------------------------------------------------- 086 emotion prior
check("emotion: detect + synonyms (ominous -> menacing)",
      EP.detect("an ominous, wistful piece") ==
      ["melancholic", "menacing"])
ep = EP.emotion_prior("a sad slow song")
check("emotion: sad = minor / slower / lower / darker / legato",
      ep["mode_bias"] == "minor" and ep["tempo"] < 0 and
      ep["register"] < 0 and ep["brightness"] < 0 and
      ep["articulation"] == "legato", str(ep))
ep2 = EP.emotion_prior("tense and angry")
check("emotion: additive stacking (tense+angry dissonance sums)",
      ep2["dissonance"] > 0.3 and ep2["tempo"] == 16, str(ep2))
check("emotion: no feeling words = {} (the plan stays clean)",
      EP.emotion_prior("make a house track at 124") == {})
check("emotion: the plan line is additive-by-contract",
      "ADDITIVE" in EP.emotion_prior("happy banger")["plan_line"])

# ------------------------------------------------ w85: the process trio
song85 = {"bpm": 140, "lengthBars": 32, "tracks": [
    {"name": "kick", "notes": [{"start": 0, "len": 1, "pitch": 36,
                                "vel": 100}]},
    {"name": "organ_skank", "gainDb": -2.0,
     "notes": [{"start": float(b), "len": 0.5, "pitch": 64, "vel": 90}
               for b in range(0, 128, 2)]}]}
eds = DB.dubwise(song85, "dub")
kinds = {e["kind"] for e in eds}
check("dubwise(221): dropouts + feedback rise land; the macro stamps",
      {"dub_dropout", "dub_feedback_rise", "dubwise"} <= kinds, str(kinds))
check("dubwise: the ANCHOR law — kick never dropped",
      not song85["tracks"][0].get("automation"))
check("dubwise: idempotent", DB.dubwise(song85, "dub") == [])

import transition_ops as TO85
s85 = {"bpm": 128, "lengthBars": 16, "master": [], "tracks": [
    {"name": "keys", "notes": [{"start": float(b), "len": 1.0,
                                "pitch": 60, "vel": 90}
                               for b in range(64)]}]}
e85 = TO85.dj_transition(s85, 32.0, "club_slam")
check("dj_transition(242): club_slam composes riser + tape_stop",
      {"riser", "tape_stop", "dj_transition"} <=
      {e["kind"] for e in e85}, str([e["kind"] for e in e85]))
check("dj_transition: unknown style is a loud error",
      TO85.dj_transition(s85, 8.0, "zzz")[0]["kind"] == "error")

import dj_listener as DL85
early = [dict(rms=-30 + (10 if i == 3 else 0), centroid=2000, low=0.3,
              t=i * 8.0) for i in range(20)]
check("arc court(249): an early peak flags PEAK_MISPLACED",
      any(x["kind"] == "PEAK_MISPLACED"
          for x in DL85.arc_verdicts(early, arc="peak")))
mono = [dict(rms=-40 + i, centroid=2000, low=0.3, t=i * 8.0)
        for i in range(20)]
check("arc court: a valley-less climb flags MONOTONE_CLIMB",
      any(x["kind"] == "MONOTONE_CLIMB"
          for x in DL85.arc_verdicts(mono, arc="peak")))
wavey = [dict(rms=-40 + (i if i < 14 else 14)
              - (9 if i in (7, 8, 9, 10) else 0), centroid=2000,
              low=0.3, t=i * 8.0) for i in range(20)]
check("arc court: a journey that ends at its peak flags NO_RELEASE "
      "(peak arcs exempt)",
      any(x["kind"] == "NO_RELEASE"
          for x in DL85.arc_verdicts(wavey, arc="journey")) and
      not DL85.arc_verdicts(wavey, arc="peak") or
      any(x["kind"] == "NO_RELEASE"
          for x in DL85.arc_verdicts(wavey, arc="journey")))
good = [dict(rms=-40 + min(i, 13) - (9 if i in (7, 8, 9, 10) else 0)
             - (6 if i >= 18 else 0), centroid=2000, low=0.3,
             t=i * 8.0) for i in range(20)]
check("arc court: the shaped set (valley + resolve) passes clean",
      not DL85.arc_verdicts(good, arc="journey"))

print()
if FAILS:
    print(f"dub_emotion_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("dub_emotion_battery: ALL GREEN")
