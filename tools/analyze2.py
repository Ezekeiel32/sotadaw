#!/usr/bin/env python3
"""The 'ears' v3: measure a WAV and emit agent-readable JSON.
Dtype-aware, LUFS (pyloudnorm), band balance, f0, true peak (4x oversampled dBTP),
stereo width + L/R correlation, key estimate (Krumhansl-Schmuckler over chromagram),
and per-quarter gradients (rms/centroid) so MOTION (automation) is measurable."""
import json, sys
import numpy as np
from scipy.io import wavfile

KS_MAJOR = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
KS_MINOR = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
NOTE_NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

def estimate_key(x, sr):
    """Coarse chromagram (8192-pt frames) -> K-S profile correlation -> (key, confidence)."""
    n_fft, hop = 8192, 4096
    if len(x) < n_fft:
        return None, 0.0
    chroma = np.zeros(12)
    freqs = np.fft.rfftfreq(n_fft, 1 / sr)
    mask = (freqs >= 55) & (freqs <= 5000)
    midi = np.zeros_like(freqs, dtype=int)
    midi[mask] = np.round(69 + 12 * np.log2(freqs[mask] / 440.0)).astype(int)
    win = np.hanning(n_fft)
    for start in range(0, len(x) - n_fft, hop):
        X = np.abs(np.fft.rfft(x[start:start + n_fft] * win)) ** 2
        for pc in range(12):
            chroma[pc] += X[mask & (midi % 12 == pc)].sum()
    if chroma.sum() <= 0:
        return None, 0.0
    chroma /= chroma.sum()
    scores = []
    for rot in range(12):
        c = np.roll(chroma, -rot)
        scores.append(("%s major" % NOTE_NAMES[rot], float(np.corrcoef(c, KS_MAJOR)[0, 1])))
        scores.append(("%s minor" % NOTE_NAMES[rot], float(np.corrcoef(c, KS_MINOR)[0, 1])))
    scores.sort(key=lambda s: -s[1])
    best, second = scores[0], scores[1]
    conf = round(max(0.0, best[1] - second[1]) * 10, 2)   # gap-based confidence, ~0..1+
    return best[0], min(1.0, conf)

