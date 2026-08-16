#!/usr/bin/env python3
"""MUSIC COURTS battery (P2/P4/P8) — planted-fault proofs + corpus sanity.

The spec law: courts must catch planted mid AND pass real accepted work.
Pure JSON, no renders; fast enough for the default suite.
"""
import copy
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music_court as MC  # noqa: E402
import theory as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = [0]


def ok(cond, msg):
    N[0] += 1
    if not cond:
        print(f"FAIL #{N[0]}: {msg}")
        sys.exit(1)


def mknote(start, pitch, ln=0.5, vel=0.9):
    return {"start": float(start), "len": ln, "pitch": int(pitch), "vel": vel}


def base_song():
    """A clean 4-bar A-minor sketch: lead + keys in key, on grid, plus drums."""
    lead = [mknote(s, p) for s, p in
            [(0, 69), (1, 72), (2, 71), (3, 69), (4, 64), (5, 65), (6, 67), (7, 69),
             (8, 69), (9, 72), (10, 71), (11, 69), (12, 76), (13, 74), (14, 72), (15, 71)]]
    keys = [mknote(s, p, ln=1.0) for s, p in
            [(0, 57), (0, 60), (0, 64), (4, 53), (4, 57), (4, 60),
             (8, 55), (8, 59), (8, 62), (12, 52), (12, 55), (12, 59)]]
    kick = [mknote(b, 36, ln=0.2, vel=1.0) for b in range(0, 16, 1)]
    return {"version": 2, "bpm": 120, "lengthBars": 4, "key": "A minor",
            "swing": {"grid": "16th", "amount": 0.5},
            "chords": [{"bar": 1, "chord": "Am"}, {"bar": 2, "chord": "F"},
                       {"bar": 3, "chord": "G"}, {"bar": 4, "chord": "Em"}],
            "tracks": [
                {"name": "lead", "source": {"id": "pluck_bright"}, "notes": lead},
                {"name": "keys", "source": {"id": "warm_epiano"}, "notes": keys},
                {"name": "kick", "source": {"id": "kick_punch"}, "notes": kick}]}


# ---------------- P2 KEY COURT ----------------
s = base_song()
v = MC.court_key(s, "pop")
ok(v["ok"] and v["sour"] == 0, f"clean song passes key court ({v})")

# plant three sour notes (D#=63 long strong, G#=68 mid, A#=70) on the lead
s = base_song()
s["tracks"][0]["notes"][0] = mknote(0, 63, ln=1.5)     # strong beat, long: sour
s["tracks"][0]["notes"][4] = mknote(4, 70, ln=1.0)     # A# long: sour
s["tracks"][0]["notes"][8] = mknote(8, 68, ln=1.0)     # G# long: leading tone! pardoned in minor
v = MC.court_key(s, "pop")
ok(not v["ok"], "planted sours fail the court")
ok(v["sour"] == 2, f"exactly 2 sour (G# leading tone pardoned): {v['sour']}")
names = {o["name"] for o in v["offenders"]}
ok("D#4" in names and "A#4" in names, f"offenders named: {names}")
edits = MC.heal_key(s, "pop")
ok(len(edits) == 2, f"heal fixed 2: {edits}")
v2 = MC.court_key(s, "pop")
ok(v2["ok"] and v2["sour"] == 0, "healed song passes")

# SUPERMODE LAW (R-1): mixture degrees (b3 vs major) are idiom — convicted
# only when LONG + STRONG-BEAT + against the SOUNDING chord. Blues pardons
# them unconditionally.
s = base_song()
s["key"] = "A major"
s["chords"] = [{"bar": 1, "chord": "A"}, {"bar": 2, "chord": "A"}]
s["tracks"] = [s["tracks"][0], s["tracks"][2]]      # lead + kick only
s["tracks"][0]["notes"] = [mknote(i, p, ln=1.5) for i, p in
                           enumerate([72, 69, 73, 74, 76, 72, 69, 68])]
# 72=C nat at beat 0 (b3, STRONG+long vs A chord = CONVICTED in pop);
# the other C sits weak (idiom, forgiven); 68=G# in scale
vb = MC.court_key(s, "blues")
vp = MC.court_key(copy.deepcopy(s), "pop")
ok(vb["sour"] == 0, f"blues pardons blue notes unconditionally ({vb['sour']})")
ok(vp["sour"] >= 1, f"pop convicts long strong-beat b3 against the chord ({vp['sour']})")
# same b3 SHORT and off-beat = idiom, forgiven even in pop
s2 = base_song()
s2["key"] = "A major"
s2["chords"] = [{"bar": 1, "chord": "A"}]
s2["tracks"] = [s2["tracks"][0], s2["tracks"][2]]   # lead + kick only
s2["tracks"][0]["notes"] = [mknote(0, 69, 1.0), mknote(1.5, 72, 0.25),
                            mknote(1.75, 74, 0.5), mknote(3, 76, 1.0)]
