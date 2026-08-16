#!/usr/bin/env python3
"""PATCH PROOF BATTERY — wave 55 (r-17 items 020/136/137): the minted
archetype voices are MACHINE-VERIFIABLE physics, not vibes. Renders
each voice solo through the real engine (JIT — unregistered .dsp) and
asserts the r-17 spectral invariants:

  supersaw_jp  >=5 distinct partial peaks clustered around f0; the
               f0-tracking HPF leaves sub-f0 energy >=25dB down;
               0 clipped samples at vel 1.0 solo (headroom law)
  fm2op        integer ratio -> HARMONIC comb (sidebands on k*f0);
               ratio 3.5 -> INHARMONIC energy off the comb (r-17 rule)
  reese        beat rate f0*(2^(cents/1200)-1): the 4-saw stack's
               envelope pulses at the detune-predicted rate
  kick_808     the exponential pitch envelope is REAL: attack-window
               f0 sits >= 1.3x the tail-window f0
"""
import json
import math
import os
import subprocess
import sys
import tempfile
import wave as wavmod

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def read_wav(path):
    w = wavmod.open(path, "rb")
    sr, sw, ch, n = (w.getframerate(), w.getsampwidth(), w.getnchannels(),
                     w.getnframes())
    raw = w.readframes(n)
    w.close()
    if sw == 3:                     # 24-bit m1 native — the 1.5x trap
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
             | (a[:, 2].astype(np.int32) << 16))
        x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) \
            / 8388608.0
    else:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    return x.reshape(-1, ch).mean(axis=1), sr


def render(tag, source_id, notes, automation=None, bars=2):
    tmp = tempfile.mkdtemp(prefix=f"pp_{tag}_")
    sj = os.path.join(tmp, "s.json")
    wv = os.path.join(tmp, "s.wav")
    tr = {"name": "v", "source": {"id": source_id}, "gainDb": 0.0,
          "notes": notes}
    if automation:
        tr["automation"] = automation
    song = {"version": 2, "bpm": 120, "lengthBars": bars,
            "masterGainDb": 0.0, "master": [], "tracks": [tr]}
    json.dump(song, open(sj, "w"))
    r = subprocess.run([M1, "render", sj, wv], capture_output=True,
                       text=True, timeout=600)
    if r.returncode != 0 or not os.path.exists(wv):
        return None, None, (r.stdout + r.stderr)[-300:]
    x, sr = read_wav(wv)
    return x, sr, None


def spectrum(x, sr, t0, t1):
    seg = x[int(t0 * sr):int(t1 * sr)]
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    return spec, np.fft.rfftfreq(len(seg), 1.0 / sr)


# ------------------------------------------------------ supersaw_jp (020)
A3 = 220.0
x, sr, err = render("ssjp", "supersaw_jp",
                    [{"start": 0, "len": 6, "pitch": 57, "vel": 127}],
                    automation=[{"target": "source.detune",
                                 "points": [{"beat": 0.0, "v": 0.9}]}])
check("supersaw_jp renders via JIT", x is not None, str(err))
if x is not None:
    clipped = int((np.abs(x) >= 0.999).sum())
    check("headroom law: 0 clipped at vel 1.0 solo", clipped == 0,
          f"clipped={clipped}")
    spec, freqs = spectrum(x, sr, 0.5, 2.5)
    zone = (freqs > A3 * 0.82) & (freqs < A3 * 1.22)
    zs, zf = spec[zone], freqs[zone]
    floor = np.median(zs)
    peaks = [zf[i] for i in range(2, len(zs) - 2)
             if zs[i] > zs[i - 1] and zs[i] > zs[i + 1]
             and zs[i] > zs[i - 2] and zs[i] > zs[i + 2]
             and zs[i] > 12 * floor]
    check("Szabo layout: >=5 distinct partials cluster around f0 "
          "(7 detuned saws)", len(peaks) >= 5, f"peaks={len(peaks)}")
    sub = spec[(freqs > 30) & (freqs < A3 * 0.55)]
    main = spec[zone].max()
    ratio_db = 20 * math.log10(max(sub.max(), 1e-12) / main)
    check("the f0-tracking HPF: sub-f0 energy >=25dB down",
          ratio_db <= -25.0, f"{ratio_db:.1f}dB")

