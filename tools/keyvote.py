#!/usr/bin/env python3
"""KEY FROM TRANSCRIPTION — the zero-new-deps key detector (Beyond-SOTA queue).

keyvote.py <audio> [--json]

The battery's lab notes (key_battery.py) falsified every chroma-profile tweak:
aggregate spectra of a diatonic progression ≈ the scale set, and kick fundamentals
pollute four-floor material. Transcription escapes both: basic-pitch (Apache-2.0,
in tree) gives NOTES with time/duration/register, so we can vote with musical
evidence — duration-weighted pitch classes, BASS-REGISTER tonic testimony, and
third-degree mode evidence — instead of raw spectrum mass.
"""
import argparse, json, sys

import numpy as np

KS_MAJOR = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
KS_MINOR = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]


def vote(path):
    import contextlib, io, os
    from basic_pitch.inference import predict
    with contextlib.redirect_stdout(io.StringIO()):   # bp prints "Predicting MIDI..." to stdout
        _, _, events = predict(path)
    if not len(events):
        return None, 0.0, 0
    hist = np.zeros(12)
    bass = np.zeros(12)
    rows = []
    for ev in events:
        s, e, pitch, amp = float(ev[0]), float(ev[1]), int(ev[2]), float(ev[3])
        if e - s < 0.05 or amp < 0.1:
            continue
        rows.append((s, e, pitch, amp))
        w = (e - s) * amp
        if pitch < 40:              # kick-fundamental range: witness, not juror
            w *= 0.3
        hist[pitch % 12] += w
    if not rows or hist.sum() <= 0:
        return None, 0.0, 0
    # bass testimony: the lowest sounding note per half-second slice roots the harmony
    t_end = max(e for _, e, _, _ in rows)
    t = 0.0
    while t < t_end:
        active = [p for s, e, p, _ in rows if s <= t < e]
        if active:
            bass[min(active) % 12] += 1.0
        t += 0.5
    hist = hist / hist.sum()
    bass = bass / max(bass.sum(), 1e-9)

    best = []
    for rot in range(12):
        h = np.roll(hist, -rot)
        for mode, prof in (("major", KS_MAJOR), ("minor", KS_MINOR)):
            ks = float(np.corrcoef(h, prof)[0, 1])
            third = (hist[(rot + 4) % 12] - hist[(rot + 3) % 12]) * (1 if mode == "major" else -1)
            score = ks + 1.6 * float(bass[rot]) + 2.0 * float(third)
            best.append((f"{NAMES[rot]} {mode}", score))
    best.sort(key=lambda x: -x[1])
    conf = round(max(0.0, best[0][1] - best[1][1]), 2)
    return best[0][0], min(1.0, conf), len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    key, conf, n = vote(a.audio)
    if a.json:
        print(json.dumps({"file": a.audio, "key": key, "confidence": conf, "notes_used": n}))
    else:
        print(f"KEYVOTE {a.audio}: {key} (conf {conf}, {n} transcribed notes)")


if __name__ == "__main__":
    main()