ok(MC.court_key(s2, "pop")["sour"] == 0,
   "short weak-beat mixture forgiven (supermode)")

# THE AVOID-NOTE LAW (R-1 jazz): sustained strong-beat semitone-above-chord-
# tone convicts even under the generous allowance; short passing use is fine
s = base_song()
s["key"] = "C major"
s["chords"] = [{"bar": 1, "chord": "Cmaj7"}]
s["tracks"] = [{"name": "sax", "source": {"id": "sax"}, "notes": [
    mknote(0, 65, ln=2.0),      # F held on the ONE over Cmaj7 = THE avoid note
    mknote(2, 64, ln=1.0)]}]
v = MC.court_key(s, "jazz")
ok(v["sour"] == 1 and v["offenders"][0].get("law") == "avoid-note",
   f"jazz avoid-note convicted: {v['offenders']}")
s["tracks"][0]["notes"][0] = mknote(1.5, 65, ln=0.25)   # passing F = idiom
v = MC.court_key(s, "jazz")
ok(v["sour"] == 0, f"short passing F over Cmaj7 forgiven: {v.get('offenders')}")

# chromatic passing forgiven: short weak-beat stepwise
s = base_song()
s["tracks"][0]["notes"] = [mknote(0, 69, 0.5), mknote(0.5, 70, 0.25),
                           mknote(0.75, 71, 0.5), mknote(2, 72, 1.0)]
v = MC.court_key(s, "pop")
ok(v["ok"], f"chromatic passing A-A#-B forgiven ({v})")

# inferred key when undeclared
s = base_song()
del s["key"]
v = MC.court_key(s, "pop")
ok(v["key_src"] == "inferred" and "minor" in v["key"], f"key inferred: {v['key']}")

# ---------------- P4 POCKET COURT ----------------
s = base_song()
v = MC.court_pocket(s, "pop")
ok(v["ok"], f"clean song passes pocket court ({v['stragglers']}, {v['shadow_pairs']})")

# grid stragglers: 2 lead notes nudged 0.04 beats (sloppy, not intent)
s = base_song()
s["tracks"][0]["notes"][3]["start"] = 3.04
s["tracks"][0]["notes"][7]["start"] = 7.05
v = MC.court_pocket(s, "pop")
ok(len(v["stragglers"]) == 2, f"stragglers caught: {v['stragglers']}")
MC.heal_pocket(s, "pop", v)
v2 = MC.court_pocket(s, "pop")
ok(v2["ok"], "stragglers healed to grid")
ok(abs(s["tracks"][0]["notes"][3]["start"] - 3.0) < 1e-9, "3.04 -> 3.0")

# engine swing positions are NOT stragglers (odd 16ths late by law)
s = base_song()
s["swing"] = {"grid": "16th", "amount": 0.58}
sw_off = (0.58 - 0.5) * 2.0 * 0.25
s["tracks"][0]["notes"] = [mknote(b * 0.5, 69) for b in range(16)]  # 8th grid
for i, n in enumerate(s["tracks"][0]["notes"]):
    if (round(n["start"] / 0.25)) % 2 == 1:
        n["start"] += sw_off          # what the engine itself would play late
v = MC.court_pocket(s, "pop")
ok(not v["stragglers"], f"engine-lawful swing not flagged: {v['stragglers']}")

# humanized track (many off-grid) is performance intent — exempt
s = base_song()
for i, n in enumerate(s["tracks"][0]["notes"]):
    n["start"] = float(n["start"]) + (0.03 + 0.005 * (i % 5))
v = MC.court_pocket(s, "pop")
ok(not any(x["track"] == "lead" for x in v["stragglers"]),
   "fully-humanized lead exempt (intent, not sloppiness)")

# band interplay is NOT a shadow pair: parts that often lock EXACTLY and
# drift elsewhere are push-pull idiom (eval_blues guitars class)
s = base_song()
import random as _r
_r.seed(7)
lead_starts = [float(n["start"]) for n in s["tracks"][0]["notes"]]
s["tracks"][1]["notes"] = (
    [mknote(x, 55) for x in lead_starts[:8]]                  # locks exactly
    + [mknote(x + 0.07, 57) for x in lead_starts[8:]])        # drifts elsewhere
v = MC.court_pocket(s, "blues")
ok(not v["shadow_pairs"], f"band interplay exempt (exact locks): {v['shadow_pairs']}")

# shadow pair: keys shadow the lead but land 0.06 late (untitled_46 class)
s = base_song()
s["tracks"][1]["notes"] = [mknote(float(n["start"]) + 0.06, int(n["pitch"]) - 12)
                           for n in s["tracks"][0]["notes"]]
