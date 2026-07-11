#!/usr/bin/env python3
"""palette_seed.py — curate PALETTES v2 (the genre's factory-synth color).

The KG gives some genres a vst3:<plugin> SoundRecipe voice (synthwave->TAL,
techno->Odin, ...). This picks ONE render-VERIFIED factory PAD per instrument
plugin and freezes it, params inline, into library/palettes.json — self-
contained (ships in git, no preset-file dependency at loop-build time) and
offline-safe (loop_gen falls back to a Faust pad when the plugin isn't
installed).

  palette_seed.py [--tries 30]

Deterministic: prefers PAD-categorised presets, renders each candidate as a held
triad, keeps the first that peaks > -45 dBFS (which dodges Odin's gain-0
silencers, CLAUDE.md). Re-run to re-curate after preset/plugin changes.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
OUT = os.path.join(ROOT, "library", "palettes.json")
SCRATCH = os.path.join(ROOT, "songs", "_palette_probe.json")
WAV = os.path.join(ROOT, "songs", "_palette_probe.wav")

# instrument plugins the KG voices reference (Dragonfly is a reverb -> never here)
INSTRUMENTS = ["TAL-NoiseMaker", "Odin2", "Surge XT", "Dexed"]
FALLBACK_VOICE = "pad_motion"       # a real Faust pad, for offline / non-instrument
AUDIBLE_DB = -45.0


def peak_dbfs(path):
    with wave.open(path) as w:
        sw, n = w.getsampwidth(), w.getnframes()
        raw = w.readframes(n)
    peak = 0
    step = sw * 64                                   # stride for speed
    if sw == 3:
        for i in range(0, len(raw) - 2, step):
            peak = max(peak, abs(int.from_bytes(raw[i:i + 3], "little", signed=True)))
        full = 2 ** 23
    elif sw == 2:
        import struct
        for i in range(0, len(raw) - 1, step):
            peak = max(peak, abs(struct.unpack("<h", raw[i:i + 2])[0]))
        full = 2 ** 15
    else:
        return -99.0
    return 20 * math.log10(peak / full) if peak else -99.0


def probe_source(plugin, params):
    song = {"version": 2, "bpm": 120.0, "lengthBars": 2, "masterGainDb": 0.0,
            "tracks": [{"name": "t",
                        "source": {"kind": "vst3", "plugin": plugin, "params": params},
                        "gainDb": 0,
                        "notes": [{"start": 0, "len": 3.5, "pitch": p, "vel": 0.7}
                                  for p in (48, 55, 60)]}]}
    json.dump(song, open(SCRATCH, "w"))
    try:
        r = subprocess.run([M1, "render", SCRATCH, WAV],
                           capture_output=True, text=True, timeout=180)
        if "ok=1" not in (r.stdout + r.stderr):
            return -99.0
        return peak_dbfs(WAV)
    except Exception:
        return -99.0


def curate(tries):
    lib = json.load(open(os.path.join(ROOT, "library.json")))
    by = {}
    for e in lib.get("vst_presets", []):
        by.setdefault(e["plugin"], []).append(e)
    palettes = {}
    for plugin in INSTRUMENTS:
        if plugin in ("Surge XT",):
            continue      # blob preset — not shipped in the self-contained default
        mod = {"TAL-NoiseMaker": "tal_presets", "Odin2": "odin_presets"}.get(plugin)
        if mod is None:
            continue
        entries = by.get(plugin, [])
        if not entries:
            continue
        pads = sorted([e for e in entries
                       if "pad" in (e.get("category", "") + " " + e["name"]).lower()],
                      key=lambda e: e["name"])
        rest = sorted([e for e in entries if e not in pads], key=lambda e: e["name"])
        picked = None
        for e in (pads + rest)[:tries]:
            try:
                params = __import__(mod).parse_preset(e["path"])
            except Exception:
                continue
            pk = probe_source(plugin, params)
            print(f"  {plugin:15} {e['name'][:32]:32} [{(e.get('category','') or '')[:8]:8}]"
                  f" peak {pk:6.1f} dB")
            if pk > AUDIBLE_DB:
                picked = {"preset_name": e["name"], "category": e.get("category", ""),
                          "source": {"kind": "vst3", "plugin": plugin, "params": params}}
                break
        if picked:
            palettes[plugin] = picked
            print(f"  -> {plugin}: '{picked['preset_name']}'  ({picked['category']})")
        else:
            print(f"  -> {plugin}: NO audible pad found in {tries} tries")
    return palettes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tries", type=int, default=30)
    a = ap.parse_args()
    palettes = curate(a.tries)
    doc = {"_doc": "Palettes v2 — render-verified factory PAD per instrument plugin for "
                   "the KG's vst3 SoundRecipe voices. loop_gen resolves a genre's "
                   "vst3:<plugin> color voice to by_plugin[<plugin>].source; falls back to "
                   "fallback_voice (a Faust pad) when the plugin is a non-instrument "
                   "(reverb) or not installed. Regenerate with tools/palette_seed.py.",
           "fallback_voice": FALLBACK_VOICE,
           "instruments": INSTRUMENTS,
           "by_plugin": palettes}
    json.dump(doc, open(OUT, "w"), indent=1)
    for f in (SCRATCH, WAV):
        if os.path.exists(f):
            os.remove(f)
    print(f"WROTE {os.path.relpath(OUT, ROOT)} — {len(palettes)} plugin palettes: "
          f"{list(palettes)}")
    return 0 if palettes else 1


if __name__ == "__main__":
    sys.exit(main())
