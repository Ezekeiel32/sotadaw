#!/usr/bin/env python3
"""SOURCE KIT v3 — imported stems must SOUND like their audio counterparts
(Chezy's identity law, 2026-07-08): the MIDI triggers the record's OWN audio.

Three builders, all engine-calibrated:

  build_source_kit(stem_wav, notes, name)      drums: per-GM-lane exemplars
  build_pitched_kit(stem_wav, notes, name)     vocals/other/bass: REAL pitches
                                               in the roll, one exemplar slice
                                               per distinct pitch, range-filled
                                               zones (edits keep speaking) +
                                               sustain/salvage/closed-loop laws
  build_phrase_kit(stem_wav, notes, name)      RETIRED from sketch lanes (the
                                               sequential-key staircase
                                               photocopied the audio lane —
                                               Chezy rejected it live); kept
                                               for chop/reference tooling

THE ENGINE LAW (measured through the real m1 binary, 2026-07-08 rig):
  tracktion SamplerPlugin maps velocity to dB: gain = zoneGainDb - 20*(1-vel),
  constant trim 0.00dB (mono->stereo center loses nothing). So the linear
  factor is 10^(vel-1): vel 1.0 = unity, 0.5 = -10dB, 0.05 = -19dB. Every
  gainDb and every velocity here is computed through THAT law — the old
  "wav*gain*vel" linear assumption played snares 25dB down.

THE ANCHOR LAW (v4 CEILING): never trust an exemplar slice's absolute level
(a gutted or mispicked slice baked the snare -28.8dB). Anchor to the STEM's
CEILING: lane_ref = the lane's LOUDEST measured band-peak (capped p95+9dB vs
glitch measurements); zone gainDb makes vel=1.0 reproduce that ceiling in the
lane's own band. Per-hit velocities (transcribe_stems v5, same law) carry
each hit's measured distance below the ceiling, so `zone @ vel` reproduces
the record's level hit by hit AND no real accent ever clamps — the old p95
anchor squashed the top 5% (every accent) to the p95 level: baked-in
limiting, "NON SNAPPY" (Chezy 2026-07-08).

kit.json gains "openEnded": true for drum kits (the engine gates samples at
note-off otherwise — a 26ms hat note amputated the record's ring).

Every choice is measurable: render_notes() lays the slices back through the
ENGINE law so a battery can verify the kit against the source stem.
Pure numpy/scipy + stdlib wave — no engine, no GPU.
"""
import json
import math
import os
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KITS = os.path.join(ROOT, "kits")

LANE_NAME = {36: "kick", 38: "snare", 39: "perc", 42: "hat_closed",
             46: "hat_open", 49: "crash",
             # drum-pieces rail (tools/drumsep): physical toms + ride lanes.
             # Pitches chosen to match gm_drums' shipped voices (43/47/50/51)
             # so the stock-kit fallback can never leave them silent.
             43: "tom_lo", 47: "tom_mid", 50: "tom_hi", 51: "ride"}
# per-lane slice ceiling (s): a hat exemplar must not drag half a bar of bleed
LANE_MAX_S = {36: 0.45, 38: 0.40, 39: 0.30, 42: 0.12, 46: 0.60, 49: 1.60,
              43: 0.55, 47: 0.50, 50: 0.45, 51: 1.20}
# the DETECTION bands (transcribe_stems drum lanes) — measurement and playback
# anchoring go through the SAME filter, so the calibration equation closes
LANE_BAND_HZ = {36: (0.0, 140.0), 38: (180.0, 2000.0), 39: (2000.0, 5000.0),
                42: (5500.0, 0.0), 46: (5500.0, 0.0), 49: (5500.0, 0.0),
                43: (55.0, 350.0), 47: (70.0, 450.0), 50: (90.0, 550.0),
                51: (2500.0, 0.0)}


def _load_wav(path):
    """(sr, x[N, C]) float64 — channels KEPT (identity slices ship stereo).
    soundfile-first: stems are float32 since THE CLEAN SPLIT (stdlib wave
    raises 'unknown format: 3' on IEEE-float wavs)."""
    try:
        import soundfile as sf
        x, sr = sf.read(path, dtype="float64", always_2d=True)
        return sr, x
    except Exception:
        pass
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        nch = w.getnchannels()
        sw = w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw == 2:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    elif sw == 3:  # 24-bit (the m1 render format — sampwidth law)
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = ((b[:, 0].astype(np.int32)) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        x = (x - (x >> 23 << 24)).astype(np.float64) / 8388608.0
    elif sw == 4:
        x = np.frombuffer(raw, dtype=np.int32).astype(np.float64) / 2147483648.0
    else:
        raise ValueError(f"sampwidth {sw}")
    return sr, x.reshape(-1, nch)


def _load_mono(path):
    sr, x = _load_wav(path)
    return sr, x.mean(axis=1)


def _save_wav16(path, x, sr):
    """Mono [N] or multichannel [N, C] float — 16-bit PCM."""
    x = np.clip(np.asarray(x), -1.0, 1.0)
    nch = 1 if x.ndim == 1 else x.shape[1]
    with wave.open(path, "wb") as w:
        w.setnchannels(nch)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767.0).astype(np.int16).tobytes())


def _save_mono16(path, x, sr):
    _save_wav16(path, x, sr)


def _band_filter(x, sr, lo, hi):
    """The lane's detection band. lo==0 -> lowpass(hi); hi==0 -> highpass(lo)."""
    from scipy.signal import butter, sosfilt
    ny = sr / 2.0
    if lo <= 0:
        sos = butter(4, min(hi, ny * 0.99) / ny, "low", output="sos")
    elif hi <= 0:
        sos = butter(4, min(lo, ny * 0.98) / ny, "high", output="sos")
    else:
        sos = butter(4, [lo / ny, min(hi, ny * 0.99) / ny], "band", output="sos")
    return sosfilt(sos, x)


def _hit_band_peak(xb, sr, t, pre_s=0.006, post_s=0.045):
    """The hit's peak in its lane band around time t (grid-snap tolerant)."""
    a = max(0, int((t - pre_s) * sr))
    b = min(len(xb), int((t + post_s) * sr))
    return float(np.abs(xb[a:b]).max()) if b > a else 0.0


def _find_attack(xb, sr, t, search_s=0.045):
    """The TRUE attack sample near t: notes arrive grid-snapped (up to ~26ms
    off the audio), so search +-search_s on the lane-banded envelope for the
    steepest rise, then walk back to the attack FOOT (pre-attack air) — the
    fade-in must never land on the attack itself (battery: 2ms fades shaved
    every peak, snare -10dB)."""
    a = max(0, int((t - search_s) * sr))
    b = min(len(xb), int((t + search_s) * sr))
    if b - a < 32:
        return max(0, int(t * sr))
    seg = np.abs(xb[a:b])
    env = np.convolve(seg, np.ones(24) / 24.0, "same")
    rise = np.diff(env)
    if len(rise) == 0 or float(rise.max()) <= 0:
        return max(0, int(t * sr))
    r = int(np.argmax(rise))
    floor = 0.15 * float(env[r:].max() + 1e-12)
    foot = r
    while foot > 0 and env[foot] > floor:
        foot -= 1
    return a + foot


# where each lane is ALLOWED to subtract: its home register, generous. The
# STFT frame of any onset is transient-smeared (near-flat across all bins), so
# an unbanded estimate eats the host hit's own attack — a hat "subtracting"
# 60Hz gutted the kick 7dB before this law (battery evidence, 2026-07-08).
SUB_BAND_HZ = {36: (0.0, 300.0), 38: (140.0, 6000.0), 39: (1500.0, 9000.0),
               42: (3500.0, 22050.0), 46: (3000.0, 22050.0), 49: (2000.0, 22050.0),
               43: (45.0, 800.0), 47: (55.0, 900.0), 50: (70.0, 1000.0),
               51: (2000.0, 22050.0)}


def _spectral_subtract(seg, sr, contams):
    """SOUND-AWARE DECONTAMINATION: remove co-onsetting lanes' expected
    contribution from an exemplar slice by magnitude-domain Wiener masking
    (waveform subtraction can't null independent noise content — physics).
    contams: [(clean_seg_at_expected_level, dt_seconds, lane_gm)]."""
    import librosa
    n_fft, hop = 1024, 256
    S = librosa.stft(seg.astype(np.float32), n_fft=n_fft, hop_length=hop)
    mag = np.abs(S)
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    est = np.zeros_like(mag)
    for cseg, dt, gm in contams:
        buf = np.zeros(len(seg))
        j0 = max(0, int(dt * sr))
        m = min(len(cseg), len(buf) - j0)
        if m <= 0:
            continue
        buf[j0:j0 + m] = cseg[:m]
        C = np.abs(librosa.stft(buf.astype(np.float32), n_fft=n_fft, hop_length=hop))
        lo, hi = SUB_BAND_HZ.get(gm, (0.0, sr * 0.5))
        C[(freqs < lo) | (freqs > hi), :] = 0.0          # home register only
        K = min(est.shape[1], C.shape[1])
        est[:, :K] = np.maximum(est[:, :K], C[:, :K])
    mask = np.clip((mag - 1.2 * est) / (mag + 1e-12), 0.10, 1.0)  # 1.2 = oversubtract
    out = librosa.istft(S * mask, hop_length=hop, length=len(seg))
    return out.astype(np.float64)


def engine_vel_gain(vel):
    """The measured tracktion SamplerPlugin law: linear factor for a velocity."""
    return 10.0 ** (float(vel) - 1.0)


def vel_for_level(peak, ref):
    """Velocity that makes the engine reproduce `peak` when vel=1.0 plays `ref`
    (the inverse of the dB law), clamped to the sampler's expressible range."""
    if peak <= 0 or ref <= 0:
        return 0.05
    return float(min(1.0, max(0.05, 1.0 + math.log10(peak / ref))))


