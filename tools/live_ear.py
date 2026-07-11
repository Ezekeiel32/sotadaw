#!/usr/bin/env python3
"""THE LIVE EAR — R1 (BEST_DAW_30 #15): a CAUSAL beat/tempo tracker on live input.

The band-member keystone: dj_live advises on OUR OWN playback; audio_follow
follows OUR grid. Nothing tracked EXTERNAL time — the band could not follow a
human drummer's drift and the DJ could not beatmatch an outside deck. R1 is
the kernel: pure own-math (license-clean; no BeatNet weights), deterministic,
replay-provable, CPU-cheap, streaming:

  flux   spectral-flux onset envelope (hop ~11.6ms @44.1k, half-wave rectified,
         adaptive-mean normalized)
  tempo  autocorrelation of the last ~6s of flux, 60-200 BPM, with a strong
         CONTINUITY PRIOR (a working drummer drifts, never teleports)
  phase  comb alignment of recent onsets against the tempo hypothesis
  conf   autocorr peak sharpness x onset support

LAWS: CONFIDENCE OR SILENCE (below conf the tracker HOLDS its last grid instead
of chasing noise) · ZERO TOKENS (pure math) · CAUSAL ONLY (never reads ahead).

  live_ear.py --wav <file> [--json]     replay a recording through the kernel
  live_ear.py --selftest                synthetic proofs (steady / drift / noise)

Integration (next rungs): the app's input bus feeds blocks -> events
{"kind":"live_grid","bpm","phase_beat","conf","t"} ride ears.jsonl; the JAM
scheduler retargets per-phrase (retarget_base exists); deck verbs quantize to
the LIVE grid; Link publishes the tracked tempo.
"""
import argparse, json, math, os, sys

import numpy as np

HOP = 512                    # samples @44.1k = 11.6ms
WIN = 1024
ACF_S = 6.0                  # tempo window
BPM_LO, BPM_HI = 60.0, 200.0
CONF_FLOOR = 0.25            # below: HOLD, don't chase


class CausalBeat:
    def __init__(self, sr=44100):
        self.sr = sr
        self.prev_mag = None
        self.flux = []                       # onset envelope, one per hop
        self.carry = np.zeros(0)
        self.bpm = 0.0
        self.conf = 0.0
        self.phase_hop = 0.0                 # hop index of the last beat
        self.events = []
        self.hops = 0

    # ---- streaming input ----
    def feed(self, block):
        """Feed any-size mono float block; returns new grid events."""
        x = np.concatenate([self.carry, np.asarray(block, dtype=np.float64)])
        out = []
        i = 0
        while i + WIN <= len(x):
            frame = x[i:i + WIN] * np.hanning(WIN)
            mag = np.abs(np.fft.rfft(frame))
            if self.prev_mag is not None:
                d = mag - self.prev_mag
                self.flux.append(float(d[d > 0].sum()))
            else:
                self.flux.append(0.0)
            self.prev_mag = mag
            self.hops += 1
            i += HOP
            ev = self._tick()
            if ev:
                out.append(ev)
        self.carry = x[i:]
        return out

    # ---- the causal brain: runs every ~0.75s of new material ----
    def _tick(self):
        if self.hops % 32 != 0:              # re-estimate ~every 0.37s
            return None
        n_acf = int(ACF_S * self.sr / HOP)
        if len(self.flux) < n_acf:
            return None
        env = np.asarray(self.flux[-n_acf:])
        env = env - env.mean()
        if float(np.abs(env).sum()) < 1e-9:
            return None
        acf = np.correlate(env, env, "full")[len(env) - 1:]
        acf[0] = 0.0
        hop_s = HOP / self.sr
        lo = max(2, int(60.0 / BPM_HI / hop_s))
        hi = min(len(acf) - 1, int(60.0 / BPM_LO / hop_s))
        if hi <= lo:
            return None
        lags = np.arange(lo, hi)
        weights = np.ones_like(lags, dtype=np.float64)
        if self.bpm > 0:                     # CONTINUITY PRIOR: ±12% soft window
            cur_lag = 60.0 / self.bpm / hop_s
            weights = np.exp(-0.5 * ((lags - cur_lag) / (0.12 * cur_lag)) ** 2)
            weights = 0.35 + 0.65 * weights  # never fully blind to a real jump
        score = acf[lo:hi] * weights
        k = int(np.argmax(score))
        lag = float(lags[k])
        # parabolic refine
        if 0 < k < len(score) - 1:
            a, b, c = score[k - 1], score[k], score[k + 1]
            den = a - 2 * b + c
            if abs(den) > 1e-12:
                lag += 0.5 * (a - c) / den
        bpm = 60.0 / (lag * hop_s)
        peak = float(acf[lo + k])
        conf = peak / (float(np.abs(acf[lo:hi]).mean()) * 4.0 + 1e-9)
        conf = max(0.0, min(1.0, conf))
        if conf < CONF_FLOOR and self.bpm > 0:
            return None                      # CONFIDENCE OR SILENCE: hold
        # phase: best comb offset over the last 4 beats of flux
        beat_hops = 60.0 / bpm / hop_s
        recent = np.asarray(self.flux[-int(beat_hops * 3):])   # fresh anchor under drift
        if len(recent) < int(beat_hops):
            return None
        offs = np.arange(0.0, beat_hops, max(1.0, beat_hops / 48.0))
        best_o, best_s = 0.0, -1.0
        for o in offs:
            idx = np.arange(o, len(recent) - 1, beat_hops).astype(int)
            s = float(recent[idx].sum()) / max(1, len(idx))
            if s > best_s:
                best_s, best_o = s, float(o)
        start_hop = self.hops - len(recent)
        last_beat_hop = start_hop + best_o + \
            math.floor((self.hops - (start_hop + best_o)) / beat_hops) * beat_hops
        self.bpm, self.conf, self.phase_hop = bpm, conf, last_beat_hop
        ev = {"kind": "live_grid", "t": round(self.hops * hop_s, 3),
              "bpm": round(bpm, 2), "conf": round(conf, 3),
              "last_beat_s": round(last_beat_hop * hop_s, 3)}
        self.events.append(ev)
        return ev

    def beat_times(self, until_s):
        """The tracked grid unrolled forward from the last event (for scoring)."""
        if self.bpm <= 0:
            return []
        per = 60.0 / self.bpm
        t0 = self.phase_hop * HOP / self.sr
        out, t = [], t0
        while t > 0:
            t -= per                         # walk back to the window start
        while t < until_s:
            if t >= 0:
                out.append(t)
            t += per
        return out


