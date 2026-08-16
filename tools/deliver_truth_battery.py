#!/usr/bin/env python3
"""DELIVER + TRUTH BATTERY — W99 (Chezy live, untitled_56: doubled
responses + 'AGENT CONFIDENTLY TELLS ME ITS 164 BARS WHEN IT NOT!').

Three laws proven pure (functions harvested from sidecar.py — the
daemon never imports):

  ADOPTER      the fence-era _prop_<song>_full.json is seen; a
               run-fresh _full SUBSUMES a stale prop; a newer prop
               wins; the rendered wav rides along
  TRUTH COURT  fabricated bars/duration claims get the MEASURED line;
               honest finals stay silent
  DEDUPE       a final already carded as 'agent:' never repeats in
               'agent done:' (the doubled-response law)
"""
import json
import os
import shutil
import sys
import tempfile
import time
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "agent", "sidecar.py")).read()


def harvest(name, end_marker):
    i = src.index(f"def {name}")
    j = src.index(end_marker, i)
    return src[i:j]


emitted = []
tmp = tempfile.mkdtemp(prefix="w99_")
ns = {
    "os": os, "json": json, "shutil": shutil, "SONGS": tmp,
    "emit": lambda rid, kind, **kw: emitted.append((kind,
                                                    kw.get("text", ""))),
    "chronicle": types.SimpleNamespace(append=lambda *a, **k: None),
    "surgical": types.SimpleNamespace(
        coarse_receipt=lambda *a, **k: None),
}
exec(harvest("final_truth_court", "def adopt_stranded_take"), ns)
exec(harvest("adopt_stranded_take", "def corpse_court"), ns)


def wj(name, doc):
    p = os.path.join(tmp, name)
    json.dump(doc, open(p, "w"))
    return p


# ------------------------------------------------- the adopter
now = time.time()
big = {"bpm": 140, "lengthBars": 164,
       "tracks": [{"name": "kick", "notes": [{"start": 0, "len": 1,
                                              "pitch": 36, "vel": 100}]}]}
small = {"bpm": 140, "lengthBars": 4,
         "tracks": [{"name": "kick", "notes": [{"start": 0, "len": 1,
                                                "pitch": 36, "vel": 90}]}]}
# fence-era name + stale prop -> the _full SUBSUMES
wj("_prop_s1_full.json", big)
open(os.path.join(tmp, "_prop_s1_full.wav"), "wb").write(b"RIFFfake")
pp = wj("_prop_s1.json", small)
os.utime(os.path.join(tmp, "_prop_s1_full.json"), (now, now))
os.utime(pp, (now - 60, now - 60))            # the prop is OLDER
ok = ns["adopt_stranded_take"](1, "s1", "_prop_s1", now - 120)
adopted = json.load(open(pp))
check("adopter: the fence-era _full SUBSUMES the stale 4-bar prop "
      "(the untitled_56 class)",
      ok and adopted["lengthBars"] == 164, str(adopted.get("lengthBars")))
check("adopter: the rendered wav rides to the prop slot",
      os.path.exists(os.path.join(tmp, "_prop_s1.wav")))

# a NEWER prop wins (the loop was the later intent)
wj("_prop_s2_full.json", big)
p2 = wj("_prop_s2.json", small)
os.utime(os.path.join(tmp, "_prop_s2_full.json"), (now - 60, now - 60))
os.utime(p2, (now, now))
ok2 = ns["adopt_stranded_take"](1, "s2", "_prop_s2", now - 120)
check("adopter: a NEWER prop is the truth (no adoption)",
      not ok2 and json.load(open(p2))["lengthBars"] == 4)

# stale _full from an old session never adopts
wj("_prop_s3_full.json", big)
os.utime(os.path.join(tmp, "_prop_s3_full.json"),
         (now - 9999, now - 9999))
check("adopter: a stale _full (older than the run) never adopts",
      not ns["adopt_stranded_take"](1, "s3", "_prop_s3", now - 120))

# the UNfenced legacy name still works
wj("s4_full.json", big)
os.utime(os.path.join(tmp, "s4_full.json"), (now, now))
check("adopter: the legacy <song>_full.json path still adopts",
      ns["adopt_stranded_take"](1, "s4", "_prop_s4", now - 120) and
      json.load(open(os.path.join(tmp, "_prop_s4.json")))
      ["lengthBars"] == 164)

# ------------------------------------------------- the truth court
emitted.clear()
wj("_prop_s5.json", small)
ns["final_truth_court"](1, "s5", "_prop_s5",
                        "SICK GOA DELIVERED. 164-bar epic (4:43) at "
                        "140 BPM")
check("truth court: fabricated bars + duration get the MEASURED line",
      any(k == "activity" and "MEASURED TRUTH" in t and "164" in t
          and "0:0" in t for k, t in emitted), str(emitted))
emitted.clear()
ns["final_truth_court"](1, "s5", "_prop_s5",
                        "a tight 4-bar loop at 140bpm, punchy")
check("truth court: an honest final stays silent", not emitted)
emitted.clear()
ns["final_truth_court"](1, "nosuch", "_prop_nosuch", "164-bar epic")
check("truth court: no take = no verdict (fail-open)", not emitted)

# ------------------------------------------------- the dedupe law
final = "Perfect. DELIVERED."
last_carded = {7: final.strip()}
repeats = final.strip() == last_carded.get(7, "")
check("dedupe: a final already carded never repeats "
      "('agent done.' short stamp)", repeats)
check("dedupe: a DIFFERENT final still ships in full",
      not ("other text" == last_carded.get(7, "")))
check("dedupe: all three epilogues carry the guard",
      src.count('last_carded.get(req_id, "")') >= 3 and
      src.count('text="agent done."') >= 3)

shutil.rmtree(tmp, ignore_errors=True)
print()
if FAILS:
    print(f"deliver_truth_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("deliver_truth_battery: ALL GREEN")
