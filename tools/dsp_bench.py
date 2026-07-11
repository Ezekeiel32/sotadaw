#!/usr/bin/env python3
"""A1 — THE LAB BENCH (docs/THE_PHYSICS.md §6; gaps G2/G6/G9; laws E2/E5).

The oscilloscope + network analyzer + THD meter the DSP author never had. Every
measurement rides the engine's own transport (audioClip probe song -> m1 render),
so what is measured is what ships — not a model of it.

Method receipts:
  FR/GD/THD   exponential sine sweep (Farina AES-108) deconvolved by REGULARIZED
              SPECTRAL DIVISION. With division-deconvolution the k-th harmonic IR's
              spectrum evaluated at OUTPUT frequency k*f0 equals a_k(f0)/A exactly
              (sweep dwell 1/f and the divisor's 1/f cancel) — so
                  THD_k(f0) = |G_k(k*f0)| / |G_1(f0)|
              with no axis-convention folklore; the selftest cross-checks it against
              steady-state sine ground truth (S6).
  fixture     every transfer measure is CHAIN render vs DRY render of the same probe
              (network-analyzer calibration): pan law, clip gain, engine offsets cancel.
  aliasing    high-f0 sine probes where ALL k>=2 products fold (12.5k/15k @ 44.1k):
              alias_dbc = worst folded-product level rel. the fundamental (E5 budget).
  noise       silence probe -> steady-state RMS (24-bit file floor ~= -144 dBFS).
  tails (G7)  impulse-at-last-beat through a big reverb; measures what the render
              guillotines (P15) -> ledger verdict.
  warp (G9)   bin-snapped sine clip warped (sourceBpm != song bpm) -> artifact index.

usage:
  dsp_bench.py --selftest [--keep]          the battery (exit 0 = green)
  dsp_bench.py chain '<fx-json>' [--probe all|ess|silence|alias|sine:F] [--drive DB]
  dsp_bench.py voice <name> [--note 60] [--vel 1.0]
  dsp_bench.py cert <name> [--force]        one cert -> instruments/certs/<name>.cert.json
  dsp_bench.py cert --all [--force]         retro-cert sweep (every voice + fx)
  dsp_bench.py tails | warp                 standalone probes
Prints BENCH_JSON <payload> on every path.
"""
import hashlib
import json
import math
import os
import re
import shutil
import socket
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt
from scipy.signal.windows import tukey

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
CERTS = os.path.join(ROOT, "instruments", "certs")
SCRATCH = os.environ.get("DSP_BENCH_SCRATCH") or os.path.join(SONGS, "_bench_probes")

SR = 44100
BPM = 120.0                      # beat = 0.5 s
ESS_F1, ESS_F2, ESS_T = 20.0, 20000.0, 6.0
ESS_LEAD, ESS_TAIL = 2.0, 1.5    # lead >= L*ln(6) so harmonic IRs never collide
NFFT_SINE = 65536

_DRY_CACHE = {}                  # probe path -> rendered dry wav (per process)


# ---------------------------------------------------------------- plumbing
def _db(v, floor=-200.0):
    return round(20.0 * math.log10(v), 2) if v > 10 ** (floor / 20.0) else floor


def read_wav(path):
    x, sr = sf.read(path, always_2d=True, dtype="float64")
    return x, sr


def write_probe(name, mono, sr=SR):
    os.makedirs(SCRATCH, exist_ok=True)
    path = os.path.join(SCRATCH, name)
    if not os.path.exists(path):
        sf.write(path, np.stack([mono, mono], axis=1), sr, subtype="PCM_24")
    return path


def render(song, tag, timeout=600):
    """m1 render; returns (wav_path, render_sha256|None) or (None, log_tail)."""
    sj = os.path.join(SONGS, f"_bench_{tag}.json")
    wv = os.path.join(SONGS, f"_bench_{tag}.wav")
    with open(sj, "w") as f:
        json.dump(song, f, indent=1)
    r = subprocess.run([M1, "render", sj, wv], capture_output=True, text=True,
                       timeout=timeout)
    out = r.stdout + r.stderr
    if "ok=1" not in out:
        return None, out[-400:]
    m = re.search(r"render_sha256=([0-9a-f]{64})", out)
    return wv, (m.group(1) if m else None)


def probe_song(clip_path, fx=None, length_bars=6, gain_db=0.0, master=None,
               source_bpm=0.0, clip_beats=None):
    dur = sf.info(clip_path).duration
    beats = clip_beats if clip_beats is not None else math.ceil(dur / 0.5)
    tr = {"name": "probe", "source": {"kind": "audio"}, "gainDb": gain_db,
          "audioClips": [{"file": clip_path, "startBeat": 0,
                          "lengthBeats": beats, "offsetSec": 0}]}
    if source_bpm > 0:
        tr["audioClips"][0]["sourceBpm"] = source_bpm
    if fx:
        tr["fx"] = fx
    return {"version": 2, "bpm": BPM, "lengthBars": length_bars, "masterGainDb": 0,
            "master": master or [], "tracks": [tr]}


