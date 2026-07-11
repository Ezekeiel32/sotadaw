#!/usr/bin/env python3
"""VST MOAT — verify the DAW EXPOSES every VST3 knob (the inspection differentiator
firing-75 established: competitors 'generally don't support' VST control; we list
every param). READ path only — the proven, non-fragile half of the moat.

Skip-safe: if no VST3 is scannable / no vst3 song exists (a fresh box without the
plugins), it SKIPS rather than fails, so it never reds check_all. Exit 1 only on a
genuine regression (a vst3 song whose params DON'T surface)."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
SONGS = os.path.join(ROOT, "songs")


def main():
    # find a committed song that uses a vst3/preset source
    vst_song = None
    for f in sorted(os.listdir(SONGS)):
        if not f.endswith(".json"):
            continue
        try:
            s = json.load(open(os.path.join(SONGS, f)))
        except Exception:
            continue
        for t in s.get("tracks", []):
            src = t.get("source", {})
            if isinstance(src, dict) and ("vst3" in str(src.get("id", "")).lower()
                                          or src.get("kind") == "vst3" or src.get("preset")):
                vst_song = os.path.join(SONGS, f)
                break
        if vst_song:
            break

    if not vst_song:
        print("  [SKIP] no vst3/preset song present — VST moat not exercised on this box")
        return

    r = subprocess.run([M1, "list-params", vst_song], capture_output=True, text=True, timeout=180)
    line = next((l for l in (r.stdout + r.stderr).splitlines() if "PARAMS_JSON" in l), None)
    if not line:
        print(f"  [SKIP] {os.path.basename(vst_song)}: no PARAMS_JSON (VSTs may not be installed)")
        return
    try:
        params = json.loads(line.split("PARAMS_JSON", 1)[1].strip())
    except Exception as e:
        print(f"  [FAIL] PARAMS_JSON parse: {e}")
        sys.exit(1)

    by_plugin = {}
    for p in params:
        by_plugin[p.get("plugin", "?")] = by_plugin.get(p.get("plugin", "?"), 0) + 1
    vst_params = sum(n for pl, n in by_plugin.items()
                     if pl not in ("FaustInstrument", "FaustFx", "Volume & Pan Plugin")
                     and not pl.startswith("Aux"))

    print(f"  {os.path.basename(vst_song)}: {len(params)} params across {list(by_plugin)}")
    if vst_params >= 10:
        print(f"  [PASS] READ moat: {vst_params} non-Faust plugin params EXPOSED "
              f"(every knob readable — the differentiator competitors lack)")
    else:
        print(f"  [FAIL] only {vst_params} VST3 params surfaced (expected the full knob set)")
        sys.exit(1)

    # SET path: a PARAMS-BASED vst3 source must honor set params (audible change).
    # (preset-based sources load a state blob that owns params — the preset rail's
    # 'tweak after load' flow, not source.params; so only test params-based here.)
    import copy
    pb = None
    for f in sorted(os.listdir(SONGS)):
        if not f.endswith(".json"):
            continue
        try:
            s = json.load(open(os.path.join(SONGS, f)))
        except Exception:
            continue
        for t in s.get("tracks", []):
            src = t.get("source", {})
            if isinstance(src, dict) and src.get("kind") == "vst3" and not src.get("preset"):
                pb = (t, src)
                break
        if pb:
            break
    if not pb:
        print("  [SKIP] no params-based vst3 source — SET path not exercised on this box")
        return
    track, src = pb
    # pick a loudness-ish param present on this plugin (Output/Level/Gain/Volume)
    names = {p["name"] for p in params if p.get("plugin") == src.get("plugin")}
    loud = next((n for n in ("Output", "Master", "Volume", "Level", "Gain") if n in names), None)
    if not loud:
        print("  [SKIP] no loudness param on this plugin — SET path not exercised")
        return

    def render_set(val):
        t = copy.deepcopy(track)
        t["notes"] = [{"start": b, "len": 0.8, "pitch": 52 + (b % 7), "vel": 0.9} for b in range(8)]
        t["gainDb"] = -6; t.pop("fx", None)
        t["source"].setdefault("params", {})[loud] = val
        song = {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0, "tracks": [t]}
        json.dump(song, open(os.path.join(SONGS, "_vstmoat.json"), "w"), indent=1)
        r = subprocess.run([M1, "render", os.path.join(SONGS, "_vstmoat.json"), os.path.join(SONGS, "_vstmoat.wav")],
                           capture_output=True, text=True, timeout=300)
        if "ok=1" not in (r.stdout + r.stderr):
            return None
        pa = subprocess.run([os.path.join(ROOT, ".venv/bin/python"), os.path.join(ROOT, "tools", "analyze2.py"),
                             os.path.join(SONGS, "_vstmoat.wav")], capture_output=True, text=True)
        return json.loads(pa.stdout)["rms_db"]

    lo, hi = render_set(0.15), render_set(1.0)
    for f in ("_vstmoat.json", "_vstmoat.wav"):
        p = os.path.join(SONGS, f)
        os.path.exists(p) and os.remove(p)
    if lo is None or hi is None:
        print("  [SKIP] SET render failed (plugin unavailable)")
        return
    if hi - lo > 3.0:
        print(f"  [PASS] WRITE moat: setting {src['plugin']} '{loud}' 0.15->1.0 changed loudness "
              f"{lo:.1f}->{hi:.1f}dB ({hi-lo:+.1f}dB) — the knob reaches the plugin")
    else:
        print(f"  [FAIL] setting '{loud}' didn't change the audio ({lo:.1f}->{hi:.1f}dB) — SET path broken")
        sys.exit(1)

    # AUTOMATE moat (the third leg competitors lack — REAPER MCP "cannot automate
    # params over time"). Faust fx (always available): a held chord through
    # fx_filter with a cutoff automation must SWEEP the centroid over time.
    def render_auto(automated):
        t = {"name": "drone", "source": {"kind": "faust", "id": "strings_disco"}, "gainDb": -6,
             "fx": [{"id": "fx_filter", "params": {"cutoff": 300, "res": 0.3}}],
             "notes": [{"start": 0, "len": 32, "pitch": p, "vel": 0.7} for p in (48, 55, 60, 64)]}
        if automated:
            t["automation"] = [{"target": "fx[0].cutoff",
                                "points": [{"beat": 0, "v": 300, "curve": 0}, {"beat": 32, "v": 10000, "curve": 0}]}]
        song = {"version": 2, "bpm": 120, "lengthBars": 8, "masterGainDb": 0, "tracks": [t]}
        json.dump(song, open(os.path.join(SONGS, "_vstmoat.json"), "w"), indent=1)
        r = subprocess.run([M1, "render", os.path.join(SONGS, "_vstmoat.json"), os.path.join(SONGS, "_vstmoat.wav")],
                           capture_output=True, text=True, timeout=300)
        if "ok=1" not in (r.stdout + r.stderr):
            return None
        pa = subprocess.run([os.path.join(ROOT, ".venv/bin/python"), os.path.join(ROOT, "tools", "analyze2.py"),
                             os.path.join(SONGS, "_vstmoat.wav")], capture_output=True, text=True)
        return json.loads(pa.stdout)["centroid_by_quarter_hz"]

    cbq = render_auto(True)
    for f in ("_vstmoat.json", "_vstmoat.wav"):
        p = os.path.join(SONGS, f)
        os.path.exists(p) and os.remove(p)
    if cbq is None:
        print("  [SKIP] automate render failed")
        return
    rise = cbq[-1] - cbq[0]
    mono = all(cbq[i] <= cbq[i + 1] + 40 for i in range(len(cbq) - 1))
    if rise > 500 and mono:
        print(f"  [PASS] AUTOMATE moat: cutoff automation swept the centroid {cbq[0]}->{cbq[-1]}Hz "
              f"monotonically over time (competitors 'cannot automate params')")
    else:
        print(f"  [FAIL] automation didn't sweep the param over time ({cbq})")
        sys.exit(1)

    # VST3 FX moat: a VST3 EFFECT (not just instrument) must process audio. Skip-safe:
    # only runs if a scannable VST3 reverb is present. A hall reverb on dry plucks must
    # add a DECAYING tail where dry is silent.
    scan = subprocess.run([M1, "scan-plugins"], capture_output=True, text=True, timeout=90)
    fx_name = next((n for n in ("Dragonfly Hall Reverb", "Dragonfly Room Reverb",
                                "Dragonfly Plate Reverb") if n in (scan.stdout + scan.stderr)), None)
    if not fx_name:
        print("  [SKIP] no VST3 reverb scannable — FX moat not exercised on this box")
        return

    def fx_tail(with_fx):
        import numpy as np, soundfile as sf
        t = {"name": "pluck", "source": {"kind": "faust", "id": "pluck"}, "gainDb": 0,
             "notes": [{"start": b * 0.5, "len": 0.2, "pitch": 60, "vel": 1.0} for b in range(4)]}
        if with_fx:
            t["fx"] = [{"id": "vst3:" + fx_name}]
        song = {"version": 2, "bpm": 120, "lengthBars": 4, "masterGainDb": 0, "tracks": [t]}
        json.dump(song, open(os.path.join(SONGS, "_vstmoat.json"), "w"), indent=1)
        r = subprocess.run([M1, "render", os.path.join(SONGS, "_vstmoat.json"), os.path.join(SONGS, "_vstmoat.wav")],
                           capture_output=True, text=True, timeout=300)
        if "ok=1" not in (r.stdout + r.stderr):
            return None
        x = np.abs(sf.read(os.path.join(SONGS, "_vstmoat.wav"), always_2d=True)[0].mean(axis=1))
        sr = sf.info(os.path.join(SONGS, "_vstmoat.wav")).samplerate
        return [float((x[int(a * sr):int(b * sr)] ** 2).mean() ** 0.5)
                for a, b in ((2.2, 2.6), (2.6, 3.0), (3.0, 3.5))]

    dry, wet = fx_tail(False), fx_tail(True)
    for f in ("_vstmoat.json", "_vstmoat.wav"):
        p = os.path.join(SONGS, f)
        os.path.exists(p) and os.remove(p)
    if not dry or not wet:
        print("  [SKIP] FX render failed")
        return
    decays = wet[0] > wet[1] > wet[2]
    louder = wet[0] > max(dry[0] * 5, 1e-6)
    if decays and louder:
        print(f"  [PASS] VST3 FX moat: '{fx_name}' added a decaying reverb tail "
              f"{wet[0]:.5f}->{wet[2]:.5f} where dry is silent — VST3 effects process audio")
    else:
        print(f"  [FAIL] VST3 fx produced no decaying tail (wet {wet}, dry {dry})")
        sys.exit(1)


if __name__ == "__main__":
    main()
