#!/usr/bin/env python3
"""THE NOISE TRANSPLANT (wave 3 — "the 5% needs to be MIDI too"): upgrade a
truth deck's stochastic layer to the MEL-TRUE bank (default 128 bands, the
fidelity ruler's own resolution) WITHOUT re-tracking a single partial.

Per window: isolate the true residual (source - zero-noise render of the
existing capture), re-analyze it at the new bank, regenerate the phase
fields + noise notes, re-render. The tonal layer — hours of ultra capture —
is byte-untouched. Probe-proven on w13: 32-band+phase 88.53% -> 128-band
seed-only 92.14% on the float source (the band count, not phase, is the
lever on the mel ruler; phase fields ride on top for wave/si).

    noise_transplant.py <song> [--stem-name vocals] [--bands 128] [--window K]
"""
import argparse
import base64
import copy
import gc
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
sys.path.insert(0, os.path.join(ROOT, "tools"))


def say(msg):
    print(f"[transplant] {msg}", flush=True)


def transplant_window(wdir, n_bands=128):
    """Returns (old_fidelity, new_fidelity) or None (skipped)."""
    import spectral as spx
    from vocal_truth import load_mono
    cp = os.path.join(wdir, "capture.json")
    raw = open(cp).read()
    cap = json.loads(raw)
    if int(cap.get("noise_bands", 0)) == n_bands \
            and cap.get("noise_env_ruler") and cap.get("mix_env_ruler"):
        return None       # already mel-true + ruler-exact + polish-target'd
    old_nb = cap.get("noise_bands", "?")
    src_p = os.path.join(wdir, "source.wav")
    if not os.path.exists(src_p):
        say(f"{os.path.basename(wdir)}: no source.wav — skipped")
        return None
    src, sr = load_mono(src_p)
    n = min(len(src), int(cap["n_samples"]))
    hop = int(cap["hop"])
    spb = 60.0 / float(cap["bpm"])

    # 1. the tonal truth (partials + clicks), noise silenced. POP the ruler
    # fields too: a leftover mix_env_ruler would POLISH the tonal-only
    # render toward the FULL source env and poison r_true (wave-3.6 trap).
    nonoise = copy.deepcopy(cap)
    nonoise["tracks"]["noise"] = []
    nonoise.pop("noise_phase", None)
    nonoise.pop("noise_phase_lo", None)
    nonoise.pop("noise_env_ruler", None)
    nonoise.pop("mix_env_ruler", None)
    ne0 = nonoise.get("noise_env")
    if ne0:
        z = np.zeros((int(ne0["bands"]), int(ne0["frames"])), np.float16)
        ne0["data"] = base64.b64encode(z.tobytes()).decode()
    tonal = np.asarray(spx.render_capture(nonoise), dtype=np.float64)[:n]
    del nonoise
    r_true = src[:n].astype(np.float64) - tonal

    # FAST PATH (wave 3.5/3.6 field retrofit): the bank already matches —
    # the stochastic layer + phase fields are correct; only the ruler
    # targets are missing. Skip band/phase regeneration entirely.
    if int(cap.get("noise_bands", 0)) == n_bands:
        old_fid = (cap.get("fidelity") or {}).get("spectral_pct")
        renv = spx.ruler_env(r_true.astype(np.float32), sr, int(n_bands))
        cap["noise_env_ruler"] = {"bands": int(renv.shape[0]),
                                  "frames": int(renv.shape[1]),
                                  "data": base64.b64encode(
                                      renv.astype(np.float16)
                                      .tobytes()).decode()}
        menv = spx.ruler_env(src[:n].astype(np.float32), sr, int(n_bands))
        cap["mix_env_ruler"] = {"bands": int(menv.shape[0]),
                                "frames": int(menv.shape[1]),
                                "data": base64.b64encode(
                                    menv.astype(np.float16)
                                    .tobytes()).decode()}
        del renv, menv
        rend = np.asarray(spx.render_capture(cap), dtype=np.float32)[:n]
        v = spx.verify_arrays(src[:n], rend, sr)
        if old_fid is not None and float(v["spectral_pct"]) < float(old_fid):
            say(f"{os.path.basename(wdir)}: {old_fid} -> {v['spectral_pct']} "
                f"WORSE — old deck kept")
            del tonal, r_true, rend, src
            gc.collect()
            return None
        cap["fidelity"] = v
        bak = cp + f".nb{old_nb}bak"
        if not os.path.exists(bak):
            open(bak, "w").write(raw)
        rp = cap.get("files", {}).get("render")
        rp = os.path.join(wdir, os.path.basename(rp)) if rp \
            else os.path.join(wdir, "render.wav")
        from scipy.io import wavfile as _wf
        _wf.write(rp, sr, np.clip(rend, -1.0, 1.0).astype(np.float32))
        json.dump(cap, open(cp, "w"))
        del tonal, r_true, rend, src
        gc.collect()
        return old_fid, v["spectral_pct"]

    # 2. mel-true stochastic layer + phase fields at the new bank
    band_env = spx.noise_analyze(r_true.astype(np.float32), sr, hop,
                                 n_bands=n_bands)
    noise_notes = spx._noise_to_notes(band_env, hop, sr, spb)
    import librosa as _lb
    nlo, nhi = spx._noise_ffts(sr)
    PH = np.angle(_lb.stft(r_true.astype(np.float32), n_fft=nhi,
                           hop_length=hop, window="hann", center=True))
    PHL = np.angle(_lb.stft(r_true.astype(np.float32), n_fft=nlo,
                            hop_length=hop, window="hann", center=True))
    ver = spx._nb_version(n_bands)
    lo_rows, hi_rows = spx._noise_band_masks(sr, n_bands, ver)
    fb_hi, _ = spx._noise_filterbank(sr, nhi, ver, n_bands=n_bands)
    fb_lo, _ = spx._noise_filterbank(sr, nlo, ver, n_bands=n_bands)
    mask_hi = spx._phase_activity_mask(band_env, hi_rows, fb_hi, PH.shape[0])
    mask_lo = spx._phase_activity_mask(band_env, lo_rows, fb_lo, PHL.shape[0])

    old_fid = (cap.get("fidelity") or {}).get("spectral_pct")

    cap["noise_bands"] = int(n_bands)
    cap["noise_env"] = {"bands": int(band_env.shape[0]),
                        "frames": int(band_env.shape[1]),
                        "data": base64.b64encode(
                            band_env.astype(np.float16).tobytes()).decode()}
    renv = spx.ruler_env(r_true.astype(np.float32), sr, int(n_bands))
    cap["noise_env_ruler"] = {"bands": int(renv.shape[0]),
                              "frames": int(renv.shape[1]),
                              "data": base64.b64encode(
                                  renv.astype(np.float16).tobytes()).decode()}
    menv = spx.ruler_env(src[:n].astype(np.float32), sr, int(n_bands))
    cap["mix_env_ruler"] = {"bands": int(menv.shape[0]),
                            "frames": int(menv.shape[1]),
                            "data": base64.b64encode(
                                menv.astype(np.float16).tobytes()).decode()}
    del renv, menv
    cap["noise_phase"] = {"n_fft": int(nhi), "bins": int(PH.shape[0]),
                          "frames": int(PH.shape[1]), "bits": 8,
                          "codec": "zlib",
                          "data": spx._pack_phase8(PH, mask_hi)}
    cap["noise_phase_lo"] = {"n_fft": int(nlo), "bins": int(PHL.shape[0]),
                             "frames": int(PHL.shape[1]), "bits": 8,
                             "codec": "zlib",
                             "data": spx._pack_phase8(PHL, mask_lo)}
    cap["tracks"]["noise"] = noise_notes
    del PH, PHL, mask_hi, mask_lo, band_env

    # 3. re-render + honest per-window fidelity vs the float source.
    # KEEP-THE-WIN: capture-time correction rounds sometimes tuned the old
    # 32-band layer past what a single-shot re-analysis recovers (w24:
    # 84.14 -> 83.55) — commit ONLY a measured win, else disk is untouched.
    rend = np.asarray(spx.render_capture(cap), dtype=np.float32)[:n]
    v = spx.verify_arrays(src[:n], rend, sr)
    if old_fid is not None and float(v["spectral_pct"]) < float(old_fid):
        say(f"{os.path.basename(wdir)}: {old_fid} -> {v['spectral_pct']} "
            f"WORSE — old deck kept")
        del tonal, r_true, rend, src
        gc.collect()
        return None
    cap["fidelity"] = v
    bak = cp + f".nb{old_nb}bak"
    if not os.path.exists(bak):                 # first transplant keeps the old
        open(bak, "w").write(raw)
    rp = cap.get("files", {}).get("render")
    rp = os.path.join(wdir, os.path.basename(rp)) if rp \
        else os.path.join(wdir, "render.wav")
    from scipy.io import wavfile as _wf
    _wf.write(rp, sr, np.clip(rend, -1.0, 1.0).astype(np.float32))
    json.dump(cap, open(cp, "w"))
    del tonal, r_true, rend, src
    gc.collect()
    return old_fid, v["spectral_pct"]