# THE DRY REPLICA LAW (Chezy 2026-07-10: hits must be "very sharply clear and
# not echoey or far away" — DETECTED replicas, never snippets of the wet mix).
# A one-shot sliced from the record carries the room, the reverb tail and the
# neighbors' bleed; triggering it hundreds of times smears the product.
TAIL_S = {36: 0.32, 38: 0.28, 39: 0.16, 42: 0.08, 46: 0.45, 49: 1.40,
          43: 0.40, 47: 0.35, 50: 0.30, 51: 1.00}


def _band_shares(sig, sr):
    """Fraction of |FFT|^2 energy in identity bands: (sub<140, body 150-2500,
    hi>=4000). The measurement that convicted the opptical kit."""
    s = np.asarray(sig, dtype=np.float64)
    S = np.abs(np.fft.rfft(s * np.hanning(len(s)))) ** 2
    fr = np.fft.rfftfreq(len(s), 1.0 / sr)
    tot = float(S.sum()) + 1e-20
    return (float(S[fr < 140].sum()) / tot,
            float(S[(fr >= 150) & (fr < 2500)].sum()) / tot,
            float(S[fr >= 4000].sum()) / tot)


# THE VOICE IDENTITY CONTRACT (Chezy live 2026-07-11: "hi hat comes as SNARE
# sound and snare comes as BASS sound"): the phase-aligned median only votes
# out bleed that VARIES between instances — a MUSICALLY-LOCKED bleeder (the
# 808 hitting the same note under every open hat) is phase-consistent across
# all rows and survives the vote wearing the drum's name (measured on
# opptical_drums: snare.wav 95% sub, hat_open.wav 98% sub). Every built voice
# must WEAR ITS OWN BAND; a violator is rebuilt from band-conformed rows —
# the locked bleeder lives outside the band and dies in the filter.
#   contract(gm) -> (violates(shares) -> bool, rebuild_band (lo, hi|None))
_ID_FAMILY = {**{g: "kick" for g in (33, 35, 36)},
              **{g: "snare" for g in (34, 37, 38, 40)},
              **{g: "hat" for g in (26, 41, 42, 44, 46)},
              **{g: "cym" for g in (49, 51, 52, 55, 57, 59)},
              **{g: "tom" for g in (43, 45, 47, 48, 50)}}
_ID_CONTRACT = {
    "kick":  (lambda sub, body, hi: sub < 0.35,            (20.0, 350.0)),
    # snare family: bass-wearing (sub) OR pure-hat-wearing (no body, all hi);
    # bright clap/snap snares (hi-dominant WITH some body) pass honestly
    "snare": (lambda sub, body, hi: sub > 0.60
              or (body < 0.05 and hi > 0.80), (140.0, 8000.0)),
    "hat":   (lambda sub, body, hi: sub > 0.20 or hi < 0.15,   (3000.0, None)),
    "cym":   (lambda sub, body, hi: sub > 0.25 or hi < 0.20,   (2500.0, None)),
    # tom: fundamental lives 55-200Hz (sub+body); a hi-dominant "tom" is
    # cymbal wash on the tom lane, a pure-sub one is kick bleed
    "tom":   (lambda sub, body, hi: hi > 0.55 or sub > 0.80,   (55.0, 1200.0)),
}


def _identity_verdict(seg, sr, gm):
    """None when the voice honestly wears its band, else the rebuild band."""
    fam = _ID_FAMILY.get(gm)
    if fam is None or len(seg) < 256:
        return None
    violates, band = _ID_CONTRACT[fam]
    sub, body, hi = _band_shares(seg, sr)
    return band if violates(sub, body, hi) else None


def _band_sos(band, sr):
    from scipy.signal import butter
    lo, hi = band
    ny = sr * 0.5
    if hi is None or hi >= ny * 0.98:
        return butter(4, lo / ny, btype="highpass", output="sos")
    return butter(4, [lo / ny, hi / ny], btype="bandpass", output="sos")


def _median_replica(x, xb, sr, cands, anchor_i0, l_max, band=None):
    """Phase-aligned per-sample MEDIAN across the lane's clean instances.
    The drum itself is coherent on every hit and survives the vote; reverb
    wash, room and other-voice bleed differ per hit and get voted out.
    band=(lo,hi): rows are band-conformed BEFORE the vote (the identity-
    contract rebuild path — kills musically-locked bleed the vote cannot).
    Returns (replica, n_used, wash_suppression_db) or None (thin lane)."""
    att = int(0.015 * sr)
    ref = xb[anchor_i0:anchor_i0 + att].astype(np.float64)
    rn = float(np.linalg.norm(ref))
    if rn <= 1e-9:
        return None
    sos = None
    if band is not None:
        from scipy.signal import sosfilt
        sos = (_band_sos(band, sr), sosfilt)
    rows, lens = [], []
    # CLEAN-FIRST, CO-ADMITTED: a co-onset from ANOTHER voice differs on every
    # instance (different hat, jittered micro-timing) — the median votes it
    # out; excluding co starved kick/snare to <4 rows in dense grooves and the
    # whole law fell back to single wet slices (measured, first live run).
    for (nt, t, i0, pk, iso, co, lm) in sorted(cands, key=lambda c: (bool(c[5]), -c[3])):
        if pk <= 0:
            continue
        # FULL-BUDGET ROWS: never cap a row at its iso — the next hit differs
        # per instance (different neighbor, jittered timing) and the median
        # votes it out like any bleed. iso-capped rows cut the crash and the
        # snare to 50ms stubs (measured: p70 of iso in a dense groove).
        L = min(int(l_max * sr), len(x) - i0)
        if L < int(0.05 * sr):
            continue
        best_l, best_c = 0, -1.0
        for lag in range(-int(0.002 * sr), int(0.002 * sr) + 1, 4):
            b0 = i0 + lag
            if b0 < 0 or b0 + att > len(xb):
                continue
            seg = xb[b0:b0 + att].astype(np.float64)
            c = float(np.dot(ref, seg) / (rn * (np.linalg.norm(seg) + 1e-12)))
            if c > best_c:
                best_c, best_l = c, lag
        if best_c < 0.35:
            continue                            # a different-sounding hit
        a0 = i0 + best_l
        s = x[a0:a0 + L].astype(np.float64)
        if sos is not None:
            s = sos[1](sos[0], s)
        bp = float(np.abs(xb[a0:a0 + L]).max())
        if bp <= 1e-6:
            continue
        rows.append(s / bp)
        lens.append(L)
        if len(rows) >= 24:
            break
    if len(rows) < 4:
        return None
    lm_n = min(int(np.percentile(lens, 70)), int(l_max * sr))
    M = np.full((len(rows), lm_n), np.nan)
    for r, s in enumerate(rows):
        M[r, :min(lm_n, len(s))] = s[:lm_n]
    valid = (~np.isnan(M)).sum(axis=0)
    cut = int(np.argmax(valid < 3)) if bool((valid < 3).any()) else lm_n
    if cut < int(0.05 * sr):
        return None                             # too little common tail
    M = M[:, :cut]
    med = np.nanmedian(M, axis=0)
    w0 = int(0.04 * sr)                         # post-attack wash window
    supp = 0.0
    if cut > w0 + int(0.02 * sr):
        # receipt = what the vote removed vs shipping the strongest single
        # slice (the old product): wash-window RMS, single vs median
        single = M[0]
        e_one = float(np.sqrt(np.nanmean(single[w0:] ** 2)) + 1e-12)
        e_med = float(np.sqrt(np.nanmean(med[w0:] ** 2)) + 1e-12)
        supp = 20.0 * math.log10(max(1.0, e_one / e_med))
    return med, len(rows), round(supp, 1)


# WAVE 2 MULTI-EXEMPLAR (Chezy: "each and every note stands out … exactly
# like their audio counterparts"): a lane's hits are NOT one voice — velocity
# layers, alternate strikes, tuned toms live in one GM lane. Cluster the
# candidate pool by timbre, ship a median replica PER CLUSTER on adjacent GM
# notes, and retarget each hit to the exemplar that sounds like ITS moment.
ALT_GM = {36: (35, 33), 38: (40, 34), 39: (31, 30), 42: (44, 41),
          46: (26,), 49: (57, 52),
          43: (47,), 47: (43, 50), 50: (47,), 51: (59, 52)}


def _exemplar_clusters(cands, k_max=3, min_rows=5):
    """Timbre clusters over the candidate pool (cosine distance on the
    log-mel vectors pass 1 already computed, c[6]). Greedy medoid split,
    accepted only when k explains >=18% more spread than k-1 AND every
    cluster can still win a median vote (min_rows). Deterministic.
    Returns [(member_indices, medoid_index)] sorted largest-first."""
    n = len(cands)
    if n < 2 * min_rows:
        return [(list(range(n)), 0 if n else -1)]
    V = np.stack([c[6] for c in cands]).astype(np.float64)
    V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-12)
    D = 1.0 - V @ V.T
    med1 = int(np.argmin(D.sum(axis=1)))
    best_cost = float(D[:, med1].sum())
    best = [(list(range(n)), med1)]
    prev_meds = [med1]
    for k in (2, 3):
        if k > k_max or n < k * min_rows:
            break
        meds = list(prev_meds[:1])
        while len(meds) < k:                    # farthest-point init
            meds.append(int(np.argmax(np.min(D[:, meds], axis=1))))
        assign = np.zeros(n, dtype=int)
        for _ in range(12):                     # Lloyd over medoids
            assign = np.argmin(D[:, meds], axis=1)
            new = []
            for j in range(k):
                idx = np.where(assign == j)[0]
                if not len(idx):
                    new.append(meds[j])
                    continue
                new.append(int(idx[np.argmin(D[np.ix_(idx, idx)].sum(axis=1))]))
            if new == meds:
                break
            meds = new
        assign = np.argmin(D[:, meds], axis=1)
        sizes = [int((assign == j).sum()) for j in range(k)]
        if min(sizes) < min_rows:
            break
        c = float(sum(D[i, meds[assign[i]]] for i in range(n)))
        if c > best_cost * 0.82:                # <18% gain: one voice, stop
            break
        best_cost, prev_meds = c, meds
        best = [(sorted(np.where(assign == j)[0].tolist()), meds[j])
                for j in range(k)]
    best.sort(key=lambda mm: -len(mm[0]))
    return best


