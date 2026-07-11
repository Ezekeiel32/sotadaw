#!/usr/bin/env python3
"""SUGGEST_CHORDS battery — theory assertions, grammar law, the full circle.

Pure (no KG required, KG-less prior asserted empty), deterministic, plus one
subprocess leg: suggest -> reharm --to (the color_one rewrite) -> chordvote
reads the target back at root+quality (a 3-voice source can't witness a 7th).
"""
import copy, glob, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from suggest_chords import (suggest, roman_of, func_of, vl_cost, FLOW,
                            genre_degree_prior, classify_cadence)
from reharm import parse_chord
from chordvote import chord_map

N = 0


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        print(f"FAIL {N} — {msg}")
        sys.exit(1)
    print(f"ok {N} — {msg}")


def axis_song():
    song = {"key": "C major", "bpm": 120, "lengthBars": 8,
            "tracks": [{"name": "keys", "notes": []}, {"name": "bass", "notes": []}]}
    prog = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
    roots = [0, 9, 5, 7]
    for rep in range(2):
        for bar in range(4):
            b = (rep * 4 + bar) * 4.0
            for p in prog[bar]:
                song["tracks"][0]["notes"].append({"start": b, "len": 3.9, "pitch": p, "vel": 0.9})
            song["tracks"][1]["notes"].append({"start": b, "len": 3.5, "pitch": 36 + roots[bar], "vel": 0.9})
    return song


def minor_song():
    song = {"key": "A minor", "bpm": 120, "lengthBars": 4,
            "tracks": [{"name": "keys", "notes": []}, {"name": "bass", "notes": []}]}
    prog = [[57, 60, 64], [53, 57, 60], [60, 64, 67], [55, 59, 62]]   # Am F C G
    roots = [9, 5, 0, 7]
    for bar in range(4):
        b = bar * 4.0
        for p in prog[bar]:
            song["tracks"][0]["notes"].append({"start": b, "len": 3.9, "pitch": p, "vel": 0.9})
        song["tracks"][1]["notes"].append({"start": b, "len": 3.5, "pitch": 36 + roots[bar], "vel": 0.9})
    return song


out = suggest(axis_song(), k=12)
ok(out["available"] and out["cycle_bars"] == 4 and out["progression"] == ["C", "Am", "F", "G"],
   "axis song: 8 bars compress to the 4-bar cycle C Am F G")
ok(out["roman"] == ["I", "vi", "IV", "V"], "roman numerals I vi IV V in C major")
ok(out["cadence"] == "authentic (V→I)", "wrap cadence classified authentic")
s = {x["slot"]: x for x in out["slots"]}
alts3 = {a["chord"]: a for a in s[3]["alts"]}
ok("Db7" in alts3 and any("tritone" in w for w in alts3["Db7"]["why"]),
   "tritone sub Db7 offered on the V slot with the tritone WHY")
ok("Bb7" in alts3 and any("backdoor" in w for w in alts3["Bb7"]["why"]),
   "backdoor dominant Bb7 offered heading into I")
alts2 = {a["chord"]: a for a in s[2]["alts"]}
ok("D7" in alts2 and any("V7 of next" in w for w in alts2["D7"]["why"]),
   "secondary dominant D7 (V7 of G) offered on the IV slot")
ok("Fm" in {a["chord"] for x in out["slots"] for a in x["alts"]}
   and any("mixture" in w for x in out["slots"] for a in x["alts"]
           if a["chord"] == "Fm" for w in a["why"]),
   "borrowed iv (Fm) offered with the mode-mixture WHY")
for x in out["slots"]:
    for a in x["alts"]:
        parse_chord(a["chord"])
    sc = [a["score"] for a in x["alts"]]
    ok(sc == sorted(sc, reverse=True), f"slot {x['slot']}: alts grammar-legal and sorted by score")
ok(json.dumps(suggest(axis_song(), k=12), sort_keys=True)
   == json.dumps(out, sort_keys=True), "deterministic: two runs byte-identical")