def run(song_name, stem_name="vocals", n_bands=128, only_window=None):
    sub = "vtruth" if stem_name == "vocals" else f"truth_{stem_name}"
    root = os.path.join(SONGS, f"{song_name}_spectral", sub)
    wdirs = sorted((d for d in os.listdir(root) if d.startswith("w")
                    and d[1:].isdigit()
                    and os.path.exists(os.path.join(root, d, "capture.json"))),
                   key=lambda d: int(d[1:]))
    if only_window is not None:
        wdirs = [d for d in wdirs if int(d[1:]) == only_window]
    say(f"{stem_name}: {len(wdirs)} windows -> {n_bands}-band mel-true noise")
    ups, t_old, t_new = 0, [], []
    for d in wdirs:
        r = transplant_window(os.path.join(root, d), n_bands=n_bands)
        if r is None:
            continue
        old, new = r
        ups += 1
        if old is not None:
            t_old.append(float(old))
        t_new.append(float(new))
        say(f"{d}: {old} -> {new}")
    if ups:
        say(f"done: {ups} windows transplanted "
            f"(mean {np.mean(t_old):.2f} -> {np.mean(t_new):.2f})"
            if t_old else f"done: {ups} windows")
    return ups


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("song")
    ap.add_argument("--stem-name", default="vocals",
                    choices=["vocals", "drums", "bass", "other"])
    ap.add_argument("--bands", type=int, default=128)
    ap.add_argument("--window", type=int, default=None)
    a = ap.parse_args()
    run(a.song, stem_name=a.stem_name, n_bands=a.bands, only_window=a.window)
