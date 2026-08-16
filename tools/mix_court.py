#!/usr/bin/env python3
"""THE GRADIENT COURT (F7, docs/IMPORT_FINALE.md) — descent on the whole experience.

Chezy 2026-07-17: "it needs attention to the song! to feel the full experience
a human hears while listening to the audio! it focuses on side noises too
much! and the full experience is there but shunned and underwhelming compared
to the outliers! it needs perfect loss and gradient descent for all audio!"

Every prior court is per-lane (a note vs its stem window, a lane vs its stem,
a kit vs its slice) — nobody owned the SUM a human hears. Side elements can
each read stem-exact while the mix is wrong: transients measure loud and
confident, the sustained musical core measures noisy and lands shrunk, and
the song's body ends up recessed behind its own ornaments. This court defines
the loss Chezy named and descends on it:

  THE LOSS   multi-resolution log-mel distance between the master-free full
             mix and the stem-sum record (the same record master_match reads),
             over cells where the record holds energy (its top 70dB).
             Headline: exp_loss_db = RMS dB distance from the full experience.

  THE DESCENT  the pre-master mix is LINEAR in lane amplitudes, so per-lane
             mel powers are cached once and the loss is a closed function of
             the gain vector — Adam on log-gains with the analytic gradient,
             zero renders inside the loop. A smooth per-band + per-time offset
             (refit closed-form every step) absorbs master tilt/level/motion,
             so lanes own only the RELATIVE balance; master_match keeps owning
             the sum's tone. (Same family as Diff-MST / differentiable-console
             reverse-engineering, but our console is exactly linear.)

  THE VERDICT  solved moves under 0.75dB are measurement noise (dropped);
             moves clamp to +-9dB; the applied song is RE-RENDERED and the
             TRUE loss must drop — one halved retry if the linear model and
             the engine disagree, then REVERT and file the refusal.

Receipts -> <stems>/mix_court.json. Kill: SOTADAW_NO_MIXCOURT=1.

    .venv/bin/python tools/mix_court.py <song> [--dry] [--report path]
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SONGS = os.path.join(ROOT, "songs")

from a2m_correct import (M1, load_mono, render_stems,       # noqa: E402
                         stem_paths_from_song, sum_files)

# (n_fft, hop, n_mels): fine time for balance + long window for bass truth
SCALES = ((2048, 1024, 64), (8192, 2048, 48))
FMIN, FMAX = 45.0, 16000.0
VALID_DB = 70.0        # cells within this of the record's mel peak count
MIN_MOVE_DB = 0.75     # a solved move under this is noise, not a verdict
CLAMP_DB = 9.0         # one court, one bounded correction
CRED_RAISE_CAP = 2.0   # THE CREDIBILITY GATE (F7.1, Chezy: "IT ALMOST MAKES
#   UP NOTES"): a lane whose CONTENT is untrustworthy (noisy velocity mapping
#   vs its stem, or a failed credibility corr) may be CUT freely but raised
#   at most this — boosting a wrong-note lane to fill the record's cells
#   fabricates presence. Cuts are always safe; raises must be earned.
CRED_MAD_DB = 1.5      # vel_err_db_mad_before above this = untrusted content
CRED_CORR = 0.35       # a2m credibility corr below this = untrusted content
APPLY_MIN_DB = 0.15    # predicted RMS drop must clear this to touch the song
REAL_IMPROVE_DB = 0.05  # ... and the REAL render must confirm at least this
ITERS = 300
LR = 0.05
RIDGE = 1e-3           # prefer no-move when the data is indifferent
U2DB = 10.0 / math.log(10.0)   # u = ln(power multiplier) -> dB
OFF_T_SMOOTH_S = 2.0   # time-offset smoothing (absorbs master motion, not lanes)
OFF_B_SMOOTH = 9       # band-offset smoothing (absorbs tilt, not per-band theft)


def say(msg):
    print(f"[mix] {msg}", flush=True)


# ---------------------------------------------------------------- mel machinery
def mel_fb(sr, n_fft, n_mels, fmin=FMIN, fmax=FMAX):
    def h2m(f):
        return 2595.0 * np.log10(1.0 + f / 700.0)

    def m2h(m):
        return 700.0 * (10.0 ** (m / 2595.0) - 1.0)

    pts = m2h(np.linspace(h2m(fmin), h2m(min(fmax, sr / 2 - 1)), n_mels + 2))
    bins = np.floor((n_fft + 1) * pts / sr).astype(int)
    fb = np.zeros((n_mels, n_fft // 2 + 1), np.float32)
    for i in range(n_mels):
        a, b, c = bins[i], bins[i + 1], bins[i + 2]
        b = max(b, a + 1)
        c = max(c, b + 1)
        fb[i, a:b] = np.linspace(0.0, 1.0, b - a, endpoint=False)
        fb[i, b:c] = np.linspace(1.0, 0.0, c - b, endpoint=False)
    return fb


def mel_power(x, sr, n_fft, hop, n_mels, fb=None):
    """(n_mels, T) mel POWER, chunked so the rfft never balloons."""
    if fb is None:
        fb = mel_fb(sr, n_fft, n_mels)
    n = len(x)
    T = max(0, 1 + (n - n_fft) // hop)
    if T <= 0:
        return np.zeros((n_mels, 0), np.float32)
    win = np.hanning(n_fft).astype(np.float32)
    out = np.empty((n_mels, T), np.float32)
    block = max(256, (1 << 22) // (n_fft // 2 + 1))
    x = x.astype(np.float32, copy=False)
    for s in range(0, T, block):
        e = min(T, s + block)
        idx = (np.arange(s, e)[:, None] * hop + np.arange(n_fft)[None, :])
        F = np.fft.rfft(x[idx] * win[None, :], axis=1)
        out[:, s:e] = fb @ (F.real ** 2 + F.imag ** 2).T.astype(np.float32)
    return out


def db(p):
    return (10.0 * np.log10(p + 1e-12)).astype(np.float32)


# ------------------------------------------------------------- offsets + loss
def _smooth(v, k):
    k = int(k) | 1                       # odd width
    if k <= 1 or len(v) < 3:
        return v.astype(np.float32)
    pad = k // 2
    vp = np.pad(v.astype(np.float32), pad, mode="edge")
    ker = np.ones(k, np.float32) / k
    return np.convolve(vp, ker, "valid").astype(np.float32)


def fit_offsets(D, w, t_smooth, b_smooth=OFF_B_SMOOTH):
    """Closed-form smooth bias field o(b,t) = ob[b] + ot[t] over valid cells.
    ob carries the tilt AND the level (master_match's turf); ot is zero-mean
    motion. Both smoothed so lanes can't be stolen band-by-band or beat-by-beat."""
    ob = np.zeros(D.shape[0], np.float32)
    ot = np.zeros(D.shape[1], np.float32)
    for _ in range(2):
        r = (D - ot[None, :]) * w
        ob = _smooth(r.sum(1) / (w.sum(1) + 1e-9), b_smooth)
        r = (D - ob[:, None]) * w
        ot = _smooth(r.sum(0) / (w.sum(0) + 1e-9), t_smooth)
        ot -= float(ot.mean()) if len(ot) else 0.0
    return ob, ot


def loss_of_logM(logM, R, w, tsm):
    """Offset-fitted mean-square dB error of one already-built mix log-mel."""
    T = min(logM.shape[1], R.shape[1])
    logM, Rc, wc = logM[:, :T], R[:, :T], w[:, :T]
    ob, ot = fit_offsets(Rc - logM, wc, tsm)
    E = (logM + ob[:, None] + ot[None, :] - Rc) * wc
    return float((E ** 2).sum() / (wc.sum() + 1e-9)), (ob, ot, E, wc)


def loss_grad(u, P, R, w, tsm):
    """Data loss + analytic gradient wrt u (ln power multipliers) for one scale.
    P: (N, B, T) lane mel powers; R: (B, T) record log-mel dB; w: valid mask."""
    A = np.exp(u).astype(np.float32)
    M = np.tensordot(A, P, axes=1) + 1e-12
    logM = (U2DB * np.log(M)).astype(np.float32)
    L, (ob, ot, E, wc) = loss_of_logM(logM, R, w, tsm)
    n = wc.sum() + 1e-9
    G = (2.0 * E / n) * (U2DB / M[:, :E.shape[1]])
    grad = np.tensordot(P[:, :, :E.shape[1]], G, axes=([1, 2], [0, 1])) * A
    return L, grad.astype(np.float64), (ob, ot, E)


def solve(P_scales, R_scales, w_scales, tsms, iters=ITERS, lr=LR,
          raise_caps_db=None):
    """Adam on u with the exact linear-mix gradient; offsets refit each step.
    raise_caps_db: optional per-lane UPPER bound in dB (the credibility gate)
    — cuts always keep the full clamp."""
    n_lanes = P_scales[0].shape[0]
    u = np.zeros(n_lanes, np.float64)
    m = np.zeros_like(u)
    v = np.zeros_like(u)
    ulim = CLAMP_DB / U2DB
    umax = np.full(n_lanes, ulim)
    if raise_caps_db is not None:
        umax = np.minimum(umax, np.asarray(raise_caps_db, np.float64) / U2DB)
    hist = []
    for it in range(1, iters + 1):
        Lt, g = 0.0, np.zeros_like(u)
        for P, R, w, tsm in zip(P_scales, R_scales, w_scales, tsms):
            L, gr, _ = loss_grad(u, P, R, w, tsm)
            Lt += L / len(P_scales)
            g += gr / len(P_scales)
        g += 2.0 * RIDGE * u
        m = 0.9 * m + 0.1 * g
        v = 0.999 * v + 0.001 * g * g
        mh = m / (1 - 0.9 ** it)
        vh = v / (1 - 0.999 ** it)
        u -= lr * mh / (np.sqrt(vh) + 1e-9)
        # a uniform shift of every lane is EXACTLY the offset's job (null
        # space: e^c*M <-> ob-c) — pin it so moves are pure RELATIVE balance
        # and the master trim keeps owning level
        u -= u.mean()
        np.clip(u, -ulim, umax, out=u)
        hist.append(Lt)
        if it > 60 and hist[-30] - hist[-1] < 1e-5:
            break
    return u, hist


def model_loss(u, P_scales, R_scales, w_scales, tsms):
    Ls = []
    for P, R, w, tsm in zip(P_scales, R_scales, w_scales, tsms):
        L, _, _ = loss_grad(u, P, R, w, tsm)
        Ls.append(L)
    return math.sqrt(sum(Ls) / len(Ls))


def attribution(P, R, w, tsm, names):
    """Per-lane over/under story at u=0, on the fine scale: for cells a lane
    DOMINATES, the offset-fitted signed error = how far that lane's territory
    sits from the record. Positive = louder than the record."""
    A = np.ones(P.shape[0], np.float32)
    M = np.tensordot(A, P, axes=1) + 1e-12
    logM = (U2DB * np.log(M)).astype(np.float32)
    _, (ob, ot, E, wc) = loss_of_logM(logM, R, w, tsm)
    T = E.shape[1]
    dom = np.argmax(P[:, :, :T], axis=0)
    total = float((wc > 0).sum()) + 1e-9
    rows = []
    for i, nm in enumerate(names):
        cells = (dom == i) & (wc > 0)
        k = int(cells.sum())
        if k == 0:
            continue
        rows.append({"lane": nm, "cells_pct": round(100.0 * k / total, 1),
                     "err_db": round(float(E[cells].mean()), 2)})
    rows.sort(key=lambda r: -abs(r["err_db"]))
    return rows


# ------------------------------------------------------------------ the court
def _tsm_frames(hop, sr):
    return max(3, int(OFF_T_SMOOTH_S * sr / hop))


def render_mix_masterfree(song_path, out):
    """The REAL pre-master mix (mutes honored, spectral lanes stripped —
    render_stems' own OOM law), rendered through the engine."""
    song = json.load(open(song_path))
    song["tracks"] = [t for t in song.get("tracks", [])
                      if (t.get("source") or {}).get("kind") != "spectral"]
    song["master"] = []
    song["masterGainDb"] = 0.0
    tp = os.path.join(SONGS, f"_mixc_{os.path.basename(song_path)}")
    json.dump(song, open(tp, "w"))
    try:
        r = subprocess.run([M1, "render", tp, out], capture_output=True,
                           text=True, timeout=1800, cwd=ROOT)
        if r.returncode != 0:
            raise RuntimeError(f"m1 render rc={r.returncode}: "
                               f"{r.stderr[-300:]}")
    finally:
        if os.path.exists(tp):
            os.remove(tp)


def true_loss(mix_wav, R_scales, w_scales, tsms):
    x, sr = load_mono(mix_wav)
    Ls, mels = [], []
    for (nfft, hop, nm), R, w, tsm in zip(SCALES, R_scales, w_scales, tsms):
        logM = db(mel_power(x, sr, nfft, hop, nm))
        L, _ = loss_of_logM(logM, R, w, tsm)
        Ls.append(L)
        mels.append(logM)
    return math.sqrt(sum(Ls) / len(Ls)), mels


def court(song_path, dry=False, iters=ITERS, say=say):
    if os.environ.get("SOTADAW_NO_MIXCOURT") == "1":
        say("SOTADAW_NO_MIXCOURT=1 — skipped")
        return None
    song = json.load(open(song_path))
    stems = stem_paths_from_song(song)
    if not stems:
        say("no *_stems/ references — no record to descend toward")
        return None
    tmp = tempfile.mkdtemp(prefix="mix_court_")
    receipt = {"song": os.path.relpath(song_path, ROOT), "applied": False}
    try:
        # 1) the record: stem-sum mel per scale + the valid-cell mask
        rec, sr = sum_files(list(stems.values()))
        R_scales, w_scales, tsms = [], [], []
        for nfft, hop, nm in SCALES:
            R = db(mel_power(rec, sr, nfft, hop, nm))
            w = (R > R.max() - VALID_DB).astype(np.float32)
            R_scales.append(R)
            w_scales.append(w)
            tsms.append(_tsm_frames(hop, sr))
        del rec

        # 2) the lanes: per-lane mel powers from master-free stem renders
        files, rtracks = render_stems(song_path, tmp)
        names, Ps = [], []
        for f, t in zip(files, rtracks):
            if t.get("muted"):
                continue                     # the real mix excludes them
            x, xsr = load_mono(os.path.join(tmp, f))
            if not len(x) or float(np.abs(x).max()) < 1e-5:
                continue                     # silent render: frozen out
            names.append(t.get("name", f))
            Ps.append([mel_power(x, xsr, *sc) for sc in SCALES])
            del x
        if len(names) < 2:
            say(f"{len(names)} sounding lane(s) — nothing to balance")
            return None
        P_scales = []
        for si in range(len(SCALES)):
            T = min(min(p[si].shape[1] for p in Ps), R_scales[si].shape[1])
            P_scales.append(np.stack([p[si][:, :T] for p in Ps]))
            R_scales[si] = R_scales[si][:, :T]
            w_scales[si] = w_scales[si][:, :T]
        say(f"{len(names)} lanes x {[p.shape[2] for p in P_scales]} frames "
            f"vs the record")

        # 3) the REAL before-loss + how honest the linear model is
        before_wav = os.path.join(tmp, "_before.wav")
        render_mix_masterfree(song_path, before_wav)
        before, mels = true_loss(before_wav, R_scales, w_scales, tsms)
        mdiff = []
        for si, logM_real in enumerate(mels):
            T = min(logM_real.shape[1], P_scales[si].shape[2])
            logM_model = db(P_scales[si][:, :, :T].sum(axis=0))
            wc = w_scales[si][:, :T]
            mdiff.append(((logM_model - logM_real[:, :T]) * wc) ** 2
                         / (wc.sum() + 1e-9))
        model_rms = math.sqrt(sum(float(d.sum()) for d in mdiff)
                              / len(mdiff))
        receipt["exp_loss_before_db"] = round(before, 3)
        receipt["model_rms_db"] = round(model_rms, 2)
        say(f"exp_loss BEFORE {before:.3f}dB RMS (linear model within "
            f"{model_rms:.2f}dB of the engine)")
        if model_rms > 1.5:
            say("model looks far from the engine — verdicts lean on the "
                "real-render verify")

        # 4) the story at u=0: whose territory is over, whose is shunned
        att = attribution(P_scales[0], R_scales[0], w_scales[0], tsms[0],
                          names)
        receipt["attribution"] = att
        for r in att[:8]:
            say(f"  {r['lane']:<18} {r['err_db']:+.2f}dB over "
                f"{r['cells_pct']}% of the record's cells")

        # 5) THE CREDIBILITY GATE (F7.1): consume the correction's own
        # measurements — a lane with a noisy velocity mapping vs its stem
        # (vel_err_db_mad_before > CRED_MAD_DB) or a failed credibility corr
        # may be cut freely but raised at most CRED_RAISE_CAP. Boosting a
        # wrong-note lane to fill the record's territory MAKES UP NOTES
        # louder (aranyanyara_4: vocals_sketch mad 2.09, a2m had pulled it
        # -10.5dB, the ungated court raised it +8.8 — Chezy heard it).
        caps = [CLAMP_DB] * len(names)
        gated = {}
        rp = os.path.join(os.path.splitext(song_path)[0] + "_stems",
                          "a2m_report.json")
        if os.path.exists(rp):
            try:
                rep = json.load(open(rp))
                mel = rep.get("melodic", {}) or {}
                cred = rep.get("credibility", {}) or {}
                for i, n in enumerate(names):
                    mad = (mel.get(n) or {}).get("vel_err_db_mad_before")
                    corr = cred.get(n)
                    why = []
                    if mad is not None and mad > CRED_MAD_DB:
                        why.append(f"vel mad {mad:.2f}dB")
                    if corr is not None and corr < CRED_CORR:
                        why.append(f"cred corr {corr:.2f}")
                    if why:
                        caps[i] = CRED_RAISE_CAP
                        gated[n] = ", ".join(why)
            except Exception:
                pass
        if gated:
            say(f"credibility gate: raises capped at +{CRED_RAISE_CAP}dB for "
                f"{gated} (cuts stay free)")
        receipt["credibility_gate"] = gated

        # 6) descend
        u, hist = solve(P_scales, R_scales, w_scales, tsms, iters=iters,
                        raise_caps_db=caps)
        moves = {n: round(float(U2DB * ui), 2) for n, ui in zip(names, u)}
        kept = {n: v for n, v in moves.items() if abs(v) >= MIN_MOVE_DB}
        predicted = model_loss(u, P_scales, R_scales, w_scales, tsms)
        pred0 = math.sqrt(hist[0]) if hist else predicted
        receipt.update({"moves_solved": moves, "moves_applied": kept,
                        "predicted_after_db": round(predicted, 3),
                        "iters_ran": len(hist)})
        say(f"descent: {len(hist)} iters, model {pred0:.3f} -> "
            f"{predicted:.3f}dB; moves >= {MIN_MOVE_DB}dB: {kept}")
        if not kept or (pred0 - predicted) < APPLY_MIN_DB:
            receipt["verdict"] = "balance already at the optimum"
            say("court closes: the balance is already at the optimum")
            return receipt
        if dry:
            receipt["verdict"] = "dry run — moves not applied"
            return receipt

        # 6) apply by (name, occurrence) — never trust names to be unique
        def _gains(sj, mv, scale=1.0):
            seen = {}
            for t in sj.get("tracks", []):
                nm = t.get("name", "")
                k = (nm, seen.get(nm, 0))
                seen[nm] = seen.get(nm, 0) + 1
                if k[1] == 0 and nm in mv:
                    t["gainDb"] = round(float(t.get("gainDb", 0.0))
                                        + mv[nm] * scale, 2)
        orig = json.load(open(song_path))
        cur = json.loads(json.dumps(orig))
        _gains(cur, kept)
        json.dump(cur, open(song_path, "w"), indent=1)
        after_wav = os.path.join(tmp, "_after.wav")
        render_mix_masterfree(song_path, after_wav)
        after, _ = true_loss(after_wav, R_scales, w_scales, tsms)
        say(f"exp_loss AFTER {after:.3f}dB RMS (real render)")
        if after > before - REAL_IMPROVE_DB:
            say("the engine disagrees with the model — one halved retry")
            cur = json.loads(json.dumps(orig))
            _gains(cur, kept, scale=0.5)
            json.dump(cur, open(song_path, "w"), indent=1)
            render_mix_masterfree(song_path, after_wav)
            after, _ = true_loss(after_wav, R_scales, w_scales, tsms)
            receipt["halved"] = True
            say(f"exp_loss HALVED {after:.3f}dB RMS")
            if after > before - REAL_IMPROVE_DB:
                json.dump(orig, open(song_path, "w"), indent=1)
                receipt["verdict"] = ("REVERTED: the real render never "
                                      "confirmed the drop")
                receipt["exp_loss_after_db"] = round(after, 3)
                say("REVERTED — the loss never dropped on the real render")
                return receipt
            kept = {n: round(v * 0.5, 2) for n, v in kept.items()}
            receipt["moves_applied"] = kept
        receipt.update({"applied": True, "exp_loss_after_db": round(after, 3),
                        "verdict": f"balance moved {len(kept)} lanes, "
                                   f"{before:.3f} -> {after:.3f}dB RMS"})
        say(f"VERDICT: {receipt['verdict']} {kept}")
        return receipt
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        try:
            sd = os.path.splitext(song_path)[0] + "_stems"
            if os.path.isdir(sd) and receipt.get("exp_loss_before_db") \
                    is not None:
                json.dump(receipt, open(os.path.join(sd, "mix_court.json"),
                                        "w"), indent=1)
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("song")
    ap.add_argument("--dry", action="store_true",
                    help="measure + solve + report; never touch the song")
    ap.add_argument("--iters", type=int, default=ITERS)
    ap.add_argument("--force", action="store_true",
                    help="run even while the app is live (heal scripts only)")
    ap.add_argument("--report", default=None)
    a = ap.parse_args()
    os.chdir(ROOT)
    if not a.dry and not a.force \
            and subprocess.run(["pgrep", "-x", "sotadaw"],
                               capture_output=True).returncode == 0:
        sys.exit("[mix] sotadaw is LIVE — refusing to move a base song "
                 "under the user (--force to override)")
    import songname
    name = songname.resolve(a.song)
    path = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(path):
        sys.exit(f"no such song: {path}")
    rep = court(path, dry=a.dry, iters=a.iters)
    if rep and a.report:
        json.dump(rep, open(a.report, "w"), indent=1)
        say(f"report -> {a.report}")


if __name__ == "__main__":
    main()