def _psd(x, sr, win=65536, hop=32768):
    """Windowed power spectrum accumulator — bounded memory at ANY duration
    (the single whole-file FFT OOM'd on the first 12-minute render)."""
    if len(x) <= win:
        w = x * np.hanning(len(x))
        return np.abs(np.fft.rfft(w)).astype(np.float64) ** 2, np.fft.rfftfreq(len(x), 1 / sr)
    h = np.hanning(win)
    acc = np.zeros(win // 2 + 1)
    for s in range(0, len(x) - win, hop):
        acc += np.abs(np.fft.rfft(x[s:s + win] * h)) ** 2
    return acc, np.fft.rfftfreq(win, 1 / sr)


def analyze(path):
    sr, x = wavfile.read(path)
    if x.dtype == np.int16:
        x = x.astype(np.float32) / 32768.0
    elif x.dtype == np.int32:
        x = x.astype(np.float32) / 2147483648.0
    else:
        x = x.astype(np.float32)
    stereo = x if (x.ndim > 1 and x.shape[1] >= 2) else None
    if x.ndim > 1:
        x = x.mean(axis=1)

    n = len(x)
    dur = n / sr
    ax = np.abs(x)
    peak = float(np.max(ax)) if n else 0.0
    rms = float(np.sqrt(np.mean(x.astype(np.float64) ** 2))) if n else 0.0
    clipped_samples = int(np.sum(ax >= 0.999))            # non-saturating: shows PROGRESS near 0 dBFS
    peak_p999 = float(np.percentile(ax, 99.9)) if n else 0.0

    P, f = _psd(x, sr)
    tot = float(P.sum()) + 1e-12
    def band(lo, hi):
        m = (f >= lo) & (f < hi)
        return round(float(P[m].sum()) / tot * 100.0, 1)
    Xm = np.sqrt(P)
    centroid = float((f * Xm).sum() / (Xm.sum() + 1e-9))

    seg = x[: int(min(1.0, dur) * sr)]
    if len(seg) > 64:
        Xs = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        fs = np.fft.rfftfreq(len(seg), 1 / sr)
        m = (fs > 20) & (fs < 2000)
        f0 = float(fs[m][np.argmax(Xs[m])]) if m.any() else 0.0
    else:
        f0 = 0.0

    lufs = None
    band_lufs = None
    try:
        import pyloudnorm
        meter = pyloudnorm.Meter(sr)
        lufs = round(float(meter.integrated_loudness(x)), 2)
        # per-band LUFS (V24): loudness CONTRIBUTION per band — band-energy % says how the
        # spectrum divides, band LUFS says how LOUD each lane is in absolute terms.
        try:
            from scipy.signal import butter, sosfilt
            band_lufs = {}
            for name, lo, hi in (("low_20_120", 20, 120), ("lowmid_120_500", 120, 500),
                                 ("mid_500_2k", 500, 2000), ("himid_2k_6k", 2000, 6000),
                                 ("high_6k_up", 6000, None)):
                if hi is None or hi >= sr / 2:
                    sos = butter(4, lo, btype="highpass", fs=sr, output="sos")
                else:
                    sos = butter(4, [lo, hi], btype="bandpass", fs=sr, output="sos")
                v = float(meter.integrated_loudness(sosfilt(sos, x)))
                band_lufs[name] = round(v, 2) if np.isfinite(v) else None
        except Exception:
            band_lufs = None
    except Exception:
        pass

    # windowed loudness (EBU R128 / ITU-R BS.1770-4 K-weighting): momentary (400ms) +
    # short-term (3s) maxima and LRA (loudness range) — the dynamics the integrated value
    # hides. Computed on the SAME mono sum as lufs_integrated (consistent with KG targets).
    lufs_momentary_max = lufs_short_term_max = lra = None
    try:
        from scipy.signal import lfilter
        # sample-rate-adaptive K-weighting (pyloudnorm / ITU-R BS.1770-4 constants)
        _Q1 = 0.7071752369554193
        K1 = np.tan(np.pi * 1681.9744509555319 / sr)
        Vh = 10.0 ** (3.99984385397 / 20.0); Vb = Vh ** 0.4996667741545416
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
        z = lfilter(b_hp, a_hp, lfilter(b_sh, a_sh, x.astype(np.float64)))
        z2 = z * z
        csum = np.concatenate(([0.0], np.cumsum(z2)))
        def _win_loud(win_s, hop_s=0.1):
            w = int(round(win_s * sr)); h = max(1, int(round(hop_s * sr)))
            if w < 1 or len(z2) < w:
                return np.array([])
            starts = np.arange(0, len(z2) - w + 1, h)
            ms = (csum[starts + w] - csum[starts]) / w        # block mean-squares (vectorized)
            out = np.full(ms.shape, -np.inf)
            nz = ms > 0
            out[nz] = -0.691 + 10.0 * np.log10(ms[nz])        # BS.1770 loudness of each block
            return out
        mom = _win_loud(0.4); stl = _win_loud(3.0)
        mf = mom[np.isfinite(mom)]; sf = stl[np.isfinite(stl)]
        if mf.size: lufs_momentary_max = round(float(mf.max()), 2)
        if sf.size: lufs_short_term_max = round(float(sf.max()), 2)
        # INTEGRATED FALLBACK (2026-07-13, the Inspiron null-LUFS crash): a
        # public install without pyloudnorm emitted lufs_integrated null and
        # the sidecar's loudness pass died on float(None) — but BS.1770-4
        # integrated is just these same 400ms/75%-overlap K-weighted blocks
        # through the two gates (abs -70, relative mean-10 LU). Ears never
        # depend on an optional wheel again.
        if (lufs is None or not np.isfinite(lufs)) and mf.size:
            absg_i = mf[mf >= -70.0]
            if absg_i.size:
                rel_i = (-0.691 + 10.0 * np.log10(
                    np.mean(10.0 ** ((absg_i + 0.691) / 10.0)))) - 10.0
                g_i = absg_i[absg_i >= rel_i]
                if g_i.size:
                    lufs = round(float(-0.691 + 10.0 * np.log10(
                        np.mean(10.0 ** ((g_i + 0.691) / 10.0)))), 2)
        # LRA (EBU Tech 3342): abs-gate -70 LU, relative-gate (mean-20 LU), P95-P10 spread
        absg = sf[sf >= -70.0]
        if absg.size >= 2:
            mean_ms = np.mean(10.0 ** ((absg + 0.691) / 10.0))
            rel = (-0.691 + 10.0 * np.log10(mean_ms)) - 20.0
            g = absg[absg >= rel]
            if g.size >= 2:
                lra = round(float(np.percentile(g, 95) - np.percentile(g, 10)), 2)
    except Exception:
        pass

    def dbfs(v):
        return round(20 * np.log10(v), 2) if v > 1e-9 else -120.0

    # true peak: 4x oversample (inter-sample overs that plain peak misses) — chunked
    # so a 12-minute render doesn't 4x itself into the OOM killer
    try:
        from scipy.signal import resample_poly
        true_peak, CH = 0.0, sr * 30
        for s in range(0, n, CH):
            seg = x[max(0, s - 64): min(n, s + CH + 64)]
            true_peak = max(true_peak, float(np.max(np.abs(resample_poly(seg, 4, 1)))))
    except Exception:
        true_peak = peak

    # stereo image: side/mid energy + L/R correlation (1 = mono, ~0 = wide, <0 = phase risk)
    width_db, lr_corr = None, None
    if stereo is not None:
        L, R = stereo[:, 0], stereo[:, 1]
        mid, side = (L + R) * 0.5, (L - R) * 0.5
        rm, rs = np.sqrt(np.mean(mid ** 2)) + 1e-12, np.sqrt(np.mean(side ** 2))
        width_db = dbfs(rs / rm) if rs > 1e-9 else -120.0
        denom = np.sqrt(np.mean(L ** 2) * np.mean(R ** 2))
        lr_corr = round(float(np.mean(L * R) / denom), 3) if denom > 1e-12 else 1.0

    key_name, key_conf = estimate_key(x, sr)

    # dynamics ratios pros master by: crest (peak/RMS), PLR (true-peak - integrated LUFS,
    # whole-track headroom), PSR (true-peak - loudest short-term, the over-limiting tell).
    tp_db = dbfs(true_peak)
    crest_db = round(dbfs(peak) - dbfs(rms), 2) if (peak > 1e-9 and rms > 1e-9) else None
    plr = round(tp_db - lufs, 2) if lufs is not None else None
    psr = round(tp_db - lufs_short_term_max, 2) if lufs_short_term_max is not None else None

    # gradients over time (quarters) — automation/motion shows up HERE
    q = max(1, n // 4)
    rms_by_q, cen_by_q = [], []
    for qi in range(4):
        seg_q = x[qi * q: (qi + 1) * q]
        if len(seg_q) < 256:
            break
        rms_by_q.append(dbfs(float(np.sqrt(np.mean(seg_q.astype(np.float64) ** 2)))))
        Pq, fq = _psd(seg_q, sr)
        Xq = np.sqrt(Pq)
        cen_by_q.append(round(float((fq * Xq).sum() / (Xq.sum() + 1e-9))))

    return {
        "file": path,
        "duration_s": round(dur, 2),
        "sample_rate": sr,
        "peak_dbfs": dbfs(peak),
        "true_peak_dbtp": dbfs(true_peak),
        "peak_p999_dbfs": dbfs(peak_p999),
        "clipped_samples": clipped_samples,
        "rms_db": dbfs(rms),
        # true silence stays honest null (never -inf: json -Infinity breaks
        # non-python consumers and float(-inf) poisons downstream arithmetic)
        "lufs_integrated": (lufs if lufs is not None
                            and np.isfinite(lufs) else None),
        "lufs_momentary_max": lufs_momentary_max,
        "lufs_short_term_max": lufs_short_term_max,
        "lra": lra,
        "crest_factor_db": crest_db,
        "plr": plr,
        "psr": psr,
        "clipping": bool(clipped_samples > 0),
        "key_estimate": key_name,
        "key_confidence": key_conf,
        "stereo_width_db": width_db,
        "lr_correlation": lr_corr,
        "rms_by_quarter_db": rms_by_q,
        "centroid_by_quarter_hz": cen_by_q,
        "spectral_centroid_hz": round(centroid),
        "f0_hz": round(f0, 1),
        "band_energy_pct": {
            "low_20_120": band(20, 120),
            "lowmid_120_500": band(120, 500),
            "mid_500_2k": band(500, 2000),
            "himid_2k_6k": band(2000, 6000),
            "high_6k_up": band(6000, sr / 2),
        },
        "band_lufs": band_lufs,
    }

if __name__ == "__main__":
    print(json.dumps([analyze(p) for p in sys.argv[1:]] if len(sys.argv) > 2
                     else analyze(sys.argv[1]), indent=1))
