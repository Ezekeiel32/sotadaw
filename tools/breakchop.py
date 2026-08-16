#!/usr/bin/env python3
"""THE SYMBOLIC BREAKBEAT CHOPPER — wave 86 (r-4 item 253): a break
wav becomes INSPECTABLE song.json clips — every chop a slice of the
ORIGINAL file (offsetSec + lengthBeats + sourceBpm warp), resequenced
by a genre grammar. No rendered mush: the whole break is diffable.

  chop(wav, bpm_src, target_bpm, genre, seed) -> song dict
    1. onset detection (energy-derivative — percussive material is the
       easy case; zero deps)
    2. slice classification: kick (low-dominant) / snare (broadband
       mid) / hat (high-dominant) via band shares
    3. THE SKELETON LAW (jungle grammar): kick lands on beat 1, snare
       on 2 & 4 (or 3, halftime), syncopated picks fill the 16ths,
       the last 16th of each phrase RETRIGGERS (the stutter)
    4. clips carry sourceBpm -> the engine warps (soundtouch), never
       pitch
"""
import json
import os
import sys
import wave as wv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402


def _read(path):
    w = wv.open(path, "rb")
    sr, sw, ch, n = (w.getframerate(), w.getsampwidth(), w.getnchannels(),
                     w.getnframes())
    raw = w.readframes(n)
    w.close()
    if sw == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
             | (a[:, 2].astype(np.int32) << 16))
        x = np.where(x & 0x800000, x - 0x1000000,
                     x).astype(np.float64) / 8388608.0
    else:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    return x.reshape(-1, ch).mean(axis=1), sr


def onsets(x, sr, min_gap_s=0.06):
    """Energy-derivative peaks — percussive onsets."""
    n = max(int(sr * 0.01), 1)
    m = len(x) // n
    env = np.sqrt(np.mean(x[:m * n].reshape(m, n) ** 2, axis=1))
    d = np.diff(env, prepend=env[0])
    th = np.median(env) * 0.8 + 0.05 * env.max()
    outs, last = [], -1e9
    for i in range(1, m):
        if d[i] > 0.35 * env.max() * 0.25 and env[i] > th and \
                (i * 0.01) - last >= min_gap_s:
            outs.append(i * 0.01)
            last = i * 0.01
    return outs


def classify(x, sr, t0, t1):
    """kick | snare | hat via band shares of the slice."""
    seg = x[int(t0 * sr):int(t1 * sr)]
    if len(seg) < 32:
        return "hat"
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
    freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
    tot = float(spec.sum()) or 1e-12
    low = float(spec[freqs < 150].sum()) / tot
    high = float(spec[freqs > 4000].sum()) / tot
    if low > 0.35:
        return "kick"
    if high > 0.45:
        return "hat"
    return "snare"


def chop(wav, bpm_src, target_bpm=None, genre="jungle", seed=1,
         bars=4, name="breakchop"):
    x, sr = _read(wav)
    ons = onsets(x, sr)
    if len(ons) < 4:
        raise RuntimeError(f"only {len(ons)} onsets — not a break")
    ends = ons[1:] + [len(x) / sr]
    slices = []
    for t0, t1 in zip(ons, ends):
        slices.append({"t0": t0, "dur": min(t1 - t0, 1.2),
                       "cls": classify(x, sr, t0, min(t1, t0 + 0.35))})
    by = {"kick": [], "snare": [], "hat": []}
    for i, s in enumerate(slices):
        by[s["cls"]].append(i)
    if not by["kick"] or not by["snare"]:
        raise RuntimeError(f"skeleton impossible (kicks {len(by['kick'])}, "
                           f"snares {len(by['snare'])})")
    rng = np.random.RandomState(seed)
    target_bpm = float(target_bpm or bpm_src)
    halftime = "halftime" in str(genre) or target_bpm >= 160 and \
        "jungle" not in str(genre)
    grid = []                                      # (beat, slice_idx)
    spb_src = 60.0 / float(bpm_src)
    for bar in range(bars):
        base = bar * 4.0
        grid.append((base + 0.0, by["kick"][bar % len(by["kick"])]))
        snare_beats = (2.0,) if halftime else (1.0, 3.0)
        for sb in snare_beats:
            grid.append((base + sb,
                         by["snare"][(bar + int(sb)) % len(by["snare"])]))
        # syncopated fills on off-16ths
        pool = by["hat"] or by["snare"]
        for off in (0.75, 1.5, 2.25, 2.75, 3.5):
            if rng.rand() < 0.65:
                grid.append((base + off,
                             int(rng.choice(pool + by["kick"]
                                            if off in (2.75,)
                                            else pool))))
        # THE STUTTER: the phrase's last 16th retriggers its own chop
        last_idx = grid[-1][1]
        grid.append((base + 3.75, last_idx))
        if bar % 2 == 1:
            grid.append((base + 3.875, last_idx))
    grid.sort()
    clips = []
    for beat, idx in grid:
        s = slices[idx]
        clips.append({"file": os.path.abspath(wav),
                      "startBeat": round(beat, 4),
                      "lengthBeats": round(min(s["dur"] / spb_src, 1.0), 4),
                      "offsetSec": round(s["t0"], 4),
                      "sourceBpm": round(float(bpm_src), 2)})
    song = {"version": 2, "bpm": round(target_bpm, 2), "lengthBars": bars,
            "masterGainDb": 0.0,
            "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "provenance": {"breakchop": {"source": os.path.basename(wav),
                                         "genre": genre, "seed": seed,
                                         "slices": len(slices)}},
            "tracks": [{"name": "break", "gainDb": 0.0,
                        "source": {"kind": "audio", "id": "break"},
                        "notes": [], "audioClips": clips}]}
    return song


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE BREAK CHOPPER (w86)")
    ap.add_argument("wav")
    ap.add_argument("name")
    ap.add_argument("--bpm", type=float, required=True,
                    help="the break's OWN tempo")
    ap.add_argument("--target-bpm", type=float, default=None)
    ap.add_argument("--genre", default="jungle")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--bars", type=int, default=4)
    a = ap.parse_args()
    song = chop(a.wav, a.bpm, a.target_bpm, a.genre, a.seed, a.bars)
    out = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "songs", f"{a.name}.json")
    json.dump(song, open(out, "w"), indent=1)
    print(f"[breakchop] {out}: {len(song['tracks'][0]['audioClips'])} "
          f"chops, skeleton kick@1 snare@{'3' if a.target_bpm and a.target_bpm >= 160 else '2&4'}")