def _finish_seg(seg, sr):
    """Shared exemplar finishing: 2ms in (pre-attack air), 12ms out."""
    fi = min(len(seg), max(8, int(0.002 * sr)))
    fo = min(len(seg), max(16, int(0.012 * sr)))
    seg[:fi] *= np.linspace(0.0, 1.0, fi)
    seg[-fo:] *= np.linspace(1.0, 0.0, fo)
    return seg


def _tail_discipline(seg, sr, gm):
    """De-echo by construction: the replica must reach -60dB by its voice's
    snap budget (TAIL_S). The wet mix's room rides every slice otherwise —
    a closed hat that rings 120ms reads as 'far away'."""
    bud = TAIL_S.get(gm)
    if bud is None:
        return seg
    k = int(bud * sr)
    if len(seg) <= k:
        return seg
    fade_n = max(16, int(0.3 * bud * sr))
    out = seg[:min(len(seg), k + fade_n)].copy()
    n = len(out) - k
    if n > 0:
        out[k:] *= 10.0 ** (-3.0 * np.linspace(0.0, 1.0, n))   # 0 -> -60dB
    return out


def build_source_kit(stem_wav, notes, name, bpm=120.0, min_lanes=2):
    """Slice per-lane exemplars out of the stem. Returns kit name or None
    (too few usable lanes -> caller keeps its stock-kit fallback)."""
    sr, x = _load_mono(stem_wav)
    spb = 60.0 / bpm
    onsets_all = sorted(float(n["start"]) * spb for n in notes)
    lanes = {}
    for nt in notes:
        lanes.setdefault(int(nt["pitch"]), []).append(nt)
    lane_times = {gm: sorted(float(n["start"]) * spb for n in lns)
                  for gm, lns in lanes.items()}
    # the lane-banded stems (measurement + attack search share these)
    xb = {gm: _band_filter(x, sr, *LANE_BAND_HZ[gm])
          for gm in lanes if gm in LANE_NAME}
    # THE CEILING ANCHOR (v4): each lane's reference = its LOUDEST measured
    # band peak (capped at p95+9dB against a glitch measurement). v3 anchored
    # p95 — every hit in the top 5% (THE accents) clamped at vel 1.0 and
    # rendered squashed to the p95 level: the drums lost their snap ("NON
    # SNAPPY", Chezy 2026-07-08). vel = 1+log10(pk/ceiling) reproduces every
    # hit BELOW the ceiling exactly; nothing real clamps any more.
    # lane_body (p95) stays the yardstick for candidate tiers/dust — "how
    # strong is this hit vs the lane's true voice" is a body question.
    lane_ref = {}
    lane_body = {}
    lane_peaks = {}
    for gm, lns in lanes.items():
        if gm not in LANE_NAME:
            continue
        pks = np.array([_hit_band_peak(xb[gm], sr, float(n["start"]) * spb)
                        for n in lns])
        lane_peaks[gm] = pks
        if len(pks):
            body = float(np.percentile(pks, 95))
            lane_body[gm] = body
            lane_ref[gm] = float(min(float(pks.max()),
                                     body * 10.0 ** (9.0 / 20.0)))

    # ---- pass 1: pick each lane's REPRESENTATIVE exemplar ----
    # THE MEDOID LAW (Chezy 2026-07-08): pick the candidate whose timbre
    # (log-mel) is CLOSEST to the lane's centroid. Strength is the MEASURED
    # band peak (v3) — the detector's onset-strength vel lied (a -32dBFS
    # moment wore vel 0.72 and became the snare).
    import librosa as _lb
    _mel = _lb.filters.mel(sr=sr, n_fft=1024, n_mels=40, fmin=30,
                           fmax=min(16000.0, sr * 0.5))

    def _cand_logmel(i0):
        seg = x[i0:i0 + int(0.10 * sr)]
        if len(seg) < int(0.03 * sr):
            return None
        if len(seg) < int(0.10 * sr):
            seg = np.pad(seg, (0, int(0.10 * sr) - len(seg)))
        S = np.abs(_lb.stft(seg.astype(np.float32), n_fft=1024, hop_length=256)) ** 2
        v = 10.0 * np.log10((_mel @ S).mean(axis=1) + 1e-10)
        return v - v.max()

    picks = {}          # gm -> (attack_sample, iso, co_list)
    cands_by = {}       # gm -> the pass-1 candidate pool (THE DRY REPLICA stack)
    for gm, lane_notes in lanes.items():
        if gm not in LANE_NAME or gm not in lane_ref or lane_ref[gm] <= 0:
            continue
        ref = lane_body[gm]
        # STRONG TIER: candidates within 8dB of the lane reference (its true
        # voice, by MEASUREMENT) — a weak ghost or bleed detection must never
        # become the lane's sound. Bound to the strongest 40 for speed (Pi).
        scored = []
        for nt in lane_notes:
            t = float(nt["start"]) * spb
            pk = _hit_band_peak(xb[gm], sr, t)
            if pk >= ref * (10.0 ** (-8.0 / 20.0)):
                scored.append((pk, t, nt))
        if not scored:
            pks = sorted(((float(_hit_band_peak(xb[gm], sr, float(n["start"]) * spb)),
                           float(n["start"]) * spb, n) for n in lane_notes),
                         reverse=True)
            scored = list(pks[:8])
        scored.sort(key=lambda c: -c[0])
        scored = scored[:40]
        cands = []
        for pk, t, nt in scored:
            i0 = _find_attack(xb[gm], sr, t)
            nxt = min((o for o in onsets_all if o > t + 1e-4), default=t + 9.0)
            iso = min(max(0.05, nxt - t), LANE_MAX_S[gm])   # clean tail length
            co = any(abs(o - t) < 0.025
                     for og, os_ in lane_times.items() if og != gm
                     for o in os_)
            lm = _cand_logmel(i0)
            if lm is not None:
                cands.append((nt, t, i0, pk, iso, co, lm))
        if not cands:
            continue
        cands_by[gm] = cands
        clean = [c for c in cands if not c[5] and c[4] >= 0.05] or cands
        centroid = np.median(np.stack([c[6] for c in clean]), axis=0)
        cnorm = float(np.linalg.norm(centroid)) + 1e-12
        best, best_score = None, -1.0
        for nt, t, i0, pk, iso, co, lm in cands:
            centrality = float((lm * centroid).sum()
                               / (np.linalg.norm(lm) * cnorm + 1e-12))
            # strength(measured, relative to ref) * iso * co-penalty *
            # centrality^2 — an outlier-timbre hit needs 4x the level to win
            rel = min(1.0, pk / ref)
            score = rel * iso * (0.15 if co else 1.0) * max(0.05, centrality) ** 2
            if score > best_score:
                best, best_score = (nt, t, i0, iso), score
        if best is None:
            continue
        nt, t, i0, iso = best
        co_list = []
        for og, lns in lanes.items():
            if og == gm or og not in LANE_NAME or og not in lane_ref:
                continue
            for on in lns:
                dt = float(on["start"]) * spb - t
                if abs(dt) >= 0.025:
                    continue
                # only a co-hit STRONG in its own lane is real (>= ref-8dB);
                # a weak co-detection here is THIS hit's own band bleed and
                # subtracting it subtracts the exemplar from itself
                opk = _hit_band_peak(xb[og], sr, float(on["start"]) * spb)
                if opk >= lane_body[og] * (10.0 ** (-8.0 / 20.0)):
                    co_list.append((og, opk, max(0.0, dt)))
        picks[gm] = (i0, iso, co_list)

    # ---- pass 2: slice — THE DRY REPLICA first (median vote over the lane's
    # clean instances), single-exemplar decontamination as the thin-lane
    # fallback. Tail discipline on every replica: snappy by construction.
    raw = {}            # gm -> seg (natural level, pre-normalisation)
    alts = {}           # gm -> [(alt_pitch, seg, n_rows, centroid)] (wave 2)
    prim_cent = {}      # gm -> primary-cluster centroid (multi lanes only)
    dry_receipts = {}
    def _identity_gate(rep, xb_gm, cands, anchor, gm):
        """Post-vote contract: a voice not wearing its band rebuilds from
        band-conformed rows (the locked bleeder dies in the filter)."""
        if rep is None:
            return rep, ""
        band = _identity_verdict(rep[0], sr, gm)
        if band is None:
            return rep, ""
        rep2 = _median_replica(x, xb_gm, sr, cands, anchor,
                               LANE_MAX_S[gm], band=band)
        hi_s = "top" if band[1] is None else f"{band[1]:.0f}"
        if rep2 is not None:
            note = (f" ID-REBUILT {band[0]:.0f}-{hi_s}Hz"
                    if _identity_verdict(rep2[0], sr, gm) is None
                    else f" ID-REBUILT-partial {band[0]:.0f}-{hi_s}Hz")
            print(f"[kit] IDENTITY gm{gm}: locked bleed survived the vote ->"
                  f" rebuilt band-true ({band[0]:.0f}-{hi_s}Hz)", flush=True)
            return rep2, note
        print(f"[kit] IDENTITY gm{gm}: VIOLATION but band rebuild too thin"
              " — kept full-band voice", flush=True)
        return rep, " ID-VIOLATION-kept"

    order = sorted(picks, key=lambda g: len(picks[g][2]))   # fewest co-onsets first
    for gm in order:
        i0, iso, co_list = picks[gm]
        pool = cands_by.get(gm, [])
        clusters = _exemplar_clusters(pool) if (gm in xb and pool) else []
        multi = len(clusters) >= 2
        if multi:                               # per-cluster medians: the
            mem0, med0 = clusters[0]            # lane's distinct voices
            pool_u, anch_u = [pool[i] for i in mem0], pool[med0][2]
            rep = _median_replica(x, xb[gm], sr, pool_u, anch_u, LANE_MAX_S[gm])
            if rep is None:                     # thin after the vote: fall
                multi = False                   # back to the one-voice path
                pool_u, anch_u = pool, i0
                rep = _median_replica(x, xb[gm], sr, pool, i0, LANE_MAX_S[gm])
        else:
            pool_u, anch_u = pool, i0
            rep = _median_replica(x, xb[gm], sr, pool, i0,
                                  LANE_MAX_S[gm]) if gm in xb else None
        if rep is not None:
            rep, idnote = _identity_gate(rep, xb[gm], pool_u, anch_u, gm)
            seg, n_used, supp = rep
            seg = _tail_discipline(seg, sr, gm)
            dry_receipts[gm] = f"median-of-{n_used} wash-{supp}dB" + idnote
            if multi:
                prim_cent[gm] = np.mean(
                    np.stack([pool[i][6] for i in clusters[0][0]]), axis=0)
                built = []
                for j, (mem, med) in enumerate(clusters[1:]):
                    if j >= len(ALT_GM.get(gm, ())):
                        break
                    repj = _median_replica(x, xb[gm], sr,
                                           [pool[i] for i in mem],
                                           pool[med][2], LANE_MAX_S[gm])
                    if repj is None:
                        continue
                    repj, _idn = _identity_gate(repj, xb[gm],
                                                [pool[i] for i in mem],
                                                pool[med][2], gm)
                    if _identity_verdict(repj[0], sr, gm) is not None:
                        # an ALT still wearing another voice's band after the
                        # rebuild is a mis-cluster (a hat that fired in the
                        # snare band) — DROP it; assign_exemplars retargets
                        # its hits to an honest voice. Primaries stay (a lane
                        # must sound); alts are optional by construction.
                        print(f"[kit] IDENTITY gm{gm} alt{j}: still foreign "
                              "after rebuild -> dropped (mis-cluster)",
                              flush=True)
                        continue
                    sj, nj, _sup = repj
                    sj = _finish_seg(_tail_discipline(sj, sr, gm), sr)
                    cj = np.mean(np.stack([pool[i][6] for i in mem]), axis=0)
                    built.append((ALT_GM[gm][j], sj, nj, cj))
                if built:
                    alts[gm] = built
                    dry_receipts[gm] += f" +{len(built)}voice"
        else:
            i1 = min(len(x), i0 + int(max(0.05, iso) * sr))
            seg = x[i0:i1].copy()
            if len(seg) < int(0.03 * sr):
                continue
            # SOUND-AWARE CORRECTION: subtract what the OTHER lanes contributed
            # at this instant — their clean exemplars, scaled to the co-hit's
            # MEASURED band level — so a kick sliced under a hat comes out kick
            contams = []
            for og, opk, dt in co_list:
                if og in raw:
                    cseg = raw[og]
                    own = float(np.abs(_band_filter(cseg, sr, *LANE_BAND_HZ[og])).max())
                    if own > 1e-6:
                        contams.append((cseg * (opk / own), dt, og))
            if contams:
                seg = _spectral_subtract(seg, sr, contams)
            # IDENTITY CONTRACT on the thin path too: a single slice can't
            # re-vote, but it CAN be band-conformed — same filter, same law
            # (hat_open shipped 99% sub through this door, measured live).
            idn = ""
            band = _identity_verdict(seg, sr, gm)
            if band is not None:
                from scipy.signal import sosfilt
                seg = sosfilt(_band_sos(band, sr), seg)
                hi_s = "top" if band[1] is None else f"{band[1]:.0f}"
                idn = f" ID-CONFORMED {band[0]:.0f}-{hi_s}Hz"
                print(f"[kit] IDENTITY gm{gm}: single-exemplar wore the wrong"
                      f" band -> conformed ({band[0]:.0f}-{hi_s}Hz)", flush=True)
            seg = _tail_discipline(seg, sr, gm)
            dry_receipts[gm] = "single-exemplar" + idn
        seg = _finish_seg(seg, sr)
        # FALSE-DETECTION FLOOR: a lane whose exemplar peaks below -46dBFS is
        # a phantom — drop it, don't ship an inaudible zone.
        if float(np.abs(seg).max()) < 0.005:
            continue
        raw[gm] = seg
    if dry_receipts:
        print("[kit] DRY REPLICAS: "
              + "  ".join(f"{LANE_NAME.get(g, g)}={r}"
                          for g, r in sorted(dry_receipts.items())), flush=True)

    def _anchor(seg, gm):
        # THE ANCHOR LAW: gainDb makes vel=1.0 reproduce lane_ref in the
        # lane's own band through the ENGINE's dB velocity law. The slice's
        # absolute level is never trusted (a gutted slice baked -28.8dB).
        pk = float(np.abs(seg).max())
        if pk < 0.005:
            return None
        seg_n = seg * (0.9 / pk)
        bp = float(np.abs(_band_filter(seg_n, sr, *LANE_BAND_HZ[gm])).max())
        if bp < 1e-6:
            return None
        return seg_n, round(min(12.0, 20.0 * math.log10(lane_ref[gm] / bp)), 2)

    picked = {}
    for gm, seg in raw.items():
        a = _anchor(seg, gm)
        if a:
            picked[gm] = a
    if len(picked) < min_lanes:
        return None
    kdir = os.path.join(KITS, name)
    os.makedirs(kdir, exist_ok=True)
    samples, ex_meta = [], {}
    for gm in sorted(picked):
        fn = LANE_NAME[gm] + ".wav"
        seg_n, gain_db = picked[gm]
        _save_mono16(os.path.join(kdir, fn), seg_n, sr)
        lref = round(20.0 * math.log10(lane_ref[gm] + 1e-12), 2)
        samples.append({"file": fn, "keyNote": gm, "minNote": gm,
                        "maxNote": gm, "gainDb": gain_db, "laneRefDb": lref})
        shipped = []
        for ap, seg_a, n_rows, cent in alts.get(gm, []):
            a = _anchor(seg_a, gm)
            if a is None:
                continue
            sa, ga = a
            fn_a = f"{LANE_NAME[gm]}_alt{ap}.wav"
            _save_mono16(os.path.join(kdir, fn_a), sa, sr)
            samples.append({"file": fn_a, "keyNote": ap, "minNote": ap,
                            "maxNote": ap, "gainDb": ga, "laneRefDb": lref})
            shipped.append({"pitch": ap, "file": fn_a, "n": int(n_rows),
                            "centroid": [round(float(v), 3) for v in cent]})
        if shipped and gm in prim_cent:         # assignment needs BOTH sides
            ex_meta[str(gm)] = ([{"pitch": gm, "file": fn,
                                  "centroid": [round(float(v), 3)
                                               for v in prim_cent[gm]]}]
                                + shipped)
    kit_doc = {"name": name, "kind": "drum", "openEnded": True,
               "calib": "engine-db-v4-ceiling",
               "source": os.path.relpath(stem_wav, ROOT),
               "samples": samples}
    if ex_meta:
        kit_doc["exemplars"] = ex_meta
    json.dump(kit_doc, open(os.path.join(kdir, "kit.json"), "w"), indent=1)
    shipped = {s["file"] for s in samples}     # ORPHAN SWEEP: a rebuild that
    for f in os.listdir(kdir):                 # drops a voice must not leave
        if f.endswith(".wav") and f not in shipped:   # the old wav wearing
            os.remove(os.path.join(kdir, f))   # the dropped name (measured:
    return name                                # a stale mis-cluster alt)


