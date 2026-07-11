#!/usr/bin/env python3
"""Wave 45: THE BEIGE SWEEP (2026-07-12) — the census (taste campaign, Chezy
live: "insts it picks are weird/off-putting") showed pluck/pluck2 leading 44
genres and bass_warm under 114 melodic lanes — while the voices these genres
are DEFINED by sit unused in instruments/: fiddle, upright_bass, acid303,
oud, strings_disco, ep_bright, cine_brass, clean_chime_guitar.

Every pick below is an identity claim, not a preference:
  guitar cultures  -> clean_chime_guitar (soukous sebene, highlife, bossa
                      nylon comp, fado/morna Portuguese guitar, samba
                      cavaquinho, surf twang, flamenco nylon)
  rebetiko/chaabi  -> oud (bouzouki / Algerian mandole family)
  bluegrass/country-> fiddle (THE bluegrass lead)
  mariachi         -> cine_brass (the trumpet section)
  soca             -> brass_stab (the horn hits)
  detroit_techno   -> strings_disco (the Rhythim Is Rhythim string stab)
  goa              -> acid303 (the squelch IS the language)
  grime            -> chiptune_pulse (sinogrime square bleeps)
  gfunk            -> sine_siren (the portamento whine — glide built in)
  new_jack_swing   -> ep_bright (DX7 electric piano hits)
  kpop/jpop        -> supersaw (the modern synth hook)
  upright_bass     -> the jazz family + bossanova/bluegrass/tango/doo_wop/
                      klezmer (double bass cultures born with electric warmth)
  reese bass       -> ebm/industrial/darksynth/hyperpop (sequenced saw throb)
  sub_clean        -> chillwave/synthpop/ambient/berlin_school (synth sub)
  sub_808_slide    -> footwork/miami_bass/ghettotech (the 808 IS the genre)
  ambient color    -> pad_motion (was marimba plink under a beatless bed)

Assignments ride the grid blob (lead_voice/bass_voice/color_voice, W47/W71)
— both DNA paths inherit them with no schema change.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG, esc

PROV = ("curated:claude/2026-07-12 (wave45 beige sweep; census receipts in "
        "the taste campaign — identity voices existed unused in instruments/)")

LEAD = {}
for g in ("surf_rock", "soukous", "highlife", "benga", "juju", "champeta",
          "mbaqanga", "ndombolo", "kompa", "bossanova", "fado", "morna",
          "samba", "flamenco"):
    LEAD[g] = "clean_chime_guitar"
LEAD.update({"rebetiko": "oud", "chaabi": "oud",
             "bluegrass": "fiddle", "country": "fiddle",
             "mariachi": "cine_brass", "soca": "brass_stab",
             "detroit_techno": "strings_disco", "goa": "acid303",
             "grime": "chiptune_pulse", "gfunk": "sine_siren",
             "new_jack_swing": "ep_bright",
             "kpop": "supersaw", "jpop": "supersaw"})

BASS = {}
for g in ("jazz", "bebop", "hard_bop", "modal_jazz", "free_jazz",
          "spiritual_jazz", "swing_bigband", "bossanova", "bluegrass",
          "tango", "doo_wop", "klezmer"):
    BASS[g] = "upright_bass"
for g in ("ebm", "industrial", "darksynth", "hyperpop"):
    BASS[g] = "reese"
for g in ("chillwave", "synthpop", "ambient", "berlin_school"):
    BASS[g] = "sub_clean"
for g in ("footwork", "miami_bass", "ghettotech"):
    BASS[g] = "sub_808_slide"

COLOR = {"ambient": "pad_motion"}


def set_grid_fields(kg, genre, **fields):
    rows = kg.q(f"MATCH (g:Genre {{name:'{esc(genre)}'}})-[:CHARACTERIZED_BY]->"
                "(p:PatternArchetype) WHERE p.grid IS NOT NULL RETURN id(p), p.grid")
    for pid, grid in rows:
        d = json.loads(grid)
        for k, v in fields.items():
            d[k] = v                        # top-level field wins in loop_gen
            if k == "lead_voice" and isinstance(d.get("lead"), dict):
                d["lead"]["voice"] = v      # keep the nested block consistent
        kg.q(f"MATCH (p:PatternArchetype) WHERE id(p) = {int(pid)} "
             f"SET p.grid = '{esc(json.dumps(d))}', "
             f"p.provenance = p.provenance + ' | {esc(PROV)}'")
        return True
    return False


if __name__ == "__main__":
    kg = KG()
    done, miss = 0, []
    for g, v in LEAD.items():
        (set_grid_fields(kg, g, lead_voice=v) and (done := done + 1)) or miss.append(f"{g}(lead)")
    for g, v in BASS.items():
        (set_grid_fields(kg, g, bass_voice=v) and (done := done + 1)) or miss.append(f"{g}(bass)")
    for g, v in COLOR.items():
        (set_grid_fields(kg, g, color_voice=v) and (done := done + 1)) or miss.append(f"{g}(color)")
    print(f"wave45: {done} identity voices assigned"
          + (f" — MISSING: {miss}" if miss else ""))
