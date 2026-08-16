#!/usr/bin/env python3
"""GROOVE RENDER E2E (wave-14, R-3 item 184): the KERNEL->RENDER->MEASURE
circle. Apply a known groove (mpc_62: off-16ths at 62%) to a hat lane,
render through the REAL engine (m1), onset-detect the wav, recover the
swing fraction, assert within tolerance of the intent. Closes the loop
between symbolic groove numbers and rendered audio truth.

Skip-safe: missing m1 binary or librosa -> SKIP (exit 0 with notice).
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import drum_grammar as DG  # noqa: E402

M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
OUT_DIR = os.path.join(ROOT, "songs")


def main():
    if not os.path.exists(M1):
        print("groove_render_e2e: SKIP (no m1 binary)")
        return 0
    try:
        import numpy as np
        import librosa
    except Exception as e:
        print(f"groove_render_e2e: SKIP (librosa: {e})")
        return 0
    bpm = 120.0
    hats = [{"start": i * 0.25, "pitch": 42, "len": 0.12, "vel": 0.9}
            for i in range(64)]                       # 4 bars of 16ths
    from groove import GROOVES
    prof = GROOVES["mpc_62"]
    DG.apply_slot_groove(hats, prof["off"], [1.0] * 16, amount=1.0)
    song = {"version": 2, "bpm": bpm, "lengthBars": 4, "key": "C major",
            "tracks": [{"name": "hats", "gainDb": 0.0,
                        "source": {"kind": "faust", "id": "hat"},
                        "notes": hats}]}
    sj = os.path.join(OUT_DIR, "_groove_e2e.json")
    wav = os.path.join(OUT_DIR, "_groove_e2e.wav")
    json.dump(song, open(sj, "w"), indent=1)
    r = subprocess.run([M1, "render", sj, wav], capture_output=True,
                       text=True, timeout=420)
    if r.returncode != 0 or not os.path.exists(wav):
        print(f"groove_render_e2e: RED — render failed: {r.stderr[-300:]}")
        return 1
    y, sr = librosa.load(wav, sr=22050, mono=True)
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time",
                                        backtrack=False, delta=0.04)
    spb = 60.0 / bpm
    fracs = []
    for t in onsets:
        b = t / spb
        pair = int(b / 0.5)
        frac = (b - pair * 0.5) / 0.5
        if 0.3 <= frac <= 0.85:
            fracs.append(frac)
    if len(fracs) < 8:
        print(f"groove_render_e2e: RED — only {len(fracs)} off-slot onsets "
              f"recovered from {len(onsets)} total")
        return 1
    sw = sum(fracs) / len(fracs)
    # intent: mpc_62 puts off-16ths +0.12 beats late = 0.5 + 0.12/0.5 = 0.74?
    # no — the off-16th sits at 0.25+0.12=0.37 of the 0.5 pair = 0.74. The
    # COURT's swing convention measures the same fraction; assert vs intent.
    want = (0.25 + 0.12) / 0.5
    ok = abs(sw - want) <= 0.06
    print(f"groove_render_e2e: measured swing {sw:.3f} vs intent {want:.3f} "
          f"({len(fracs)} onsets) — {'GREEN' if ok else 'RED'}")
    for p in (sj, wav):
        try:
            os.remove(p)
        except OSError:
            pass
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
