#!/usr/bin/env python3
"""SPECTRAL CAPTURE: audio -> editable MIDI -> audio, at reconstruction fidelity.

The musical rails (transcribe_stems.py) answer "what notes were played" — great
for editing, hopeless for reconstruction (a note list throws the SOUND away).
This tool answers the other question: "what is this audio, AS notes" — the
McAulay-Quatieri / SMS answer, engineered for a DAW:

  ANALYSIS   dual-band STFT (long window <250Hz so 808 stacks resolve, short
             window above so attacks don't smear) -> per-frame peak picking
             (parabolic interp on log magnitude) -> greedy partial tracking
             (birth/death, gap bridging) -> every partial IS a MIDI note:
             pitch = nearest semitone, vel = peak amplitude, plus per-note
             envelopes: bend[] (cents vs the semitone, RDP-decimated),
             gain[] (linear amp, RDP-decimated), ph0 + sparse phase locks.
             What the sine model can't say (breath, hats, room) is measured
             as a 26-band mel noise floor -> band-energy notes on a noise lane.

  RENDER     deterministic additive resynthesis: cubic-phase MQ oscillators
             follow each note's bend/gain envelopes from its birth phase,
             drifting phase re-locked at sparse checkpoints (waveform-level
             match, not just spectral); noise notes shape a seeded white
             noise STFT. Same capture -> bit-identical render, every time.

  LOSSLESS   the render is subtracted from the original IN INTEGER DOMAIN and
             the difference ships as a residual layer: render + residual ==
             the original file, byte for byte (int16/int24 sources). Edit the
             MIDI and the residual stays as texture — graceful, never broken.

  VERIFY     honest metrics, no vibes: spectral fidelity % (mel-magnitude
             match), waveform correlation @ best lag, SI-SDR, per-octave
             envelope agreement, byte-exact bool. The headline number is
             spectral fidelity; the others are printed right next to it.

Editability contract: notes in song.json stay plain {start,len,pitch,vel} —
the piano roll doesn't change. The envelopes live in a sidecar
(songs/<name>_spectral/capture.json) keyed by note identity; at render time
current song notes are matched back to captured notes (exact match when
unedited -> byte-exact holds; moved/transposed/stretched notes carry their
envelopes along, transformed; brand-new notes synthesize clean).

CLI:
  spectral.py capture  in.wav  --name mysong [--mode lossless|spectral]
                       [--bpm 120] [--t0 A --t1 B] [--into songs/x.json]
  spectral.py render   songs/<name>_spectral/capture.json out.wav
                       [--song songs/x.json] [--lossless]
  spectral.py verify   original.wav render.wav [--json]
  spectral.py roundtrip in.wav [--mode ...]   # capture -> render -> verify
  spectral.py selftest                        # fast numerical proof (no files)

Battery: tools/spectral_battery.py (thresholds asserted on synthetic + real).
"""
import argparse, json, math, os, sys, time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")

TWO_PI = 2.0 * math.pi
NOISE_SEED = 0x50C7DA  # deterministic noise identity: same capture -> same render
NOISE_BANDS = 26
NOISE_PITCH0 = 24        # noise band b lands on MIDI pitch 24+b (C1..C3 rows)
DB_FLOOR = -90.0         # absolute analysis floor vs global peak

# ---------------------------------------------------------------------- progress
class Prog:
    """Structured progress: human line + machine line ('[prog] {json}') on stdout.
    Stages carry weights so the whole run reads as one honest 0..100%."""

    def __init__(self, stages, label="spectral", quiet=False):
        self.label = label
        self.quiet = quiet
        self.stages = [s for s, _ in stages]
        tot = sum(w for _, w in stages) or 1.0
        self.w = {s: w / tot for s, w in stages}
        self.base = {}
        acc = 0.0
        for s, _ in stages:
            self.base[s] = acc
            acc += self.w[s]
        self.t0 = time.time()
        self._last = 0.0

    def emit(self, stage, frac, msg=""):
        frac = min(1.0, max(0.0, frac))
        pct = 100.0 * (self.base.get(stage, 0.0) + self.w.get(stage, 0.0) * frac)
        now = time.time()
        if now - self._last < 0.15 and frac < 1.0:      # <=~7Hz on the wire
            return
        self._last = now
        eta = (now - self.t0) * (100.0 - pct) / pct if pct > 1.0 else -1.0
        if not self.quiet:
            line = {"stage": stage, "pct": round(pct, 1), "msg": msg,
                    "eta_s": round(eta, 1), "elapsed_s": round(now - self.t0, 1),
                    "label": self.label}
            print(f"[prog] {json.dumps(line)}", flush=True)

    def say(self, msg):
        if not self.quiet:
            print(f"[spectral] {msg}", flush=True)


_NULL_PROG = Prog([("x", 1.0)], quiet=True)

# ---------------------------------------------------------------------- audio io
def load_audio(path, prefer_int=True):
    """Returns dict: sr, mono float64 x, orig (channels x n float64), int_data
    (original integer samples, or None), int_kind ('int16'/'int24'/None).
    mp3/anything-not-wav decodes via soundfile/librosa to float."""
    import soundfile as sf
    int_data, int_kind = None, None
    try:
        info = sf.info(path)
        if prefer_int and info.subtype in ("PCM_16", "PCM_24", "PCM_32"):
            bits = {"PCM_16": 16, "PCM_24": 24, "PCM_32": 32}[info.subtype]
            raw, sr = sf.read(path, dtype="int32", always_2d=True)   # int24 -> int32<<8
            int_data = (raw >> (32 - bits)).astype(np.int64)
            int_kind = f"int{bits}"
            orig = int_data.T.astype(np.float64) / float(2 ** (bits - 1))
        else:
            data, sr = sf.read(path, dtype="float64", always_2d=True)
            orig = data.T
    except Exception:
        import librosa
        y, sr = librosa.load(path, sr=None, mono=False)
        orig = y[None, :] if y.ndim == 1 else y
        orig = orig.astype(np.float64)
    x = orig.mean(axis=0)
    return {"sr": int(sr), "x": x, "orig": orig,
            "int": int_data, "int_kind": int_kind, "path": os.path.abspath(path)}


def save_wav_f32(path, data, sr):
    import soundfile as sf
    if data.ndim == 1:
        data = data[:, None]
    else:
        data = data.T if data.shape[0] < data.shape[1] else data
    sf.write(path, data.astype(np.float32), sr, subtype="FLOAT")


def save_wav_i16(path, data, sr):
    import soundfile as sf
    if data.ndim == 1:
        data = data[:, None]
    else:
        data = data.T if data.shape[0] < data.shape[1] else data
    sf.write(path, np.clip(np.round(data * 32767.0), -32768, 32767).astype(np.int16),
             sr, subtype="PCM_16")

# ---------------------------------------------------------------------- helpers
def hz_to_midi_f(f):
    return 69.0 + 12.0 * np.log2(np.maximum(f, 1e-9) / 440.0)


def midi_to_hz(p):
    return 440.0 * 2.0 ** ((np.asarray(p, dtype=np.float64) - 69.0) / 12.0)


def rdp(points, eps):
    """Ramer-Douglas-Peucker on [[x,y]...] (x ascending). Iterative, returns
    the decimated polyline INCLUDING both endpoints. Linear-interp error <= eps."""
    pts = np.asarray(points, dtype=np.float64)
    n = len(pts)
    if n <= 2:
        return pts.tolist()
    keep = np.zeros(n, bool)
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        xa, ya = pts[a]
        xb, yb = pts[b]
        xs = pts[a + 1:b, 0]
        ys = pts[a + 1:b, 1]
        t = (xs - xa) / max(xb - xa, 1e-12)
        d = np.abs(ys - (ya + t * (yb - ya)))
        i = int(np.argmax(d))
        if d[i] > eps:
            m = a + 1 + i
            keep[m] = True
            stack.append((a, m))
            stack.append((m, b))
    return pts[keep].tolist()


def env_sample(env, t):
    """Sample a [[t,v]...] breakpoint envelope at times t (np array), linear,
    clamped ends."""
    e = np.asarray(env, dtype=np.float64)
    if len(e) == 0:
        return np.zeros_like(t)
    if len(e) == 1:
        return np.full_like(t, e[0, 1])
    return np.interp(t, e[:, 0], e[:, 1])

# ---------------------------------------------------------------------- analysis
def _stft_mag_phase(x, sr, n_win, n_fft, hop):
    import librosa
    from scipy.signal import get_window
    S = librosa.stft(x.astype(np.float64), n_fft=n_fft, hop_length=hop,
                     win_length=n_win, window="blackman", center=True,
                     pad_mode="reflect")   # edge frames read true amplitude, not taper
    w = get_window("blackman", n_win, fftbins=True)
    scale = 2.0 / w.sum()                      # sinusoid amp A -> peak mag A/scale
    return np.abs(S) * scale, np.angle(S), S.shape[1]


def _stft_band_stream(x, n_win, n_fft, hop, row0, row1, block=1536):
    """THE STREAMING STFT (A2M byte-par wave 2): band rows [row0:row1) of the
    spectrogram, computed in frame BLOCKS — the full-spectrum matrix never
    exists. The monolithic float64 path allocated ~3.3GB for 45s of mono at
    n_fft 32768 (measured, OOM-killed on 15GB boxes and any Raspberry Pi);
    this one peaks at one block (~300MB) + the sliced band rows.

    Equivalence to _stft_mag_phase(center=True, pad_mode='reflect'): the
    signal is reflect-padded n_fft//2 ONCE up front, then blocks run
    center=False — frame k covers xp[k*hop : k*hop+n_fft], i.e. centered on
    x[k*hop], no seam re-reflection, same frame count. float32/complex64:
    phase is 8-bit-packed downstream and mag feeds dB peak-picking — f64
    precision was never load-bearing here.

    Returns (mag*scale rows, phase rows, n_frames, global_mag_max*scale)."""
    import librosa
    from scipy.signal import get_window
    w = get_window("blackman", n_win, fftbins=True)
    scale = np.float32(2.0 / w.sum())
    half = n_fft // 2
    xp = np.pad(np.asarray(x, dtype=np.float32), half, mode="reflect")
    n_frames = 1 + (len(xp) - n_fft) // hop
    mag = np.empty((row1 - row0, n_frames), np.float32)
    ph = np.empty((row1 - row0, n_frames), np.float32)
    gmax = 0.0
    k0 = 0
    while k0 < n_frames:
        k1 = min(n_frames, k0 + block)
        seg = xp[k0 * hop:(k1 - 1) * hop + n_fft]
        S = librosa.stft(seg, n_fft=n_fft, hop_length=hop, win_length=n_win,
                         window="blackman", center=False)
        a = np.abs(S)
        if a.size:
            gmax = max(gmax, float(a.max()))
        mag[:, k0:k1] = a[row0:row1]
        ph[:, k0:k1] = np.angle(S[row0:row1])
        del S, a
        k0 = k1
    mag *= scale
    return mag, ph, n_frames, gmax * float(scale)


def _frame_peaks(mag_db, floor_db, top):
    """Indices of local maxima above floor, strongest first, capped at top."""
    m = mag_db
    cand = np.where((m[1:-1] > m[:-2]) & (m[1:-1] >= m[2:]) & (m[1:-1] > floor_db))[0] + 1
    if len(cand) > top:
        cand = cand[np.argsort(m[cand])[::-1][:top]]
    return cand


def _parabolic(mag_db, i):
    a, b, c = mag_db[i - 1], mag_db[i], mag_db[i + 1]
    den = a - 2 * b + c
    d = 0.5 * (a - c) / den if abs(den) > 1e-12 else 0.0
    d = float(np.clip(d, -0.5, 0.5))
    return i + d, b - 0.25 * (a - c) * d


def _phase_at_center(phase_col, bin_f, n_fft):
    """Phase at the WINDOW CENTER (= frame time k*hop), from the DFT angle at the
    nearest bin. For a periodic window padded centered at exactly N/2, the
    window's linear phase ramp is pi/bin and the center rotation is pi*bin_f;
    they combine to the clean identity  phi_center = angle[i] + pi*i  (mod 2pi),
    independent of the fractional peak position."""
    i = int(round(bin_f))
    return float((phase_col[i] + math.pi * i) % TWO_PI)


def _transient_frames(x, sr, hop):
    """Frames where broadband novelty spikes — partial BIRTHS are blocked there
    (a click is not a sine; it belongs to the noise layer)."""
    import librosa
    env = librosa.onset.onset_strength(y=x.astype(np.float32), sr=sr,
                                       hop_length=hop)
    if env.max() <= 0:
        return set()
    thr = float(np.percentile(env, 90)) * 1.4
    hits = set(int(i) for i in np.where(env > thr)[0])
    return hits | {i + 1 for i in hits}


def _pd_freq(freq, ph, sr, hop, n_win):
    """PHASE-DERIVED instantaneous frequency: the phase advance between hops
    resolves fast vibrato/glides the (long) analysis window smears. Clamped to
    the peak's half main lobe — a low-SNR phase never yanks the track."""
    K = len(freq)
    if K < 2:
        return freq
    T = hop / sr
    max_dev = 3.0 * sr / n_win
    pd = np.full(K - 1, np.nan)
    for k in range(K - 1):
        if ph[k] >= 0 and ph[k + 1] >= 0:
            frac = (ph[k + 1] - ph[k]) / TWO_PI
            m = round(freq[k] * T - frac)
            f = (frac + m) / T
            if abs(f - freq[k]) <= max_dev:
                pd[k] = f
    out = freq.copy()
    for k in range(K):
        cands = []
        if k > 0 and not math.isnan(pd[k - 1]):
            cands.append(pd[k - 1])
        if k < K - 1 and not math.isnan(pd[k]):
            cands.append(pd[k])
        if cands:
            out[k] = float(np.mean(cands))
    return out


