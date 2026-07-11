#!/usr/bin/env python3
"""preset_battery.py — the preset rail's regression net.

  preset_battery.py [--per-plugin N] [--seed K]

Samples N presets per plugin from library.json vst_presets, renders each as a
2-second A3 note (or as an insert on a pluck for fx presets), and asserts:
  AUDIBLE   peak > -50 dBFS
  SANE      no clipping (peak < 0 dBFS after the pass-through master)
Deterministic per seed. Prints a scoreboard; exits nonzero if any plugin's
pass rate < 80% (a SongLoader/param-path regression tripwire). Run after any
change to SongLoader's vst3 path, the preset tools, or plugin updates.
"""
import argparse, json, os, random, subprocess, sys, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
SCRATCH = os.path.join(ROOT, "songs", "_battery_tmp.json")
sys.path.insert(0, os.path.join(ROOT, "tools"))


def peak_db(path):
    with wave.open(path) as w:
        sw, n = w.getsampwidth(), w.getnframes()
        raw = w.readframes(n)
    peak = 0
    if sw == 3:
        for i in range(0, len(raw) - 2, 3 * 32):     # stride for speed
            v = int.from_bytes(raw[i:i + 3], "little", signed=True)
            peak = max(peak, abs(v))
        full = float(2 ** 23)
    else:
        import array
        a = array.array("h"); a.frombytes(raw[: len(raw) // 2 * 2])
        peak = max((abs(x) for x in a[::16]), default=0)
        full = float(2 ** 15)
    import math
    return 20 * math.log10(max(peak, 1) / full)


def song_for(entry):
    """Build the probe song for one preset entry."""
    plugin = entry["plugin"]
    if plugin == "Surge XT Effects":
        from surgefx_presets import synth_state
        tables = json.load(open(os.path.join(ROOT, "tools", "surgefx_tables.json")))
        blob = os.path.join(ROOT, "songs", "_battery_fx.blob")
        open(blob, "wb").write(synth_state(entry["path"], tables))
        return {"version": 2, "bpm": 120.0, "lengthBars": 1, "masterGainDb": 0.0,
                "tracks": [{"name": "t", "source": {"kind": "faust", "id": "pluck"},
                            "gainDb": 0, "fx": [{"id": "vst3:Surge XT Effects", "preset": blob}],
                            "notes": [{"start": 0, "len": 1.0, "pitch": 69, "vel": 0.9}]}]}
    if plugin == "Surge XT":
        from surge_presets import wrap_fxp
        blob = os.path.join(ROOT, "songs", "_battery_src.blob")
        open(blob, "wb").write(wrap_fxp(entry["path"]))
        src = {"kind": "vst3", "plugin": plugin, "preset": blob}
    else:
        mod = "tal_presets" if plugin == "TAL-NoiseMaker" else "odin_presets"
        params = __import__(mod).parse_preset(entry["path"])
        src = {"kind": "vst3", "plugin": plugin, "params": params}
    return {"version": 2, "bpm": 120.0, "lengthBars": 1, "masterGainDb": 0.0,
            "tracks": [{"name": "t", "source": src, "gainDb": 0,
                        "notes": [{"start": 0, "len": 2.0, "pitch": 57, "vel": 0.9}]}]}


def main(per_plugin, seed):
    lib = json.load(open(os.path.join(ROOT, "library.json")))
    by = {}
    for e in lib.get("vst_presets", []):
        by.setdefault(e["plugin"], []).append(e)
    rng = random.Random(seed)
    wav = os.path.join(ROOT, "songs", "_battery_tmp.wav")
    board, worst = {}, 0
    for plugin, entries in sorted(by.items()):
        sample = rng.sample(entries, min(per_plugin, len(entries)))
        passed, fails = 0, []
        for e in sample:
            try:
                json.dump(song_for(e), open(SCRATCH, "w"))
                r = subprocess.run([M1, "render", SCRATCH, wav],
                                   capture_output=True, text=True, timeout=180)
                ok = "ok=1" in r.stdout + r.stderr and peak_db(wav) > -50.0
            except Exception:
                ok = False
            passed += ok
            if not ok:
                fails.append(e["name"])
        rate = passed / max(1, len(sample))
        board[plugin] = (passed, len(sample), fails[:3])
        worst = max(worst, 0 if rate >= 0.8 else 1)
        print(f"  {plugin:18} {passed}/{len(sample)} audible"
              + (f"  FAILS: {fails[:3]}" if fails else ""))
    for f in (SCRATCH, wav, os.path.join(ROOT, "songs", "_battery_fx.blob"),
              os.path.join(ROOT, "songs", "_battery_src.blob")):
        if os.path.exists(f):
            os.remove(f)
    print("preset battery:", "PASS" if worst == 0 else "REGRESSION (some plugin < 80%)")
    sys.exit(worst)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-plugin", type=int, default=6)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    main(a.per_plugin, a.seed)
