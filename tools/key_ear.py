#!/usr/bin/env python3
"""THE KEY EAR v3 — own-math key detection that survives what falsified v1.

key_battery's lab notes (2026-07-04) killed every static-profile tweak: the
aggregate chroma of a diatonic progression ~= the scale SET, so windowless K-S
confuses relatives (Am -> C major) and kick fundamentals pollute the low bins.
This kernel answers each finding with structure instead of profile tweaks:

  scale-set ambiguity  -> WINDOWED scoring (2s windows are chord-shaped, not
                          scale-shaped; per-window K-S + Temperley votes, energy
                          weighted, aggregate over time = temporal chord evidence)
                          + a CHORD-SPAN FUNCTIONAL COURT (v3): median-smoothed
                          bass-anchored root scores on a fine 0.5s track
                          run-length-encode into chord spans; each span's root
                          scores as a scale DEGREE of the candidate (a G chord
                          is I of G major but bVII of A minor — the sequence
                          evidence every profile misses), and the OPENER span
                          testifies "home" in proportion to its coverage
                          (loop material restarts at bar 1; a pickup can't
                          own the badge)
  relative confusion   -> a TONIC COURT on the shortlist: bass-register tonic
                          testimony + leading-tone evidence (a minor key's #7 is
                          OUTSIDE its relative major's set) + final-rest emphasis
  kick pollution       -> harmonic-FOLDED salience (a kick thump has no harmonic
                          series to fold; a bass note does) + per-window MEDIAN
                          over frames for the bass chroma (transients die in the
                          median, sustained notes survive)
  binning artifacts    -> global tuning-offset estimate (cents histogram over
                          spectral peaks) shifts the semitone grid before folding

Zero new dependencies (numpy only), CPU-fast (<1s for 40s @ 44.1k): safe on
analyze2's every-proposal seam. Consumers inherit through analyze2.estimate_key
(stems_import, dj_mix, reference_match, sidecar ears).

Proof: tools/key_battery.py (legacy 12 + forced-key transposition sweep).
"""
import numpy as np

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

KS_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KS_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
# Temperley-Kostka-Payne: dot-product profiles keep ABSOLUTE tonic emphasis that
# Pearson correlation subtracts away (the two votes disagree exactly where v1 failed)
TP_MAJOR = np.array([5.0, 2.0, 3.5, 2.0, 4.5, 4.0, 2.0, 4.5, 2.0, 3.5, 1.5, 4.0])
TP_MINOR = np.array([5.0, 2.0, 3.5, 4.5, 2.0, 4.0, 2.0, 4.5, 3.5, 2.0, 1.5, 4.0])

N_FFT, HOP = 8192, 2048
NOTE_LO, NOTE_HI = 28, 96          # E1..C7 salience range
BASS_HI = 52                       # notes < E3 testify in the bass court
TREBLE_LO = 48                     # notes >= C3 build the harmony chroma
N_HARM, HARM_DECAY = 5, 0.75
WIN_S = 2.0                        # scoring window (chord-scale, not song-scale)
MAX_S = 120.0                      # key evidence cap (DJ-set-length safety)


def _tuning_cents(P, freqs):
    """Global tuning offset in cents from prominent spectral peaks (A440 grid)."""
    if P.sum() <= 0:
        return 0.0
    m = (freqs >= 80.0) & (freqs <= 2000.0)
    idx = np.where(m)[0]
    if len(idx) < 8:
        return 0.0
    seg = P[idx]
    peaks = idx[1:-1][(seg[1:-1] > seg[:-2]) & (seg[1:-1] >= seg[2:])]
    if len(peaks) == 0:
        return 0.0
    order = peaks[np.argsort(P[peaks])[::-1][:60]]
    cents = []
    weights = []
    for b in order:
        # quadratic-interpolated peak frequency (the binning-artifact answer)
        if 0 < b < len(P) - 1 and P[b] > 0:
            a, c = P[b - 1], P[b + 1]
            denom = (a - 2 * P[b] + c)
            delta = 0.5 * (a - c) / denom if abs(denom) > 1e-12 else 0.0
            f = freqs[b] + delta * (freqs[1] - freqs[0])
            if f <= 0:
                continue
            midi = 69.0 + 12.0 * np.log2(f / 440.0)
            cents.append(((midi + 0.5) % 1.0 - 0.5) * 100.0)
            weights.append(float(P[b]))
    if not cents:
        return 0.0
    hist, edges = np.histogram(cents, bins=10, range=(-50, 50), weights=weights)
    off = float((edges[np.argmax(hist)] + edges[np.argmax(hist) + 1]) / 2.0)
    return off if abs(off) > 8.0 else 0.0