def cleanup(keep=False):
    if keep:
        return
    for f in os.listdir(SONGS):
        if f.startswith("_bench_") and (f.endswith(".json") or f.endswith(".wav")):
            try:
                os.remove(os.path.join(SONGS, f))
            except OSError:
                pass
    shutil.rmtree(SCRATCH, ignore_errors=True)


# ---------------------------------------------------------------- probe signals
def make_ess(drive_db=-12.0):
    amp = 10 ** (drive_db / 20.0)
    L = ESS_T / math.log(ESS_F2 / ESS_F1)
    n = int(ESS_T * SR)
    t = np.arange(n) / SR
    sweep = amp * np.sin(2 * math.pi * ESS_F1 * L * (np.exp(t / L) - 1.0))
    nf_in, nf_out = int(0.020 * SR), int(0.100 * SR)
    sweep[:nf_in] *= 0.5 - 0.5 * np.cos(np.pi * np.arange(nf_in) / nf_in)
    sweep[-nf_out:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(nf_out) / nf_out)
    full = np.concatenate([np.zeros(int(ESS_LEAD * SR)), sweep,
                           np.zeros(int(ESS_TAIL * SR))])
    path = write_probe(f"ess_{drive_db:+.1f}.wav", full)
    return path, {"L": L, "x": full, "drive_db": drive_db}


def make_silence(seconds=4.0):
    return write_probe("silence.wav", np.zeros(int(seconds * SR)))


def snap_bin(f0):
    df = SR / NFFT_SINE
    return round(f0 / df) * df


def make_sine(f0, drive_db=-12.0, seconds=3.0):
    f0s = snap_bin(f0)
    amp = 10 ** (drive_db / 20.0)
    n = int(seconds * SR)
    tone = amp * np.sin(2 * math.pi * f0s * np.arange(n) / SR)
    nf = int(0.010 * SR)
    tone[:nf] *= np.linspace(0, 1, nf)
    tone[-nf:] *= np.linspace(1, 0, nf)
    full = np.concatenate([np.zeros(int(0.5 * SR)), tone, np.zeros(int(0.3 * SR))])
    path = write_probe(f"sine_{f0s:.2f}_{drive_db:+.1f}.wav", full)
    return path, f0s


# ---------------------------------------------------------------- kernels
def deconvolve(y_mono, x_full):
    """Regularized spectral division, BAND-LIMITED to the sweep's band.

    Out-of-band content (aliases, harmonics minted above f2) would be divided by
    the tiny regularized |X| there and amplified ~+80 dB — loud enough to leak
    through any window's sidelobes into every THD bin (measured before this
    guard: a flat fake +19 dBc floor). Zeroing H outside [0.7*f1, 1.02*f2]
    removes the amplified junk without touching the in-band division law."""
    n = 1 << int(math.ceil(math.log2(len(y_mono) + len(x_full))))
    Y = np.fft.rfft(y_mono, n)
    X = np.fft.rfft(x_full, n)
    eps = np.max(np.abs(X)) * 1e-4
    H = Y * np.conj(X) / (np.abs(X) ** 2 + eps ** 2)
    f = np.fft.rfftfreq(n, 1 / SR)
    H[(f < ESS_F1 * 0.7) | (f > ESS_F2 * 1.02)] = 0.0
    return np.fft.irfft(H, n)


def _peak(h):
    return int(np.argmax(np.abs(h)))


def _seg(h, center, half, nfft):
    idx = (np.arange(center - half, center + half)) % len(h)
    seg = h[idx] * tukey(2 * half, 0.25)
    return np.abs(np.fft.rfft(seg, nfft)), np.fft.rfft(seg, nfft)


