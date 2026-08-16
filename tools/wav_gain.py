#!/usr/bin/env python3
"""Pure-gain wav lift for THE UNIVERSAL LOUDNESS PASS's linear region (W117
speed rung). In the region recovery_step itself calls clear of the wall
(dBTP <= -4 after the step), the engine re-render of a +N dB master trim is
mathematically a sample multiply — fx_trim is static dB staging and fx_truepeak
is unity below its ceiling. So do the multiply, atomically, and let analyze2
re-measure the real samples: a ~16s render becomes ~1s with zero prediction.

REFUSES rather than clips: any post-gain sample beyond full scale = error and
the untouched file stays — the caller falls back to the real render through the
real wall. 16-bit and 24-bit (m1's format; the sampwidth=3 law) both handled.

  wav_gain.py <file.wav> <delta_db>     # prints a JSON result line
  wav_gain.py --selftest                # isolated proof
"""
import json
import os
import sys
import wave

import numpy as np


def apply_gain(path, db):
    """Multiply samples by 10^(db/20) in place (atomic tmp+replace).
    -> {"ok": True, "gain_db", "sample_peak_dbfs"} or {"error": why}."""
    g = 10.0 ** (float(db) / 20.0)
    try:
        with wave.open(path, "rb") as w:
            nch, sw, sr = w.getnchannels(), w.getsampwidth(), w.getframerate()
            comp = w.getcomptype()
            raw = w.readframes(w.getnframes())
    except (OSError, wave.Error) as e:
        return {"error": f"unreadable wav: {e}"}
    if comp != "NONE":
        return {"error": f"compressed wav ({comp}) unsupported"}
    if sw == 2:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float64)
        full = 32767.0
    elif sw == 3:
        b = np.frombuffer(raw, dtype=np.uint8)
        if b.size % 3:
            return {"error": "truncated 24-bit frame data"}
        b = b.reshape(-1, 3)
        x = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        x = ((x << 8) >> 8).astype(np.float64)      # sign-extend 24 -> 32
        full = 8388607.0
    else:
        return {"error": f"sampwidth {sw} unsupported (16/24-bit only)"}
    y = x * g
    peak = float(np.max(np.abs(y))) if y.size else 0.0
    if peak > full:
        over = 20.0 * np.log10(max(peak, 1e-9) / full)
        return {"error": f"post-gain samples would clip (+{over:.2f} dBFS over "
                         "full scale) — this lift needs the real wall, render instead"}
    yi = np.rint(y)
    if sw == 2:
        out = yi.astype("<i2").tobytes()
    else:
        yi32 = yi.astype(np.int32)
        out = np.stack([(yi32 & 0xFF).astype(np.uint8),
                        ((yi32 >> 8) & 0xFF).astype(np.uint8),
                        ((yi32 >> 16) & 0xFF).astype(np.uint8)], axis=1).tobytes()
    tmp = path + ".gaintmp"
    try:
        with wave.open(tmp, "wb") as w:
            w.setnchannels(nch)
            w.setsampwidth(sw)
            w.setframerate(sr)
            w.writeframes(out)
        os.replace(tmp, path)
    except OSError as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        return {"error": f"write failed: {e}"}
    return {"ok": True, "gain_db": round(float(db), 3),
            "sample_peak_dbfs": round(20.0 * np.log10(max(peak, 1e-9) / full), 2)}


def _read_peak_db(path):
    with wave.open(path, "rb") as w:
        sw = w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw == 2:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float64)
        full = 32767.0
    else:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        x = ((x << 8) >> 8).astype(np.float64)
        full = 8388607.0
    return 20.0 * np.log10(max(float(np.max(np.abs(x))), 1e-9) / full), sw


def selftest():
    import tempfile
    n, ok = [0], True

    def check(name, cond):
        print(("  PASS " if cond else "  FAIL ") + name)
        if not cond:
            sys.exit(1)
        n[0] += 1

    sr = 44100
    t = np.arange(sr) / sr
    sine = np.sin(2 * np.pi * 220.0 * t)
    with tempfile.TemporaryDirectory() as td:
        for sw, full, tag in ((2, 32767.0, "16-bit"), (3, 8388607.0, "24-bit")):
            p = os.path.join(td, f"t{sw}.wav")
            amp = 10.0 ** (-20.0 / 20.0)             # -20 dBFS peak
            xi = np.rint(sine * amp * full).astype(np.int32)
            with wave.open(p, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(sw)
                w.setframerate(sr)
                if sw == 2:
                    w.writeframes(xi.astype("<i2").tobytes())
                else:
                    w.writeframes(np.stack(
                        [(xi & 0xFF).astype(np.uint8),
                         ((xi >> 8) & 0xFF).astype(np.uint8),
                         ((xi >> 16) & 0xFF).astype(np.uint8)], axis=1).tobytes())
            r = apply_gain(p, 6.0)
            pk, sw2 = _read_peak_db(p)
            check(f"{tag}: +6 lands at -14 dBFS (got {pk:.2f})", abs(pk - -14.0) < 0.05)
            check(f"{tag}: format preserved (sampwidth {sw2})", sw2 == sw)
            check(f"{tag}: result reports ok + peak", r.get("ok") and
                  abs(r["sample_peak_dbfs"] - -14.0) < 0.06)
            before = open(p, "rb").read()
            r2 = apply_gain(p, 30.0)                  # -14 + 30 = would clip
            check(f"{tag}: clipping lift REFUSED", "error" in r2 and "clip" in r2["error"])
            check(f"{tag}: refused lift leaves file untouched",
                  open(p, "rb").read() == before)
            r3 = apply_gain(p, -6.0)
            pk3, _ = _read_peak_db(p)
            check(f"{tag}: negative gain exact (-20, got {pk3:.2f})",
                  r3.get("ok") and abs(pk3 - -20.0) < 0.05)
        bad = os.path.join(td, "x.wav")
        open(bad, "wb").write(b"RIFFjunk")
        check("junk file = honest error", "error" in apply_gain(bad, 3.0))
    print(f"WAV GAIN SELFTEST: {n[0]}/13 PASS")
    return 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    res = apply_gain(sys.argv[1], float(sys.argv[2]))
    print(json.dumps(res))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
