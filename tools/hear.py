#!/usr/bin/env python3
"""hear.py — THE SOUND TENSOR: RGB-for-audio LLM perception (task #32).

analyze2 gives NUMBERS (LUFS, centroid, band %) — summary statistics. hear gives
SIGHT: a mel-band x time grid the model reads like an image. Builds, drops, dead
zones, spectral collapse, echo tails — visible in one glance instead of inferred
from scalars. (The funk top-end collapse that needed a judge to catch would show
here as an empty upper third.)

  hear.py <wav> [--bpm N] [--json] [--rows 14] [--cols 96]

Default output = ASCII heatmap: rows are mel bands (TOP = high freq), cols are
time (bar ruler when --bpm given), chars ' .:-=+*#%@' = dB intensity within the
file's own dynamic range. --json emits the raw tensor {bands_hz, t_step_s, grid
(rows x cols, 0-9), onsets (0-9 per col)} for programmatic reading.

Reading guide (also printed): a healthy build fills rows bottom-up over time; a
drop = sudden full-column jump; the hat/air lives in the top 3 rows; an empty
top third on a horn/lead genre = the spectral_presence failure; silence gaps and
echo tails are visible as column fades.
"""
import argparse, json, math, sys, wave
import numpy as np


def load_wav(path):
    try:                        # soundfile-first: float32 stems (THE CLEAN
        import soundfile as sf  # SPLIT) crash stdlib wave with 'format: 3'
        x, sr = sf.read(path, dtype="float64", always_2d=False)
        if x.ndim > 1:
            x = x.mean(axis=1)
        return sr, x
    except Exception:
        pass
    w = wave.open(path, "rb")
    sr, sw, nch = w.getframerate(), w.getsampwidth(), w.getnchannels()
    raw = w.readframes(w.getnframes()); w.close()
    if sw == 3:                                   # m1 renders 24-bit
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3)
        x = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        x = (x - (x >> 23 << 24)).astype(np.float64) / 8388608.0
    elif sw == 2:
        x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768.0
    else:
        x = np.frombuffer(raw, np.uint8).astype(np.float64) / 128.0 - 1.0
    if nch > 1:
        x = x.reshape(-1, nch).mean(axis=1)
    return sr, x


def mel_edges(n_bands, fmin=25.0, fmax=12000.0):
    m = lambda f: 2595.0 * math.log10(1 + f / 700.0)
    mi = lambda v: 700.0 * (10 ** (v / 2595.0) - 1)
    return [mi(m(fmin) + (m(fmax) - m(fmin)) * i / n_bands) for i in range(n_bands + 1)]


def sound_tensor(path, bpm=None, rows=14, cols=96):
    sr, x = load_wav(path)
    dur = len(x) / sr
    hop = max(256, len(x) // cols)
    n_frames = len(x) // hop
    edges = mel_edges(rows)
    # per-frame band energies via rFFT on each hop window
    win = np.hanning(hop)
    grid_db = np.full((rows, n_frames), -90.0)
    onset = np.zeros(n_frames)
    prev = None
    fr = np.fft.rfftfreq(hop, 1 / sr)
    band_idx = [(np.searchsorted(fr, edges[i]), np.searchsorted(fr, edges[i + 1]))
                for i in range(rows)]
    for f in range(n_frames):
        seg = x[f * hop:(f + 1) * hop] * win
        S = np.abs(np.fft.rfft(seg)) ** 2
        for b, (lo, hi) in enumerate(band_idx):
            e = S[lo:max(hi, lo + 1)].mean()
            grid_db[b, f] = 10 * math.log10(e + 1e-12)
        flux = float(np.maximum(0, S - prev).sum()) if prev is not None else 0.0
        onset[f] = flux
        prev = S
    # normalize each into 0..9 within the file's own dynamics
    top = grid_db.max()
    grid = np.clip((grid_db - (top - 48.0)) / 48.0 * 9.0, 0, 9).astype(int)
    o9 = np.clip(onset / (onset.max() + 1e-12) * 9.0, 0, 9).astype(int)
    # downsample to cols
    if n_frames > cols:
        idx = np.linspace(0, n_frames - 1, cols).astype(int)
        grid, o9 = grid[:, idx], o9[idx]
    return {"sr": sr, "dur_s": round(dur, 2), "rows": rows, "cols": grid.shape[1],
            "band_hz": [round(e) for e in edges], "hop_s": round(hop / sr, 4),
            "bpm": bpm, "grid": grid.tolist(), "onsets": o9.tolist()}


CHARS = " .:-=+*#%@"

def ascii_view(t):
    lines = [f"hear: {t['dur_s']}s, {t['rows']} mel bands (top=high) x {t['cols']} cols"
             + (f", bpm {t['bpm']}" if t['bpm'] else "")]
    grid = t["grid"]
    for r in range(t["rows"] - 1, -1, -1):        # top row = highest band
        hz = t["band_hz"][r + 1]
        label = f"{hz/1000:.1f}k" if hz >= 1000 else f"{hz:3.0f} "
        lines.append(f"{label:>5}|" + "".join(CHARS[v] for v in grid[r]))
    lines.append("  ons|" + "".join(CHARS[v] for v in t["onsets"]))
    if t["bpm"]:
        spb = 60.0 / t["bpm"]
        bars_total = t["dur_s"] / (4 * spb)
        ruler = [" "] * t["cols"]
        for bar in range(0, int(bars_total) + 1, 4):
            c = int(bar * 4 * spb / t["dur_s"] * t["cols"])
            if c < t["cols"]:
                for i, ch in enumerate(str(bar + 1)):
                    if c + i < t["cols"]: ruler[c + i] = ch
        lines.append("  bar|" + "".join(ruler))
    lines.append("read: builds fill bottom-up; a drop = full-column jump; top 3 rows = hats/air "
                 "(empty top third on a lead/horn genre = spectral collapse); column fades = tails/gaps")
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--bpm", type=float, default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--rows", type=int, default=14)
    ap.add_argument("--cols", type=int, default=96)
    a = ap.parse_args()
    t = sound_tensor(a.wav, a.bpm, a.rows, a.cols)
    print(json.dumps(t) if a.json else ascii_view(t))
