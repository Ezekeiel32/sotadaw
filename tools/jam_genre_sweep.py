#!/usr/bin/env python3
"""THE GENRE SWEEP — the band seat generalizes, proven across DNA shapes.

Every seat law was proven on the house fixture; the laws are genre-agnostic BY
CONSTRUCTION, but construction isn't proof. This sweeps maximally diverse loop
DNA (major-key ambient, jazz bebop, log-drum amapiano, balkan brass...) through
a REAL jam_live set each and asserts the MACHINERY invariants that must hold
for any genre: the set runs, the grid is contiguous and exact, every late
render repeats (never silence), the kept take is valid song grammar and
renders NON-SILENT through the real engine. Content quality stays the ears'
job (genre-relative calibration); this is the generalization seal.

Usage: .venv/bin/python tools/jam_genre_sweep.py [genre ...]
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import jam
import jam_live as JL

DEFAULT = ["house", "ambient", "funk", "amapiano", "drill", "bebop",
           "balkan_brass", "synthwave"]

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)


def sweep_one(genre, d):
    name = f"_gsweep_{genre}"
    ipc = os.path.join(d, genre)
    res, err = JL.jam_live(genre, "wave", phrases=2, seed=3, name=name,
                           bars_per=1, ipc=ipc)
    ok(err is None and res is not None, f"[{genre}] the set ran ({err})")
    if res is None:
        return
    try:
        feed = [json.loads(l) for l in open(os.path.join(ipc, "live.jsonl"))]
        prs = [e for e in feed if e.get("ev") == "phrase_ready"]
        pos, contig = 0.0, True
        for e in prs:
            contig = contig and abs(float(e["start_beat"]) - pos) < 1e-6
            pos = float(e["start_beat"]) + float(e["bars"]) * 4.0
        ok(contig and abs(pos - 8.0) < 1e-6,
           f"[{genre}] grid law holds ({pos} beats)")
        late = [t for t in res["timing"][:-1] if not t["ready"]]
        reps = [e for e in prs if e.get("repeat")]
        ok(len(reps) >= len(late),
           f"[{genre}] repeat law holds ({len(late)} late / {len(reps)} repeats)")
        take = os.path.join(jam.SONGS, f"{name}.json")
        doc = json.load(open(take))
        ok(doc.get("tracks") and float(doc.get("lengthBars", 0)) == 2.0,
           f"[{genre}] take grammar sane ({doc.get('lengthBars')} bars, "
           f"{len(doc.get('tracks', []))} tracks)")
        tw = os.path.join(d, f"{genre}.wav")
        import render_cache as RC
        RC.render_cached(take, tw, quiet=True)
        rms = jam.wav_rms_db(tw) if os.path.exists(tw) else -120.0
        ok(rms > -60.0, f"[{genre}] the take renders NON-SILENT ({rms:.1f} dB)")
    finally:
        p = os.path.join(jam.SONGS, f"{name}.json")
        if os.path.exists(p):
            os.remove(p)


def main():
    if not os.path.exists(jam.M1):
        print("genre sweep: SKIP (m1 not built)")
        return
    genres = sys.argv[1:] or DEFAULT
    d = tempfile.mkdtemp(prefix="gsweep_")
    try:
        for g in genres:
            sweep_one(g, d)
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"genre sweep: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
