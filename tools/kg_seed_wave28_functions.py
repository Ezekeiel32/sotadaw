#!/usr/bin/env python3
"""Wave 28: THE FUNCTIONAL LAYER — chord DNA learns WHY it moves (FHO blueprint,
KG_SOURCES increment 9: ChoCo modeling + Functional Harmony Ontology's T/S/D lens,
pragmatic-modal edition for the genres this graph actually holds).

For every PatternArchetype carrying chords:
  - functions: the progression as a T/S/D string ("T-D-S-S")
  - loop_cadence: how the LOOP resolves (last chord -> first chord classified)
Plus cadence/progression Techniques as first-class nodes with genre edges — the
agent can now say "that's a modal VII-i cadence, standard for amapiano" with a graph
edge behind the sentence.
Provenance: curated:claude/2026-07-05 (wave28 functional layer).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = "curated:claude/2026-07-05 (wave28 functional layer; FHO blueprint KG_SOURCES inc.9)"

# pragmatic-modal function map (minor-rooted electronic/pop practice):
# 1=i tonic, 3=III relative-tonic, 6=VI subdominant-family, 2/4=S, 5=D, 7=VII modal dominant
FUNC = {1: "T", 2: "S", 3: "T", 4: "S", 5: "D", 6: "S", 7: "D"}

CADENCES = {
    (7, 1): ("cadence_modal_VII_i", "the modal cadence: bVII -> i (no leading tone; THE loop-closer of minor-modal electronic music)"),
    (5, 1): ("cadence_authentic_V_i", "authentic cadence V->i: the classical resolve; rare and DELIBERATE in modal genres — flags tonal writing"),
    (4, 1): ("cadence_plagal_IV_i", "plagal IV->i: the soft 'amen' close — gospel/soul/lofi warmth"),
    (6, 1): ("cadence_VI_i_fall", "VI->i fall: subdominant slide home — melancholic loop-closer (trance/dnb/phonk)"),
    (2, 1): ("cadence_ii_i_step", "ii->i step-down close: jazz-adjacent (boombap/lofi ii-V lineage)"),
}
PROGRESSION_TECHS = {
    "axis_progression": ("i-VI-... 4-chord axis family (I-V-vi-IV and rotations): the pop engine",
                         lambda degs: sorted(set(degs)) in ([1, 4, 5, 6], [1, 2, 5, 6])),
    "two_chord_vamp": ("two-chord vamp: harmony as texture, motion lives in the beat (dnb/dub/phonk/ambient)",
                       lambda degs: len(set(degs)) == 2),
    "andalusian_descent": ("stepwise minor descent (i-VII-VI-...): the andalusian/lament lineage",
                           lambda degs: any(degs[i] - 1 == degs[i + 1] or degs[i] + 12 - 1 == degs[i + 1]
                                            for i in range(len(degs) - 1)) and 7 in degs and 6 in degs and 1 in degs),
}

if __name__ == "__main__":
    kg = KG()
    rows = kg.q("MATCH (p:PatternArchetype) RETURN p.name, p.grid")
    stamped, techs_linked = 0, 0
    genre_of = {}   # archetype -> genres using it
    for g, a in kg.q("MATCH (g:Genre)-[:CHARACTERIZED_BY]->(p:PatternArchetype) RETURN g.name, p.name"):
        genre_of.setdefault(a, []).append(g)
    for name, grid_s in rows:
        if not grid_s:
            continue
        try:
            grid = json.loads(grid_s)
        except Exception:
            continue
        chords = grid.get("chords")
        if not chords:
            continue
        degs = [int(c[1]) for c in chords]
        funcs = "-".join(FUNC.get(((d - 1) % 7) + 1, "?") for d in degs)
        norm = [((d - 1) % 7) + 1 for d in degs]
        cad_key = (norm[-1], norm[0])
        cad = CADENCES.get(cad_key)
        kg.upsert("PatternArchetype", name, PROV,
                  functions=funcs, loop_cadence=(cad[0] if cad else f"loop_{norm[-1]}_to_{norm[0]}"))
        stamped += 1
        hits = []
        if cad:
            hits.append(cad)
        for tname, (desc, pred) in PROGRESSION_TECHS.items():
            if pred(norm):
                hits.append((tname, desc))
        for tname, desc in hits:
            kg.upsert("Technique", tname, PROV, desc=desc, weight=0.6)
            for g in genre_of.get(name, []):
                kg.link("Genre", g, "USES_TECHNIQUE", "Technique", tname, weight=0.6)
                techs_linked += 1
        print(f"  {name:18} degs {norm} -> {funcs:12} cadence {(cad[0] if cad else '(open loop)')}"
              + (f"  [{', '.join(t for t, _ in hits)}]" if hits else ""))
    print(f"wave28: {stamped} archetypes functionally annotated, {techs_linked} genre-technique edges")