def _track_band(x, sr, hop, n_win, n_fft, fmin, fmax, top_peaks, floor_rel_db,
                prog=None, stage="analyze", fr0=0.0, fr1=1.0, transients=None):
    """Peak-track one band. Returns list of partials:
    {f0 (frame idx), freq[], amp[], ph[] (per-frame, at frame centers)}."""
    hz_per_bin = sr / n_fft
    n_bins = n_fft // 2 + 1
    lo_bin = max(1, int(fmin / hz_per_bin))
    hi_bin = min(n_bins - 2, int(fmax / hz_per_bin))
    # LOBE SHADOW: a local max within the stronger peak's main lobe is the lobe's
    # shoulder, not a partial (blackman main lobe = 6 true-window bins).
    lobe_bins = 6.0 * n_fft / n_win
    # STREAMED BAND ROWS (wave 2): only [row0:row1) of the spectrogram is ever
    # materialized — the tracker reads nothing else (lo band at n_fft 32768 =
    # 168 of 16385 rows; the monolithic matrix was the 3.3GB/45s bomb). Margin
    # covers _frame_peaks neighbors + parabolic +-1 + the lobe-shadow compare.
    m = max(16, int(lobe_bins) + 2)
    row0 = max(0, lo_bin - m)
    row1 = min(n_bins, hi_bin + m + 1)
    mag, phase, n_frames, gmax = _stft_band_stream(x, n_win, n_fft, hop,
                                                   row0, row1)
    with np.errstate(divide="ignore"):
        mag_db = 20.0 * np.log10(mag + 1e-12)
    del mag
    g_floor = 20.0 * math.log10(gmax + 1e-12) + DB_FLOOR
    # TRANSIENT SHADOW: any frame whose window overlaps a click still SEES the
    # click — births stay blocked for the whole overlap, not just the hit frame
    if transients:
        half = n_win // (2 * hop) + 1
        transients = {t + d for t in transients for d in range(-half, half + 1)}

    active = []      # {freq, amp, ph, fs:[], as:[], ps:[], gap}
    done = []
    for k in range(n_frames):
        col = mag_db[:, k]                      # band rows only (local indices)
        floor = max(g_floor,
                    float(col[lo_bin - row0:hi_bin - row0].max()) + floor_rel_db) \
            if hi_bin > lo_bin else g_floor
        idx = _frame_peaks(col, floor, top_peaks)
        idx = idx[(idx + row0 >= lo_bin) & (idx + row0 <= hi_bin)]
        cands = []
        for i in idx:
            bf, pdb = _parabolic(col, int(i))
            f = (bf + row0) * hz_per_bin
            if fmin <= f <= fmax:
                cands.append((bf, f, pdb))
        cands.sort(key=lambda p: -p[2])
        peaks, taken = [], []
        for bf, f, pdb in cands:
            # conditional: a REAL close partial rivals its neighbor's height;
            # a lobe shoulder sits well below it
            if any(abs(bf - tb) < lobe_bins and pdb < tdb - 12.0
                   for tb, tdb in taken):
                continue
            taken.append((bf, pdb))
            il = int(round(bf))                 # local row; identity needs the
            peaks.append((f, 10.0 ** (pdb / 20.0),   # ABSOLUTE bin (il + row0)
                          float((phase[il, k]
                                 + math.pi * (il + row0)) % TWO_PI)))
        used = np.zeros(len(peaks), bool)
        # match strongest active tracks first
        for tr in sorted(active, key=lambda t: -t["as"][-1]):
            best, bd = -1, 1e9
            for j, (f, a, ph) in enumerate(peaks):
                if used[j]:
                    continue
                d = abs(1200.0 * math.log2(f / tr["freq"]))
                if d < bd:
                    bd, best = d, j
            if best >= 0 and bd < 70.0:
                used[best] = True
                f, a, ph = peaks[best]
                tr["freq"] = f
                tr["gap"] = 0
                tr["fs"].append(f)
                tr["as"].append(a)
                tr["ps"].append(ph)
            else:
                tr["gap"] += 1
                tr["fs"].append(tr["fs"][-1])
                tr["as"].append(tr["as"][-1])           # hold through the gap
                tr["ps"].append(-1.0)                   # unmeasured
        survivors = []
        for tr in active:
            if tr["gap"] > 2:
                for _ in range(tr["gap"]):              # trim unmeasured tail
                    tr["fs"].pop(); tr["as"].pop(); tr["ps"].pop()
                done.append(tr)
            else:
                survivors.append(tr)
        active = survivors
        if not (transients and k in transients):     # clicks don't birth sines
            for j, (f, a, ph) in enumerate(peaks):
                if not used[j]:
                    active.append({"freq": f, "gap": 0, "f0": k,
                                   "fs": [f], "as": [a], "ps": [ph]})
        if prog and (k & 127) == 0:
            prog.emit(stage, fr0 + (fr1 - fr0) * (k / max(1, n_frames)),
                      f"tracking {fmin:.0f}-{fmax:.0f}Hz ({len(active)} live)")
    for tr in active:
        if tr["gap"]:
            for _ in range(tr["gap"]):
                tr["fs"].pop(); tr["as"].pop(); tr["ps"].pop()
        done.append(tr)

    # EDGE HEAL: frames whose window hangs past the file edge measure phase/freq
    # against the reflection, not the music. Extrapolate from the first/last
    # clean interior frame instead (matters for --t0/--t1 crops mid-note too).
    edge = n_win // (2 * hop) + 1
    out = []
    for tr in done:
        n = len(tr["fs"])
        if n < 4:
            continue
        amps = np.array(tr["as"])
        if float(amps.max()) < 10.0 ** ((DB_FLOOR + 10.0) / 20.0):
            continue
        ph = np.array(tr["ps"])
        freq = _pd_freq(np.array(tr["fs"]), ph, sr, hop, n_win)
        f0 = int(tr["f0"])
        j = edge - f0                              # first clean local index
        if 0 < j < n:
            # extrapolate the clean interior's SLOPE (a chirp keeps moving);
            # boundary zone is unknowable, the interior is the best guess
            sl = (freq[min(j + 4, n - 1)] - freq[j]) / max(1, min(4, n - 1 - j))
            for k in range(j):
                freq[k] = max(1.0, freq[j] + sl * (k - j))
            amps[:j] = amps[j]
            w = TWO_PI * freq / sr
            for k in range(j - 1, -1, -1):
                if ph[k + 1] >= 0:
                    ph[k] = (ph[k + 1] - (w[k] + w[k + 1]) * hop / 2.0) % TWO_PI
        j2 = (n_frames - 1 - edge) - f0            # last clean local index
        if 0 <= j2 < n - 1:
            sl = (freq[j2] - freq[max(0, j2 - 4)]) / max(1, min(4, j2))
            for k in range(j2 + 1, n):
                freq[k] = max(1.0, freq[j2] + sl * (k - j2))
            amps[j2 + 1:] = amps[j2]
            w = TWO_PI * freq / sr
            for k in range(j2 + 1, n):
                if ph[k - 1] >= 0:
                    ph[k] = (ph[k - 1] + (w[k - 1] + w[k]) * hop / 2.0) % TWO_PI
        out.append({"f0": f0, "freq": freq, "amp": amps, "ph": ph})
    return out


