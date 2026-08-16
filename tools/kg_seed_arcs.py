#!/usr/bin/env python3
"""KG SEED: THE ARC TEMPLATES (backlog wave 18 — R-14 item 017, R-20 027).

Idempotent Genre-field upserts from the tension court's verified tables:
arc_family (one of tension.ARC_FAMILIES), climax_lo/climax_hi (the
validated 65-85% window, genre-shifted), hook_first (pop preview idiom),
drop_law (EDM drop-contrast court applies). Farbood's 6 contours are the
family vocabulary; r-14's genre form templates pick per family.

Provenance: r-14.json/r-20.json via tension.py, wave 18 (2026-07-15).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402
import tension as TN  # noqa: E402

PROV = "backlog-w18 arc templates (R-14/R-20, 2026-07-15)"

FAMILY_TABLE = (
    # texture = plateau (checked first: most specific stand-down)
    (("ambient", "drone", "meditation", "soundscape", "new_age", "field",
      "lowercase", "dark_ambient", "chillout", "downtempo"), "plateau"),
    # journey / hypnotic = long ramp (before EDM: psytrance beats 'trance')
    (("psytrance", "goa", "psy", "minimal", "dub_techno", "berlin",
      "krautrock", "post_rock"), "ramp"),
    # EDM / build-drop forms = oscillating (sharp pre-drop ramps)
    (("edm", "house", "techno", "trance", "dubstep", "dnb", "drum_and_bass",
      "hardstyle", "big_room", "electro", "garage", "riddim", "breakbeat",
      "bass_music", "gabber", "hard_house"), "oscillating"),
    # ballad / song forms = single arch
    (("ballad", "soul", "gospel", "rnb", "r_b", "country", "folk", "indie",
      "rock", "blues", "jazz", "singer", "acoustic", "motown", "doo_wop"),
     "arch"),
    # verse/hook alternation = peak (late inverted-V)
    (("pop", "kpop", "jpop", "hiphop", "hip_hop", "trap", "drill", "grime",
      "phonk", "rap", "reggaeton", "afrobeats", "amapiano", "dancehall"),
     "peak"),
)


def family_for(norm):
    for keys, fam in FAMILY_TABLE:
        if any(k in norm for k in keys):
            return fam
    return "arch"


def main():
    g = kg.KG()
    genres = [r[0] for r in g.q("MATCH (x:Genre) RETURN x.name")]
    if not genres:
        print("kg_seed_arcs: no Genre nodes (is sotadaw-kg up?)")
        return 1
    n = 0
    for name in genres:
        norm = name.lower().replace("-", "_").replace(" ", "_")
        fam = family_for(norm)
        attrs = {"arc_family": fam,
                 "climax_lo": TN.CLIMAX_LO, "climax_hi": TN.CLIMAX_HI,
                 "hook_first": any(k in norm for k in TN._HOOK_FIRST),
                 "drop_law": any(k in norm for k in TN._EDM)}
        if fam == "plateau":       # texture: no climax demand
            attrs["climax_lo"], attrs["climax_hi"] = 0.0, 1.0
        g.upsert("Genre", name, PROV, **attrs)
        n += 1
    print(f"kg_seed_arcs: {n} genres tagged "
          "(arc family / climax window / hook-first / drop law)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
