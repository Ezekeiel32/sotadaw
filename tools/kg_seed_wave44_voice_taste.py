#!/usr/bin/env python3
"""Wave 44: VOICE TASTE (2026-07-12) — Chezy live: "the insts it picks are
sometimes weird sounding and off-putting. Definitely not production ready."

The census (204 genres, every birth lane) found the crimes; the eligibility
law (kg.eligible_recipe_voice, both DNA paths) stops drum-zone recipe voices
from carrying melodic lanes. This wave curates the genres the law leaves
voiceless, plus the census's worst culture mismatches:

  ukgarage    color was a HI-HAT  -> ukg_stab recipe gains organ_soul (the
              Todd Edwards / MJ Cole chopped-organ stab IS the genre's chords)
  boombap     color was a SNARE   -> grid color_voice rhodes (dusty keys bed)
  hard_techno color was a KICK    -> grid color_voice pad_motion (dark motion
              bed under the rumble; techno-family precedent)
  rnb         lead was formant_vox (a vowel formant synth as THE lead) ->
              rhodes (silky keys lead; sung vocals take over when they land)
  reggaeton   bass was a dnb REESE (bass_style sustained) -> "sub" (round
              808 sub riding the tresillo; the modern perreo low end)
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = ("curated:claude/2026-07-12 (wave44 voice taste; census receipts: "
        "boombap color=snare, ukgarage color=hat, hard_techno color=kick_punch, "
        "rnb lead=formant_vox, reggaeton bass=reese)")


def set_grid_fields(kg, genre, **fields):
    rows = kg.q(f"MATCH (g:Genre {{name:'{esc(genre)}'}})-[:CHARACTERIZED_BY]->"
                "(p:PatternArchetype) WHERE p.grid IS NOT NULL RETURN id(p), p.grid")
    for pid, grid in rows:
        d = json.loads(grid)
        for k, v in fields.items():
            if k == "lead_voice":          # nested: grid.lead.voice
                if isinstance(d.get("lead"), dict):
                    d["lead"]["voice"] = v
            else:
                d[k] = v
        kg.q(f"MATCH (p:PatternArchetype) WHERE id(p) = {int(pid)} "
             f"SET p.grid = '{esc(json.dumps(d))}', "
             f"p.provenance = p.provenance + ' | {esc(PROV)}'")
        return True
    return False


if __name__ == "__main__":
    kg = KG()
    done = []
    if kg.q("MATCH (g:Genre {name:'ukgarage'})-[:CHARACTERIZED_BY]->"
            "(r:SoundRecipe {name:'ukg_stab'}) SET r.voice = 'organ_soul', "
            "r.provenance = r.provenance + ' | " + esc(PROV) + "' RETURN r.name") is not None:
        done.append("ukgarage: ukg_stab -> organ_soul")
    if set_grid_fields(kg, "boombap", color_voice="rhodes"):
        done.append("boombap: color_voice rhodes")
    if set_grid_fields(kg, "hard_techno", color_voice="pad_motion"):
        done.append("hard_techno: color_voice pad_motion")
    if set_grid_fields(kg, "rnb", lead_voice="rhodes"):
        done.append("rnb: lead rhodes")
    if set_grid_fields(kg, "reggaeton", bass_style="sub"):
        done.append("reggaeton: bass_style sub")
    print(f"wave44: {len(done)} taste fixes\n  " + "\n  ".join(done))
