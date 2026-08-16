#!/usr/bin/env python3
"""ARC COURT battery (P6) — planted flat songs fail, real arcs pass, and the
CORPUS EVIDENCE case (untitled_48, LRA 1.88 measured 2026-07-14) stays caught.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arc_court as AC  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = [0]


def ok(cond, msg):
    N[0] += 1
    if not cond:
        print(f"FAIL #{N[0]}: {msg}")
        sys.exit(1)


def mknote(start, pitch, ln=0.5, vel=0.9):
    return {"start": float(start), "len": ln, "pitch": int(pitch), "vel": vel}


def arcsong(chorus_boost=1.0, sections=True):
    """8-bar verse + 8-bar chorus; chorus_boost scales chorus velocity+density."""
    tracks = [{"name": "lead", "source": {"id": "pluck"}, "notes": []},
              {"name": "keys", "source": {"id": "epiano"}, "notes": []},
              {"name": "kick", "source": {"id": "kick"}, "notes": []}]
    for bar in range(16):
        boost = chorus_boost if bar >= 8 else 1.0
        base = bar * 4.0
        for b in range(4):
            tracks[2]["notes"].append(mknote(base + b, 36, 0.2, min(1.0, 0.9 * boost)))
            tracks[0]["notes"].append(mknote(base + b, 69 + (5 if bar >= 8 else 0),
                                             0.5, min(1.0, 0.7 * boost)))
            if boost > 1.0:
                tracks[0]["notes"].append(mknote(base + b + 0.5, 72, 0.4, 0.85))
                tracks[1]["notes"].append(mknote(base + b, 60, 0.9, 0.8))
        if bar < 8:
            tracks[1]["notes"].append(mknote(base, 57, 2.0, 0.55))
    song = {"version": 2, "bpm": 120, "lengthBars": 16, "key": "A minor",
            "tracks": tracks}
    if sections:
        song["sections"] = [{"name": "verse", "startBar": 0},
                            {"name": "chorus", "startBar": 8}]
    return song


# real arc passes
v = AC.court_arc(arcsong(chorus_boost=1.35), "pop")
ok(v["ok"], f"lifted chorus passes: {v.get('flags')}")

# flat chorus fails
v = AC.court_arc(arcsong(chorus_boost=1.0), "pop")
ok(not v["ok"] and any(f["kind"] == "flat_chorus" for f in v["flags"]),
   f"flat chorus caught: {v.get('flags')}")

# no sections = exempt (loops are loops)
v = AC.court_arc(arcsong(sections=False), "pop")
ok(v["ok"] and v.get("skipped"), "sectionless song exempt")

# late hook: 24 bars of intro at 120bpm = 48s past pop patience. The 20s law
# is VOCAL-pop streaming truth, so the planted pop record carries a voice.
s = arcsong(chorus_boost=1.4)
s["lengthBars"] = 40
s["sections"] = [{"name": "intro", "startBar": 0},
                 {"name": "chorus", "startBar": 24}]
s["tracks"].append({"name": "vocals", "source": {"id": "formant_vox"},
                    "notes": [mknote(96 + b, 69, 0.5, 0.9) for b in range(8)]})
v = AC.court_arc(s, "pop")
ok(any(f["kind"] == "late_hook" for f in v.get("flags", [])),
   f"48s hook arrival caught for pop: {v.get('flags')}")

# the same 48s hook WITHOUT a voice = an instrumental journey — exempt
# (untitled_65: a bluegrass/orchestral film theme nagged at pop patience
# while its hook landed at 60s exactly like the record's)
s_inst = {k: (v2 if k != "tracks" else [t for t in v2 if t["name"] != "vocals"])
          for k, v2 in s.items()}
v = AC.court_arc(s_inst, "pop")
ok(not any(f["kind"] == "late_hook" for f in v.get("flags", [])),
   f"instrumental 48s hook earns journey patience: {v.get('flags')}")
# bluegrass rides the folk bucket now (30s, vocal case)
s_bg = json.loads(json.dumps(s))
s_bg["bpm"] = 240   # 24-bar intro at 240bpm = 24s: past pop 20s, inside folk 30s
v_pop, v_bg = AC.court_arc(s_bg, "pop"), AC.court_arc(s_bg, "bluegrass")
ok(any(f["kind"] == "late_hook" for f in v_pop.get("flags", []))
   and not any(f["kind"] == "late_hook" for f in v_bg.get("flags", [])),
   f"bluegrass patience > pop ({v_pop.get('flags')} vs {v_bg.get('flags')})")
v = AC.court_arc(s, "psytrance")
ok(not any(f["kind"] == "late_hook" for f in v.get("flags", [])),
   "psy patience window is longer — same song passes")

# LRA floor from the RENDERED analysis (the untitled_48 class)
v = AC.court_arc(arcsong(1.35), "pop", analysis={"lra": 1.88})
ok(any(f["kind"] == "lra_floor" for f in v.get("flags", [])),
   "LRA 1.88 fails the pop floor (the corpus evidence case)")
v = AC.court_arc(arcsong(1.35), "techno", analysis={"lra": 2.3})
ok(not any(f["kind"] == "lra_floor" for f in v.get("flags", [])),
   "techno floor is club-true (2.3 passes)")
v = AC.court_arc(arcsong(1.35), "ambient", analysis={"lra": 2.3})
ok(any(f["kind"] == "lra_floor" for f in v.get("flags", [])),
   "the same 2.3 fails ambient (genre-true floors)")

# THE REAL EVIDENCE: untitled_48's actual json + measured LRA must flag
p48 = os.path.join(ROOT, "songs", "untitled_48.json")
if os.path.exists(p48):
    song48 = json.load(open(p48))
    v = AC.court_arc(song48, "pop", analysis={"lra": 1.88})
    ok(not v["ok"], f"untitled_48 (the corpus evidence) flags: {[f['kind'] for f in v.get('flags', [])]}")
    print(f"[evidence] untitled_48 flags: {[f['kind'] for f in v.get('flags', [])]}")

# energy profile sanity: chorus bars carry more energy than verse bars
prof = AC.energy_profile(arcsong(1.35))
ok(sum(prof[8:]) > sum(prof[:8]) * 1.1, "profile sees the lift")
ok(len(prof) == 16 and all(0 <= p <= 1 for p in prof), "profile normalized")

# wave 27 item 070: RENDERED chorus lift on SHORT-TERM windows
flat_rq = [-14.0] * 64                       # 4 quarters/beat x 16 bars
v = AC.court_arc(arcsong(1.35), "pop", analysis={"rms_by_quarter_db": flat_rq})
ok(any(f["kind"] == "flat_chorus_rendered" for f in v.get("flags", [])),
   "rendered flat chorus flagged on short-term windows")
lift_rq = [-16.0] * 32 + [-12.5] * 32
v = AC.court_arc(arcsong(1.35), "pop",
                 analysis={"rms_by_quarter_db": lift_rq})
ok(not any(f["kind"] == "flat_chorus_rendered"
           for f in v.get("flags", [])),
   "3.5dB short-term lift passes (the r-14 significant band)")

# wave 27 item 069: the hook-teaser HEAL for late hooks
late = arcsong(1.35)
late["sections"] = [{"name": "intro", "startBar": 0},
                    {"name": "chorus", "startBar": 8}]
late["bpm"] = 30                             # 8 bars @30 = 64s > 3x pop 20s
v = AC.court_arc(late, "pop")
ok(any(f["kind"] == "late_hook" for f in v.get("flags", [])),
   "60bpm 8-bar intro = late hook for pop")
eds = AC.heal_late_hook(late, v, "pop")
ok(eds and eds[0]["kind"] == "hook_teaser", "teaser heal lands")
teaser = next(t for t in late["tracks"] if t["name"] == "hook_teaser")
ok(teaser["notes"][0]["start"] < 4.0 and teaser["gainDb"] == -6.0 and
   teaser["source"] == {"id": "pluck"},
   "teaser sits at the top, -6dB, wearing the lead's own voice")
ok(AC.heal_late_hook(late, AC.court_arc(late, "pop"), "pop") == [],
   "teaser heal idempotent")

print(f"ARC COURT BATTERY PASS — {N[0]} checks green")
