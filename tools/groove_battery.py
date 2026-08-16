#!/usr/bin/env python3
"""THE GROOVE ENGINE battery (wave-14 backlog fold; pure, zero renders).

Courts: tempo (+halftime resolver), kick topology, backbeat, swing (+heal),
hats (+heal), jitter cap, DNA masks (+snap heal), clave cruzao, fills
(+heal), ghosts (+heal), layering caps, AI-tell composite. Grammar: rolls,
hat automaton choke, ghost grammar, fills, downbeat delay. humanize_v2:
velocity-first discrimination + structured-only. GigaMIDI courts. GrooVAE
round-trip.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drum_grammar as DG  # noqa: E402
import groove_court as GC  # noqa: E402
import groove as GR  # noqa: E402
import expressive as EX  # noqa: E402

FAILS = 0


def check(name, cond, detail=""):
    global FAILS
    print(f"[{'ok' if cond else 'RED'}] {name}" + ("" if cond else f" — {detail}"))
    if not cond:
        FAILS += 1


def hits(starts, pitch=36, vel=0.9, ln=0.1):
    return [{"start": float(s), "pitch": pitch, "len": ln, "vel": vel}
            for s in starts]


def four_floor(bars=4):
    return hits([b * 4 + q for b in range(bars) for q in range(4)])


def song_of(lanes, bpm=128, bars=4, sections=None, key="C major"):
    s = {"bpm": bpm, "key": key, "lengthBars": bars,
         "tracks": [{"name": nm, "source": {"kind": "faust", "id": "kit"},
                     "notes": ns} for nm, ns in lanes]}
    if sections:
        s["sections"] = sections
    return s


# ------------------------------------------------------------- tempo court
v = GC.court_tempo(song_of([("kick", four_floor())], bpm=128), "house")
check("house 128 in window", v["ok"], json.dumps(v))
v = GC.court_tempo(song_of([("kick", four_floor())], bpm=150), "house")
check("house 150 flagged", not v["ok"], json.dumps(v))
# halftime resolver: drill notated 70 (felt 140), snare on beat 3
drill = song_of([("kick", hits([0, 2.75, 4 + 0, 6.75])),
                 ("snare", hits([2, 6, 10, 14], pitch=38)),
                 ("hats", hits([i * 0.5 for i in range(32)], pitch=42))],
                bpm=70, bars=4)
v = GC.court_tempo(drill, "drill")
check("halftime double-count resolved (70 felt as 140)", v["ok"] and
      v.get("feel") == "halftime", json.dumps(v))

# ------------------------------------------------------------- kick court
v = GC.court_kick(song_of([("kick", four_floor())]), "techno")
check("techno 4x4 passes", v["ok"])
v = GC.court_kick(song_of([("kick", hits([0, 2.5, 4, 6.5, 8, 10.5, 12, 14.5]))]),
                  "techno")
check("techno broken floor flagged", not v["ok"], json.dumps(v))
v = GC.court_kick(song_of([("kick", four_floor())]), "ukgarage")
check("UKG 4x4 FORBIDDEN flagged", not v["ok"], json.dumps(v))

# ---------------------------------------------------------- backbeat court
bb = song_of([("snare", hits([1, 3, 5, 7, 9, 11, 13, 15], pitch=38))])
check("boom-bap snare 2&4 passes", GC.court_backbeat(bb, "boombap")["ok"])
bb3 = song_of([("snare", hits([2, 6, 10, 14], pitch=38))])
check("trap snare-on-3 passes", GC.court_backbeat(bb3, "trap")["ok"])
check("trap snare-on-2&4 flagged",
      not GC.court_backbeat(bb, "trap")["ok"])

# ------------------------------------------------------------- swing court
straight_hats = song_of([("hats", hits([i * 0.25 for i in range(64)], pitch=42))])
v = GC.court_swing(straight_hats, "ukgarage")
check("dead-straight UKG hats flagged", not v["ok"] and
      v["flags"][0]["kind"] == "dead_grid", json.dumps(v))
sw = copy.deepcopy(straight_hats)
edits = GC.heal_swing(sw, "ukgarage", v)
v2 = GC.court_swing(sw, "ukgarage")
check("swing heal lands in window", bool(edits) and v2["ok"],
      f"{json.dumps(v2)}")
kick_anchor = all(abs(float(n["start"]) - round(float(n["start"]) / 0.25) * 0.25) < 1e-6
                  for n in sw["tracks"][0]["notes"][:0] or [{'start': 0}])
check("heal touched hats only (kick+bass anchored law)",
      "hats" in json.dumps(edits) and "kick" not in json.dumps(edits))
v = GC.court_swing(song_of([("hats", hits([i * 0.25 for i in range(64)],
                                          pitch=42))]), "techno")
check("techno straight grid exempt", v["ok"])

# --------------------------------------------------------------- hat court
flat = song_of([("hats", hits([i * 0.25 for i in range(64)], pitch=42, vel=0.8)),
                ("snare", hits([2, 6, 10, 14], pitch=38))], bpm=140)
v = GC.court_hats(flat, "trap")
check("flat-velocity + roll-less trap hats flagged",
      not v["ok"] and {f["kind"] for f in v["flags"]} >= {"flat_velocity", "no_rolls"},
      json.dumps(v))
fh = copy.deepcopy(flat)
edits = GC.heal_hats(fh, "trap", v)
v2 = GC.court_hats(fh, "trap")
check("hat heal: velocity grammar + rolls -> green", bool(edits) and v2["ok"],
      json.dumps(v2))

# ------------------------------------------------------------ jitter court
import random
rng = random.Random(3)
jittery = song_of([("hats", hits([i * 0.25 + rng.uniform(-0.06, 0.06)
                                  for i in range(64)], pitch=42))])
v = GC.court_jitter(jittery, "house")
check("over-humanized lane flagged", not v["ok"], json.dumps(v)[:160])
tight = song_of([("hats", hits([i * 0.25 + (0.01 if i % 2 else 0)
                                for i in range(64)], pitch=42))])
check("structured micro-timing passes", GC.court_jitter(tight, "house")["ok"])

# ---------------------------------------------------------- DNA mask court
demb = song_of([("rim", hits([0.75, 1.5, 2.75, 3.5, 4.75, 5.5, 6.75, 7.5],
                             pitch=37))])
v = GC.court_dna_mask(demb, "reggaeton")
check("dembow rim mask passes", v["ok"], json.dumps(v))
wrong = song_of([("rim", hits([0, 1, 2, 3, 4, 5, 6, 7], pitch=37))])
v = GC.court_dna_mask(wrong, "reggaeton")
check("on-grid rim vs dembow flagged", not v["ok"], json.dumps(v)[:200])
w2 = copy.deepcopy(wrong)
edits = GC.heal_dna_mask(w2, "reggaeton", v)
check("mask snap heal improves hit ratio",
      bool(edits) and GC.court_dna_mask(w2, "reggaeton")["ok"],
      json.dumps(GC.court_dna_mask(w2, "reggaeton"))[:200])

# --------------------------------------------------------------- clave law
cruzao = song_of([("clave_a", hits([0, 0.75, 1.5, 2.5, 3.0], pitch=75)),
                  ("clave_b", hits([0.5, 1.0, 2.0, 2.75, 3.5], pitch=76))])
v = GC.court_clave(cruzao, "salsa")
check("cruzao (crossed clave) flagged", not v["ok"], json.dumps(v)[:200])
aligned = song_of([("clave_a", hits([0, 0.75, 1.5, 2.5, 3.0], pitch=75)),
                   ("perc", hits([0, 0.75, 1.5, 2.5, 3.0], pitch=63))])
check("aligned 3-2 passes", GC.court_clave(aligned, "salsa")["ok"])

# -------------------------------------------------------------- fill court
secs = [{"name": "verse", "startBar": 0}, {"name": "chorus", "startBar": 2}]
nofill = song_of([("kick", four_floor(4)), ("snare", hits([1, 3, 5, 7, 9, 11, 13, 15], pitch=38)),
                  ("crash", hits([], pitch=49))], bars=4, sections=secs)
v = GC.court_fills(nofill, "pop")
check("flat verse->chorus seam flagged", not v["ok"], json.dumps(v)[:200])
nf = copy.deepcopy(nofill)
edits = GC.heal_fills(nf, "pop", v)
check("fill heal lands ladder + crash + re-court green",
      bool(edits) and edits[0]["crash"] and GC.court_fills(nf, "pop")["ok"],
      json.dumps(edits))

# -------------------------------------------------------------- ghost law
plain = song_of([("snare", hits([1, 3, 5, 7], pitch=38, vel=0.9))])
v = GC.court_ghosts(plain, "funk")
check("ghostless funk snare flagged", not v["ok"])
pg = copy.deepcopy(plain)
edits = GC.heal_ghosts(pg, "funk", v)
check("ghost heal adds soft taps", bool(edits) and
      GC.court_ghosts(pg, "funk")["ok"] and
      any(float(n["vel"]) < 0.5 for n in pg["tracks"][0]["notes"]),
      json.dumps(edits))

# ------------------------------------------------------------ layering law
stacked = song_of([("kick", four_floor()), ("kick2", four_floor()),
                   ("kick_sub", four_floor())])
v = GC.court_layering(stacked, "trap")
check("3 kick-zone lanes flagged (cap 2)", not v["ok"], json.dumps(v))

# ------------------------------------------------------- AI-tell composite
fake = song_of([("kick", hits([b * 4 + q for b in range(12) for q in (0.0, 2.5)])),
                ("hats", hits([i * 0.25 for i in range(192)], pitch=42, vel=0.8)),
                ("snare", hits([b * 4 + q for b in range(12) for q in (1, 3)],
                               pitch=38))],
               bpm=132, bars=12)
v = GC.court_ai_tells(fake, "ukgarage")
check("AI-tell composite counts the tells",
      len(v["tells"]) >= 3 and not v["ok"] and v["authenticity"] < 0.6,
      json.dumps(v))

# ------------------------------------------------------------ drum grammar
hp = DG.hat_pattern("house", 1)
opens = [n for n in hp if n["pitch"] == 46]
check("house hat automaton: opens on offbeat 8ths", bool(opens) and
      all(abs((n["start"] % 1.0) - 0.5) < 1e-6 for n in opens), str(opens[:2]))
choked = all(a["len"] <= (b["start"] - a["start"]) + 1e-6
             for a, b in zip(hp, hp[1:]))
check("choke law: no hat rings past the next hit", choked)
roll = DG.hat_roll(14.0, 2.0, start_vel=0.4, end_vel=1.0)
check("roll velocity crescendos", roll[0]["vel"] < roll[-1]["vel"] and
      len(roll) == 16, f"n={len(roll)}")
dd = hits([0, 0.5, 1, 1.5, 2], pitch=60)
n_moved = DG.downbeat_delay(dd, 0.07)
check("downbeat delay moves ONLY downbeats", n_moved == 3 and
      dd[1]["start"] == 0.5, str(dd[:3]))

# ------------------------------------------------------------- humanize v2
line = [{"start": i * 0.5, "pitch": 60 + (i % 5), "len": 0.4, "vel": 0.7}
        for i in range(32)]
h = EX.humanize_v2(line, "pop", key_root_pc=0)
vels = [n["vel"] for n in h]
check("humanize_v2 varies velocity (velocity-first law)",
      len(set(vels)) > 8, f"{len(set(vels))} distinct")
check("humanize_v2 EDM keeps the grid (structured-only law)",
      all(abs(n["start"] - line[i]["start"]) < 1e-9
          for i, n in enumerate(EX.humanize_v2(line, "techno"))))
hj = EX.humanize_v2(line, "jazz")
check("jazz rubato moves timing (structured arch)",
      any(abs(n["start"] - line[i]["start"]) > 1e-6 for i, n in enumerate(hj)))
g1 = EX.humanize_v2(line, "pop", key_root_pc=0)
g2 = EX.humanize_v2(line, "pop", key_root_pc=0)
check("humanize_v2 deterministic", json.dumps(g1) == json.dumps(g2))

# --------------------------------------------------------- GigaMIDI courts
dead = [{"start": i * 0.25, "pitch": 42, "len": 0.1, "vel": 0.8}
        for i in range(64)]
gm = EX.gigamidi_courts(dead)
check("GigaMIDI: dead grid reads mechanical", gm["mechanical"], json.dumps(gm))
gm2 = EX.gigamidi_courts(EX.humanize_v2(
    [{"start": i * 0.25 + (0.011 if i % 2 else 0.0), "pitch": 42, "len": 0.1,
      "vel": 0.5 + (i % 7) * 0.05} for i in range(64)], "jazz"))
check("GigaMIDI: humanized take clears DNVR", gm2["dnvr"] > gm["dnvr"],
      f"{gm2['dnvr']} vs {gm['dnvr']}")

# --------------------------------------------------------- final ritard
rsong = {"bpm": 100, "lengthBars": 16, "tracks": []}
rows = EX.final_ritard(rsong, "classical")
check("kinematic ritard: monotone decel to ~0.68x",
      rows and rows[-1]["bpm"] < rows[0]["bpm"] and
      abs(rows[-1]["bpm"] - 68.0) < 2.0,
      str([r["bpm"] for r in rows]))
check("EDM gets no ritard", EX.final_ritard({"bpm": 128, "lengthBars": 16,
                                             "tracks": []}, "techno") == [])

# ------------------------------------------------------- GrooVAE round-trip
rows = GR.to_groovae("mpc_58")
back = GR.from_groovae(rows)
check("GrooVAE encode: offsets are 16th-fractions in [-0.5,0.5]",
      all(-0.5 <= r["offset"] <= 0.5 for r in rows) and rows[1]["offset"] > 0.25)
check("GrooVAE round-trip preserves the pocket",
      all(abs(a - b) < 0.02 for a, b in zip(back["off"], GR.GROOVES["mpc_58"]["off"])))

# --------------------------------------------------------------- aggregate
agg = GC.court_groove(copy.deepcopy(fake), "ukgarage", heal=True)
check("aggregate heals then re-courts (swing green after heal)",
      agg.get("swing_after", {}).get("ok", False), json.dumps(agg.get("swing_after")))
a1 = GC.court_groove(copy.deepcopy(drill), "drill")
a2 = GC.court_groove(copy.deepcopy(drill), "drill")
check("determinism", json.dumps(a1, sort_keys=True) == json.dumps(a2, sort_keys=True))

print(f"\ngroove_battery: {'ALL GREEN' if not FAILS else f'{FAILS} RED'}")
sys.exit(1 if FAILS else 0)