def ess_analyze(chain_wav, dry_wav, meta, harmonics=6):
    """FR (dB rel dry), GD, latency, THD-by-order via the division-deconvolution law."""
    yc = read_wav(chain_wav)[0][:, 0]
    yd = read_wav(dry_wav)[0][:, 0]
    hc, hd = deconvolve(yc, meta["x"]), deconvolve(yd, meta["x"])
    pc, pd = _peak(hc), _peak(hd)

    half = int(0.200 * SR)
    nfft = 1 << int(math.ceil(math.log2(2 * half)))
    fr_f = np.fft.rfftfreq(nfft, 1 / SR)
    # PEAK-CENTERED windows, same geometry as the harmonic segs: an impulse offset
    # into the Tukey taper reads ~-48 dB low (the bug S6 caught on first light —
    # FR ratios cancelled it, absolute THD didn't). Center = unity gain, always.
    Gc_mag, Gc = _seg(hc, pc, half, nfft)
    Gd_mag, Gd = _seg(hd, pd, half, nfft)
    ratio = (Gc + 1e-30) / (Gd + 1e-30)
    fr_db = 20 * np.log10(np.abs(ratio) + 1e-30)

    band = (fr_f >= 100) & (fr_f <= 15000)
    phi = np.unwrap(np.angle(ratio[band]))
    gd_res = -np.gradient(phi, 2 * math.pi * fr_f[band])
    lat_samples = pc - pd
    gd_ms = float(np.median(gd_res[(fr_f[band] >= 200) & (fr_f[band] <= 8000)]) * 1000
                  + lat_samples / SR * 1000)

    # harmonic IRs: at pc - L*ln(k)*SR (division law -> evaluate G_k at k*f0)
    L = meta["L"]
    thd = {}
    grid = [125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0]
    Gk_interp = {}
    for k in range(2, harmonics + 1):
        pos = int(round(pc - L * math.log(k) * SR))
        gap = L * (math.log(k + 1) - math.log(k)) * SR
        hk = min(int(0.030 * SR), int(0.4 * gap))
        if hk < 64:
            continue
        mag, _ = _seg(hc, pos, hk, nfft)
        Gk_interp[k] = (np.fft.rfftfreq(nfft, 1 / SR), mag)
    G1f = fr_f
    G1 = Gc_mag
    for f0 in grid:
        orders = {}
        a1 = float(np.interp(f0, G1f, G1))
        if a1 <= 0:
            continue
        for k, (fk, mk) in Gk_interp.items():
            if k * f0 > ESS_F2 * 0.95:
                continue
            ak = float(np.interp(k * f0, fk, mk))
            orders[str(k)] = round(20 * math.log10(ak / a1 + 1e-12), 1)
        if orders:
            tot = math.sqrt(sum(10 ** (v / 10.0) for v in orders.values()))
            thd[str(int(f0))] = {"orders_dbc": orders,
                                 "thd_pct": round(tot * 100, 3)}

    # sampled FR curve for the cert (1/6 oct)
    grid_f = np.geomspace(30, 18000, 60)
    fr_curve = [[round(float(f), 1), round(float(np.interp(f, fr_f, fr_db)), 2)]
                for f in grid_f]
    mid = (fr_f >= 100) & (fr_f <= 10000)
    return {"latency_samples": int(lat_samples),
            "gd_ms": round(gd_ms, 3),
            "fr_mean_db_100_10k": round(float(np.mean(fr_db[mid])), 3),
            "fr_std_db_100_10k": round(float(np.std(fr_db[mid])), 3),
            "fr_curve_db": fr_curve,
            "thd_by_f0": thd,
            "_fr_f": fr_f, "_fr_db": fr_db}


def sine_analyze(wav, f0, max_k=10):
    """Steady-state sine: THD (true harmonics in-band) + alias products (folded)."""
    x = read_wav(wav)[0][:, 0]
    s0 = int(1.2 * SR)
    seg = x[s0:s0 + NFFT_SINE]
    if len(seg) < NFFT_SINE:
        seg = np.pad(seg, (0, NFFT_SINE - len(seg)))
    X = np.abs(np.fft.rfft(seg * np.hanning(NFFT_SINE)))
    df = SR / NFFT_SINE
    E = X ** 2

    def band_amp(f, half_bins=3):
        b = int(round(f / df))
        lo, hi = max(0, b - half_bins), min(len(E), b + half_bins + 1)
        return math.sqrt(float(E[lo:hi].sum()))

    def fold(nu):
        nu = nu % SR
        return SR - nu if nu > SR / 2 else nu

    a1 = band_amp(f0)
    harm, alias = {}, {}
    for k in range(2, max_k + 1):
        nu = k * f0
        if nu < SR / 2 * 0.98:
            harm[str(k)] = round(20 * math.log10(band_amp(nu) / (a1 + 1e-30) + 1e-12), 1)
        else:
            fv = fold(nu)
            if abs(fv - f0) > 4 * df and fv > 20:
                alias[f"{k}({fv:.0f}Hz)"] = round(
                    20 * math.log10(band_amp(fv) / (a1 + 1e-30) + 1e-12), 1)
    thd_pct = round(100 * math.sqrt(sum(10 ** (v / 10.0) for v in harm.values())), 3) \
        if harm else 0.0
    worst_alias = max(alias.values()) if alias else None
    return {"f0": round(f0, 2), "fundamental_dbfs": _db(a1 / (NFFT_SINE / 4)),
            "harmonics_dbc": harm, "thd_pct": thd_pct,
            "alias_products_dbc": alias, "alias_dbc_worst": worst_alias}