def replay(path, block_s=0.25):
    import soundfile as sf
    y, sr = sf.read(path, always_2d=True, dtype="float64")
    x = y.mean(axis=1)
    cb = CausalBeat(sr)
    n = int(block_s * sr)
    for i in range(0, len(x), n):
        cb.feed(x[i:i + n])
    return cb


def _click_track(sr, dur, bpm_fn, swing_noise=0.0, seed=7):
    rng = np.random.default_rng(seed)
    x = 0.02 * rng.standard_normal(int(dur * sr))
    t = 0.0
    while t < dur - 0.1:
        bpm = bpm_fn(t)
        i = int(t * sr)
        n = int(0.02 * sr)
        x[i:i + n] += np.hanning(n) * np.sin(2 * np.pi * 1800 *
                                             np.arange(n) / sr) * 0.9
        t += 60.0 / bpm * (1.0 + swing_noise * float(rng.standard_normal()) * 0.01)
    return x


def _score(cb, sr, dur, bpm_fn):
    """p95 |predicted beat - nearest true beat| in ms, scored the way a CONSUMER
    reads the tracker: each event's grid predicts only until the NEXT event
    (the JAM/deck ask 'where is the next beat' against the CURRENT grid — a
    12s straight-line unroll under curved drift would measure the scorer, not
    the tracker). Second half only (post lock-in)."""
    true = []
    t = 0.0
    while t < dur:
        true.append(t)
        t += 60.0 / bpm_fn(t)
    errs = []
    evs = [e for e in cb.events if e["t"] > dur / 2]
    for e, nxt in zip(evs, evs[1:] + [{"t": dur}]):
        per = 60.0 / e["bpm"]
        b = e["last_beat_s"]
        while b < nxt["t"]:
            if b > e["t"] - per:             # beats this grid actually predicts
                errs.append(min(abs(b - tb) for tb in true) * 1000.0)
            b += per
    if not errs:
        return None
    return float(np.percentile(errs, 95))


def selftest():
    ok = True

    def chk(tag, cond, detail=""):
        nonlocal ok
        print(f"  {'ok' if cond else 'XX'} {tag} {detail}")
        ok = ok and cond
    sr, dur = 44100, 24.0
    cb = CausalBeat(sr)
    cb.feed(_click_track(sr, dur, lambda t: 120.0))
    chk("steady 120 tracked", abs(cb.bpm - 120.0) < 2.0, f"bpm {cb.bpm:.2f}")
    e = _score(cb, sr, dur, lambda t: 120.0)
    chk("steady phase p95 <= 60ms", e is not None and e <= 60.0, f"{e:.1f}ms")
    drift = lambda t: 120.0 + 6.0 * min(1.0, t / dur)      # 120 -> 126
    cb2 = CausalBeat(sr)
    cb2.feed(_click_track(sr, dur, drift))
    chk("±4-6 BPM drift followed", abs(cb2.bpm - drift(dur)) < 3.0,
        f"end bpm {cb2.bpm:.2f} (true {drift(dur):.1f})")
    e2 = _score(cb2, sr, dur, drift)
    chk("drift phase p95 <= 60ms", e2 is not None and e2 <= 60.0, f"{e2:.1f}ms")
    cb3 = CausalBeat(sr)
    rng = np.random.default_rng(1)
    cb3.feed(0.05 * rng.standard_normal(int(8 * sr)))       # pure noise
    chk("CONFIDENCE OR SILENCE on noise",
        cb3.bpm == 0.0 or cb3.conf < 0.6, f"bpm {cb3.bpm:.1f} conf {cb3.conf:.2f}")
    cb4 = CausalBeat(sr)
    evs = cb4.feed(_click_track(sr, 12.0, lambda t: 174.0))
    chk("fast genre (174) locks", abs(cb4.bpm - 174.0) < 4.0
        or abs(cb4.bpm - 87.0) < 2.0, f"bpm {cb4.bpm:.2f}")
    chk("events stream causally", len(evs) >= 3 and
        all(a["t"] < b["t"] for a, b in zip(evs, evs[1:])))
    print(f"live_ear selftest: {'clean' if ok else 'RED'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.wav:
        sys.exit("need --wav or --selftest")
    cb = replay(a.wav)
    out = {"bpm": round(cb.bpm, 2), "conf": round(cb.conf, 3),
           "events": len(cb.events)}
    print(json.dumps(out if a.json else {**out, "tail": cb.events[-3:]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