def assign_exemplars(stem_wav, notes, kit_name, bpm=120.0):
    """THE EXEMPLAR ASSIGNMENT (wave 2): every hit plays the exemplar that
    sounds like ITS moment in the record, not the lane's one average voice.
    Retargets note pitches IN PLACE to the nearest exemplar centroid (cosine
    on the same 0.10s log-mel the clusters were built from — _logmel_seg
    dur_s=0.10 is _cand_logmel's exact math). Returns notes moved."""
    kp = os.path.join(KITS, kit_name, "kit.json")
    if not os.path.exists(kp):
        return 0
    ex = {int(g): v for g, v in
          (json.load(open(kp)).get("exemplars") or {}).items() if len(v) >= 2}
    if not ex:
        return 0
    sr, x = _load_mono(stem_wav)
    spb = 60.0 / bpm
    moved = 0
    for gm, exemplars in sorted(ex.items()):
        if gm not in LANE_BAND_HZ:
            continue
        fam = {int(e["pitch"]) for e in exemplars} | {gm}
        lane_notes = [nt for nt in notes if int(nt["pitch"]) in fam]
        if not lane_notes:
            continue
        xb = _band_filter(x, sr, *LANE_BAND_HZ[gm])
        C = np.stack([np.asarray(e["centroid"], dtype=np.float64)
                      for e in exemplars])
        Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
        for nt in lane_notes:
            i0 = _find_attack(xb, sr, float(nt["start"]) * spb)
            lm = _logmel_seg(x, sr, i0, dur_s=0.10)
            if lm is None:
                continue
            v = lm / (np.linalg.norm(lm) + 1e-12)
            tgt = int(exemplars[int(np.argmax(Cn @ v))]["pitch"])
            if int(nt["pitch"]) != tgt:
                nt["pitch"] = tgt
                moved += 1
    return moved


# ---------------------------------------------------------------- phrase kit
def _activity_spans(x, sr, gate_db=44.0, min_span_s=0.04):
    """The stem's OWN audible spans (10ms RMS grid, ref − gate_db) — identity
    coverage must not be bounded by what the f0 tracker could voice (a rap
    vocal's breaths/adlibs are 15% of the performance). Reference is the p99.7
    frame (one hot peak must not lift the gate over quiet verses)."""
    hop = int(sr / 100)
    n = len(x) // hop
    if n < 4:
        return []
    env = np.sqrt((x[:n * hop].reshape(-1, hop) ** 2).mean(axis=1))
    db = 20.0 * np.log10(env + 1e-9)
    ref = float(np.percentile(db, 99.7))
    act = db > max(ref - gate_db, -78.0)
    spans, i = [], 0
    while i < n:
        if act[i]:
            j = i
            while j + 1 < n and act[j + 1]:
                j += 1
            if (j - i + 1) * hop / sr >= min_span_s:
                spans.append([i * hop / sr, (j + 1) * hop / sr])
            i = j + 1
        else:
            i += 1
    return spans