def _dedup(parts):
    """Band overlap makes duplicates: drop a track when >=60% of its sampled
    frames sit within 35 cents of an already-kept (stronger) track."""
    parts = sorted(parts, key=lambda p: -float((p["amp"] ** 2).sum()))
    kept, grid = [], {}
    for tr in parts:
        n = len(tr["freq"])
        idx = range(0, n, max(1, n // 24))
        dup = 0
        for i in idx:
            f = tr["freq"][i]
            for kf in grid.get(tr["f0"] + i, ()):
                if abs(1200.0 * math.log2(f / kf)) < 35.0:
                    dup += 1
                    break
        if dup / max(1, len(list(idx))) >= 0.6:
            continue
        kept.append(tr)
        for i in range(n):
            grid.setdefault(tr["f0"] + i, []).append(tr["freq"][i])
    return kept


def _stitch(parts):
    """A glide that crosses a band seam (or a brief dropout) arrives as two
    tracks; join tail->head when they meet within 3 frames and 60 cents."""
    parts = sorted(parts, key=lambda p: p["f0"])
    out = []
    for tr in parts:
        merged = False
        for o in out:
            oe = o["f0"] + len(o["freq"])           # end frame, exclusive
            gap = tr["f0"] - oe
            if -3 <= gap <= 3:
                fa, fb = float(o["freq"][-1]), float(tr["freq"][0])
                if abs(1200.0 * math.log2(fb / fa)) < 60.0:
                    s = max(0, -gap)
                    if s >= len(tr["freq"]):
                        merged = True
                        break
                    if gap > 0:                     # bridge the hole
                        for g in range(gap):
                            t01 = (g + 1.0) / (gap + 1.0)
                            o["freq"] = np.append(o["freq"], fa + (fb - fa) * t01)
                            o["amp"] = np.append(o["amp"],
                                                 o["amp"][-1] + (tr["amp"][s] - o["amp"][-1]) * t01)
                            o["ph"] = np.append(o["ph"], -1.0)
                    o["freq"] = np.append(o["freq"], tr["freq"][s:])
                    o["amp"] = np.append(o["amp"], tr["amp"][s:])
                    o["ph"] = np.append(o["ph"], tr["ph"][s:])
                    merged = True
                    break
        if not merged:
            out.append(tr)
    return out


def _heterodyne_refine(x, partials, sr, hop, cutoff=25.0):
    """ANALYSIS-BY-DEMODULATION: mix the signal down around each tracked
    partial (e^{-j phi_track}), zero-phase lowpass the complex baseband, read
    TRUE instantaneous amp/freq/phase at sample resolution — window smear
    (vibrato depth loss, FM bias, click splash) is gone. Deterministic."""
    from scipy.signal import butter, sosfiltfilt
    sos = butter(6, cutoff / (sr / 2.0), "low", output="sos")   # SOS: (b,a) is
    pad = int(0.15 * sr)                                        # unstable here
    margin = int(0.05 * sr)
    n = len(x)
    for tr in partials:
        K = len(tr["freq"])
        s0 = tr["f0"] * hop
        s1 = min(n, s0 + K * hop)
        if s1 - s0 < 4 * hop:
            continue
        a0 = max(0, s0 - pad)
        b0 = min(n, s1 + pad)
        seg = x[a0:b0]
        # tracked phase at every sample (freq frames -> linear interp)
        tf = (np.arange(K) * hop + s0 - a0).astype(np.float64)
        fs = np.interp(np.arange(len(seg), dtype=np.float64), tf, tr["freq"])
        phi = np.concatenate([[0.0], np.cumsum(TWO_PI * fs[:-1] / sr)])
        z = seg * np.exp(-1j * phi)
        try:
            zl = sosfiltfilt(sos, z.real) + 1j * sosfiltfilt(sos, z.imag)
        except ValueError:                     # segment too short for the filter
            continue
        from scipy.signal import medfilt
        amp2 = 2.0 * np.abs(zl)
        dphi = np.unwrap(np.angle(zl))
        idx = np.clip(tf.astype(int), 0, len(seg) - 1)
        ref_amp = medfilt(amp2[idx], 5)        # kill ~1% demod ripple
        tot = phi + dphi
        ref_ph = tot[idx] % TWO_PI
        # freq FROM the refined phases (their differences) — the phases are
        # exact, a gradient would only add jitter back
        df = np.diff(tot[idx]) / (TWO_PI * hop / sr)
        ref_f = np.concatenate([df, df[-1:]]) if len(df) else tr["freq"]
        ref_f = np.clip(ref_f, tr["freq"] * 0.7, tr["freq"] * 1.4)
        # trust refinement only away from the filter's own edges, and never
        # let it more than double the tracked amplitude (demod leakage guard)
        ok = (ref_amp > 1e-7) & (ref_amp < tr["amp"] * 2.0 + 1e-6) \
            & (idx >= margin) & (idx <= len(seg) - 1 - margin)
        tr["amp"] = np.where(ok, ref_amp, tr["amp"])
        tr["freq"] = np.where(ok, ref_f, tr["freq"])
        tr["ph"] = np.where(ok & (tr["ph"] >= 0), ref_ph, tr["ph"])
    return partials


def _mel_sim_local(a, b, sr):
    """Cheap local mel similarity (the same currency as verify's headline)."""
    import librosa
    def S(y):
        M = _mel_filters(sr, 1024, 64) \
            @ (np.abs(librosa.stft(y, n_fft=1024, hop_length=512)) ** 2)
        return 10.0 * np.log10(M + 1e-10)
    A = np.maximum(S(a), -80.0) + 80.0
    B = np.maximum(S(b), -80.0) + 80.0
    K = min(A.shape[1], B.shape[1])
    return 1.0 - float(np.abs(A[:, :K] - B[:, :K]).sum()) \
        / float(np.maximum(A[:, :K], B[:, :K]).sum() + 1e-12)


def _refine_gated(x, parts, sr, hop):
    """PER-NOTE refine gating: refine every MOVING partial, then adopt each
    refined version only where it beats the original IN THE CONTRACT CURRENCY
    (local mel similarity vs the signal, everything else held fixed) without
    worsening residual energy. Stationary notes are already exact — skip."""
    n = len(x)
    g_pk = max((float(t["amp"].max()) for t in parts), default=0.0)
    floor = g_pk * 10.0 ** (-30.0 / 20.0)   # quiet notes can't move global mel
    cands = []
    for tr in parts:
        f = tr["freq"]
        rng = 1200.0 * math.log2(float(f.max()) / max(float(f.min()), 1e-9))
        if rng > 20.0 and len(f) >= 8 and float(tr["amp"].max()) >= floor:
            cands.append(tr)
    if not cands:
        return parts, 0
    refined = _heterodyne_refine(
        x, [{"f0": t["f0"], "freq": t["freq"].copy(), "amp": t["amp"].copy(),
             "ph": t["ph"].copy()} for t in cands], sr, hop)
    full = resynth_exact(parts, hop, sr, n)
    adopted = 0
    for orig, ref in zip(cands, refined):
        K = len(orig["freq"])
        alive = (orig["f0"] + K) * hop >= n - hop
        seg_o = _mq_render_track(orig["freq"], orig["amp"], orig["ph"], sr, hop,
                                 sustain_tail=alive)
        seg_r = _mq_render_track(ref["freq"], ref["amp"], ref["ph"], sr, hop,
                                 sustain_tail=alive)
        s0 = orig["f0"] * hop - hop
        a, b = max(0, s0), min(n, s0 + len(seg_o))
        if b <= a:
            continue
        base = x[a:b] - full[a:b]                    # residual WITH orig in place
        cand = base + seg_o[a - s0:b - s0] - seg_r[a - s0:b - s0]
        if float((cand ** 2).sum()) > float((base ** 2).sum()) * 1.02:
            continue                                 # residual must not worsen
        swap = full[a:b] + seg_r[a - s0:b - s0] - seg_o[a - s0:b - s0]
        bm = min(b, a + 4 * sr)                      # mel-test span cap: 4s
        if _mel_sim_local(x[a:bm], swap[:bm - a], sr) > \
                _mel_sim_local(x[a:bm], full[a:bm], sr) + 1e-4:
            full[a:b] = swap
            orig["freq"], orig["amp"], orig["ph"] = ref["freq"], ref["amp"], ref["ph"]
            adopted += 1
    return parts, adopted


def _is_stable(tr, min_frames=24):
    """A STATIONARY partial (chord/pad/held note): a real lifetime (>=150ms),
    tiny frame-to-frame motion, small total range. Vibrato, glides, comb-hop
    artifacts and edge phantoms all fail this."""
    f = tr["freq"]
    ph = tr["ph"]
    if len(f) < min_frames:
        return False
    d = [abs(1200.0 * math.log2(f[k + 1] / f[k]))
         for k in range(len(f) - 1) if ph[k] >= 0 and ph[k + 1] >= 0]
    if not d:
        return False
    rng = 1200.0 * math.log2(float(f.max()) / max(float(f.min()), 1e-9))
    return float(np.median(d)) <= 2.5 and rng <= 50.0


def analyze(x, sr, hop=None, prog=None, max_partials=None, refine=False,
            light=False):
    """STABILITY-ROUTED CASCADE analysis. The uncertainty principle says one
    window can't resolve both a dense chord (needs LONG) and a deep vibrato
    (needs SHORT) — so route content instead of compromising:

    LOW  25-260Hz  : long window — 808/sub harmonic stacks resolve
    MID  235-2300  : LONG pass (8192) keeps only STABLE tracks (chords, pads);
                     unstable ones are discarded, the stable resynth is
                     SUBTRACTED, and a SHORT pass (2048) re-reads the remainder
                     — vibrato/glides arrive clean at 46ms resolution
    HIGH 2150+     : short window — attacks tight where music is sparse."""
    prog = prog or _NULL_PROG
    hop = hop or max(128, int(round(sr * 0.006)))       # ~6ms grid
    # WINDOW DURATIONS are the physics; sample counts must scale with sr
    # (fixed 2048 at 96k = half the frequency resolution everywhere — the
    # measured flat +1dB systematic on hi-rate sources)
    f2 = max(1, 1 << int(round(np.log2(max(1.0, sr / 44100.0)))))
    trans = _transient_frames(x, sr, hop)
    if light:
        # SALVAGE CONFIG: remainders have no dense stable layer by
        # construction — short passes only, no long STFTs, no subtraction
        lo_s = _track_band(x, sr, hop, n_win=4096 * f2, n_fft=16384 * f2, fmin=25.0,
                           fmax=250.0, top_peaks=24, floor_rel_db=-58.0,
                           prog=prog, stage="analyze", fr0=0.0, fr1=0.4,
                           transients=trans)
        mid_s = _track_band(x, sr, hop, n_win=2048 * f2, n_fft=8192 * f2, fmin=250.0,
                            fmax=2200.0, top_peaks=90, floor_rel_db=-62.0,
                            prog=prog, stage="analyze", fr0=0.4, fr1=0.75,
                            transients=trans)
        hi_s = _track_band(x, sr, hop, n_win=2048 * f2, n_fft=8192 * f2, fmin=2200.0,
                           fmax=min(18000.0, sr * 0.45), top_peaks=90,
                           floor_rel_db=-66.0, prog=prog, stage="analyze",
                           fr0=0.75, fr1=1.0, transients=trans)
        parts = _stitch(_dedup(lo_s + mid_s + hi_s))
        if max_partials and len(parts) > max_partials:
            parts.sort(key=lambda p: -float((p["amp"] ** 2).sum()))
            parts = parts[:max_partials]
        prog.emit("analyze", 1.0, f"{len(parts)} partials (light)")
        return parts, hop
    lo_long = _track_band(x, sr, hop,
                          n_win=min(16384 * f2, 1 << int(math.log2(sr * 0.35))),
                          n_fft=32768 * f2, fmin=25.0, fmax=250.0, top_peaks=24,
                          floor_rel_db=-64.0, prog=prog, stage="analyze",
                          fr0=0.0, fr1=0.2)
    mid_long = _track_band(x, sr, hop, n_win=8192 * f2, n_fft=16384 * f2, fmin=250.0,
                           fmax=2200.0, top_peaks=90, floor_rel_db=-74.0,
                           prog=prog, stage="analyze", fr0=0.2, fr1=0.4)
    # dedup BEFORE subtracting: a seam partial seen by two passes must not be
    # subtracted twice
    stable = _dedup([t for t in lo_long + mid_long if _is_stable(t)])
    x_rem = x - resynth_exact(stable, hop, sr, len(x)) if stable else x
    lo_short = _track_band(x_rem, sr, hop, n_win=4096 * f2, n_fft=16384 * f2, fmin=25.0,
                           fmax=250.0, top_peaks=24, floor_rel_db=-58.0,
                           prog=prog, stage="analyze", fr0=0.4, fr1=0.55,
                           transients=trans)
    mid_short = _track_band(x_rem, sr, hop, n_win=2048 * f2, n_fft=8192 * f2, fmin=250.0,
                            fmax=2200.0, top_peaks=90, floor_rel_db=-66.0,
                            prog=prog, stage="analyze", fr0=0.55, fr1=0.75,
                            transients=trans)
    if stable:
        # post-subtraction remnants of the stable layer must not re-enter as
        # junk tracks: cascade shorts clear an ABSOLUTE floor vs the loudest
        # stable partial (music 45dB under the lead belongs to the noise lane)
        gate = max(float(t["amp"].max()) for t in stable) * 10.0 ** (-45.0 / 20.0)
        lo_short = [t for t in lo_short if float(t["amp"].max()) >= gate]
        mid_short = [t for t in mid_short if float(t["amp"].max()) >= gate]
    hi = _track_band(x, sr, hop, n_win=2048 * f2, n_fft=8192 * f2, fmin=2200.0,
                     fmax=min(18000.0, sr * 0.45), top_peaks=90,
                     floor_rel_db=-72.0, prog=prog, stage="analyze",
                     fr0=0.75, fr1=1.0, transients=trans)
    parts = _stitch(_dedup(stable + lo_short + mid_short + hi))
    if max_partials and len(parts) > max_partials:
        parts.sort(key=lambda p: -float((p["amp"] ** 2).sum()))
        parts = parts[:max_partials]
    if refine == "auto":   # per-note gated: adopt only measured local wins
        prog.emit("analyze", 0.97, "heterodyne refinement (gated)")
        parts, n_adopt = _refine_gated(x, parts, sr, hop)
        prog.emit("analyze", 0.99, f"refinement adopted on {n_adopt} notes")
    elif refine:    # EXPERIMENT (wins si_sdr, costs mel on FM content — see
        # spectral_battery history): demod-true amp/freq/phase per partial
        prog.emit("analyze", 0.97, "heterodyne refinement")
        parts = _heterodyne_refine(x, parts, sr, hop)
    prog.emit("analyze", 1.0, f"{len(parts)} partials "
                              f"({len(stable)} stable / "
                              f"{len(lo_short) + len(mid_short)} agile)")
    return parts, hop

# ------------------------------------------------------------------ MQ synthesis
def _mq_segment(T, w0, w1, p0, p1, a0, a1):
    """One hop of a cubic-phase MQ oscillator: angular freqs rad/sample, phases
    at segment ends, linear amp. Returns T samples (not including the p1 end)."""
    t = np.arange(T, dtype=np.float64)
    M = np.round(((p0 - p1) + (w0 + w1) * T / 2.0) / TWO_PI)
    dp = (p1 + TWO_PI * M) - p0 - w0 * T
    al = 3.0 * dp / (T * T) - (w1 - w0) / T
    be = -2.0 * dp / (T ** 3) + (w1 - w0) / (T * T)
    ph = p0 + w0 * t + al * t * t + be * t ** 3
    amp = a0 + (a1 - a0) * (t / T)
    return amp * np.cos(ph)


def _mq_render_track(freq, amp, ph, sr, hop, sustain_tail=False):
    """Render one partial from PER-FRAME freq/amp/phase arrays (phases in rad,
    -1 = unmeasured -> integrate through). Frame k sits at sample k*hop; the
    first/last hop fade from/to silence — unless sustain_tail (the partial is
    alive at the FILE edge: fading would dip below the truth)."""
    K = len(freq)
    w = TWO_PI * np.asarray(freq, dtype=np.float64) / sr
    a = np.asarray(amp, dtype=np.float64)
    p = np.asarray(ph, dtype=np.float64).copy()
    # fill unmeasured phases by trapezoid integration from the last known
    for k in range(K):
        if p[k] < 0:
            p[k] = (p[k - 1] + (w[k - 1] + w[k]) * hop / 2.0) % TWO_PI if k else 0.0
    out = np.zeros((K + 1) * hop, dtype=np.float64)
    # birth ramp: constant freq into the first measured frame
    out[:hop] = _mq_segment(hop, w[0], w[0], (p[0] - w[0] * hop) % TWO_PI, p[0],
                            0.0, a[0])
    pos = hop
    for k in range(K - 1):
        out[pos:pos + hop] = _mq_segment(hop, w[k], w[k + 1], p[k], p[k + 1],
                                         a[k], a[k + 1])
        pos += hop
    out[pos:pos + hop] = _mq_segment(hop, w[-1], w[-1], p[-1],
                                     (p[-1] + w[-1] * hop) % TWO_PI, a[-1],
                                     a[-1] if sustain_tail else 0.0)
    return out


def resynth_exact(partials, hop, sr, n_samples):
    """Analysis-phase additive reconstruction (used to carve the noise floor)."""
    y = np.zeros(n_samples + 4 * hop, dtype=np.float64)
    for tr in partials:
        alive_at_end = (tr["f0"] + len(tr["freq"])) * hop >= n_samples - hop
        seg = _mq_render_track(tr["freq"], tr["amp"], tr["ph"], sr, hop,
                               sustain_tail=alive_at_end)
        s0 = tr["f0"] * hop - hop
        a = max(0, s0)
        b = min(len(y), s0 + len(seg))
        if b > a:
            y[a:b] += seg[a - s0:b - s0]
    return y[:n_samples]

# ------------------------------------------------------------------- noise model
_FB_CACHE = {}


def _mel_filters(sr, n_fft, n_bands):
    import librosa
    key = ("mel", sr, n_fft, n_bands)
    if key not in _FB_CACHE:
        _FB_CACHE[key] = librosa.filters.mel(sr=sr, n_fft=n_fft,
                                             n_mels=n_bands, fmin=20.0,
                                             fmax=min(18000.0, sr * 0.5))
    return _FB_CACHE[key]


def _lin_tris(freqs, f0, f1, n):
    """n linear triangles f0..f1, slaney-normalized (2/(r-l))."""
    edges = np.linspace(f0, f1, n + 2)
    fb = np.zeros((n, len(freqs)))
    for i in range(n):
        l, c, r = edges[i], edges[i + 1], edges[i + 2]
        up = (freqs - l) / max(c - l, 1e-9)
        dn = (r - freqs) / max(r - c, 1e-9)
        fb[i] = np.clip(np.minimum(up, dn), 0.0, None) * (2.0 / (r - l))
    return fb, edges[1:n + 1]


def _nb_version(n_bands):
    """Bank version FROM band count — the single selector every call site
    shares (a v3 mask into a v2 bank was the 2026-07-08 IndexError)."""
    return 4 if n_bands >= 48 else (3 if n_bands >= 32 else
                                    (2 if n_bands >= 30 else 1))


def _noise_filterbank(sr, n_fft, version=2, n_bands=None):
    """v4 (wave 3, MEL-TRUE): n_bands pure mel rows 20Hz-18k — the fidelity
    ruler itself is 128-mel, and a 32-band model paints wash/breath with a
    brush 4x too wide (the 'last 5%' lives there). At >=48 bands the mel rows
    are dense everywhere, so the sparse-top valley sag that motivated v3's
    linear rows never appears.
    v3 (32 rows): 20 mel to 8k + 12 LINEAR rows 8-18k — wide mel rows up
    top sagged -2.3dB in the inter-center valley (the 9.6-10.2k barrier).
    v2 (30): 24 mel to 12k + 6 linear 12-18k. v1 (26 mel) — old captures."""
    key = ("nfb", sr, n_fft, version, n_bands if version >= 4 else None)
    if key in _FB_CACHE:
        return _FB_CACHE[key]
    import librosa
    hi_max = min(18000.0, sr * 0.5)
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    if version >= 4:
        nb = int(n_bands or 64)
        fb = _mel_filters(sr, n_fft, nb)
        centers = librosa.mel_frequencies(n_mels=nb + 2, fmin=20.0,
                                          fmax=hi_max)[1:-1]
        out = (fb, centers)
    elif version < 2:
        fb = _mel_filters(sr, n_fft, NOISE_BANDS)
        centers = librosa.mel_frequencies(n_mels=NOISE_BANDS + 2, fmin=20.0,
                                          fmax=hi_max)[1:-1]
        out = (fb, centers)
    elif version == 2:
        fb_lo = librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=24, fmin=20.0,
                                    fmax=12000.0)
        c_lo = librosa.mel_frequencies(n_mels=26, fmin=20.0, fmax=12000.0)[1:-1]
        fb_hi, c_hi = _lin_tris(freqs, 12000.0, hi_max, 6)
        out = (np.vstack([fb_lo, fb_hi]), np.concatenate([c_lo, c_hi]))
    else:
        fb_lo = librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=20, fmin=20.0,
                                    fmax=8000.0)
        c_lo = librosa.mel_frequencies(n_mels=22, fmin=20.0, fmax=8000.0)[1:-1]
        fb_hi, c_hi = _lin_tris(freqs, 8000.0, hi_max, 12)
        out = (np.vstack([fb_lo, fb_hi]), np.concatenate([c_lo, c_hi]))
    _FB_CACHE[key] = out
    return out


