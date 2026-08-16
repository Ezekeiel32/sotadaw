#!/usr/bin/env python3
"""THE RECORD COURT battery (A4-T1, docs/SPEC_TRANSCENDENCE.md). Pure."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import record_court as rc

N = [0, 0]


def ok(cond, msg):
    N[0] += 1
    if cond:
        print(f"  ok {N[0]:2d}: {msg}")
    else:
        N[1] += 1
        print(f"FAIL {N[0]:2d}: {msg}")


def song(key, bpm, bars=64, lead=None, name="lead"):
    tracks = [{"name": "kick", "notes": [{"start": 0.0, "pitch": 36,
                                          "vel": 0.9, "len": 0.5}]}]
    if lead:
        notes = [{"start": float(i), "pitch": p, "vel": 0.8, "len": 0.5}
                 for i, p in enumerate(lead)]
        tracks.append({"name": name, "notes": notes})
    return {"key": key, "bpm": bpm, "lengthBars": bars, "tracks": tracks}


def main():
    # key parsing + distance table
    ok(rc.parse_key("A minor") == (9, True), "parse 'A minor'")
    ok(rc.parse_key("F# major") == (6, False), "parse 'F# major'")
    ok(rc.parse_key("garbage") is None, "unparseable key = honest None")
    ok(rc.key_distance((9, True), (0, False)) == 0.5,
       "Am -> C = relative (0.5)")
    ok(rc.key_distance((0, False), (0, True)) == 0.5, "C -> Cm = parallel")
    ok(rc.key_distance((0, False), (7, False)) == 1.0, "C -> G = 1 fifth")
    ok(rc.key_distance((0, False), (6, False)) == 6.0, "C -> F# = tritone 6")

    # smooth record passes; cold jump flags
    smooth = [song("A minor", 120, lead=[60, 62, 64, 65, 67]),
              song("C major", 122, lead=[60, 62, 64, 65, 67]),
              song("G major", 124, lead=[55, 57, 59, 60, 62])]
    v = rc.court_record(smooth, ["one", "two", "three"])
    ok(v["key_journey"]["ok"], "Am->C->G journey smooth")
    ok(v["tempo_arc"]["ok"] and v["tempo_arc"]["shape"] == "rise",
       "gentle rise arc classified")
    cold = [song("Eb minor", 120), song("A major", 121)]
    vc = rc.court_record(cold, ["a", "b"])
    ok(not vc["key_journey"]["ok"]
       and "cold key jump" in vc["key_journey"]["flags"][0],
       "Ebm -> A flags a cold jump (3 fifths between homes)")

    # tempo: whiplash vs musical ratio
    whip = [song("C major", 120), song("C major", 85)]
    vw = rc.court_record(whip, ["a", "b"])
    ok(not vw["tempo_arc"]["ok"], "120->85 (no musical ratio) = whiplash flag")
    half = [song("C major", 140), song("C major", 70)]
    vh = rc.court_record(half, ["a", "b"])
    ok(vh["tempo_arc"]["ok"], "140->70 halftime hop is musical, passes")

    # thread: shared motif detected across tracks; absence honest
    motif = [64, 67, 65, 62, 60, 64, 67, 65, 62, 60]
    threaded = [song("C major", 120, lead=motif),
                song("A minor", 120, lead=[52, 55] + motif),
                song("F major", 118, lead=[40, 41, 43, 45, 40, 41, 43, 45])]
    vt = rc.court_thread(threaded, ["one", "two", "three"])
    ok(vt["has_thread"] and any(p["a"] == "one" and p["b"] == "two"
                                for p in vt["pairs"]),
       "shared interval motif found between tracks one+two")
    bare = [song("C major", 120, lead=[60, 61, 63, 66, 70]),
            song("C major", 120, lead=[60, 59, 57, 54, 50])]
    vb = rc.court_thread(bare, ["a", "b"])
    ok(not vb["has_thread"] and "reprise" in vb["note"],
       "no thread -> honest advisory, never a hard fail")
    ok(vb["ok"], "thread court never hard-fails a record")

    # drum-only songs: no crash, honest empty intervals
    drums = [song("C major", 120), song("C major", 120)]
    vd = rc.court_thread(drums, ["a", "b"])
    ok(not vd["has_thread"], "drum-only record: no fake thread")

    # pacing: back-to-back marathons advise
    lp = [song("C major", 120, bars=200), song("C major", 120, bars=200),
          song("C major", 120, bars=32)]
    vp = rc.court_pacing(lp, ["one", "two", "three"])
    ok(not vp["ok"] and "marathons" in vp["flags"][0],
       f"two >6m tracks adjacent advise ({vp['minutes']})")

    # degenerate: single-track record skips honestly
    ok("skipped" in rc.court_record([song("C major", 120)], ["solo"]),
       "a 1-track record skips (needs >=2)")

    print(f"\nrecord_battery: {N[0] - N[1]}/{N[0]} PASS"
          + (f", {N[1]} FAIL" if N[1] else ""))
    return 1 if N[1] else 0


if __name__ == "__main__":
    sys.exit(main())
