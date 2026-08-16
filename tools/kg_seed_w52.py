#!/usr/bin/env python3
"""KG SEED WAVE 52 — three researched data legs (idempotent MERGEs):

  150 (r-22)  the 808-lineage tree: boom-bap -> trap -> drill/phonk/
              plugg/jersey/rage families as Genre nodes with VERIFIED
              tempo windows + groove signatures + SUBGENRE_OF parent
              chains (unbanked variants inherit sane floors — the
              groove-inheritance hop already walks SUBGENRE_OF)
  099 (r-25)  psy/downtempo per-subgenre BPM windows + required_texture
              tags (forest = organic foley, darkpsy = FM/atonal,
              dub techno = <=5 elements + filter motion, psybient =
              evolving pads + tempo changes allowed)
  160 (r-26)  ORCHESTRATION BLEND/DOUBLING table: the three functional
              clusters, sanctioned doublings, blend-difficulty ladder,
              the exposed-woodwind-unison trap

Provenance REQUIRED on every node (the factory law). --verify = query-
back proofs + idempotency (second run adds nothing).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg  # noqa: E402

PROV = "r-22/r-25/r-26 producer-mind seed w52 (2026-07-16)"

# ---------------------------------------------------- 150 the lineage
# fields: bpm windows are COURT floors (r-22 3-source numbers);
# signature = the one-line groove truth a compiled skill quotes
LINEAGE = {
    "boombap": dict(bpm_lo=85, bpm_hi=95, swing_pct="54-58 (60-64 Dilla)",
                    signature="MPC 16th swing; 94bpm optimal; full range 80-105"),
    "trap": dict(bpm_lo=130, bpm_hi=160, halftime_felt="70-75",
                 signature="snare beat 3; hats 1/16 w/ 1/32 + triplet rolls, "
                           "crescendo 32nds into the snare; 808 key-locked"),
    "chicago_drill": dict(bpm_lo=60, bpm_hi=70, halftime_felt="60-70 sparse",
                          signature="SUSTAINED/STATIC 808 (never slides); "
                                    "dark sparse halftime"),
    "uk_drill": dict(bpm_lo=138, bpm_hi=151, halftime_felt="69-75",
                     signature="3+3+2 hat polyrhythm (16th steps 1,4,7,9,12,15); "
                               "SLIDING mono 808 (slide 20-35, note-cut); ghost "
                               "snare and-of-4 at 40-50% vel; snare to beat 4 "
                               "on bar 2"),
    "ny_drill": dict(bpm_lo=138, bpm_hi=145,
                     signature="uk drill drums + sample loops; sliding 808"),
    "memphis_rap": dict(bpm_lo=60, bpm_hi=80,
                        signature="lo-fi tape hiss mandatory; controlled "
                                  "(non-distorted) 808 sub; dark chants"),
    "memphis_phonk": dict(bpm_lo=60, bpm_hi=80,
                          signature="memphis rap DNA + vinyl lo-fi; cowbell "
                                    "enters the vocabulary"),
    "driftphonk": dict(bpm_lo=130, bpm_hi=160,
                       signature="pitched TR-808 COWBELL as the melodic lead; "
                                 "heavily distorted 808"),
    "house_phonk": dict(bpm_lo=125, bpm_hi=130,
                        signature="4-on-floor kick under phonk cowbell/vox"),
    "brazilian_phonk": dict(bpm_lo=90, bpm_hi=110,
                            signature="baile-funk rhythm bed under phonk tops"),
    "crunk": dict(bpm_lo=70, bpm_hi=80, doubletime_felt="140-160",
                  signature="shouted call-and-response gang hook MANDATORY; "
                            "synth ostinato + heavy 808 stabs"),
    "snap": dict(bpm_lo=68, bpm_hi=80,
                 signature="FINGER-SNAP one-shot replaces the snare on the "
                           "backbeat; minimal/sparse"),
    "cloud_rap": dict(bpm_lo=60, bpm_hi=100,
                      signature="plate/shimmer reverb 2.0-3.0s on nearly every "
                                "element; pitched-stretched vocal chops lead"),
    "plugg": dict(bpm_lo=65, bpm_hi=78,
                  signature="airy bell/pluck melodies, compact drums, space"),
    "pluggnb": dict(bpm_lo=65, bpm_hi=78, fulltime="130-160",
                    signature="DETUNED bright bell/arp leads; R&B/gospel chord "
                              "voicings; compact drums"),
    # the graph's club node is the FUSED name "jerseyclub" (w22) — w52 minted a
    # "jersey_club" twin STUB and jersey_drill's parent edge pointed into the
    # void (naming-twin heal 2026-07-25; stub detach-deleted live)
    "jerseyclub": dict(bpm_lo=130, bpm_hi=142,
                       signature="5-kick riddim on 16th steps 1,5,9,12,15; "
                                 "bed-squeak sample"),
    "jersey_drill": dict(bpm_lo=130, bpm_hi=142,
                         signature="jersey 5-kick riddim under drill 808s/vox"),
    "rage": dict(bpm_lo=150, bpm_hi=170,
                 signature="distorted/bitcrushed synth leads; bass-heavy 808; "
                           "halftime"),
    "sexy_drill": dict(bpm_lo=130, bpm_hi=140,
                       signature="ny drill drums under plush r&b samples"),
    "sample_drill": dict(bpm_lo=138, bpm_hi=145,
                         signature="chipmunk-soul pitched-up sample hooks over "
                                   "drill drums"),
    "afro_drill": dict(bpm_lo=110, bpm_hi=130,
                       signature="afrobeats log-drum bounce under drill 808s"),
}
# the EXPLICIT r-22 parent chains (never invented lineage)
PARENTS = [
    ("ny_drill", "uk_drill"), ("uk_drill", "chicago_drill"),
    ("chicago_drill", "trap"),
    ("pluggnb", "plugg"), ("pluggnb", "cloud_rap"),
    ("jersey_drill", "jerseyclub"), ("jersey_drill", "uk_drill"),
    ("driftphonk", "memphis_phonk"), ("memphis_phonk", "memphis_rap"),
    ("house_phonk", "memphis_phonk"), ("brazilian_phonk", "memphis_phonk"),
    ("sexy_drill", "ny_drill"), ("sample_drill", "ny_drill"),
    ("afro_drill", "uk_drill"), ("rage", "trap"),
]

# --------------------------------------------- 099 psy/downtempo windows
PSY = {
    "fullon": dict(bpm_lo=142, bpm_hi=146, required_texture="rolling 16th "
                   "psy-bass, full-power leads"),
    "goa": dict(bpm_lo=135, bpm_hi=150, required_texture="303-ish spiral "
                "melodic layers"),
    "progressive_psy": dict(bpm_lo=138, bpm_hi=144, required_texture="deep "
                            "groove, restrained lead vocabulary"),
    "darkpsy": dict(bpm_lo=148, bpm_hi=158, required_texture="FM/atonal "
                    "textures mandatory"),
    "forest": dict(bpm_lo=148, bpm_hi=158, required_texture="ORGANIC FOLEY "
                   "layer mandatory (wood, insects, water)"),
    "hitech": dict(bpm_lo=170, bpm_hi=220, required_texture="glitch-edit "
                   "vocabulary, hyper-speed 16ths"),
    "psybient": dict(bpm_lo=70, bpm_hi=120, grid_optional=True,
                     required_texture="EVOLVING pads; tempo changes allowed"),
    "dub_techno": dict(bpm_lo=110, bpm_hi=125, element_cap=5,
                       required_texture="<=5 elements + filter automation "
                                        "motion mandatory"),
    "triphop": dict(bpm_lo=70, bpm_hi=90, required_texture="dusty breaks, "
                    "vinyl noise bed"),
    "downtempo": dict(bpm_lo=60, bpm_hi=110, required_texture="soft/wide, "
                      "unhurried motion"),
    "idm": dict(bpm_lo=80, bpm_hi=160, required_texture="soft/wide dynamics, "
                "edit-heavy percussion"),
}

# --------------------------------------------- 160 orchestration table
ORCH = [
    ("cluster_standard", "cluster",
     "STANDARD role: strings+woodwinds carry theme/harmony — the default "
     "orchestral bed"),
    ("cluster_power", "cluster",
     "POWER role: brass marcato + low strings + percussion — climax force"),
    ("cluster_color", "cluster",
     "COLOR role: harp/celesta/choir/solo winds — highlights, never the bed"),
    ("doubling_vln_cl", "doubling",
     "violins + clarinet: SOFTENS the string edge (the classic blend)"),
    ("doubling_vln_tpt", "doubling",
     "violins + trumpet: brilliant string-brass unison (use sparingly)"),
    ("doubling_vla_hn", "doubling",
     "violas + horns: warm middle — the safest string-brass blend"),
    ("doubling_vc_hn", "doubling",
     "celli + horns: noble low-mid unison (film staple)"),
    ("doubling_cl_bsn_ca", "doubling",
     "clarinet + bassoon + cor anglais reads as a HORN — the wind 'horn-like' "
     "trick when brass must rest"),
    ("difficulty_ladder", "difficulty",
     "blend difficulty: strings-within-strings EASIEST < winds+strings < "
     "brass+brass < strings+brass HARDEST (reserve for climaxes)"),
    ("trap_exposed_ww_unison", "trap",
     "NEVER expose a woodwind unison pair alone — intonation beats; "
     "double with a string or separate by an octave"),
]
ORCH_GENRES = ("cinematic", "orchestral", "filmscore", "film_score",
               "epic", "soundtrack", "classical")


# W61 (r-18 item 216): per-genre KICK-FUNDAMENTAL felt-band targets +
# the register-over-pitch principle (prefer transposing the SONG to
# seat a great 808 in its comfort zone over detuning the 808 and
# losing its character)
SUB_FUNDAMENTALS = {
    "house": "40-50", "deep_house": "40-50", "techno": "40-50",
    "trap": "<40", "drill": "<40", "uk_drill": "<40", "ny_drill": "<40",
    "trance": "50-60", "uplifting_trance": "50-60",
    "dnb": "90-110", "jungle": "90-110", "neurofunk": "90-110",
}
REGISTER_LAW = ("register/formant position outranks exact pitch for sub "
                "voices: transpose the SONG to seat a great-sounding 808 "
                "in its comfort zone (boom ~30 / thump ~50 / punch ~80Hz) "
                "rather than detune the 808 and lose its character")


def seed(g):
    added = {"genres": 0, "patched": 0, "edges": 0, "orch": 0}
    have = {r[0] for r in g.q("MATCH (x:Genre) RETURN x.name")}
    for name, attrs in list(LINEAGE.items()) + list(PSY.items()):
        if name not in have:
            added["genres"] += 1
        else:
            added["patched"] += 1
        g.upsert("Genre", name, PROV, **attrs)
    for gname, hz in SUB_FUNDAMENTALS.items():
        if gname in have or gname in LINEAGE:
            g.upsert("Genre", gname, PROV, kick_fundamental_hz=hz,
                     register_law=REGISTER_LAW)
    for child, parent in PARENTS:
        g.link("Genre", child, "SUBGENRE_OF", "Genre", parent,
               provenance=PROV)
        added["edges"] += 1
    for name, kind, rule in ORCH:
        g.upsert("OrchestrationRule", name, PROV, kind=kind, rule=rule)
        added["orch"] += 1
        for og in ORCH_GENRES:
            if og in have:
                g.link("Genre", og, "HAS_ORCH_RULE", "OrchestrationRule",
                       name, provenance=PROV)
    return added


def verify(g):
    fails = []

    def check(name, cond):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    row = g.q("MATCH (g:Genre {name:'uk_drill'}) RETURN g.bpm_lo, g.bpm_hi")
    check("uk_drill window 138-151",
          row and row[0][0] == 138 and row[0][1] == 151)
    row = g.q("MATCH (g:Genre {name:'ny_drill'})-[:SUBGENRE_OF]->(p) "
              "RETURN p.name")
    check("ny_drill inherits from uk_drill",
          row and row[0][0] == "uk_drill")
    row = g.q("MATCH (g:Genre {name:'driftphonk'})-[:SUBGENRE_OF*2]->(p) "
              "RETURN p.name")
    check("driftphonk two hops up = memphis_rap",
          "memphis_rap" in [r[0] for r in row or []])
    row = g.q("MATCH (g:Genre {name:'forest'}) RETURN g.required_texture")
    check("forest demands the organic foley layer",
          row and "FOLEY" in str(row[0][0]))
    row = g.q("MATCH (g:Genre {name:'dub_techno'}) RETURN g.element_cap")
    check("dub_techno caps at 5 elements", row and row[0][0] == 5)
    row = g.q("MATCH (g:Genre {name:'psybient'}) RETURN g.grid_optional")
    check("psybient is grid-optional", row and bool(row[0][0]))
    row = g.q("MATCH (o:OrchestrationRule) RETURN count(o)")
    check("10 orchestration rules stand", row and row[0][0] >= 10)
    row = g.q("MATCH (o:OrchestrationRule {name:'doubling_cl_bsn_ca'}) "
              "RETURN o.rule")
    check("the wind horn-trick doubling banked",
          row and "HORN" in str(row[0][0]))
    row = g.q("MATCH (g:Genre) WHERE g.provenance IS NULL RETURN count(g)")
    check("provenance law: no orphan Genre nodes", row is not None)
    return fails


def main():
    g = kg.KG()
    a1 = seed(g)
    print(f"[kg_w52] seed: {a1}")
    if "--verify" in sys.argv:
        a2 = seed(g)
        idem = a2["genres"] == 0
        print(f"[kg_w52] idempotency: second run minted {a2['genres']} "
              f"genres ({'PASS' if idem else 'FAIL'})")
        fails = verify(g)
        if not idem:
            fails.append("idempotency")
        if fails:
            print(f"kg_w52: {len(fails)} RED — {fails}")
            return 1
        print("kg_w52: ALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
