#!/usr/bin/env python3
"""THE CURRICULUM AUDIT (THE_UTMOST §8 road: which genres lack grooves / gold /
recipes / skills — the gap map, named so the factory knows where to aim).

Coverage per genre is read from the graph (MixTarget / Groove / Technique /
SoundRecipe edges), the gold bank (library/gold), and the skills shelf
(<genre>-arrangement.v*). DEMAND comes from telemetry — genres Chezy actually
asks for rank first, so depth lands where it is felt. Output is a worklist of
concrete actions (seed grooves / bank gold / compile skill), not a lament.

  report        the live audit (needs FalkorDB up: docker start sotadaw-kg)
  --selftest    kernel proof, graph-free (the suite leg)
"""
from __future__ import annotations
import json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

GAP_ACTIONS = {
    "no_mixtarget":    "seed a MixTarget (tools/kg_seed*.py wave)",
    "no_grooves":      "seed HAS_GROOVE profiles (the feel is born in)",
    "no_gold":         "bank gold DNA (tools/gold_bank.py seed — needs an ears-passed exemplar)",
    "no_skill":        "compile the skill (tools/skill_compiler.py <g> --publish)",
    "thin_techniques": "curate techniques (<3 in graph — the vocabulary is thin)",
}


def genre_gaps(row, gold_set, skill_set, straight=frozenset()):
    """row: {name, mixtargets, grooves, techniques, recipes} -> [gap names].
    `straight` = the groove atlas's STRAIGHT_ON_PURPOSE set: a documented NONE
    is a RULING, not a gap (the audit never re-litigates curation silently —
    demanded members surface separately as revisit candidates)."""
    g = []
    if row.get("mixtargets", 0) == 0:
        g.append("no_mixtarget")
    if row.get("grooves", 0) == 0 and row["name"] not in straight:
        g.append("no_grooves")
    if row["name"] not in gold_set:
        g.append("no_gold")
    if row["name"] not in skill_set:
        g.append("no_skill")
    if 0 < row.get("techniques", 0) < 3:
        g.append("thin_techniques")
    return g


def rank(rows, demand, gold_set, skill_set, straight=frozenset()):
    """-> [(score, row, gaps)] worst-first. Demand multiplies: a gap in a genre
    Chezy asks for outranks ten gaps in one nobody has touched."""
    out = []
    for row in rows:
        gaps = genre_gaps(row, gold_set, skill_set, straight)
        if not gaps:
            continue
        score = (1 + demand.get(row["name"], 0) * 3) * len(gaps)
        out.append((score, row, gaps))
    out.sort(key=lambda x: (-x[0], x[1]["name"]))
    return out


def load_demand():
    c = Counter()
    try:
        for line in open(os.path.join(ROOT, "telemetry", "proposals.jsonl"),
                         errors="replace"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r.get("genre"), str):
                c[r["genre"]] += 1
    except OSError:
        pass
    return c


def load_shelves():
    gold = set()
    try:
        gold = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(ROOT, "library", "gold"))
                if f.endswith(".json")}
    except OSError:
        pass
    skills = set()
    try:
        for f in os.listdir(os.path.join(ROOT, "skills")):
            m = re.match(r"(.+)-arrangement\.v\d+\.md$", f)
            if m:
                skills.add(m.group(1))
    except OSError:
        pass
    return gold, skills


