#!/usr/bin/env python3
"""key_battery.py — ground-truth benchmark for analyze2's key estimator.

Generates loops with KNOWN keys (loop_gen writes key into the json), renders,
compares analyze2.key_estimate to truth. Baseline (2026-07-04): 4/12.

FINDINGS from the improvement attempts (all falsified, reverted):
- Aggregate chroma of a diatonic PROGRESSION ~= the scale set (Am-G-F-G sums
  to C-major pcs + G emphasis) — windowless K-S guesses among relatives/
  dominants. Real fix needs temporal chord tracking, not profile tweaks.
- Kick fundamentals (~55Hz = A1) pollute chroma in four-floor genres.
- Head/tail weighting introduced semitone-shifted picks (binning artifact).
Next real step: a proper key algorithm (essentia streaming_extractor_music or
madmom CNN) as an optional dependency; rekordbox stays authoritative for DJ.
"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENRES = ["house","trap","gospel","jazz","synthwave","reggae","disco","soul","salsa","blues","ukgarage","amapiano"]
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
PY = os.path.join(ROOT, ".venv", "bin", "python")
tmp = os.path.join(ROOT, "songs", "_keybat")
ENH = {"C#":"Db","D#":"Eb","F#":"Gb","G#":"Ab","A#":"Bb"}
def same_key(a, b):
    """enharmonic-fair compare (G# major IS Ab major — the old compare docked a point)"""
    if not a or not b: return False
    def norm(k):
        parts = k.split()
        n = parts[0]
        n = ENH.get(n, n)
        return n + " " + parts[1] if len(parts) > 1 else n
    return norm(a) == norm(b)

engine = sys.argv[1] if len(sys.argv) > 1 else "analyze2"
hits = 0
for g in GENRES:
    subprocess.run([PY, f"{ROOT}/tools/loop_gen.py", g, "_keybat", "--bars", "4", "--seed", "3"],
                   capture_output=True)
    truth = json.load(open(f"{tmp}.json"))["key"]
    subprocess.run([M1, "render", f"{tmp}.json", f"{tmp}.wav"], capture_output=True)
    if engine == "keyvote":
        kv = json.loads(subprocess.run([PY, f"{ROOT}/tools/keyvote.py", f"{tmp}.wav", "--json"],
                                       capture_output=True, text=True).stdout)
        est = kv.get("key")
    else:
        a = json.loads(subprocess.run([PY, f"{ROOT}/tools/analyze2.py", f"{tmp}.wav"],
                                      capture_output=True, text=True).stdout)
        est = a.get("key_estimate")
    ok = same_key(est, truth); hits += ok
    print(f"  {g:10} {truth:10} -> {str(est):10} {'OK' if ok else 'MISS'}")
for f in (f"{tmp}.json", f"{tmp}.wav"):
    if os.path.exists(f): os.remove(f)
print(f"key battery [{engine}]: {hits}/{len(GENRES)}")
