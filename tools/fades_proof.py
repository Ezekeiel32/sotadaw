#!/usr/bin/env python3
"""V46 CLIP FADES proof — the schema's fadeInBeats/fadeOutBeats must SHAPE THE AUDIO.

Renders the same audio clip twice through m1: bare vs 4-beat fade-in + 4-beat
fade-out (linear). Asserts on the rendered envelopes:

  F1 both render ok, same duration
  F2 fade-in head is quieter: first-beat RMS drops >= 6 dB vs the bare render
  F3 fade-out tail is quieter: last-beat RMS drops >= 6 dB vs the bare render
  F4 the middle is untouched (|delta| < 1.5 dB) — fades are EDGE surgery
  F5 faded render still clean (clipped == 0)

usage: fades_proof.py [source.wav]   (default songs/_lg_house.wav)
Prints FADES_JSON; exit 0 = green.
"""
import json, os, subprocess, sys, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
sys.path.insert(0, os.path.join(ROOT, "tools"))

BPM = 120.0
BARS = 4                       # 16 beats; fades take the outer 4+4


def read_mono(path):
    import numpy as np
    with wave.open(path, "rb") as w:
        sw, n, sr, ch = w.getsampwidth(), w.getnframes(), w.getframerate(), w.getnchannels()
        raw = w.readframes(n)
    if sw == 3:   # m1's 24-bit truth
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        x = (b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16))
        x = (x - ((x >> 23) << 24)).astype(np.float64) / 8388608.0
    else:
        dt = {2: "int16", 4: "int32"}[sw]
        import numpy as _np
        x = _np.frombuffer(raw, dtype=dt).astype(_np.float64) / float(1 << (8 * sw - 1))
    return sr, x.reshape(-1, ch).mean(axis=1)


def seg_rms_db(x, sr, t0, t1):
    import numpy as np
    seg = x[int(t0 * sr): int(t1 * sr)]
    return 20.0 * np.log10(float(np.sqrt(np.mean(seg * seg)) + 1e-12))


def make(path, src_rel, fades):
    clip = {"file": src_rel, "startBeat": 0, "lengthBeats": BARS * 4.0, "offsetSec": 0.0}
    if fades:
        clip.update({"fadeInBeats": 4.0, "fadeOutBeats": 4.0, "fadeCurve": "linear"})
    song = {"version": 2, "bpm": BPM, "lengthBars": BARS, "masterGainDb": 0,
            "master": [{"type": "faustfx", "id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": [{"name": "clip", "source": {"kind": "audio"}, "gainDb": 0.0,
                        "notes": [], "audioClips": [clip]}]}
    json.dump(song, open(path, "w"), indent=1)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SONGS, "_lg_house.wav")
    if not os.path.exists(src):
        print(f"no source wav {src}", file=sys.stderr)
        return 2
    src_rel = os.path.relpath(src, ROOT)
    checks, fails = [], []

    def check(nm, ok, detail):
        checks.append({"name": nm, "ok": bool(ok), "detail": detail})
        if not ok:
            fails.append(nm)

    paths = {}
    for tag, fades in (("bare", False), ("faded", True)):
        sj = os.path.join(SONGS, f"_fades_{tag}.json")
        wv = os.path.join(SONGS, f"_fades_{tag}.wav")
        make(sj, src_rel, fades)
        r = subprocess.run([M1, "render", sj, wv], capture_output=True, text=True, timeout=600)
        ok = "ok=1" in (r.stdout + r.stderr) and os.path.exists(wv)
        check(f"render_{tag}", ok, "ok" if ok else (r.stdout + r.stderr)[-250:])
        paths[tag] = wv
    if fails:
        print("FADES_JSON " + json.dumps({"pass": False, "checks": checks}))
        return 1

    sr_b, xb = read_mono(paths["bare"])
    sr_f, xf = read_mono(paths["faded"])
    beat = 60.0 / BPM
    check("durations_match", abs(len(xb) / sr_b - len(xf) / sr_f) < 0.05,
          {"bare_s": round(len(xb) / sr_b, 3), "faded_s": round(len(xf) / sr_f, 3)})

    head_b, head_f = seg_rms_db(xb, sr_b, 0, beat), seg_rms_db(xf, sr_f, 0, beat)
    check("fade_in_shapes_head", head_b - head_f >= 6.0,
          {"bare_db": round(head_b, 2), "faded_db": round(head_f, 2)})

    end = BARS * 4 * beat
    tail_b = seg_rms_db(xb, sr_b, end - beat, end)
    tail_f = seg_rms_db(xf, sr_f, end - beat, end)
    check("fade_out_shapes_tail", tail_b - tail_f >= 6.0,
          {"bare_db": round(tail_b, 2), "faded_db": round(tail_f, 2)})

    mid_b = seg_rms_db(xb, sr_b, end / 2 - beat, end / 2 + beat)
    mid_f = seg_rms_db(xf, sr_f, end / 2 - beat, end / 2 + beat)
    check("middle_untouched", abs(mid_b - mid_f) < 1.5,
          {"bare_db": round(mid_b, 2), "faded_db": round(mid_f, 2)})

    from analyze2 import analyze
    a = analyze(paths["faded"])
    check("faded_clean", a["clipped_samples"] == 0, {"clipped": a["clipped_samples"]})

    result = {"pass": not fails, "failing": fails, "checks": checks}
    print("FADES_JSON " + json.dumps(result))
    if not fails:
        for tag in paths:
            for ext in (".json", ".wav"):
                p = os.path.join(SONGS, f"_fades_{tag}{ext}")
                if os.path.exists(p):
                    os.remove(p)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