def silence_analyze(wav):
    x = read_wav(wav)[0][:, 0]
    seg = x[int(0.5 * SR):]
    rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
    bands = {}
    for name, lo, hi in (("low", 20, 500), ("mid", 500, 4000), ("high", 4000, 20000)):
        sos = butter(4, [lo, min(hi, SR / 2 - 100)], btype="bandpass", fs=SR,
                     output="sos")
        b = sosfilt(sos, seg)
        bands[name] = _db(float(np.sqrt(np.mean(b ** 2))))
    return {"noise_dbfs": _db(rms), "noise_bands_dbfs": bands}


def voice_analyze(wav, on_s=0.5, off_s=2.5):
    x2 = read_wav(wav)[0]
    x = x2.mean(axis=1)
    ax = np.abs(x)
    peak = float(ax.max()) if len(x) else 0.0
    clipped = int((np.abs(x2) >= 0.999).sum())
    hop = int(0.010 * SR)
    env = np.array([ax[i:i + hop].max() if i + hop <= len(ax) else 0.0
                    for i in range(0, len(ax) - hop, hop)])
    env_t = np.arange(len(env)) * hop / SR
    w = (env_t >= on_s - 0.02) & (env_t <= on_s + 1.0)
    attack_ms = None
    if w.any() and env[w].max() > 0:
        ew, tw = env[w], env_t[w]
        pk = ew.max()
        i90 = int(np.argmax(ew >= 0.9 * pk))
        i10 = 0
        for j in range(i90, -1, -1):
            if ew[j] <= 0.1 * pk:
                i10 = j
                break
        attack_ms = round((tw[i90] - tw[i10]) * 1000, 1)
    sus0, sus1 = int((on_s + 0.3) * SR), int(off_s * SR)
    sus = x[sus0:sus1]
    centroid = None
    harmonics = []
    if len(sus) > 4096:
        Xs = np.abs(np.fft.rfft(sus * np.hanning(len(sus))))
        fs = np.fft.rfftfreq(len(sus), 1 / SR)
        centroid = round(float((fs * Xs).sum() / (Xs.sum() + 1e-12)))
        m = fs > 25
        idx = np.argsort(Xs[m])[::-1][:8]
        top = Xs[m].max() + 1e-30
        harmonics = [[round(float(fs[m][i]), 1),
                      round(20 * math.log10(Xs[m][i] / top + 1e-12), 1)]
                     for i in sorted(idx, key=lambda i: fs[m][i])]
    # decay: from global env peak to -60 dB
    ip = int(np.argmax(env))
    pk = env[ip] + 1e-30
    tail_s = None
    for j in range(ip, len(env)):
        if env[j] < pk * 1e-3:
            tail_s = round(env_t[j] - env_t[ip], 2)
            break
    noise = _db(float(np.sqrt(np.mean(x[-int(0.3 * SR):] ** 2))))
    sus_rms = _db(float(np.sqrt(np.mean(sus ** 2)))) if len(sus) else None
    return {"peak_dbfs": _db(peak), "clipped_samples": clipped,
            "attack_ms": attack_ms, "sustain_rms_db": sus_rms,
            "sustain_centroid_hz": centroid, "harmonics_top": harmonics,
            "decay_to_m60_s": tail_s if tail_s is not None else ">end",
            "noise_tail_dbfs": noise}


# ---------------------------------------------------------------- probes
def _dry_render(probe_path, tag_hint, length_bars=6):
    key = (probe_path, length_bars)
    if key not in _DRY_CACHE:
        w, _ = render(probe_song(probe_path, fx=None, length_bars=length_bars),
                      f"dry_{tag_hint}")
        if w is None:
            raise RuntimeError(f"dry render failed: {_}")
        _DRY_CACHE[key] = w
    return _DRY_CACHE[key]


