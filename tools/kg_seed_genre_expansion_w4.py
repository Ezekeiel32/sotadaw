#!/usr/bin/env python3
"""KG curation wave 4 (2026-07-06): THE BACKLOG CLOSER — slice-B tail + emerging/jazz-soul
tail. Session `genre-scout`. INLINE model-knowledge authorship (no-subagents law);
evidence + flags in docs/research_genre_expansion_w4.md. Empties the campaign backlog.
Idempotent (MERGE). Retro-edge: hardwave DERIVED_FROM wave.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("curated:claude/2026-07-06 (coverage-expansion wave 4 backlog-closer, session genre-scout; "
        "INLINE model-knowledge authorship, flags in docs/research_genre_expansion_w4.md)")
CITE = "curated:claude/2026-07-06-genrexp4"

NEW_TECH = {
 "istikhbar_rubato": "a free-time modal instrumental prelude (istikhbar/taksim/taximi family) BEFORE the groove enters — open with rubato drone+lead",
 "mandole_tremolo": "the chaabi mandole: double-course tremolo lead in Andalusi-derived modes, answered by banjo and violin unison",
 "percussion_only_ensemble": "fuji law: NO harmony instruments — layered talking drums, shekere and bells ARE the arrangement; melody lives in the voice and the drum bends",
 "layered_talking_drums": "multiple talking-drum voices at different registers converse (lead drum speaks, others answer) — write 2-3 bending drum tracks in dialogue",
 "danse_sequence": "the ndombolo drop: the song strips to kick + percussion + shouts while the seben guitar cycles — a named dance section, not a breakdown",
 "ravanne_roll": "the sega ravanne: a frame-drum roll figure leaning into beat 1 of each 6/8 group, maravanne shaker washing, triangle ticking the pulse",
 "rouleur_trance_pulse": "the maloya rouleur: a deep drum pulse on the 6/8 groups with kayamb shaker wash — hypnotic minor call-response chant over cycles (island trance)",
 "dabke_gallop": "the dabke derbouka gallop: DUM on 1 then a dum-tek gallop through the bar, tabl reinforcing, line-dance stomps on downbeats",
 "zurna_hijaz_lead": "a piercing double-reed (zurna/mijwiz) lead wailing Hijaz/Bayati lines with trills and long holds — the outdoor-celebration voice",
 "sawt_khaleeji_limp": "the khaleeji 6/8-over-2 sawt lilt: layered hand percussion (tabla + duff frame drums) with a distinctive limping accent — the Gulf pocket",
 "massed_unison_strings": "a large string section playing the vocal melody in UNISON (no harmony) with heavy melisma — the arabesk/filmi orchestral cry",
 "saz_baglama_ornament": "bağlama saz picks ornamented makam lines (Kurdi/Hicaz), answering the voice — Anatolian steel-string filigree",
 "electro_tom_percussion": "TR-808 electro-funk percussion: syncopated toms, claves, cowbell and rimshots dancing AROUND the backbeat — the freestyle/electro engine",
 "minor_stab_arp_hook": "minor synth-stab hooks + arpeggio runs as the instrumental identity between diva vocal lines (freestyle grammar)",
 "octave_fifth_bass_drive": "eurobeat engine: synth bass hammering octave/fifth 16ths nonstop under a four-floor kick — faster and busier than Hi-NRG's octave 8ths",
 "key_lift_chorus": "the eurobeat chorus LIFTS — modulate up (often +1 semitone or relative-major jump) at the hook for the para-para surge",
 "wave_hybrid_bass": "the wave signature: a hybrid reese/808 bass that SLIDES between melody notes — the bass IS the lead, dark and vocal-like, over lush pads",
 "ethereal_pad_wash": "huge detuned atmospheric pads washing behind everything — melancholy club euphoria (wave/hardwave family)",
 "stutter_chop_lead": "glitchcore law: the pitched vocal chop is STUTTERED into the lead instrument — constant micro-edit retriggers as melody, not occasional glitches",
 "sensory_overload_stack": "dense bright synth stacks + breakneck switch-ups every 2-4 bars — maximal density as the aesthetic (glitchcore/dariacore kinship)",
}

G = [
 dict(name="chaabi", bpm=(90,120), key="D Phrygian (Andalusi)", form="song",
   voicing={"style":"algiers_mandole","lo":38,"hi":84}, parents=[], derived=[],
   tech=["mandole_tremolo","istikhbar_rubato","derbouka_dum_tek","melisma_maqam_vocal"],
   pattern=("chaabi_groove","Chaâbi (~104 BPM): free istikhbar intro, then the groove — derbouka dum on 1 + and-of-2, bendir under; mandole tremolo leads Andalusi modes answered by banjo/violin unison; storytelling vocal with melisma.",
     {"bars":1,"swing":0.54,"bass_style":"sustained","kick":[0,6],"snare":[4,10,12],"hat":[2,6,10,14],
      "vel":{"snare":{"4":0.7,"10":0.5,"12":0.7}},"chords":[[0,1],[2,5]],
      "lead":{"voice":"pluck2","octave":4,"steps":[[0,1,1],[1,2,1],[2,3,1],[4,2,1],[6,1,1],[8,3,1],[10,2,1],[12,1,3]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-11,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":9.0},
   sounds=[("chaabi_band","pluck2","mandole = pluck2 double-course tremolo; banjo = pluck bright; violin unison = strings_stacc; derbouka = dhol tight + tick lane; open FREE (istikhbar) before the groove")]),

 dict(name="fuji", bpm=(100,135), key="C major (vocal-modal)", form="through_composed",
   voicing={"style":"drum_orchestra","lo":36,"hi":80}, parents=[], derived=[],
   tech=["percussion_only_ensemble","layered_talking_drums","praise_call_response","shekere_eighths"],
   pattern=("fuji_orchestra","Fuji (~116 BPM, 12/8 undercurrent — swing .58): NO harmony instruments — layered talking drums converse (lead drum speaks slots 0/3/6/11, answers at 8/14), shekere rides 8ths, agogo bell ticks; Islamic-tinged praise melisma leads, chorus answers; the drums ARE the arrangement.",
     {"bars":1,"swing":0.58,"bass_style":"sub","kick":[0,6,8],"snare":[3,6,11,14],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"3":0.6,"6":0.75,"11":0.6,"14":0.7},"hat":{"0":0.5,"2":0.4,"4":0.5,"6":0.4,"8":0.5,"10":0.4,"12":0.5,"14":0.4}},
      "chords":[[0,1]],"lead":{"voice":"formant_vox","octave":4,"steps":[[0,1,2],[3,2,1],[6,1,1],[8,3,2],[11,2,1],[14,1,2]]}}),
   mix={"lufs_lo":-12,"lufs_hi":-9,"band_order":"lowmid>low>mid","clipped":0},
   sounds=[("fuji_drums","formant_vox","2-3 dhol tracks at different pitches IN DIALOGUE (ride the bend zone — they speak); log_drum accents; shekere = hat 8ths; agogo = hat_metal; lead = formant_vox melisma + chorus answers; NO chords, no bass guitar — percussion carries everything")]),

 dict(name="ndombolo", bpm=(96,120), key="G major", form="club",
   voicing={"style":"kinshasa_dance","lo":38,"hi":86}, parents=[], derived=["soukous"],
   tech=["danse_sequence","interlocking_guitars","atalaku_animation","cavacha_churn"],
   pattern=("ndombolo_danse","Ndombolo (~108 BPM): heavier kick than soukous (1, 2&, 3), cavacha-derived snare churn; seben guitars cycle bright interlocks; THE DANSE SEQUENCE — the song strips to kick + perc + atalaku shouts while one guitar cycles, then the band slams back.",
     {"bars":1,"swing":0.53,"bass_style":"roots","kick":[0,6,8],"snare":[4,12],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"4":0.85,"12":0.85},"hat":{"1":0.35,"3":0.35}},"chords":[[0,1],[1,4],[2,5],[3,1]],
      "lead":{"voice":"pluck","octave":5,"steps":[[0,1,1],[1,3,1],[2,5,1],[4,3,1],[6,5,1],[8,1,1],[10,3,1],[12,5,1],[14,3,1]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("ndombolo_band","pluck","seben guitars = pluck + pluck2 interlock (soukous inheritance, graph edge); kick_punch heavier than soukous; shouts = formant_vox stabs; the danse sequence = arrangement mute-to-percussion law")]),

 dict(name="sega", bpm=(105,140), key="F major", form="song",
   voicing={"style":"ravanne_sway","lo":40,"hi":84}, parents=[], derived=[],
   tech=["ravanne_roll","sodade_ballad_lilt","boliyan_call_response"],
   pattern=("sega_sway","Sega (~120 BPM, 6/8 — swing .66): the ravanne frame-drum roll leans into each group head, maravanne shaker washes, triangle ticks; major-leaning creole melody sways call-response; no stomp — a sway. [BPM verified inline: sega mauricien 105-140, Chosic tempo data.]",
     {"bars":1,"swing":0.66,"bass_style":"roots","kick":[0,8],"snare":[6,14],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"6":0.5,"14":0.5},"hat":{"0":0.55,"2":0.35,"4":0.45,"6":0.35,"8":0.55,"10":0.35,"12":0.45,"14":0.35}},
      "chords":[[0,1],[2,5]],"lead":{"voice":"pluck","octave":5,"steps":[[0,1,2],[3,3,1],[6,5,1],[8,4,2],[12,3,1],[14,1,1]]}}),
   mix={"lufs_lo":-13,"lufs_hi":-10,"band_order":"lowmid>mid>low","clipped":0},
   sounds=[("sega_kit","pluck","ravanne = dhol low with a roll lean (write grace notes into velocities); triangle = hat_metal tick; maravanne = hat wash; bright pluck melodies; sunny island sway, dynamic")]),

 dict(name="maloya", bpm=(100,135), key="D minor", form="through_composed",
   voicing={"style":"island_trance","lo":36,"hi":82}, parents=[], derived=[],
   tech=["rouleur_trance_pulse","praise_call_response","hypnotic_repetition","percussion_only_ensemble"],
   pattern=("maloya_trance","Maloya (~118 BPM, 6/8 trance — swing .66): the rouleur bass drum pulses the group heads, kayamb flat-shaker washes every pulse, pikér ticks; minor call-response chant cycles hypnotically; percussion + voices only (the banned island blues) — build by adding voices, never chords.",
     {"bars":1,"swing":0.66,"bass_style":"sub","kick":[0,6,8,14],"snare":[3,11],"hat":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
      "vel":{"kick":{"0":1.0,"6":0.7,"8":0.9,"14":0.7},"snare":{"3":0.5,"11":0.5},"hat":{"1":0.3,"3":0.3,"5":0.3,"7":0.3,"9":0.3,"11":0.3,"13":0.3,"15":0.3}},
      "chords":[[0,1]],"lead":{"voice":"formant_vox","octave":4,"steps":[[0,1,2],[3,2,1],[6,3,1],[8,1,2],[11,2,1],[14,1,1]]}}),
   mix={"lufs_lo":-13,"lufs_hi":-10,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("maloya_circle","formant_vox","rouleur = dhol DEEP pulse; kayamb = hat 16th wash (loose vel); chant lead = formant_vox + chorus answers; darker minor cousin of sega; hypnotic — let it cycle, add voices as the build")]),

 dict(name="dabke", bpm=(110,140), key="D Phrygian (Bayati/Hijaz)", form="song",
   voicing={"style":"levant_line_dance","lo":38,"hi":86}, parents=[], derived=[],
   tech=["dabke_gallop","zurna_hijaz_lead","melisma_maqam_vocal","accelerando_drive"],
   pattern=("dabke_line","Dabke (~124 BPM): the derbouka gallop — DUM on 1, dum-tek galloping through (slots 0,3,4,7,8,11,12), tabl deep on 1&3, stomps on downbeats; the ZURNA wails Hijaz lines with trills over the line-dance drive; accelerate toward the end (tempoMap).",
     {"bars":1,"swing":0.52,"bass_style":"roots","kick":[0,8],"snare":[3,4,7,11,12],"hat":[2,6,10,14],
      "vel":{"kick":{"0":1.0,"8":0.9},"snare":{"3":0.5,"4":0.8,"7":0.5,"11":0.5,"12":0.8}},"chords":[[0,1]],
      "lead":{"voice":"zurna","octave":5,"steps":[[0,1,2],[2,2,1],[4,3,1],[6,2,1],[8,1,1],[10,3,1],[12,2,1],[14,1,1]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":10.0},
   sounds=[("dabke_party","zurna","zurna lead (EXISTS — trills + long holds in Hijaz); derbouka = dhol tight + tick gallop; tabl = kick_punch deep; stomps = layered low hits on downbeats; Omar Souleyman electrified variant = add supersaw drone stabs")]),

 dict(name="khaleeji", bpm=(95,125), key="C Bayati (maqam)", form="song",
   voicing={"style":"gulf_limp","lo":38,"hi":84}, parents=[], derived=[],
   tech=["sawt_khaleeji_limp","massed_unison_strings","melisma_maqam_vocal","istikhbar_rubato"],
   pattern=("sawt_limp","Khaleeji (~118 BPM): the sawt 6/8-over-2 LIMP — layered hand percussion (tabla + duff frames) accenting the lopsided pocket (kick 1 & 4th-triplet, claps answer); oud + massed strings state the maqam melody in unison; ornamented vocal above. [BPM verified inline: typ ~120, 6/12-beat iqa'at confirmed.]",
     {"bars":1,"swing":0.6,"bass_style":"sustained","kick":[0,6,10],"snare":[4,8,12],"hat":[2,6,10,14],
      "vel":{"snare":{"4":0.6,"8":0.75,"12":0.6}},"chords":[[0,1],[2,4]],
      "lead":{"voice":"oud","octave":4,"steps":[[0,1,1],[2,2,1],[4,3,1],[6,2,1],[8,1,2],[12,3,1],[14,2,1]]}}),
   mix={"lufs_lo":-12,"lufs_hi":-9,"band_order":"lowmid>mid>low","clipped":0},
   sounds=[("gulf_ensemble","oud","oud = faust `oud` (warm Karplus body, fretless — slide with neighbor bends; knobs warmth/ring/pick); massed strings = strings_stacc unison doubling the melody; tabla+duff = dhol + frame ticks layered (the limp lives in the velocities); ornament the lead heavily")]),

 dict(name="arabesk", bpm=(70,110), key="A Kurdi (Phrygian)", form="song",
   voicing={"style":"anatolian_strings","lo":36,"hi":86}, parents=[], derived=[],
   tech=["massed_unison_strings","saz_baglama_ornament","istikhbar_rubato","saudade_rubato"],
   pattern=("arabesk_ballad","Arabesk (~88 BPM, düyek feel): darbuka lays dum-tek under massed strings playing the Kurdi/Hicaz melody in UNISON melisma; bağlama saz answers with ornamented filigree; sorrowful vocal pulls the tempo (rubato); free taksim intro.",
     {"bars":1,"swing":0.54,"bass_style":"sustained","kick":[0,6,8],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"snare":{"4":0.6,"12":0.6}},"chords":[[0,1],[2,5]],
      "lead":{"voice":"strings_stacc","octave":4,"steps":[[0,1,2],[2,2,1],[4,3,2],[8,2,2],[12,1,3]]}}),
   mix={"lufs_lo":-13,"lufs_hi":-10,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":9.0},
   sounds=[("arabesk_orchestra","strings_stacc","massed strings = strings_stacc + strings_disco unison (NO harmony — one line, many voices); saz = pluck2 ornamented answers; darbuka = dhol + ticks; sorrow first: rubato intros, heavy melisma (neighbor-bend the lead)")]),

 dict(name="freestyle", bpm=(110,122), key="A minor", form="club",
   voicing={"style":"electro_heartbreak","lo":36,"hi":86}, parents=["electro"], derived=["disco"],
   tech=["electro_tom_percussion","minor_stab_arp_hook","disco_diva_belt","linn_clap_crack"],
   pattern=("freestyle_engine","Latin freestyle (~116 BPM): 808 electro-funk percussion — kick syncopated (1, and-of-2, 4), claps 2&4, toms/claves/cowbell dancing around the backbeat; minor synth stabs + arpeggio runs hook between diva vocal lines.",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,6,12],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"snare":{"4":0.9,"12":0.9},"hat":{"2":0.6,"6":0.6,"10":0.6,"14":0.6}},"chords":[[0,1],[1,6],[2,4],[3,5]],
      "lead":{"voice":"supersaw","octave":4,"steps":[[0,1,1],[2,3,1],[4,5,1],[6,4,1],[8,1,1],[10,5,1],[12,6,1],[14,5,1]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("freestyle_rig","supersaw","kick_808 kit + timpani-pitched electro toms + clave ticks (hat_metal); minor supersaw stabs + chiptune_pulse arps; clap_909 crack; diva topline = the vocal rail; heartbreak in a dance record")]),

 dict(name="eurobeat", bpm=(150,160), key="A minor", form="club",
   voicing={"style":"parapara_octane","lo":36,"hi":88}, parents=["italo_disco"], derived=["hi_nrg"],
   tech=["octave_fifth_bass_drive","key_lift_chorus","fourfloor_hinrg","minor_arp_stab"],
   pattern=("parapara_engine","Eurobeat (~155 BPM): four-floor kick, claps 2&4, open-hat off-8ths; the synth bass HAMMERS octave/fifth 16ths nonstop (busier than Hi-NRG); sax/synth riff hooks answer the verse; the chorus LIFTS a key (+1 st) — the Initial D surge.",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,4,8,12],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"hat":{"2":0.75,"6":0.75,"10":0.75,"14":0.75}},"chords":[[0,1],[2,6]],
      "lead":{"voice":"supersaw","octave":5,"steps":[[0,1,1],[1,5,1],[2,1,1],[3,5,1],[4,3,1],[5,8,1],[6,3,1],[7,8,1],[8,1,1],[9,5,1],[10,1,1],[11,5,1],[12,4,1],[13,8,1],[14,4,1],[15,8,1]]}}),
   mix={"lufs_lo":-10,"lufs_hi":-7,"band_order":"low>mid>lowmid","clipped":0},
   sounds=[("parapara_rig","supersaw","chip_bass hammering octave/fifth 16ths (write them in); supersaw riff hooks; clap_909; the CHORUS KEY-LIFT is law (sections up a semitone); relentless, campy, joyful")]),

 dict(name="wave", bpm=(130,145), key="F# minor", form="song",
   voicing={"style":"lush_dark_glide","lo":30,"hi":86}, parents=[], derived=[],
   tech=["wave_hybrid_bass","ethereal_pad_wash","triplet_hat_roll","sidechain_menace"],
   pattern=("wave_glide","Wave (~138 BPM, half-time): snare on 3; sparse kick (1, and-of-3); the hybrid reese/808 bass SLIDES between melody notes — the bass IS the lead, dark and vocal-like; lush detuned pads wash behind; light triplet hat details; melancholy club euphoria. (hardwave in the graph is its harder child — edge added.)",
     {"bars":1,"swing":0.5,"bass_style":"sub","kick":[0,10],"snare":[8],"hat":[2,5,8,11,14],
      "vel":{"hat":{"2":0.4,"5":0.35,"11":0.35,"14":0.4}},"chords":[[0,1],[2,6]],
      "lead":{"voice":"reese","octave":3,"steps":[[0,1,2],[4,3,2],[8,5,2],[12,4,2],[14,3,1]]}}),
   mix={"lufs_lo":-10,"lufs_hi":-7,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("wave_rig","reese","the hybrid bass = reese + sub_clean gliding (portamento slides between melody notes — it IS the lead); pad_motion + vox_pad huge detuned washes; soft snare 3; fx_pump gentle; melancholy, wide, deep")]),

 dict(name="glitchcore", bpm=(150,180), key="A minor", form="song",
   voicing={"style":"stutter_overload","lo":33,"hi":90}, parents=["hyperpop"], derived=["digicore"],
   tech=["stutter_chop_lead","sensory_overload_stack","glitch_interruption","distorted_gummy_808","hard_cut_ending"],
   pattern=("stutter_engine","Glitchcore (~165 BPM): breakneck trap grid (kick 1 + slides, clap 2&4, 16th hats with roll bursts); the pitched vocal chop is STUTTERED into the lead — constant micro-edit retriggers AS melody (write repeated 16th/32nd note clusters); dense bright synth stacks; switch-ups every 2-4 bars; hard-cut ending.",
     {"bars":1,"swing":0.5,"bass_style":"sub","kick":[0,7,10],"snare":[4,12],"hat":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
      "vel":{"hat":{"1":0.3,"3":0.3,"5":0.3,"7":0.3,"9":0.3,"11":0.3,"13":0.3,"15":0.4}},"chords":[[0,1],[2,6]],
      "lead":{"voice":"chiptune_pulse","octave":5,"steps":[[0,1,1],[1,1,1],[2,1,1],[4,3,1],[5,3,1],[8,5,1],[9,5,1],[10,5,1],[12,4,1],[14,3,1]]}}),
   mix={"lufs_lo":-8,"lufs_hi":-6,"band_order":"mid>low>lowmid","clipped":0,"mid_floor":10.0},
   sounds=[("stutter_rig","chiptune_pulse","stutter lead = chiptune_pulse/supersaw repeated micro-notes (the retrigger written as note clusters) + fx_crush hard (bits 6-10); distorted 808; fx_stutter-style edits = arrangement law (repeat last-16th clusters); louder and busier than digicore — overload IS the aesthetic")]),
]

EXTRA_DERIVED = [("hardwave", "wave")]


def seed():
    kg = KG()
    for n, d in NEW_TECH.items():
        kg.upsert("Technique", n, PROV, desc=d)
    for g in G:
        kg.upsert("Genre", g["name"], PROV, bpm_lo=g["bpm"][0], bpm_hi=g["bpm"][1],
                  common_key=g["key"], voicing=json.dumps(g["voicing"]), form_family=g["form"])
    for g in G:
        name = g["name"]
        for i, t in enumerate(g["tech"]):
            kg.link("Genre", name, "USES_TECHNIQUE", "Technique", t, weight=round(1.0 - i * 0.08, 2))
        pname, pdesc, pgrid = g["pattern"]
        kg.upsert("PatternArchetype", pname, PROV, desc=pdesc, grid=json.dumps(pgrid))
        kg.link("Genre", name, "CHARACTERIZED_BY", "PatternArchetype", pname)
        mt = g["mix"]; mt_name = f"{name}_mix"
        kg.upsert("MixTarget", mt_name, PROV, lufs_lo=mt["lufs_lo"], lufs_hi=mt["lufs_hi"],
                  band_order=mt["band_order"], clipped_samples=mt["clipped"],
                  mid_floor_pct=mt.get("mid_floor"), himid_floor_pct=mt.get("himid_floor"))
        kg.link("Genre", name, "TARGETS", "MixTarget", mt_name)
        for sname, voice, sdesc in g["sounds"]:
            kg.upsert("SoundRecipe", sname, PROV, voice=voice, desc=sdesc)
            kg.link("Genre", name, "CHARACTERIZED_BY", "SoundRecipe", sname)
        for p in g["parents"]:
            kg.link("Genre", name, "SUBGENRE_OF", "Genre", p)
        for d in g["derived"]:
            kg.link("Genre", name, "DERIVED_FROM", "Genre", d, citation=CITE)
    for a, b in EXTRA_DERIVED:
        kg.link("Genre", a, "DERIVED_FROM", "Genre", b, citation=CITE)

    n_gen = kg.q("MATCH (g:Genre) RETURN count(g)")[0][0]
    n_tech = kg.q("MATCH (t:Technique) RETURN count(t)")[0][0]
    print(f"seeded {len(G)} genres (+{len(NEW_TECH)} techniques). graph now: "
          f"{n_gen} genres, {n_tech} techniques.")
    for g in G:
        v = kg.genre_view(g["name"])
        print(f"  {g['name']:12s} parents={v['parents']} tech={len(v['techniques'])} "
              f"inherited={len(v['inherited_techniques'])} mix={bool(v['mixtargets'])}")


if __name__ == "__main__":
    seed()