NOISE_SPLIT_HZ = 500.0
RULER_FFT, RULER_HOP = 2048, 512   # the fidelity ruler's own STFT grid


def ruler_env(sig, sr, n_bands):
    """Band amplitudes of `sig` in the RULER's exact bank+grid (2048/512).
    The v4 bank IS librosa.filters.mel — verify_arrays' own triangles — so
    matching these aggregates matches the fidelity ruler cell-for-cell.
    Stored by captures/transplants as `noise_env_ruler` (parameters, not
    audio): the exact target for _ruler_true_finish."""
    import librosa
    fb, _c = _noise_filterbank(sr, RULER_FFT, _nb_version(n_bands),
                               n_bands=n_bands)
    S = librosa.stft(np.asarray(sig, dtype=np.float32), n_fft=RULER_FFT,
                     hop_length=RULER_HOP, window="hann", center=True)
    return np.sqrt(fb.astype(np.float32) @ (np.abs(S) ** 2) + 1e-20)


def _ruler_true_finish(yn, band_env, hop_cap, sr, n, ruler=None, rounds=3,
                       gmax=8.0):
    """WAVE 3.5 — THE RULER-TRUE FINISH (the dust ceiling's analytic kill).

    The split shaping equalizes band energies in ITS OWN grids (46ms lo /
    ~12ms hi at cap hop); the fidelity ruler reads 2048/512. A realization
    matched in one STFT grid still fluctuates chi-square in the other — on
    pure-noise content (breath/room/wash, all >=500Hz = the hi grid) that
    mismatch WAS the 71-75 ceiling (error share 64.8% in 112 hi rows,
    measured). This pass re-equalizes the assembled noise layer in the
    ruler's exact bank+grid, GL-consistently (each round re-measures the
    actual re-rendered signal, so overlap-add can't silently undo it).

    ruler = the stored exact target (noise_env_ruler, measured from the
    true residual in this grid — no cross-window unit bridge needed).
    Without it, the stored split-grid env is interpolated + per-band
    energy-rescaled (windows of different lengths measure different units;
    the per-band ratio cancels them) — worth +8 on dust vs +21 exact.
    Probe (w36/w45/w18 dust, w0/w13 healthy): +21.3/+19.7/+17.8/+0.7/+2.7
    spectral, corr and si_sdr improve in EVERY case (w13 si 39->45dB).
    SOTADAW_NO_RULERTRUE=1 disables."""
    if os.environ.get("SOTADAW_NO_RULERTRUE") == "1":
        return yn
    if band_env.max() <= 0 or n < RULER_FFT * 2:
        return yn
    import librosa
    nb = band_env.shape[0]
    fb, _c = _noise_filterbank(sr, RULER_FFT, _nb_version(nb), n_bands=nb)
    fb = fb.astype(np.float32)
    wsum = fb.sum(axis=0)
    nz = wsum > 1e-12
    y = np.asarray(yn, dtype=np.float32)
    S = librosa.stft(y, n_fft=RULER_FFT, hop_length=RULER_HOP,
                     window="hann", center=True)
    cur = np.sqrt(fb @ (np.abs(S) ** 2) + 1e-20)
    F = S.shape[1]
    tk = np.arange(band_env.shape[1]) * (hop_cap / sr)
    tj = np.arange(F) * (RULER_HOP / sr)
    be2 = band_env.astype(np.float64) ** 2
    T = np.empty((nb, F), np.float32)
    for b in range(nb):
        T[b] = np.sqrt(np.interp(tj, tk, be2[b]))
    eT = (T.astype(np.float64) ** 2).sum(1)
    eC = (cur.astype(np.float64) ** 2).sum(1)
    alive = eT > (eT.max() + 1e-30) * 1e-10
    T[alive] *= np.sqrt(eC[alive] / (eT[alive] + 1e-30)
                        )[:, None].astype(np.float32)
    T[~alive] = cur[~alive]                     # silent bands: leave them be
    if ruler is not None:
        # exact where the field has truth; env-derived elsewhere. A fused
        # (merged) field is ZERO on spans whose windows never stored one —
        # a zero target there would SILENCE real noise, and f16 also
        # flushes truly-silent cells to zero, so per-cell overlay is the
        # only shape that serves both.
        Tx = np.asarray(ruler, dtype=np.float32)
        if Tx.shape[1] < F:
            Tx = np.pad(Tx, ((0, 0), (0, F - Tx.shape[1])))
        Tx = Tx[:, :F]
        env_alive = T > (float(T.max()) + 1e-30) * 1e-5
        T = np.where((Tx > 0) | ~env_alive, Tx, T)
    for _ in range(rounds):
        g_band = np.clip(T / (cur + 1e-20), 0.0, gmax).astype(np.float32)
        g_bin = np.ones((fb.shape[1], F), np.float32)
        g_bin[nz] = (fb.T[nz] @ g_band) / wsum[nz, None]
        y = librosa.istft(S * g_bin, hop_length=RULER_HOP, window="hann",
                          length=n)
        S = librosa.stft(y, n_fft=RULER_FFT, hop_length=RULER_HOP,
                         window="hann", center=True)
        cur = np.sqrt(fb @ (np.abs(S) ** 2) + 1e-20)
    return y.astype(np.float64)


def _mix_ruler_polish(y, T, sr, n, rounds=3, gmax=4.0):
    """WAVE 3.6 — WHOLE-MIX RULER POLISH: GL-consistent match-EQ of the
    VERBATIM render toward the source's stored ruler env (mix_env_ruler —
    a 128-band dynamic-EQ automation target; parameters, not audio). The
    remaining mel error after the noise finish is the TONAL layer's (MQ
    resynthesis loss); this closes it at the ruler's own resolution.
    Probe: w36 +3.1, w13 +2.5 (si 40->45.7dB), w0 +0.8 (->99.56) — corr
    and si up in every case. Gains clip to +-12dB (gmax 4): a gentle EQ,
    never a rebuild. T==0 cells = the source's own silence -> the clip
    floor dims toward it. ONLY verbatim renders take this (edits win);
    SOTADAW_NO_MIXPOLISH=1 disables."""
    import librosa
    nb = T.shape[0]
    fb, _c = _noise_filterbank(sr, RULER_FFT, _nb_version(nb), n_bands=nb)
    fb = fb.astype(np.float32)
    wsum = fb.sum(axis=0)
    nz = wsum > 1e-12
    y = np.asarray(y, dtype=np.float32)
    S = librosa.stft(y, n_fft=RULER_FFT, hop_length=RULER_HOP,
                     window="hann", center=True)
    cur = np.sqrt(fb @ (np.abs(S) ** 2) + 1e-20)
    F = S.shape[1]
    Tx = np.asarray(T, dtype=np.float32)
    if Tx.shape[1] < F:
        Tx = np.pad(Tx, ((0, 0), (0, F - Tx.shape[1])))
    Tx = Tx[:, :F]
    for _ in range(rounds):
        g_band = np.clip(Tx / (cur + 1e-20), 1.0 / gmax, gmax) \
            .astype(np.float32)
        g_bin = np.ones((fb.shape[1], F), np.float32)
        g_bin[nz] = (fb.T[nz] @ g_band) / wsum[nz, None]
        y = librosa.istft(S * g_bin, hop_length=RULER_HOP, window="hann",
                          length=n)
        S = librosa.stft(y, n_fft=RULER_FFT, hop_length=RULER_HOP,
                         window="hann", center=True)
        cur = np.sqrt(fb @ (np.abs(S) ** 2) + 1e-20)
    return y.astype(np.float64)
CORRECT_ROUNDS = 3   # sound-aware analysis-by-synthesis correction rounds
GL_ROUNDS = 3


def _pack_phase8(ph, mask=None):
    """(bins, frames) radians -> 8-bit codes, zlib+b64. 4-bit (±11°) measured
    DEAD (GL can't converge); 8-bit (±0.7°) keeps the full win. `mask` zeroes
    inactive bins first — phases are incompressible noise, sparsity is the
    only diet (11x measured at the -60dB activity mask, -0.09 mel)."""
    import base64, zlib
    if mask is not None:
        ph = ph.copy()
        K = min(ph.shape[1], mask.shape[1])
        ph[:, :K][~mask[:, :K]] = 0.0
        if ph.shape[1] > K:
            ph[:, K:] = 0.0
    q = (np.round(ph / (TWO_PI / 256.0)).astype(np.int64) % 256).astype(np.uint8)
    return base64.b64encode(zlib.compress(q.T.reshape(-1).tobytes(), 6)).decode()


def _unpack_phase8(b64, n_bins, n_frames, codec="zlib"):
    import base64, zlib
    raw = base64.b64decode(b64)
    if codec == "zlib":
        raw = zlib.decompress(raw)
    flat = np.frombuffer(raw, dtype=np.uint8)[:n_bins * n_frames]
    return (flat.reshape(n_frames, n_bins).T.astype(np.float64)) * (TWO_PI / 256.0)


def _phase_activity_mask(band_env, rows, fb, n_bins, thr_db=-65.0):
    """bin x frame activity from band envelopes: a bin's phase matters only
    while its band is alive (below -60dB of global peak GL fills fine)."""
    gpk = float(band_env.max()) + 1e-12
    act_band = band_env > gpk * 10.0 ** (thr_db / 20.0)
    act_band[~rows] = False
    binw = fb > 0
    K = band_env.shape[1]
    act = np.zeros((n_bins, K), bool)
    for b in np.where(rows)[0]:
        act[binw[b][:n_bins], :] |= act_band[b][None, :]
    return act


def _noise_ffts(sr):
    """Window sizes scale with sr: hop is ~6ms of SAMPLES, so at 96k a fixed
    512 window is SMALLER than the hop (COLA violated -> gapped noise; the
    96kHz generalization catch). Keep ~46ms / ~11.6ms真 durations."""
    hop = max(128, int(round(sr * 0.006)))
    lo = 1 << int(np.ceil(np.log2(max(2048, 4 * hop))))
    hi = 1 << int(np.ceil(np.log2(max(512, 2 * hop))))
    return lo, hi


NOISE_FFT_LO = 2048   # 44.1k values (call sites use _noise_ffts(sr))
NOISE_FFT_HI = 512


def _noise_band_masks(sr, n_bands=NOISE_BANDS, version=2):
    _, centers = _noise_filterbank(sr, 2048, version, n_bands=n_bands)
    lo = centers < NOISE_SPLIT_HZ
    return lo, ~lo


def _noise_shape_pass(sig_or_env, sr, hop, n_fft, rows, band_env=None, wn=None,
                      n_samples=None, n_bands=None):
    """analyze (band_env=None): band energies of `sig_or_env` for `rows` bands.
    render (band_env given): shape `wn` so those band rows match band_env."""
    import librosa
    nb = n_bands or len(rows)
    fb, _c = _noise_filterbank(sr, n_fft, _nb_version(nb), n_bands=nb)
    if band_env is None:
        # FRAME-BLOCKED (wave 2): fb @ |S|^2 accumulated per block — the full
        # power matrix never exists (complex128 whole-file STFT was ~1.7GB on
        # a 410s stem; a block peaks ~40MB). Pre-pad matches librosa's
        # center=True default pad_mode='constant'; blocks run center=False so
        # seams never re-pad. f32: band ENERGIES feed dB-domain note carving.
        sig = np.asarray(sig_or_env, dtype=np.float32)
        half = n_fft // 2
        xp = np.pad(sig, half, mode="constant")
        n_frames = 1 + (len(xp) - n_fft) // hop
        out = np.empty((fb.shape[0], n_frames), np.float32)
        k0 = 0
        while k0 < n_frames:
            k1 = min(n_frames, k0 + 4096)
            seg = xp[k0 * hop:(k1 - 1) * hop + n_fft]
            S = librosa.stft(seg, n_fft=n_fft, hop_length=hop, window="hann",
                             center=False)
            out[:, k0:k1] = np.sqrt(fb.astype(np.float32)
                                    @ (np.abs(S) ** 2) + 1e-20)
            del S
            k0 = k1
        out[~rows] = 0.0
        return out
    W = librosa.stft(wn, n_fft=n_fft, hop_length=hop, window="hann", center=True)
    cur = np.sqrt(fb @ (np.abs(W) ** 2) + 1e-20)
    K = min(cur.shape[1], band_env.shape[1])
    g_band = np.zeros_like(cur)
    g_band[rows, :K] = band_env[rows, :K] / cur[rows, :K]
    fb_r = fb * rows[:, None]
    wsum = fb_r.sum(axis=0)
    nz = wsum > 1e-12
    g_bin = np.zeros((fb.shape[1], cur.shape[1]))
    g_bin[nz] = (fb_r.T[nz] @ g_band) / wsum[nz, None]
    # TRIANGLE DILUTION correction: overlapping mel triangles average an active
    # band's gain down toward quiet neighbors (measured -9dB "air"). Measure
    # the achieved band amplitude IN THE STFT DOMAIN and correct, 3 rounds.
    tgt = np.where(g_band[rows] > 0, band_env[rows, :g_band.shape[1]], 0.0)         if K == g_band.shape[1] else None
    for _ in range(3):
        ach = np.sqrt(fb @ (np.abs(W * g_bin) ** 2) + 1e-20)
        corr = np.ones_like(g_band)
        corr[rows, :K] = np.where(g_band[rows, :K] > 0,
                                  band_env[rows, :K] / ach[rows, :K], 1.0)
        g_band = g_band * corr
        g_bin = np.zeros((fb.shape[1], cur.shape[1]))
        g_bin[nz] = (fb_r.T[nz] @ g_band) / wsum[nz, None]
    return librosa.istft(W * g_bin, hop_length=hop, window="hann",
                         length=n_samples).astype(np.float64)


def noise_analyze(residual, sr, hop, n_bands=30):
    """Per-frame band amplitudes of the residual — LOW bands from a 46ms
    window (sub resolution), HIGH bands from an 11.6ms window (click timing).
    v2 bank: 24 mel + 6 linear top bands (n_bands>=30 selects v2)."""
    lo_rows, hi_rows = _noise_band_masks(sr, n_bands, _nb_version(n_bands))
    nlo, nhi = _noise_ffts(sr)
    e_lo = _noise_shape_pass(residual, sr, hop, nlo, lo_rows, n_bands=n_bands)
    e_hi = _noise_shape_pass(residual, sr, hop, nhi, hi_rows, n_bands=n_bands)
    K = min(e_lo.shape[1], e_hi.shape[1])
    return e_lo[:, :K] + e_hi[:, :K]


