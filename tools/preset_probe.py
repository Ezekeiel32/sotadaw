#!/usr/bin/env python3
"""preset_probe.py <plugin> <name> — render (and cache) a staged audition of a sound.

Prints the wav path on success. Cache: songs/.preset_previews/<sha1>.wav.
The UI's single-click audition shells this; first click renders (~2s),
repeats are instant. plugin "__faust__" auditions instruments/<name>.dsp.

v2 THE STAGED EAR (2026-07-11): raw m1 renders hit 0 dBFS — every click was a
horrible full-scale crack through the shared device ("generic blast for all
sounds"). Previews are now post-staged: onset-trimmed, peak-normalized to
-6 dBFS (both directions, +18 dB boost cap), 4 ms fade-in / 80 ms fade-out,
16-bit. The cache key carries the version so v1 blasts regenerate.
"""
import hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
CACHE = os.path.join(ROOT, "songs", ".preset_previews")
VERSION = "v2"


def stage(wav):
    """Trim + normalize + fade the raw render in place. Fail-open: a preview
    beats no preview, so any error leaves the raw file standing."""
    try:
        import numpy as np
        import soundfile as sf
        x, sr = sf.read(wav, always_2d=True)
        mono = np.abs(x).max(axis=1)
        hot = np.where(mono > 10 ** (-50 / 20))[0]          # content above -50 dBFS
        if len(hot) == 0:
            return
        a = max(0, int(hot[0]) - int(0.005 * sr))           # 5 ms pre-onset
        b = min(len(x), int(hot[-1]) + int(0.1 * sr))       # 100 ms past the last life
        b = min(b, a + int(2.5 * sr))                       # auditions stay short
        x = x[a:b].copy()
        peak = float(np.abs(x).max())
        if peak > 1e-6:
            x = x * min(10 ** (-6 / 20) / peak, 10 ** (18 / 20))   # to -6 dBFS, boost-capped
        fi = min(int(0.004 * sr), len(x))
        fo = min(int(0.08 * sr), len(x))
        if fi > 0:
            x[:fi] *= np.linspace(0.0, 1.0, fi)[:, None]
        if fo > 0:
            x[-fo:] *= np.linspace(1.0, 0.0, fo)[:, None]
        sf.write(wav, x, sr, subtype="PCM_16")
    except Exception:
        pass


def main(plugin, name):
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(f"{VERSION}|{plugin}|{name}".encode()).hexdigest()[:16]
    wav = os.path.join(CACHE, f"{key}.wav")
    if os.path.exists(wav) and os.path.getsize(wav) > 20000:
        print(wav)
        return 0
    # build the source via the same rails the tools use
    if plugin == "__faust__":
        if not os.path.exists(os.path.join(ROOT, "instruments", f"{name}.dsp")):
            return 1
        track = {"name": "t", "source": {"kind": "faust", "id": name}, "gainDb": 0,
                 "notes": [{"start": 0, "len": 1.6, "pitch": 57, "vel": 0.9}]}
    elif "Effects" in plugin:
        from surgefx_presets import synth_state, scan
        e = next((x for x in scan() if x["name"] == name), None)
        if e is None: return 1
        import json as _j
        tables = _j.load(open(os.path.join(ROOT, "tools", "surgefx_tables.json")))
        blob = os.path.join(CACHE, f"{key}.blob")
        open(blob, "wb").write(synth_state(e["path"], tables))
        track = {"name": "t", "source": {"kind": "faust", "id": "pluck"}, "gainDb": 0,
                 "fx": [{"id": "vst3:Surge XT Effects", "preset": blob}],
                 "notes": [{"start": 0, "len": 1.0, "pitch": 69, "vel": 0.9}]}
    elif "Surge" in plugin:
        from surge_presets import scan, wrap_fxp
        e = next((x for x in scan() if x["name"] == name), None)
        if e is None: return 1
        blob = os.path.join(CACHE, f"{key}.blob")
        open(blob, "wb").write(wrap_fxp(e["path"]))
        track = {"name": "t", "source": {"kind": "vst3", "plugin": "Surge XT", "preset": blob},
                 "gainDb": 0, "notes": [{"start": 0, "len": 1.6, "pitch": 57, "vel": 0.9}]}
    else:
        mod = "tal_presets" if "TAL" in plugin else "odin_presets"
        m = __import__(mod)
        e = next((x for x in m.scan() if x["name"] == name), None)
        if e is None: return 1
        track = {"name": "t", "source": {"kind": "vst3", "plugin": e["plugin"],
                                         "params": m.parse_preset(e["path"])},
                 "gainDb": 0, "notes": [{"start": 0, "len": 1.6, "pitch": 57, "vel": 0.9}]}
    song = {"version": 2, "bpm": 120.0, "lengthBars": 1, "masterGainDb": 0.0, "tracks": [track]}
    sj = os.path.join(CACHE, f"{key}.json")
    json.dump(song, open(sj, "w"))
    tmp = os.path.join(CACHE, f"{key}.part.wav")   # never let a killed render poison the cache
    r = subprocess.run([M1, "render", sj, tmp], capture_output=True, text=True, timeout=180)
    os.remove(sj)
    if "ok=1" not in r.stdout + r.stderr or not os.path.exists(tmp):
        return 1
    stage(tmp)
    os.replace(tmp, wav)
    print(wav)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