v = MC.court_pocket(s, "pop")
ok(v["shadow_pairs"], f"keys-vs-lead drift caught: {v['shadow_pairs']}")
MC.heal_pocket(s, "pop", v)
v2 = MC.court_pocket(s, "pop")
ok(not v2["shadow_pairs"], "shadow pair healed to alignment")
la = sorted(float(n["start"]) for n in s["tracks"][0]["notes"])
lb = sorted(float(n["start"]) for n in s["tracks"][1]["notes"])
ok(la == lb, "follower now lands WITH the leader")

# ---------------- P8 INSTRUCTION COURT ----------------
s = base_song()          # 4 bars @120 = 8s
v = MC.court_instruction("make a full 10 minute goa track", s)
ok(not v["ok"] and v["unmet"][0]["kind"] == "duration", f"10-minute contract unmet: {v}")
big = base_song()
big["lengthBars"] = 300  # 300 bars @120 = 600s
v = MC.court_instruction("make a full 10 minute goa track", big)
ok(v["ok"], f"600s satisfies 10 minutes: {v}")
v = MC.court_instruction("16 bars please", s)
ok(not v["ok"], "16-bar ask vs 4-bar song unmet")
v = MC.court_instruction("dark trap at 142 with an 808", {**s, "bpm": 142,
    "tracks": s["tracks"] + [{"name": "808 sub", "source": {"id": "sub_808"}, "notes": [mknote(0, 36)]}]})
ok(v["ok"], f"bpm+element contract met: {v}")
v = MC.court_instruction("dark trap at 142 with an 808", s)
ok(not v["ok"] and any(c["kind"] in ("bpm", "element") for c in v["unmet"]),
   "wrong bpm + missing 808 caught")
v = MC.court_instruction("a pop song in F minor", {**s, "key": "F minor"})
ok(v["ok"], "key contract met")
v = MC.court_instruction("a pop song in F minor", s)
ok(not v["ok"], "key contract A minor != F minor")
v = MC.court_instruction("make a new pop hit with real word vocals", s)
ok(not v["ok"] and v["unmet"][0]["kind"] == "vocals", "vocal demand unmet on instrumental")
sv = copy.deepcopy(s)
sv["lyrics"] = [{"beat": 0, "text": "we"}]
sv["tracks"].append({"name": "lead_vocal", "source": {"kind": "audio"},
                     "audioClips": [{"file": "x_vocal.wav", "startBeat": 0}]})
v = MC.court_instruction("make a new pop hit with real word vocals", sv)
ok(v["ok"], "vocal demand met with staged lyrics + vocal lane")
v = MC.court_instruction("2:20 long with vocals", {**sv, "lengthBars": 70})  # 70*4*0.5s=140s
ok(all(c["ok"] for c in v["contracts"] if c["kind"] == "duration"),
   f"2:20 parsed and met at 140s: {v['contracts']}")

# ---------------- aggregate + corpus sanity ----------------
s = base_song()
s["tracks"][0]["notes"][0] = mknote(0, 63, ln=1.5)
out = MC.run_courts(s, "pop", ask="4 bars in A minor", heal=True)
ok(out["heals"]["key"], "aggregate healed key")
ok(out["key_after"]["ok"], "aggregate re-court green after heal")
ok(out["instruction"]["ok"], "aggregate instruction contracts met")

# corpus truth: the WITNESS LAW must silence imported-sketch songs; genuinely
# sour agent compositions (demo_track's F-minor lead with A/B naturals — the
# class Chezy screamed about) MUST stay flagged. Both directions asserted.
flagged, checked, names = 0, 0, []
paths = [p for p in sorted(glob.glob(os.path.join(ROOT, "songs", "*.json")))
         if not os.path.basename(p).startswith(("_", "."))][:40]
for path in paths:
    try:
        song = json.load(open(path))
    except Exception:
        continue
    if not isinstance(song, dict) or not song.get("tracks"):
        continue
    checked += 1
    v = MC.court_key(song, "")
    if not v.get("ok", True):
        flagged += 1
        names.append(os.path.basename(path))
print(f"[corpus] key court on {checked} real songs: {flagged} flagged: {names}")
ok(checked >= 10, f"corpus sweep covered {checked}")
ok(flagged <= checked // 3,
   f"witness+fx laws hold ({flagged}/{checked} flagged)")
# the known-sour reference stays caught (true positive, Chezy-class)
demo = json.load(open(os.path.join(ROOT, "songs", "demo_track.json")))
ok(not MC.court_key(demo, "")["ok"], "demo_track's sour F-minor lead stays caught")
# imported-sketch songs are witnesses, never defendants
imp = os.path.join(ROOT, "songs", "entheogenic-aranyanyara_2.json")
if os.path.exists(imp):
    vi = MC.court_key(json.load(open(imp)), "")
    ok(vi["ok"], f"imported sketches exempt under the witness law ({vi.get('sour')})")

print(f"MUSIC COURT BATTERY PASS — {N[0]} checks green")
