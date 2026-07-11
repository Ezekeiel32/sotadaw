#!/usr/bin/env python3
"""chords_audio.py — a chord lane FROM AUDIO (V54), dependency-free.

firing-31 verdict (see chordvote.py): naive audio-HMM harmony fails OUR material
— drums bury the chroma, a maj/min vocab meets all-dominant blues. So this is
NOT a full-mix HMM: it reads CQT chroma from a HARMONIC signal (a demucs
'other'/no-drums stem is ideal) and reuses chordvote's OWN template scorer +
naming, so an audio witness speaks the same maj/min/dom7 grammar as the symbolic
vote and FUSES with it (chordvote.chord_map(audio_wav=...)). On the full mix it
degrades gracefully; on a stem it is a strong second witness where transcription
is weak.

  chords_audio.py <wav> --bpm N --bars M [--key "A minor"]

Zero deps beyond librosa (already vendored for retune/analyze). librosa chroma is
C-based (index 0 = C), matching chordvote.PC — the two witnesses are aligned.
Output: [{bar, chord, conf}] + a CHORDS_AUDIO_JSON line.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def chroma_per_bar(wav, bpm, bars):
    """CQT chroma folded into `bars` bar-aligned 12-d vectors (index 0 = C).
    Uses a low-octave chroma as a separate BASS witness (chordvote's B input)."""
    import numpy as np
    import librosa
    y, sr = librosa.load(wav, sr=22050, mono=True)
    hop = 512
    C = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)                 # (12, T)
    # bass witness: chroma of the low register only (fmin C1, 3 octaves)
    try:
        Cb = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop,
                                        fmin=librosa.note_to_hz("C1"), n_octaves=3)
    except Exception:
        Cb = C
    spbar = (60.0 / float(bpm)) * 4.0            # seconds per 4/4 bar
    tpf = hop / sr
    W, B = [], []
    for b in range(int(bars)):
        f0 = int(round(b * spbar / tpf))
        f1 = int(round((b + 1) * spbar / tpf))
        seg = C[:, f0:f1]
        segb = Cb[:, f0:f1]
        W.append(seg.mean(axis=1) if seg.shape[1] else np.zeros(12))
        B.append(segb.mean(axis=1) if segb.shape[1] else np.zeros(12))
    return W, B


def _scale(v, target=4.0):
    import numpy as np
    v = np.asarray(v, dtype=float)
    s = float(v.sum())
    return v * (target / s) if s > 1e-9 else v


def chords(wav, bpm, bars, key=None, min_conf=0.2):
    """Standalone audio->chords via chordvote's scorer (index 0 = C both sides).
    min_conf drops low-confidence bars (silence/noise vote flat -> low conf)."""
    import chordvote
    W, B = chroma_per_bar(wav, bpm, bars)
    out = []
    for i in range(len(W)):
        w = list(_scale(W[i], 4.0))
        b = list(_scale(B[i], 2.5))              # bass witness, chordvote weights it x2.5
        label, conf = chordvote.vote_bar(w, b)
        if label and conf >= min_conf:
            out.append({"bar": i + 1, "chord": label, "conf": conf})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--bpm", type=float, required=True)
    ap.add_argument("--bars", type=int, required=True)
    ap.add_argument("--key", default=None)
    a = ap.parse_args()
    ch = chords(a.wav, a.bpm, a.bars, a.key)
    run = []
    for c in ch:
        if run and run[-1][1] == c["chord"]:
            run[-1][2] = c["bar"]
        else:
            run.append([c["bar"], c["chord"], c["bar"]])
    print("[chords_audio] " + "  ".join(
        (f"{x}-{z}" if z > x else f"{x}") + f":{c2}" for x, c2, z in run))
    print("CHORDS_AUDIO_JSON " + json.dumps({"bars": len(ch), "chords": ch[:16]}))


if __name__ == "__main__":
    main()
