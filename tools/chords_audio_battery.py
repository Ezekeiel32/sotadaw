#!/usr/bin/env python3
"""chords_audio_battery.py — V54 audio->chords regression net.

Renders a known progression (Am-F-C-G, no drums) via m1 and asserts:
  STANDALONE  chords_audio maj/min bar-accuracy >= 75% (drum-free chroma is clean)
  FUSION      chordvote.chord_map(audio_wav=) recovers chords a DRUM-ONLY song's
              symbols alone cannot — the audio witness carries where transcription
              is blind (the point of V54's fusion).
Engine-dependent (needs m1); sandbox-isolated songs. Exit code IS the verdict.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
SONG = os.path.join(ROOT, "songs", "_chaud_bat.json")
WAV = os.path.join(ROOT, "songs", "_chaud_bat.wav")

PROG = [("Am", [57, 60, 64], 45), ("F", [53, 57, 60], 41),
        ("C", [48, 52, 55], 48), ("G", [55, 59, 62], 43)]        # 2 bars each
GT8 = ["Am", "Am", "F", "F", "C", "C", "G", "G"]


def build_harmonic():
    pad, bass = [], []
    for i, (_nm, tri, rt) in enumerate(PROG):
        b0 = i * 8.0
        for p in tri:
            pad.append({"start": b0, "len": 7.8, "pitch": p, "vel": 0.6})
        bass.append({"start": b0, "len": 7.8, "pitch": rt, "vel": 0.7})
    return {"version": 2, "bpm": 120, "key": "A minor", "lengthBars": 8, "masterGainDb": 0,
            "tracks": [{"name": "pad", "source": {"kind": "faust", "id": "pad_motion"},
                        "gainDb": -6, "notes": pad},
                       {"name": "bass", "source": {"kind": "faust", "id": "sub_clean"},
                        "gainDb": -8, "notes": bass}]}


def rq(c):
    import reharm
    r, q, _ = reharm.parse_chord(c)
    return (r, q)


def acc(det):
    return sum(1 for i, g in enumerate(GT8)
               if any(x["bar"] == i + 1 and rq(x["chord"]) == rq(g) for x in det))


def main():
    import chords_audio
    import chordvote
    print("== CHORDS-FROM-AUDIO BATTERY (V54) ==")
    json.dump(build_harmonic(), open(SONG, "w"), indent=1)
    r = subprocess.run([M1, "render", SONG, WAV], capture_output=True, text=True, timeout=180)
    if "ok=1" not in (r.stdout + r.stderr):
        print("  XX m1 render failed")
        return 1
    fails = 0

    hits = acc(chords_audio.chords(WAV, 120, 8))
    ok = hits >= 6                                    # 6/8 = 75%
    fails += not ok
    print(f"  {'OK ' if ok else 'XX '}standalone maj/min accuracy {hits}/8 = {hits/8:.0%} (bar 75%)")

    # FUSION: a drum-only song has NO harmonic symbols; the audio witness recovers them
    drum_song = {"version": 2, "bpm": 120, "key": "A minor", "lengthBars": 8,
                 "tracks": [{"name": "kick", "source": {"kind": "faust", "id": "kick_punch"},
                             "notes": [{"start": b, "len": 0.2, "pitch": 36, "vel": 0.9}
                                       for b in range(0, 32)]}]}
    sym_only = chordvote.chord_map(drum_song)
    fused = chordvote.chord_map(drum_song, audio_wav=WAV, audio_bpm=120)
    fh = acc(fused)
    ok2 = len(sym_only) == 0 and fh >= 6
    fails += not ok2
    print(f"  {'OK ' if ok2 else 'XX '}fusion: drum-only symbols={len(sym_only)} chords "
          f"-> audio-fused {fh}/8 recovered")

    for f in (SONG, WAV):
        if os.path.exists(f):
            os.remove(f)
    print("PASS" if fails == 0 else f"REGRESSION ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