# ------------------------------------------------------------ fm2op (136)
x, sr, err = render("fm2h", "fm2op",
                    [{"start": 0, "len": 6, "pitch": 57, "vel": 110}])
check("fm2op renders via JIT", x is not None, str(err))
if x is not None:
    spec, freqs = spectrum(x, sr, 0.15, 1.5)

    def comb_energy(f0, spec, freqs, kmax=12):
        on = off = 0.0
        for k in range(1, kmax + 1):
            f = f0 * k
            if f > freqs[-1] * 0.9:
                break
            on += spec[(freqs > f * 0.985) & (freqs < f * 1.015)].sum()
            fo = f0 * (k + 0.5)
            off += spec[(freqs > fo * 0.985) & (freqs < fo * 1.015)].sum()
        return on, off
    on, off = comb_energy(A3, spec, freqs)
    check("integer ratio 1:1 = HARMONIC comb (on-comb >> half-comb)",
          on > 8 * off, f"on={on:.0f} off={off:.0f}")

x2, sr2, err = render(
    "fm2b", "fm2op",
    [{"start": 0, "len": 6, "pitch": 57, "vel": 110}],
    automation=[{"target": "source.ratio",
                 "points": [{"beat": 0.0, "v": 3.5}]},
                {"target": "source.index_decay",
                 "points": [{"beat": 0.0, "v": 1.2}]}])
check("fm2op ratio=3.5 renders (zone via automation)", x2 is not None,
      str(err))
if x2 is not None:
    spec2, freqs2 = spectrum(x2, sr2, 0.15, 1.5)
    on2, off2 = comb_energy(A3, spec2, freqs2)
    check("non-integer ratio 3.5 = INHARMONIC (energy leaves the comb — "
          "the r-17 bell rule)", on2 < 4 * off2,
          f"on={on2:.0f} off={off2:.0f}")

# ------------------------------------------------------------ reese
CENTS_EQ = 0.015                 # reese.dsp detune 0.015 ~ 25.8 cents
x, sr, err = render("reese", "reese",
                    [{"start": 0, "len": 7.5, "pitch": 33, "vel": 100}],
                    bars=2)
check("reese renders", x is not None, str(err))
if x is not None:
    f0 = 440.0 * 2 ** ((33 - 69) / 12.0)          # A1 = 55Hz
    f_beat = f0 * CENTS_EQ                        # f0*(1+d) - f0
    seg = x[int(0.4 * sr):int(3.4 * sr)]
    env = np.abs(seg)
    k = max(int(sr * 0.02), 1)
    env = np.convolve(env, np.ones(k) / k, mode="same")[::k]
    env = env - env.mean()
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    sr_e = sr / k
    lo, hi = int(sr_e / (f_beat * 1.6)), int(sr_e / max(f_beat * 0.6, 0.1))
    lag = lo + int(np.argmax(ac[lo:min(hi, len(ac) - 1)]))
    measured = sr_e / lag
    check("reese beat rate matches detune physics "
          f"(predict {f_beat:.2f}Hz)",
          0.5 * f_beat <= measured <= 1.7 * f_beat,
          f"measured {measured:.2f}Hz")

# ------------------------------------------------------------ kick_808
x, sr, err = render("k808", "kick_808",
                    [{"start": float(b), "len": 0.9, "pitch": 36,
                      "vel": 120} for b in range(4)], bars=1)
check("kick_808 renders", x is not None, str(err))
if x is not None:
    def f0_of(t0, t1):
        spec, freqs = spectrum(x, sr, t0, t1)
        band = (freqs > 25) & (freqs < 300)
        return float(freqs[band][np.argmax(spec[band])])
    fa = f0_of(0.002, 0.05)          # the attack window
    ft = f0_of(0.18, 0.45)           # the settled tail
    check("808 pitch envelope is REAL (attack f0 >= 1.3x tail f0)",
          fa >= 1.3 * ft, f"attack {fa:.0f}Hz tail {ft:.0f}Hz")

print()
if FAILS:
    print(f"patch_proof_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("patch_proof_battery: ALL GREEN")
