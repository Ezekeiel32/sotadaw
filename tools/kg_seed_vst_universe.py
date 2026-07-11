#!/usr/bin/env python3
"""VST UNIVERSE wave 1 (2026-07-03): the manifesto pillar starts moving —
free third-party plugins installed rootless (~/.vst3), scanned, hosted,
rendered, and param-verified (TAL 'Filter Cutoff' 0.15->0.95 = centroid
51->2761Hz from song JSON). Recipes teach agents to REACH for them.
Roster: Odin2 (263 named params), TAL-NoiseMaker (93), Dragonfly
Hall/Room/Plate/EarlyReflections, + prior Surge XT (+FX), Dexed = 9.
Idempotent (MERGE)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-vst-universe-w1 (render+param A/B verified: TAL cutoff 51->2761Hz)"
    R = {
     "tal_analog_bass": ("vst3:TAL-NoiseMaker",
        "TAL-NoiseMaker as the analog bass/lead: source {kind:'vst3', id:'TAL-NoiseMaker', params:{'Filter Cutoff':0.2-0.5,'Filter Resonance':0.2-0.5,'Filter Contour':0.3+}} — params fuzzy-match by NAME; automate any of its 93 knobs via set_track_param/automate",
        ["acid_house", "electro", "house", "synthwave", "italo_disco", "ebm"]),
     "odin_modular_lead": ("vst3:Odin2",
        "Odin2 (263 named params: Osc1-3 wavetable/analog/FM, dual filters, 3 envs) as the big lead/pad synth: source {kind:'vst3', id:'Odin2'} + params by name ('Osc1 Wavetble Position', 'Filter1 Freq'...) — design leads for trance/hardwave/dubstep beyond the faust palette",
        ["trance", "hardwave", "dubstep", "progressive_house", "future_bass"]),
     "dragonfly_space": ("vst3:Dragonfly",
        "the Dragonfly reverb family as track fx ({'id':'vst3:Dragonfly Hall Reverb'} etc.): Hall = cinematic/ambient beds, Room = drum glue, Plate = vocals/leads, Early Reflections = tightening — a pro reverb rack beyond fx_reverb",
        ["ambient", "orchestral_cinematic", "dub_techno", "shoegaze", "gospel"]),
    }
    for name, (voice, desc, genres) in R.items():
        kg.upsert("SoundRecipe", name, prov, voice=voice, desc=desc)
        for g in genres:
            kg.link("Genre", g, "CHARACTERIZED_BY", "SoundRecipe", name)
    print("vst-universe recipes seeded:", ", ".join(R))

if __name__ == "__main__":
    seed()


def seed_preset_rail():
    """Preset rail (2026-07-03): TAL's 256 factory presets playable via
    tal_presets.py get -> source.params (normalized-name matching in SongLoader).
    Acoustically verified: PAD 448ms/779Hz, BASS 10ms/338Hz."""
    kg = KG()
    prov = "verified:tal-preset-rail/2026-07-03 (pad 448ms attack/779Hz; bass 10ms/338Hz)"
    kg.upsert("Technique", "vst_factory_presets", prov,
              desc="playing a VST like its designers intended: tal_presets.py get '<name>' returns the params dict — inline it as source {kind:'vst3', plugin:'TAL-NoiseMaker', params:{...}}; 256 factory sounds in 8 categories (54 BASS, 77 LEAD, 26 PAD...); search library.json vst_presets by category, then tweak the named params from there")
    for g in ("synthwave", "italo_disco", "ebm", "synthpop", "trance", "house", "electro"):
        kg.link("Genre", g, "USES_TECHNIQUE", "Technique", "vst_factory_presets", weight=0.6)
    print("preset-rail technique seeded")

if __name__ == "__main__" and "--presets" in sys.argv:
    seed_preset_rail()