def bench_chain(fx_list, probes=("ess", "silence", "alias"), drive_db=-12.0,
                tag="chain"):
    out = {"chain": fx_list, "drive_db": drive_db, "machine": socket.gethostname()}
    if "ess" in probes or "sine" in probes:
        pass
    if "ess" in probes:
        p, meta = make_ess(drive_db)
        dry = _dry_render(p, f"ess{drive_db:+.0f}")
        w, sha = render(probe_song(p, fx=fx_list), f"{tag}_ess")
        if w is None:
            out["error"] = f"ess render failed: {sha}"
            return out
        r = ess_analyze(w, dry, meta)
        r.pop("_fr_f", None), r.pop("_fr_db", None)
        out["ess"] = r
    if "silence" in probes:
        p = make_silence()
        w, _ = render(probe_song(p, fx=fx_list, length_bars=3), f"{tag}_sil")
        if w is not None:
            out["silence"] = silence_analyze(w)
    if "alias" in probes:
        worst = musical = None
        out["alias_probes"] = {}
        # 6k/8k = the highest fundamentals real instruments reach; 12.5k/15k = the
        # near-Nyquist TORTURE tones (a saturated 15k sine isn't musical content).
        # alias_dbc_musical (<=8k) is the E5 budget gate; alias_dbc_worst keeps the
        # honest torture number too (single-rate physics can't fully tame near-Nyquist).
        for f0 in (6000.0, 8000.0, 12500.0, 15000.0):
            p, f0s = make_sine(f0, drive_db)
            w, _ = render(probe_song(p, fx=fx_list, length_bars=3), f"{tag}_al{int(f0)}")
            if w is None:
                continue
            r = sine_analyze(w, f0s)
            out["alias_probes"][str(int(f0))] = r
            a = r["alias_dbc_worst"]
            if a is not None:
                worst = a if worst is None else max(worst, a)
                if f0 <= 8000.0:
                    musical = a if musical is None else max(musical, a)
        out["alias_dbc_worst"] = worst
        out["alias_dbc_musical"] = musical
    for pr in probes:
        if isinstance(pr, str) and pr.startswith("sine:"):
            f0 = float(pr.split(":")[1])
            p, f0s = make_sine(f0, drive_db)
            w, _ = render(probe_song(p, fx=fx_list, length_bars=3),
                          f"{tag}_s{int(f0)}")
            if w is not None:
                out.setdefault("sine", {})[str(int(f0))] = sine_analyze(w, f0s)
    return out


def bench_voice(name, note=60, vel=1.0, tag=None):
    song = {"version": 2, "bpm": BPM, "lengthBars": 3, "masterGainDb": 0, "master": [],
            "tracks": [{"name": "probe", "source": {"kind": "faust", "id": name},
                        "gainDb": 0.0,
                        "notes": [{"start": 1.0, "len": 4.0, "pitch": note,
                                   "vel": vel}]}]}
    w, sha = render(song, tag or f"voice_{name}")
    if w is None:
        return {"voice": name, "error": f"render failed: {sha}"}
    r = voice_analyze(w)
    r.update({"voice": name, "note": note, "vel": vel,
              "machine": socket.gethostname()})
    return r


def tails_probe():
    """G7/P15: does a render truncate fx tails past the edit end? Measure, don't vibe."""
    fx = [{"id": "fx_reverb", "params": {"mix": 1.0, "size": 0.97}}]
    base = {"version": 2, "bpm": BPM, "masterGainDb": 0, "master": [],
            "tracks": [{"name": "probe", "source": {"kind": "faust", "id": "hat"},
                        "gainDb": 0.0, "fx": fx,
                        "notes": [{"start": 7.5, "len": 0.25, "pitch": 70,
                                   "vel": 0.9}]}]}
    short = dict(base, lengthBars=2)          # note at the LAST half-beat of bar 2
    long = dict(base, lengthBars=4)           # same note, room for the tail
    ws, _ = render(short, "tails_short")
    wl, _ = render(long, "tails_long")
    if ws is None or wl is None:
        return {"error": "tails renders failed"}
    xs = read_wav(ws)[0][:, 0]
    xl = read_wav(wl)[0][:, 0]
    edit_len_s = 2 * 4 * 0.5                      # nominal 2-bar edit
    n_edit = int(edit_len_s * SR)
    pad_s = round(len(xs) / SR - edit_len_s, 3)   # what the ENGINE adds on its own
    e_nominal_end = _db(float(np.sqrt(np.mean(
        xs[n_edit - int(0.05 * SR):min(n_edit + int(0.05 * SR), len(xs))] ** 2))))
    e_file_end = _db(float(np.sqrt(np.mean(xs[-int(0.1 * SR):] ** 2))))
    cut = xl[len(xs):] if len(xl) > len(xs) else np.zeros(1)
    e_cut = _db(float(np.sqrt(np.mean(cut ** 2))))
    t_dead = None
    hop = int(0.05 * SR)
    for i in range(n_edit, len(xl) - hop, hop):
        if _db(float(np.sqrt(np.mean(xl[i:i + hop] ** 2)))) < -90:
            t_dead = round((i - n_edit) / SR, 2)
            break
    truncates = e_cut > -90.0
    return {"nominal_edit_s": edit_len_s,
            "engine_pad_s": pad_s,                # P15 ANSWER: measured tail allowance
            "energy_at_nominal_end_dbfs": e_nominal_end,
            "energy_at_file_end_dbfs": e_file_end,
            "energy_truly_cut_dbfs": e_cut,       # long render past short's FILE end
            "tail_dead_after_nominal_s": t_dead,
            "verdict": (f"ENGINE PADS +{pad_s}s past the edit; "
                        + ("but STILL cuts audible tail (E9: needs tail:cut note)"
                           if truncates else
                           "residue beyond the pad is inaudible (< -90 dBFS)"))}


