#!/usr/bin/env python3
"""THE COURT BATTERY — pure synthetic proof of tools/import_court.py.

Chezy's own scenarios are checks here verbatim: "no way that by accident
there'll be two notes off key" (1), "thirty two beats of a bass drum unless
it's a double bass ... hundred percent confident" (5/6), "no non snap to
note" (8/9), "no echoey, weird sounding music" (10/11).
"""
import json
import os
import shutil
import sys
import tempfile

import numpy as np

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import import_court as ic  # noqa: E402
import source_kit as sk  # noqa: E402

SR = 44100
N = 0
FAILS = []


def check(name, ok, detail=""):
    global N
    N += 1
    print(f"[court-battery] {N:2}. {name:58} {'OK' if ok else 'FAIL ' + detail}")
    if not ok:
        FAILS.append(name)


def _note(start, pitch, vel=0.8, ln=0.4):
    return {"start": float(start), "len": float(ln), "pitch": int(pitch),
            "vel": float(vel)}


def _acts(rr, action):
    return [r for r in rr if r["action"] == action]


# ------------------------------------------------------------- key court
def t_key():
    # C major scaffold with ONE stray F# (accident) at a leap (not passing)
    mel = [_note(i * 0.5, p) for i, p in enumerate((60, 64, 67, 72, 67, 64))]
    mel.insert(3, _note(1.25, 66, vel=0.6))       # F# between 72 leaps = accident
    out, rr = ic.court_key(mel, "C major")
    snapped = _acts(rr, "snapped")
    check("key: isolated off-key note snapped to scale",
          bool(snapped) and all((n["pitch"] % 12) in {0, 2, 4, 5, 7, 9, 11}
                                for n in out),
          f"rr={rr}")

    # Bb repeated 6x in C major = borrowed INTENT, kept
    mel = [_note(i * 0.5, 60) for i in range(6)] + \
          [_note(3 + i * 0.5, 70, vel=0.9) for i in range(6)]
    out, rr = ic.court_key(mel, "C major")
    check("key: pattern-supported blue note kept",
          any(n["pitch"] == 70 for n in out) and bool(_acts(rr, "kept")),
          f"rr={rr}")

    # chromatic passing run C C# D survives (the measured-slide law)
    mel = [_note(0, 60), _note(0.5, 61, vel=0.5), _note(1.0, 62)]
    out, rr = ic.court_key(mel, "C major")
    check("key: chromatic passing tone exempt (slides survive)",
          any(n["pitch"] == 61 for n in out), f"out={[n['pitch'] for n in out]}")

    # no key = no verdicts
    out, rr = ic.court_key([_note(0, 61)], "")
    check("key: no detected key -> no opinion", out[0]["pitch"] == 61 and not rr)


# ------------------------------------------------------------- runs court
def _burst_hat(sec=0.06, amp=0.5):
    rng = np.random.default_rng(3)
    from scipy.signal import butter, sosfilt
    n = rng.standard_normal(int(sec * SR))
    h = sosfilt(butter(4, 6000 / (SR / 2), btype="highpass", output="sos"), n)
    t = np.linspace(0, sec, len(h), endpoint=False)
    return amp * h / (np.abs(h).max() + 1e-9) * np.exp(-t / 0.02)


def _burst_sub(f=55.0, sec=0.12, amp=0.9):
    t = np.linspace(0, sec, int(sec * SR), endpoint=False)
    return amp * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.06)


def _wav_of(events, total_s):
    x = np.zeros(int(total_s * SR))
    for t, sig in events:
        i0 = int(t * SR)
        x[i0:i0 + len(sig)] += sig[: len(x) - i0]
    d = tempfile.mkdtemp(prefix="court_")
    p = os.path.join(d, "drums.wav")
    sk._save_wav16(p, np.clip(x, -1, 1), SR)
    return p, d


