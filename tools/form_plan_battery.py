#!/usr/bin/env python3
"""FORM PLAN BATTERY — proves THE PLANNER (wave 33; R-29 042/105).
Pure, deterministic."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import form_plan as FP  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


ASK = "make a dark trap song at 142bpm in F minor, 2 minutes"
b = FP.plan_block(ASK, "")
check("plan: generative ask produces the block", bool(b), b)
check("plan: hard targets typed FROM the court (one resolver)",
      "bpm=142" in b and "F minor" in b, b)
check("plan: trap family form (three hooks framing the verses)",
      b.count("hook") >= 3 and b.count("verse") >= 2 and "outro" in b, b)
check("plan: semantic goal rides (dark)", "dark@" in b, b)
check("plan: the law line names the court",
      "instruction court" in b and "EXACTLY" in b)
check("plan: session-diet cap holds", len(b) <= 900, str(len(b)))

# duration -> bars arithmetic: 120s at 142bpm = 71 bars -> 4-bar grid
total = sum(x[1] for x in FP.scaled_form("trap", FP._bars_for(
    FP.hard_targets(ASK), 142.0, "trap")))
check("plan: asked duration scales the form (2min@142 ~ 68-72 bars)",
      64 <= total <= 76, str(total))

# gates
check("gate: tweak asks get NO plan",
      FP.plan_block("make the vocal warmer and punchier", "") == "")
check("gate: revises get NO plan",
      FP.plan_block(ASK, "", revise=True) == "")
check("gate: standing sections = respected form, NO plan",
      FP.plan_block(ASK, "", song={"sections": [{"name": "intro",
                                                 "startBar": 0}]}) == "")
check("gate: generative verbs without a piece noun stay quiet",
      FP.plan_block("make it louder", "") == "")

# form template law
for fam, tpl in FP.FORM_TEMPLATES.items():
    total = sum(b for _, b in FP.scaled_form(fam, 64))
    check(f"form[{fam}]: scales to the asked total on the 4-bar grid",
          total == 64 and all(b % 4 == 0
                              for _, b in FP.scaled_form(fam, 64)),
          str(FP.scaled_form(fam, 64)))
check("family: psybient routes to journey (no chorus machine)",
      FP.family_for("psybient") == "journey")
check("family: house routes to edm (drop form)",
      FP.family_for("deep house") == "edm")

# determinism
check("plan: deterministic", FP.plan_block(ASK, "") == FP.plan_block(ASK, ""))

print()
if FAILS:
    print(f"form_plan_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("form_plan_battery: ALL GREEN")
