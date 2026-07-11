#!/usr/bin/env python3
"""KG curation wave 5 (2026-07-11): CHEZY'S GENRES — psybient + psychill.

His live session asked for "psybient psychill ambient" and neither genre
existed in the graph (his MAKEs fell to neighbor routing); his own imports
(Entheogenic) ARE the reference class. INLINE model-knowledge authorship
(no-subagents law). Idempotent (MERGE).
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("curated:claude/2026-07-11 (coverage wave 5: the user's own live genres, "
        "session fable-gen; reference class = his Entheogenic imports)")
CITE = "curated:claude/2026-07-11-genrexp5"

NEW_TECH = {
 "dub_space_bloom": "psybient space law: long dark delays + a huge damped hall bloom "
                    "behind everything — the SPACE is an instrument; sends run hot on "
                    "pads/leads, the sub stays bone dry",
 "acid_whisper": "a 303 line UNDER the mix (gain low, cutoff modest) — the acid is felt "
                 "as movement, never a scream; whispered squelch on offbeats",
 "world_perc_conversation": "hand percussion (dhol/duduk-adjacent voices) converses in "
                            "the midground — sparse call-answer hits, never a loop wall",
 "heartbeat_half_kick": "the psybient pulse: a soft round kick on 1 and the and-of-2 "
                        "(heartbeat), NOT a club four-floor — the sub carries the drive",
}

G = [
 dict(name="psybient", bpm=(90, 105), key="E Phrygian", form="club",
   voicing={"style": "smooth", "lo": 45, "hi": 78}, parents=[],
   derived=["psytrance", "ambient", "dub"],
   tech=["dub_space_bloom", "acid_whisper", "world_perc_conversation",
         "heartbeat_half_kick"],
   pattern=("psybient_journey",
     "Psybient (~98 BPM): heartbeat kick (1 + and-of-2), deep rolling sub in "
     "Phrygian, lush motion pads breathing whole bars, a whispered 303 on "
     "offbeats, sparse world percs conversing; the space blooms dark and "
     "long — Shpongle/Entheogenic territory.",
     {"bars": 2, "swing": 0.52, "bass_style": "wub", "bass_gain_db": -8.0,
      "kick": [0, 6, 16, 22], "kick_gain_db": -4.0,
      "hat": [4, 12, 20, 28], "hat_gain_db": -13.0,
      "ghost": [10, 26], "ghost_voice": "dhol", "ghost_gain_db": -10.0,
      "ghost_pitch": 55,
      "vel": {"hat": {"4": 0.4, "12": 0.35, "20": 0.4, "28": 0.35}},
      "chords": [[0, 1], [1, 1], [2, 4], [3, 3]],
      "color_gain_db": -10.0,
      "lead": {"voice": "acid303", "octave": 3, "bars": 2,
               "steps": [[2, 1, 1], [6, 3, 1], [10, 1, 2], [18, 4, 1],
                         [22, 3, 1], [26, 1, 2]]},
      "lead_gain_db": -12.0}),
   mix={"lufs_lo": -14, "lufs_hi": -11, "band_order": "low>lowmid>mid",
        "clipped": 0},
   sounds=[("psybient_space", "pad_motion",
            "lush motion pads (detune pair) = the bed; acid303 whispered LOW "
            "(gain -12, its squelch felt not heard); sub = rolling wub reese; "
            "dhol speaks midground at 196Hz; sends hot to a dark long hall; "
            "kick soft and round — the sub drives, not the kick")]),

 dict(name="psychill", bpm=(80, 95), key="A minor", form="club",
   voicing={"style": "smooth", "lo": 48, "hi": 80}, parents=[],
   derived=["psybient", "downtempo"],
   tech=["dub_space_bloom", "world_perc_conversation"],
   pattern=("psychill_drift",
     "Psychill (~88 BPM): softer than psybient — halftime kick, warm dark "
     "keys answering the pads, sub in long notes, percs barely there; the "
     "drift between ambient and groove.",
     {"bars": 2, "swing": 0.5, "bass_style": "sustained",
      "bass_voice": "sub_clean", "bass_gain_db": -6.0,
      "kick": [0, 16, 22], "kick_gain_db": -5.0,
      "hat": [8, 24], "hat_gain_db": -14.0,
      "chords": [[0, 1], [1, 6], [2, 4], [3, 5]],
      "color_voice": "keys_dark", "color_gain_db": -13.0,
      "lead": {"voice": "rhodes", "octave": 4, "bars": 2,
               "steps": [[0, 1, 3], [6, 3, 2], [12, 5, 3], [18, 4, 2],
                         [24, 3, 3], [30, 1, 2]]},
      "lead_gain_db": -10.0}),
   mix={"lufs_lo": -15, "lufs_hi": -12, "band_order": "low>lowmid>mid",
        "clipped": 0},
   sounds=[("psychill_warmth", "keys_dark",
            "dark keys bed + a rhodes line drifting over sustained sub; "
            "halftime pulse; everything swims in the hall except the sub")]),
]


def seed():
    kg = KG()
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, PROV, desc=d)
    for g in G:
        kg.upsert("Genre", g["name"], PROV, bpm_lo=g["bpm"][0], bpm_hi=g["bpm"][1],
                  common_key=g["key"], voicing=json.dumps(g["voicing"]),
                  form_family=g["form"])
    for g in G:
        name = g["name"]
        for i, t in enumerate(g["tech"]):
            kg.link("Genre", name, "USES_TECHNIQUE", "Technique", t,
                    weight=round(1.0 - i * 0.08, 2))
        pname, pdesc, pgrid = g["pattern"]
        kg.upsert("PatternArchetype", pname, PROV, desc=pdesc, grid=json.dumps(pgrid))
        kg.link("Genre", name, "CHARACTERIZED_BY", "PatternArchetype", pname)
        mt = g["mix"]; mt_name = f"{name}_mix"
        kg.upsert("MixTarget", mt_name, PROV, lufs_lo=mt["lufs_lo"],
                  lufs_hi=mt["lufs_hi"], band_order=mt["band_order"],
                  clipped_samples=mt["clipped"])
        kg.link("Genre", name, "TARGETS", "MixTarget", mt_name)
        for sname, voice, sdesc in g["sounds"]:
            kg.upsert("SoundRecipe", sname, PROV, voice=voice, desc=sdesc)
            kg.link("Genre", name, "CHARACTERIZED_BY", "SoundRecipe", sname)
        for d in g["derived"]:
            kg.link("Genre", name, "DERIVED_FROM", "Genre", d, citation=CITE)
    n_gen = kg.q("MATCH (g:Genre) RETURN count(g)")[0][0]
    print(f"seeded {len(G)} genres (+{len(NEW_TECH)} techniques); graph: {n_gen} genres")
    for g in G:
        v = kg.genre_view(g["name"])
        print(f"  {g['name']:10s} tech={len(v['techniques'])} mix={bool(v['mixtargets'])}")


if __name__ == "__main__":
    seed()
