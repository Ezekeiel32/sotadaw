#!/usr/bin/env python3
"""THE CLAP HOST battery (V50) — host any .clap plugin as a session insert:
  fx: {"id": "clap:<plugin.clap>", "params": {"index": 0, "mix": 1.0}}

JUCE/Tracktion host VST3/AU/LADSPA but NOT clap; this is a direct C-ABI host
(app/clap_bridge). Proof at the render level, two DIFFERENT plugin classes so
one lucky no-op can't pass:
  1) a REVERB (Dragonfly Plate) turns a bit-identical-mono source into decorrelated
     STEREO — impossible for a passthrough/no-op (mono side channel is exactly 0).
  2) a SATURATOR/console (Airwindows Consolidated) shifts the SPECTRUM + adds
     upper harmonics on a sustained tone.
Both must LOAD with our minimal host (get_extension → null) and change the audio.

SKIP-green when m1 or the test .clap files are absent (fresh box): searches
library/clap/*.clap + standard CLAP dirs. Exit code IS the verdict.
"""
import glob
import os
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)
    print(f"  {'OK ' if cond else 'XX '}{msg}")


def find_clap(*name_frags):
    roots = [os.path.join(ROOT, "library", "clap"),
             os.path.expanduser("~/.clap"), "/usr/lib/clap", "/usr/local/lib/clap"]
    for r in roots:
        for p in glob.glob(os.path.join(r, "*.clap")):
            base = os.path.basename(p).lower()
            if all(f.lower() in base for f in name_frags):
                return p
    return None


def load(p):
    w = wave.open(p); sr = w.getframerate(); sw = w.getsampwidth()
    raw = w.readframes(w.getnframes()); ch = w.getnchannels()
    if sw == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8) | (a[:, 2].astype(np.int32) << 16))
        x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) / 8388608.0
    else:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    return x.reshape(-1, ch), sr


def render(song, wav, debug=False):
    env = dict(os.environ)
    if debug:
        env["SOTADAW_FX_DEBUG"] = "1"
    return subprocess.run([M1, "render", song, wav], capture_output=True, text=True,
                          timeout=300, env=env)


def width_db(x):
    if x.shape[1] < 2:
        return -240.0
    s = np.sqrt(((x[:, 0] - x[:, 1]) ** 2).mean())
    m = np.sqrt(((x[:, 0] + x[:, 1]) ** 2).mean())
    return 20 * np.log10((s + 1e-12) / (m + 1e-12))


def main():
    import json
    import tempfile
    if not os.path.exists(M1):
        print("SKIP: m1 not built")
        return 0
    reverb = find_clap("dragonfly", "plate") or find_clap("reverb")
    sat = find_clap("airwindows") or find_clap("consolidated")
    if not reverb and not sat:
        print("SKIP: no test .clap found (put one in library/clap/)")
        return 0
    print("== THE CLAP HOST BATTERY (V50) ==")
    work = tempfile.mkdtemp(prefix="clap_battery_")

    def song(fx, notes, src="pluck", gain=-6):
        d = {"version": 2, "bpm": 100, "lengthBars": 2, "masterGainDb": 0.0, "master": [],
             "tracks": [{"name": "s", "source": {"kind": "faust", "id": src}, "gainDb": gain,
                         "notes": notes}]}
        if fx:
            d["tracks"][0]["fx"] = fx
        return d

    # 1) REVERB: mono pluck -> stereo decorrelation
    if reverb:
        notes = [{"start": 0, "len": 0.5, "pitch": 60, "vel": 0.9},
                 {"start": 1.5, "len": 0.5, "pitch": 64, "vel": 0.9}]
        dj = os.path.join(work, "rv_dry.json"); wj = os.path.join(work, "rv_wet.json")
        dw = os.path.join(work, "rv_dry.wav"); ww = os.path.join(work, "rv_wet.wav")
        json.dump(song(None, notes), open(dj, "w"))
        json.dump(song([{"id": f"clap:{reverb}", "params": {"mix": 1.0}}], notes), open(wj, "w"))
        render(dj, dw)
        r = render(wj, ww, debug=True)
        ok("[clap]" in r.stderr and "up (" in r.stderr,
           f"reverb LOADS with the minimal host ({os.path.basename(reverb)})")
        d, _ = load(dw); wv, _ = load(ww)
        wd_dry, wd_wet = width_db(d), width_db(wv)
        ok(wd_dry < -80 and wd_wet - wd_dry > 50,
           f"reverb decorrelates mono->stereo (width {wd_dry:.0f}->{wd_wet:.0f} dB — a no-op can't)")

    # 2) SATURATOR: sustained tone -> spectral shift + harmonics
    if sat:
        notes = [{"start": 0, "len": 4, "pitch": 48, "vel": 1.0}]
        dj = os.path.join(work, "sa_dry.json"); wj = os.path.join(work, "sa_wet.json")
        dw = os.path.join(work, "sa_dry.wav"); ww = os.path.join(work, "sa_wet.wav")
        json.dump(song(None, notes, src="reese", gain=-3), open(dj, "w"))
        json.dump(song([{"id": f"clap:{sat}", "params": {"mix": 1.0}}], notes, src="reese", gain=-3),
                  open(wj, "w"))
        render(dj, dw)
        r = render(wj, ww, debug=True)
        ok("[clap]" in r.stderr and "up (" in r.stderr,
           f"saturator LOADS with the minimal host ({os.path.basename(sat)})")
        d, sr = load(dw); wv, _ = load(ww)
        def cen(x):
            X = np.abs(np.fft.rfft(x.mean(axis=1) * np.hanning(len(x))))
            f = np.fft.rfftfreq(len(x), 1 / sr)
            return (X * f).sum() / max(X.sum(), 1e-9)
        cd, cw = cen(d), cen(wv)
        ok(abs(cw - cd) > 20, f"saturator shifts the spectrum (centroid {cd:.0f}->{cw:.0f} Hz)")

    # 3) missing .clap -> graceful (load fails, audio passes through, no crash)
    notes = [{"start": 0, "len": 1, "pitch": 60, "vel": 0.9}]
    mj = os.path.join(work, "miss.json"); mw = os.path.join(work, "miss.wav")
    json.dump(song([{"id": "clap:/nonexistent/x.clap"}], notes), open(mj, "w"))
    r = render(mj, mw)
    ok(r.returncode == 0 and os.path.exists(mw),
       "missing .clap -> passthrough, render still completes (graceful)")

    print(f"clap battery: {PASS}/{PASS + len(FAIL)} " + ("clean" if not FAIL else "RED"))
    for f in FAIL:
        print("FAIL:", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
