#!/usr/bin/env python3
"""THE WORLD GRID seed (BEST_DAW_30 #1) — Genre.native_meter + the odd-meter cells.

THE LIE THIS RETIRES: three PatternArchetypes were NAMED for their meter and
PLAYED 4/4, because the schema had no way to say anything else.

  aksak_oompah   (balkan_brass) — "aksak" IS the Balkan word for the limping,
      unequal-beat meter. The cell was kick [0,4,8,12]: four-on-the-floor.
  zeibekiko      (rebetiko)     — the zeibekiko is a NINE-beat dance (2+2+2+3).
      The cell was four-on-the-floor under straight-8th hats.
  odd_meter_cell (math_rock)    — a plain 4/4 rock beat.

The curators' own VELOCITY MAPS knew the truth: balkan_brass accents kick steps
0 and 8 to 1.0 — exactly the group heads of a 7/8 aksak (2+2+3 = 16th-steps
0,4,8) — while the kick LIST said 0/4/8/12. They heard the meter and had no
field to write it in. meterMap[] + Genre.native_meter is that field.

WHAT LANDS (idempotent MERGE; provenance APPENDED, never clobbered):
  * Genre.native_meter ("7/8", "9/8") — read by loop_gen.genre_dna on BOTH the
    live query AND the dna_cache path (the KG-FIELD LAW), and stamped into the
    take as meterMap [{bar:0,num,den}]. ABSENT = 4/4: the other 202 genres are
    byte-for-byte unchanged (the identity law — tools/meter_battery.py is the court).
  * the three cells re-authored in their OWN step-count. A 7/8 bar is 14
    sixteenths, a 9/8 bar is 18 — every lane interlocks inside the bar and
    nothing crosses a barline (a hit past the barline is a wrong bar, not a
    syncopation). `groups` rides the grid blob (whole-blob = both KG paths by
    construction) so 9/8 groups 2+2+2+3 instead of the compound-default 3+3+3.

WHAT DOESN'T (honest non-claims — no silent caps):
  * celtic/reel_lilt, flamenco/rumba_palmas, klezmer/freylekh_bounce ARE 4/4
    dances (a reel/rumba/freylekh is not a jig/buleria/hora) — untouched.
  * gnawa/sega/maloya carry their triplet feel through swing 0.66 today; 6/8 vs
    swung-4/4 is a real curation question, not a bug. Left for a follow-on wave.
  * carnatic/adi_tala IS an 8-beat cycle (8/4 would make one bar = one
    avartanam), but an 8/4 bar is TWICE a 4/4 bar — every fixed-bar section form
    would double in length. It needs the seconds-aware section planner first.

usage: kg_seed_meter.py [--dry]     (--dry prints the plan, writes nothing)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from kg import KG, esc                                                # noqa: E402
from meter import parse_meter                                        # noqa: E402

PROV = ("curated:claude/2026-07-12 (THE WORLD GRID wave, BEST_DAW_30 #1 — "
        "native_meter + odd-meter cells; the archetypes were named for meters "
        "they could not express and played 4/4)")

# genre -> (native_meter, grid patch). The patch is MERGED onto the genre's
# existing PatternArchetype grid — every uncited field (chords/lead/swing/
# gains/voices) survives untouched.
#
# 7/8 aksak = 2+2+3 -> 16th-step group heads [0, 4, 8], bar = 14 steps.
# 9/8 zeibekiko = 2+2+2+3 -> heads [0, 4, 8, 12], bar = 18 steps.
WAVE = {
    "balkan_brass": ("7/8", {
        "groups": [2, 2, 3],
        # the tapan's two deep weights: the bar head and the 3-group head. (The
        # old cell's own vel map already accented exactly these two.)
        "kick": [0, 8],
        # the crack on the 2nd group + the bar's last eighth = the aksak limp
        "snare": [4, 12],
        # the remaining off-eighths (the old [2,6,10,14] put a hat on step 14 —
        # which in a 14-step bar IS the next bar's downbeat)
        "hat": [2, 6, 10],
        "vel": {"kick": {"0": 1.0, "8": 1.0},
                "snare": {"4": 0.9, "12": 0.9}},
    }),
    "rebetiko": ("9/8", {
        "groups": [2, 2, 2, 3],
        "kick": [0, 8],
        # the long group's head takes the weight — the zeibekiko's signature lean
        "snare": [4, 12],
        "hat": [2, 6, 10, 14, 16],
        "vel": {"kick": {"0": 1.0, "8": 0.9},
                "snare": {"4": 0.85, "12": 0.95},
                "hat": {"16": 0.6}},
    }),
    "math_rock": ("7/8", {
        "groups": [2, 2, 3],
        # kick [0,8] + snare [4] were ALREADY the 2+2+3 heads — only the hats
        # (straight 8ths through step 14) spilled over the barline
        "hat": [0, 2, 4, 6, 8, 10, 12],
    }),
}


def bar_steps(m):
    num, den = parse_meter(m)
    return num * 16 // den


def check_cell(genre, meter, grid):
    """Every onset must live inside the bar it was written for."""
    spb = bar_steps(meter) * int(grid.get("bars", 1))
    bad = []
    for lane, steps in grid.items():
        if lane == "lead" and isinstance(steps, dict):
            lspb = bar_steps(meter) * int(steps.get("bars", 1))
            bad += [f"lead step {s} >= {lspb}" for s, _, _ in steps.get("steps", [])
                    if s >= lspb]
        elif isinstance(steps, list) and steps and all(
                isinstance(s, int) for s in steps) and lane != "groups":
            bad += [f"{lane} step {s} >= {spb}" for s in steps if s >= spb]
    return bad


def main(dry=False):
    kg = KG()
    n = 0
    for genre, (nmeter, patch) in sorted(WAVE.items()):
        rows = kg.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})"
                    f"-[:CHARACTERIZED_BY]->(p:PatternArchetype) "
                    f"WHERE p.grid IS NOT NULL "
                    f"RETURN p.name, p.grid, p.provenance, g.provenance")
        if not rows:
            print(f"[skip] {genre}: no PatternArchetype with a grid")
            continue
        pname, gjson, pprov, gprov = rows[0]
        grid = json.loads(gjson)
        grid.update(patch)
        bad = check_cell(genre, nmeter, grid)
        if bad:
            print(f"[ABORT] {genre} ({nmeter}): cell crosses its own barline: {bad}")
            return 1
        gp = gprov or ""
        pp = pprov or ""
        gp = gp if PROV in gp else (gp + " | " + PROV if gp else PROV)
        pp = pp if PROV in pp else (pp + " | " + PROV if pp else PROV)
        spb = bar_steps(nmeter)
        print(f"[{'dry' if dry else 'kg'}] {genre:14s} {nmeter}  bar = {spb} 16ths "
              f"({spb * 0.25} quarters)  archetype {pname}")
        for lane in ("kick", "snare", "hat", "groups"):
            if lane in patch:
                print(f"        {lane:7s} {patch[lane]}")
        if not dry:
            kg.upsert("Genre", genre, gp, native_meter=nmeter)
            kg.upsert("PatternArchetype", pname, pp,
                      grid=json.dumps(grid, sort_keys=True))
        n += 1
    if dry:
        print(f"[dry] would stamp {n} genre(s) — nothing written")
        return 0
    # proof read-back: the graph says it, and every cell fits its bar
    for genre, (nmeter, _) in sorted(WAVE.items()):
        row = kg.q(f"MATCH (g:Genre {{name: '{esc(genre)}'}})"
                   f"-[:CHARACTERIZED_BY]->(p:PatternArchetype) "
                   f"WHERE p.grid IS NOT NULL RETURN g.native_meter, p.grid")
        got, grid = row[0][0], json.loads(row[0][1])
        assert got == nmeter, f"{genre}: read back {got!r} != {nmeter!r}"
        assert not check_cell(genre, nmeter, grid), f"{genre}: cell escaped its bar"
    n_other = kg.q("MATCH (g:Genre) WHERE g.native_meter IS NULL RETURN count(g)")[0][0]
    print(f"[kg-meter] {n} genre(s) carry a native meter; {n_other} stay mapless 4/4 "
          f"(the identity law) — provenance appended, not clobbered")
    print("[kg-meter] NEXT: .venv/bin/python tools/kg_export_cache.py "
          "(the KG-field law — the cache must carry native_meter too)")
    return 0


if __name__ == "__main__":
    sys.exit(main(dry="--dry" in sys.argv))