def warp_probe():
    """G9: time-stretch artifact index — warped vs unwarped bin-snapped sine."""
    p, f0s = make_sine(997.0, -12.0, seconds=4.0)

    def artifact(wav):
        x = read_wav(wav)[0][:, 0]
        s0 = int(1.0 * SR)
        seg = x[s0:s0 + NFFT_SINE]
        if len(seg) < NFFT_SINE:
            seg = np.pad(seg, (0, NFFT_SINE - len(seg)))
        X = np.abs(np.fft.rfft(seg * np.hanning(NFFT_SINE))) ** 2
        f = np.fft.rfftfreq(NFFT_SINE, 1 / SR)
        fund = X[(f > f0s - 30) & (f < f0s + 30)].sum()
        rest = X[(f > 25) & ((f < f0s - 30) | (f > f0s + 30))].sum()
        return round(10 * math.log10((rest + 1e-30) / (fund + 1e-30)), 1)

    wd, _ = render(probe_song(p, length_bars=6), "warp_dry")
    ww, _ = render(probe_song(p, length_bars=6, source_bpm=90.0, clip_beats=16),
                   "warp_warp")
    if wd is None or ww is None:
        return {"error": "warp renders failed"}
    return {"f0": round(f0s, 2), "stretch_ratio": round(BPM / 90.0, 3),
            "artifact_db_unwarped": artifact(wd),
            "artifact_db_warped": artifact(ww),
            "note": "artifact = non-fundamental energy rel fundamental; delta = warp cost"}


# ---------------------------------------------------------------- certs
def _dsp_sha(name):
    p = os.path.join(ROOT, "instruments", f"{name}.dsp")
    if not os.path.exists(p):
        return None
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def _m1_md5():
    return hashlib.md5(open(M1, "rb").read()).hexdigest()[:16]


FX_PREFIXES = ("fx_", "master_limiter")
ADAPTIVE_FX = {"fx_retune"}       # realtime pitch-follower: latency-only cert


def is_fx(name):
    return name.startswith("fx_") or name in ("master_limiter",)


def cert_one(name, force=False):
    os.makedirs(CERTS, exist_ok=True)
    out_path = os.path.join(CERTS, f"{name}.cert.json")
    sha = _dsp_sha(name)
    if not force and os.path.exists(out_path):
        try:
            old = json.load(open(out_path))
            if old.get("dsp_sha") == sha:
                return {"name": name, "cached": True, "path": out_path}
        except Exception:
            pass
    import datetime
    base = {"name": name, "kind": "fx" if is_fx(name) else "voice",
            "dsp_sha": sha, "m1_md5": _m1_md5(),
            "machine": socket.gethostname(),
            "date": datetime.date.today().isoformat(),
            "law": "E2 (docs/THE_PHYSICS.md)"}
    if is_fx(name):
        if name in ADAPTIVE_FX:
            r = bench_chain([{"id": name}], probes=("ess",), tag=f"c_{name}")
            base.update({"adaptive": True,
                         "latency_samples": r.get("ess", {}).get("latency_samples"),
                         "gd_ms": r.get("ess", {}).get("gd_ms")})
        else:
            r = bench_chain([{"id": name}], probes=("ess", "silence", "alias"),
                            tag=f"c_{name}")
            if "error" in r:
                base["error"] = r["error"]
            else:
                ess = r["ess"]
                base.update({
                    "latency_samples": ess["latency_samples"],
                    "gd_ms": ess["gd_ms"],
                    "fr_mean_db_100_10k": ess["fr_mean_db_100_10k"],
                    "fr_std_db_100_10k": ess["fr_std_db_100_10k"],
                    "fr_curve_db": ess["fr_curve_db"],
                    "thd_by_f0": ess["thd_by_f0"],
                    "noise_dbfs": r.get("silence", {}).get("noise_dbfs"),
                    "alias_dbc_worst": r.get("alias_dbc_worst"),
                    "alias_dbc_musical": r.get("alias_dbc_musical"),
                    "verdicts": {
                        "flat_pass": abs(ess["fr_mean_db_100_10k"]) < 0.5
                                     and ess["fr_std_db_100_10k"] < 0.5,
                        # E5 budget on the MUSICAL band (<=8k); torture tones stay honest
                        "alias_budget_pass": (r.get("alias_dbc_musical") is None
                                              or r["alias_dbc_musical"] <= -60.0),
                        "noise_ok": (r.get("silence", {}).get("noise_dbfs", 0)
                                     <= -120.0),
                    }})
    else:
        r = bench_voice(name, tag=f"c_{name}")
        if "error" in r:
            base["error"] = r["error"]
        else:
            base.update({k: r[k] for k in
                         ("peak_dbfs", "clipped_samples", "attack_ms",
                          "sustain_rms_db", "sustain_centroid_hz", "harmonics_top",
                          "decay_to_m60_s", "noise_tail_dbfs")})
            base["verdicts"] = {
                "headroom_pass_vel1": r["clipped_samples"] == 0,   # voice-headroom law
                # peak_dbfs == 0.0 (FULL SCALE) is falsy — a bare `or` here once read
                # slammed voices as "silent". Explicit None check only.
                "audible": (-200.0 if r["peak_dbfs"] is None
                            else r["peak_dbfs"]) > -60.0,
            }
    with open(out_path, "w") as f:
        json.dump(base, f, indent=1)
    return base


