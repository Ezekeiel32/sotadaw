#!/usr/bin/env python3
"""KG SEED: THE HARMONY MIND (backlog wave 13 — R-1/R-23 items 104/253/038).

Idempotent upserts into FalkorDB:
  HarmonicLoop nodes      canonical per-family progressions (Axis, Royal Road,
                          ii-V-I, 12-bar, EDM minor loops, Andalusian) linked
                          Genre -[:USES_LOOP]-> HarmonicLoop
  Genre.prog_family       which canon grammar judges the genre's chords[]
  Genre.key_profile       which pitch-class profile keys the genre
                          (aarden | supermode | bellman_budge)
  Genre.ext_floor         chord-extension richness floor (R-23/R-21 court)

Provenance: canon repertoire tables (harmony_court.PROG_LIBRARY), wave 13.
Run: .venv/bin/python tools/kg_seed_harmony.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402
import harmony_court as H  # noqa: E402
import theory as T  # noqa: E402

PROV = "backlog-w13 canon tables (R-1/R-23, 2026-07-14)"


def roman_text(prog):
    names = []
    for deg, q in prog:
        base = T.SHARPS[deg % 12]
        names.append(base + (q or ""))
    return "-".join(names)


def main():
    g = kg.KG()
    genres = [r[0] for r in g.q("MATCH (x:Genre) RETURN x.name")]
    if not genres:
        print("kg_seed_harmony: no Genre nodes (is sotadaw-kg up?)")
        return 1
    made_loops = 0
    for fam, progs in H.PROG_LIBRARY.items():
        for i, prog in enumerate(progs):
            name = f"{fam}_loop_{i + 1}"
            g.upsert("HarmonicLoop", name, PROV,
                     family=fam, roman=roman_text(prog),
                     degrees=",".join(str(d) for d, _ in prog),
                     qualities=",".join(q or "maj" for _, q in prog))
            made_loops += 1
    tagged = 0
    for name in genres:
        fam = H._prog_family(name)
        prof = "bellman_budge"
        gmaj, _ = T.key_profiles_for(name)
        if gmaj is T._AARDEN_MAJ:
            prof = "aarden"
        elif gmaj is T._SUPERMODE_MAJ:
            prof = "supermode"
        low = name.lower()
        if any(k in low for k in H._EXT_RICH):
            floor = 0.6
        elif any(k in low for k in H._EXT_M7):
            floor = 0.5
        else:
            floor = 0.0
        g.upsert("Genre", name, PROV, prog_family=fam, key_profile=prof,
                 ext_floor=floor)
        for i in range(len(H.PROG_LIBRARY[fam])):
            g.link("Genre", name, "USES_LOOP", "HarmonicLoop",
                   f"{fam}_loop_{i + 1}")
        tagged += 1
    print(f"kg_seed_harmony: {made_loops} loops upserted, "
          f"{tagged} genres tagged (prog_family/key_profile/ext_floor)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
