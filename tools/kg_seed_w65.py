#!/usr/bin/env python3
"""KG SEED WAVE 65 — item 193 (r-7): MixTarget LUFS windows on the
CORE macro genres updated to the researched as-practiced values
(finished-master integrated loudness, 3-source):

  EDM/house/techno -6..-10, hiphop/trap -8..-11, pop/rock/metal
  -9..-12, jazz -14..-18, classical -18..-24

Subgenres keep their curated windows (the taste circle outranks a
macro table); only the named cores move, provenance-stamped.
--verify = query-backs + idempotency.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402

PROV = "r-7 as-practiced LUFS windows w65 (2026-07-16)"

WINDOWS = {  # genre: (lufs_lo, lufs_hi)
    "edm": (-10, -6), "house": (-10, -6), "techno": (-10, -6),
    "hiphop": (-11, -8), "hip_hop": (-11, -8), "trap": (-11, -8),
    "pop": (-12, -9), "rock": (-12, -9), "metal": (-12, -9),
    "jazz": (-18, -14), "classical": (-24, -18),
}


def seed(g):
    patched = 0
    for name, (lo, hi) in WINDOWS.items():
        rows = g.q(f"MATCH (x:Genre {{name: '{kg.esc(name)}'}})"
                   f"-[:TARGETS]->(m:MixTarget) RETURN m.name")
        if not rows:
            continue
        g.q(f"MATCH (x:Genre {{name: '{kg.esc(name)}'}})-[:TARGETS]->"
            f"(m:MixTarget) SET m.lufs_lo = {lo}, m.lufs_hi = {hi}, "
            f"m.provenance_w65 = '{kg.esc(PROV)}'")
        patched += 1
    return patched


def verify(g):
    fails = []

    def check(name, cond):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    row = g.q("MATCH (x:Genre {name:'house'})-[:TARGETS]->(m) "
              "RETURN m.lufs_lo, m.lufs_hi")
    check("house window = -10..-6 (as practiced)",
          row and row[0][0] == -10 and row[0][1] == -6)
    row = g.q("MATCH (x:Genre {name:'trap'})-[:TARGETS]->(m) "
              "RETURN m.lufs_lo, m.lufs_hi")
    check("trap window tightened to -11..-8 (was -18..-9)",
          row and row[0][0] == -11 and row[0][1] == -8)
    row = g.q("MATCH (x:Genre {name:'classical'})-[:TARGETS]->(m) "
              "RETURN m.lufs_lo")
    check("classical stays dynamic (-24 floor) or unbanked",
          not row or row[0][0] == -24)
    row = g.q("MATCH (x:Genre {name:'deep_house'})-[:TARGETS]->(m) "
              "RETURN m.provenance_w65")
    check("subgenres untouched (deep_house carries no w65 stamp)",
          not row or row[0][0] is None)
    return fails


def main():
    g = kg.KG()
    n = seed(g)
    print(f"[kg_w65] {n} core MixTargets re-windowed")
    if "--verify" in sys.argv:
        seed(g)
        fails = verify(g)
        if fails:
            print(f"kg_w65: {len(fails)} RED — {fails}")
            return 1
        print("kg_w65: ALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
