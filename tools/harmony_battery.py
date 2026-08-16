#!/usr/bin/env python3
"""THE HARMONY MIND battery (wave-13 backlog fold; R-1 proof battery item).

Known-answer voice-leading, planted parallel fifths, avoid-note law,
cadence kernel, LIL muddiness court + heal, extension court + heal, modal
law + snap, canon progression grammar, spread voicing, per-genre key
profiles (rock bVII regression), aggregate determinism.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theory as T  # noqa: E402
import harmony_court as H  # noqa: E402

FAILS = 0


def check(name, cond, detail=""):
    global FAILS
    print(f"[{'ok' if cond else 'RED'}] {name}" + ("" if cond else f" — {detail}"))
    if not cond:
        FAILS += 1


def mk(pitches, step=1.0, start=0.0, ln=None, vel=0.8):
    return [{"start": start + i * step, "pitch": int(p),
             "len": ln if ln is not None else step * 0.9, "vel": vel}
            for i, p in enumerate(pitches)]


# ------------------------------------------------ 1. rotation voicing (R-1)
g = T.parse_chord("G")
v = T.rotation_voicing(g["pcs"], [60, 64, 67])
cost = sum(min(abs(a - b) % 12, 12 - abs(a - b) % 12)
           for a, b in zip([60, 64, 67], v))
check("rotation solver: C->G minimal motion (L1<=3, keeps G)", cost <= 3 and 67 in v,
      f"v={v} cost={cost}")
am = T.parse_chord("Am")
v2 = T.rotation_voicing(am["pcs"], [60, 64, 67])
check("rotation solver: C->Am keeps common tones C,E", 60 in v2 and 64 in v2,
      f"v={v2}")

# --------------------------------------------- 2. parallel fifths detector
hits = T.parallel_perfects([60, 67], [62, 69])
check("parallel fifths caught", hits and hits[0][2] == 7, str(hits))
check("contrary motion clean", not T.parallel_perfects([60, 67], [59, 67]))

# ------------------------------------------------ 3. chord classification
cmaj7 = T.parse_chord("Cmaj7")
check("F over Cmaj7 = avoid", T.classify_vs_chord(65, cmaj7) == "avoid")
check("D over Cmaj7 = tension", T.classify_vs_chord(62, cmaj7) == "tension")
check("E over Cmaj7 = chord tone", T.classify_vs_chord(64, cmaj7) == "chord_tone")
check("F# over Cmaj7 = tension (#11)", T.classify_vs_chord(66, cmaj7) == "tension")
c7 = T.parse_chord("C7")
check("Db over C7 = tension (b9, dominants take all)",
      T.classify_vs_chord(61, c7) == "tension")

# ----------------------------------------------------- 4. chord-tone court
song = {"bpm": 120, "key": "C major", "lengthBars": 8,
        "chords": [{"bar": 1, "chord": "Cmaj7"}],
        "tracks": [{"name": "keys_line",
                    "source": {"kind": "faust", "id": "pluck"},
                    "notes": mk([65, 65, 65, 65, 64, 62, 60, 64], step=2.0,
                                ln=1.8)}]}
v = H.court_chord_tones(song, "pop")
check("held strong-beat avoid notes flagged",
      not v["ok"] and v["flags"][0]["kind"] == "avoid_notes",
      json.dumps(v)[:200])
song2 = copy.deepcopy(song)
edits = H.heal_chord_tones(song2, "pop")
after = H.court_chord_tones(song2, "pop")
check("avoid heal resolves down a semitone + re-court green",
      edits and after["ok"] and all(e["new"].startswith("E") for e in edits),
      f"{edits[:2]} after_ok={after['ok']}")

pass_song = {"bpm": 120, "key": "C major", "lengthBars": 4,
             "chords": [{"bar": 1, "chord": "Cmaj7"}],
             "tracks": [{"name": "keys", "source": {"kind": "faust", "id": "p"},
                         "notes": mk([64, 65, 67, 65, 64, 62, 60, 62],
                                     step=0.5, ln=0.4)}]}
check("passing color never convicts", H.court_chord_tones(pass_song, "pop")["ok"])

# ------------------------------------------------------ 5. cadence kernel
key = T.parse_key("C major")
check("V7->I with tonic soprano = PAC",
      T.cadence_of(T.parse_chord("G7"), T.parse_chord("C"), key, 0) == "PAC")
check("IV->I = plagal",
      T.cadence_of(T.parse_chord("F"), T.parse_chord("C"), key) == "plagal")
check("V->vi = deceptive",
      T.cadence_of(T.parse_chord("G"), T.parse_chord("Am"), key) == "deceptive")
check("x->V = half",
      T.cadence_of(T.parse_chord("Dm"), T.parse_chord("G"), key) == "half")
check("functions: C=T F=P G=D",
      (T.function_of(T.parse_chord("C"), key),
       T.function_of(T.parse_chord("F"), key),
       T.function_of(T.parse_chord("G"), key)) == ("T", "P", "D"))

# ------------------------------------------------------------- 6. LIL court
mud = {"bpm": 120, "key": "C major", "lengthBars": 4,
       "tracks": [{"name": "pad", "source": {"kind": "faust", "id": "pad"},
                   "notes": (mk([36], step=1, ln=8)[:1] + mk([40], step=1, ln=8)[:1]
                             + mk([36], start=8, ln=8)[:1] + mk([40], start=8, ln=8)[:1])}]}
v = H.court_lil(mud)
check("M3 voiced at C2 flagged as mud",
      not v["ok"] and v["flags"][0]["interval"] == 4, json.dumps(v)[:200])
mud2 = copy.deepcopy(mud)
edits = H.heal_lil(mud2, H.court_lil(mud2))
check("LIL heal opens the stack (+12) + re-court green",
      edits and H.court_lil(mud2)["ok"], f"{edits[:2]}")
hi = {"bpm": 120, "lengthBars": 4,
      "tracks": [{"name": "pad", "source": {"kind": "faust", "id": "pad"},
                  "notes": mk([60], ln=8)[:1] + mk([64], ln=8)[:1]}]}
check("same M3 at C4 clean", H.court_lil(hi)["ok"])

# --------------------------------------------------- 7. extension court+heal
dh = {"bpm": 122, "key": "A minor", "lengthBars": 8,
      "chords": [{"bar": 1, "chord": "Am"}, {"bar": 3, "chord": "Dm"},
                 {"bar": 5, "chord": "F"}, {"bar": 7, "chord": "G"}],
      "tracks": [{"name": "chords", "source": {"kind": "faust", "id": "epiano"},
                  "notes": mk([57, 60, 64], step=0.0, ln=4)}]}
v = H.court_extensions(dh, "deep_house")
check("deep house triads FAIL", not v["ok"], json.dumps(v)[:160])
dh2 = copy.deepcopy(dh)
edits = H.heal_extensions(dh2, "deep_house")
check("extension heal upgrades symbols + lands the 7th",
      any(e["kind"] == "chord_symbol" for e in edits)
      and any(e["kind"] == "land_7th" for e in edits)
      and H.court_extensions(dh2, "deep_house")["ok"],
      f"{edits[:3]}")
check("Am7 chord text after heal",
      dh2["chords"][0]["chord"] in ("Am7",), dh2["chords"][0]["chord"])
punk = {"bpm": 170, "key": "E minor", "lengthBars": 4,
        "chords": [{"bar": 1, "chord": "Em9"}, {"bar": 2, "chord": "Cmaj7"},
                   {"bar": 3, "chord": "G13"}, {"bar": 4, "chord": "Dm11"}],
        "tracks": []}
vp = H.court_extensions(punk, "punk")
check("punk over-extension = advisory not conviction",
      vp["ok"] and vp["advisories"], json.dumps(vp)[:160])

# ------------------------------------------------------------ 8. modal law
psy_major = {"bpm": 145, "key": "E minor", "lengthBars": 8,
             "tracks": [{"name": "acid_lead",
                         "source": {"kind": "faust", "id": "acid"},
                         "notes": mk([64, 66, 68, 69, 71, 73, 75, 76,
                                      64, 66, 68, 69, 71, 73, 75, 76], step=0.5)}]}
v = H.court_modal(psy_major, "psytrance")
check("major psy lead flagged", not v["ok"], json.dumps(v)[:200])
psy2 = copy.deepcopy(psy_major)
edits = H.heal_modal(psy2, "psytrance", v)
check("modal heal snaps to a dark collection + re-court green",
      edits and H.court_modal(psy2, "psytrance")["ok"], f"{edits[:2]}")
dark = {"bpm": 145, "key": "E minor", "lengthBars": 8,
        "tracks": [{"name": "acid_lead", "source": {"kind": "faust", "id": "a"},
                    "notes": mk([64, 65, 68, 69, 71, 72, 74, 76,
                                 64, 65, 68, 69, 71, 72, 74, 76], step=0.5)}]}
check("phrygian-dominant psy lead passes",
      H.court_modal(dark, "goa")["ok"],
      json.dumps(H.court_modal(dark, "goa"))[:200])

# ---------------------------------------------------- 9. progression grammar
axis = {"bpm": 120, "key": "C major", "lengthBars": 16,
        "chords": [{"bar": 1, "chord": "C"}, {"bar": 5, "chord": "G"},
                   {"bar": 9, "chord": "Am"}, {"bar": 13, "chord": "F"}],
        "tracks": []}
v = H.court_progression(axis, "pop")
check("Axis progression scores idiomatic", v["ok"] and v["mean_p"] > 0.1,
      json.dumps(v)[:160])
alien = {"bpm": 120, "key": "C major", "lengthBars": 16,
         "chords": [{"bar": 1, "chord": "C"}, {"bar": 3, "chord": "F#m"},
                    {"bar": 5, "chord": "B"}, {"bar": 7, "chord": "Ebm"},
                    {"bar": 9, "chord": "Db"}, {"bar": 11, "chord": "Em"},
                    {"bar": 13, "chord": "Bb"}, {"bar": 15, "chord": "F#"}],
         "tracks": []}
va = H.court_progression(alien, "pop")
check("alien chain flagged", not va["ok"], json.dumps(va)[:160])
sug = H.suggest_next("pop", "C", "C major")
check("suggest_next returns canon continuations",
      sug and all("chord" in s for s in sug), str(sug))

# ------------------------------------------------------- 10. spread voicing
sp = T.voice_spread(T.parse_chord("Cmaj7"))
lows = [p for p in sp if p < 48]
check("spread voicing: no 3rds below C3 (root/5th/oct only)",
      all(p % 12 in (0, 7) for p in lows) and len(sp) >= 4, str(sp))

# ------------------------------------- 11. per-genre key profiles (rock bVII)
rock_line = mk([60, 62, 64, 65, 67, 70, 67, 65, 60, 62, 64, 65, 67, 70, 67, 64,
                60, 60, 67, 67, 70, 70, 67, 65], step=0.5)
k_rock = T.infer_key(rock_line, "rock")
check("rock bVII-heavy line still keys to C (supermode profile)",
      k_rock and k_rock["tonic_pc"] == 0, str(k_rock and k_rock["name"]))

# ------------------------------------------------------------ 12. aggregate
clean = {"bpm": 120, "key": "C major", "lengthBars": 16,
         "chords": [{"bar": 1, "chord": "C"}, {"bar": 5, "chord": "G"},
                    {"bar": 9, "chord": "Am"}, {"bar": 13, "chord": "F"}],
         "tracks": [{"name": "lead", "source": {"kind": "faust", "id": "p"},
                     "notes": mk([60, 62, 64, 67, 64, 62, 60, 62], step=0.5,
                                 ln=0.4)}]}
agg = H.court_harmony(clean, "pop")
check("aggregate green on a clean pop song", agg["ok"],
      json.dumps({k: v.get('ok') for k, v in agg.items() if isinstance(v, dict)}))
a1 = H.court_harmony(copy.deepcopy(clean), "pop")
a2 = H.court_harmony(copy.deepcopy(clean), "pop")
check("determinism", json.dumps(a1, sort_keys=True) == json.dumps(a2, sort_keys=True))

print(f"\nharmony_battery: {'ALL GREEN' if not FAILS else f'{FAILS} RED'}")
sys.exit(1 if FAILS else 0)
