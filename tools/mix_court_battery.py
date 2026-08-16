#!/usr/bin/env python3
"""THE GRADIENT COURT battery (F7, docs/IMPORT_FINALE.md) — pure, no engine.

Proves the descent kernel on synthetic lanes with KNOWN truth: relative-gain
recovery, the SIDE-NOISE LAW (a hot ornament lane is pulled down, the shunned
core raised), offset non-theft (master tilt/level/motion never stolen from
lanes), the null-space pin, clamps, noise floors, and the court's statics
(kill switch, stomp guard, revert path, receipts).

    .venv/bin/python tools/mix_court_battery.py
"""
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import mix_court as mc  # noqa: E402

N_OK = 0
N_BAD = 0


def ok(name, cond, detail=""):
    global N_OK, N_BAD
    if cond:
        N_OK += 1
        print(f"  ok  {name}")
    else:
        N_BAD += 1
        print(f" FAIL {name}  {detail}")


# ------------------------------------------------------------- synthetic rig
SR = 44100
N = 6 * SR
_t = np.arange(N) / SR
_rng = np.random.default_rng(7)

_gate8 = ((_t * 4) % 1 < 0.45).astype(np.float32)
BASS = (np.sin(2 * np.pi * 82 * _t) * _gate8 * 0.5).astype(np.float32)
_wn = _rng.standard_normal(N).astype(np.float32)
_F = np.fft.rfft(_wn)
_fr = np.fft.rfftfreq(N, 1 / SR)
_F[(_fr < 6000) | (_fr > 12000)] = 0
HATS = np.fft.irfft(_F, N).astype(np.float32)
HATS *= ((_t * 8) % 1 < 0.12).astype(np.float32) * 2.0
PAD = sum(np.sin(2 * np.pi * f * _t) for f in (220.0, 277.2, 329.6, 440.0))
PAD = (PAD * (0.6 + 0.4 * np.sin(2 * np.pi * 0.21 * _t)) * 0.12) \
    .astype(np.float32)
LANES = {"bass": BASS, "hats": HATS, "pad": PAD}


def setup(rec, lane_scale=None):
    """Record mel + lane mel powers, lanes optionally pre-scaled (a wrong
    CURRENT mix) — exactly what court() hands the solver."""
    lane_scale = lane_scale or {}
    R_s, w_s, tsms, P_s = [], [], [], []
    for nfft, hop, nm in mc.SCALES:
        R = mc.db(mc.mel_power(rec, SR, nfft, hop, nm))
        R_s.append(R)
        w_s.append((R > R.max() - mc.VALID_DB).astype(np.float32))
        tsms.append(mc._tsm_frames(hop, SR))
    for si, (nfft, hop, nm) in enumerate(mc.SCALES):
        Ps = [mc.mel_power(x * lane_scale.get(n, 1.0), SR, nfft, hop, nm)
              for n, x in LANES.items()]
        T = min(min(p.shape[1] for p in Ps), R_s[si].shape[1])
        P_s.append(np.stack([p[:, :T] for p in Ps]))
        R_s[si] = R_s[si][:, :T]
        w_s[si] = w_s[si][:, :T]
    return P_s, R_s, w_s, tsms


def solve_moves(rec, lane_scale=None, caps=None):
    P_s, R_s, w_s, tsms = setup(rec, lane_scale)
    u, hist = mc.solve(P_s, R_s, w_s, tsms, raise_caps_db=caps)
    return dict(zip(LANES, (mc.U2DB * u))), hist


REC_TRUE = (BASS * 1.0 + HATS * 10 ** (-6 / 20)
            + PAD * 10 ** (3 / 20)).astype(np.float32)


