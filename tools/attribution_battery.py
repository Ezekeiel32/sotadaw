#!/usr/bin/env python3
"""ATTRIBUTION BATTERY — proves THE ATTRIBUTION COURT (wave 29; R-31
item 006). Pure — no signing, no audio."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attribution_court as AC  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


instr = {"tracks": [{"name": "kick", "notes": [{"start": 0}]},
                    {"name": "lead", "notes": [{"start": 0}]}]}
check("court: instrumental take skipped",
      AC.court_attribution(instr).get("skipped", "").startswith("no voice"))

sung = {"tracks": [
    {"name": "vocals", "audioClips": [{"file": "songs/x_vocal.wav",
                                       "startBeat": 0}]},
    {"name": "kick", "notes": [{"start": 0}]}]}
v = AC.court_attribution(sung)
check("court: sung clip with NO attribution CONVICTED",
      not v["ok"] and v["flags"][0]["kind"] == "unattributed_voice", str(v))

marked = {"tracks": [
    {"name": "vocals", "comment": "voice: Gahata Meiji from LUNAI Project",
     "audioClips": [{"file": "songs/x_vocal.wav", "startBeat": 0}]}]}
check("court: surviving voice comment passes",
      AC.court_attribution(marked)["ok"])

eds = AC.heal_attribution(sung)
kinds = {e["kind"] for e in eds}
check("heal: license stamped + lane re-marked",
      kinds == {"license_stamp", "lane_mark"}, str(eds))
check("heal: song carries the structural license (non-commercial)",
      sung["voice_license"]["non_commercial"] is True and
      sung["voice_license"]["attribution"], str(sung.get("voice_license")))
check("heal: re-court OK (the impossible state is closed)",
      AC.court_attribution(sung)["ok"])
check("heal: idempotent", AC.heal_attribution(sung) == [])
check("heal: instrumental untouched", AC.heal_attribution(instr) == [])

la = AC.license_assertion(sung)
check("assertion: C2PA voice_license rides with non_commercial true",
      la and la["label"] == "org.sotadaw.voice_license" and
      la["data"]["non_commercial"] is True and
      la["data"]["attribution"], str(la))
check("assertion: none for instrumentals",
      AC.license_assertion(instr) is None)

check("bank truth: attribution string non-empty (manifest or default)",
      len(AC.bank_attribution()) > 8, AC.bank_attribution())

# the export seam wiring is greppable law (export_master runs the court
# pre-sign + embeds the assertion)
em = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "export_master.py")).read()
check("export seam: court runs pre-sign",
      "court_attribution" in em and "heal_attribution" in em)
check("export seam: license assertion embedded",
      "license_assertion" in em)

print()
if FAILS:
    print(f"attribution_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("attribution_battery: ALL GREEN")