def _split_long(x, sr, a, b, max_s):
    """Split [a,b] at its quietest internal 10ms frame until every piece fits
    max_s. NEVER truncates — v3 cut activity spans at a+max_phrase_s and
    dropped 12s of a 20s verse (vocal identity 92%→40%, the regression)."""
    if b - a <= max_s:
        return [[a, b]]
    i0, i1 = int(a * sr), int(b * sr)
    hop = int(sr / 100)
    seg = x[i0:i1]
    n = max(1, len(seg) // hop)
    env = np.sqrt((seg[:n * hop].reshape(-1, hop) ** 2).mean(axis=1))
    lo = max(1, int(n * 0.25))
    hi = max(lo + 1, int(n * 0.75))
    cut = a + (lo + int(np.argmin(env[lo:hi]))) * hop / sr
    if not (a + 0.05 < cut < b - 0.05):
        cut = (a + b) / 2.0
    return _split_long(x, sr, a, cut, max_s) + _split_long(x, sr, cut, b, max_s)


def build_phrase_kit(stem_wav, notes, name, bpm=120.0, key0=8, max_keys=64,
                     merge_gap_s=0.18, release_s=0.9, max_phrase_s=8.0,
                     min_phrases=3, spans_from="union"):
    """THE IDENTITY LANE for vocals (and any stem): slice the stem into
    PHRASES, map slices to sequential keys, and return (kit_name,
    phrase_notes). Playing the notes at vel 1.0 reproduces the record's own
    performance — micro-dynamics, words, cracks — because it IS the record,
    sliced. Phrases stay editable like MPC pads (move/repeat/drop a bar).
    Polyphonic stems work identically (slices don't care). Slices keep the
    stem's CHANNELS (stereo width is part of identity).

    spans_from="union" (default) = transcribed note spans ∪ the stem's own
    audible activity (breaths/unvoiced words survive; coverage isn't bounded
    by the f0 tracker). "notes"/"activity" restrict to one witness. Long
    spans SPLIT at their quietest frame (never truncated); phrases that share
    a split point get seam crossfades that SUM TO UNITY (24ms linear), so
    back-to-back playback reconstructs the span sample-faithfully; disjoint
    phrases keep their attack untouched (fade fully in pre-span air) and
    their reverb tail (release extends into silence). Returns (None, [])
    when the stem is too sparse.

    max_keys=64 is a HARD ENGINE CEILING, not a tuning knob: tracktion's
    SamplerPlugin::addSound rejects the 65th sound outright ("Can't load any
    more samples", maxNumSamples=64 in tracktion_SamplerPlugin.cpp) — a kit
    built past it silently drops the tail of its own slices in the real
    engine while this file's own render_notes (no such cap) keeps scoring it
    as if every slice loaded. A fast bassline (wad3: 120 raw phrases) hits
    this for real, not just in theory."""
    sr, xs = _load_wav(stem_wav)
    x = xs.mean(axis=1)
    spb = 60.0 / bpm
    spans = []
    if spans_from in ("notes", "union") and notes:
        spans += [[float(n["start"]) * spb,
                   (float(n["start"]) + float(n["len"])) * spb] for n in notes]
    if spans_from in ("activity", "union"):
        spans += [list(s) for s in _activity_spans(x, sr)]
    spans = sorted([max(0.0, a), min(len(x) / sr, b)] for a, b in spans if b > a)
    if not spans:
        return None, []
    merged = [list(spans[0])]
    for a, b in spans[1:]:
        if a <= merged[-1][1] + merge_gap_s:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    # reverb tails: extend each span into following silence until the envelope
    # dies (up to release_s), then re-merge anything the extension bridged
    hop = int(sr / 100)
    n_env = len(x) // hop
    env_db = 20.0 * np.log10(np.sqrt(
        (x[:n_env * hop].reshape(-1, hop) ** 2).mean(axis=1)) + 1e-9)
    for i, ab in enumerate(merged):
        lim = merged[i + 1][0] if i + 1 < len(merged) else len(x) / sr
        j = int(ab[1] * sr / hop)          # frame index at the span's end
        j_max = min(n_env - 1, int(min(ab[1] + release_s, lim) * sr / hop))
        floor = env_db[min(j, n_env - 1)] - 30.0
        while j < j_max and env_db[j] > max(floor, -72.0):
            j += 1
        ab[1] = min(max(ab[1], j * hop / sr), lim)
    re = [list(merged[0])]
    for a, b in merged[1:]:
        if a <= re[-1][1] + 1e-4:
            re[-1][1] = max(re[-1][1], b)
        else:
            re.append([a, b])
    # TOTAL COVERAGE: gaps between musical spans still hold the record's air
    # (reverb wash, room, separation residue). Identity means the render and
    # the stem match EVERYWHERE, so audible gaps (> -72dBFS peak) become
    # FILLER spans — same seam math, their own pads. True digital silence
    # stays uncovered (silent render == silent stem).
    covered = re
    fillers = []
    edges = [0.0] + [b for _, b in covered]
    nexts = [a for a, _ in covered] + [len(x) / sr]
    for ga, gb in zip(edges, nexts):
        if gb - ga < 0.05:
            continue
        gpk = float(np.abs(x[int(ga * sr):int(gb * sr)]).max()) if gb > ga else 0.0
        if gpk > 10.0 ** (-72.0 / 20.0):
            fillers.append([ga, gb])
    # long spans split at silence minima; count-cap by merging nearest pairs
    phrases = []
    for a, b in re:
        phrases += [p + [0] for p in _split_long(x, sr, a, b, max_phrase_s)]
    for a, b in fillers:
        phrases += [p + [1] for p in _split_long(x, sr, a, b, max_phrase_s)]
    phrases.sort(key=lambda p: p[0])
    while len(phrases) > max_keys:
        gaps = [phrases[i + 1][0] - phrases[i][1] for i in range(len(phrases) - 1)]
        i = int(np.argmin(gaps))
        phrases[i][1] = phrases[i + 1][1]
        phrases[i][2] = min(phrases[i][2], phrases[i + 1][2])
        del phrases[i + 1]
    if len([p for p in phrases if not p[2]]) < min_phrases:
        return None, []
    env = np.abs(x)
    kdir = os.path.join(KITS, name)
    os.makedirs(kdir, exist_ok=True)
    samples, pnotes = [], []
    xf = int(0.012 * sr)                    # seam half-width (24ms crossfade)
    k = 0
    prev_end = 0                            # last sample the previous slice used
    for pi, (a, b, fil) in enumerate(phrases):
        seam_l = pi > 0 and (a - phrases[pi - 1][1]) < 0.02
        seam_r = pi + 1 < len(phrases) and (phrases[pi + 1][0] - b) < 0.02
        if seam_l:
            i0 = max(0, int(a * sr) - xf)   # ramp 0→1 across the cut (sums to 1)
            fi = min(2 * xf, int(b * sr) - i0)
        else:
            # attack foot: fade fully INSIDE pre-span air, never on the attack —
            # but never back INTO audio the previous slice already covers
            # (double-covered 25ms played seams +6dB hot)
            i0 = max(0, int((a - 0.025) * sr), prev_end)
            seg_pre = env[i0:int(a * sr) + 1]
            if len(seg_pre) > 8:
                floor = 0.10 * float(seg_pre.max() + 1e-12)
                j = len(seg_pre) - 1
                while j > 0 and seg_pre[j] > floor:
                    j -= 1
                i0 = i0 + j
            fi = max(16, min(int(0.004 * sr), int(a * sr) - i0 + 16))
        if seam_r:
            i1 = min(len(x), int(b * sr) + xf)
            fo = min(2 * xf, i1 - i0)
        else:
            i1 = min(len(x), int(b * sr))
            fo = min(max(32, int(0.020 * sr)), i1 - i0)
        prev_end = i1 - (2 * xf if seam_r else 0)
        seg = xs[i0:i1].copy()
        if len(seg) < int(0.03 * sr):
            continue
        pk = float(np.abs(seg).max())
        # dust gate: -50dBFS for musical phrases, -74 for fillers (their whole
        # point is the quiet air between phrases)
        if pk < (2e-4 if fil else 0.003):
            continue
        seg[:fi] *= np.linspace(0.0, 1.0, fi)[:, None]
        seg[-fo:] *= np.linspace(1.0, 0.0, fo)[:, None]
        fn = f"p{k:03d}.wav"
        # normalization boost capped at 42dB: the engine clamps sound gainDb
        # to +-48 (SamplerPlugin jlimit) — an uncapped -73dB filler would pin
        # at -48 and play 25dB hot
        scale = min(0.9 / pk, 10.0 ** (42.0 / 20.0))
        _save_wav16(os.path.join(kdir, fn), seg * scale, sr)
        key = key0 + k
        # vel 1.0 -> the slice's NATURAL level, exactly (engine dB law)
        smp = {"file": fn, "keyNote": key, "minNote": key, "maxNote": key,
               "gainDb": round(-20.0 * math.log10(scale), 2)}
        if fil:
            smp["filler"] = True
        samples.append(smp)
        pnotes.append({"start": round(i0 / sr / spb, 5),
                       "len": round(max(0.05, (i1 - i0 + int(0.03 * sr)) / sr / spb), 5),
                       "pitch": key, "vel": 1.0})
        k += 1
    if len(samples) < min_phrases:
        return None, []
    json.dump({"name": name, "kind": "phrase", "openEnded": False,
               "calib": "engine-db-v4",
               "source": os.path.relpath(stem_wav, ROOT), "samples": samples},
              open(os.path.join(kdir, "kit.json"), "w"), indent=1)
    return name, pnotes


# ---------------------------------------------------------------- pitched kit
def _pitch_band(f0, sr):
    """A pitch's home register: fundamental through ~5th harmonic, generous."""
    lo = max(25.0, f0 * 0.70)
    hi = min(sr * 0.45, max(f0 * 5.5, f0 + 600.0))
    return lo, max(hi, lo * 1.5)


def _logmel_seg(x, sr, i0, dur_s=0.20):
    """Log-mel timbre vector of a slice head (the medoid law's yardstick —
    same math as the drum builder's _cand_logmel, longer window because a
    pitched note's identity lives in its sustain, not just its attack)."""
    import librosa as _lb
    n = int(dur_s * sr)
    seg = x[i0:i0 + n]
    if len(seg) < int(0.05 * sr):
        return None
    if len(seg) < n:
        seg = np.pad(seg, (0, n - len(seg)))
    mel = _lb.filters.mel(sr=sr, n_fft=1024, n_mels=40, fmin=30,
                          fmax=min(16000.0, sr * 0.5))
    S = np.abs(_lb.stft(seg.astype(np.float32), n_fft=1024, hop_length=256)) ** 2
    v = 10.0 * np.log10((mel @ S).mean(axis=1) + 1e-10)
    return v - v.max()


def _harmonic_subtract_pitched(seg, sr, f0, contam_f0s):
    """SOUND-AWARE DECONTAMINATION for pitched exemplars: a slice cut from a
    polyphonic moment carries every co-sounding note — replaying it on each
    chord tone re-stacks the whole chord (the pitched kit's chord-smear).
    Suppress the CONTAMINANTS' harmonic combs (transcription tells us their
    pitches) while every bin my own comb claims stays untouched — shared
    harmonics resolve to the host. Conservative binary Wiener floor (0.15),
    per channel, so a wrong guess dulls, never mangles."""
    import librosa
    n_fft, hop = 2048, 512
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    mine = np.zeros(len(freqs), bool)
    for h in range(1, 17):
        fh = f0 * h
        if fh > sr * 0.48:
            break
        mine |= np.abs(freqs - fh) < max(20.0, fh * 0.035)
    kill = np.zeros(len(freqs), bool)
    for cf in contam_f0s:
        for h in range(1, 17):
            fh = cf * h
            if fh > sr * 0.48:
                break
            kill |= np.abs(freqs - fh) < max(18.0, fh * 0.03)
    kill &= ~mine
    if not kill.any():
        return seg
    out = np.empty_like(seg)
    for c in range(seg.shape[1]):
        S = librosa.stft(seg[:, c].astype(np.float32), n_fft=n_fft, hop_length=hop)
        S[kill, :] *= 0.15
        out[:, c] = librosa.istft(S, hop_length=hop, length=len(seg))
    return out


def build_pitched_kit(stem_wav, notes, name, bpm=120.0, min_notes=6, role="melodic"):
    """THE IDENTITY LANE for melodic/vocal stems: REAL transcribed pitches in
    the roll, the record's OWN timbre behind every key. One exemplar slice
    per distinct pitch, zones range-filled so every in-between pitch (and any
    edit) resamples from its nearest exemplar. (The phrase-chop lane was
    REJECTED 2026-07-08: pad-index staircases are not notes — identity
    listening belongs to the audio lane; THIS lane is the actual music,
    remade in sounds.)

    The drum builder's laws, adapted to pitch (v2):
    - every level is MEASURED in the note's own harmonic band (fundamental
      through ~5th harmonic), so a hat wash never sets a bass velocity;
    - the exemplar is the cleanest ISOLATED take — co-onset collisions pay
      0.15, each co-sounding neighbour divides the score, sustain length and
      measured strength earn it back, and among the clean the TIMBRE MEDOID
      wins (centrality**2, the opus law);
    - exemplars still caught inside polyphony get their contaminants'
      harmonic combs suppressed (_harmonic_subtract_pitched);
    - THE ANCHOR: zone gainDb makes vel=1.0 reproduce the pitch's p90
      band-measured level through the engine's dB velocity law;
    - CLOSED LOOP (the final correction): self-render through the engine's
      measured laws (render_notes), fix the global lag, then refit every
      note's velocity against the stem's own band level and keep the pass
      only if the envelope agrees more.

    Returns (kit_name, calibrated_notes) — calibrated_notes keep the REAL
    pitches/starts (chord priors downstream still apply; range-fill keeps
    snapped pitches playable). max 64 zones: SamplerPlugin::addSound hard
    ceiling (tracktion_SamplerPlugin.cpp)."""
    from scipy.signal import butter, sosfilt
    sr, xs = _load_wav(stem_wav)
    x = xs.mean(axis=1)
    spb = 60.0 / bpm
    if len(notes) < min_notes:
        return None, notes
    starts = np.array([float(n["start"]) * spb for n in notes])
    lens = np.array([max(0.02, float(n["len"]) * spb) for n in notes])
    ends = starts + lens
    pitches = np.array([int(n["pitch"]) for n in notes])
    f0s = 440.0 * 2.0 ** ((pitches - 69) / 12.0)
    order_t = np.argsort(starts)
    sorted_starts = starts[order_t]

    ny = sr / 2.0
    sos_cache = {}

    def band_win(i, t0, t1):
        """The note's harmonic-band view of [t0,t1] (+60ms shoulders).
        Returns (abs_start_sample, banded_window)."""
        p = int(pitches[i])
        if p not in sos_cache:
            lo, hi = _pitch_band(f0s[i], sr)
            sos_cache[p] = butter(4, [lo / ny, min(hi, ny * 0.99) / ny],
                                  "band", output="sos")
        a = max(0, int((t0 - 0.06) * sr))
        b = min(len(x), int((t1 + 0.06) * sr))
        if b - a < 64:
            return a, np.zeros(0)
        return a, sosfilt(sos_cache[p], x[a:b])

    def note_band_peak(i, sig=None, off=0):
        """Measured peak of note i in its own band (stem by default; pass a
        render to measure the OTHER side with the same ruler)."""
        t = starts[i]
        w1 = t + min(lens[i], 0.35)
        if sig is None:
            a, w = band_win(i, t, w1)
        else:
            p = int(pitches[i])
            if p not in sos_cache:
                lo, hi = _pitch_band(f0s[i], sr)
                sos_cache[p] = butter(4, [lo / ny, min(hi, ny * 0.99) / ny],
                                      "band", output="sos")
            a = max(0, int((t - 0.06) * sr))
            b = min(len(sig), int((w1 + 0.06) * sr))
            if b - a < 64:
                return 0.0
            w = sosfilt(sos_cache[p], sig[a:b])
        c0 = max(0, int((t - 0.005) * sr) - a)
        c1 = min(len(w), int((w1 + 0.010) * sr) - a)
        return float(np.abs(w[c0:c1]).max()) if c1 > c0 else 0.0

    peaks = np.array([note_band_peak(i) for i in range(len(notes))])
    if not (peaks > 0).any():
        return None, notes

    work = [dict(n) for n in notes]
    # ---- THE SUSTAIN LAW (loss anatomy 2026-07-08: the record still rings at
    # 29-55% amplitude after note-off on EVERY stem measured — transcribers
    # report the voiced core, the instrument rings longer). Extend each note
    # until its own band envelope decays 26dB below its head, bounded by the
    # next onset (any pitch when the stem plays one line at a time, same
    # pitch when it plays chords, +0.22s ring-under allowance). The roll gets
    # the TRUE lengths; the gate stops amputating sustains.
    ov = 0
    for i in range(len(work)):
        o = (starts < ends[i] - 0.05) & (ends > starts[i] + 0.05)
        o[i] = False
        ov += int(o.any())
    is_mono = (ov / max(1, len(work))) < 0.20
    hopE = int(sr / 100)
    for i in range(len(work)):
        t, ln = starts[i], lens[i]
        if is_mono:
            j = np.searchsorted(sorted_starts, t + 0.01, side="right")
            # ring-under allowance: NOT for bass — neighboring 808 pitches
            # share harmonic bands, so "its own decay" reads the NEXT note's
            # energy as its own ring and every note dragged 0.22s of wrong
            # pitch under the next hit (footprint bass 69->55, proopen 65->61
            # before this gate; env_corr rose while spectral fell = the
            # signature of level-right-timbre-wrong doubling).
            ring = -0.01 if role == "bass" else 0.22
            limit = (sorted_starts[j] + ring) if j < len(sorted_starts) else t + ln + 3.0
        else:
            same = starts[(pitches == pitches[i]) & (starts > t + 0.01)]
            limit = (float(same.min()) - 0.01) if len(same) else t + ln + 3.0
        limit = min(limit, t + ln + 3.0, len(x) / sr)
        if limit <= t + ln + 0.03:
            continue
        a, w = band_win(i, t, limit)
        if not len(w):
            continue
        m = len(w) // hopE
        if m < 3:
            continue
        fe = np.sqrt((w[:m * hopE].reshape(-1, hopE) ** 2).mean(axis=1))
        h0 = max(0, int((t - a / sr) * 100))
        h1 = min(m, h0 + max(2, int(min(ln, 0.25) * 100)))
        head = float(fe[h0:h1].max()) if h1 > h0 else 0.0
        if head <= 0:
            continue
        floor = head * 10.0 ** (-26.0 / 20.0)
        j = min(m - 1, h0 + int(ln * 100))
        jl = min(m - 1, h0 + int((limit - t) * 100))
        while j < jl and fe[j] >= floor:
            j += 1
        new_len = max(ln, (j - h0) / 100.0)
        if new_len > ln + 0.02:
            lens[i] = new_len
            ends[i] = t + new_len
            work[i]["len"] = round(new_len / spb, 5)

    # ---- THE SALVAGE PASS (vocal anatomy: 19-32% of the ALIVE frames carry
    # no note — adlibs, weak lines the consensus dropped). Every alive span
    # the notes don't cover gets a fast yin look; STABLE voiced runs become
    # REAL notes (their true pitch, start, length — honest music, not fill).
    # Unvoiced spans (rap consonants, breath) stay the chops lane's job.
    # VOCAL-ONLY: bass/other carry <12% alive-uncovered (measured) so salvage
    # buys little there, and yin at fmin=55 octave-errors on 808 slides —
    # it REGRESSED footprint/proopen bass 14/5 pts before this gate.
    if role == "vocal":
      try:
        import librosa as _lb
        spans = _activity_spans(x, sr)
        iv = sorted(zip(starts, ends))
        gaps = []
        for a0, b0 in spans:
            cur = a0
            for s0, e0 in iv:
                if e0 <= cur or s0 >= b0:
                    continue
                if s0 > cur + 0.12:
                    gaps.append((cur, min(s0, b0)))
                cur = max(cur, e0)
                if cur >= b0:
                    break
            if b0 > cur + 0.12:
                gaps.append((cur, b0))
        added = []
        cap = max(8, int(0.35 * len(work)))
        for a0, b0 in gaps:
            if len(added) >= cap:
                break
            seg = x[int(a0 * sr):int(b0 * sr)]
            if len(seg) < int(0.12 * sr):
                continue
            f0 = _lb.yin(seg.astype(np.float32), fmin=55.0, fmax=1400.0,
                         sr=sr, frame_length=2048, hop_length=256)
            tf = 256.0 / sr
            run = []
            for k, f in enumerate(f0):
                ok = 55.0 < f < 1400.0
                if ok and run and abs(math.log2(f / run[-1][1])) > 0.06:
                    ok = False                  # >~0.7 semitone jump = new run
                if ok:
                    run.append((k, f))
                    continue
                if len(run) * tf >= 0.09:
                    t0 = a0 + run[0][0] * tf
                    t1 = a0 + (run[-1][0] + 1) * tf
                    p = int(round(69 + 12 * math.log2(np.median([r[1] for r in run]) / 440.0)))
                    if 24 <= p <= 108:
                        added.append({"start": round(t0 / spb, 5),
                                      "len": round(max(0.06, (t1 - t0)) / spb, 5),
                                      "pitch": p, "vel": 0.7, "salvaged": True})
                run = [(k, f)] if ok else []
            if len(run) * tf >= 0.09 and len(added) < cap:
                t0 = a0 + run[0][0] * tf
                t1 = a0 + (run[-1][0] + 1) * tf
                p = int(round(69 + 12 * math.log2(np.median([r[1] for r in run]) / 440.0)))
                if 24 <= p <= 108:
                    added.append({"start": round(t0 / spb, 5),
                                  "len": round(max(0.06, (t1 - t0)) / spb, 5),
                                  "pitch": p, "vel": 0.7, "salvaged": True})
        if added:
            # yin on a wet vocal drops the odd note an OCTAVE (subharmonic) or
            # doubles it — a lone D2 under an A2 floor is D3 halved. FOLD each
            # salvage pitch back toward the sung range [p5,p95] instead of
            # dropping it: the timing/energy is real, only the octave is wrong.
            lo = float(np.percentile(pitches, 5))
            hi = float(np.percentile(pitches, 95))
            pmed = float(np.median(pitches))
            fixed = []
            for n in added:
                p = n["pitch"]
                while p < lo - 6 and p + 12 <= 108:
                    p += 12
                while p > hi + 6 and p - 12 >= 24:
                    p -= 12
                if abs(p - pmed) <= 26:        # sanity-bound the rare wild pick
                    n["pitch"] = p
                    fixed.append(n)
            work += fixed
      except Exception:
        pass                                   # salvage is a bonus, never a gate

    # rebuild the measured view over the (extended + salvaged) union
    starts = np.array([float(n["start"]) * spb for n in work])
    lens = np.array([max(0.02, float(n["len"]) * spb) for n in work])
    ends = starts + lens
    pitches = np.array([int(n["pitch"]) for n in work])
    f0s = 440.0 * 2.0 ** ((pitches - 69) / 12.0)
    order_t = np.argsort(starts)
    sorted_starts = starts[order_t]
    peaks = np.array([note_band_peak(i) for i in range(len(work))])

    # (GLIDE-STITCH tombstone, measured 2026-07-09: collapsing 1-2-semitone
    # staircase runs into per-gesture zones keyed at the start pitch LOST
    # 1.7-5.6 pts on every chain-heavy track, gated AND open — instance
    # timing inside a duration bucket never lines up, and gesture keys steal
    # the pitch's curated plain exemplar. The staircase through repitched
    # one-shots says glides better; PERFECT glides live on the phrase lane.
    # Don't re-walk it without a new ruler.)

    # THE DENSITY GATE (measured 2026-07-09): open-ended ring-stacking won
    # +3.8..+12.6 on discrete-hit bass lines (glide mass 0-37% of sounding
    # time) and LOST -1.3 on a 94%-glide line — there each "note" is a STEP
    # of one continuous gesture, masked at once by the next step, so rings
    # stack into mud. Mostly-glide lines play GATED; discrete lines ring
    # OPEN (one-shot, length-blind — standard sampler semantics).
    open_ring = role == "bass"
    if open_ring and len(work) >= 6:
        ot = list(np.argsort(starts))
        glide_t, cur = 0.0, [ot[0]]
        for k in ot[1:]:
            step = abs(int(pitches[k]) - int(pitches[cur[-1]]))
            if (starts[k] - ends[cur[-1]]) < 0.06 and 1 <= step <= 2:
                cur.append(k)
            else:
                if len(cur) >= 3:
                    glide_t += float(ends[cur[-1]] - starts[cur[0]])
                cur = [k]
        if len(cur) >= 3:
            glide_t += float(ends[cur[-1]] - starts[cur[0]])
        open_ring = glide_t < 0.5 * max(float(lens.sum()), 1e-6)

    by_pitch = {}
    for i, p in enumerate(pitches):
        by_pitch.setdefault(int(p), []).append(i)
    p90s = {p: float(np.percentile([peaks[i] for i in idx if peaks[i] > 0], 90))
            for p, idx in by_pitch.items()
            if any(peaks[i] > 0 for i in idx)}
    # THE CEILING ANCHOR (v6): vel=1.0 = the pitch's LOUDEST measured hit
    # (capped p90+9dB vs glitch measurements). Anchoring p90 clamped every
    # accent at the p90 level — a built-in limiter ("HEAVILY LIMITED",
    # Chezy 2026-07-08). p90 stays the body yardstick for candidate tiers.
    pref = {p: float(min(max(peaks[i] for i in by_pitch[p] if peaks[i] > 0),
                         p90s[p] * 10.0 ** (9.0 / 20.0)))
            for p in p90s}
    # ENGINE CEILING: strongest 64 pitches win, ranked by CONTRIBUTION
    # (level x how often the music actually plays them), not one loud outlier.
    ranked = sorted(pref, key=lambda p: -(pref[p] * math.sqrt(len(by_pitch[p]))))
    keep = sorted(ranked[:64])

    samples, zone_pitches = [], []
    kdir = os.path.join(KITS, name)
    os.makedirs(kdir, exist_ok=True)
    for f in os.listdir(kdir):                 # stale slices from any prior
        if f.endswith(".wav"):                 # builder die with the rebuild
            os.unlink(os.path.join(kdir, f))
    for pitch in keep:
        idx = by_pitch[pitch]
        p_ref = pref[pitch]
        p_body = p90s[pitch]
        strong = [i for i in idx if peaks[i] >= p_body * 10.0 ** (-10.0 / 20.0)]
        if not strong:
            continue
        strong.sort(key=lambda i: -peaks[i])
        strong = strong[:24]
        cands = []
        for i in strong:
            t = starts[i]
            j = np.searchsorted(sorted_starts, t + 0.01, side="right")
            gap = (sorted_starts[j] - t) if j < len(sorted_starts) else 9.0
            others = (pitches != pitch)
            co = bool(np.any(others & (np.abs(starts - t) < 0.025)))
            n_ov = int(np.sum(others & (starts < t + min(lens[i], 0.8))
                              & (ends > t + 0.02)))
            a, w = band_win(i, t, t + min(lens[i], 0.35))
            if not len(w):
                continue
            foot = _find_attack(w, sr, t - a / sr)
            i0 = a + foot
            lm = _logmel_seg(x, sr, i0)
            if lm is None:
                continue
            iso = min(max(0.05, min(lens[i] + 0.35, gap)), 3.0)
            cands.append((i, i0, gap, co, n_ov, iso, lm))
        if not cands:
            continue
        clean = [c for c in cands if not c[3] and c[4] == 0] or cands
        centroid = np.median(np.stack([c[6] for c in clean]), axis=0)
        cnorm = float(np.linalg.norm(centroid)) + 1e-12
        # centrality weight is ROLE-AWARE: on 808 bass the 0.2s mel head is
        # dominated by KICK BLEED at the onset, so the medoid gravitates to
        # the most-typically-bled hit, not the cleanest 808 (footprint bass
        # 69->59 under centrality^2). Isolation + strength carry bass.
        cw = 0.0 if role == "bass" else 2.0
        best, best_score = None, -1.0
        for i, i0, gap, co, n_ov, iso, lm in cands:
            centrality = float((lm * centroid).sum()
                               / (np.linalg.norm(lm) * cnorm + 1e-12))
            rel = min(1.0, peaks[i] / p_body)
            score = (rel * iso * (0.15 if co else 1.0) / (1.0 + n_ov)
                     * max(0.05, centrality) ** cw)
            if score > best_score:
                best, best_score = (i, i0, gap, co, n_ov), score
        if best is None:
            continue
        i, i0, gap, co, n_ov = best
        if role == "bass":
            # THE RING LAW (loss anatomy 2026-07-09): the dominant bass loss
            # is UNCOVERED frames — the record rings ~0.5 amplitude past
            # every note-off while a gated render emits digital silence. Cut
            # the exemplar with its natural ring (bounded by its own clean
            # air) and mark the kit OPEN-ENDED like the phrase lane: every
            # hit decays exactly as the record's own hit decayed. The ring is
            # CAPPED at ~1.5x the line's own median inter-onset gap — a mono
            # 808 rings until its next retrigger masks it; uncapped rings
            # STACK on dense lines (proopen 64->62 under P1-uncapped while
            # its note_sdr rose to -0.19dB: the loss moved between notes).
            # never SHORTER than the baseline law (dense lines have gap<lens:
            # a pure-gap cut starved them into 0.25s stubs, proopen 64->62).
            base = lens[i] + min(0.35, max(0.05, gap - 0.02))
            cut = max(0.25, base, min(4.0, gap - 0.02))
        else:
            tail = min(0.35, max(0.05, gap - 0.02))
            cut = max(0.25, lens[i] + tail)
        i1 = min(len(x), i0 + int(min(cut, 6.0) * sr))
        seg = xs[i0:i1].copy()
        if len(seg) < int(0.05 * sr) or float(np.abs(seg).max()) < 0.004:
            continue
        if co or n_ov:
            t = starts[i]
            ov = np.where((pitches != pitch) & (starts < t + min(lens[i], 1.0))
                          & (ends > t))[0]
            ov = sorted(ov, key=lambda k: -peaks[k])[:8]
            cfs = sorted({round(float(f0s[k]), 1) for k in ov
                          if abs(int(pitches[k]) - pitch) >= 2})
            if cfs:
                try:
                    seg = _harmonic_subtract_pitched(seg, sr, float(f0s[i]), cfs)
                except Exception:
                    pass
        fi = min(len(seg), max(16, int(0.003 * sr)))
        fo = min(len(seg), max(32, int(0.020 * sr)))
        seg[:fi] *= np.linspace(0.0, 1.0, fi)[:, None]
        seg[-fo:] *= np.linspace(1.0, 0.0, fo)[:, None]
        spk = float(np.abs(seg).max())
        if spk < 1e-6:
            continue
        seg_n = seg * (0.9 / spk)
        # THE ANCHOR LAW: vel=1.0 reproduces this pitch's CEILING band level;
        # the slice's absolute level is never trusted (decontamination moves it).
        p = int(pitches[i])
        bp = float(np.abs(sosfilt(sos_cache[p], seg_n.mean(axis=1))).max())
        if bp < 1e-6:
            continue
        gain_db = min(20.0 * math.log10(p_ref / bp), 12.0)
        fn = f"n{pitch:03d}.wav"
        _save_wav16(os.path.join(kdir, fn), seg_n, sr)
        samples.append({"file": fn, "keyNote": pitch, "minNote": pitch,
                        "maxNote": pitch, "gainDb": round(gain_db, 2)})
        zone_pitches.append(pitch)
    if len(samples) < 2:
        return None, notes
    # range-fill: every pitch between exemplars resamples from the nearest
    zone_pitches.sort()
    for i, s in enumerate(samples):
        p = zone_pitches[i]
        lo = 0 if i == 0 else (zone_pitches[i - 1] + p + 1) // 2
        hi = 127 if i == len(samples) - 1 else (p + zone_pitches[i + 1]) // 2
        s["minNote"], s["maxNote"] = int(lo), int(hi)
    json.dump({"name": name, "kind": "pitched", "openEnded": bool(open_ring),
               "calib": "engine-db-v6-ceiling",
               "source": os.path.relpath(stem_wav, ROOT), "samples": samples},
              open(os.path.join(kdir, "kit.json"), "w"), indent=1)

    # (GATED-RING tombstone, measured 2026-07-09: re-creating the ring in a
    # GATED kit by extending note lens through the slice's own decay lost
    # 1.8-8 pts vs open-ended — the engine chokes same-pitch voices on
    # note-on (tracktion_SamplerPlugin.cpp:311), so a gated kit is
    # mono-per-pitch BY CONSTRUCTION and can never stack the cross-note
    # ring mass the record carries. One-shot = length-blind is standard
    # sampler semantics; the bass lane ships open-ended.)
    # first-pass velocities: each note plays at its band-measured level
    zone_pref = {p: pref[p] for p in zone_pitches}
    zp = np.array(zone_pitches)
    out_notes = []
    for k, n in enumerate(work):
        zone = int(zp[np.argmin(np.abs(zp - int(n["pitch"])))])
        m = dict(n)
        m["vel"] = round(vel_for_level(peaks[k], zone_pref[zone]), 3)
        out_notes.append(m)

    # ---- CLOSED LOOP: render through the engine's measured laws and fix
    # what measurement can see — global lag, then per-note level (v2).
    def _env(sig, hop):
        m = len(sig) // hop
        return np.sqrt((sig[:m * hop].reshape(-1, hop) ** 2).mean(axis=1))

    try:
        hop = int(sr / 100)
        env_ref = _env(x, hop)
        ren = render_notes(name, out_notes, bpm, sr, len(x))
        env_ren = _env(ren, hop)
        m = min(len(env_ref), len(env_ren))
        e0 = float(np.corrcoef(env_ref[:m], env_ren[:m])[0, 1])
        # global lag: the transcriber grid-snaps starts; the whole take can
        # sit a few ms off the audio. One number, cross-correlated, capped.
        W = 6                                   # +-60ms search
        best_s, best_c = 0, e0
        for s in range(-W, W + 1):
            if s == 0:
                continue
            a_r = env_ref[max(0, s):m + min(0, s)]
            a_n = env_ren[max(0, -s):m - max(0, s)]
            k = min(len(a_r), len(a_n))
            if k < 100:
                continue
            c = float(np.corrcoef(a_r[:k], a_n[:k])[0, 1])
            if c > best_c + 1e-4:
                best_s, best_c = s, c
        if best_s:
            dt_beats = (best_s * hop / sr) / spb
            for n in out_notes:
                n["start"] = round(max(0.0, float(n["start"]) + dt_beats), 5)
            starts = starts + best_s * hop / sr
            ren = render_notes(name, out_notes, bpm, sr, len(x))
        # per-note velocity refit against the stem's own band level
        refit = [dict(n) for n in out_notes]
        for k in range(len(refit)):
            rl = note_band_peak(k, sig=ren)
            sl = peaks[k]
            if rl <= 1e-7 or sl <= 1e-7:
                continue
            delta = float(np.clip(math.log10(sl / rl), -0.4, 0.4)) * 0.8
            refit[k]["vel"] = round(min(1.0, max(0.05,
                                                 float(refit[k]["vel"]) + delta)), 3)
        ren2 = render_notes(name, refit, bpm, sr, len(x))
        env2 = _env(ren2, hop)
        m2 = min(len(env_ref), len(env2))
        e2 = float(np.corrcoef(env_ref[:m2], env2[:m2])[0, 1])
        if e2 > max(e0, best_c):
            out_notes = refit
    except Exception:
        pass                                   # the loop is a refinement, not a gate
    return name, out_notes


def render_notes(kit_name, notes, bpm, sr, n_samples):
    """Lay the kit's slices at the note times through the ENGINE's measured
    laws — the battery's engine-free identity render. Mirrors the sampler:
    velocity is dB (factor 10^(vel-1)); a note inside a zone's [minNote,
    maxNote] plays that zone's sample REPITCHED by 2^((pitch-keyNote)/12)
    (v3 looked up exact keyNote only, so every range-filled bass note
    rendered SILENT and the identity measure read -24dB si_sdr on a fine
    kit — measure through the engine's eyes or don't measure). Samples past
    #64 are dropped, mirroring SamplerPlugin::addSound's hard ceiling
    (tracktion_SamplerPlugin.cpp) — a kit built past it must score AS THE
    ENGINE WOULD PLAY IT, not as if every slice loaded."""
    kdir = os.path.join(KITS, kit_name)
    kit = json.load(open(os.path.join(kdir, "kit.json")))
    zones = []                               # (minN, maxN, keyN, x, lin_gain)
    for s in kit["samples"][:64]:
        zsr, z = _load_mono(os.path.join(kdir, s["file"]))
        if zsr != sr:
            idx = np.minimum((np.arange(int(len(z) * sr / zsr)) * zsr / sr)
                             .astype(np.int64), len(z) - 1)
            z = z[idx]
        zones.append((int(s.get("minNote", s["keyNote"])),
                      int(s.get("maxNote", s["keyNote"])), int(s["keyNote"]),
                      z, 10.0 ** (float(s.get("gainDb", 0.0)) / 20.0)))
    open_ended = bool(kit.get("openEnded", False))
    out = np.zeros(n_samples)
    spb = 60.0 / bpm
    for nt in notes:
        p = int(nt["pitch"])
        zn = next((z for z in zones if z[0] <= p <= z[1]), None)
        if zn is None:                       # engine: out-of-zone = silent
            continue
        _, _, key, z, g = zn
        if p != key:                         # sampler repitch = rate change
            ratio = 2.0 ** ((p - key) / 12.0)
            n_out = int(len(z) / ratio)
            if n_out < 8:
                continue
            pos = np.arange(n_out) * ratio
            i = np.minimum(pos.astype(np.int64), len(z) - 2)
            fr = pos - i
            z = z[i] * (1.0 - fr) + z[i + 1] * fr
        i0 = int(float(nt["start"]) * spb * sr)
        if i0 >= n_samples:
            continue
        m = min(len(z), n_samples - i0)
        if not open_ended:                   # note-off gates the sample
            m = min(m, int((float(nt.get("len", 1.0)) * spb + 0.005) * sr))
        zz = z[:m]
        if not open_ended and m < len(z) and m > 96:
            zz = zz.copy()
            zz[-96:] *= np.linspace(1.0, 0.0, 96)
        out[i0:i0 + m] += zz * g * engine_vel_gain(nt.get("vel", 0.8))
    pk = float(np.abs(out).max())
    if pk > 1.0:
        out /= pk
    return out


if __name__ == "__main__":
    # CLI: source_kit.py drums.wav notes.json name [bpm]
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    nts = json.load(open(sys.argv[2]))
    nm = build_source_kit(sys.argv[1], nts, sys.argv[3],
                          bpm=float(sys.argv[4]) if len(sys.argv) > 4 else 120.0)
    print(f"[source_kit] -> {nm}" if nm else "[source_kit] too few lanes")
