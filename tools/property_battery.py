#!/usr/bin/env python3
"""THE PROPERTY BATTERY — wave 90 (r-32 item 184): Hypothesis fuzzes
RANDOM song.json documents through the court/op stack. The properties
are the house laws themselves:

  P1  no court CRASHES on any generated song (fail-open is law)
  P2  every court verdict is a dict carrying its contract keys
  P3  the metamorphic transforms preserve note counts + song length
  P4  heals never make a song unparseable (json round-trip) and never
      touch MUTED lanes' notes
  P5  flow's coverage kernel: total sounding beats never exceeds the
      grid, never goes negative

pluginval stays a named CI remainder (external binary, not on this
box). Run: .venv/bin/python tools/property_battery.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hypothesis import given, settings, strategies as st  # noqa: E402

FAILS = []
NAMES = ("kick", "snare", "hat", "bass", "pad_warm", "lead", "keys",
         "vocal_lead", "riser", "gtr")

note = st.fixed_dictionaries({
    "start": st.floats(0, 256, allow_nan=False, allow_infinity=False),
    "len": st.floats(0.01, 16, allow_nan=False, allow_infinity=False),
    "pitch": st.integers(0, 127),
    "vel": st.integers(1, 127),
})
track = st.fixed_dictionaries({
    "name": st.sampled_from(NAMES),
    "muted": st.booleans(),
    "gainDb": st.floats(-24, 6, allow_nan=False),
    "pan": st.floats(-1, 1, allow_nan=False),
    "notes": st.lists(note, max_size=40),
})
section = st.fixed_dictionaries({
    "name": st.sampled_from(("intro", "verse", "chorus", "build",
                             "drop", "bridge", "outro")),
    "startBar": st.integers(0, 60),
})
song_st = st.fixed_dictionaries({
    "bpm": st.floats(40, 220, allow_nan=False),
    "lengthBars": st.integers(1, 64),
    "key": st.sampled_from(("C major", "A minor", "F# minor", "", None)),
    "sections": st.lists(section, max_size=8),
    "tracks": st.lists(track, max_size=8),
})


def check(name, fn):
    try:
        fn()
        print(f"[PASS] {name}")
    except Exception as e:
        print(f"[FAIL] {name} — {str(e)[:220]}")
        FAILS.append(name)


N = int(os.environ.get("PROP_N", "60"))


def p1_courts_never_crash():
    import music_court as MC
    import flow_court as FC
    import movement_court as MV
    import structure_court as SC
    import form_court as FCT
    import tension as TN

    @settings(max_examples=N, deadline=None)
    @given(song_st)
    def run(song):
        MC.court_key(song, "pop")
        FC.court_flow(song)
        MV.court_movement(song)
        SC.court_structure(song, "pop")
        FCT.court_ritual(song, "trap")
        TN.court_trend(song, "edm")
    run()


def p2_contract_keys():
    import flow_court as FC

    @settings(max_examples=N, deadline=None)
    @given(song_st)
    def run(song):
        v = FC.court_flow(song)
        assert isinstance(v, dict) and "court" in v and "ok" in v
        assert isinstance(v.get("convictions", []), list)
    run()


def p3_transforms_preserve():
    import metamorphic_court as MM

    @settings(max_examples=N, deadline=None)
    @given(song_st, st.integers(-6, 6))
    def run(song, semis):
        t = MM.transpose(song, semis)
        assert sum(len(x["notes"]) for x in t["tracks"]) == \
            sum(len(x["notes"]) for x in song["tracks"])
        assert t["lengthBars"] == song["lengthBars"]
        p = MM.pan_mirror(song)
        assert len(p["tracks"]) == len(song["tracks"])
    run()


def p4_heals_stay_lawful():
    import flow_court as FC
    import movement_court as MV

    @settings(max_examples=N, deadline=None)
    @given(song_st)
    def run(song):
        muted_before = {id(t): len(t["notes"]) for t in song["tracks"]
                        if t.get("muted")}
        v = FC.court_flow(song)
        if v.get("convictions"):
            FC.heal_flow(song, v)
        MV.heal_movement(song, MV.court_movement(song))
        json.loads(json.dumps(song))            # still a document
        for t in song["tracks"]:
            if t.get("muted") and id(t) in muted_before:
                assert len(t["notes"]) == muted_before[id(t)], \
                    "a heal wrote into a MUTED lane"
    run()


def p5_coverage_bounds():
    import flow_court as FC

    @settings(max_examples=N, deadline=None)
    @given(song_st)
    def run(song):
        cov = FC.coverage(song)
        beat = cov["beat"]
        assert all(v in (0.0, 1.0) for v in beat)
        occ = cov["bar_occupancy"]
        assert all(0.0 <= v <= 1.0 for v in occ)
    run()


check("P1 no court crashes on any generated song", p1_courts_never_crash)
check("P2 flow verdicts carry the contract keys", p2_contract_keys)
check("P3 transforms preserve notes + length", p3_transforms_preserve)
check("P4 heals keep documents lawful + muted lanes sacred",
      p4_heals_stay_lawful)
check("P5 coverage kernel stays in bounds", p5_coverage_bounds)

print()
if FAILS:
    print(f"property_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print(f"property_battery: ALL GREEN ({N} examples/property)")
