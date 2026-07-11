#!/usr/bin/env python3
"""TASTE-CORRECTED SKILLS battery — Genre.complaints become skill guidance.

Pure: taste_section thresholds (noise floor, 40%-share rule, verbatim words,
unknown buckets ignored). Real: two scratch genres in the LIVE graph — one with
complaints, one without — compile through the REAL compile_genre (publish=False)
and assert the section appears exactly where taste data exists. Everything
scrubbed (nodes, edges, SkillDoc, emitted .md files).

Usage: .venv/bin/python tools/taste_skill_battery.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skill_compiler as scmp
from kg import KG

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

def main():
    # ---- pure ----
    ok(scmp.taste_section({}) == [], "no complaints -> no section")
    ok(scmp.taste_section({"complaints": "bright:1"}) == [], "one-off complaint = noise")
    s = scmp.taste_section({"complaints": "bright:3;groove:2", "last_whys": "too bright | stiff"})
    ok(any("rejected 3x as 'bright'" in l for l in s), "dominant bucket ranked first")
    ok(any("rejected 2x as 'groove'" in l for l in s), "second bucket included (>=2)")
    ok(any('their words, verbatim: "too bright | stiff"' in l for l in s), "verbatim words ride")
    s = scmp.taste_section({"complaints": "unknownbucket:5;bright:2"})
    ok(any("'bright'" in l for l in s) and not any("unknownbucket" in l for l in s),
       "unknown buckets ignored, known ones survive")
    s = scmp.taste_section({"complaints": "bright:1;groove:1;busy:1"})
    ok(all("rejected" not in l for l in s) or s == [],
       "three scattered one-offs: no bucket passes the 2x/40% bar")

    # ---- real graph + real compiler ----
    kg = KG()
    def scrub(g):
        kg.g.query(f"MATCH (x:Genre {{name: '{g}'}}) DETACH DELETE x")
        kg.g.query(f"MATCH (d:SkillDoc) WHERE d.name STARTS WITH '{g}-arrangement' DETACH DELETE d")
        for f in os.listdir(os.path.join(ROOT, "skills")):
            if f.startswith(f"{g}-arrangement"):
                os.remove(os.path.join(ROOT, "skills", f))
    for g in ("_tastea", "_tasteb"):
        scrub(g)
        kg.upsert("Genre", g, "test:taste_skill_battery",
                  bpm_lo=120, bpm_hi=130, common_key="A minor")
        kg.upsert("Technique", f"{g}_tech", "test:taste_skill_battery",
                  desc="test technique for the taste battery")
        kg.link("Genre", g, "USES_TECHNIQUE", "Technique", f"{g}_tech", weight=1.0)
    kg.g.query("MATCH (g:Genre {name: '_tastea'}) "
               "SET g.complaints = 'bright:3;groove:2', "
               "g.last_whys = 'too bright, lost the groove | wrong groove'")
    try:
        scmp.compile_genre("_tastea", publish=False)
        scmp.compile_genre("_tasteb", publish=False)
        fa = next(f for f in os.listdir(os.path.join(ROOT, "skills"))
                  if f.startswith("_tastea-arrangement"))
        fb = next(f for f in os.listdir(os.path.join(ROOT, "skills"))
                  if f.startswith("_tasteb-arrangement"))
        ta = open(os.path.join(ROOT, "skills", fa)).read()
        tb = open(os.path.join(ROOT, "skills", fb)).read()
        ok("TASTE CORRECTIONS" in ta and "rejected 3x as 'bright'" in ta,
           "compiled skill CARRIES the taste section when the graph has verdicts")
        ok("too bright, lost the groove" in ta, "the user's words reach the compiled skill")
        ok("TASTE CORRECTIONS" not in tb, "no verdicts -> no section (control genre)")
        ok(ta.index("TASTE CORRECTIONS") < ta.index("## Verify"),
           "section stands before Verify (guidance precedes the checkline)")
    finally:
        for g in ("_tastea", "_tasteb"):
            scrub(g)
            kg.g.query(f"MATCH (t:Technique {{name: '{g}_tech'}}) DETACH DELETE t")
    ok(not [f for f in os.listdir(os.path.join(ROOT, "skills")) if f.startswith("_taste")],
       "scratch skill files scrubbed")

if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"taste-skill battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
