#!/usr/bin/env python3
"""THE AUDIO EAR battery — mic/guitar audio -> the FOLLOW's notes, proven.

Ground truth is a REAL render: a known melody through m1 (the same engine a
captured take would carry), then the tracker must recover it. Legs:
  - offline: >=7/8 melody notes matched (pitch exact, onset within a 16th),
    spurious notes bounded, velocities follow the written dynamics
  - silence -> zero notes
  - octave law: the low rung (48) never subharmonic-flips
  - STREAMING: the wav GROWS while the tracker follows it — notes must be
    EMITTED to the JSONL before the writer finishes (bounded live latency),
    and the final set must equal the offline read
  - determinism: two offline runs byte-identical

Usage: .venv/bin/python tools/audio_follow_battery.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import audio_follow as AF

M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
BPM = 120.0
#           beat  pitch  vel      — 8 notes, includes the low-octave guard (48)
MELODY = [(0.0, 60, 0.95), (1.0, 63, 0.6), (2.0, 67, 0.95), (3.0, 70, 0.6),
          (4.0, 67, 0.9), (5.0, 63, 0.9), (6.0, 60, 0.9), (7.0, 48, 0.9)]

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)


def render_melody(d):
    song = {"version": 2, "bpm": BPM, "lengthBars": 2, "masterGainDb": 0.0, "master": [],
            "tracks": [{"name": "lead", "source": {"kind": "faust", "id": "flute_lead"},
                        "gainDb": -6, "pan": 0,
                        "notes": [{"start": b, "len": 0.6, "pitch": p, "vel": v}
                                  for b, p, v in MELODY]}]}
    pj, pw = os.path.join(d, "mel.json"), os.path.join(d, "mel.wav")
    json.dump(song, open(pj, "w"))
    r = subprocess.run([M1, "render", pj, pw], capture_output=True, timeout=180)
    return pw if os.path.exists(pw) and r.returncode == 0 else None


def match(notes):
    """(matched melody rows, spurious count) — pitch exact, onset within a 16th."""
    hit, used = 0, set()
    for b, p, _v in MELODY:
        for i, n in enumerate(notes):
            if i in used:
                continue
            if n["pitch"] == p and abs(n["start"] - b) <= 0.25:
                hit += 1
                used.add(i)
                break
    return hit, len(notes) - len(used)


def main():
    if not os.path.exists(M1):
        print("audio-follow battery: SKIP (m1 not built)")
        return
    d = tempfile.mkdtemp(prefix="audio_follow_")
    try:
        pw = render_melody(d)
        ok(pw is not None, "melody rendered through the real engine")
        if pw is None:
            return

        # ---- offline read ----
        out1 = os.path.join(d, "h1.jsonl")
        notes = AF.follow(pw, BPM, out1)
        hit, spur = match(notes)
        ok(hit >= 7, f"offline: {hit}/8 melody notes recovered (got {[(n['pitch'], n['start']) for n in notes]})")
        ok(spur <= 2, f"offline: spurious bounded ({spur})")
        low = [n for n in notes if abs(n["start"] - 7.0) <= 0.25]
        ok(any(n["pitch"] == 48 for n in low) and not any(n["pitch"] == 36 for n in low),
           f"octave law: 48 tracked as 48, never 36 (got {[n['pitch'] for n in low]})")
        loud = [n for n in notes if n["pitch"] == 60 and abs(n["start"]) <= 0.25]
        soft = [n for n in notes if n["pitch"] == 63 and abs(n["start"] - 1.0) <= 0.25]
        ok(loud and soft and loud[0]["vel"] > soft[0]["vel"],
           f"velocity follows the written dynamics ({loud and loud[0]['vel']} > {soft and soft[0]['vel']})")
        ok([json.loads(l) for l in open(out1)] == notes, "JSONL mirrors the return")

        # ---- determinism ----
        out2 = os.path.join(d, "h2.jsonl")
        ok(AF.follow(pw, BPM, out2) == notes, "deterministic offline")

        # ---- silence ----
        sj, sw_ = os.path.join(d, "sil.json"), os.path.join(d, "sil.wav")
        json.dump({"version": 2, "bpm": BPM, "lengthBars": 1, "masterGainDb": 0.0,
                   "master": [], "tracks": [{"name": "lead", "gainDb": -6, "pan": 0,
                                             "source": {"kind": "faust", "id": "flute_lead"},
                                             "notes": []}]}, open(sj, "w"))
        subprocess.run([M1, "render", sj, sw_], capture_output=True, timeout=120)
        out3 = os.path.join(d, "h3.jsonl")
        ok(AF.follow(sw_, BPM, out3) == [], "silence -> zero notes")

        # ---- STREAMING: the wav grows under the tracker ----
        src = open(pw, "rb").read()
        grow = os.path.join(d, "grow.wav")
        out4 = os.path.join(d, "h4.jsonl")
        header_end = AF.wav_header(pw)[3]     # the REAL data offset, not a guess
        wrote_done = {"t": None}
        first_emit = {"t": None}

        def writer():
            with open(grow, "wb") as f:
                f.write(src[:header_end])
                f.flush()
                pos = header_end
                while pos < len(src):
                    nxt = min(len(src), pos + max(8192, len(src) // 24))
                    f.write(src[pos:nxt])
                    f.flush()
                    pos = nxt
                    time.sleep(0.12)
            wrote_done["t"] = time.monotonic()

        def watcher():
            while wrote_done["t"] is None or first_emit["t"] is None:
                if first_emit["t"] is None and os.path.exists(out4) \
                        and os.path.getsize(out4) > 0:
                    first_emit["t"] = time.monotonic()
                if wrote_done["t"] is not None and first_emit["t"] is None \
                        and time.monotonic() - wrote_done["t"] > 5.0:
                    return
                time.sleep(0.03)

        tw = threading.Thread(target=writer)
        tv = threading.Thread(target=watcher)
        tw.start(); tv.start()
        live_notes = AF.follow(grow, BPM, out4, stream=True, idle_sec=1.2)
        tw.join(); tv.join(timeout=6.0)
        ok(first_emit["t"] is not None and wrote_done["t"] is not None
           and first_emit["t"] < wrote_done["t"],
           "STREAMING: first note EMITTED before the writer finished (live latency bounded)")
        ok(live_notes == notes,
           f"STREAMING: the growing read converges to the offline truth "
           f"({len(live_notes)} vs {len(notes)} notes)")

        # ---- THE WET EAR: reverb-drowned takes (YIN's documented failure class) ----
        try:
            import torchfcpe  # noqa: F401 — the neural rail must exist to test it
            have_fcpe = True
        except Exception:
            have_fcpe = False
            print("  (wet-ear leg skipped: torchfcpe not importable)")
        if have_fcpe:
            wsong = {"version": 2, "bpm": BPM, "lengthBars": 2, "masterGainDb": 0.0,
                     "master": [],
                     "tracks": [{"name": "lead",
                                 "source": {"kind": "faust", "id": "flute_lead"},
                                 "gainDb": -6, "pan": 0,
                                 "fx": [{"id": "fx_reverb",
                                         "params": {"mix": 0.85, "size": 2.8}}],
                                 "notes": [{"start": b, "len": 0.6, "pitch": p, "vel": v}
                                           for b, p, v in MELODY]}]}
            wj, ww = os.path.join(d, "wet.json"), os.path.join(d, "wet.wav")
            json.dump(wsong, open(wj, "w"))
            subprocess.run([M1, "render", wj, ww], capture_output=True, timeout=180)
            # HONESTY: synthetic reverb keeps the flute's direct tone — YIN can
            # match fcpe here. The wet ear's superiority evidence is the
            # transcribe rails' REAL-recording record (bleed/breath/room: fcpe
            # 98% where harvest-class trackers drop 1/3). This leg proves the
            # NEURAL RAIL rides the same segmentation law, on wet AND dry.
            if os.path.exists(ww):
                fcpe_wet = AF.follow_fcpe(ww, BPM, os.path.join(d, "hf.jsonl"))
                hf, sf = match(fcpe_wet)
                ok(hf >= 7, f"WET EAR: fcpe recovers the drowned melody ({hf}/8)")
                ok(sf <= 5, f"WET EAR: spurious bounded in the wash ({sf})")
                fcpe_dry = AF.follow_fcpe(pw, BPM, os.path.join(d, "hfd.jsonl"))
                hfd, _ = match(fcpe_dry)
                ok(hfd >= 7, f"WET EAR: dry parity through the same law ({hfd}/8)")
            else:
                ok(False, "wet melody failed to render")
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"audio-follow battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
