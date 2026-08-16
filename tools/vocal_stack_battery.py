#!/usr/bin/env python3
"""VOCAL STACK BATTERY — proves THE STACK (wave 25; R-12 item 014).
Pure, deterministic, no KG required (policy falls back to seed presets)."""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vocal_stack as VS  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def hook_song(genre="gospel", chords=True):
    verse = [{"start": float(i), "len": 0.8, "pitch": 62, "vel": 0.8}
             for i in range(8)]
    hook = [{"start": 8.0 + i * 0.5, "len": 0.45,
             "pitch": [60, 62, 64, 65, 67, 65, 64, 62][i], "vel": 0.85}
            for i in range(8)]
    s = {"bpm": 100, "lengthBars": 4, "genre": genre,
         "sections": [{"name": "verse", "startBar": 0},
                      {"name": "chorus", "startBar": 2}],
         "tracks": [{"name": "lead_vocals",
                     "source": {"id": "formant_vox"},
                     "notes": verse + hook}]}
    if chords:
        s["chords"] = [{"beat": 8.0, "chord": "C"},
                       {"beat": 10.0, "chord": "F"}]
    return s


s = hook_song("gospel")
plans = VS.plan_stacks(s, "gospel")
names = {p["interval"] for p in plans}
check("plan: gospel policy = unison + third + fifth stacks",
      names == {"unison", "third_up", "fifth_up"}, str(names))
uni = next(p for p in plans if p["interval"] == "unison")
check("plan: stacks cover HOOK notes only (verse stays solo)",
      len(uni["notes"]) == 8 and
      all(n["start"] >= 8.0 for n in uni["notes"]), str(len(uni["notes"])))
check("plan: stack level rides the VocalTarget policy (-4dB gospel)",
      uni["gainDb"] == -4.0, str(uni["gainDb"]))
third = next(p for p in plans if p["interval"] == "third_up")
hook_by_start = {n["start"]: n["pitch"]
                 for n in s["tracks"][0]["notes"] if n["start"] >= 8}
up_by = [t["pitch"] - hook_by_start[t["start"]] for t in third["notes"]]
check("plan: thirds are CHORD TONES 3-5 st up (never parallel-major)",
      up_by and all(3 <= u <= 5 for u in up_by), str(up_by))
# C chord at beat 8: lead 60(C)->64(E, +4=major 3rd in C); lead 64(E)->67(G,+3)
c_map = {t["start"]: t["pitch"] for t in third["notes"]}
check("plan: C-chord beats harmonize inside C (E over C, G over E)",
      c_map.get(8.0) == 64 and c_map.get(9.0) == 67,
      str({k: c_map[k] for k in sorted(c_map)[:4]}))

check("plan: no sections = no stacks",
      VS.plan_stacks({"tracks": s["tracks"], "bpm": 100}, "gospel") == [])
check("plan: no vocal lane = no stacks",
      VS.plan_stacks({"sections": s["sections"], "bpm": 100,
                      "tracks": [{"name": "kick", "notes": [{"start": 0}]}]},
                     "gospel") == [])

folk = VS.plan_stacks(hook_song("folk"), "folk")
check("plan: folk policy = unison double only",
      {p["interval"] for p in folk} == {"unison"}, str(folk))

# apply: lanes land, idempotent, proxy source = the lead's own voice
s = hook_song("gospel")
landed = VS.apply_stacks(s, "gospel")
check("apply: lanes landed with stack_of provenance",
      len(landed) == 3 and
      all(t.get("stack_of") == "lead_vocals" for t in s["tracks"]
          if str(t.get("name", "")).startswith("vox_stack")), str(landed))
lanes1 = [t["name"] for t in s["tracks"]]
VS.apply_stacks(s, "gospel")
check("apply: idempotent (re-apply refreshes, never duplicates)",
      [t["name"] for t in s["tracks"]] == lanes1)
stack = next(t for t in s["tracks"] if t["name"] == "vox_stack_unison")
check("apply: proxy source = the lead's own voice (whisper-double idiom)",
      stack["source"] == {"id": "formant_vox"})
check("apply: pans split around the lead",
      stack["pan"] < 0 < next(t for t in s["tracks"]
                              if t["name"] == "vox_stack_third_up")["pan"])

# determinism
a = VS.plan_stacks(hook_song("gospel"), "gospel")
b = VS.plan_stacks(hook_song("gospel"), "gospel")
check("plan: deterministic", a == b)

# ------------------------------------------------ w76 choir gen (033)
import copy
import choir_gen as CG
csong = {"bpm": 100, "lengthBars": 16, "key": "C major",
         "chords": [{"bar": b, "chord": c} for b, c in
                    [(9, "C"), (11, "F"), (13, "G"), (15, "C")]],
         "sections": [{"name": "verse", "startBar": 0},
                      {"name": "chorus", "startBar": 8}],
         "tracks": [{"name": "vocals_lead", "gainDb": 0.0,
                     "source": {"id": "vocals"},
                     "notes": [{"start": float(b), "len": 1.0,
                                "pitch": p, "vel": 92}
                               for b, p in [(0, 60), (2, 62),
                                            (32, 67), (34, 64), (36, 65),
                                            (38, 67), (40, 62), (42, 64),
                                            (44, 60), (46, 67)]]}]}
g = copy.deepcopy(csong)
CG.gospel_choir(g)
alto = next(t for t in g["tracks"] if t["name"] == "vocals_alto")
bass = next(t for t in g["tracks"] if t["name"] == "vocals_bass")
check("choir: SATB lanes land inside real ranges",
      all(CG.RANGES["alto"][0] <= n["pitch"] <= CG.RANGES["alto"][1]
          for n in alto["notes"]) and
      all(CG.RANGES["bass"][0] <= n["pitch"] <= CG.RANGES["bass"][1]
          for n in bass["notes"]))
check("choir: the harmony ARRIVES at the hook (verses stay unison)",
      all(float(n["start"]) >= 32 for n in alto["notes"] + bass["notes"]))
check("choir: idempotent", CG.gospel_choir(g) == [])
k = copy.deepcopy(csong)
eds = CG.kpop_stack(k)
fin = [e for e in eds if e["kind"] == "kpop_stack"][0]
check("kpop: 6-12 layer formation w/ breath (vel x0.3) + wide pair",
      6 <= fin["layers"] <= 12 and
      any(t["name"] == "vox_breath" and t["notes"][0]["vel"] < 30
          for t in k["tracks"]) and
      {t["pan"] for t in k["tracks"]
       if t["name"].startswith("vox_choir")} == {-0.8, 0.8})
check("kpop: every layer is a SINGABLE vocals lane (source rides)",
      all(t.get("source") for t in k["tracks"]
          if t["name"].startswith(("vox_", "vocals_"))))

print()
if FAILS:
    print(f"vocal_stack_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("vocal_stack_battery: ALL GREEN")
