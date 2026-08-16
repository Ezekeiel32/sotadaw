#!/usr/bin/env python3
"""KG SEED: THE TRANSLATION WINDOWS (backlog wave 22 — R-7 items
119/190).

Idempotent Genre-field upserts from translation_court's CORPUS-MEASURED
family windows: tilt_lo/tilt_hi (LTAS dB/oct), band_low_lo/band_low_hi
(20-250Hz power %), band_highmid_max. Band-dependent tolerance is the
law: bass cells are wide, mid cells tight.

Provenance: r-7.json recipes, windows measured from the project's own
corpus (self-measure 2026-07-15), via translation_court, wave 22.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402
import translation_court as TC  # noqa: E402

PROV = "backlog-w22 translation windows (R-7, corpus-measured 2026-07-15)"


def main():
    g = kg.KG()
    genres = [r[0] for r in g.q("MATCH (x:Genre) RETURN x.name")]
    if not genres:
        print("kg_seed_translation: no Genre nodes (is sotadaw-kg up?)")
        return 1
    n = 0
    for name in genres:
        fam = TC.family_for(name)
        t_lo, t_hi, b_lo, b_hi, hm = TC.FAMILY_WINDOWS[fam]
        g.upsert("Genre", name, PROV,
                 translation_family=fam,
                 tilt_lo=float(t_lo), tilt_hi=float(t_hi),
                 band_low_lo=float(b_lo), band_low_hi=float(b_hi),
                 band_highmid_max=float(hm))
        n += 1
    print(f"kg_seed_translation: {n} genres tagged "
          "(family / tilt window / band windows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