def report():
    from kg import KG
    k = KG()
    res = k.q(
        "MATCH (g:Genre) "
        "OPTIONAL MATCH (g)-[:TARGETS]->(m:MixTarget) "
        "OPTIONAL MATCH (g)-[:HAS_GROOVE]->(gr:Groove) "
        "OPTIONAL MATCH (g)-[:USES_TECHNIQUE]->(t:Technique) "
        "OPTIONAL MATCH (g)-[:CHARACTERIZED_BY]->(sr:SoundRecipe) "
        "RETURN g.name, count(DISTINCT m), count(DISTINCT gr), "
        "count(DISTINCT t), count(DISTINCT sr) ORDER BY g.name")
    rows = [{"name": r[0], "mixtargets": r[1], "grooves": r[2],
             "techniques": r[3], "recipes": r[4]} for r in res if r and r[0]]
    gold, skills = load_shelves()
    demand = load_demand()
    try:
        from kg_seed_grooves import STRAIGHT_ON_PURPOSE as straight
    except Exception:
        straight = frozenset()
    ranked = rank(rows, demand, gold, skills, straight)
    complete = len(rows) - len(ranked)
    print(f"THE CURRICULUM — {len(rows)} genres in the graph; "
          f"{complete} fully deep, {len(ranked)} carry gaps "
          f"(gold bank {len(gold)}, skill shelf {len(skills)})")
    print("\nTHE WORKLIST (demand-weighted, worst first):")
    for score, row, gaps in ranked[:16]:
        d = demand.get(row["name"], 0)
        dstr = f" asked x{d}" if d else ""
        print(f"  {row['name']:<22} score {score:>3}{dstr:<12} gaps: {', '.join(gaps)}")
    print("\nACTIONS (top 8):")
    seen = set()
    for score, row, gaps in ranked:
        for gap in gaps:
            key = (row["name"], gap)
            if key in seen or len(seen) >= 8:
                continue
            seen.add(key)
            print(f"  {row['name']}: {GAP_ACTIONS[gap]}")
        if len(seen) >= 8:
            break
    revisit = sorted((demand[n], n) for n in straight if demand.get(n, 0) > 0)
    if revisit:
        print("\nDELIBERATE-STRAIGHT, DEMANDED (groove NONE is a documented ruling; "
              "demand says re-argue it with evidence, the gqom way):")
        for d, n in reversed(revisit):
            print(f"  {n}: asked x{d}")
    hot = [(s, r, g) for s, r, g in ranked if demand.get(r["name"], 0) > 0]
    if hot:
        print(f"\nFELT GAPS: {len(hot)} genres Chezy has ASKED FOR carry gaps — "
              "these outrank everything uncurated.")
    return 0


def selftest():
    n = [0]
    def check(name, cond):
        print(("  PASS " if cond else "  FAIL ") + name)
        if not cond:
            sys.exit(1)
        n[0] += 1
    rows = [
        {"name": "house",   "mixtargets": 1, "grooves": 2, "techniques": 8, "recipes": 3},
        {"name": "gabber",  "mixtargets": 0, "grooves": 0, "techniques": 1, "recipes": 0},
        {"name": "zydeco",  "mixtargets": 0, "grooves": 0, "techniques": 0, "recipes": 0},
    ]
    gold, skills = {"house"}, {"house"}
    check("complete genre carries no gaps", genre_gaps(rows[0], gold, skills) == [])
    g = genre_gaps(rows[1], gold, skills)
    check("all five gap classes detected",
          set(g) == {"no_mixtarget", "no_grooves", "no_gold", "no_skill", "thin_techniques"})
    check("zero techniques is uncurated, not 'thin'",
          "thin_techniques" not in genre_gaps(rows[2], gold, skills))
    check("deliberate-straight is a RULING, not a gap",
          "no_grooves" not in genre_gaps(rows[1], gold, skills, straight={"gabber"})
          and "no_gold" in genre_gaps(rows[1], gold, skills, straight={"gabber"}))
    ranked = rank(rows, {"gabber": 2}, gold, skills)
    check("complete genre absent from worklist", all(r["name"] != "house" for _, r, _ in ranked))
    check("DEMANDED gaps outrank undemanded (gabber asked x2 > zydeco)",
          ranked[0][1]["name"] == "gabber")
    check("every gap names its action", set(GAP_ACTIONS) >= set(ranked[0][2]))
    print(f"CURRICULUM AUDIT SELFTEST: {n[0]}/7 PASS")
    return 0 if n[0] == 7 else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else report())
