#!/usr/bin/env python3
"""THE WORLD BAND WIRING (2026-07-31; provenance APPENDS — the first run REPLACED and erased lineage, healed same day from git-truth seed waves) — point the worst-eval genres' DNA at the
identity voices minted in 54fad62 (they birthed on placeholders because the
instruments did not exist; band evidence in docs/VOICE_HEADROOM_CAMPAIGN.md +
agents_collab 07:4x-07:5x).

Grid surgery (PatternArchetype.grid JSON):
  balkan_brass  lead.voice brass_stab -> trumpet_lead; +bass_voice tuba (oompah)
  arabesk       lead.voice strings_stacc -> saz; +hat_voice darbuka
  bachata       lead.voice pluck -> clean_chime_guitar; +hat_voice guira
  bhangra       lead.voice pluck -> tumbi
  chimurenga    lead.voice kalimba -> mbira (the archetype is NAMED mbira_wheel)
SoundRecipe surgery:
  bluegrass     recipe voice pluck -> banjo (color lane; fiddle keeps the lead)

Per-lane overrides (bass_voice/hat_voice) need loop_gen's override hook — this
script refuses to run until loop_gen.py contains 'bass_voice' (fail-closed:
data without the reader = silently inert DNA).

Idempotent; every touched node gets provenance. After: kg_export_cache.py, then
births + band-split verification (expect low% to fall toward declared band_order).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from kg import KG, esc

PROV = "worldband wiring 2026-07-31 (54fad62 voices; eval-floor evidence agents_collab 07:4x)"

GRID_SWAPS = {
    "balkan_brass": {"lead.voice": "trumpet_lead", "bass_voice": "tuba"},
    "arabesk": {"lead.voice": "saz", "hat_voice": "darbuka"},
    "bachata": {"lead.voice": "clean_chime_guitar", "hat_voice": "guira"},
    "bhangra": {"lead.voice": "tumbi"},
    "chimurenga": {"lead.voice": "mbira"},
}
RECIPE_SWAPS = {"bluegrass": ("pluck", "banjo")}


def main(dry=False):
    hook = open(os.path.join(ROOT, "tools", "loop_gen.py")).read()
    if "bass_voice" not in hook:
        print("REFUSING: loop_gen.py has no per-lane override hook yet "
              "(grid bass_voice/hat_voice would be inert DNA)")
        return 1
    kg = KG()
    changed = 0
    for genre, swaps in GRID_SWAPS.items():
        rows = kg.q(f"MATCH (g:Genre {{name:'{esc(genre)}'}})-[:CHARACTERIZED_BY]->"
                    f"(p:PatternArchetype) WHERE p.grid IS NOT NULL "
                    f"RETURN p.name, p.grid")
        if not rows:
            print(f"  {genre}: NO ARCHETYPE GRID — skipped")
            continue
        pname, grid_s = rows[0][0], rows[0][1]
        grid = json.loads(grid_s)
        before = json.dumps(grid, sort_keys=True)
        for path, val in swaps.items():
            if path == "lead.voice":
                grid.setdefault("lead", {})["voice"] = val
            else:
                grid[path] = val
        after = json.dumps(grid, sort_keys=True)
        if before == after:
            print(f"  {genre}: grid already wired")
            continue
        changed += 1
        print(f"  {genre} [{pname}]: {swaps}")
        if not dry:
            kg.q(f"MATCH (g:Genre {{name:'{esc(genre)}'}})-[:CHARACTERIZED_BY]->"
                 f"(p:PatternArchetype {{name:'{esc(pname)}'}}) "
                 f"SET p.grid = '{esc(json.dumps(grid))}', "
                 f"p.provenance = coalesce(p.provenance, 'curated') + ' | {esc(PROV)}'")
    for genre, (old, new) in RECIPE_SWAPS.items():
        rows = kg.q(f"MATCH (g:Genre {{name:'{esc(genre)}'}})-[:CHARACTERIZED_BY]->"
                    f"(r:SoundRecipe) WHERE r.voice = '{esc(old)}' "
                    f"RETURN r.name, r.voice")
        if not rows:
            print(f"  {genre}: recipe voice != {old} (already wired or absent)")
            continue
        changed += 1
        print(f"  {genre} recipe [{rows[0][0]}]: {old} -> {new}")
        if not dry:
            kg.q(f"MATCH (g:Genre {{name:'{esc(genre)}'}})-[:CHARACTERIZED_BY]->"
                 f"(r:SoundRecipe {{name:'{esc(rows[0][0])}'}}) "
                 f"SET r.voice = '{esc(new)}', "
                 f"r.provenance = coalesce(r.provenance, 'curated') + ' | {esc(PROV)}'")
    print(f"{'DRY: ' if dry else ''}{changed} nodes {'would change' if dry else 'changed'}")
    if changed and not dry:
        print("NEXT: .venv/bin/python tools/kg_export_cache.py && births + band verify")
    return 0


if __name__ == "__main__":
    sys.exit(main(dry="--dry" in sys.argv))
