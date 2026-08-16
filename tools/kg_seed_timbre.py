#!/usr/bin/env python3
"""KG SEED: THE TIMBRE TARGET TABLE (backlog wave 20 — R-16 item 018).

Idempotent RoleTimbre node upserts from sound_court.ROLE_TABLE: per-role
centroid fail band, attack class band, width ceiling, tonal class. Bands
not points (the adversarial law). Genre-family refinements land on these
nodes as they are measured (the self-measure loop, item 135).

Provenance: r-16.json role table + corpus calibration via sound_court,
wave 20 (2026-07-15).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402
import sound_court as SC  # noqa: E402

PROV = "backlog-w20 timbre table (R-16, corpus-calibrated 2026-07-15)"


def main():
    g = kg.KG()
    n = 0
    for role, spec in SC.ROLE_TABLE.items():
        attrs = {}
        if "centroid_fail" in spec:
            attrs["centroid_lo"], attrs["centroid_hi"] = \
                float(spec["centroid_fail"][0]), float(spec["centroid_fail"][1])
        if "attack_fail" in spec:
            attrs["attack_lo_ms"], attrs["attack_hi_ms"] = \
                float(spec["attack_fail"][0]), float(spec["attack_fail"][1])
        if "width_max" in spec:
            attrs["width_max_pct"] = float(spec["width_max"])
        if "flat_max" in spec:
            attrs["flatness_max"] = float(spec["flat_max"])
        attrs["tonal"] = bool(spec.get("tonal", False))
        g.upsert("RoleTimbre", role, PROV, **attrs)
        n += 1
    print(f"kg_seed_timbre: {n} RoleTimbre nodes (bands, never points)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