def noise_render(band_env, sr, hop, n_samples, seed=NOISE_SEED,
                 ruler_env=None):
    """Deterministic: seeded white noise shaped per-frame/per-band to the target
    band amplitudes — same split-window banks as analysis — then the
    RULER-TRUE FINISH (exact if ruler_env given, env-derived otherwise)."""
    nb0 = band_env.shape[0]
    lo_rows, hi_rows = _noise_band_masks(sr, nb0, _nb_version(nb0))
    rng = np.random.default_rng(seed)
    wn = rng.standard_normal(n_samples).astype(np.float64)
    nlo, nhi = _noise_ffts(sr)
    y = _noise_shape_pass(None, sr, hop, nlo, lo_rows,
                          band_env=band_env, wn=wn, n_samples=n_samples)
    y += _noise_shape_pass(None, sr, hop, nhi, hi_rows,
                           band_env=band_env, wn=wn, n_samples=n_samples)
    return _ruler_true_finish(y, band_env, hop, sr, n_samples, ruler=ruler_env)

# ------------------------------------------------------- capture -> spectral MIDI
def _partial_to_note(tr, hop, sr, spb, plock_every=48):
    """One tracked partial -> one note dict with envelopes (times in BEATS,
    relative to note start). Returns None for junk."""
    freq = tr["freq"]; amp = tr["amp"]; ph = tr["ph"]
    K = len(freq)
    t0_s = tr["f0"] * hop / sr
    dur_s = K * hop / sr
    wmed = float(np.median(freq))
    pitch = int(np.clip(round(69.0 + 12.0 * math.log2(wmed / 440.0)), 0, 127))
    f_ref = float(midi_to_hz(pitch))
    tb = (np.arange(K) * hop / sr) / spb
    cents = 1200.0 * np.log2(freq / f_ref)
    peak = float(amp.max())
    # a MOVING partial (vibrato/glide) drifts phase faster between locks:
    # lock 3x denser and keep the bend curve finer
    wobbly = float(cents.max() - cents.min()) > 20.0
    # HF: 1.5c at 9.4kHz is 8Hz — enough to scramble a ring cluster's 20-40Hz
    # beat structure between locks. Precision is cheap up there (few notes).
    hf = f_ref > 5000.0
    bend = rdp(np.stack([tb, cents], 1),
               eps=0.35 if wobbly else (0.5 if hf else 1.5))
    gain = rdp(np.stack([tb, amp / peak], 1), eps=0.008)
    locks = []
    for k in range(0, K, 4 if wobbly else (16 if hf else plock_every)):
        if ph[k] >= 0:
            locks.append([round(float(tb[k]), 6), round(float(ph[k]), 6)])
    ph0 = float(ph[0]) if ph[0] >= 0 else 0.0
    return {"start": round(t0_s / spb, 6), "len": round(dur_s / spb, 6),
            "pitch": pitch,
            "vel": round(min(1.0, max(0.05, peak ** 0.5 * 2.0)), 3),
            "sp": {"peak": peak, "ph0": round(ph0, 6),
                   "bend": [[round(t, 6), round(c, 2)] for t, c in bend],
                   "gain": [[round(t, 6), round(g, 5)] for t, g in gain],
                   "plock": locks}}


def _noise_to_notes(band_env, hop, sr, spb, gate_db=-70.0, floor_db=-90.0):
    """Band envelopes -> one note per active band segment, envelope attached.
    pitch = NOISE_PITCH0 + band. Gate PER BAND (its own dynamics) with a global
    absolute floor — hats/air must not die under a loud sub band."""
    notes = []
    n_bands, K = band_env.shape
    ref = float(band_env.max() + 1e-12)
    for b in range(n_bands):
        env = band_env[b]
        thr = max(float(env.max()) * 10 ** (gate_db / 20.0),
                  ref * 10 ** (floor_db / 20.0))
        on = env > thr
        k = 0
        while k < K:
            if not on[k]:
                k += 1
                continue
            j = k
            gap = 0
            while j + 1 < K and gap <= int(0.12 * sr / hop):
                j += 1
                gap = gap + 1 if not on[j] else 0
            j -= gap
            seg = env[k:j + 1]
            peak = float(seg.max())
            if peak > 0 and (j - k) >= 2:
                tb = (np.arange(j + 1 - k) * hop / sr) / spb
                # decimate in LOG space: hats need their valleys as much as
                # their hits (linear eps flattened everything under -40dB
                # into a wash — the measured 8kHz "missing contrast" bug)
                seg_db = 20.0 * np.log10(seg / peak + 1e-4)
                gain = [[t, 10.0 ** (d / 20.0)]
                        for t, d in rdp(np.stack([tb, seg_db], 1), eps=0.6)]
                notes.append({"start": round(k * hop / sr / spb, 6),
                              "len": round((j + 1 - k) * hop / sr / spb, 6),
                              "pitch": NOISE_PITCH0 + b,
                              "vel": round(min(1.0, max(0.05, (peak / ref) ** 0.5)), 3),
                              "sp": {"peak": peak,
                                     "gain": [[round(t, 6), round(g, 5)] for t, g in gain],
                                     "noise_band": b}})
            k = j + 1 + gap
    return notes


CLICK_FADE = 32
CLICK_LEN = 8192


def _extract_clicks(residual, band_env, hop, sr, spb, max_per_s=20):
    """THE TRANSIENT LANE: residual bursts (snare cracks, clicks, consonants)
    become notes carrying their own int16 waveform snippet — moved like MIDI,
    rendered exactly. Returns (click_notes, carved) where carved is EXACTLY
    what the renderer will re-add (subtract it before noise modeling)."""
    import base64
    e = (band_env[8:] ** 2).sum(axis=0)     # transients are an HF phenomenon
    db = 10.0 * np.log10(e + 1e-20)
    K = len(db)
    hits = []
    for k in range(1, K - 1):
        # median EXCLUDING the hit's own width (a click is 2-4 frames wide;
        # including it inflates the baseline and hides the hit)
        ctx = np.concatenate([db[max(0, k - 9):max(0, k - 2)], db[k + 3:k + 10]])
        med = float(np.median(ctx)) if len(ctx) else -120.0
        if db[k] - med > 5.0 and db[k] >= db[k - 1] and db[k] >= db[k + 1]:
            if hits and k - hits[-1][0] < 2:
                if e[k] > e[hits[-1][0]]:
                    hits[-1] = (k, float(e[k]))
                continue
            hits.append((k, float(e[k])))
    cap_n = int(max_per_s * len(residual) / sr) + 1
    if len(hits) > cap_n:
        hits = sorted(hits, key=lambda h: -h[1])[:cap_n]
        hits.sort()
    notes = []
    work = residual.copy()      # carve sequentially: overlapping snippets must
    for k, _ in hits:           # each capture only what REMAINS (no double-count)
        s0 = max(0, k * hop - 128)
        L = min(CLICK_LEN, len(residual) - s0)
        if L < 256:
            continue
        snip = work[s0:s0 + L].copy()
        snip[:CLICK_FADE] *= np.linspace(0.0, 1.0, CLICK_FADE)
        snip[-CLICK_FADE:] *= np.linspace(1.0, 0.0, CLICK_FADE)
        speak = float(np.abs(snip).max())
        if speak < 1e-6:
            continue
        q = np.clip(np.round(snip / speak * 32767.0), -32768, 32767).astype(np.int16)
        rendered = q.astype(np.float64) / 32767.0 * speak
        work[s0:s0 + L] -= rendered
        band = int(np.argmax(band_env[:, k]))
        notes.append({"start": round(s0 / sr / spb, 6),
                      "len": round(L / sr / spb, 6),
                      "pitch": int(np.clip(60 + band, 0, 127)),
                      "vel": round(min(1.0, max(0.05, speak ** 0.5 * 2.0)), 3),
                      "sp": {"snip": base64.b64encode(q.tobytes()).decode(),
                             "speak": round(speak, 8)}})
    return notes, residual - work


QUALITY = {
    # fast: interactive capture — no correction, one salvage gen, seed noise,
    # smaller partial budget. ~2-3x realtime; ~96-97% pure-MIDI on music.
    "fast":     {"refine": False,  "salvage_gens": (2,),   "correct_rounds": 0,
                 "max_partials": 3000, "phase_field": False, "correct_gate_db": -48.0},
    # standard: sound-aware noise + phase fields, one correction round.
    "standard": {"refine": "auto", "salvage_gens": (2, 3), "correct_rounds": 1,
                 "max_partials": 6000, "phase_field": True,  "correct_gate_db": -48.0},
    # max: the fidelity path (default) — full analysis-by-synthesis. gate -64
    # + 5 correction rounds (VOCAL SWEEP 2026-07-08: pulls quiet breath/vibrato
    # tonal content back as correction notes — +0.5 spectral on a reverbed
    # choir stem, the hardest vocal case, no regression on drums/bass legs).
    # noise_bands 32 = the v3 bank (20 mel + 12 linear top rows) — finer air-band
    # resolution, now that the v2/v3 filterbank-vs-mask mismatch is fixed (that
    # IndexError kept 32 unreachable). +0.04 spectral on the choir; rap 98.8.
    "max":      {"refine": "auto", "salvage_gens": (2, 3), "correct_rounds": 5,
                 "max_partials": 13000, "phase_field": True, "correct_gate_db": -64.0,
                 "noise_bands": 32},
    # ultra: the DECK tier (wave 2, fidelity decks only) — deeper correction
    # (8 rounds at gate -72) pulls reverb modes and breath that -64 leaves to
    # the noise lane, +salvage gen 4, 20k partial budget. ~1.5-2x max cost;
    # deck windows are 10-12s so the box survives. Adopt per-deck only when
    # measured on that deck's worst window (docs/A2M_BYTE_PAR.md wave 2).
    # wave 3: ultra captures are born MEL-TRUE — 128 noise bands = the
    # fidelity ruler's own resolution (w13: 32b+phase 88.53 -> 128b 94.93;
    # the stochastic layer painted wash/breath with a brush 4x too wide).
    # Older 32-band captures upgrade via tools/noise_transplant.py without
    # re-tracking a partial.
    "ultra":    {"refine": "auto", "salvage_gens": (2, 3, 4), "correct_rounds": 8,
                 "max_partials": 20000, "phase_field": True,
                 "correct_gate_db": -72.0, "noise_bands": 128},
}
# noise_bands: per-profile noise-field resolution (30 = v2 bank; >=32 = the
# finer 3-split bank the masks already support). Absent = 30 (byte-back-compat:
# renders of old captures read the count from the capture dict, never from here).


