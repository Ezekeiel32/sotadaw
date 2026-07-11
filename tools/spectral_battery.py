#!/usr/bin/env python3
"""SPECTRAL CAPTURE battery: the roundtrip proof (audio -> MIDI -> audio).

Every leg captures a signal, renders it BACK from the note representation
(bend/gain envelopes + phase locks + noise lane), and scores the render against
the source. Thresholds are floors, not vibes — a regression turns the leg red.

  synthetic: tone / chord / sweep / vibrato / AM / noise / clicks+tone
  contract:  render determinism (md5 x2), edited-notes graceful render,
             LOSSLESS byte-exactness (int16 mono + stereo, md5 of ints)
  real:      any wavs/mp3s passed on the CLI (10s clips) — honest scoreboard

Run:  .venv/bin/python tools/spectral_battery.py [--real a.mp3 b.wav ...]
"""
import argparse, hashlib, json, math, os, sys, tempfile, time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import spectral as sp

SR = 44100
RESULTS = []


def leg(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}  {detail}", flush=True)
    return bool(cond)


def roundtrip(x, sr=SR, with_noise=True, bpm=120.0):
    """array -> THE REAL CAPTURE PATH -> render. Returns (render, metrics, cap)."""
    cap = sp.capture_arrays(x, sr, bpm=bpm)
    if not with_noise:
        cap["tracks"]["noise"] = []
        cap["tracks"]["clicks"] = []
    r = sp.render_capture(cap)
    return r, sp.verify_arrays(x, r, sr), cap


def t_tone():
    t = np.arange(int(SR * 2)) / SR
    x = 0.5 * np.sin(sp.TWO_PI * 440 * t + 0.7)
    _, m, _ = roundtrip(x, with_noise=False)
    leg("tone 440 spectral>=99.5", m["spectral_pct"] >= 99.5, f"{m['spectral_pct']}%")
    leg("tone 440 si_sdr>=40dB", m["si_sdr_db"] >= 40.0, f"{m['si_sdr_db']}dB")


def t_chord():
    t = np.arange(int(SR * 2.5)) / SR
    x = np.zeros_like(t)
    for f, a in ((220.0, .3), (277.18, .22), (329.63, .2), (415.3, .12), (554.37, .08)):
        x += a * np.sin(sp.TWO_PI * f * t + f)
    x *= (1.0 + 0.15 * np.sin(sp.TWO_PI * 0.7 * t))          # slow AM
    _, m, _ = roundtrip(x, with_noise=False)
    leg("chord+AM spectral>=99", m["spectral_pct"] >= 99.0, f"{m['spectral_pct']}%")
    leg("chord+AM si_sdr>=25dB", m["si_sdr_db"] >= 25.0, f"{m['si_sdr_db']}dB")


def t_sweep():
    t = np.arange(int(SR * 2)) / SR
    f0, f1 = 200.0, 800.0
    ph = sp.TWO_PI * (f0 * t + (f1 - f0) * t * t / (2 * t[-1]))
    x = 0.4 * np.sin(ph)
    _, m, _ = roundtrip(x, with_noise=False)
    leg("sweep 200-800 spectral>=98", m["spectral_pct"] >= 98.0, f"{m['spectral_pct']}%")
    leg("sweep si_sdr>=18dB", m["si_sdr_db"] >= 18.0, f"{m['si_sdr_db']}dB")


def t_vibrato():
    t = np.arange(int(SR * 2)) / SR
    inst = 440.0 * 2.0 ** (0.5 / 12.0 * np.sin(sp.TWO_PI * 6.0 * t))    # +-50c @6Hz
    ph = sp.TWO_PI * np.cumsum(inst) / SR
    x = 0.4 * np.sin(ph)
    _, m, _ = roundtrip(x, with_noise=False)
    # +-50c @6Hz is an extreme synthetic (vocal vibrato is shallower); 95 is
    # the honest current floor — raising it = the roadmap's reassignment work
    leg("vibrato spectral>=95", m["spectral_pct"] >= 95.0, f"{m['spectral_pct']}%")
    leg("vibrato si_sdr>=15dB", m["si_sdr_db"] >= 15.0, f"{m['si_sdr_db']}dB")
    # FULL PATH (noise + phase fields, as real music runs): waveform truth —
    # mel under-reads sparse content (quiet-band L1 vs a -60dB floor) but the
    # reconstruction is near-perfect; SI is the honest guard here
    _, mf, _ = roundtrip(x, with_noise=True)
    leg("vibrato FULL-PATH si_sdr>=30dB", mf["si_sdr_db"] >= 30.0,
        f"{mf['si_sdr_db']}dB corr {mf['wave_corr']}")


