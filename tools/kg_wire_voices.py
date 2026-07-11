#!/usr/bin/env python3
"""Wire the 11 NEW dedicated Faust voices (built 2026-07-06, session genre-forge) into the
bands+jazz genre KG: point each genre's SoundRecipe.voice + PatternArchetype lead.voice at
the REAL instrument voices (was guitar_grit/rhodes/sax_section/etc. stand-ins). Idempotent;
run AFTER tools/kg_seed_bands_jazz.py. Then recompile the affected skills.
New voices: fuzz_guitar, highgain_guitar, upright_bass, clean_chime_guitar, sax_reed,
jazz_piano, ride_cymbal, brush_snare, blast_kick, tanpura_drone, hammond_organ."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG
PROV = "curated:claude/2026-07-06 (dedicated Faust voices wired; genre-forge; instruments/*.dsp)"

# SoundRecipe name -> (new primary voice, refreshed desc naming the real voices)
RECIPES = {
 "grunge_fuzz": ("fuzz_guitar", "faust fuzz_guitar (Big-Muff 4-stage cascade): HEAVY drive for the chorus wall, near-bypass for the clean verse -- the verse->chorus GAIN AUTOMATION (curve <0, early-jump) IS the song; scoop the mids; preserve dynamics at master (DR11-12 feel, NOT a -8 brickwall)."),
 "desert_fuzz": ("fuzz_guitar", "faust fuzz_guitar downtuned + thick: high drive, sub-octave girth, low-mid wall; bass_warm doubles near-lead; wah = an fx_djfilter/fx_filter sweep automated on leads; analog-warm, not brickwalled."),
 "clean_chime": ("clean_chime_guitar", "faust clean_chime_guitar: bright ringing dual-Karplus with shimmer chorus + LONG sustain (open strings ring/overlap); two tracks panned L/R for counterpoint; NO distortion; preserve transient crest at master (do not limit hard)."),
 "twinkle_guitar": ("clean_chime_guitar", "faust clean_chime_guitar: fingerpicked OPEN-tuning arpeggios, high sustain so notes ring/overlap, gentle chorus shimmer; medium plate + triplet delay; hard-panned pair; intimate high-crest master."),
 "frost_tremolo": ("highgain_guitar", "faust highgain_guitar TREBLY (mids KEPT, not scooped -> mids slightly >0), mute=0 (open ringing wall), tremolo-picked, thin/cold; double-tracked; aesthetic is fidelity not loudness -- keep it raw + treble-forward."),
 "buzzsaw": ("highgain_guitar", "faust highgain_guitar high drive: mids>0 = Swedish HM-2 buzzsaw honk ~1k, mids<0 = Florida scoop; palm-mute chugs (mute~0.6) traded with tremolo; hard L/R double; loud tight low; blast_kick on the double-kick."),
 "iommi_wall": ("fuzz_guitar", "faust fuzz_guitar downtuned + WARM (heavy sustain, sub-octave): long ringing power chords + a low held drone track for feedback; huge low + PRESENT mids (Sabbath tone isn't scooped); large room reverb; let the slow hits BREATHE."),
 "core_chug": ("highgain_guitar", "faust highgain_guitar drop-tuned: mute~0.6 for the chug, mute=0 for leads; hard L/R double; the breakdown is an ARRANGEMENT half-time (thin density + snare-to-beat-3); blast_kick under gallops; fx_djfilter riser + fx_trim lift into the drop."),
 "tectonic_layers": ("highgain_guitar", "faust highgain_guitar in 2-3 layers (octaves/detunes) feeding a SHARED reverb bus for the wall; clean valleys = keys_dark/pad_motion + big reverb; THE CRESCENDO IS AUTOMATION (fx_trim + drive + reverb-send + layer mute-ins, late-bloom curve >0); do NOT brickwall."),
 "bop_combo": ("jazz_piano", "faust jazz_piano (felt additive grand) comping, sax_reed the horn front line, upright_bass walking, ride_cymbal + brush_snare kit (ride-forward, hats on 2&4); PAN hard L/C/R (Blue Note, not fx_widen); short room reverb + tape; do NOT compress (keep the swing snap)."),
 "blue_note_combo": ("hammond_organ", "faust hammond_organ (drawbars + Leslie + key-click) or jazz_piano gospel block comping, sax_reed harmonized front line, upright_bass walking, ride_cymbal + brush_snare with a HARD 2&4 backbeat; vibraphone as a Blue Note color; short plate + tape warmth; stay dynamic."),
 "modal_combo": ("jazz_piano", "faust jazz_piano QUARTAL comping over an upright_bass modal PEDAL, sax_reed lead, ride_cymbal + brush_snare kit; ONE shared room-reverb send bus; long AABA vamp; build intensity over the solo via gain + reverb-send AUTOMATION (late-bloom); steady tempoMap."),
 "devotional_combo": ("sax_reed", "faust sax_reed pentatonic WAILS (growl up for the ecstatic peak) over a tanpura_drone + upright_bass ostinato, harp arpeggios, jazz_piano McCoy quartal+pedal, hand percussion; DEEP long reverb send; a multi-minute crescendo AUTOMATION; leave free sections un-quantized; keep highly dynamic."),
}
# PatternArchetype name -> new lead voice (rides generate_loop's grid lead)
LEADS = {
 "quiet_loud": "fuzz_guitar", "desert_groove": "fuzz_guitar", "odd_meter_cell": "clean_chime_guitar",
 "twinkle_cell": "clean_chime_guitar", "frostbite_blast": "highgain_guitar", "bomb_blast_chug": "highgain_guitar",
 "iommi_crawl": "fuzz_guitar", "breakdown": "highgain_guitar", "crescendo": "highgain_guitar",
 "swing_head": "sax_reed", "backbeat_shuffle": "sax_reed", "so_what_vamp": "jazz_piano", "drone_build": "sax_reed",
}


def wire():
    kg = KG()
    for name, (voice, desc) in RECIPES.items():
        kg.upsert("SoundRecipe", name, PROV, voice=voice, desc=desc)
    for pname, lead in LEADS.items():
        r = kg.q(f"MATCH (p:PatternArchetype {{name:'{pname}'}}) RETURN p.grid, p.provenance")
        if not r or not r[0][0]:
            print("  MISS pattern", pname); continue
        grid = json.loads(r[0][0])
        if isinstance(grid.get("lead"), dict):
            grid["lead"]["voice"] = lead
        kg.upsert("PatternArchetype", pname, r[0][1] or PROV, grid=json.dumps(grid))  # keep original prov
    print(f"wired {len(RECIPES)} SoundRecipes + {len(LEADS)} pattern leads to dedicated voices.")


if __name__ == "__main__":
    wire()