def capture_arrays(x, sr, bpm=120.0, hop=None, max_partials=None, prog=None,
                   quality="max"):
    """The whole capture on arrays: partials + clicks + noise -> cap dict.
    Shared by capture() and the battery so proofs measure the real path.
    quality: fast (interactive) | standard | max (fidelity, default)."""
    prog = prog or _NULL_PROG
    q = QUALITY.get(quality, QUALITY["max"])
    if max_partials is None:
        max_partials = q["max_partials"]
    n = len(x)
    spb = 60.0 / bpm
    partials, hop = analyze(x, sr, hop=hop, prog=prog, max_partials=max_partials,
                            refine=q["refine"])

    prog.emit("carve", 0.05, "sinusoidal reconstruction (analysis phase)")
    sine_exact = resynth_exact(partials, hop, sr, n)
    residual = x - sine_exact
    prog.emit("carve", 0.35, "transient snippets")
    band0 = noise_analyze(residual, sr, hop)
    click_notes, carved = _extract_clicks(residual, band0, hop, sr, spb)
    res2 = residual - carved
    # SALVAGE UNTIL DRY: re-listen to the remainder — quiet tonal content the
    # first pass floors missed surfaces once the loud layer is subtracted.
    g_ref = max((float(t["amp"].max()) for t in partials), default=0.0)
    for gen in q["salvage_gens"]:
        if len(partials) >= max_partials:
            break
        prog.emit("carve", 0.35 + 0.15 * (gen - 2),
                  f"salvage pass (gen-{gen} partials)")
        parts_g, _ = analyze(res2, sr, hop=hop, prog=_NULL_PROG,
                             max_partials=(max_partials - len(partials)) // 2,
                             light=True)
        if g_ref > 0:
            gate_g = g_ref * 10 ** (-55 / 20.0)
            parts_g = [t for t in parts_g if float(t["amp"].max()) >= gate_g]
        if len(parts_g) < 8:
            break
        res2 = res2 - resynth_exact(parts_g, hop, sr, n)
        partials = partials + parts_g
    import librosa as _lb
    _, nhi = _noise_ffts(sr)
    nlo_c, _ = _noise_ffts(sr)

    prog.emit("notes", 0.1, "partials -> notes")
    notes = [nt for nt in (_partial_to_note(tr, hop, sr, spb) for tr in partials)
             if nt]

    # FAST path: fit noise to the analysis-phase residual, seed-noise render,
    # no phase fields. Cheap; the editable lanes + lossless residual are
    # unchanged (lossless is still 100% byte-exact in any quality tier).
    if not q["phase_field"]:
        band_env = noise_analyze(res2, sr, hop)
        noise_notes = _noise_to_notes(band_env, hop, sr, spb)
        import base64 as _b64
        prog.emit("notes", 1.0, f"{len(notes)} partial + {len(click_notes)} click "
                                f"+ {len(noise_notes)} noise notes (fast)")
        renv = ruler_env(res2, sr, band_env.shape[0])
        menv = ruler_env(x[:n], sr, band_env.shape[0])
        return {"version": 1, "sr": sr, "hop": hop, "bpm": bpm, "n_samples": n,
                "seed": NOISE_SEED, "noise_bands": int(band_env.shape[0]),
                "quality": quality,
                "noise_env": {"bands": int(band_env.shape[0]),
                              "frames": int(band_env.shape[1]),
                              "data": _b64.b64encode(
                                  band_env.astype(np.float16).tobytes()).decode()},
                "noise_env_ruler": {"bands": int(renv.shape[0]),
                                    "frames": int(renv.shape[1]),
                                    "data": _b64.b64encode(
                                        renv.astype(np.float16).tobytes()).decode()},
                "mix_env_ruler": {"bands": int(menv.shape[0]),
                                  "frames": int(menv.shape[1]),
                                  "data": _b64.b64encode(
                                      menv.astype(np.float16).tobytes()).decode()},
                "tracks": {"partials": notes, "clicks": click_notes,
                           "noise": noise_notes}}

    # SOUND-AWARE CORRECTION (analysis-by-synthesis): the note representation
    # renders LOSSIER than resynth_exact, so fitting noise to the analysis-phase
    # residual leaves the real render's gap unmodeled. Instead: render the
    # ACTUAL tonal+click layers, measure the TRUE residual, pull strong missed
    # tonal content back as correction notes, repeat. Downstream noise (mags AND
    # phases) is fit to the real residual — tighter by construction.
    def _render_tonal(nl):
        return render_capture({"version": 1, "sr": sr, "hop": hop, "bpm": bpm,
                               "n_samples": n, "seed": NOISE_SEED,
                               "noise_bands": 30,
                               "tracks": {"partials": nl, "clicks": click_notes,
                                          "noise": []}})[:n]
    xpk = float(np.abs(x).max()) + 1e-12
    for rnd in range(q["correct_rounds"]):
        if len(notes) >= max_partials:
            break
        prog.emit("notes", 0.2 + 0.1 * rnd, f"sound-aware correction (round {rnd+1})")
        real_res = x - _render_tonal(notes)
        corr, _ = analyze(real_res, sr, hop=hop, prog=_NULL_PROG,
                          max_partials=min(1200, max_partials - len(notes)),
                          light=True)
        gate_c = xpk * 10 ** (q["correct_gate_db"] / 20.0)
        corr = [t for t in corr if float(t["amp"].max()) >= gate_c]
        add = [nt for nt in (_partial_to_note(t, hop, sr, spb) for t in corr) if nt]
        if len(add) < 8:
            break
        notes += add

    prog.emit("notes", 0.6, "phase-field reference render (real residual)")
    base_tonal = _render_tonal(notes)
    ref_sig = x - base_tonal
    prog.emit("carve", 1.0,
              f"real residual {20*math.log10(float(np.sqrt((ref_sig**2).mean()))/ (float(np.sqrt((x**2).mean()))+1e-12)+1e-12):.1f} dB vs source")
    band_env = noise_analyze(ref_sig, sr, hop, n_bands=q.get("noise_bands", 30))
    noise_notes = _noise_to_notes(band_env, hop, sr, spb)
    PH = np.angle(_lb.stft(ref_sig, n_fft=nhi, hop_length=hop,
                           window="hann", center=True))
    PHL = np.angle(_lb.stft(ref_sig, n_fft=nlo_c, hop_length=hop,
                            window="hann", center=True))
    # the filterbank VERSION must match the band masks or _phase_activity_mask
    # indexes a v3 band (>=32) into a v2 bank -> IndexError (dormant until a
    # profile asks for >30 noise bands; caught by the vocal sweep 2026-07-08)
    nb_ver = _nb_version(band_env.shape[0])
    lo_rows_c, hi_rows_c = _noise_band_masks(sr, band_env.shape[0], nb_ver)
    fb_hi_c, _ = _noise_filterbank(sr, nhi, nb_ver, n_bands=band_env.shape[0])
    fb_lo_c, _ = _noise_filterbank(sr, nlo_c, nb_ver, n_bands=band_env.shape[0])
    mask_hi = _phase_activity_mask(band_env, hi_rows_c, fb_hi_c, PH.shape[0])
    mask_lo = _phase_activity_mask(band_env, lo_rows_c, fb_lo_c, PHL.shape[0])
    prog.emit("notes", 1.0, f"{len(notes)} partial + {len(click_notes)} click "
                            f"+ {len(noise_notes)} noise notes")
    import base64 as _b64
    return {"version": 1, "sr": sr, "hop": hop, "bpm": bpm, "n_samples": n,
            "seed": NOISE_SEED, "noise_bands": int(band_env.shape[0]),
            "quality": quality,
            "noise_phase": {"n_fft": int(nhi), "bins": int(PH.shape[0]),
                            "frames": int(PH.shape[1]), "bits": 8,
                            "codec": "zlib", "data": _pack_phase8(PH, mask_hi)},
            "noise_phase_lo": {"n_fft": int(nlo_c), "bins": int(PHL.shape[0]),
                               "frames": int(PHL.shape[1]), "bits": 8,
                               "codec": "zlib", "data": _pack_phase8(PHL, mask_lo)},
            "noise_env": {"bands": int(band_env.shape[0]),
                          "frames": int(band_env.shape[1]),
                          "data": _b64.b64encode(
                              band_env.astype(np.float16).tobytes()).decode()},
            # the exact ruler-grid residual truth — _ruler_true_finish's
            # target (wave 3.5) — and the source's own ruler env — the
            # whole-mix polish target (wave 3.6). Parameters, not audio.
            "noise_env_ruler": (lambda re_: {
                "bands": int(re_.shape[0]), "frames": int(re_.shape[1]),
                "data": _b64.b64encode(
                    re_.astype(np.float16).tobytes()).decode()})(
                        ruler_env(ref_sig, sr, band_env.shape[0])),
            "mix_env_ruler": (lambda me_: {
                "bands": int(me_.shape[0]), "frames": int(me_.shape[1]),
                "data": _b64.b64encode(
                    me_.astype(np.float16).tobytes()).decode()})(
                        ruler_env(x[:n], sr, band_env.shape[0])),
            "tracks": {"partials": notes, "clicks": click_notes,
                       "noise": noise_notes}}


def capture_arrays_stereo(orig, sr, bpm=120.0, hop=None, max_partials=6000,
                          prog=None):
    """M/S stereo capture: MID gets the full treatment; SIDE (width/ambience)
    gets a lighter pass (half partials, no click lane). Returns the mid cap
    with cap["side"] nested. Mono input -> plain capture_arrays."""
    if orig.shape[0] < 2:
        return capture_arrays(orig[0], sr, bpm=bpm, hop=hop,
                              max_partials=max_partials, prog=prog)
    mid = (orig[0] + orig[1]) * 0.5
    side = (orig[0] - orig[1]) * 0.5
    cap = capture_arrays(mid, sr, bpm=bpm, hop=hop,
                         max_partials=max_partials, prog=prog)
    if float(np.abs(side).max()) > 1e-5:
        cap["side"] = capture_arrays(side, sr, bpm=bpm, hop=hop,
                                     max_partials=max_partials // 2,
                                     prog=prog or _NULL_PROG)
        cap["side"].pop("side", None)
    cap["stereo"] = True
    return cap


def render_capture_stereo(cap, song_notes=None, prog=None):
    """Stereo render: (n, 2) [(m+s), (m-s)] when cap carries a side; else
    mono duplicated. song_notes applies to the MID lanes (side lanes are
    ambience — edited via their own *_side notes when present)."""
    m = render_capture(cap, song_notes=song_notes, prog=prog)
    sd = cap.get("side")
    if not sd:
        return np.stack([m, m], axis=1)
    s2 = render_capture(sd, song_notes=None, prog=prog)
    n = min(len(m), len(s2))
    return np.stack([m[:n] + s2[:n], m[:n] - s2[:n]], axis=1)


def verify_stereo(orig, rend2, sr):
    """Per-channel verify, averaged — the honest ruler for stereo sources."""
    ms = [verify_arrays(orig[ch], rend2[:, ch], sr) for ch in range(2)]
    return {k: round((ms[0][k] + ms[1][k]) / 2.0, 4 if k == "wave_corr" else 2)
            for k in ("spectral_pct", "wave_corr", "si_sdr_db", "env_corr")}


def capture(path, name=None, bpm=120.0, mode="lossless", t0=None, t1=None,
            hop=None, max_partials=None, prog=None, out_dir=None,
            prefix="spectral", quality="max"):
    """Full capture. Returns dict with capture data + file paths + metrics."""
    prog = prog or Prog([("load", 3), ("analyze", 38), ("carve", 22),
                         ("notes", 7), ("render", 22), ("residual", 5),
                         ("verify", 3)], label="capture")
    name = name or os.path.splitext(os.path.basename(path))[0]
    prog.emit("load", 0.1, os.path.basename(path))
    au = load_audio(path)
    sr, x = au["sr"], au["x"]
    if t0 is not None or t1 is not None:
        a = int((t0 or 0.0) * sr)
        b = int(t1 * sr) if t1 else len(x)
        x = x[a:b]
        au["orig"] = au["orig"][:, a:b]
        au["int"] = au["int"][a:b] if au["int"] is not None else None
    n = len(x)
    prog.emit("load", 1.0, f"{n/sr:.1f}s @ {sr}Hz")

    cap = capture_arrays(x, sr, bpm=bpm, hop=hop, max_partials=max_partials,
                         prog=prog, quality=quality)
    cap.update({"source": au["path"], "int_kind": au["int_kind"],
                "prefix": prefix,
                "created": time.strftime("%Y-%m-%d %H:%M:%S")})

    render = render_capture(cap, prog=prog, stage_render="render")

    out_dir = out_dir or (os.path.join(SONGS, f"{name}_spectral")
                          if prefix == "spectral" else
                          os.path.join(SONGS, f"{name}_spectral",
                                       prefix.replace("spectral_", "", 1)))
    os.makedirs(out_dir, exist_ok=True)
    files = {"capture": os.path.join(out_dir, "capture.json"),
             "render": os.path.join(out_dir, "render.wav"),
             "residual": os.path.join(out_dir, "residual.wav"),
             "source": os.path.join(out_dir, "source.wav")}
    prog.emit("residual", 0.2, "integer-exact residual")
    ch = au["orig"].shape[0]
    if au["int"] is not None and au["int_kind"] == "int16":
        r_i = np.round(np.clip(render, -1.0, 1.0) * 32767.0).astype(np.int64)
        resid = (au["int"] - r_i[:, None]).astype(np.float64) / 32768.0   # exact in f32/f64
        byte_capable = True
    else:
        resid = (au["orig"] - render[None, :]).T
        byte_capable = False
    if mode == "lossless":
        save_wav_f32(files["residual"], resid, sr)
    else:
        files.pop("residual")
    save_wav_f32(files["render"], render, sr)
    save_wav_i16(files["source"], au["orig"].T if ch > 1 else x, sr)
    cap["files"] = {k: os.path.relpath(v, ROOT) for k, v in files.items()}
    cap["mode"] = mode
    cap["byte_capable"] = bool(byte_capable)
    prog.emit("residual", 1.0)

    prog.emit("verify", 0.1, "scoring fidelity")
    m = verify_arrays(x, render, sr)
    if mode == "lossless":
        recon = reconstruct_lossless(render, resid, au)
        m["byte_exact"] = bool(au["int"] is not None
                               and np.array_equal(recon, au["int"]))
        if au["int"] is None:
            m["byte_exact"] = bool(np.allclose((resid.T + render[None, :]),
                                               au["orig"], atol=1e-7))
    cap["fidelity"] = m
    json.dump(cap, open(files["capture"], "w"))
    prog.emit("verify", 1.0, f"spectral {m['spectral_pct']}% | corr {m['wave_corr']}")
    tk = cap["tracks"]
    prog.say(f"capture -> {os.path.relpath(files['capture'], ROOT)} "
             f"({len(tk['partials'])}+{len(tk.get('clicks', []))}"
             f"+{len(tk['noise'])} notes) | spectral {m['spectral_pct']}% "
             f"si_sdr {m['si_sdr_db']}dB"
             + (f" | BYTE-EXACT {m.get('byte_exact')}" if mode == "lossless" else ""))
    return cap


def reconstruct_lossless(render, resid, au):
    """render (mono float) + residual (n,ch float) -> original integers."""
    r_i = np.round(np.clip(render, -1.0, 1.0) * 32767.0).astype(np.int64)
    return r_i[:, None] + np.round(resid * 32768.0).astype(np.int64)

# ------------------------------------------------------------------ render (MIDI)
def _match_notes(cur_notes, cap_notes):
    """Match current song notes to captured notes: exact (start,len,pitch) first,
    then nearest same-pitch-class / any with a transform. Returns list of
    (cur, cap, transform) + list of unmatched cur. transform = (dt_beats,
    dpitch_semis, stretch)."""
    used = [False] * len(cap_notes)
    out, new = [], []
    by_key = {}
    for i, cn in enumerate(cap_notes):
        by_key.setdefault((round(cn["start"], 4), round(cn["len"], 4), cn["pitch"]),
                          []).append(i)
    for nt in cur_notes:
        key = (round(float(nt["start"]), 4), round(float(nt["len"]), 4),
               int(nt["pitch"]))
        hit = None
        for i in by_key.get(key, []):
            if not used[i]:
                hit = i
                break
        if hit is not None:
            used[hit] = True
            out.append((nt, cap_notes[hit], (0.0, 0, 1.0)))
            continue
        # transformed match: nearest unused by (start, pitch) distance
        best, bd = -1, 1e18
        for i, cn in enumerate(cap_notes):
            if used[i]:
                continue
            d = (abs(float(nt["start"]) - cn["start"]) * 4.0
                 + abs(int(nt["pitch"]) - cn["pitch"]) * 0.5
                 + abs(float(nt.get("len", cn["len"])) - cn["len"]))
            if d < bd:
                bd, best = d, i
        if best >= 0 and bd < 24.0:
            used[best] = True
            cn = cap_notes[best]
            stretch = float(nt.get("len", cn["len"])) / max(cn["len"], 1e-9)
            out.append((nt, cn, (float(nt["start"]) - cn["start"],
                                 int(nt["pitch"]) - cn["pitch"], stretch)))
        else:
            new.append(nt)
    return out, new