def _fold_matrix(sr, n_bins, cents_off):
    """(n_bins x n_notes) harmonic-fold: column m sums the spectrum at the note's
    harmonics 1..N_HARM with decaying weights + linear bin interpolation."""
    n_notes = NOTE_HI - NOTE_LO + 1
    M = np.zeros((n_bins, n_notes), dtype=np.float32)
    bin_hz = sr / float(N_FFT)
    for j, midi in enumerate(range(NOTE_LO, NOTE_HI + 1)):
        f0 = 440.0 * 2.0 ** ((midi - 69 + cents_off / 100.0) / 12.0)
        for h in range(1, N_HARM + 1):
            fb = f0 * h / bin_hz
            b = int(fb)
            if b + 1 >= n_bins:
                break
            frac = fb - b
            w = HARM_DECAY ** (h - 1)
            M[b, j] += w * (1.0 - frac)
            M[b + 1, j] += w * frac
    return M


def _window_chromas(x, sr, win_s=WIN_S, hop_s=None):
    """-> (treble_chromas[w,12], bass_chromas[w,12], weights[w]) or None.
    win_s: 2s default = chord-shaped windows. hop_s < win_s = SLIDING windows
    (the span court's clock): chord-SHAPED evidence at note-RATE sampling —
    0.5s windows tracked the lead melody note-by-note (bar 1 of a Dm7 groove
    read G/A/F roots, 2026-07-31), and chord-RATE hops would feed the span
    median one window per chord so the smoothing erases the changes."""
    if len(x) < N_FFT:
        return None
    n_take = int(min(len(x), MAX_S * sr))
    x = x[:n_take]
    n_frames = 1 + (len(x) - N_FFT) // HOP
    if n_frames < 1:
        return None
    win = np.hanning(N_FFT).astype(np.float32)
    frames = np.lib.stride_tricks.as_strided(
        x, shape=(n_frames, N_FFT),
        strides=(x.strides[0] * HOP, x.strides[0])).astype(np.float32)
    X = np.abs(np.fft.rfft(frames * win, axis=1))
    # log compression = spectral whitening: booms stop out-massing harmony
    Xc = np.log1p(X * (64.0 / (np.median(X[X > 0]) * X.shape[1] + 1e-12)))
    P = (X ** 2).sum(axis=0)
    freqs = np.fft.rfftfreq(N_FFT, 1.0 / sr)
    cents = _tuning_cents(P, freqs)
    M = _fold_matrix(sr, X.shape[1], cents)
    sal = Xc @ M                                      # (frames x notes)
    notes = np.arange(NOTE_LO, NOTE_HI + 1)
    pcs = notes % 12
    fold12 = np.zeros((len(notes), 12), dtype=np.float32)
    fold12[np.arange(len(notes)), pcs] = 1.0
    treb = sal[:, notes >= TREBLE_LO] @ fold12[notes >= TREBLE_LO]
    # bass testimony reads the LINEAR spectrum: the log-whitening that serves
    # the treble profiles FLATTENS the low register into mush (forensics:
    # near-uniform bass pcs, B-bass "mass" in a D-minor take). Linear power
    # keeps the real bass note dominant; the median still kills transients.
    bass = (X @ M)[:, notes < BASS_HI] @ fold12[notes < BASS_HI]
    fpw = max(1, int(round(win_s * sr / HOP)))        # frames per window
    hpw = max(1, int(round((hop_s if hop_s else win_s) * sr / HOP)))
    n_win = max(1, 1 + (n_frames - fpw) // hpw) if n_frames >= fpw else 1
    tc, bc, wt = [], [], []
    for w in range(n_win):
        s = w * hpw
        e = min(n_frames, s + fpw) if w < n_win - 1 else n_frames
        t = treb[s:e].sum(axis=0)
        b = np.median(bass[s:e], axis=0)              # transients die in the median
        tc.append(t / (t.sum() + 1e-9))
        bc.append(b / (b.sum() + 1e-9))
        wt.append(float(t.sum()))
    wt = np.array(wt)
    wt = wt / (wt.sum() + 1e-9)
    return np.array(tc), np.array(bc), wt


# FALSIFIED BRANCHES (2026-07-24, battery evidence — do not re-walk):
# - BASSLINE argmax-run extraction (persistence-gated): our generator triggers
#   kicks at C2 and the zone-enriched drum voice RENDERS that pitch — the
#   C-run owns the low argmax of every four-floor genre (12->5). A sustain
#   gate on runs killed staccato garage stabs with the kicks (8->7).
# - HPSS median masking at N_FFT 8192: 86% frame overlap smears transients
#   horizontal — kicks survive as "harmonic", chords get chopped (8->4).
#   HPSS wants ~1024-2048 windows; this kernel's resolution serves folding.
# FALSIFIED 2026-07-31 (span-court rungs, battery evidence):
# - Window-level position bonuses: CLOSER = a turnaround witness (disco
#   i-iv-bIII-iv handed the key to iv, 9->5), OPENER = a pickup witness
#   (salsa montuno detects V first, reggae skank starts offbeat). Only the
#   length-scaled OPENER-SPAN badge survives (a span earns "home" with
#   coverage).
# - SLIDING chord windows for the root track (2s @ 0.5s hop): boundary
#   windows mix adjacent chords and the track drifts to relative minors
#   (gospel Ab->Fm, jazz Bb->Gm; 9->8). The fine track wants DISJOINT 0.5s
#   windows + k=3 median, chord-shaped evidence be damned.


def _root_scores(tc, bc=None, bw=0.8):
    """(w,12) chord-ROOT scores per window. QUALITY-AGNOSTIC by lesson:
    major-vs-minor triads differ only at the third, and at 2s-window
    resolution busy textures decide that third by noise (trap F minor read F
    MAJOR; the mode court owns mode). Root+fifth dyads with either third are
    stable. bc = per-window BASS chroma (median-filtered, kick-proof): the
    bass STATES roots (walking bass, log drum, house sub) — treble stabs
    alone missed the tonic chord entirely in house/amapiano (2026-07-31
    forensics). A soft blend, never an argmax (passing tones stay soft)."""
    S = np.zeros((len(tc), 12), dtype=np.float64)
    for w, c in enumerate(tc):
        b = bc[w] if bc is not None else None
        for r in range(12):
            S[w, r] = (1.2 * c[r] + c[(r + 7) % 12]
                       + 0.5 * max(c[(r + 3) % 12], c[(r + 4) % 12])
                       + (bw * b[r] if b is not None else 0.0))
    return S


def _chord_spans(tc, bc=None):
    """THE CHORD-SPAN COURT's segmentation: sliding-median (k=3) over the
    bass-anchored root scores kills one-window flickers, argmax per window,
    run-length-encode -> [(root_pc, start_w, n_windows, strength)].
    Strength = span length x mean argmax margin: a long stable span outvotes
    a pickup flicker structurally (window-level votes could not — salsa's
    2s montuno pickup owned "opener", disco's turnaround owned "closer")."""
    S = _root_scores(tc, bc)
    n = len(S)
    Sm = np.empty_like(S)
    for w in range(n):
        lo, hi = max(0, w - 1), min(n, w + 2)
        Sm[w] = np.median(S[lo:hi], axis=0)
    roots = np.argmax(Sm, axis=1)
    margins = Sm[np.arange(n), roots] - np.partition(Sm, -2, axis=1)[:, -2]
    spans = []
    s = 0
    for w in range(1, n + 1):
        if w == n or roots[w] != roots[s]:
            spans.append((int(roots[s]), s, w - s,
                          float((w - s) * max(1e-6, margins[s:w].mean()))))
            s = w
    return spans


# functional weight of a chord ROOT (as scale degree) in a key — the SEQUENCE
# evidence every static profile misses: a G chord is I of G major but bVII of
# A minor; only function + position can tell those apart. An i-bVII-bVI set
# (amapiano/house minor) is ALL in-table for the minor key but reads b7+b6
# junk under its C-major twin — the exact class aggregate chroma confuses.
_DEG_MAJ = {0: 3.0, 7: 2.0, 5: 1.7, 9: 1.2, 2: 1.0, 4: 0.8, 10: 0.5, 11: 0.3}
_DEG_MIN = {0: 3.0, 7: 1.8, 10: 1.5, 8: 1.5, 5: 1.5, 3: 1.2, 2: 0.5, 11: 0.3}
FN_W = 0.6                          # court weight of the functional term
                                    # (advisory: must not override bass court)


def _functional_score(spans, tonic, minor):
    """Chord-SPAN functional court: each span's root scores as a scale DEGREE
    of the candidate, weighted by span strength (length x stability)."""
    if not spans:
        return 0.0
    table = _DEG_MIN if minor else _DEG_MAJ
    tot = wsum = 0.0
    for root, _start, _n, strength in spans:
        deg = (root - tonic) % 12
        tot += table.get(deg, -1.2) * strength
        wsum += strength
    score = tot / (wsum + 1e-9)
    # OPENER SPAN = HOME, LENGTH-SCALED. Loop material restarts at bar 1 —
    # but window-level opener/closer testimony was battery-falsified today
    # (disco's turnaround owned "closer", salsa's 2s montuno pickup owned
    # "opener"). A span must EARN the badge with coverage: full weight only
    # when the opening span owns >=half the material.
    n_total = sum(s[2] for s in spans)
    if spans[0][0] == tonic:
        score += 0.8 * min(1.0, 2.0 * spans[0][2] / max(1, n_total))
    return score


def _profile_scores(tc, wt):
    """Windowed K-S correlation + Temperley dot, energy-weighted -> (24,) in key
    order [C major, C minor, C# major, ...]."""
    tpM = TP_MAJOR / TP_MAJOR.sum()
    tpm = TP_MINOR / TP_MINOR.sum()
    out = np.zeros(24)
    for rot in range(12):
        c = np.roll(tc, -rot, axis=1)                 # (w,12) aligned to tonic=0
        cz = c - c.mean(axis=1, keepdims=True)
        cs = cz / (np.linalg.norm(cz, axis=1, keepdims=True) + 1e-9)
        for k, (prof, tp) in enumerate(((KS_MAJOR, tpM), (KS_MINOR, tpm))):
            pz = prof - prof.mean()
            pz = pz / np.linalg.norm(pz)
            corr = cs @ pz                            # per-window Pearson
            dot = (c * tp).sum(axis=1) * 12.0         # absolute-emphasis vote
            out[rot * 2 + k] = float((wt * (corr + 0.5 * (dot - 1.0))).sum())
    return out


def key_from_audio(x, sr):
    """-> (key_name|None, confidence 0..1, evidence dict). x mono float."""
    got = _window_chromas(np.asarray(x, dtype=np.float32), sr)
    if got is None:
        return None, 0.0, {}
    tc, bc, wt = got
    agg = (tc * wt[:, None]).sum(axis=0)
    agg = agg / (agg.sum() + 1e-9)
    base = _profile_scores(tc, wt)
    order = np.argsort(base)[::-1]
    short = order[:6]
    bass_mean = (bc * wt[:, None]).sum(axis=0)
    bass_mean = bass_mean / (bass_mean.sum() + 1e-9)
    final_t, final_b = tc[-1], bc[-1]
    head_t, head_b = tc[0], bc[0]
    # THE SPAN COURT reads a FINER clock than the profile windows: 0.5s
    # root-track windows, k=3-median smoothed, RLE'd into chord spans
    # (a 1-bar chord = ~4 windows, survives; a pickup flicker = 1, dies).
    fine = _window_chromas(np.asarray(x, dtype=np.float32), sr, win_s=0.5)
    spans = _chord_spans(fine[0], fine[1]) if fine is not None else []
    # out-of-set costs: Pearson blurs exact membership, but Am-vs-G IS "F or F#"
    # and Dm-vs-C IS "Bb or B". Soft spots: major forgives b7 (mixolydian is
    # everywhere) and half-forgives the blue b3; minor forgives the harmonic #7
    # and half-forgives the dorian 6.
    MAJ_COST = np.ones(12); MAJ_COST[[0, 2, 4, 5, 7, 9, 11]] = 0.0
    MAJ_COST[10] = 0.3; MAJ_COST[3] = 0.5
    MIN_COST = np.ones(12); MIN_COST[[0, 2, 3, 5, 7, 8, 10]] = 0.0
    MIN_COST[11] = 0.1; MIN_COST[9] = 0.5
    court = {}
    for ki in short:
        tonic, minor = ki // 2, ki % 2 == 1
        fifth = (tonic + 7) % 12
        bass_ev = bass_mean[tonic] + 0.33 * bass_mean[fifth]
        if minor:
            # harmonic minor's #7 lives OUTSIDE the relative major's pc set;
            # the natural 7 (subtonic) argues for the relative major instead
            lt_ev = agg[(tonic + 11) % 12] - 0.5 * agg[(tonic + 10) % 12]
            out_pen = float(np.roll(MIN_COST, tonic) @ agg)
        else:
            # mass on b6 (the relative minor's #7) argues AGAINST this major
            lt_ev = -agg[(tonic + 8) % 12]
            out_pen = float(np.roll(MAJ_COST, tonic) @ agg)
        rest_ev = 0.5 * (final_t[tonic] + final_b[tonic])
        head_ev = 0.5 * (head_t[tonic] + head_b[tonic])
        fn_ev = _functional_score(spans, tonic, minor)
        # SUBDOMINANT-DOMINANCE: when a candidate's own 4th out-masses its
        # tonic in the bass, the 4th is probably home (kills fifth-up errors:
        # a B-major candidacy dies when E owns the bass). One-sided, bass-only.
        sub_pen = max(0.0, float(bass_mean[(tonic + 5) % 12] - bass_mean[tonic]))
        court[ki] = float(base[ki] + 2.2 * bass_ev + 1.6 * lt_ev
                          + 0.8 * rest_ev + 0.8 * head_ev - 3.0 * out_pen
                          - 1.5 * sub_pen + FN_W * fn_ev)
    ranked = sorted(court.items(), key=lambda kv: -kv[1])
    best, s1 = ranked[0]
    s2 = ranked[1][1] if len(ranked) > 1 else s1 - 1.0
    name = f"{NOTE_NAMES[best // 2]} {'minor' if best % 2 else 'major'}"
    conf = float(min(1.0, max(0.0, (s1 - s2) * 2.5)))
    return name, round(conf, 2), {
        "tuning_windows": int(len(wt)),
        "runner_up": f"{NOTE_NAMES[ranked[1][0] // 2]} {'minor' if ranked[1][0] % 2 else 'major'}" if len(ranked) > 1 else None,
        "margin": round(float(s1 - s2), 4)}


if __name__ == "__main__":
    import json
    import sys
    from scipy.io import wavfile
    sr_, x_ = wavfile.read(sys.argv[1])
    if x_.dtype == np.int16:
        x_ = x_.astype(np.float32) / 32768.0
    elif x_.dtype == np.int32:
        x_ = x_.astype(np.float32) / 2147483648.0
    else:
        x_ = x_.astype(np.float32)
    if x_.ndim > 1:
        x_ = x_.mean(axis=1)
    k, c, ev = key_from_audio(x_, sr_)
    print(json.dumps({"key": k, "conf": c, **ev}))
