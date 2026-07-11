#!/usr/bin/env python3
"""KG curation wave 3 (2026-07-06): WORLD SLICE B — South Asia, SE Asia, Mediterranean,
Maghreb, African lineages, Caribbean-Colombian, Lusophone. Session `genre-scout`
(campaign: genre-research-campaign). AUTHORED INLINE from model knowledge per the
no-subagents law — evidence + confidence flags in docs/research_genre_expansion_w3.md
(no web pass ran; ⚠BPM genres get eval-rail verification). Idempotent (MERGE).

Also adds cross-wave lineage: kwaito<-mbaqanga, dangdut<-bollywood_filmi,
coupe_decale<-soukous, champeta<-soukous+dancehall.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kg import KG

PROV = ("curated:claude/2026-07-06 (coverage-expansion wave 3 slice B, session genre-scout; "
        "INLINE model-knowledge authorship [Jan-2026 cutoff], confidence flags in "
        "docs/research_genre_expansion_w3.md — no web pass; eval-rail verifies)")
CITE = "curated:claude/2026-07-06-genrexp3"

NEW_TECH = {
 # qawwali
 "qawwali_takrar": "ecstatic REPETITION: the hook phrase repeats and intensifies (takrar) while the lead inserts girah (couplets) and sargam runs — the arc climbs in waves, never resets",
 "party_clap_response": "the qawwali party claps HARD on 2 & 4 and answers every lead phrase in unison — call-and-response as the engine",
 "harmonium_shadow": "the harmonium doubles the vocal line in real time (slightly behind, ornamented) over a tonic drone — melody and accompaniment are ONE voice",
 "accelerating_arc": "the performance accelerates across sections (tempoMap ramps ~70 -> ~140) with intensity, not a fixed tempo",
 # carnatic / hindustani
 "gamaka_ornament": "Carnatic gamaka: pitches OSCILLATE — write melodies as neighbor-note oscillations around the target tone, never plain held notes",
 "adi_tala_cycle": "adi tala: an 8-beat cycle (2 bars of 4/4) with the cadence (korvai) landing on beat 1 of the NEXT cycle — phrase across the barline, resolve on sam",
 "melodic_shadowing": "the accompanying melody instrument SHADOWS the lead a moment behind, echoing each phrase — heterophony, not harmony",
 "teental_16": "teental: a 16-beat cycle = one 16-slot bar; SAM (strongest) on slot 0, KHALI (empty — tabla skips the bass) on slot 8, claps 0/4/12 — the whole form breathes in 16s",
 "tabla_theka_bols": "the tabla theka speaks bols (dha dhin dhin dha ...): bass dagga strokes on the tali beats, dry treble ticks between, bass SILENT at khali",
 "alap_free_intro": "alap: a free-time drumless raga exploration BEFORE the pulse enters — open every piece with a rubato drone+melody section",
 "tanpura_eternal_drone": "the tanpura tonic-fifth drone runs the ENTIRE piece — nothing modulates, the raga lives against the drone",
 # dangdut
 "gendang_dangdut_figure": "THE dangdut signature: the gendang plays a low pickup 'dang' late in the bar into the high 'DUT' on the downbeat (slots ~12/14 -> 0) — the sway lives in that pickup",
 "cengkok_vibrato_vocal": "wailing melismatic vocal with heavy slow vibrato and note-bends (cengkok) — the melody is 70% ornament",
 "suling_answer": "a breathy suling flute answers every vocal phrase in the gaps",
 # luk thung / mor lam
 "lukthung_croon_bend": "luk thung vocal: crooned country phrasing with deep note-bending vibrato (luk khrua) over langorous two-chord minor vamps",
 "upbeat_brass_stab": "brass/organ stabs on the upbeats push the sway — Thai country's backbeat shimmer",
 "khaen_drone_riff": "the khaen mouth organ holds chordal drones AND riffs simultaneously (free-reed clusters) — sustained harmonica-family chords driving the lam",
 "phin_interlock": "the phin lute picks a bright cyclic pentatonic riff interlocking with the khaen — Isan's twin engine",
 "lam_speech_song": "lam vocal: rapid semi-spoken pentatonic patter that resolves to sung tones at phrase ends",
 # rebetiko
 "zeibekiko_9_4": "THE rebetiko meter: zeibekiko 9/4 felt as 2+2+2+3 (the aksak family) at a heavy ~60-90 — a solo man's slow limping dance; encode via section time-sig/tempoMap, accent the long cell",
 "bouzouki_tremolo_dromoi": "double-course bouzouki tremolo lead in the dromoi (Hijaz, Ousak=Phrygian, Rast) with taximi (free rubato intro) before the song",
 "baglamas_chirp": "the tiny baglamas doubles the bouzouki an octave up, chirping offbeat chords",
 # rai
 "derbouka_dum_tek": "derbouka engine: deep DUM on 1 and the and-of-2, dry TEK splashes on the offbeats, bendir frame-drum roll under — the Maghreb pocket",
 "melisma_maqam_vocal": "melismatic vocal in Bayati/Hijaz color sliding between phrases — the raï cry, answered by a synth line",
 "pop_rai_synth_stab": "cheap bright 80s synth stabs + string-machine pads riding the derbouka — the Oran cabaret-to-club sound",
 # mbaqanga
 "marabi_cycle": "the marabi harmonic engine: I - IV - I6/4 - V cycling FOREVER (no bridge, no key change) — South African township perpetual motion",
 "groaner_bass_vocal": "the GROANER: a huge gravel bass voice answering the sweet girl-group hook — register contrast as arrangement",
 "jangly_cycle_guitar": "a bright clean lead guitar picks short cyclic lines over the cycle, more riff than solo",
 "township_foursquare": "four-square stomp: kick on all four, snare cracking 2 & 4, organ/sax stabs on the offbeats — dance-floor steady, never busy",
 # juju
 "talking_drum_speech": "the dundun talking drum BENDS pitch mid-phrase (squeeze the strings) to 'speak' — use a bending drum voice (dhol bend zone) playing conversational phrases across the groove",
 "shekere_eighths": "shekere/beaded-gourd rides straight 8ths with hand accents — the juju timekeeper",
 "praise_call_response": "leader sings praise lines, the chorus answers the SAME melody — long-form medleys that flow without stopping",
 # benga
 "benga_running_bass": "THE benga marker: the bass GALLOPS — fast melodic running lines (nyatiti-derived) that lead the band like a second guitar; write the bassline as a melody, not roots",
 "parallel_thirds_vocal": "verses sung in sweet parallel thirds — two voices moving together",
 "dry_snap_kit": "a dry, tight, snappy kit — no reverb wash; the speed needs air",
 # chimurenga
 "mbira_kushaura_kutsinhira": "two interlocking mbira parts: kushaura leads, kutsinhira answers OFFSET (a pulse behind/ahead) — together they weave the wheel; write two kalimba tracks offset",
 "hosho_triplet_drive": "the hosho shaker drives the 3-pulse (12/8) with a sharp chick on each group — the clave of chimurenga",
 "four_phrase_wheel": "the harmony is a 4-phrase wheel (48-pulse cycles, the i-VII-VI-VII family) that turns forever — form = texture change over the wheel",
 # coupe decale
 "rolling_tom_decale": "four-floor kick + ROLLING tom/perc figures filling the offbeats — the percussion IS the melody hook",
 "atalaku_shout_lead": "chanted shouts and crowd commands lead the track (the atalaku lineage from soukous) — vocals as percussion",
 "drop_to_drums": "the decale drop: everything mutes except drums + shout, then slams back — arrangement by subtraction",
 # champeta
 "pico_guitar_loop": "a looping bright soukous-style guitar riff (2-4 bars) carries the whole track — the pico soundsystem inheritance",
 "espeluque_break": "el espeluque: the percussion-and-vocal breakdown where the beat strips to perc + chant — champeta's drop",
 "dembow_perc_bed": "a dembow-leaning perc bed (boom-ch-boom-chick) under the guitar loop; modern urbana adds the reggaeton kit outright",
 # morna
 "sodade_ballad_lilt": "morna's habanera-leaning lilt: the bass leans on 1 and the and-of-2, arpeggios fill — unhurried, the voice sits BEHIND the beat",
 "cavaquinho_violao_weave": "cavaquinho (bright, high strums/arpeggios) weaves over violao (fingered arpeggios + bassline) — the two-guitar morna bed",
 "diminished_passing_color": "minor ii-V-i motion sweetened with chromatic passing diminished chords — the sodade harmonic signature",
}

G = [
 dict(name="qawwali", bpm=(70,140), key="D major (raga-modal)", form="through_composed",
   voicing={"style":"devotional_unison","lo":38,"hi":84}, parents=[], derived=[],
   tech=["qawwali_takrar","party_clap_response","harmonium_shadow","accelerating_arc","tanpura_eternal_drone"],
   pattern=("qawwali_arc","Qawwali (~104 BPM rising, keherwa-family 4/4, swing ~0.54): tabla/dholak bass on 1 + the pickup, dry ticks between; the PARTY claps HARD on 2&4; harmonium shadows the vocal over an eternal tanpura drone; the hook repeats and INTENSIFIES (takrar) — build with tempoMap acceleration and layer-adds, never reset.",
     {"bars":1,"swing":0.54,"bass_style":"sustained","kick":[0,6,8],"snare":[4,12],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"4":0.95,"12":0.95},"hat":{"0":0.4,"2":0.3,"4":0.4,"6":0.3,"8":0.4,"10":0.3,"12":0.4,"14":0.3}},
      "chords":[[0,1]],"lead":{"voice":"accordion","octave":4,"steps":[[0,1,2],[2,2,1],[4,3,2],[8,2,2],[10,3,1],[12,1,3]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-10,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":10.0},
   sounds=[("qawwali_party","accordion","harmonium = accordion shadowing the lead melody; tabla/dholak = dhol (bass, bend for the dagga) + tight tick snare; claps STACKED (clap_909 layered, human-loose) on 2&4; tanpura_drone under everything; build = tempoMap ramp + adding clap/voice layers")]),

 dict(name="carnatic", bpm=(60,120), key="C major (shankarabharanam)", form="through_composed",
   voicing={"style":"gamaka_modal","lo":48,"hi":88}, parents=[], derived=[],
   tech=["gamaka_ornament","adi_tala_cycle","melodic_shadowing","tanpura_eternal_drone","alap_free_intro"],
   pattern=("adi_tala","Carnatic (adi tala: 8-beat cycle = 2 bars 4/4, ~84 BPM): mridangam theka — bass strokes anchor beats 1/5/7 with dry ticks between; NO backbeat; the melody OSCILLATES (gamaka) around raga tones over the tanpura drone; violin/flute shadows a beat behind; cadences (korvai) land on the NEXT cycle's beat 1.",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0,6,10],"hat":[2,4,8,12,14],
      "vel":{"hat":{"2":0.4,"4":0.5,"8":0.5,"12":0.5,"14":0.4}},"chords":[[0,1]],
      "lead":{"voice":"flute_lead","octave":5,"steps":[[0,1,1],[1,2,1],[2,1,1],[4,3,1],[5,4,1],[6,3,1],[8,5,1],[9,4,1],[10,5,1],[12,3,2],[14,1,2]]}}),
   mix={"lufs_lo":-16,"lufs_hi":-12,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":10.0},
   sounds=[("carnatic_ensemble","flute_lead","Carnatic flute (flute_lead) or veena (pluck, long ring) with gamaka written as neighbor-note oscillation; mridangam = dhol (low, short) + tick lane; tanpura_drone eternal; open with a FREE drumless alap section; room-intimate, very dynamic")]),

 dict(name="hindustani", bpm=(60,140), key="D major (raga-modal)", form="through_composed",
   voicing={"style":"raga_long_arc","lo":45,"hi":88}, parents=[], derived=[],
   tech=["teental_16","tabla_theka_bols","alap_free_intro","tanpura_eternal_drone","melodic_shadowing"],
   pattern=("teental_gat","Hindustani gat in teental (~96 BPM): the 16-beat cycle IS the 16-slot bar — SAM heavy on slot 0, tali marked at 4/12, KHALI at slot 8 (tabla bass SILENT there, ticks continue); sitar states the bandish, doubles into jhala; tanpura drone forever; open free (alap) before the theka enters.",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0,4,12],"hat":[1,2,3,5,6,7,8,9,10,11,13,14,15],
      "vel":{"kick":{"0":1.0,"4":0.7,"12":0.7},"hat":{"8":0.55,"1":0.3,"3":0.3,"5":0.3,"7":0.3,"9":0.35,"11":0.3,"13":0.3,"15":0.3}},
      "chords":[[0,1]],"lead":{"voice":"pluck","octave":4,"steps":[[0,1,2],[3,2,1],[4,3,1],[6,4,1],[8,5,2],[11,4,1],[12,3,1],[14,2,2]]}}),
   mix={"lufs_lo":-16,"lufs_hi":-12,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":10.0},
   sounds=[("hindustani_trio","pluck","sitar = pluck (bright, long ring, meend written as pitch-neighbor motion); tabla = dhol with the BEND zone for dagga speech + a dry tick lane (khali law: no bass at slot 8); tanpura_drone; alap first, theka enters late; never quantize the lead hard")]),

 dict(name="dangdut", bpm=(90,140), key="A minor (Hijaz color)", form="song",
   voicing={"style":"melayu_sway","lo":38,"hi":84}, parents=[], derived=["bollywood_filmi"],
   tech=["gendang_dangdut_figure","cengkok_vibrato_vocal","suling_answer","four_on_floor_club_layer"],
   pattern=("dang_dut","Dangdut (~112 BPM): THE gendang figure — low 'dang' pickup at slots 12/14 rolling into the high 'DUT' on the downbeat; kick anchors 1&3, offbeat hats sway; suling flute answers the wailing cengkok vocal; minor/Hijaz-tinged Melayu melody; koplo variant runs hotter with busier gendang rolls.",
     {"bars":1,"swing":0.53,"bass_style":"roots","kick":[0,8,12],"snare":[14],"hat":[2,6,10,14],
      "vel":{"kick":{"0":1.0,"8":0.9,"12":0.7},"snare":{"14":0.8}},"chords":[[0,1],[2,5]],
      "lead":{"voice":"flute_lead","octave":5,"steps":[[0,1,2],[3,2,1],[4,3,1],[6,2,1],[8,1,2],[12,5,2],[14,4,1]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("dangdut_kit","flute_lead","suling = flute_lead breathy answers; gendang = dhol two-voiced (low bend 'dang' + tight high 'dut'); modern koplo layer = kick_808 four-floor under the acoustic figure; vocal melody 70% ornament (write neighbor bends)")]),

 dict(name="luk_thung", bpm=(60,110), key="F minor", form="song",
   voicing={"style":"thai_croon","lo":38,"hi":84}, parents=[], derived=[],
   tech=["lukthung_croon_bend","upbeat_brass_stab","dorian_min7_vamp"],
   pattern=("lukthung_sway","Luk thung (~88 BPM sway): kick 1&3, snare soft 2&4, brass/organ stabs on the UPBEATS; a langorous two-chord minor vamp; the crooned lead bends deep into notes (write approach-note slides); string pads swell behind. [BPM verified inline 2026-07-06, see doc addendum.]",
     {"bars":1,"swing":0.5,"bass_style":"roots","kick":[0,8],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"snare":{"4":0.6,"12":0.6},"hat":{"2":0.6,"6":0.6,"10":0.6,"14":0.6}},"chords":[[0,1],[2,4]],
      "lead":{"voice":"flute_lead","octave":4,"steps":[[0,1,2],[2,2,1],[4,3,2],[8,2,2],[12,1,3]]}}),
   mix={"lufs_lo":-13,"lufs_hi":-10,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":9.0},
   sounds=[("lukthung_band","flute_lead","crooning lead = flute_lead/pluck with slow approach bends; organ_soul + brass_stab upbeat stabs; strings_disco pads; warm vintage master, dynamic")]),

 dict(name="mor_lam", bpm=(110,145), key="G major (pentatonic)", form="song",
   voicing={"style":"isan_drive","lo":40,"hi":86}, parents=[], derived=["luk_thung"],
   tech=["khaen_drone_riff","phin_interlock","lam_speech_song","dry_snap_kit"],
   pattern=("lam_drive","Mor lam (~126 BPM drive): kick four-square-ish (1, 3, 3.5), snare 2&4, light running hats; the KHAEN (mouth organ) holds chordal drone-riffs while the phin lute picks a bright pentatonic interlock; lam vocal = rapid speech-song resolving to sung tones. [BPM verified inline 2026-07-06, see doc addendum.]",
     {"bars":1,"swing":0.52,"bass_style":"roots","kick":[0,8,10],"snare":[4,12],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"hat":{"0":0.5,"2":0.35,"4":0.5,"6":0.35,"8":0.5,"10":0.35,"12":0.5,"14":0.35}},"chords":[[0,1],[2,5]],
      "lead":{"voice":"harmonica","octave":4,"steps":[[0,1,2],[2,3,1],[4,5,1],[6,3,1],[8,1,2],[10,5,1],[12,3,1],[14,2,1]]}}),
   mix={"lufs_lo":-12,"lufs_hi":-9,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":10.0},
   sounds=[("isan_engine","harmonica","khaen = harmonica (free-reed twin) holding chord drones + riffs; phin = pluck bright cyclic pentatonic; dry snappy kit; modern lam sing = hotter, add bass_warm driving")]),

 dict(name="rebetiko", bpm=(60,130), key="D Phrygian (Ousak)", form="song",
   voicing={"style":"bouzouki_dromoi","lo":38,"hi":84}, parents=[], derived=[],
   tech=["zeibekiko_9_4","bouzouki_tremolo_dromoi","baglamas_chirp","saudade_rubato"],
   pattern=("zeibekiko","Rebetiko zeibekiko (9/4 as 2+2+2+3 — the aksak cousin — at a heavy ~72; the 16-grid approximates one 9/4 bar, accent the cell heads and give the last cell its extra length via the final quarter): bouzouki tremolo leads in Ousak/Hijaz dromoi, baglamas chirps offbeat octaves, one guitar chugs i-V; open with a free taximi. Hasapiko variant = straight 2/4 ~120.",
     {"bars":1,"swing":0.5,"bass_style":"sustained","kick":[0,4,8,12],"snare":[2,6,10],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"kick":{"0":1.0,"4":0.85,"8":0.85,"12":0.95},"snare":{"2":0.4,"6":0.4,"10":0.4},"hat":{"12":0.6,"14":0.6}},
      "chords":[[0,1],[3,5]],"lead":{"voice":"pluck2","octave":4,"steps":[[0,1,1],[1,2,1],[2,3,1],[4,4,1],[6,3,1],[8,2,1],[10,3,1],[12,1,3]]}}),
   mix={"lufs_lo":-15,"lufs_hi":-11,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":10.0},
   sounds=[("rebetiko_trio","pluck2","bouzouki = pluck2 double-course tremolo (write tremolo as repeated 16ths) in Hijaz/Ousak; baglamas = pluck octave up, offbeat chirps; viola-strum guitar chugs; intimate taverna room, very dynamic; encode TRUE 9/4 via section time-sig/tempoMap")]),

 dict(name="rai", bpm=(100,130), key="E Phrygian (Bayati color)", form="song",
   voicing={"style":"oran_cabaret_club","lo":36,"hi":84}, parents=[], derived=[],
   tech=["derbouka_dum_tek","melisma_maqam_vocal","pop_rai_synth_stab","four_on_floor_club_layer"],
   pattern=("rai_pocket","Raï (~116 BPM): derbouka engine — deep DUM on 1 and the and-of-2 (slot 6), dry TEK splashing offbeats, bendir roll under; 80s pop-raï synth stabs answer the melismatic Bayati/Hijaz vocal; modern raï lays a four-floor kick beneath the derbouka.",
     {"bars":1,"swing":0.54,"bass_style":"roots","kick":[0,6,8],"snare":[4,10,12],"hat":[2,6,10,14],
      "vel":{"kick":{"0":1.0,"6":0.8,"8":0.9},"snare":{"4":0.7,"10":0.5,"12":0.7}},"chords":[[0,1],[2,6]],
      "lead":{"voice":"accordion","octave":4,"steps":[[0,1,2],[2,2,1],[4,1,1],[6,3,1],[8,2,2],[12,1,2],[14,2,1]]}}),
   mix={"lufs_lo":-11,"lufs_hi":-8,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("rai_rig","accordion","derbouka = dhol tight (dum) + tick lane (tek); synth stabs = supersaw/accordion bright; strings pads; the vocal line slides between phrases (write chromatic approach bends); modern layer = kick_punch four-floor")]),

 dict(name="mbaqanga", bpm=(110,130), key="C major", form="song",
   voicing={"style":"township_jive","lo":33,"hi":84}, parents=[], derived=[],
   tech=["marabi_cycle","groaner_bass_vocal","jangly_cycle_guitar","township_foursquare"],
   pattern=("township_jive","Mbaqanga (~118 BPM): four-square stomp — kick all four, snare cracks 2&4, organ/sax stabs offbeats; the marabi cycle I-IV-I6/4-V loops FOREVER; jangly clean guitar picks cyclic lines; the groaner bass voice answers the girl-group hook (register contrast = the arrangement).",
     {"bars":1,"swing":0.52,"bass_style":"walking","kick":[0,4,8,12],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"snare":{"4":0.9,"12":0.9},"hat":{"2":0.6,"6":0.6,"10":0.6,"14":0.6}},
      "chords":[[0,1],[1,4],[2,1],[3,5]],
      "lead":{"voice":"pluck","octave":5,"steps":[[0,1,1],[2,3,1],[4,5,1],[6,3,1],[8,1,1],[10,4,1],[12,5,1],[14,3,1]]}}),
   mix={"lufs_lo":-12,"lufs_hi":-9,"band_order":"lowmid>low>mid","clipped":0},
   sounds=[("township_band","pluck","jangly lead = pluck bright cyclic; organ_soul offbeat stabs + sax_section riffs; the groaner = a LOW bass_warm/formant_vox counter-voice; four-square kit, warm and danceable — the direct ancestor of kwaito (edge in graph)")]),

 dict(name="juju", bpm=(100,125), key="G major", form="through_composed",
   voicing={"style":"yoruba_interlock","lo":38,"hi":86}, parents=[], derived=[],
   tech=["talking_drum_speech","shekere_eighths","praise_call_response","interlocking_guitars"],
   pattern=("juju_weave","Jùjú (~112 BPM, 12/8 undercurrent — swing ~0.56): kick 1&3 soft; shekere rides straight 8ths; the TALKING DRUM (pitch-bending) speaks conversational accents across slots 3/6/11/14; two clean guitars interlock a two-chord major vamp (I-IV cycling); leader/chorus praise call-response; long-form — flow, don't drop.",
     {"bars":1,"swing":0.56,"bass_style":"roots","kick":[0,8],"snare":[3,6,11,14],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"3":0.55,"6":0.7,"11":0.55,"14":0.7},"hat":{"0":0.5,"2":0.4,"4":0.5,"6":0.4,"8":0.5,"10":0.4,"12":0.5,"14":0.4}},
      "chords":[[0,1],[2,4]],"lead":{"voice":"pluck","octave":5,"steps":[[0,1,1],[2,5,1],[4,3,1],[6,1,1],[8,5,1],[10,3,1],[12,4,1],[14,5,1]]}}),
   mix={"lufs_lo":-13,"lufs_hi":-10,"band_order":"lowmid>mid>low","clipped":0},
   sounds=[("juju_band","pluck","talking drum = dhol with the BEND zone ridden per-note (it speaks); shekere = bright hat 8ths; two interlocking plucks (lead octave 5 + mi-solo pluck2 octave 4); warm bass; pedal-steel color = pad_motion soft swells")]),

 dict(name="benga", bpm=(100,135), key="D major", form="song",
   voicing={"style":"bass_led_gallop","lo":33,"hi":86}, parents=[], derived=[],
   tech=["benga_running_bass","parallel_thirds_vocal","dry_snap_kit","interlocking_guitars"],
   pattern=("benga_gallop","Benga (~124 BPM): THE BASS LEADS — a galloping melodic running bassline (nyatiti-derived) written as a melody; bright interlocking guitars answer; light four-square kick, dry snappy snare 2&4; major I-IV-V at speed; vocals in parallel thirds. [BPM verified inline 2026-07-06, see doc addendum.]",
     {"bars":1,"swing":0.5,"bass_style":"walking","kick":[0,4,8,12],"snare":[4,12],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"kick":{"0":0.8,"4":0.6,"8":0.8,"12":0.6},"hat":{"0":0.45,"2":0.35,"4":0.45,"6":0.35,"8":0.45,"10":0.35,"12":0.45,"14":0.35}},
      "chords":[[0,1],[1,4],[2,5],[3,1]],
      "lead":{"voice":"pluck","octave":5,"steps":[[0,1,1],[1,3,1],[2,5,1],[4,4,1],[5,3,1],[6,1,1],[8,5,1],[9,3,1],[10,1,1],[12,4,1],[13,5,1],[14,3,1]]}}),
   mix={"lufs_lo":-12,"lufs_hi":-9,"band_order":"lowmid>mid>low","clipped":0},
   sounds=[("benga_band","pluck","the bass = bass_warm playing MELODIC running lines (walking style, fast); two bright plucks interlocking; DRY snappy kit (no wash); sunny, fast, guitar-forward")]),

 dict(name="chimurenga", bpm=(110,130), key="A minor (mbira wheel)", form="through_composed",
   voicing={"style":"mbira_wheel","lo":40,"hi":86}, parents=[], derived=[],
   tech=["mbira_kushaura_kutsinhira","hosho_triplet_drive","four_phrase_wheel","hypnotic_repetition"],
   pattern=("mbira_wheel","Chimurenga (~120 BPM, 12/8 — swing 0.66 approximates the triplet wheel): TWO kalimba (mbira) parts interlock — kushaura leads, kutsinhira answers offset; the hosho shaker chicks the 3-pulse; kick breathes 1 & the 4th triplet group; the 4-phrase harmonic wheel (i-VII-VI-VII family) turns forever; texture evolves, the wheel never stops.",
     {"bars":1,"swing":0.66,"bass_style":"roots","kick":[0,8],"snare":[6,14],"hat":[0,2,4,6,8,10,12,14],
      "vel":{"snare":{"6":0.5,"14":0.5},"hat":{"0":0.6,"2":0.4,"4":0.5,"6":0.4,"8":0.6,"10":0.4,"12":0.5,"14":0.4}},
      "chords":[[0,1],[1,7],[2,6],[3,7]],
      "lead":{"voice":"kalimba","octave":4,"steps":[[0,1,1],[2,3,1],[4,5,1],[6,3,1],[8,1,1],[10,5,1],[12,3,1],[14,5,1]]}}),
   mix={"lufs_lo":-14,"lufs_hi":-11,"band_order":"mid>lowmid>low","clipped":0,"mid_floor":10.0},
   sounds=[("mbira_pair","kalimba","TWO kalimba tracks (kushaura + kutsinhira OFFSET by a pulse — write the second track shifted); hosho = hat triplet chicks; soft kit underneath; guitar may double the mbira line (pluck); hypnotic — let the wheel turn 16+ cycles")]),

 dict(name="coupe_decale", bpm=(100,125), key="F major", form="club",
   voicing={"style":"abidjan_roll","lo":36,"hi":84}, parents=[], derived=["soukous"],
   tech=["rolling_tom_decale","atalaku_shout_lead","drop_to_drums","static_major_harmony"],
   pattern=("decale_roll","Coupé-décalé (~112 BPM): four-floor kick + ROLLING tom/perc figures filling the offbeats (slots 2/5/10/13) — the percussion IS the hook; one-chord major harmony; chanted shouts lead; the drop strips to drums + shout then slams back. [BPM verified inline 2026-07-06, see doc addendum.]",
     {"bars":1,"swing":0.52,"bass_style":"roots","kick":[0,4,8,12],"snare":[2,5,10,13],"hat":[2,6,10,14],
      "vel":{"snare":{"2":0.6,"5":0.75,"10":0.6,"13":0.75}},"chords":[[0,1]],
      "lead":{"voice":"marimba","octave":5,"steps":[[0,1,1],[2,5,1],[5,3,1],[8,1,1],[10,5,1],[13,3,1]]}}),
   mix={"lufs_lo":-10,"lufs_hi":-7,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("decale_kit","marimba","rolling toms = timpani pitched mid + log_drum accents; marimba perc-melody hook; shouts = formant_vox stabs; synth-brass = brass_stab; the DROP = mute all but drums+shout (arrangement law)")]),

 dict(name="champeta", bpm=(100,170), key="A minor", form="club",
   voicing={"style":"pico_loop","lo":36,"hi":84}, parents=[], derived=["soukous","dancehall","highlife"],
   tech=["pico_guitar_loop","espeluque_break","dembow_perc_bed","atalaku_shout_lead"],
   pattern=("pico_loop","Champeta (~130 BPM): a looping bright soukous-style guitar riff (2-4 bars) over a dembow-leaning perc bed (kick 0/3/8/11 boom-ch-boom-chick), chanted costeño vocals; EL ESPELUQUE = strip to percussion + chant, then slam the loop back; urbana variant adds the reggaeton kit. [BPM verified inline 2026-07-06, see doc addendum.]",
     {"bars":1,"swing":0.53,"bass_style":"roots","kick":[0,3,8,11],"snare":[4,12],"hat":[2,6,10,14],
      "vel":{"kick":{"0":1.0,"3":0.75,"8":1.0,"11":0.75}},"chords":[[0,1],[2,6]],
      "lead":{"voice":"pluck","octave":5,"steps":[[0,1,1],[1,3,1],[2,5,1],[4,3,1],[6,5,1],[8,1,1],[9,3,1],[10,5,1],[12,3,1],[14,5,1]]}}),
   mix={"lufs_lo":-10,"lufs_hi":-7,"band_order":"low>lowmid>mid","clipped":0},
   sounds=[("pico_rig","pluck","the guitar loop = pluck bright cycling (soukous inheritance, graph edge); dembow perc bed; bass_warm simple; espeluque = arrangement mute-to-perc; urbana = swap kit to kick_808 + reggaeton snare")]),

 dict(name="morna", bpm=(55,90), key="A minor", form="song",
   voicing={"style":"sodade_ballad","lo":40,"hi":81}, parents=[], derived=[],
   tech=["sodade_ballad_lilt","cavaquinho_violao_weave","diminished_passing_color","saudade_rubato","percussionless_intimacy"],
   pattern=("sodade","Morna (~68 BPM, habanera-leaning lilt, essentially percussionless): violao lays fingered arpeggios + a soft bass leaning on 1 and the and-of-2; cavaquinho weaves bright arpeggios above; minor ii-V-i with chromatic passing diminished color; the voice sits BEHIND the beat (rubato). Drumless grid (fado precedent).",
     {"bars":1,"swing":0.54,"bass_style":"sustained","chords":[[0,1],[1,2],[2,5],[3,1]],
      "lead":{"voice":"pluck2","octave":4,"steps":[[0,1,2],[2,3,1],[4,5,2],[6,4,1],[8,3,2],[12,1,3]]}}),
   mix={"lufs_lo":-18,"lufs_hi":-13,"band_order":"lowmid>mid>low","clipped":0,"mid_floor":9.0},
   sounds=[("morna_duo","pluck2","violao = pluck2 fingered arpeggios + bassline; cavaquinho = pluck bright above; upright_bass soft; accordion/violin color answering the voice; intimate room, very dynamic, voice behind the beat (never quantize)")]),
]

# cross-wave lineage completion (targets all exist in the graph)
EXTRA_DERIVED = [("kwaito", "mbaqanga")]


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
        print(f"  {g['name']:14s} parents={v['parents']} tech={len(v['techniques'])} "
              f"inherited={len(v['inherited_techniques'])} mix={bool(v['mixtargets'])}")


if __name__ == "__main__":
    seed()
