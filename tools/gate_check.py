#!/usr/bin/env python3
"""THE 0.020 GATE verdict: machine-check the unattended arc's output against every criterion."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name = sys.argv[1] if len(sys.argv) > 1 else "gate_arc"
song = json.load(open(os.path.join(ROOT, "songs", f"{name}.json")))
wav = os.path.join(ROOT, "songs", f"{name}.wav")

checks = {}
tracks = song["tracks"]
names = [t["name"].lower() for t in tracks]
checks["extended_to_16_bars"] = float(song.get("lengthBars", 0)) >= 16
checks["drums_on_sota_kit"] = any(t.get("source", {}).get("kit") == "sota_drums" for t in tracks)
checks["has_bass_and_lead_layers"] = len(tracks) >= 5
checks["groove_applied"] = any(t.get("groove", {}).get("name") == "ukg_shuffle" for t in tracks)
checks["eq_or_comp_used"] = any(fx.get("type") in ("eq", "comp")
                                for t in tracks for fx in t.get("fx", []))
checks["sections_with_drop"] = any("drop" in str(s.get("name", "")).lower()
                                   for s in song.get("sections", []))
checks["drop_duplicated"] = sum("drop" in str(s.get("name", "")).lower()
                                for s in song.get("sections", [])) >= 2
checks["launcher_scenes_authored"] = bool(song.get("scenes")) and any(t.get("slots") for t in tracks)
checks["lyrics_written"] = bool(song.get("lyrics"))
checks["vocal_track_with_audio"] = any(
    t.get("source", {}).get("kind") == "audio" and t.get("audioClips") for t in tracks)
vocal_wav = os.path.join(ROOT, "songs", f"{name}_vocal.wav")
checks["vocal_wav_rendered"] = os.path.exists(vocal_wav)

if os.path.exists(wav):
    a = json.loads(subprocess.run(
        [os.path.join(ROOT, ".venv", "bin", "python"), os.path.join(ROOT, "tools", "analyze2.py"), wav],
        capture_output=True, text=True).stdout)
    if isinstance(a, list):
        a = a[0]
    checks["render_exists"] = True
    checks["clipped_zero"] = a.get("clipped_samples", 1) == 0
    checks["true_peak_ok"] = (a.get("true_peak_dbtp") or 0) <= -0.9
    checks["lufs_in_genre_window"] = -16.5 <= (a.get("lufs_integrated") or -99) <= -8
    metrics = {k: a.get(k) for k in ("peak_dbfs", "true_peak_dbtp", "lufs_integrated", "clipped_samples", "duration_s")}
else:
    checks["render_exists"] = False
    metrics = {}

passed = sum(bool(v) for v in checks.values())
print(json.dumps({"gate": name, "score": f"{passed}/{len(checks)}",
                  "checks": checks, "metrics": metrics}, indent=1))