def t_runs():
    spb = 0.5                                     # 120bpm
    # 32 hits LABELED kick, audio = hat rolls -> reassigned
    notes = [_note(i * 0.25, 36, vel=0.7, ln=0.1) for i in range(32)]
    wav, d = _wav_of([(n["start"] * spb, _burst_hat()) for n in notes], 6.0)
    try:
        out, rr = ic.court_runs(notes, wav, 120.0, available_pitches={36, 38, 42, 46})
        re = _acts(rr, "reassigned")
        check("runs: 32 'kicks' measuring hi-band -> reassigned to hats",
              bool(re) and all(n["pitch"] == 42 for n in out), f"rr={rr}")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # 32 hits labeled kick, audio IS sub -> kept + verified receipt
    notes = [_note(i * 0.25, 36, vel=0.9, ln=0.1) for i in range(32)]
    wav, d = _wav_of([(n["start"] * spb, _burst_sub()) for n in notes], 6.0)
    try:
        out, rr = ic.court_runs(notes, wav, 120.0, available_pitches={36, 42})
        ver = _acts(rr, "verified")
        check("runs: true double-bass run kept, receipt measures sub",
              all(n["pitch"] == 36 for n in out) and bool(ver)
              and "double bass" in ver[0]["why"], f"rr={rr}")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # run labeled SNARE whose audio is sub AND the kick lane already has the
    # same moments -> dupes DROPPED, not doubled onto the kick
    fake = [_note(i * 0.25, 38, vel=0.6, ln=0.1) for i in range(16)]
    real = [_note(i * 0.25, 36, vel=0.9, ln=0.1) for i in range(16)]
    wav, d = _wav_of([(n["start"] * spb, _burst_sub()) for n in real], 5.0)
    try:
        out, rr = ic.court_runs(fake + real, wav, 120.0,
                                available_pitches={36, 38, 42})
        re = _acts(rr, "reassigned")
        kicks = [n for n in out if n["pitch"] == 36]
        check("runs: bleed doubles drop instead of doubling the true lane",
              bool(re) and re[0]["dropped_dupes"] == 16 and len(kicks) == 16,
              f"rr={rr} kicks={len(kicks)}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ------------------------------------------------------------- snap court
def t_snap():
    ns = [_note(i * 0.25, 60) for i in range(20)]
    ns += [_note(5.0 + 0.06, 60), _note(5.5 + 0.07, 60), _note(6.0 - 0.06, 60)]
    out, rr = ic.court_snap(ns, lane="x_sketch")
    snapped = _acts(rr, "snapped")
    d = [abs(ic._wrap(n["start"], 0.25)) for n in out]
    check("snap: consensus lane snaps its stragglers",
          bool(snapped) and max(d) < 0.02, f"rr={rr} maxd={max(d):.3f}")

    trip = [_note(i / 3.0, 60) for i in range(18)]
    out, rr = ic.court_snap(trip, lane="t_sketch")
    check("snap: triplet lane untouched",
          [n["start"] for n in out] == [n["start"] for n in trip]
          and not _acts(rr, "snapped"), f"rr={rr}")


# ------------------------------------------------------------- echo court
def t_echo():
    src = [_note(0, 60, vel=0.9), _note(4, 60, vel=0.9)]
    tail = [_note(0.75, 60, vel=0.5), _note(1.5, 60, vel=0.28),
            _note(2.25, 60, vel=0.15)]
    out, rr = ic.court_echo(src + tail, lane="v_sketch")
    check("echo: decaying constant-gap chain culled, sources stay",
          len(out) == 2 and all(n["vel"] == 0.9 for n in out)
          and bool(_acts(rr, "culled")), f"out={len(out)} rr={rr}")

    ost = [_note(i * 0.5, 40, vel=0.8) for i in range(16)]
    out, rr = ic.court_echo(ost, lane="b_sketch")
    check("echo: equal-velocity ostinato is music, untouched",
          len(out) == 16 and not rr, f"out={len(out)}")


# ------------------------------------------------------------- idempotence
def t_idem():
    mel = [_note(i * 0.5, p) for i, p in enumerate((60, 64, 67, 72, 67, 64))]
    mel.insert(3, _note(1.25, 66, vel=0.6))
    mel += [_note(5.0 + 0.06, 60)] * 1
    a, _ = ic.court_key(mel, "C major")
    a, _ = ic.court_echo(a)
    a, _ = ic.court_snap(a)
    b, r1 = ic.court_key(a, "C major")
    b, r2 = ic.court_echo(b)
    b, r3 = ic.court_snap(b)
    acts = [r for r in r1 + r2 + r3 if r["action"] in
            ("snapped", "culled", "reassigned")]
    check("idempotence: a courted lane re-courts to zero convictions",
          not acts and b == a, f"acts={acts}")


# ------------------------------------------------------------- hold_court e2e
def t_hold():
    spb = 0.5
    fake_kicks = [_note(i * 0.25, 36, vel=0.7, ln=0.1) for i in range(32)]
    real_hats = [_note(8.5 + i * 0.5, 42, vel=0.6, ln=0.05) for i in range(8)]
    ev = [(n["start"] * spb, _burst_hat()) for n in fake_kicks + real_hats]
    wav, d = _wav_of(ev, 8.0)
    song = {"bpm": 120.0, "key": "C major", "tracks": [
        {"name": "other_sketch", "source": {"kind": "faust"},
         "notes": [_note(0, 60), _note(0.5, 66, vel=0.5), _note(1.0, 72)]},
        {"name": "Kick", "source": {"kind": "sample", "kit": "x"},
         "notes": fake_kicks},
        {"name": "Hats", "source": {"kind": "sample", "kit": "x"},
         "notes": real_hats},
    ]}
    try:
        docket = ic.hold_court(song, drums_wav=wav,
                               kit_pitches={36, 38, 42, 46})
        kick = next(t for t in song["tracks"] if t["name"] == "Kick")
        hats = next(t for t in song["tracks"] if t["name"] == "Hats")
        check("hold_court: docket lands + fake kicks re-homed to the Hats lane",
              bool(docket) and len(kick["notes"]) == 0
              and len(hats["notes"]) == 40,
              f"kick={len(kick['notes'])} hats={len(hats['notes'])}")
        mel = next(t for t in song["tracks"] if t["name"] == "other_sketch")
        check("hold_court: melodic lane courted in the same session",
              all((n["pitch"] % 12) in {0, 2, 4, 5, 7, 9, 11}
                  for n in mel["notes"]),
              f"pitches={[n['pitch'] for n in mel['notes']]}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    t_key()
    t_runs()
    t_snap()
    t_echo()
    t_idem()
    t_hold()
    want = 14
    ok = not FAILS and N == want
    print(f"[court-battery] {N}/{want} checks, "
          + ("ALL PASS — the court is seated" if ok else f"RED: {FAILS}"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
