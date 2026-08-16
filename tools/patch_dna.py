#!/usr/bin/env python3
"""PATCH DNA accessor (wave 54; r-17 item 021) — the kernel lookup that
makes patch design graph facts, not LLM vibes.

  patch_for(genre) -> the genre's PatchArchetype dict (direct
  HAS_PATCH first; up to two SUBGENRE_OF hops of inheritance — an
  unbanked drill variant sounds like its parent, never a guess).
  Returns None when the graph holds nothing (no fake DNA).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _row_to_dict(g, pname):
    rows = g.q(f"MATCH (p:PatchArchetype {{name: '{pname}'}}) RETURN p")
    if not rows:
        return None
    node = rows[0][0]
    props = getattr(node, "properties", None) or {}
    d = dict(props)
    d["name"] = pname
    return d


def patch_for(genre):
    try:
        import kg
        g = kg.KG()
        gn = str(genre or "").lower().replace("-", "_").replace(" ", "_")
        row = g.q(f"MATCH (x:Genre {{name: '{kg.esc(gn)}'}})-[:HAS_PATCH]->"
                  f"(p:PatchArchetype) RETURN p.name LIMIT 1")
        if row and row[0]:
            return _row_to_dict(g, row[0][0])
        row = g.q(f"MATCH (x:Genre {{name: '{kg.esc(gn)}'}})"
                  f"-[:SUBGENRE_OF*1..2]->(a:Genre)-[:HAS_PATCH]->"
                  f"(p:PatchArchetype) RETURN p.name, a.name LIMIT 1")
        if row and row[0]:
            d = _row_to_dict(g, row[0][0])
            if d is not None:
                d["inherited_from"] = row[0][1]
            return d
    except Exception:
        return None
    return None


if __name__ == "__main__":
    print(json.dumps(patch_for(sys.argv[1] if len(sys.argv) > 1 else
                               "trap"), indent=1))