def t_noise():
    rng = np.random.default_rng(7)
    x = 0.2 * rng.standard_normal(int(SR * 1.5))
    from scipy.signal import butter, sosfilt
    x = sosfilt(butter(2, [300 / (SR / 2), 6000 / (SR / 2)], "band", output="sos"), x)
    r, m, _ = roundtrip(x)
    leg("shaped noise spectral>=96", m["spectral_pct"] >= 96.0, f"{m['spectral_pct']}%")
    # a stationary noise REALIZATION can't envelope-correlate; what must match
    # is the band ENERGY PROFILE (mean per-band level within 2dB)
    ea = sp.noise_analyze(x, SR, 256).mean(axis=1)
    eb = sp.noise_analyze(r[:len(x)], SR, 256).mean(axis=1)
    live = ea > ea.max() * 0.05
    dev = float(np.abs(20 * np.log10((eb[live] + 1e-12) / (ea[live] + 1e-12))).mean())
    leg("shaped noise band profile <=2dB", dev <= 2.0, f"{dev:.2f}dB mean dev")


def t_clicks_tone():
    t = np.arange(int(SR * 2)) / SR
    x = 0.3 * np.sin(sp.TWO_PI * 330 * t)
    rng = np.random.default_rng(3)
    for c in range(8):
        i = int((0.2 + 0.2 * c) * SR)
        x[i:i + 200] += 0.4 * rng.standard_normal(200) * np.exp(-np.arange(200) / 40.0)
    _, m, _ = roundtrip(x)
    # transient snippets carry the clicks at -23..-32dB per hit; the last few
    # % live in window-view amp pollution of the tone — roadmap: refinement
    leg("clicks+tone spectral>=92", m["spectral_pct"] >= 92.0, f"{m['spectral_pct']}%")


def t_determinism():
    t = np.arange(int(SR * 1)) / SR
    x = 0.4 * np.sin(sp.TWO_PI * 300 * t) + 0.1 * np.sin(sp.TWO_PI * 900 * t)
    r1, _, cap = roundtrip(x)
    r2 = sp.render_capture(cap)
    h1 = hashlib.md5(r1.tobytes()).hexdigest()
    h2 = hashlib.md5(r2.tobytes()).hexdigest()
    leg("render md5-deterministic", h1 == h2, h1[:12])


def t_edited():
    t = np.arange(int(SR * 1.2)) / SR
    x = 0.4 * np.sin(sp.TWO_PI * 440 * t)
    _, _, cap = roundtrip(x, with_noise=False)
    edited = {"partials": [], "noise": []}
    for i, n in enumerate(cap["tracks"]["partials"]):
        e = {k: n[k] for k in ("start", "len", "pitch", "vel")}
        e["pitch"] += 3                      # transpose up a minor third
        e["start"] += 0.5                    # push half a beat
        edited["partials"].append(e)
    edited["partials"].append({"start": 0.0, "len": 0.5, "pitch": 72, "vel": 0.9})
    r = sp.render_capture(cap, song_notes=edited)
    ok = np.isfinite(r).all() and len(r) == cap["n_samples"] and float(np.abs(r).max()) < 2.0
    # the transposed render must actually BE higher: dominant freq check
    F = np.abs(np.fft.rfft(r[:SR]))
    f_dom = float(np.argmax(F) * SR / SR)    # bin == Hz at 1s window
    leg("edited notes render sane", ok, f"dom {f_dom:.0f}Hz (expect ~523)")
    leg("edit actually transposed", 500 <= f_dom <= 560, f"{f_dom:.0f}Hz")


def t_lossless():
    t = np.arange(int(SR * 1.2)) / SR
    L = 0.4 * np.sin(sp.TWO_PI * 349.23 * t) + 0.05 * np.sin(sp.TWO_PI * 1200 * t)
    R = 0.3 * np.sin(sp.TWO_PI * 349.23 * t + 1.0) + 0.1 * np.sin(sp.TWO_PI * 523.25 * t)
    rng = np.random.default_rng(11)
    L += 0.02 * rng.standard_normal(len(t))
    R += 0.02 * rng.standard_normal(len(t))
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "src.wav")
        sp.save_wav_i16(src, np.stack([L, R]), SR)
        cap = sp.capture(src, name="_battery_lossless", mode="lossless",
                         prog=sp._NULL_PROG, out_dir=td)
        leg("lossless capture reports byte_exact",
            cap["fidelity"].get("byte_exact") is True, json.dumps(cap["fidelity"]))
        # independent witness: reconstruct via files, compare INT md5s
        import soundfile as sf
        render = sp.render_capture(cap)
        resid, _ = sf.read(os.path.join(td, "residual.wav"), dtype="float64",
                           always_2d=True)
        orig, _ = sf.read(src, dtype="int16", always_2d=True)
        recon = sp.reconstruct_lossless(render[:len(resid)], resid, {"int": None})
        same = np.array_equal(recon.astype(np.int16), orig)
        leg("lossless bytes == original bytes",
            same, f"md5 {hashlib.md5(recon.astype(np.int16).tobytes()).hexdigest()[:10]}"
                  f" vs {hashlib.md5(orig.tobytes()).hexdigest()[:10]}")


