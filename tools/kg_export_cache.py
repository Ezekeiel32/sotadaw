#!/usr/bin/env python3
"""Bake the loop-DNA the generator needs into agent/dna_cache.json.

WHY: the KG (FalkorDB on localhost:6380) exists only on the dev box. Any other
machine — the Inspiron, a fresh install — has no graph, no falkordb lib, no
venv. This export makes MAKE/generate_loop work there IDENTICALLY: loop_gen
tries the live graph first (dev box = live curation), falls back to this file.

Re-run after every kg_seed wave (or let check_all catch staleness):
  .venv/bin/python tools/kg_export_cache.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from kg import KG, esc, eligible_recipe_voice

OUT = os.path.join(ROOT, "agent", "dna_cache.json")


def main():
    kg = KG()
    genres = {}
    for gname, aname, grid, lo, hi, key in kg.q(
            "MATCH (g:Genre)-[:CHARACTERIZED_BY]->(p:PatternArchetype) "
            "WHERE p.grid IS NOT NULL "
            "RETURN g.name, p.name, p.grid, g.bpm_lo, g.bpm_hi, g.common_key"):
        genres[gname] = {"archetype": aname, "grid": json.loads(grid),
                         "bpm_lo": lo, "bpm_hi": hi, "key": key}
    for gname, voice in kg.q(
            "MATCH (g:Genre)-[:CHARACTERIZED_BY]->(r:SoundRecipe) "
            "WHERE r.voice IS NOT NULL RETURN g.name, r.voice"):
        # LIMIT 1 semantics of the live query: keep the FIRST voice seen per
        # genre — first ELIGIBLE (THE TASTE LAW 2026-07-12: drum-zone recipe
        # voices handed boombap's chord lane a SNARE; same predicate as the
        # live path, the two-path DNA rule).
        if gname in genres and "voice" not in genres[gname] \
                and eligible_recipe_voice(voice):
            genres[gname]["voice"] = voice
    for gname, border, llo, lhi, psr, lra in kg.q(
            "MATCH (g:Genre)-[:TARGETS]->(m:MixTarget) "
            "RETURN g.name, m.band_order, m.lufs_lo, m.lufs_hi, m.psr_floor, "
            "m.lra_floor"):
        if gname in genres:
            genres[gname].update({"band_order": border, "lufs_lo": llo, "lufs_hi": lhi})
            if psr is not None:            # E12 physics floors (KG-field law:
                genres[gname]["psr_floor"] = psr   # ride BOTH query and cache)
            if lra is not None:            # W66 breath floors, same law
                genres[gname]["lra_floor"] = lra
    for gname, grname in kg.q(
            "MATCH (g:Genre)-[:HAS_GROOVE]->(gr:Groove) RETURN g.name, gr.name"):
        # first edge wins: the genre's signature FEEL, applied at loop birth
        if gname in genres and "groove" not in genres[gname]:
            genres[gname]["groove"] = grname
    # INHERIT (one hop): a subgenre with no own groove takes its parent's feel —
    # the same rule as inherited_techniques/psr_floor. A death_metal grooves like
    # metal (rock_drive's 0.006-beat push), never a dead grid. Direct edge wins.
    for gname, grname in kg.q(
            "MATCH (g:Genre)-[:SUBGENRE_OF]->(:Genre)-[:HAS_GROOVE]->(gr:Groove) "
            "RETURN g.name, gr.name"):
        if gname in genres and "groove" not in genres[gname]:
            genres[gname]["groove"] = grname
    for gname, vc in kg.q("MATCH (g:Genre) WHERE g.voicing IS NOT NULL RETURN g.name, g.voicing"):
        if gname in genres:
            genres[gname]["voicing"] = json.loads(vc)
    # THE WORLD GRID (#1): the genre's native meter — absent = 4/4 (the identity
    # law, so only the odd-meter genres carry the key). KG-FIELD LAW: this rides
    # BOTH the live query (loop_gen.genre_dna) and this cache path, or it
    # silently vanishes on every machine without a graph.
    for gname, nm in kg.q("MATCH (g:Genre) WHERE g.native_meter IS NOT NULL "
                          "RETURN g.name, g.native_meter"):
        if gname in genres:
            genres[gname]["native_meter"] = nm
    for gname, ff in kg.q("MATCH (g:Genre) WHERE g.form_family IS NOT NULL RETURN g.name, g.form_family"):
        if gname in genres:
            genres[gname]["form_family"] = ff
    # INHERIT (one hop): a subgenre with no own form_family takes its parent's
    # song-structure family — the same rule as groove/technique inheritance. A
    # jungle arranges club-form like its dnb parent, not the generic default.
    # Direct value above wins; the 74 genres with no form-bearing parent stay on
    # arrange.py's family default (their curation is the pending KG wave).
    for gname, ff in kg.q("MATCH (g:Genre)-[:SUBGENRE_OF]->(p:Genre) "
                          "WHERE p.form_family IS NOT NULL RETURN g.name, p.form_family"):
        # setdefault, not `in genres`: an archetype-less subgenre (no loop
        # DNA of its own — chicago_drill, 2026-07-17) still ARRANGES, and
        # arrange.py reads form_family from this cache only; gating on the
        # archetype dict silently dropped it to the generic form
        if "form_family" not in genres.setdefault(gname, {}):
            genres[gname]["form_family"] = ff
    # ATOMIC (wave 43, ledger MED): arrange/loop_gen/finish read this file while
    # seed waves rebake it — a torn read used to silently drop every genre to
    # the EDM form. tmp + os.replace, the same law as genres.json below.
    _tmp_out = OUT + ".w~"
    json.dump({"genres": genres}, open(_tmp_out, "w"), indent=0, sort_keys=True)
    os.replace(_tmp_out, OUT)
    # W127 THE DROPDOWN ARTIFACT: agent/genres.json feeds the UI's MAKE
    # genre box at launch. It was ORPHANED (its producer left the tree;
    # 74 genres stale by 2026-07-11) — now it regenerates with every
    # cache export, so seed waves reach the dropdown automatically.
    gj = os.path.join(ROOT, "agent", "genres.json")
    tmp = gj + ".w~"
    with open(tmp, "w") as f:
        json.dump(sorted(genres), f, indent=1)
    os.replace(tmp, gj)
    print(f"genres.json: {len(genres)} genres -> {gj}")
    print(f"dna_cache: {len(genres)} genres -> {OUT} "
          f"({os.path.getsize(OUT) // 1024} KB)")


if __name__ == "__main__":
    main()
