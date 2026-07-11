#!/usr/bin/env python3
"""dj_arc_battery.py — §7.7 tail proof: crowd-arc presets + acapella auto-select.

ARC: hop_cost/plan_order gain a crowd-energy preset — peak (the original law,
frozen-number backward-exact), warmup (big jumps surcharged: opening-slot
restraint), closer (rise through the body, LAND at the end: the last hop may
come down free, late climbs punished). Pure math.

BRIDGE-AUTO: build_set(bridge_auto=True) probes every hop's outgoing tail with
the builder's own cut law and bridges wherever a voice sings.
extract_vocal_tail is monkeypatched (no demucs here) — these checks prove
SELECTION, single-probe CACHING, and the JSON wiring. The real-demucs leg is a
manual CLI run (--bridge-auto on a sung wav).

Exit code IS the verdict.
"""
import contextlib
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)
    print(f"  {'OK ' if cond else 'XX '}{msg}")


def track_names(nm):
    d = json.load(open(os.path.join(ROOT, "songs", f"{nm}.json")))
    return [t["name"] for t in d["tracks"]]


def scrub(*names):
    for nm in names:
        for e in (".json", ".setplan.json"):
            p = os.path.join(ROOT, "songs", f"{nm}{e}")
            if os.path.exists(p):
                os.remove(p)


def main():
    import dj_set
    from dj_mix import harmonic_verdict

    print("== DJ ARC + BRIDGE-AUTO BATTERY (§7.7 tail) ==")
    A = lambda bpm: (bpm, "8A", 1.0)

    # ---- peak = the ORIGINAL law, frozen numbers (backward-exact) ----
    ok(abs(dj_set.hop_cost(A(120), A(126)) - 0.5) < 1e-9,
       "peak: 5% climb costs 0.5 (frozen original)")
    ok(abs(dj_set.hop_cost(A(120), A(114)) - 1.25) < 1e-9,
       "peak: 5% downshift adds 15x (frozen original)")
    cams = [f"{n}{ab}" for n in range(1, 13) for ab in "AB"]
    clash = next((b for b in cams if "CLASH" in harmonic_verdict("8A", b)), None)
    ok(clash is not None and
       abs(dj_set.hop_cost(A(120), (126, clash, 1.0)) - 6.5) < 1e-9,
       f"peak: key clash (8A->{clash}) adds +6 (frozen original)")

    # ---- warmup: gentle climbs identical, big jumps surcharged ----
    ok(abs(dj_set.hop_cost(A(120), A(126), "warmup") - 0.5) < 1e-9,
       "warmup: <=6% climb costs the same as peak")
    ok(dj_set.hop_cost(A(120), A(133), "warmup") > dj_set.hop_cost(A(120), A(133)),
       "warmup: a 10.8% jump is surcharged vs peak")

    # ---- closer: body climbs like peak; the LANDING comes down free ----
    ok(abs(dj_set.hop_cost(A(132), A(128), "closer", pos=0.5)
           - dj_set.hop_cost(A(132), A(128))) < 1e-9,
       "closer: body downshift still punished (like peak)")
    ok(dj_set.hop_cost(A(132), A(128), "closer", pos=1.0)
       < dj_set.hop_cost(A(132), A(128)),
       "closer: the last hop may come DOWN free")
    ok(dj_set.hop_cost(A(128), A(132), "closer", pos=1.0)
       > dj_set.hop_cost(A(128), A(132)),
       "closer: a late climb is punished")

    # ---- plan_order: arcs shape the ORDER (exhaustive n=4, deterministic) ----
    items = [A(126), A(122), A(132), A(128)]          # shuffled on purpose
    peak_order, _ = dj_set.plan_order(items, "peak")
    ok(peak_order == [1, 0, 3, 2],
       f"plan[peak]: ascending 122-126-128-132 ({peak_order})")
    closer_order, _ = dj_set.plan_order(items, "closer")
    ok(closer_order[0] == 1 and closer_order[-1] != 2,
       f"plan[closer]: opens lowest, does NOT end on the max-bpm deck ({closer_order})")
    ok(2 in closer_order[1:-1],
       f"plan[closer]: the peak deck lands mid-set ({closer_order})")

    # ---- bridge-auto: selection + caching + JSON wiring (demucs mocked) ----
    wavs = [w for w in sorted(glob.glob(os.path.join(ROOT, "songs", "*.wav")))
            if os.path.getsize(w) > 100000][:2]
    if len(wavs) < 2:
        print("  bridge-auto SKIP: need 2 song wavs")
    else:
        voiced, instr = wavs[0], wavs[1]
        calls = []
        real_extract = dj_set.extract_vocal_tail

        def fake_extract(path, start_s, dur_s, tag, win_s=None):
            calls.append(path)
            return os.path.join(ROOT, "songs", "_fake_bridge_vocal.wav") \
                if path == voiced else None
        dj_set.extract_vocal_tail = fake_extract
        try:
            hush = lambda: contextlib.redirect_stdout(io.StringIO())
            # default OFF: no probe ever runs
            with hush():
                dj_set.build_set("_djarc_off", [voiced, instr],
                                 bpms=[120, 120], camelots=["8A", "8A"])
            ok(len(calls) == 0, "bridge_auto default OFF: zero probes")
            # 3 decks [voiced, instr, voiced]: hop1 sings -> bridge; hop2 doesn't
            with hush():
                dj_set.build_set("_djarc_auto", [voiced, instr, voiced],
                                 bpms=[120, 120, 120], camelots=["8A"] * 3,
                                 bridge_auto=True)
            names = track_names("_djarc_auto")
            ok("bridge_ab" in names and "bridge_bc" not in names,
               f"auto: voiced hop bridged, silent hop not ({[n for n in names if 'bridge' in n]})")
            ok(len(calls) == 2,
               f"auto: exactly one probe per hop — overlay reused the cache ({len(calls)} probes)")
            d = json.load(open(os.path.join(ROOT, "songs", "_djarc_auto.json")))
            bt = next(t for t in d["tracks"] if t["name"] == "bridge_ab")
            ok(bt["audioClips"][0]["file"].endswith("_fake_bridge_vocal.wav"),
               "auto: the probed vocal wav IS the overlay clip")
            da = next(t for t in d["tracks"] if t["name"] == "deck_a")
            ok("lengthBeats" in da["audioClips"][0],
               "auto: outgoing deck cut phrase-exact (bridge style applied)")
        finally:
            dj_set.extract_vocal_tail = real_extract
            scrub("_djarc_off", "_djarc_auto")

    print(f"dj-arc battery: {PASS}/{PASS + len(FAIL)} " + ("clean" if not FAIL else "RED"))
    for f in FAIL:
        print("FAIL:", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
