#!/usr/bin/env python3
"""A4 — THE FOURTH DIMENSION (docs/THE_PHYSICS.md §6; gap G4; laws E4/E6).

analyze2 (the ears v3) already carries integrated LUFS, momentary/short-term MAXIMA,
LRA, PSR, PLR, crest (mastering-lane S11). What the standard still had that we didn't:
  - momentary (400 ms) + short-term (3 s) LOUDNESS TIMELINES (where the dynamics live)
  - per-band L/R correlation (P13: mono-folds die in the lows first)
  - crest by SECTION (the arrangement's own dynamics map)
  - the E6 verdict: PSR vs a per-genre floor (KG MixTarget when present, else the
    published-practice seed table below — D3 PENDING Chezy, provenance marked)
  - reference-meter VALIDATION: this meter vs ffmpeg ebur128 + pyloudnorm on
    constructed knowns, +/-0.5 LU (the EB4 proof bar)

This tool implements the STANDARD BS.1770 channel-summed formulation (per-channel
K-weighting, power sum) — analyze2's mono-sum contract is its own and stays untouched
(D6 stays Chezy's). Both are right; they answer different questions.

usage:
  dynamics_ears.py <wav> [--song songs/x.json] [--genre g]
  dynamics_ears.py --validate [--keep]     reference-meter agreement battery
Prints DYN_JSON <payload>. --validate exit 0 = all deltas inside the bar.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter, resample_poly, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")

# PSR floors live in ONE place (tools/psr_floors.py — the D6 no-spaghetti law);
# this tool READS them through that single resolver (KG-first, seed fallback).
sys.path.insert(0, os.path.join(ROOT, "tools"))                              # noqa: E402
import psr_floors as _psr_floors                                              # noqa: E402

BANDS = (("low_20_120", 20, 120), ("lowmid_120_500", 120, 500),
         ("mid_500_2k", 500, 2000), ("himid_2k_6k", 2000, 6000),
         ("high_6k_up", 6000, None))


def _db(v, floor=-200.0):
    return round(20.0 * math.log10(v), 2) if v > 10 ** (floor / 20.0) else floor


def k_weight(x, sr):
    """BS.1770-4 K-weighting (fs-adaptive two-stage, pyloudnorm constants)."""
    _Q1 = 0.7071752369554193
    K1 = np.tan(np.pi * 1681.9744509555319 / sr)
    Vh = 10.0 ** (3.99984385397 / 20.0)
    Vb = Vh ** 0.4996667741545416
    a0 = 1.0 + K1 / _Q1 + K1 * K1
    b_sh = np.array([(Vh + Vb * K1 / _Q1 + K1 * K1) / a0,
                     2.0 * (K1 * K1 - Vh) / a0,
                     (Vh - Vb * K1 / _Q1 + K1 * K1) / a0])
    a_sh = np.array([1.0, 2.0 * (K1 * K1 - 1.0) / a0,
                     (1.0 - K1 / _Q1 + K1 * K1) / a0])
    _Q2 = 0.5003270373253953
    K2 = np.tan(np.pi * 38.13547087613982 / sr)
    a0h = 1.0 + K2 / _Q2 + K2 * K2
    b_hp = np.array([1.0, -2.0, 1.0])
    a_hp = np.array([1.0, 2.0 * (K2 * K2 - 1.0) / a0h,
                     (1.0 - K2 / _Q2 + K2 * K2) / a0h])
    return lfilter(b_hp, a_hp, lfilter(b_sh, a_sh, x, axis=0), axis=0)


def block_loudness(z2sum, sr, win_s, hop_s=0.1):
    """LUFS of sliding windows over the CHANNEL-SUMMED squared K-weighted signal."""
    w = int(round(win_s * sr))
    h = max(1, int(round(hop_s * sr)))
    if len(z2sum) < w:
        return np.array([]), np.array([])
    c = np.concatenate(([0.0], np.cumsum(z2sum)))
    starts = np.arange(0, len(z2sum) - w + 1, h)
    ms = (c[starts + w] - c[starts]) / w
    out = np.full(ms.shape, -np.inf)
    nz = ms > 0
    out[nz] = -0.691 + 10.0 * np.log10(ms[nz])
    return out, starts / sr


def true_peak_db(x, sr):
    tp = 0.0
    CH = sr * 30
    for c in range(x.shape[1]):
        for s in range(0, len(x), CH):
            seg = x[max(0, s - 64):min(len(x), s + CH + 64), c]
            tp = max(tp, float(np.max(np.abs(resample_poly(seg, 4, 1)))))
    return _db(tp)


def measure(path):
    x, sr = sf.read(path, always_2d=True, dtype="float64")
    z = k_weight(x, sr)
    z2 = (z ** 2).sum(axis=1)              # BS.1770 channel power sum (G_i = 1 for L/R)

    mom, mt = block_loudness(z2, sr, 0.4)
    st, stt = block_loudness(z2, sr, 3.0)

    def gated_mean(blocks, rel_gate):
        b = blocks[blocks >= -70.0]
        if not b.size:
            return None
        e = 10.0 ** ((b + 0.691) / 10.0)
        thr = (-0.691 + 10.0 * np.log10(e.mean())) + rel_gate
        g = b[b >= thr]
        if not g.size:
            return None
        return -0.691 + 10.0 * np.log10(np.mean(10.0 ** ((g + 0.691) / 10.0)))

    integrated = gated_mean(mom, -10.0)
    lra = None
    stf = st[np.isfinite(st)]
    absg = stf[stf >= -70.0]
    if absg.size >= 2:
        e = 10.0 ** ((absg + 0.691) / 10.0)
        rel = (-0.691 + 10.0 * np.log10(e.mean())) - 20.0
        g = absg[absg >= rel]
        if g.size >= 2:
            lra = float(np.percentile(g, 95) - np.percentile(g, 10))

    tp = true_peak_db(x, sr)
    st_max = float(stf.max()) if stf.size else None
    mom_f = mom[np.isfinite(mom)]
    mom_max = float(mom_f.max()) if mom_f.size else None
    psr = round(tp - st_max, 2) if st_max is not None else None
    plr = round(tp - integrated, 2) if integrated is not None else None

    def strip(vals, times, n=200):
        if not len(vals):
            return []
        k = max(1, len(vals) // n)
        return [[round(float(times[i]), 2),
                 (round(float(vals[i]), 2) if np.isfinite(vals[i]) else None)]
                for i in range(0, len(vals), k)]

    # per-band L/R correlation (P13): the lows are where mono-folds die
    band_corr = {}
    if x.shape[1] >= 2:
        for name, lo, hi in BANDS:
            hi_eff = min(hi or sr / 2 - 100, sr / 2 - 100)
            sos = butter(4, [lo, hi_eff], btype="bandpass", fs=sr, output="sos")
            L = sosfilt(sos, x[:, 0])
            R = sosfilt(sos, x[:, 1])
            d = math.sqrt(float(np.mean(L ** 2)) * float(np.mean(R ** 2)))
            band_corr[name] = round(float(np.mean(L * R) / d), 3) if d > 1e-14 else None

    ax = np.abs(x).max(axis=1)
    crest = round(_db(float(ax.max())) - _db(float(np.sqrt(np.mean(x ** 2)))), 2)

    return {
        "file": path, "sample_rate": sr, "duration_s": round(len(x) / sr, 2),
        "lufs_integrated": round(integrated, 2) if integrated is not None else None,
        "lufs_momentary_max": round(mom_max, 2) if mom_max is not None else None,
        "lufs_short_term_max": round(st_max, 2) if st_max is not None else None,
        "lra": round(lra, 2) if lra is not None else None,
        "true_peak_dbtp": tp, "psr": psr, "plr": plr, "crest_db": crest,
        "momentary_timeline": strip(mom, mt),
        "short_term_timeline": strip(st, stt),
        "band_lr_correlation": band_corr,
        "_x": x, "_sr": sr, "_ax": ax,
    }


def section_crests(m, song):
    bpm = float(song.get("bpm", 120.0))
    if song.get("tempoMap"):
        m["note_tempo"] = "tempoMap present: section times use base bpm (approx)"
    beats_per_bar = 4.0
    secs = song.get("sections") or []
    x, sr, ax = m["_x"], m["_sr"], m["_ax"]
    out = []
    total_bars = float(song.get("lengthBars", 0)) or (len(x) / sr) / (beats_per_bar * 60 / bpm)
    for i, s in enumerate(secs):
        b0 = float(s.get("startBar", 0))
        b1 = float(secs[i + 1].get("startBar")) if i + 1 < len(secs) else total_bars
        t0, t1 = (b0 * beats_per_bar * 60 / bpm), (b1 * beats_per_bar * 60 / bpm)
        i0, i1 = int(t0 * sr), min(len(x), int(t1 * sr))
        if i1 - i0 < sr // 4:
            continue
        seg = x[i0:i1]
        pk = float(np.abs(seg).max())
        rms = float(np.sqrt(np.mean(seg ** 2)))
        out.append({"section": s.get("name", f"s{i}"), "bars": [b0, b1],
                    "crest_db": round(_db(pk) - _db(rms), 2)})
    return out


def psr_floor_for(genre):
    """Delegate to the single PSR resolver (tools/psr_floors.py) — KG-first with
    subgenre inheritance, published-practice seed fallback, default. E6."""
    return _psr_floors.floor_for_genre(genre)


# ---------------------------------------------------------------- validation
def _ffmpeg_ebur128(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path,
                        "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=300)
    e = r.stderr
    out = {}
    m = re.search(r"Integrated loudness:.*?I:\s*(-?[\d.]+) LUFS", e, re.S)
    if m:
        out["I"] = float(m.group(1))
    m = re.search(r"Loudness range:.*?LRA:\s*(-?[\d.]+) LU", e, re.S)
    if m:
        out["LRA"] = float(m.group(1))
    m = re.search(r"True peak:.*?Peak:\s*(-?[\d.]+) dBFS", e, re.S)
    if m:
        out["TP"] = float(m.group(1))
    svals = [float(v) for v in re.findall(r"S:\s*(-?[\d.]+) LUFS", e)
             if float(v) > -70]
    if svals:
        out["S_max"] = max(svals)
    return out


def _known(path, kind, sr=48000):
    t = lambda s: np.arange(int(s * sr)) / sr
    if kind == "steady":
        x = 10 ** (-18 / 20) * np.sin(2 * np.pi * 997 * t(12))
    elif kind == "two_level":
        a = 10 ** (-33 / 20) * np.sin(2 * np.pi * 997 * t(10))
        b = 10 ** (-13 / 20) * np.sin(2 * np.pi * 997 * t(10))
        x = np.concatenate([a, b])
    else:  # bursts
        rng = np.random.default_rng(7)
        n = rng.standard_normal(int(24 * sr))
        sos = butter(2, [80, 8000], btype="bandpass", fs=sr, output="sos")
        n = sosfilt(sos, n)
        n /= np.abs(n).max() + 1e-12
        env = np.ones(len(n)) * 10 ** (-30 / 20)
        seg = int(3 * sr)
        for i in range(0, len(n), 2 * seg):
            env[i:i + seg] = 10 ** (-14 / 20)
        x = n * env * 0.9
    sf.write(path, np.stack([x, x], axis=1), sr, subtype="FLOAT")
    return path


def validate(keep=False):
    tmp = os.path.join(SONGS, "_dyn_val")
    os.makedirs(tmp, exist_ok=True)
    checks, fails = [], []

    def check(nm, ok, detail):
        checks.append({"name": nm, "ok": bool(ok), "detail": detail})
        if not ok:
            fails.append(nm)
        print(("  ok " if ok else "FAIL ") + f"{nm}  {detail}", flush=True)

    cases = [("steady", 0.5), ("two_level", 0.5), ("bursts", 0.5)]
    real = os.path.join(SONGS, "eval_funk.wav")
    if os.path.exists(real):
        cases.append((real, 0.5))
    try:
        for kind, bar in cases:
            path = kind if os.path.sep in kind else _known(
                os.path.join(tmp, f"{kind}.wav"), kind)
            mine = measure(path)
            ref = _ffmpeg_ebur128(path)
            try:
                import pyloudnorm
                x, sr = sf.read(path, always_2d=True)
                pl = float(pyloudnorm.Meter(sr).integrated_loudness(x))
            except Exception:
                pl = None
            nm = os.path.basename(path)
            if "I" in ref and mine["lufs_integrated"] is not None:
                d = abs(mine["lufs_integrated"] - ref["I"])
                check(f"{nm} I vs ffmpeg (+/-{bar})", d <= bar,
                      f"{mine['lufs_integrated']} vs {ref['I']} (d={d:.2f})")
            if pl is not None and mine["lufs_integrated"] is not None:
                d = abs(mine["lufs_integrated"] - pl)
                check(f"{nm} I vs pyloudnorm (+/-{bar})", d <= bar,
                      f"{mine['lufs_integrated']} vs {round(pl, 2)} (d={d:.2f})")
            if "LRA" in ref and mine["lra"] is not None:
                d = abs(mine["lra"] - ref["LRA"])
                check(f"{nm} LRA vs ffmpeg (+/-{bar})", d <= bar,
                      f"{mine['lra']} vs {ref['LRA']} (d={d:.2f})")
            if "S_max" in ref and mine["lufs_short_term_max"] is not None:
                d = abs(mine["lufs_short_term_max"] - ref["S_max"])
                check(f"{nm} STmax vs ffmpeg (+/-{bar})", d <= bar,
                      f"{mine['lufs_short_term_max']} vs {ref['S_max']} (d={d:.2f})")
            if "TP" in ref:
                d = abs(mine["true_peak_dbtp"] - ref["TP"])
                check(f"{nm} TP vs ffmpeg (+/-0.4dB)", d <= 0.4,
                      f"{mine['true_peak_dbtp']} vs {ref['TP']} (d={d:.2f})")
        result = {"pass": not fails, "failing": fails, "checks": checks}
    finally:
        if not keep:
            shutil.rmtree(tmp, ignore_errors=True)
    print("DYN_JSON " + json.dumps(result))
    print(f"\n== DYNAMICS EARS: {len(checks) - len(fails)} pass / {len(fails)} fail ==")
    return 0 if not fails else 1


# ---------------------------------------------------------------- cli
def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if a[0] == "--validate":
        return validate("--keep" in a)

    def opt(flag):
        return a[a.index(flag) + 1] if flag in a else None

    m = measure(a[0])
    song_path, genre = opt("--song"), opt("--genre")
    src = None
    if song_path:
        song = json.load(open(song_path))
        m["sections_crest"] = section_crests(m, song)
        if not genre:                              # per-song intelligent resolve (E6)
            floor, src, genre = _psr_floors.floor_for_song(song)
    if genre and src is None:                      # explicit --genre path
        floor, src = psr_floor_for(genre)
    if genre:
        m["psr_floor"] = {"genre": genre, "floor": floor, "source": src,
                          "verdict": ("PASS" if (m["psr"] or 99) >= floor else
                                      f"UNDER FLOOR: psr {m['psr']} < {floor} — "
                                      f"over-limited for {genre} (E6)")}
    for k in ("_x", "_sr", "_ax"):
        m.pop(k, None)
    print("DYN_JSON " + json.dumps(m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
