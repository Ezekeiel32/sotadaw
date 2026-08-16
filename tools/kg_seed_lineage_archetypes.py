#!/usr/bin/env python3
"""KG seed — LINEAGE ARCHETYPES (2026-07-17): an archetype-less subgenre
plays its PARENT's grid until someone curates its own.

The 808-lineage wave linked memphis_phonk / chicago_drill SUBGENRE_OF
(memphis_rap / trap) without giving them loop DNA — dna_battery's
groove-inheritance parity turned red at HEAD (live groove resolves inside
the archetype branch, and generate() refused two real genres outright).
Generic one-hop rule, MERGE-idempotent: for every subgenre with NO
CHARACTERIZED_BY->PatternArchetype whose parent HAS one, link the child to
the parent's first archetype. A future curation wave that gives the child
its OWN archetype should DELETE this inherited edge in the same commit
(two archetype edges make the live pick ambiguous).

After running: tools/kg_export_cache.py (the cache is what no-graph
machines read) — then dna_battery judges parity.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from kg import KG


def main():
    kg = KG()
    rows = kg.q(
        "MATCH (g:Genre)-[:SUBGENRE_OF]->(p:Genre)-[:CHARACTERIZED_BY]->"
        "(a:PatternArchetype) WHERE a.grid IS NOT NULL "
        "AND NOT (g)-[:CHARACTERIZED_BY]->(:PatternArchetype) "
        "RETURN g.name, p.name, a.name")
    seen = set()
    for child, parent, arch in rows:
        if child in seen:
            continue                      # first parent archetype wins
        seen.add(child)
        kg.link("Genre", child, "CHARACTERIZED_BY", "PatternArchetype", arch)
        print(f"  {child} plays {parent}'s grid ({arch}) until curated")
    print(f"lineage archetypes: {len(seen)} subgenres linked (idempotent)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