m = suggest(minor_song(), k=12)
ok(m["roman"] == ["i", "VI", "III", "VII"], "minor roman i VI III VII in A minor")
ok(m["cadence"].startswith("subtonic close"), "VII→i wrap classified subtonic close")
ok(any(a["chord"] == "E7" and any("harmonic-minor" in w for w in a["why"])
       for x in m["slots"] for a in x["alts"]),
   "harmonic-minor V7 (E7) offered in A minor")

ok(vl_cost(["C", "Am", "C"]) < vl_cost(["C", "Gb", "C"]),
   "voice-leading kernel: Am nearer C than Gb (shared tones move less)")
ok(FLOW[("D", "S")] < FLOW[("S", "D")], "retrogression D→S scored below S→D")
ok(func_of("G", 0, "major") == "D" and func_of("F", 0, "major") == "S"
   and func_of("Am", 0, "major") == "T" and func_of("Db7", 0, "major") == "D",
   "function map: G=D F=S Am=T, chromatic dom7 counts dominant")
ok(roman_of("Db7", 0, "major") == "bII7", "chromatic roman spelling bII7")
ok(classify_cadence("G", "Am", 0, "major") == "deceptive (V→vi)", "V→vi classified deceptive")

ok(suggest({"tracks": []}).get("available") is False, "empty song degrades clean (available:false)")
one = {"key": "C major", "bpm": 120, "lengthBars": 2, "tracks": [
    {"name": "keys", "notes": [{"start": b * 4.0, "len": 3.9, "pitch": p, "vel": 0.9}
                               for b in range(2) for p in (60, 64, 67)]}]}
o1 = suggest(one, k=6)
ok(o1["available"] and o1["cycle_bars"] == 1 and len(o1["slots"][0]["alts"]) > 0
   and not any(r["name"].startswith("rotation") for r in o1["rewrites"]),
   "single-chord song: 1-slot cycle, alts offered, no rotations")
ok(genre_degree_prior("nonexistent_genre_xyz_2026", 0, "major") == {},
   "genre prior degrades to {} (unknown genre / KG down)")

rots = [r for r in out["rewrites"] if r["name"].startswith("rotation")]
ok(all(sorted(r["chords"]) == sorted(out["progression"]) and r["chords"] != out["progression"]
       for r in rots) and len(rots) == 2, "rotations are true rotations of the cycle")
color = [r for r in out["rewrites"] if r["name"] == "color_one"]
ok(len(color) == 1 and sum(a != b for a, b in zip(color[0]["chords"], out["progression"])) == 1
   and "--to" in color[0]["reharm"], "color_one swaps exactly one slot and ships a reharm line")

crates = sorted(glob.glob(os.path.join(ROOT, "songs", "crate", "*.json")))
ok(len(crates) > 0, "crate shopfront present for the real-song leg")
lived = 0
for c in crates:
    try:
        song = json.load(open(c))
        r = suggest(song, k=3)
        if r.get("available") and r["slots"] and r["slots"][0]["alts"]:
            lived += 1
    except Exception:
        pass
ok(lived >= 1, f"advisor lives on real crate songs ({lived}/{len(crates)} yield suggestions)")

# THE FULL CIRCLE: suggest -> reharm --to (color_one) -> chordvote reads it back
scratch = "_sugg_bat"
path = os.path.join(ROOT, "songs", scratch + ".json")
json.dump(axis_song(), open(path, "w"), indent=1)
try:
    target = color[0]["chords"]
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "reharm.py"),
                        scratch, "--to", ",".join(target), "--write"],
                       capture_output=True, text=True, cwd=ROOT)
    ok(r.returncode == 0, f"reharm applies the suggested rewrite (rc={r.returncode})")
    reharmed = json.load(open(path))
    voted = [c["chord"] for c in chord_map(reharmed)][:4]
    strip = lambda ch: ch.rstrip("7")
    ok([strip(v) for v in voted] == [strip(t) for t in target],
       f"FULL CIRCLE: chordvote reads the suggested progression back ({voted} ~ {target})")
finally:
    if os.path.exists(path):
        os.remove(path)

print(f"PASS {N}/{N} suggest_chords battery")
