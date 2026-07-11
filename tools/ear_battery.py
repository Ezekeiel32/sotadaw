#!/usr/bin/env python3
"""THE EAR BATTERY — self-identification law for tools/ear_pick.py.

"THIS EAR NEEDS TO BE A MILLION PERCENT ACCURATE" (Chezy 2026-07-11).
Accuracy is proven, not claimed: render a KNOWN voice playing a phrase
through the real engine, hand the render to the ear as if it were a stem,
and the ear must name the voice back. Closed-loop finals make this exact
by construction — the true voice's probe render nulls against the fixture.

Needs app/build m1 (like ghost_e2e); pure checks still run without it.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ear_pick as ep  # noqa: E402

N = 0
FAILS = []


def check(name, ok, detail=""):
    global N
    N += 1
    print(f"[ear-battery] {N:2}. {name:58} {'OK' if ok else 'FAIL ' + str(detail)}")
    if not ok:
        FAILS.append(name)


PHRASES = {
    "bass": [{"start": b * 1.0, "len": 0.8, "pitch": p, "vel": 0.8}
             for b, p in enumerate((36, 36, 39, 41, 36, 43, 39, 36))],
    "mid": [{"start": b * 0.5, "len": 0.45, "pitch": p, "vel": 0.7}
            for b, p in enumerate((60, 64, 67, 72, 67, 64, 62, 60,
                                   65, 69, 72, 76, 72, 69, 65, 64))],
}

SELF_ID = [("sub_clean", "bass", "bass"), ("reese", "bass", "bass"),
           ("rhodes", "keys", "mid"), ("marimba", "keys", "mid"),
           ("supersaw", "melodic", "mid"), ("pluck", "guitar", "mid")]


def main():
    import numpy as np
    sr = 44100
    t = np.linspace(0, 2.0, 2 * sr, endpoint=False)
    x = 0.5 * np.sin(2 * np.pi * 55 * t)
    f = ep.footprint(x, sr)
    check("footprint: 55Hz tone is low-band dominant",
          f and f["bands"]["low"] > 90 and f["centroid_hz"] < 120, f)
    check("footprint: silence returns None (no fake verdicts)",
          ep.footprint(np.zeros(sr), sr) is None)
    d0 = ep.distance(f, f)
    check("distance: identity is zero", d0 == 0.0, d0)

    if not os.path.exists(ep.M1):
        print("[ear-battery] m1 missing — self-ID legs skipped (engine rig)")
        print(f"[ear-battery] {N}/3 pure checks"
              + (" ALL PASS" if not FAILS else f" RED: {FAILS}"))
        return 0 if not FAILS else 1

    for voice, role, phrase in SELF_ID:
        notes = PHRASES[phrase]
        wav = ep._render_probe(voice, notes, 120.0, f"battery_{voice}")
        if wav is None:
            check(f"self-ID {voice} ({role})", False,
                  f"fixture render failed: {ep.LAST_RENDER_ERR}")
            check(f"self-ID {voice} is closed-loop + near-null", False,
                  "no fixture")
            continue
        try:
            r = ep.pick_voice(wav, notes, 120.0, role=role)
        finally:
            os.remove(wav)
        check(f"self-ID {voice} ({role} lineup)",
              r is not None and r["voice"] == voice,
              r and (r["voice"], r["score"], r["mode"]))
        if r and r["voice"] == voice:
            check(f"self-ID {voice} is closed-loop + near-null",
                  r["mode"] == "closed-loop" and r["score"] < 0.12,
                  (r["mode"], r["score"]))
        else:
            check(f"self-ID {voice} is closed-loop + near-null", False,
                  "pick missed")

    want = 3 + 2 * len(SELF_ID)
    ok = not FAILS and N == want
    print(f"[ear-battery] {N}/{want} checks, "
          + ("ALL PASS — the ear knows every voice by sound"
             if ok else f"RED: {FAILS}"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