def render_capture(cap, song_notes=None, prog=None, stage_render="render",
                   lossless_out=None):
    """Deterministic render of a capture (optionally against EDITED song notes).
    Returns mono float64. song_notes = {'partials': [...], 'noise': [...]} with
    plain notes; None = render the capture verbatim (byte-exact contract)."""
    prog = prog or _NULL_PROG
    sr, hop, n = cap["sr"], cap["hop"], cap["n_samples"]
    spb = 60.0 / cap["bpm"]
    y = np.zeros(n + 8 * hop, dtype=np.float64)

    cap_p = cap["tracks"]["partials"]
    cap_nz = cap["tracks"]["noise"]
    cap_ck = cap["tracks"].get("clicks", [])
    if song_notes is None:
        matched = [(cn, cn, (0.0, 0, 1.0)) for cn in cap_p]
        new_notes = []
        nz_matched = [(cn, cn, (0.0, 0, 1.0)) for cn in cap_nz]
        nz_new = []
        ck_matched = [(cn, cn, (0.0, 0, 1.0)) for cn in cap_ck]
    else:
        matched, new_notes = _match_notes(song_notes.get("partials", []), cap_p)
        nz_matched, nz_new = _match_notes(song_notes.get("noise", []), cap_nz)
        ck_matched, _ = _match_notes(song_notes.get("clicks", []), cap_ck)

    total = max(1, len(matched) + len(new_notes))
    for i, (nt, cn, (dt, dp, stretch)) in enumerate(matched):
        sp = cn["sp"]
        start_s = (cn["start"] + dt) * spb
        K = max(2, int(round(cn["len"] * stretch * spb * sr / hop)))
        tb = (np.arange(K) * hop / sr) / spb / max(stretch, 1e-9)
        f_ref = float(midi_to_hz(cn["pitch"] + dp))
        cents = env_sample(sp["bend"], tb)
        freq = f_ref * 2.0 ** (cents / 1200.0)
        amp = env_sample(sp["gain"], tb) * sp["peak"] \
            * (float(nt.get("vel", cn["vel"])) / max(cn["vel"], 1e-9))
        pristine = (dt == 0.0 and dp == 0 and abs(stretch - 1.0) < 1e-9
                    and abs(float(nt.get("vel", cn["vel"])) - cn["vel"]) < 1e-9)
        ph = np.full(K, -1.0)
        ph[0] = sp["ph0"]
        if pristine and sp.get("plock"):
            for tl, pl in sp["plock"]:
                k = int(round(tl * spb * sr / hop))
                if 0 <= k < K:
                    ph[k] = pl
        # integrate phase, spreading each lock's correction across its span
        w = TWO_PI * freq / sr
        phase = np.empty(K)
        phase[0] = ph[0]
        seg_start = 0
        for k in range(1, K):
            phase[k] = phase[k - 1] + (w[k - 1] + w[k]) * hop / 2.0
            if ph[k] >= 0:
                err = ((ph[k] - phase[k] + math.pi) % TWO_PI) - math.pi
                span = k - seg_start
                if span > 0:
                    phase[seg_start + 1:k + 1] += err * (np.arange(1, span + 1) / span)
                seg_start = k
        phase %= TWO_PI
        alive_at_end = int(round(start_s * sr)) + K * hop >= n - hop
        seg = _mq_render_track(freq, amp, phase, sr, hop,
                               sustain_tail=alive_at_end)
        s0 = int(round(start_s * sr)) - hop
        a, b = max(0, s0), min(len(y), s0 + len(seg))
        if b > a:
            y[a:b] += seg[a - s0:b - s0]
        if (i & 255) == 0:
            prog.emit(stage_render, 0.05 + 0.75 * i / total, f"partials {i}/{total}")

    for nt in new_notes:                       # brand-new notes: clean sine, AD env
        start_s = float(nt["start"]) * spb
        dur_s = max(0.03, float(nt.get("len", 0.25)) * spb)
        K = max(2, int(round(dur_s * sr / hop)))
        f = float(midi_to_hz(int(nt["pitch"])))
        amp = float(nt.get("vel", 0.8)) * 0.2 * np.minimum(
            1.0, np.linspace(0, K * hop / sr, K) / 0.01) \
            * np.exp(-np.linspace(0, dur_s, K) / max(dur_s * 0.7, 0.05))
        seg = _mq_render_track(np.full(K, f), amp, np.full(K, -1.0), sr, hop)
        s0 = int(round(start_s * sr)) - hop
        a, b = max(0, s0), min(len(y), s0 + len(seg))
        if b > a:
            y[a:b] += seg[a - s0:b - s0]

    # transient snippets: exact waveforms, placed like MIDI (move/vel/pitch-rate)
    import base64
    for nt, cn, (dt, dp, stretch) in ck_matched:
        sp_ = cn.get("sp") or {}
        if "snip" not in sp_:
            continue
        q = np.frombuffer(base64.b64decode(sp_["snip"]), dtype=np.int16)
        q = q.astype(np.float64) / 32767.0 * float(sp_["speak"])
        q = q * (float(nt.get("vel", cn["vel"])) / max(cn["vel"], 1e-9))
        if dp:                                   # pitch edit = playback rate
            idx = np.arange(0.0, len(q) - 1.0, 2.0 ** (dp / 12.0))
            q = np.interp(idx, np.arange(len(q), dtype=np.float64), q)
        s0 = int(round((cn["start"] + dt) * spb * sr))
        a, b = max(0, s0), min(len(y), s0 + len(q))
        if b > a:
            y[a:b] += q[a - s0:b - s0]

    # noise notes -> band envelope grid -> deterministic shaped noise
    prog.emit(stage_render, 0.85, "noise floor")
    Kf = n // hop + 2
    nz_all_verbatim = song_notes is None or (
        not nz_new and all(dt == 0.0 and dp == 0 and abs(st - 1.0) < 1e-9
                           and abs(float(nt.get("vel", cn["vel"])) - cn["vel"]) < 1e-9
                           for nt, cn, (dt, dp, st) in nz_matched))
    nef = cap.get("noise_env")
    use_field = bool(nef) and nz_all_verbatim and len(cap_nz) > 0
    if use_field:
        import base64 as _b64
        band_env = np.frombuffer(_b64.b64decode(nef["data"]), dtype=np.float16) \
            .astype(np.float64).reshape(int(nef["bands"]), int(nef["frames"]))
        if band_env.shape[1] < Kf:
            band_env = np.pad(band_env, ((0, 0), (0, Kf - band_env.shape[1])))
        band_env = band_env[:, :Kf].copy()
        nz_matched, nz_new = [], []          # the field replaces the note path
    else:
        band_env = np.zeros((int(cap.get("noise_bands", NOISE_BANDS)), Kf))
    for nt, cn, (dt, dp, stretch) in nz_matched + [(x, x, (0.0, 0, 1.0)) for x in nz_new]:
        sp = cn.get("sp") if isinstance(cn, dict) else None
        if not sp or "noise_band" not in sp:
            continue
        b_i = int(np.clip(sp["noise_band"] + dp, 0, band_env.shape[0] - 1))
        k0 = int(round((cn["start"] + dt) * spb * sr / hop))
        K = max(1, int(round(cn["len"] * stretch * spb * sr / hop)))
        tb = (np.arange(K) * hop / sr) / spb / max(stretch, 1e-9)
        g = env_sample(sp["gain"], tb) * sp["peak"] \
            * (float(nt.get("vel", cn["vel"])) / max(cn["vel"], 1e-9))
        a, b = max(0, k0), min(Kf, k0 + K)
        if b > a:
            band_env[b_i, a:b] = np.maximum(band_env[b_i, a:b], g[a - k0:b - k0])
    if band_env.max() > 0:
        nb0 = band_env.shape[0]
        lo_rows, hi_rows = _noise_band_masks(sr, nb0, _nb_version(nb0))
        nlo, nhi = _noise_ffts(sr)
        rng = np.random.default_rng(cap.get("seed", NOISE_SEED))
        wn = rng.standard_normal(n).astype(np.float64)
        y_lo = _noise_shape_pass(None, sr, hop, nlo, lo_rows,
                                 band_env=band_env, wn=wn, n_samples=n)
        y_hi = _noise_shape_pass(None, sr, hop, nhi, hi_rows,
                                 band_env=band_env, wn=wn, n_samples=n)
        nz_verbatim = nz_all_verbatim

        def _transplant(ysig, field, nfft):
            if not (field and field.get("bits") == 8
                    and int(field.get("n_fft", 0)) == nfft and nz_verbatim):
                return ysig
            import librosa as _lb
            PH = _unpack_phase8(field["data"], int(field["bins"]),
                                int(field["frames"]),
                                codec=field.get("codec", "raw"))
            A = np.abs(_lb.stft(ysig, n_fft=nfft, hop_length=hop,
                                window="hann", center=True))
            K = min(A.shape[1], PH.shape[1])
            Z = A[:, :K] * np.exp(1j * PH[:, :K])
            for _gl in range(GL_ROUNDS):
                yt = _lb.istft(Z, hop_length=hop, window="hann", length=n)
                Sg = _lb.stft(yt, n_fft=nfft, hop_length=hop, window="hann",
                              center=True)
                Kg = min(A.shape[1], Sg.shape[1])
                Z = A[:, :Kg] * np.exp(1j * np.angle(Sg)[:, :Kg])
            return _lb.istft(Z, hop_length=hop, window="hann", length=n)
        y_hi = _transplant(y_hi, cap.get("noise_phase"), nhi)
        y_lo = _transplant(y_lo, cap.get("noise_phase_lo"), nlo)
        yn = y_lo + y_hi
        rul = None
        nrf = cap.get("noise_env_ruler")
        if nrf and nz_all_verbatim:             # edited noise -> env-derived
            rul = np.frombuffer(base64.b64decode(nrf["data"]),
                                dtype=np.float16).astype(np.float32) \
                .reshape(int(nrf["bands"]), int(nrf["frames"]))
        y[:n] += _ruler_true_finish(yn, band_env, hop, sr, n, ruler=rul)
    mxf = cap.get("mix_env_ruler")
    if mxf and song_notes is None and n >= RULER_FFT * 2 \
            and os.environ.get("SOTADAW_NO_MIXPOLISH") != "1":
        T = np.frombuffer(base64.b64decode(mxf["data"]),
                          dtype=np.float16).astype(np.float32) \
            .reshape(int(mxf["bands"]), int(mxf["frames"]))
        y[:n] = _mix_ruler_polish(y[:n], T, sr, n)
    prog.emit(stage_render, 1.0)
    return y[:n]

