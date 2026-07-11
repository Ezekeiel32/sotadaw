#!/usr/bin/env python3
"""REFERENCE DECK battery (BEST_DAW_30 #7b) — the standing multi-ref contract.

Two synthetic references (dark sub sine vs bright noise), one rendered scratch
song. Proves: add/list/remove, weighted composite (weights PULL the target),
content-cache (second judge = zero re-analysis), the --deck gap report, and the
MCP wrappers (reference_deck + analyze_reference's no-arg deck route).

Run: .venv/bin/python tools/refdeck_battery.py
"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "agent"))
import numpy as np
from scipy.io import wavfile

import reference_match as RM

SONGS = os.path.join(ROOT, "songs")
NAME = "_refdeck_bat"
M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")
fails = []


def check(tag, ok, detail=""):
    print(f"  {'ok' if ok else 'XX'} {tag} {detail}")
    if not ok:
        fails.append(tag)


def synth_ref(path, kind):
    sr, dur = 44100, 6.0
    t = np.arange(int(sr * dur)) / sr
    if kind == "dark":
        x = 0.5 * np.sin(2 * np.pi * 55 * t) + 0.05 * np.sin(2 * np.pi * 440 * t)
    else:
        rng = np.random.default_rng(7)
        x = 0.25 * rng.standard_normal(t.size) + 0.1 * np.sin(2 * np.pi * 6000 * t)
    x = np.clip(x, -0.98, 0.98)
    wavfile.write(path, sr, (x * 32767).astype(np.int16))


def cleanup():
    for suf in (".json", ".wav", ".refs.json"):
        p = os.path.join(SONGS, NAME + suf)
        os.path.exists(p) and os.remove(p)
    for f in ("_rd_dark.wav", "_rd_bright.wav"):
        p = os.path.join(SONGS, f)
        os.path.exists(p) and os.remove(p)


def main():
    cleanup()
    dark = os.path.join(SONGS, "_rd_dark.wav")
    bright = os.path.join(SONGS, "_rd_bright.wav")
    synth_ref(dark, "dark")
    synth_ref(bright, "bright")
    song = {"bpm": 120, "lengthBars": 2, "tracks": [
        {"name": "sub", "gainDb": -8.0,
         "source": {"kind": "faust", "id": "sub_clean", "params": {}},
         "notes": [{"start": float(b), "len": 0.9, "pitch": 33, "vel": 0.8}
                   for b in range(8)]}]}
    json.dump(song, open(os.path.join(SONGS, f"{NAME}.json"), "w"))
    r = subprocess.run([M1, "render", os.path.join(SONGS, f"{NAME}.json"),
                        os.path.join(SONGS, f"{NAME}.wav")],
                       capture_output=True, timeout=180)
    check("scratch song rendered", r.returncode == 0
          and os.path.exists(os.path.join(SONGS, f"{NAME}.wav")))

    RM.deck_save(NAME, [])
    RM.deck_save(NAME, [{"path": dark, "weight": 1.0},
                        {"path": bright, "weight": 1.0}])
    comp, per = RM.deck_composite(NAME)
    check("composite over 2 refs", comp is not None and len(per) == 2)
    a_dark = RM.ref_analysis_cached(dark)
    a_bri = RM.ref_analysis_cached(bright)
    lo = min(a_dark["spectral_centroid_hz"], a_bri["spectral_centroid_hz"])
    hi = max(a_dark["spectral_centroid_hz"], a_bri["spectral_centroid_hz"])
    check("composite centroid sits between the refs",
          lo < comp["spectral_centroid_hz"] < hi,
          f"{lo:.0f} < {comp['spectral_centroid_hz']:.0f} < {hi:.0f}")
    RM.deck_save(NAME, [{"path": dark, "weight": 4.0},
                        {"path": bright, "weight": 1.0}])
    comp_w, _ = RM.deck_composite(NAME)
    check("weights PULL the composite (4x dark -> darker target)",
          comp_w["spectral_centroid_hz"] < comp["spectral_centroid_hz"],
          f"{comp_w['spectral_centroid_hz']:.0f} < {comp['spectral_centroid_hz']:.0f}")
    t0 = time.time()
    RM.deck_composite(NAME)
    check("cache makes the second judge instant", time.time() - t0 < 1.0,
          f"{time.time() - t0:.2f}s")

    out = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "reference_match.py"),
                          "--deck", NAME, "--json"], capture_output=True, text=True,
                         timeout=300)
    check("--deck report runs", out.returncode == 0, out.stderr[-120:])
    rep = json.loads(out.stdout) if out.returncode == 0 else {}
    check("deck report carries gaps vs the sub-only mix",
          isinstance(rep.get("gaps"), list) and len(rep["gaps"]) >= 1,
          str([g["metric"] for g in rep.get("gaps", [])][:4]))

    import daw_mcp
    lst = daw_mcp.t_reference_deck({"song": NAME, "action": "list"})
    check("MCP reference_deck lists", '"deck"' in lst and "_rd_dark" in lst)
    ar = daw_mcp.t_analyze_reference({"song": NAME})
    check("analyze_reference no-arg routes to the DECK",
          "DECK" in ar and "gap" in ar.lower(), ar[:80].replace("\n", " "))
    rm = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "reference_match.py"),
                         "--song", NAME, "--deck-remove", "2"],
                        capture_output=True, text=True, timeout=60)
    left = json.loads(rm.stdout).get("deck", []) if rm.returncode == 0 else []
    check("remove by index", len(left) == 1 and "_rd_dark" in left[0]["path"], str(len(left)))
    cleanup()
    print(f"refdeck battery: {'clean' if not fails else 'RED ' + str(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
