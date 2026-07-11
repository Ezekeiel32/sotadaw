#!/usr/bin/env python3
"""THE VOICE SPECTRUM MAP (W74, 2026-07-11).

Where does each melodic voice actually LAND — band shares, centroid, and
realized loudness at a fixed musical task. Born from the amapiano judge
dialogue: "pianos define the genre in the midrange" while three successive
bed voices (pad_motion, keys_dark, jazz_piano) failed to fill 500-2k; every
pick was a guess because no table of measured voice footprints existed.

Method: each voice plays the SAME 2-bar held C-major triad task (C4/E4/G4
whole notes, vel 0.5, gain -10) through the real engine, alone. analyze2
bands on the solo render = the voice's footprint. rms_db ranks how LOUD the
voice realizes the identical task (voices differ by >20dB at equal gain —
the second half of every "the bed didn't land" mystery).

Usage:
  voice_spectrum.py                # measure the standard melodic set
  voice_spectrum.py pluck2 harp    # measure specific voices
  --json                           # machine output (also always written to
                                   # eval/voice_spectrum.json, merge-updated)
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")
OUT = os.path.join(ROOT, "eval/voice_spectrum.json")

# the standing melodic set: every voice the color/lead rails commonly seed
STANDARD = [
    "pad_motion", "keys_dark", "jazz_piano", "rhodes", "organ_soul",
    "hammond_organ", "vox_pad", "formant_vox", "pluck", "pluck2",
    "supersaw", "supersaw_fat", "fmbell", "strings_disco", "strings_stacc",
    "sax_section", "brass_stab", "clav_funk", "vibraphone", "marimba",
    "kalimba", "harp", "clean_chime_guitar", "guitar_grit",
]

BANDS = [("low", 20, 120), ("lowmid", 120, 500), ("mid", 500, 2000),
         ("himid", 2000, 6000), ("high", 6000, 16000)]


def measure(voice):
    """Render the fixed triad task solo; return the voice's footprint."""
    song = {"bpm": 100, "lengthBars": 2, "key": "C major",
            "tracks": [{"name": "probe", "source": {"kind": "faust", "id": voice},
                        "gainDb": -10, "pan": 0,
                        "notes": [{"start": float(b * 4), "len": 3.9, "pitch": p,
                                   "vel": 0.5}
                                  for b in range(2) for p in (60, 64, 67)]}]}
    p = os.path.join(ROOT, "songs/_voicespec_probe.json")
    json.dump(song, open(p, "w"))
    wav_p = p.replace(".json", ".wav")
    r = subprocess.run([M1, "render", p, wav_p], capture_output=True, cwd=ROOT,
                       timeout=300)
    if r.returncode != 0:
        return None
    with wave.open(wav_p) as f:
        sr, sw, n = f.getframerate(), f.getsampwidth(), f.getnframes()
        raw = f.readframes(n)
    if sw == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        x = np.where(x >= 1 << 23, x - (1 << 24), x).astype(np.float64) / (1 << 23)
    else:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    mono = (x[0::2] + x[1::2]) / 2.0
    rms = float(np.sqrt(np.mean(mono ** 2)) + 1e-12)
    if rms < 1e-6:            # silent render = broken/quarantined voice
        return None
    from numpy.fft import rfft
    fr = np.fft.rfftfreq(len(mono), 1 / sr)
    P = np.abs(rfft(mono)) ** 2
    aud = P[(fr >= 20) & (fr < 16000)].sum() + 1e-12
    shares = {name: round(100.0 * float(P[(fr >= lo) & (fr < hi)].sum() / aud), 1)
              for name, lo, hi in BANDS}
    centroid = float((fr[: len(P)] * P).sum() / (P.sum() + 1e-12))
    for f2 in (p, wav_p):
        if os.path.exists(f2):
            os.remove(f2)
    return {"bands": shares, "centroid_hz": round(centroid),
            "rms_db": round(20 * np.log10(rms), 1)}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    voices = args or STANDARD
    table = {}
    if os.path.exists(OUT):
        try:
            table = json.load(open(OUT))
        except Exception:
            table = {}
    rows = []
    for v in voices:
        m = measure(v)
        if m is None:
            rows.append((v, None))
            continue
        table[v] = m
        rows.append((v, m))
    json.dump(table, open(OUT, "w"), indent=1, sort_keys=True)
    if "--json" in sys.argv:
        print(json.dumps({v: m for v, m in rows if m}, indent=1))
        return 0
    print(f"{'voice':22s} {'low':>5s} {'lowmid':>7s} {'mid':>5s} {'himid':>6s} "
          f"{'high':>5s} {'centroid':>9s} {'rms':>7s}")
    for v, m in sorted(rows, key=lambda r: -(r[1] or {"bands": {"mid": -1}})["bands"]["mid"]):
        if m is None:
            print(f"{v:22s} SILENT/BROKEN")
            continue
        b = m["bands"]
        print(f"{v:22s} {b['low']:5.1f} {b['lowmid']:7.1f} {b['mid']:5.1f} "
              f"{b['himid']:6.1f} {b['high']:5.1f} {m['centroid_hz']:8d}Hz "
              f"{m['rms_db']:6.1f}dB")
    print(f"\n-> {OUT} ({len(table)} voices banked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