# ----------------------------------------------------------------------- verify
def verify_arrays(a, b, sr):
    """Honest fidelity scorecard for two mono arrays at the same sr."""
    import librosa
    n = min(len(a), len(b))
    a = np.asarray(a, dtype=np.float64)[:n]
    b = np.asarray(b, dtype=np.float64)[:n]
    # best-lag alignment within +-20ms — lag 0 is always tested, a shift is
    # applied only when it BEATS the unshifted correlation (a near-perfect
    # render must never be 'aligned' onto a worse lag)
    max_lag = int(0.02 * sr)
    if n > 4 * max_lag:
        seg = slice(n // 4, min(n, n // 4 + 10 * sr))
        xa, xb = a[seg], b[seg]

        def corr_at(L):
            xs = xb[max(0, L):]
            ya = xa[max(0, -L):]
            m = min(len(xs), len(ya))
            return float((ya[:m] * xs[:m]).sum()) / (
                float(np.sqrt((ya[:m] ** 2).sum() * (xs[:m] ** 2).sum())) + 1e-12)

        step = max(1, max_lag // 200)
        c0 = corr_at(0)
        best, bl = c0, 0
        for L in range(-max_lag, max_lag + 1, step):
            c = corr_at(L)
            if c > best:
                best, bl = c, L
        for L in range(bl - step, bl + step + 1):        # refine to the sample
            if abs(L) <= max_lag:
                c = corr_at(L)
                if c > best:
                    best, bl = c, L
        if bl and best > c0 + 1e-4:
            if bl > 0:
                b = np.concatenate([b[bl:], np.zeros(bl)])
            else:
                b = np.concatenate([np.zeros(-bl), b[:bl]])
    # spectral fidelity on log-mel (the headline)
    def meldb(x):
        S = np.abs(librosa.stft(x, n_fft=2048, hop_length=512)) ** 2
        # score within the documented reconstruction bandwidth (analysis and
        # noise banks top out at 18k; >18k is outside the contract)
        M = librosa.filters.mel(sr=sr, n_fft=2048, n_mels=128, fmin=20,
                                fmax=min(18000.0, sr * 0.5)) @ S
        return 10.0 * np.log10(M + 1e-10)
    A, B = meldb(a), meldb(b)
    K = min(A.shape[1], B.shape[1])
    # perceptual floor: differences below -80dB don't count against fidelity
    A = np.maximum(A[:, :K], -80.0) + 80.0
    B = np.maximum(B[:, :K], -80.0) + 80.0
    spec = 1.0 - float(np.abs(A - B).sum()) / float(np.maximum(A, B).sum() + 1e-12)
    # waveform
    denom = float(np.sqrt((a * a).sum() * (b * b).sum()) + 1e-12)
    corr = float((a * b).sum()) / denom
    s_target = (float((a * b).sum()) / (float((a * a).sum()) + 1e-12)) * a
    e = b - s_target
    si_sdr = 10.0 * math.log10((float((s_target ** 2).sum()) + 1e-12)
                               / (float((e ** 2).sum()) + 1e-12))
    # per-octave envelope agreement
    env_scores = []
    from scipy.signal import butter, sosfilt
    for lo in (60, 120, 250, 500, 1000, 2000, 4000, 8000):
        hi = min(lo * 2, sr * 0.45)
        sos = butter(4, [lo / (sr / 2), hi / (sr / 2)], "band", output="sos")
        ea = np.sqrt(np.convolve(sosfilt(sos, a) ** 2, np.ones(1024) / 1024, "same"))
        eb = np.sqrt(np.convolve(sosfilt(sos, b) ** 2, np.ones(1024) / 1024, "same"))
        if ea.max() > 1e-7:
            c = float(np.corrcoef(ea[::256], eb[::256])[0, 1])
            if not math.isnan(c):
                env_scores.append(max(0.0, c))
    return {"spectral_pct": round(100.0 * max(0.0, spec), 2),
            "wave_corr": round(corr, 4),
            "si_sdr_db": round(si_sdr, 2),
            "env_corr": round(float(np.mean(env_scores)) if env_scores else 0.0, 4),
            "n_seconds": round(n / sr, 2)}


def verify_files(path_a, path_b):
    A, B = load_audio(path_a), load_audio(path_b)
    if A["sr"] != B["sr"]:
        import librosa
        B["x"] = librosa.resample(B["x"], orig_sr=B["sr"], target_sr=A["sr"])
    m = verify_arrays(A["x"], B["x"], A["sr"])
    if A["int"] is not None and B["int"] is not None \
            and A["int"].shape == B["int"].shape:
        m["byte_exact"] = bool(np.array_equal(A["int"], B["int"]))
    return m

# ----------------------------------------------------------------------- selftest
def selftest():
    """Fast numerical proof, no files: phase convention, MQ integrity, RDP,
    noise determinism, byte-exact arithmetic."""
    sr, ok = 44100, []

    def check(name, cond, detail=""):
        ok.append(bool(cond))
        print(f"  {'PASS' if cond else 'FAIL'}  {name} {detail}")

    t = np.arange(int(sr * 1.5)) / sr
    x = 0.4 * np.sin(TWO_PI * 440.0 * t + 1.234) + 0.2 * np.sin(TWO_PI * 883.0 * t)
    parts, hop = analyze(x, sr, prog=_NULL_PROG)
    pk = max(float(p["amp"].max()) for p in parts)
    strong = [p for p in parts if float(p["amp"].max()) > pk * 10 ** (-40 / 20.0)]
    check("analysis finds 2 significant partials", len(strong) == 2,
          f"({len(strong)} strong / {len(parts)} total)")
    y = resynth_exact(parts, hop, sr, len(x))
    res_db = 10 * math.log10(float(((x - y)[hop * 4:-hop * 4] ** 2).mean())
                             / float((x[hop * 4:-hop * 4] ** 2).mean()))
    check("analysis-phase resynth residual < -25dB", res_db < -25.0, f"({res_db:.1f}dB)")

    cap = {"version": 1, "sr": sr, "hop": hop, "bpm": 120.0, "n_samples": len(x),
           "seed": NOISE_SEED,
           "tracks": {"partials": [n for n in
                                   (_partial_to_note(tr, hop, sr, 0.5) for tr in parts)
                                   if n], "noise": []}}
    r1 = render_capture(cap)
    r2 = render_capture(cap)
    check("render deterministic", np.array_equal(r1, r2))
    m = verify_arrays(x, r1, sr)
    check("pure-tone spectral >= 99", m["spectral_pct"] >= 99.0, f"({m})")
    check("pure-tone si_sdr >= 20dB (phase locks)", m["si_sdr_db"] >= 20.0)

    e = [[i * 0.01, math.sin(i * 0.1)] for i in range(500)]
    d = rdp(e, 0.01)
    samp = env_sample(d, np.array([p[0] for p in e]))
    check("rdp error bound", float(np.abs(samp - [p[1] for p in e]).max()) <= 0.011,
          f"(kept {len(d)}/500)")

    rng_a = noise_render(np.ones((NOISE_BANDS, 50)) * 0.01, sr, hop, 12800)
    rng_b = noise_render(np.ones((NOISE_BANDS, 50)) * 0.01, sr, hop, 12800)
    check("noise deterministic", np.array_equal(rng_a, rng_b))

    xi = np.round(np.clip(x, -1, 1) * 32767).astype(np.int64)[:, None]
    r_i = np.round(np.clip(r1, -1, 1) * 32767.0).astype(np.int64)
    resid = (xi - r_i[:, None]).astype(np.float64) / 32768.0
    recon = r_i[:, None] + np.round(resid * 32768.0).astype(np.int64)
    check("lossless integer arithmetic byte-exact", np.array_equal(recon, xi))

    print(f"[selftest] {sum(ok)}/{len(ok)} passed")
    return all(ok)

# ------------------------------------------------------------------ DAW wiring
def inject_into_song(cap, song_path):
    """Land a capture in a song.json as EDITABLE lanes:
      spectral_low/mid/high  partial notes by register (muted sketch lanes —
                             the piano roll edits them; the renderer matches
                             them back to their envelopes by identity)
      spectral_clicks        transient snippets (move a click like a note)
      spectral_noise         band-energy notes (pitch row = mel band)
      spectral_mix           the deterministic render (the audible truth)
      spectral_residual      lossless only: mix + residual == the original
    Idempotent: existing spectral_* tracks are replaced."""
    files = cap.get("files", {})
    P = cap.get("prefix", "spectral")
    if os.path.exists(song_path):
        song = json.load(open(song_path))
    else:
        song = {"version": 2, "bpm": cap["bpm"], "lengthBars": 1,
                "masterGainDb": 0.0, "tracks": []}
    own = {P + suf for suf in ("_low", "_mid", "_high", "_clicks", "_noise",
                               "_mix", "_residual")}
    song["tracks"] = [t for t in song.get("tracks", [])
                      if str(t.get("name", "")) not in own]
    spb = 60.0 / float(song.get("bpm", cap["bpm"]))
    bars = int(math.ceil(cap["n_samples"] / cap["sr"] / spb / 4.0)) + 1
    song["lengthBars"] = max(int(song.get("lengthBars", 1)), bars)

    def plain(ns):
        return [{"start": n["start"], "len": n["len"], "pitch": n["pitch"],
                 "vel": n["vel"]} for n in ns]

    parts = cap["tracks"]["partials"]
    cap_rel = files.get("capture", "")
    lanes = [(P + "_low", [n for n in parts if n["pitch"] < 48]),
             (P + "_mid", [n for n in parts if 48 <= n["pitch"] <= 72]),
             (P + "_high", [n for n in parts if n["pitch"] > 72])]
    for nm, ns in lanes:
        if ns:
            # LIVE MONITOR VOICE (app/SpectralVoicePlugin.h): unmute the lane
            # (and mute P_mix) to HEAR edits immediately; the deterministic
            # tools/spectral.py render stays the byte-exact reference.
            song["tracks"].append({"name": nm,
                                   "source": {"kind": "spectral",
                                              "id": f"{cap_rel}#partials"},
                                   "gainDb": 0, "muted": True,
                                   "notes": plain(ns)})
    if cap["tracks"].get("clicks"):
        song["tracks"].append({"name": P + "_clicks",
                               "source": {"kind": "faust", "id": "pluck"},
                               "gainDb": -6, "muted": True,
                               "notes": plain(cap["tracks"]["clicks"])})
    if cap["tracks"]["noise"]:
        song["tracks"].append({"name": P + "_noise",
                               "source": {"kind": "faust", "id": "sub_clean"},
                               "gainDb": -12, "muted": True,
                               "notes": plain(cap["tracks"]["noise"])})
    if files.get("render"):
        song["tracks"].append({"name": P + "_mix",
                               "source": {"kind": "audio", "id": "spectral"},
                               "gainDb": 0, "notes": [],
                               "audioClips": [{"file": files["render"],
                                               "startBeat": 0}]})
    if cap.get("mode") == "lossless" and files.get("residual"):
        song["tracks"].append({"name": P + "_residual",
                               "source": {"kind": "audio", "id": "spectral"},
                               "gainDb": 0, "notes": [],
                               "audioClips": [{"file": files["residual"],
                                               "startBeat": 0}]})
    json.dump(song, open(song_path, "w"), indent=1)
    return song_path


def export_mpe(cap, out_mid):
    """Spectral MIDI -> MPE Standard MIDI File: partial notes rotate channels
    2-16, each with its own pitch-bend curve (range +-48 semis via RPN) and
    CC11 gain envelope. Any MPE synth approximates the capture; our renderer
    stays the reference."""
    import mido
    spb = 60.0 / cap["bpm"]
    mid = mido.MidiFile(ticks_per_beat=960)
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=int(spb * 1e6), time=0))
    BEND_RANGE = 48.0
    events = []                       # (tick, order, mido.Message)
    for ch in range(1, 16):           # MPE member channels 2..16 (0-indexed)
        for cc, v in ((101, 0), (100, 0), (6, int(BEND_RANGE)), (38, 0)):
            events.append((0, 0, mido.Message("control_change", channel=ch,
                                              control=cc, value=v, time=0)))
    ch_rr = 0
    for lane, notes in cap["tracks"].items():
        for n in notes:
            sp_ = n.get("sp") or {}
            if lane == "partials":
                ch = 1 + (ch_rr % 15)
                ch_rr += 1
            else:
                ch = 0                # clicks/noise ride the master channel
            t0 = int(round(n["start"] * 960))
            t1 = t0 + max(1, int(round(n["len"] * 960)))
            vel = max(1, min(127, int(round(n["vel"] * 127))))
            events.append((t0, 1, mido.Message("note_on", channel=ch,
                                               note=int(n["pitch"]),
                                               velocity=vel, time=0)))
            for tb, c in (sp_.get("bend") or [])[:400]:
                b = int(np.clip(c / 100.0 / BEND_RANGE * 8192.0, -8192, 8191))
                events.append((t0 + int(round(tb * 960)), 2,
                               mido.Message("pitchwheel", channel=ch, pitch=b,
                                            time=0)))
            for tb, g in (sp_.get("gain") or [])[:400]:
                events.append((t0 + int(round(tb * 960)), 2,
                               mido.Message("control_change", channel=ch,
                                            control=11,
                                            value=max(0, min(127, int(g * 127))),
                                            time=0)))
            events.append((t1, 3, mido.Message("note_off", channel=ch,
                                               note=int(n["pitch"]),
                                               velocity=0, time=0)))
    events.sort(key=lambda ev: (ev[0], ev[1]))
    last = 0
    for tick, _, msg in events:
        msg.time = tick - last
        last = tick
        tr.append(msg)
    mid.save(out_mid)
    return out_mid


# --------------------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("capture")
    c.add_argument("audio")
    c.add_argument("--name", default=None)
    c.add_argument("--bpm", type=float, default=120.0)
    c.add_argument("--mode", choices=["lossless", "spectral"], default="lossless")
    c.add_argument("--t0", type=float, default=None)
    c.add_argument("--t1", type=float, default=None)
    c.add_argument("--max-partials", type=int, default=None)
    c.add_argument("--quiet", action="store_true")
    c.add_argument("--into", default=None,
                   help="song.json to land the lanes in (created if missing)")
    c.add_argument("--prefix", default="spectral",
                   help="lane prefix (per-stem captures coexist: spectral_drums...)")
    c.add_argument("--quality", choices=["fast", "standard", "max"], default="max",
                   help="fast=interactive (~3x realtime), max=fidelity path (default)")

    r = sub.add_parser("render")
    r.add_argument("capture")
    r.add_argument("out")
    r.add_argument("--song", default=None,
                   help="song.json with (possibly edited) spectral_* tracks")
    r.add_argument("--lossless", action="store_true",
                   help="add the residual layer -> byte-exact int16 out")
    r.add_argument("--f32", action="store_true",
                   help="write float32 (the engine-summable clip format)")

    em = sub.add_parser("export-mpe")
    em.add_argument("capture")
    em.add_argument("out")

    v = sub.add_parser("verify")
    v.add_argument("a")
    v.add_argument("b")
    v.add_argument("--json", action="store_true")

    rt = sub.add_parser("roundtrip")
    rt.add_argument("audio")
    rt.add_argument("--bpm", type=float, default=120.0)
    rt.add_argument("--mode", choices=["lossless", "spectral"], default="lossless")

    sub.add_parser("selftest")
    a = ap.parse_args()

    if a.cmd == "selftest":
        sys.exit(0 if selftest() else 1)

    if a.cmd == "capture":
        cap = capture(a.audio, name=a.name, bpm=a.bpm, mode=a.mode, t0=a.t0,
                      t1=a.t1, max_partials=a.max_partials, prefix=a.prefix,
                      quality=a.quality,
                      prog=Prog([("load", 3), ("analyze", 38), ("carve", 22),
                                 ("notes", 7), ("render", 22), ("residual", 5),
                                 ("verify", 3)], quiet=a.quiet))
        if a.into:
            inject_into_song(cap, a.into)
            print(f"[spectral] lanes -> {a.into}")
        print(json.dumps(cap["fidelity"]))
        return

    if a.cmd == "export-mpe":
        cap = json.load(open(a.capture))
        export_mpe(cap, a.out)
        print(f"[spectral] MPE midi -> {a.out}")
        return

    if a.cmd == "render":
        cap = json.load(open(a.capture))
        song_notes = None
        if a.song:
            song = json.load(open(a.song))
            P = cap.get("prefix", "spectral")
            # EXACT lane names only: prefix "spectral" must not swallow
            # "spectral_koji_low" (a sibling capture's lane)
            part_lanes = {P + "_low", P + "_mid", P + "_high"}
            song_notes = {"partials": [], "noise": [], "clicks": []}
            for tr in song.get("tracks", []):
                nm = tr.get("name", "")
                if nm == P + "_noise":
                    song_notes["noise"] += tr.get("notes", [])
                elif nm == P + "_clicks":
                    song_notes["clicks"] += tr.get("notes", [])
                elif nm in part_lanes:
                    song_notes["partials"] += tr.get("notes", [])
        prog = Prog([("render", 90), ("write", 10)], label="render")
        y = render_capture(cap, song_notes=song_notes, prog=prog)
        if a.lossless and cap.get("files", {}).get("residual"):
            import soundfile as sf
            resid, rsr = sf.read(os.path.join(ROOT, cap["files"]["residual"]),
                                 dtype="float64", always_2d=True)
            n = min(len(y), len(resid))
            out_i = reconstruct_lossless(y[:n], resid[:n], {"int": None})
            out_i = np.clip(out_i, -32768, 32767).astype(np.int16)
            import soundfile as sf2
            sf2.write(a.out, out_i, cap["sr"], subtype="PCM_16")
        elif a.f32:
            save_wav_f32(a.out, y, cap["sr"])
        else:
            save_wav_i16(a.out, y, cap["sr"])
        prog.emit("write", 1.0, a.out)
        prog.say(f"rendered {a.out}")
        return

    if a.cmd == "verify":
        m = verify_files(a.a, a.b)
        if a.json:
            print(json.dumps(m))
        else:
            print(f"spectral fidelity : {m['spectral_pct']}%")
            print(f"waveform corr     : {m['wave_corr']}")
            print(f"SI-SDR            : {m['si_sdr_db']} dB")
            print(f"envelope corr     : {m['env_corr']}")
            if "byte_exact" in m:
                print(f"byte-exact        : {m['byte_exact']}")
        return

    if a.cmd == "roundtrip":
        cap = capture(a.audio, bpm=a.bpm, mode=a.mode)
        print(json.dumps(cap["fidelity"], indent=1))


if __name__ == "__main__":
    main()
