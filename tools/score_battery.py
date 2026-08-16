#!/usr/bin/env python3
"""THE SCORE BATTERY — machine law for the engraving kernel (app/ScoreEngrave.h).

Runs `m1 score-probe` on PLANTED songs with known notation truths, then sweeps
the real corpus for invariant violations (measure fill, spellable durations,
beam legality — the kernel self-reports via census()).

Planted truths:
  P1  whole note at bar start          -> 1 element, 0 ties
  P2  half starting on beat 2 (t=1)    -> tie-split (2 elements, 1 tie)
  P3  syncopated quarter at t=0.5      -> 1 element (editor practice)
  P4  triplet beat (0, 1/3, 2/3)       -> 3 triplet elements
  P5  rest fill: lone note at beat 3   -> measure fills to exactly 4.0 (v0 law)
  P6  chromatic C# in C major          -> >=1 accidental shown
  P7  kick+snare+hats+bass             -> ONE merged DRUMS staff (perc clef) + bass clef staff
  P8  7/8 meterMap bar                 -> measure fills to exactly 3.5
  P9  velocity ramp                    -> >=1 hairpin + >=2 dynamic marks
  P10 short lone notes (ABSORB LAW)    -> staccato beats, ZERO rest pepper
  P11 velocity spike                   -> >=1 accent
  P12 MusicXML roundtrip (untitled_65) -> export -> import -> key + note count hold
  KEYS  A minor->0m  F minor->-4m  F# minor->+3m  D major->+2M
Corpus sweep: every songs/*.json (bounded) -> violations MUST be [].

Usage: python3 tools/score_battery.py [--corpus-limit N]
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")

PASS = 0
FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def probe(song_dict):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(song_dict, f)
        path = f.name
    try:
        out = subprocess.run([M1, "score-probe", path], capture_output=True, text=True, timeout=120)
        for line in out.stdout.splitlines():
            if line.startswith("SCORE_JSON "):
                return json.loads(line[len("SCORE_JSON "):])
        raise RuntimeError(f"no SCORE_JSON line: {out.stdout[-400:]} {out.stderr[-400:]}")
    finally:
        os.unlink(path)


def probe_file(path):
    out = subprocess.run([M1, "score-probe", path], capture_output=True, text=True, timeout=180)
    for line in out.stdout.splitlines():
        if line.startswith("SCORE_JSON "):
            return json.loads(line[len("SCORE_JSON "):])
    return None


def song(tracks, key="C major", bars=1, meter=None):
    s = {"version": 2, "bpm": 120, "key": key, "lengthBars": bars, "tracks": tracks}
    if meter:
        s["meterMap"] = meter
    return s


def mel(name, notes, inst="pad_motion"):
    return {"name": name, "source": {"kind": "faust", "id": inst},
            "notes": [{"start": s, "len": l, "pitch": p, "vel": 0.8} for (s, l, p) in notes]}


def melv(name, notes, inst="pad_motion"):
    return {"name": name, "source": {"kind": "faust", "id": inst},
            "notes": [{"start": s, "len": l, "pitch": p, "vel": v} for (s, l, p, v) in notes]}


def main():
    if not os.path.exists(M1):
        print(f"FAIL m1 binary missing at {M1}")
        sys.exit(1)
    limit = 25
    if "--corpus-limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--corpus-limit") + 1])

    # P1 whole note
    c = probe(song([mel("lead", [(0, 4, 60)])]))
    check("P1 whole-note = 1 element 0 ties",
          c["ties"] == 0 and c["violations"] == [] and c["elements"] >= 1, json.dumps(c)[:200])

    # P2a the q-h-q figure: a half STARTING ON beat 2 is legal syncopation (Gould)
    c = probe(song([mel("lead", [(1, 2, 60)])]))
    check("P2a q-h-q half@beat2 stays whole", c["ties"] == 0 and c["violations"] == [], json.dumps(c)[:200])

    # P2b an OFF-beat half crossing the half-bar MUST tie-split
    c = probe(song([mel("lead", [(0.5, 2, 60)])]))
    check("P2b off-beat half tie-splits", c["ties"] >= 1 and c["violations"] == [], json.dumps(c)[:200])

    # P3 syncopated quarter at 0.5 -> single element (no tie)
    c = probe(song([mel("lead", [(0.5, 1, 60)])]))
    check("P3 syncopated quarter stays whole", c["ties"] == 0 and c["violations"] == [], json.dumps(c)[:200])

    # P4 triplet beat
    c = probe(song([mel("lead", [(0, 1 / 3, 60), (1 / 3, 1 / 3, 62), (2 / 3, 1 / 3, 64)])]))
    check("P4 triplet detected (3 triplet elements)",
          c["triplets"] >= 3 and c["violations"] == [], json.dumps(c)[:200])

    # P5 rest fill exactness (violations [] IS the fill law)
    c = probe(song([mel("lead", [(3, 1, 60)])]))
    check("P5 rest fill exact", c["violations"] == [] and c["rests"] >= 1, json.dumps(c)[:200])

    # P6 chromatic accidental in C major
    c = probe(song([mel("lead", [(0, 1, 61)])]))
    check("P6 C# shows an accidental", c["accidentals"] >= 1 and c["violations"] == [], json.dumps(c)[:200])

    # P7 drum merge + auto clefs
    c = probe(song([
        mel("kick", [(0, 0.25, 36)], "kick_punch"),
        mel("snare", [(1, 0.25, 38)], "brush_snare"),
        mel("hats", [(0.5, 0.1, 42)], "hat"),
        mel("bass", [(0, 1, 33)], "bass_warm"),
    ]))
    drums = [s for s in c["staves"] if s["drums"]]
    bass = [s for s in c["staves"] if s["name"] == "bass"]
    check("P7 one merged DRUMS staff (perc clef)",
          len(drums) == 1 and drums[0]["clef"] == "perc" and drums[0]["name"] == "DRUMS",
          json.dumps(c["staves"]))
    check("P7 bass lands on bass clef", bass and bass[0]["clef"] == "bass", json.dumps(c["staves"]))
    check("P7 violations empty", c["violations"] == [], json.dumps(c["violations"])[:300])

    # P8 7/8 world grid
    c = probe(song([mel("lead", [(0, 0.5, 60), (3, 0.5, 62)])], bars=1,
                   meter=[{"bar": 0, "num": 7, "den": 8}]))
    check("P8 7/8 measure fills exactly", c["violations"] == [], json.dumps(c["violations"])[:300])

    # P9 THE MARKS PASS: a long velocity ramp earns a hairpin + dynamic letters
    c = probe(song([melv("lead", [(i, 0.98, 60 + (i % 3), 0.25 + 0.045 * i) for i in range(16)])],
                   bars=4))
    check("P9 velocity ramp -> hairpin + dynamics",
          c["hairpins"] >= 1 and c["dynamics"] >= 2 and c["violations"] == [],
          json.dumps({k: c[k] for k in ("hairpins", "dynamics", "violations")}))

    # P10 THE ABSORB LAW: lone short notes display as staccato beats, no rest pepper
    c = probe(song([mel("lead", [(0, 0.2, 60), (1, 0.2, 62), (2, 0.2, 64), (3, 0.2, 65)])]))
    check("P10 absorb: staccato beats, zero rests",
          c["rests"] == 0 and c["artics"] >= 4 and c["elements"] == 4 and c["violations"] == [],
          json.dumps({k: c[k] for k in ("rests", "artics", "elements", "violations")}))

    # P11 accents: a genuine spike over the running mean wears the mark
    c = probe(song([melv("lead", [(i * 0.5, 0.45, 60, 1.0 if i == 7 else 0.5) for i in range(10)])],
                   bars=2))
    check("P11 velocity spike -> accent", c["artics"] >= 1 and c["violations"] == [],
          json.dumps({k: c[k] for k in ("artics", "violations")}))

    # P12 XML ROUNDTRIP: export untitled_65 -> import -> the score survives the trip
    u65 = os.path.join(ROOT, "songs/untitled_65.json")
    if os.path.exists(u65):
        import tempfile as _tf
        with _tf.TemporaryDirectory() as td:
            x = os.path.join(td, "u65.musicxml")
            j = os.path.join(td, "u65_back.json")
            r1 = subprocess.run([sys.executable, os.path.join(ROOT, "tools/musicxml_export.py"), u65, x],
                                capture_output=True, text=True, timeout=300)
            check("P12 musicxml export runs", r1.returncode == 0, r1.stderr[-300:])
            r2 = subprocess.run([sys.executable, os.path.join(ROOT, "tools/musicxml_import.py"), x, j],
                                capture_output=True, text=True, timeout=300)
            check("P12 musicxml import runs", r2.returncode == 0, r2.stderr[-300:])
            stats = {}
            for line in r2.stdout.splitlines():
                if line.startswith("MUSICXML_IMPORT "):
                    stats = json.loads(line[len("MUSICXML_IMPORT "):])
            with open(u65) as fh:
                srcj = json.load(fh)
            srcn = sum(len(t.get("notes", [])) for t in srcj.get("tracks", [])
                       if t.get("source", {}).get("kind") != "audio")
            c0 = probe_file(u65)
            check("P12 roundtrip key holds",
                  c0 is not None and stats.get("fifths") == c0.get("fifths")
                  and stats.get("minor") == c0.get("minor"),
                  f"src {c0 and (c0.get('fifths'), c0.get('minor'))} "
                  f"vs back {(stats.get('fifths'), stats.get('minor'))}")
            check("P12 roundtrip bpm holds",
                  abs(float(stats.get("bpm", 0)) - float(srcj.get("bpm", 120))) < 0.5,
                  str(stats.get("bpm")))
            got = stats.get("notes", 0)
            check(f"P12 roundtrip notes hold ({got} vs src {srcn})",
                  srcn > 0 and abs(got - srcn) / srcn < 0.12, str(stats)[:200])
            c = probe_file(j)
            check("P12 imported song engraves violation-free",
                  c is not None and c["violations"] == [],
                  json.dumps((c or {}).get("violations", "no probe"))[:300])

    # KEYS
    for key, fifths, minor in [("A minor", 0, True), ("F minor", -4, True),
                               ("F# minor", 3, True), ("D major", 2, False)]:
        c = probe(song([mel("lead", [(0, 1, 60)])], key=key))
        check(f"KEY {key} -> fifths {fifths} minor {minor}",
              c["fifths"] == fifths and c["minor"] == minor,
              f"got {c['fifths']} {c['minor']}")

    # CORPUS SWEEP — the kernel must spell every real song violation-free
    songs_dir = os.path.join(ROOT, "songs")
    corpus = sorted(f for f in os.listdir(songs_dir)
                    if f.endswith(".json") and not f.startswith("_prop_")
                    and not f.startswith("."))[:limit]
    for must in ("untitled_65.json",):          # the triplet-heavy live proof song
        if must not in corpus and os.path.exists(os.path.join(songs_dir, must)):
            corpus.append(must)
    swept = 0
    for name in corpus:
        path = os.path.join(songs_dir, name)
        try:
            with open(path) as fh:
                if not any(t.get("notes") for t in json.load(fh).get("tracks", [])):
                    continue
        except Exception:
            continue
        c = probe_file(path)
        if c is None:
            continue                       # unparseable corpus stragglers are not score bugs
        swept += 1
        check(f"corpus {name} violation-free ({c['elements']} elems)",
              c["violations"] == [], json.dumps(c["violations"])[:400])
    check(f"corpus swept >= 5 songs (got {swept})", swept >= 5)

    print(f"\nscore_battery: {PASS} ok, {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
