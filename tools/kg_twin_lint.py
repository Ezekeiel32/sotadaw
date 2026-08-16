#!/usr/bin/env python3
"""KG TWIN LINT — no two graph nodes may be the same name in different clothes.

The disease (healed 2026-07-25, three cases): a seed wave spells a genre its
own way ("jersey_club") while the graph's real node is another spelling
("jerseyclub") — MERGE happily mints a STUB twin, parent edges point into the
void, groove/skill inheritance silently dead-ends, and per-genre courts keyed
by the other spelling never fire. jersey_drill's club lineage was broken this
way for 8 days; boom_bap sat at degree 0; drift_phonk split w52's researched
DNA off the rich driftphonk node.

Law: within each audited label, node names must be UNIQUE after folding
case/underscores/hyphens/spaces. A fold-collision = suite RED with both
spellings and their degrees (the low-degree one is almost always the stub —
rekey the seed wave to the rich name, migrate unique edges, DETACH DELETE).

Graph down (docker sotadaw-kg stopped) = skip-pass: a lint that cannot see
the graph is not evidence against it.  Suite leg via ghost_suite.sh.
"""
import sys
from collections import defaultdict

AUDITED = ("Genre", "Technique", "Groove", "MixTarget", "SoundRecipe")


def fold(name):
    return str(name).lower().replace("_", "").replace("-", "").replace(" ", "")


def main():
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    try:
        import kg
        g = kg.connect()
        g.query("RETURN 1")
    except Exception as e:
        print(f"kg twin lint: SKIP (graph unreachable: {e.__class__.__name__})")
        return 0
    red = 0
    for label in AUDITED:
        names = [r[0] for r in
                 g.query(f"MATCH (x:{label}) RETURN x.name").result_set
                 if r and r[0] is not None]
        by_fold = defaultdict(list)
        for n in names:
            by_fold[fold(n)].append(n)
        twins = {k: v for k, v in by_fold.items() if len(v) > 1}
        for group in twins.values():
            red += 1
            degs = []
            for n in group:
                d = g.query(f"MATCH (x:{label} {{name: $n}}) "
                            "OPTIONAL MATCH (x)-[r]-() RETURN count(r)",
                            {"n": n}).result_set[0][0]
                degs.append(f"{n}(deg {d})")
            print(f"FAIL {label} fold-twin: " + " vs ".join(degs)
                  + "  — rekey the seed wave to the rich name, migrate unique "
                    "edges, DETACH DELETE the stub")
        print(f"{label}: {len(names)} nodes, {len(twins)} twins")
    # SKILLDOC-DANGLE sweep (2026-08-02): every SkillDoc.file must exist under
    # skills/ — a republished skill that renames its file leaves the graph
    # pointing at nothing, and get_skill serves the void (2 dangles found by
    # hand that day: an always-bump probe + a stale blues@v5).
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        rows = g.query("MATCH (s:SkillDoc) RETURN s.name, s.file").result_set
    except Exception:
        rows = []
    def _exists(f):
        f = str(f)
        return os.path.exists(os.path.join(root, f)) or \
            os.path.exists(os.path.join(root, "skills", f))
    dangles = [(n, f) for n, f in rows if f and not _exists(f)]
    for n, f in dangles:
        red += 1
        print(f"FAIL SkillDoc dangle: {n} -> {f} (no such file under skills/)"
              "  — republish the skill or repoint/DELETE the doc node")
    print(f"SkillDoc: {len(rows)} docs, {len(dangles)} dangles")
    print("kg twin lint: " + ("RED" if red else "clean — one name, one node"))
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
