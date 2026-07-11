#!/usr/bin/env python3
"""V46 WARP A/B — prove the signalsmith warp rail end-to-end through m1.

Builds two scratch songs around the SAME warped clip (a loop with a known
sourceBpm placed on a song at a different bpm): one on the default hq rail
(signalsmith when the engine patch is in), one forced legacy ("stretch":"fast"
= SoundTouch). Renders both, then asserts the rail is REAL and SANE:

  A1 both render ok and are non-silent
  A2 durations match each other (same musical length through both stretchers)
  A3 warp actually warped: rendered beat grid ~= song bpm, not the file's
     (onset spacing within 6% of the song-bpm beat period on the hq render)
  A4 levels comparable (|rms_hq - rms_fast| <= 4.5 dB; stretchers differ, but
     a collapse/blowup means the adapter's gain path is wrong)
  A5 hq render is clean (clipped == 0)

Exit 0 = all green (prints WARP_AB_JSON line). Ears: keep both wavs around —
the felt A/B (SoundTouch warble vs signalsmith) is the actual V46 payoff.

usage: warp_ab.py [loop.wav] [--keep]
       default loop: songs/_lg_house.wav (loop_gen house DNA render, 128bpm-ish)
"""
import json, os, subprocess, sys, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
sys.path.insert(0, os.path.join(ROOT, "tools"))

SONG_BPM = 100.0            # deliberately far from the loop's native tempo
SRC_BPM = 128.0             # the claim we make about the loop file
BARS = 4                    # 16 beats of warped material


def read_wav(path):
    with wave.open(path, "rb") as w:
        sw, n, sr, ch = w.getsampwidth(), w.getnframes(), w.getframerate(), w.getnchannels()
        raw = w.readframes(n)
    if sw == 3:  # m1 renders 24-bit — the documented trap
        import numpy as np
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        x = (b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16))
        x = (x - ((x >> 23) << 24)).astype(np.float64) / 8388608.0
    else:
        import numpy as np
        dt = {1: np.int8, 2: np.int16, 4: np.int32}[sw]
        x = np.frombuffer(raw, dtype=dt).astype(np.float64) / float(1 << (8 * sw - 1))
    x = x.reshape(-1, ch).mean(axis=1)
    return sr, x


def rms_db(x):
    import numpy as np
    r = float(np.sqrt(np.mean(x * x)) + 1e-12)
    return 20.0 * np.log10(r)


def onset_spacings(sr, x):
    """Median spacing between energy onsets (seconds) — the rendered beat grid."""
    import numpy as np
    hop = 512
    n = (len(x) // hop) * hop
    e = np.sqrt(np.mean(x[:n].reshape(-1, hop) ** 2, axis=1) + 1e-12)
    flux = np.maximum(0, np.diff(e))
    if flux.max() <= 0:
        return []
    thr = np.percentile(flux, 92)
    idx = np.where(flux > thr)[0]
    if len(idx) == 0:
        return []
    # collapse runs closer than 120ms into single onsets
    onsets, last = [], -10.0
    for i in idx:
        t = (i * hop) / sr
        if t - last > 0.12:
            onsets.append(t)
            last = t
    return [b - a for a, b in zip(onsets, onsets[1:])]


def make_song(path, loop_rel, stretch):
    clip = {"file": loop_rel, "startBeat": 0, "lengthBeats": BARS * 4.0,
            "offsetSec": 0.0, "sourceBpm": SRC_BPM}
    if stretch:
        clip["stretch"] = stretch
    song = {"version": 2, "bpm": SONG_BPM, "lengthBars": BARS, "masterGainDb": 0,
            "master": [{"type": "faustfx", "id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": [{"name": "warped", "source": {"kind": "audio"}, "gainDb": 0.0,
                        "notes": [], "audioClips": [clip]}]}
    json.dump(song, open(path, "w"), indent=1)


def render(sj, wav):
    r = subprocess.run([M1, "render", sj, wav], capture_output=True, text=True, timeout=600)
    ok = "ok=1" in (r.stdout + r.stderr) and os.path.exists(wav)
    return ok, (r.stdout + r.stderr)[-300:]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    loop = args[0] if args else os.path.join(ROOT, "songs", "_lg_house.wav")
    if not os.path.exists(loop):
        print(f"no loop wav at {loop}", file=sys.stderr)
        return 2
    loop_rel = os.path.relpath(loop, ROOT)
    out = os.path.join(ROOT, "songs")
    checks, fails = [], []

    def check(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
        if not ok:
            fails.append(name)

    paths = {}
    for tag, stretch in (("hq", ""), ("fast", "fast")):
        sj = os.path.join(out, f"_warp_ab_{tag}.json")
        wv = os.path.join(out, f"_warp_ab_{tag}.wav")
        make_song(sj, loop_rel, stretch)
        ok, log = render(sj, wv)
        check(f"render_{tag}", ok, log if not ok else "ok")
        paths[tag] = wv
    if fails:
        print("WARP_AB_JSON " + json.dumps({"pass": False, "checks": checks}))
        return 1

    sr_h, x_h = read_wav(paths["hq"])
    sr_f, x_f = read_wav(paths["fast"])
    rms_h, rms_f = rms_db(x_h), rms_db(x_f)
    check("nonsilent", rms_h > -50 and rms_f > -50, {"rms_hq": round(rms_h, 2), "rms_fast": round(rms_f, 2)})
    dur_h, dur_f = len(x_h) / sr_h, len(x_f) / sr_f
    check("durations_match", abs(dur_h - dur_f) < 0.05, {"hq_s": round(dur_h, 3), "fast_s": round(dur_f, 3)})
    check("levels_comparable", abs(rms_h - rms_f) <= 4.5, {"delta_db": round(rms_h - rms_f, 2)})

    beat = 60.0 / SONG_BPM
    sp = onset_spacings(sr_h, x_h)
    # accept the beat period or common subdivisions (halves count twice etc.)
    good = [s for s in sp if any(abs(s - beat * m) < 0.06 * beat * m for m in (0.25, 0.5, 1.0, 2.0))]
    warped_ok = len(sp) >= 4 and len(good) >= int(0.6 * len(sp))
    check("warped_to_song_grid", warped_ok,
          {"beat_s": round(beat, 3), "spacings": [round(s, 3) for s in sp[:8]],
           "grid_hits": f"{len(good)}/{len(sp)}"})

    from analyze2 import analyze
    a = analyze(paths["hq"])
    check("hq_clean", a["clipped_samples"] == 0, {"clipped": a["clipped_samples"],
                                                  "dbtp": a["true_peak_dbtp"]})

    result = {"pass": not fails, "failing": fails, "checks": checks,
              "ears": {k: os.path.relpath(v, ROOT) for k, v in paths.items()}}
    print("WARP_AB_JSON " + json.dumps(result))
    if "--keep" not in sys.argv and not fails:
        for tag in paths:
            os.remove(os.path.join(out, f"_warp_ab_{tag}.json"))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
