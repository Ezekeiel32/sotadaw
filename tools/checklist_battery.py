#!/usr/bin/env python3
"""CHECKLIST BATTERY — proves THE GENRE CHECKLIST (wave 30; R-21 item
029). Pure; asserts the view NEVER re-encodes law (one-resolver) and
the researched UKG example assembles cell-for-cell."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genre_checklist as GCL  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


# the r-21 worked example: UKG
b = GCL.rule_block("ukgarage")
check("UKG: tempo 130-135 (the researched cell)",
      b.get("tempo_range") == [130, 135], str(b.get("tempo_range")))
check("UKG: kick != four-on-floor", b["kick_topology"] == "no_4x4")
check("UKG: swing window present + straight grid FORBIDDEN",
      b.get("swing_range") and "straight_grid" in b["forbidden"], str(b))
check("UKG: sub mono is the standing floor", b["sub_mono"] is True)

b = GCL.rule_block("psytrance")
check("psy: 4x4 kick + unpumped-onbeat-bass forbidden (KBBB kin)",
      b["kick_topology"] == "4x4" and
      "unpumped_onbeat_bass" in b["forbidden"], str(b))
b = GCL.rule_block("rock")
check("rock: acoustic kit + live translation family + rock vocal chain",
      b["drum_machine"] == "acoustic" and
      b["translation_family"] == "live" and b["vocal_family"] == "rock",
      str(b))

# one-resolver law: the module imports the owning tables, never copies
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "genre_checklist.py")).read()
check("one-resolver: no local tempo/swing tables (imports the courts')",
      "TEMPO_RANGES =" not in src and "SWING_WINDOWS =" not in src and
      "import groove_court" in src)

# composite verdict runs the owning courts
song = {"bpm": 132, "lengthBars": 4, "tracks": [
    {"name": "kick", "notes": [{"start": float(b), "len": 0.4,
                                "pitch": 36, "vel": 0.9}
                               for b in range(16)]},   # 4x4 in UKG!
    {"name": "bass", "notes": [{"start": b + 0.5, "len": 0.4,
                                "pitch": 40, "vel": 0.8}
                               for b in range(16)]}]}
v = GCL.checklist(song, "ukgarage")
check("checklist: 4x4 kick in UKG turns the composite RED",
      not v["ok"] and not v["verdicts"]["kick"]["ok"],
      str(v["verdicts"].get("kick")))
song["tracks"][0]["notes"] = [
    {"start": float(b) + o, "len": 0.4, "pitch": 36, "vel": 0.9}
    for b in range(0, 16, 4) for o in (0.0, 2.5)]
v = GCL.checklist(song, "ukgarage")
check("checklist: broken-beat kick passes the kick cell",
      v["verdicts"]["kick"]["ok"], str(v["verdicts"].get("kick")))
check("checklist: rules ride beside verdicts",
      v["rules"]["genre"] == "ukgarage" and "verdicts" in v)

print()
if FAILS:
    print(f"checklist_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("checklist_battery: ALL GREEN")