def cert_all(force=False):
    names = sorted(os.path.splitext(f)[0]
                   for f in os.listdir(os.path.join(ROOT, "instruments"))
                   if f.endswith(".dsp"))
    results, failed = [], []
    for i, n in enumerate(names):
        try:
            r = cert_one(n, force=force)
        except Exception as e:                                    # keep sweeping
            r = {"name": n, "error": f"{type(e).__name__}: {e}"}
        results.append(r)
        ok = "error" not in r
        if not ok:
            failed.append(n)
        print(f"  [{i + 1:2d}/{len(names)}] {'cert' if ok else 'FAIL'} {n}"
              + ("" if ok else f" — {r['error'][:90]}"), flush=True)
    print(f"[certs] {len(results) - len(failed)}/{len(results)} green -> {CERTS}")
    return {"total": len(results), "failed": failed}


# ---------------------------------------------------------------- selftest
def selftest(keep=False):
    checks, fails = [], []

    def check(nm, ok, detail=""):
        checks.append({"name": nm, "ok": bool(ok), "detail": detail})
        if not ok:
            fails.append(nm)
        print(("  ok " if ok else "FAIL ") + f"{nm}  {detail}", flush=True)

    try:
        # S0 transport + fixture sanity
        p, meta = make_ess(-12.0)
        dry = _dry_render(p, "ess-12")
        yd = read_wav(dry)[0][:, 0]
        hd = deconvolve(yd, meta["x"])
        pd = _peak(hd)
        prom = np.abs(hd[pd]) / (np.median(np.abs(hd)) + 1e-30)
        check("S0 transport: dry ESS deconvolves to a clean impulse",
              prom > 1000, f"prominence {prom:.0f}x @ {pd}smp")

        # S1 fx_trim -6: flat to the dB
        r = bench_chain([{"id": "fx_trim", "params": {"level": -6.0}}],
                        probes=("ess",), tag="s1")
        m, s = r["ess"]["fr_mean_db_100_10k"], r["ess"]["fr_std_db_100_10k"]
        check("S1 fx_trim -6 => FR flat -6.00 +/- 0.05 dB",
              abs(m + 6.0) <= 0.05 and s <= 0.05, f"mean {m} std {s}")

        # S2 fx_filter cutoff 1k: -3 dB inside a third-octave
        r = bench_chain([{"id": "fx_filter",
                          "params": {"cutoff": 1000, "res": 0.7}}],
                        probes=("ess",), tag="s2")
        curve = r["ess"]["fr_curve_db"]
        ref = np.mean([d for f, d in curve if 40 <= f <= 200])
        f3 = None
        for (f, d) in curve:
            if f > 200 and d <= ref - 3.0:
                f3 = f
                break
        check("S2 fx_filter cutoff=1k => -3 dB point within third-octave",
              f3 is not None and 794 <= f3 <= 1260, f"f-3 = {f3} Hz (ref {ref:.2f} dB)")

        # S3 fx_saturate: THD monotone in drive (sine ground truth @ 1 kHz)
        thds = []
        for drv in (3.0, 9.0, 15.0):
            ps, f0s = make_sine(1000.0, -12.0)
            w, _ = render(probe_song(ps, fx=[{"id": "fx_saturate",
                                              "params": {"drive": drv, "mix": 1.0}}],
                                     length_bars=3), f"s3_{int(drv)}")
            thds.append(sine_analyze(w, f0s)["thd_pct"])
        check("S3 fx_saturate THD monotone in drive",
              thds[0] < thds[1] < thds[2], f"{thds} %")

        # S4 fx_truepeak: latency ~= its 128-sample lookahead
        r4 = bench_chain([{"id": "fx_truepeak", "params": {"ceiling": -1.0}}],
                         probes=("ess",), tag="s4")
        lat = r4["ess"]["latency_samples"]
        check("S4 fx_truepeak latency ~= 128-sample lookahead",
              112 <= lat <= 160, f"{lat} samples, gd {r4['ess']['gd_ms']} ms")

        # S5 silence through fx_trim: the floor is the file format's, nothing more
        r5 = bench_chain([{"id": "fx_trim", "params": {"level": 0.0}}],
                         probes=("silence",), tag="s5")
        nz = r5["silence"]["noise_dbfs"]
        check("S5 silence noise floor <= -140 dBFS", nz <= -140.0, f"{nz} dBFS")

        # S6 the convention proof: ESS THD == sine THD (fx_saturate drive 9 @ 1k)
        r6 = bench_chain([{"id": "fx_saturate",
                           "params": {"drive": 9.0, "mix": 1.0}}],
                         probes=("ess",), drive_db=-12.0, tag="s6")
        e = r6["ess"]["thd_by_f0"].get("1000", {}).get("thd_pct")
        s_pct = thds[1]
        ratio_db = abs(20 * math.log10((e + 1e-9) / (s_pct + 1e-9)))
        check("S6 ESS-vs-sine THD agree <= 3 dB (division-law convention proven)",
              e is not None and ratio_db <= 3.0,
              f"ess {e}% vs sine {s_pct}% ({ratio_db:.2f} dB apart)")

        # S7 aliasing: rig floor clean on a linear chain; fx_saturate (now ADAA)
        # anti-aliased — IN the E5 budget at its default drive, measured at hard drive.
        r7a = bench_chain([{"id": "fx_trim", "params": {"level": 0.0}}],
                          probes=("alias",), tag="s7a")
        r7def = bench_chain([{"id": "fx_saturate", "params": {"mix": 1.0}}],
                            probes=("alias",), tag="s7def")     # default drive = cert level
        r7b = bench_chain([{"id": "fx_saturate",
                            "params": {"drive": 9.0, "mix": 1.0}}],
                          probes=("alias",), tag="s7b")         # hard drive = torture
        fl = r7a["alias_dbc_worst"]
        mus_def, al = r7def.get("alias_dbc_musical"), r7b["alias_dbc_worst"]
        check("S7 alias rig floor <= -90 dBc on linear chain", fl is not None
              and fl <= -90.0, f"trim {fl} dBc")
        check("S7b fx_saturate (ADAA) IN E5 budget at default drive (musical<=8k <= -60)",
              mus_def is not None and mus_def <= -60.0,
              f"default-drive musical {mus_def} dBc (was ~-49 pre-ADAA); "
              f"hard-drive/near-Nyquist worst {al} dBc = single-rate tanh limit")

        # S8 tails (G7): measure + ledger
        t = tails_probe()
        check("S8 tails probe ran (P15 ledgered)", "verdict" in t,
              f"{t.get('verdict', t)} | cut energy {t.get('energy_cut_by_truncation_dbfs')} dBFS"
              f" | tail past edit {t.get('tail_survives_past_edit_s')}s")

        # S9 warp (G9): the number exists
        wq = warp_probe()
        check("S9 warp artifact index measured (G9 -> number)",
              "artifact_db_warped" in wq,
              f"unwarped {wq.get('artifact_db_unwarped')} dB -> warped "
              f"{wq.get('artifact_db_warped')} dB @ ratio {wq.get('stretch_ratio')}")

        result = {"pass": not fails, "failing": fails, "checks": checks,
                  "tails": t, "warp": wq,
                  "saturate_alias_dbc": al, "machine": socket.gethostname()}
    finally:
        cleanup(keep)
    print("BENCH_JSON " + json.dumps({k: v for k, v in result.items()
                                      if not k.startswith("_")}))
    print(f"\n== DSP BENCH: {len(checks) - len(fails)} pass / {len(fails)} fail ==")
    return 0 if not fails else 1


