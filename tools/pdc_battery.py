#!/usr/bin/env python3
"""P2.8 FULL-GRAPH PDC BATTERY — latency compensation must hold across the graph.

A DAW that smears a track by its plugin latency is disqualified from "the manual
half producers respect". The engine (Tracktion) compensates reported latency;
fx_retune reports ~140ms via getLatencySeconds — the perfect probe: if PDC works,
a click THROUGH fx_retune lands at the same beat as a dry click; if PDC is
broken, it lands ~140ms late (unmissable).

Checks (each = render a 2-track click song, measure first-onset delta):
  P1 dry vs dry           sanity: two identical dry tracks align (< 3 ms)
  P2 dry vs fx_retune     PDC across a latency-reporting insert (< 12 ms)
  P3 dry vs bus send      a send/return path adds no timing smear (< 3 ms)
  P4 dry vs 3-fx chain    zero-latency faust chain stays sample-tight (< 3 ms)

usage: pdc_battery.py [--keep]   exit 0 = all green; prints PDC_JSON.
"""
import json, os, subprocess, sys, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

BPM = 120.0
CLICKS = [0.0, 4.0, 8.0, 12.0]     # one click per bar


def click_track(name, fx=None, sends=None, gain=-6.0):
    t = {"name": name, "source": {"kind": "faust", "id": "hat"}, "gainDb": gain,
         "notes": [{"start": b, "len": 0.1, "pitch": 70, "vel": 0.9} for b in CLICKS]}
    if fx:
        t["fx"] = fx
    if sends:
        t["sends"] = sends
    return t


def render(song, tag):
    sj = os.path.join(SONGS, f"_pdc_{tag}.json")
    wv = os.path.join(SONGS, f"_pdc_{tag}.wav")
    json.dump(song, open(sj, "w"), indent=1)
    r = subprocess.run([M1, "render-stems", sj, os.path.join(SONGS, f"_pdc_{tag}_stems")],
                       capture_output=True, text=True, timeout=600)
    ok = os.path.isdir(os.path.join(SONGS, f"_pdc_{tag}_stems"))
    return ok, sj, os.path.join(SONGS, f"_pdc_{tag}_stems"), (r.stdout + r.stderr)[-250:]


def first_onset(path, thresh_db=-35.0):
    import numpy as np
    with wave.open(path, "rb") as w:
        sw, n, sr, ch = w.getsampwidth(), w.getnframes(), w.getframerate(), w.getnchannels()
        raw = w.readframes(n)
    if sw == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        x = (b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16))
        x = (x - ((x >> 23) << 24)).astype(np.float64) / 8388608.0
    else:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    x = np.abs(x.reshape(-1, ch)).max(axis=1)
    thresh = 10 ** (thresh_db / 20.0)
    idx = np.argmax(x > thresh)
    if x[idx] <= thresh:
        return None
    return idx / sr


def stem_for(stems_dir, name):
    for f in sorted(os.listdir(stems_dir)):
        if name in f and f.endswith(".wav"):
            return os.path.join(stems_dir, f)
    return None


def main():
    import shutil
    checks, fails = [], []

    def check(nm, ok, detail):
        checks.append({"name": nm, "ok": bool(ok), "detail": detail})
        if not ok:
            fails.append(nm)
        print(("  ok " if ok else "FAIL ") + f"{nm}  {detail}")

    cases = [
        ("dry_vs_dry", click_track("probe"), 0.003),
        ("dry_vs_retune", click_track("probe", fx=[{"id": "fx_retune",
                                                    "params": {"amount": 0.0}}]), 0.012),
        ("dry_vs_bus_send", click_track("probe", sends=[{"bus": "verb", "gainDb": -60}]), 0.003),
        ("dry_vs_faust_chain", click_track("probe", fx=[
            {"id": "fx_filter", "params": {"cutoff": 8000}},
            {"id": "fx_saturate", "params": {"drive": 2.0, "mix": 0.3}},
            {"id": "fx_trim", "params": {"level": -1.0}}]), 0.003),
    ]

    cleanup = []
    for tag, probe, tol in cases:
        song = {"version": 2, "bpm": BPM, "lengthBars": 4, "masterGainDb": 0, "master": [],
                "tracks": [click_track("anchor"), probe]}
        if tag == "dry_vs_bus_send":
            song["buses"] = [{"id": "verb", "gainDb": 0,
                              "fx": [{"id": "fx_reverb", "params": {"mix": 1.0}}]}]
        ok, sj, stems, log = render(song, tag)
        cleanup += [sj, stems, sj[:-5] + ".wav"]
        if not ok:
            check(tag, False, {"render": log})
            continue
        a = first_onset(stem_for(stems, "anchor"))
        p = first_onset(stem_for(stems, "probe"))
        if a is None or p is None:
            check(tag, False, {"onsets": [a, p], "note": "silent stem"})
            continue
        delta = abs(p - a)
        check(tag, delta <= tol, {"delta_ms": round(delta * 1000, 2),
                                  "tol_ms": tol * 1000})

    result = {"pass": not fails, "failing": fails, "checks": checks}
    print("PDC_JSON " + json.dumps(result))
    if "--keep" not in sys.argv:
        for p in cleanup:
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)
            elif os.path.exists(p):
                os.remove(p)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