# permanent 3rd real leg: the 96kHz mp4 that caught the COLA break — floors
# differ per file (unseen screen-audio content scores lower than music mp3s)
REAL_DEFAULTS = [("/home/chezy/329558__maxamaru__dramtic-synthtrumpet.mp3", 99.0),
                 ("/home/chezy/456798__zankuro__kojiros-trips.mp3", 99.0),
                 ("/home/chezy/20251102_1415_01k927t99wfb09m69emerhan55.mp4", 97.9)]


def t_vocal():
    """VOCALS AT TRUE FIDELITY (Chezy's ask): a real sung stem — formants,
    breath, melisma — must reproduce at high pure-MIDI AND 100% byte-exact.
    Voice is the hardest content; this is a standing floor."""
    path = "songs/yeshievishereid_stems/vocals.wav"
    if not os.path.exists(path):
        return
    au = sp.load_audio(path)
    sr = au["sr"]
    orig = au["orig"][:, int(45 * sr):int(53 * sr)]   # mid-song singing
    x = orig.mean(axis=0)
    cap = sp.capture_arrays(x, sr)
    m = sp.verify_arrays(x, sp.render_capture(cap)[:len(x)], sr)
    leg("vocal pure-MIDI spectral>=98", m["spectral_pct"] >= 98.0,
        f"{m['spectral_pct']}% | si {m['si_sdr_db']}dB | corr {m['wave_corr']}")
    # 100% byte-exact reconstruction of the vocal (lossless int16)
    import tempfile, hashlib
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "voc.wav")
        sp.save_wav_i16(src, orig, sr)
        capL = sp.capture(src, name="_voc", mode="lossless",
                          prog=sp._NULL_PROG, out_dir=td)
        render = sp.render_capture(capL)
        resid, _ = __import__("soundfile").read(os.path.join(td, "residual.wav"),
                                                dtype="float64", always_2d=True)
        origi, _ = __import__("soundfile").read(src, dtype="int16", always_2d=True)
        recon = sp.reconstruct_lossless(render[:len(resid)], resid,
                                        {"int": None}).astype(np.int16)
        leg("vocal 100% byte-exact", np.array_equal(recon, origi),
            f"md5 {hashlib.md5(recon.tobytes()).hexdigest()[:10]}")


def t_stereo():
    """TRUE STEREO (M/S): capture both channels (mid full + side lighter),
    stereo render, per-channel verify. The honest stereo target — reproduces
    the WIDTH the mono downmix discards. Proven on the two stereo real files."""
    for path, cfloor, sfloor in (
            ("/home/chezy/456798__zankuro__kojiros-trips.mp3", 0.97, 12.0),
            ("/home/chezy/20251102_1415_01k927t99wfb09m69emerhan55.mp4", 0.96, 10.0)):
        if not os.path.exists(path):
            continue
        au = sp.load_audio(path)
        sr = au["sr"]
        orig = au["orig"][:, :sr * 6]
        if orig.shape[0] < 2:
            continue
        cap = sp.capture_arrays_stereo(orig, sr)
        r2 = sp.render_capture_stereo(cap)
        m = sp.verify_stereo(orig, r2, sr)
        leg(f"stereo:{os.path.basename(path)[:20]} corr>={cfloor}",
            m["wave_corr"] >= cfloor and m["si_sdr_db"] >= sfloor,
            f"corr {m['wave_corr']} | si {m['si_sdr_db']}dB | mel {m['spectral_pct']} | side={'side' in cap}")


def t_real(paths):
    for p in paths:
        if not os.path.exists(p):
            leg(f"real:{os.path.basename(p)}", False, "missing file")
            continue
        au = sp.load_audio(p)
        sr, x = au["sr"], au["x"]
        x = x[:sr * 10]                                     # 10s clip
        t0 = time.time()
        r, m, cap = roundtrip(x, sr=sr)
        dt = time.time() - t0
        n_notes = len(cap["tracks"]["partials"])
        n_noise = len(cap["tracks"]["noise"])
        floor = dict((a, b) for a, b in REAL_DEFAULTS).get(p, 95.5)
        leg(f"real:{os.path.basename(p)[:32]} spectral>={floor}",
            m["spectral_pct"] >= floor,
            f"{m['spectral_pct']}% | si_sdr {m['si_sdr_db']}dB | corr {m['wave_corr']} "
            f"| env {m['env_corr']} | {n_notes}+{n_noise} notes | {dt:.0f}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", nargs="*", default=[])
    ap.add_argument("--skip-synth", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    if not a.skip_synth:
        t_tone(); t_chord(); t_sweep(); t_vibrato(); t_noise(); t_clicks_tone()
        t_determinism(); t_edited(); t_lossless(); t_stereo(); t_vocal()
    if a.real:
        t_real(a.real)
    elif not a.skip_synth:
        t_real([p for p, _ in REAL_DEFAULTS if os.path.exists(p)])
    n_ok = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n[spectral_battery] {n_ok}/{len(RESULTS)} passed in {time.time()-t0:.0f}s")
    sys.exit(0 if n_ok == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