# ---------------------------------------------------------------- cli
def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    keep = "--keep" in a
    if a[0] == "--selftest":
        return selftest(keep)

    def opt(flag, default=None, cast=float):
        return cast(a[a.index(flag) + 1]) if flag in a else default

    try:
        if a[0] == "chain":
            fx = json.loads(a[1])
            if isinstance(fx, dict):
                fx = [fx]
            drive = opt("--drive", -12.0)
            pr = a[a.index("--probe") + 1] if "--probe" in a else "all"
            probes = ("ess", "silence", "alias") if pr == "all" else (pr,)
            r = bench_chain(fx, probes=probes, drive_db=drive)
            r.get("ess", {}).pop("_fr_f", None)
            r.get("ess", {}).pop("_fr_db", None)
            print("BENCH_JSON " + json.dumps(r))
        elif a[0] == "voice":
            r = bench_voice(a[1], note=int(opt("--note", 60, int) or 60),
                            vel=float(opt("--vel", 1.0) or 1.0))
            print("BENCH_JSON " + json.dumps(r))
        elif a[0] == "cert":
            if "--all" in a:
                r = cert_all(force="--force" in a)
            else:
                r = cert_one(a[1], force="--force" in a)
            print("BENCH_JSON " + json.dumps(r))
            return 1 if r.get("failed") or r.get("error") else 0
        elif a[0] == "tails":
            print("BENCH_JSON " + json.dumps(tails_probe()))
        elif a[0] == "warp":
            print("BENCH_JSON " + json.dumps(warp_probe()))
        else:
            print(__doc__)
            return 2
    finally:
        cleanup(keep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
