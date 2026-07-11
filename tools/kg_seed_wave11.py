#!/usr/bin/env python3
"""KG curation wave 11 (2026-07-03): THE LINEAGE COMPLETIONS — the origin nodes
the tree still pointed at implicitly: chicago house & acid house (house's actual
birthplace), detroit techno (techno's), synthpop & post-punk (the 80s poles),
dub techno (Basic Channel's infinite chord), minimal, EBM, and two beloved
moderns (hardwave, balearic). Idempotent (MERGE). 100 -> 110 real genres."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

def seed():
    kg = KG()
    prov = "curated:claude/2026-07-03-w11"
    NEW_TECH = {
     "jack_groove": "chicago house: the raw 909 JACK — swung 16th hats against a pumping 4-floor, off-kilter clap placement, one vamping bass/organ riff; imperfection is the funk",
     "detroit_strings": "detroit techno: hi-tech soul — minor 9th/11th STRING-machine stabs over machine funk; melancholy chords, futurist optimism; the strings answer the bassline",
     "dub_techno_chord": "dub techno: ONE bandpassed minor chord stab fed to an endless echo (feedback 0.7+, dotted delay), detuned slightly per repeat; the track is the chord's decay riding a soft 4-floor",
     "minimal_pulse": "minimal: microscopic elements (a click, a tick, a one-note bass), ONE change per 16-32 bars; the groove emerges from what is NOT there — resist every urge to add",
     "ebm_bassline": "EBM: militant sequenced 16th square/saw bass, unwavering, mid-forward; stomping 4-floor + industrial claps; shouted-vocal space left in the mid band",
     "synthpop_hook": "synthpop: a MONOPHONIC analog lead hook carries the song (the hook IS the chorus), big gated snare, arpeggiated 8th bass; melody over texture, always",
     "post_punk_bass": "post-punk: the BASS is the lead — melodic driving 8ths high on the neck; scratchy staccato guitar ANSWERS in the gaps; drums dry and motorik",
     "hardwave_lead": "hardwave: mournful detuned supersaw lead melodies over trap-pattern drums, enormous reverb/space; emotional minor toplines at halftime feel",
     "balearic_glide": "balearic: 95-115 sunset groove — chorused clean guitars/pads, dreamy major-7 harmony, loose percussion; nothing urgent, everything warm",
    }
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, prov, desc=d)
    W = {
     "chicago_house":  dict(bpm=(118,126), key="A minor", tech=[("jack_groove",.95),("four_on_floor",.9),("offbeat_bass",.7),("vocal_chops",.5)], mix=(-11,-8,"low>lowmid>mid")),
     "acid_house":     dict(bpm=(118,128), key="A minor", tech=[("acid_squelch_lead",.95),("jack_groove",.8),("four_on_floor",.9)], mix=(-11,-8,"low>lowmid>mid")),
     "detroit_techno": dict(bpm=(120,135), key="C minor", tech=[("detroit_strings",.95),("four_on_floor",.85),("electro_boogie",.6),("m7_chords",.6)], mix=(-12,-8,"low>lowmid>mid")),
     "dub_techno":     dict(bpm=(115,125), key="D minor", tech=[("dub_techno_chord",.95),("dub_delay_ride",.8),("four_on_floor",.7),("huge_space",.8)], mix=(-14,-10,"low>lowmid>mid")),
     "minimal_techno": dict(bpm=(125,132), key="F minor", tech=[("minimal_pulse",.95),("four_on_floor",.8),("filter_transition",.5),("huge_space",.6)], mix=(-11,-8,"low>lowmid>mid")),
     "ebm":            dict(bpm=(115,130), key="C minor", tech=[("ebm_bassline",.95),("machine_percussion",.7),("four_on_floor",.8),("gain_staged_saturation",.6)], mix=(-10,-7,"lowmid>low>mid")),
     "synthpop":       dict(bpm=(110,130), key="C major", tech=[("synthpop_hook",.95),("gated_reverb_snare",.85),("arp_8th",.8),("topline_first",.7)], mix=(-11,-8,"lowmid>low>mid")),
     "post_punk":      dict(bpm=(130,165), key="E minor", tech=[("post_punk_bass",.95),("dbeat_energy",.5),("jangle_strum",.6),("huge_space",.5)], mix=(-13,-9,"lowmid>low>mid")),
     "hardwave":       dict(bpm=(140,160), key="F minor", tech=[("hardwave_lead",.95),("half_time_140",.8),("sliding_808",.6),("send_reverb",.8)], mix=(-9,-6,"low>mid>lowmid")),
     "balearic":       dict(bpm=(95,115),  key="D major", tech=[("balearic_glide",.95),("maj7_gloss",.7),("four_floor_disco",.5),("send_reverb",.6)], mix=(-14,-10,"lowmid>low>mid")),
    }
    for g, spec in W.items():
        kg.upsert("Genre", g, prov, bpm_lo=spec["bpm"][0], bpm_hi=spec["bpm"][1], common_key=spec["key"])
        for t, w in spec["tech"]:
            kg.link("Genre", g, "USES_TECHNIQUE", "Technique", t, weight=w)
        lo, hi, order = spec["mix"]
        kg.upsert("MixTarget", f"{g}_mix", prov, lufs_lo=lo, lufs_hi=hi, band_order=order, clipped_samples=0)
        kg.link("Genre", g, "TARGETS", "MixTarget", f"{g}_mix")
    # the birth certificates: house and techno get their actual parents
    for a, b in (("chicago_house", "disco"), ("acid_house", "chicago_house"),
                 ("house", "chicago_house"), ("detroit_techno", "funk"),
                 ("detroit_techno", "electro"), ("techno", "detroit_techno"),
                 ("dub_techno", "detroit_techno"), ("dub_techno", "dub"),
                 ("minimal_techno", "detroit_techno"), ("ebm", "industrial"),
                 ("synthpop", "disco"), ("post_punk", "punk"),
                 ("hardwave", "trap"), ("hardwave", "synthwave"),
                 ("balearic", "disco"), ("balearic", "ambient"),
                 ("psytrance", "acid_house")):
        kg.link("Genre", a, "DERIVED_FROM", "Genre", b, citation=prov)
    print("wave 11:", kg.q("MATCH (g:Genre) RETURN count(g)")[0][0], "genres,",
          kg.q("MATCH (t:Technique) RETURN count(t)")[0][0], "techniques,",
          kg.q("MATCH ()-[r]->() RETURN count(r)")[0][0], "edges")

if __name__ == "__main__":
    seed()


def seed_lead_voices():
    """Lead/ostinato voices (2026-07-03): flute_lead + strings_stacc — the
    cross-genre lead gap and cinematic's missing 8th-cell engine. Run AFTER
    the f0/centroid/tail battery passes."""
    kg = KG()
    prov = "curated:claude/2026-07-03-lead-voices (f0/centroid/tail battery-verified)"
    R = {
     "flute_topline": ("flute_lead", "faust flute_lead: breathy flute w/ late vibrato — jazz/bossa heads, trap-flute toplines, highlife runs; legato lines (len ~0.9 of gap), short notes read as tonguing", ["jazz", "bossanova", "trap", "highlife", "corridos_tumbados", "lofi"]),
     "string_ostinato": ("strings_stacc", "faust strings_stacc: spiccato section, bow bite + no sustain — THE ostinato engine: 8th/16th cells (same 1-2 pitches per bar) under cine_brass swells + timpani hits; also disco/funk stabs", ["orchestral_cinematic", "disco", "italo_disco", "kpop"]),
    }
    for name, (voice, desc, genres) in R.items():
        kg.upsert("SoundRecipe", name, prov, voice=voice, desc=desc)
        for g in genres:
            kg.link("Genre", g, "CHARACTERIZED_BY", "SoundRecipe", name)
    print("lead-voice recipes seeded")

if __name__ == "__main__" and "--voices" in sys.argv:
    seed_lead_voices()
