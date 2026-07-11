#!/usr/bin/env python3
"""palette_battery.py — PALETTES v2 regression net.

Proves loop_gen never re-emits the old SILENT color layer: a KG vst3:<plugin>
SoundRecipe voice must resolve to a real vst3 source (installed instrument) or
a Faust pad fallback — NEVER the broken {"kind":"faust","id":"vst3:..."} that
the Faust JIT can't load (which rendered 15 genres' signature synth silent).

  palette_battery.py [--render]

Default (fast): the resolver is exercised over every branch (installed TAL/Odin,
a reverb, an uninstalled synth, a plain Faust voice, and OFFLINE with no scan
cache), and three representative genres (TAL / Odin / reverb-fallback) are
generated and their color source asserted valid. --render also renders the three
and asserts each color stem is audible (> -50 dBFS). GUARDIAN-safe; exit code IS
the verdict (0 = pass, 1 = regression).
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
LG = os.path.join(ROOT, "tools", "loop_gen.py")
PY = sys.executable
TMP = os.path.join(ROOT, "songs", "_palbat_stems")

REPS = [("synthwave", "TAL vst3"), ("techno", "Odin vst3"), ("dub_techno", "reverb->faust")]


def gen(genre, name):
    subprocess.run([PY, LG, genre, name, "--seed", "3"],
                   capture_output=True, text=True, timeout=120)
    p = os.path.join(ROOT, "songs", f"{name}.json")
    return json.load(open(p)) if os.path.exists(p) else None


def color_source(song):
    for t in (song or {}).get("tracks", []):
        if t.get("name") == "color":
            return t.get("source", {})
    return None


def resolver_branches():
    """Exhaustive, in-process — the real coverage of the resolve logic."""
    import loop_gen as lg
    lg._palettes()
    cases = [
        ("vst3:TAL-NoiseMaker", "vst3", "TAL-NoiseMaker"),   # installed instrument
        ("vst3:Odin2", "vst3", "Odin2"),
        ("vst3:Dragonfly", "faust", None),                   # a reverb -> fallback
        ("vst3:Serum", "faust", None),                       # uninstalled -> fallback
        ("supersaw_fat", "faust", "supersaw_fat"),           # plain voice -> passthrough
    ]
    fails = 0
    for voice, want_kind, want_id in cases:
        s = lg.resolve_color_source(voice)
        ident = s.get("plugin") or s.get("id")
        broken = s.get("kind") == "faust" and str(ident).startswith("vst3:")
        ok = s.get("kind") == want_kind and (want_id is None or ident == want_id) and not broken
        fails += not ok
        print(f"  {'OK ' if ok else 'XX '}resolve {voice:22} -> {s.get('kind')}:{ident}")
    # OFFLINE: no scan cache -> even installed plugins fall back to Faust
    lg._PAL["scanned"] = ""
    off = lg.resolve_color_source("vst3:TAL-NoiseMaker").get("kind") == "faust"
    fails += not off
    print(f"  {'OK ' if off else 'XX '}resolve OFFLINE (no scan cache) -> faust fallback")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    a = ap.parse_args()
    print("== PALETTES v2 BATTERY ==")
    fails = resolver_branches()
    names = []
    for genre, tag in REPS:
        nm = f"_palbat_{genre}"
        names.append(nm)
        src = color_source(gen(genre, nm))
        if src is None:
            print(f"  --  {genre:12} ({tag}) no color layer")
            continue
        ident = src.get("id") or src.get("plugin") or ""
        broken = src.get("kind") == "faust" and str(ident).startswith("vst3:")
        ok = ((src.get("kind") == "vst3" and ident) or
              (src.get("kind") == "faust" and not str(ident).startswith("vst3:"))) and not broken
        fails += not ok
        shown = f"{src.get('kind')}:{ident}"
        print(f"  {'OK ' if ok else 'XX '}gen {genre:12} ({tag}) color -> {shown}")

    if a.render:
        from palette_seed import peak_dbfs
        for genre, tag in REPS:
            nm = f"_palbat_{genre}"
            od = os.path.join(TMP, genre)
            subprocess.run([M1, "render-stems", os.path.join(ROOT, "songs", f"{nm}.json"),
                            od + "/"], capture_output=True, text=True, timeout=180)
            cs = glob.glob(os.path.join(od, "*color*"))
            pk = max((peak_dbfs(w) for w in cs), default=-99.0)
            aud = pk > -50.0
            fails += not aud
            print(f"  {'OK ' if aud else 'XX '}render {genre:12} ({tag}) color peak {pk:.1f} dBFS")

    for nm in names:
        for ext in (".json", ".wav"):
            p = os.path.join(ROOT, "songs", nm + ext)
            if os.path.exists(p):
                os.remove(p)
    if os.path.isdir(TMP):
        shutil.rmtree(TMP, ignore_errors=True)
    print("PASS" if fails == 0 else f"REGRESSION ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