def main():
    print("== mel machinery ==")
    fb = mc.mel_fb(SR, 2048, 64)
    ok("fb: every band holds weight", float(fb.sum(1).min()) > 0)
    centers = fb.argmax(1)
    ok("fb: band centers monotonic", bool(np.all(np.diff(centers) >= 0)))
    P = mc.mel_power(BASS, SR, 2048, 1024, 64)
    ok("mel_power shape", P.shape == (64, 1 + (N - 2048) // 1024))
    ok("silence reads the floor",
       float(mc.db(mc.mel_power(np.zeros(SR, np.float32),
                                SR, 2048, 1024, 64)).max()) < -100)

    print("== offsets (the master absorber) ==")
    D = np.full((64, 400), 6.0, np.float32)
    w = np.ones_like(D)
    ob, ot = mc.fit_offsets(D, w, 87)
    ok("constant 6dB -> ob, not ot",
       abs(float(ob.mean()) - 6.0) < 0.05 and float(np.abs(ot).max()) < 0.05)
    Dw = (np.sin(np.linspace(0, 6 * np.pi, 400))[None, :]
          * np.ones((64, 1))).astype(np.float32) * 3.0
    ob, ot = mc.fit_offsets(Dw, w, 5)
    resid = Dw - ob[:, None] - ot[None, :]
    ok("broadband wobble -> ot absorbs", float(np.abs(resid).max()) < 0.8,
       f"resid {float(np.abs(resid).max()):.2f}")
    Dt = (np.linspace(-4, 4, 64)[:, None]
          * np.ones((1, 400))).astype(np.float32)
    ob, ot = mc.fit_offsets(Dt, w, 87)
    resid = Dt - ob[:, None] - ot[None, :]
    ok("band tilt -> ob absorbs", float(np.abs(resid).max()) < 0.8)
    ok("ot stays smooth (no beat theft)",
       float(np.abs(np.diff(ot)).max()) < 0.5)

    print("== recovery (truth 0 / -6 / +3 dB) ==")
    mv, hist = solve_moves(REC_TRUE)
    ok("relative hats-bass within 1.5dB of -6",
       abs((mv["hats"] - mv["bass"]) - (-6.0)) < 1.5,
       f"{mv['hats'] - mv['bass']:.2f}")
    ok("relative pad-bass within 1.5dB of +3",
       abs((mv["pad"] - mv["bass"]) - 3.0) < 1.5,
       f"{mv['pad'] - mv['bass']:.2f}")
    ok("descent actually descends", hist[-1] < hist[0] * 0.5,
       f"{hist[0]:.3f}->{hist[-1]:.3f}")
    ok("moves are zero-mean (null space pinned)",
       abs(sum(mv.values())) < 0.35, f"mean {sum(mv.values())/3:.2f}")

    print("== THE SIDE-NOISE LAW ==")
    # the CURRENT mix carries the ornament +8dB hot vs the record's balance
    mv, _ = solve_moves(REC_TRUE,
                        lane_scale={"hats": 10 ** ((-6 + 8) / 20),
                                    "bass": 1.0, "pad": 10 ** (3 / 20)})
    ok("hot ornament pulled DOWN >= 4dB vs core",
       (mv["hats"] - mv["pad"]) <= -4.0, f"{mv['hats'] - mv['pad']:.2f}")
    ok("the shunned core rises above the ornament",
       mv["pad"] > mv["hats"], f"pad {mv['pad']:.2f} hats {mv['hats']:.2f}")

    print("== offset non-theft ==")
    base, _ = solve_moves(REC_TRUE)
    wob = (REC_TRUE * 2.0
           * (1.0 + 0.3 * np.sin(2 * np.pi * 0.25 * _t))).astype(np.float32)
    mv, _ = solve_moves(wob)
    drift = max(abs(mv[k] - base[k]) for k in mv)
    ok("x2 level + slow wobble: lane drift < 0.75dB", drift < 0.75,
       f"drift {drift:.2f}")

    print("== rails ==")
    hot = (BASS + HATS * 10 ** (-6 / 20)
           + PAD * 10 ** (40 / 20)).astype(np.float32)
    mv, _ = solve_moves(hot)
    ok("absurd +40dB demand rails at the clamp",
       mv["pad"] <= mc.CLAMP_DB + 0.05, f"{mv['pad']:.2f}")
    mv, _ = solve_moves((BASS + HATS + PAD).astype(np.float32))
    ok("already balanced -> every move under MIN_MOVE",
       max(abs(v) for v in mv.values()) < mc.MIN_MOVE_DB,
       f"{ {k: round(v, 2) for k, v in mv.items()} }")

    print("== THE CREDIBILITY GATE (raises earned, cuts free) ==")
    # the record demands pad ~+8dB; a gated pad may not fabricate its way up
    hot_pad = (BASS + HATS * 10 ** (-6 / 20)
               + PAD * 10 ** (8 / 20)).astype(np.float32)
    caps = [mc.CLAMP_DB, mc.CLAMP_DB, mc.CRED_RAISE_CAP]   # bass, hats, pad
    mv, _ = solve_moves(hot_pad, caps=caps)
    ok("gated lane cannot rise past the cap",
       mv["pad"] <= mc.CRED_RAISE_CAP + 0.05, f"{mv['pad']:.2f}")
    # an UNGATED lane the record demands loud must sail past the cap value
    hot_bass = (BASS * 10 ** (8 / 20) + HATS * 10 ** (-6 / 20)
                + PAD).astype(np.float32)
    mv, _ = solve_moves(hot_bass, caps=caps)
    ok("ungated lanes keep the full range",
       mv["bass"] > mc.CRED_RAISE_CAP + 0.5 and mv["pad"] <= mc.CRED_RAISE_CAP + 0.05,
       f"bass {mv['bass']:.2f} pad {mv['pad']:.2f}")
    # a HOT gated lane is still cut freely — the gate is one-sided
    mv, _ = solve_moves(REC_TRUE,
                        lane_scale={"hats": 10 ** ((-6 + 8) / 20),
                                    "bass": 1.0, "pad": 10 ** (3 / 20)},
                        caps=[mc.CLAMP_DB, mc.CRED_RAISE_CAP, mc.CLAMP_DB])
    ok("gate never blocks a cut", (mv["hats"] - mv["pad"]) <= -4.0,
       f"{mv['hats'] - mv['pad']:.2f}")
    ok("gate thresholds sane",
       0.0 < mc.CRED_RAISE_CAP < mc.CLAMP_DB and mc.CRED_MAD_DB > 0
       and 0.0 < mc.CRED_CORR < 1.0)

    print("== signs + constants ==")
    ok("U2DB is 10/ln10", abs(mc.U2DB - 10.0 / math.log(10.0)) < 1e-12)
    ok("u -> dB round-trip exact",
       abs(mc.U2DB * math.log(10 ** (6 / 10)) - 6.0) < 1e-9)
    ok("court thresholds sane",
       0.0 < mc.MIN_MOVE_DB < mc.CLAMP_DB <= 12.0
       and 0.0 < mc.APPLY_MIN_DB < 1.0)

    print("== statics (the court's law in source) ==")
    src = open(os.path.join(ROOT, "tools", "mix_court.py")).read()
    ok("kill switch", "SOTADAW_NO_MIXCOURT" in src)
    ok("stomp guard on apply", "pgrep" in src and "sotadaw is LIVE" in src)
    ok("silent lanes frozen out before the solve",
       "< 1e-5" in src and "frozen out" in src)
    ok("real-render verify with revert", "REVERTED" in src
       and "halved" in src.lower())
    ok("null-space pin in the loop", "u -= u.mean()" in src)
    ok("receipts land in the stems dir", "mix_court.json" in src)
    ok("dry runs never touch the song",
       'receipt["verdict"] = "dry run — moves not applied"' in src)
    ok("master-free renders (stage separation law)",
       'song["master"] = []' in src)
    ok("credibility gate reads the correction's own report",
       "a2m_report.json" in src and "credibility gate" in src)
    ok("gate rides the receipt", 'receipt["credibility_gate"]' in src)

    print(f"\nmix_court battery: {N_OK} ok, {N_BAD} failed")
    sys.exit(1 if N_BAD else 0)


if __name__ == "__main__":
    main()
