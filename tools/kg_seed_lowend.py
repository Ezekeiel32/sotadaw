#!/usr/bin/env python3
"""KG SEED: THE LOW-END LAW (backlog wave 15 — R-4/R-5/R-25 items).

Idempotent Genre-field upserts from the low-end court's verified tables:
pump_depth_lo/hi (dB of sidechain duck), env808_decay_lo/hi (ms,
corpus-calibrated), kick_bass_interlock (offbeat_or_duck | transient_split |
kbbb_1516 | free).

Provenance: r-{4,5,25}.json via lowend_court, wave 15 (2026-07-15).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402
import lowend_court as LC  # noqa: E402

PROV = "backlog-w15 low-end law (R-4/R-5/R-25, 2026-07-15)"


def interlock_for(norm):
    if any(k in norm for k in LC._KBBB):
        return "kbbb_1516"
    if any(k in norm for k in ("house", "techno", "trance", "hardstyle",
                               "disco", "edm", "electro", "gabber")):
        return "offbeat_or_duck"
    if any(k in norm for k in ("trap", "drill", "phonk", "hiphop", "hip_hop",
                               "boombap", "rap", "grime")):
        return "transient_split"
    return "free"


def main():
    g = kg.KG()
    genres = [r[0] for r in g.q("MATCH (x:Genre) RETURN x.name")]
    if not genres:
        print("kg_seed_lowend: no Genre nodes (is sotadaw-kg up?)")
        return 1
    n = 0
    for name in genres:
        norm = name.lower().replace("-", "_").replace(" ", "_")
        attrs = {"kick_bass_interlock": interlock_for(norm)}
        for keys, (lo, hi) in LC.PUMP_DEPTH:
            if any(k in norm for k in keys):
                attrs["pump_depth_lo"], attrs["pump_depth_hi"] = \
                    float(lo), float(hi)
                break
        for k, w in sorted(LC.ENV_808.items(), key=lambda kv: -len(kv[0])):
            if k in norm and "decay_ms" in w:
                attrs["env808_decay_lo"] = float(w["decay_ms"][0])
                attrs["env808_decay_hi"] = float(w["decay_ms"][1])
                break
        g.upsert("Genre", name, PROV, **attrs)
        n += 1
    print(f"kg_seed_lowend: {n} genres tagged "
          "(interlock topology / pump depth / 808 env windows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
