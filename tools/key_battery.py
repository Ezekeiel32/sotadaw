#!/usr/bin/env python3
"""key_battery.py — ground-truth benchmark for analyze2's key estimator.

Generates loops with KNOWN keys (loop_gen writes key into the json), renders,
compares analyze2.key_estimate to truth. Baseline (2026-07-04): 4/12.
2026-07-24 THE KEY EAR v2 (tools/key_ear.py) + THE KICK IN KEY (loop_gen
tunes tonal kicks to the tonic): 9/12 legacy, 28/36 with --sweep (forced-key
transpositions; the C-bias class is dead). Suite leg = legacy 12 with a
FLOOR of 9 (exit 1 below; raise the floor as the kernel improves —
remaining misses are material that under-expresses its stated tonic:
house/jazz/amapiano at their common keys).

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

SHARPS = {"Db":"C#","Eb":"D#","Gb":"F#","Ab":"G#","Bb":"A#"}
NOTES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
def transpose_key(k, semis):
    """'Ab major' + 3 -> 'B major' (sharp-normalized; mode kept)."""
    parts = k.split()
    n = SHARPS.get(parts[0], parts[0])
    pc = (NOTES.index(n) + semis) % 12
    return NOTES[pc] + (" " + parts[1] if len(parts) > 1 else "")

def estimate(engine, wav):
    if engine == "keyvote":
        kv = json.loads(subprocess.run([PY, f"{ROOT}/tools/keyvote.py", wav, "--json"],
                                       capture_output=True, text=True).stdout)
        return kv.get("key")
    if engine == "key_ear":
        ke = json.loads(subprocess.run([PY, f"{ROOT}/tools/key_ear.py", wav],
                                       capture_output=True, text=True).stdout)
        return ke.get("key")
    a = json.loads(subprocess.run([PY, f"{ROOT}/tools/analyze2.py", wav],
                                  capture_output=True, text=True).stdout)
    return a.get("key_estimate")

engine = sys.argv[1] if len(sys.argv) > 1 else "analyze2"
sweep = "--sweep" in sys.argv
hits = 0
for g in GENRES:
    subprocess.run([PY, f"{ROOT}/tools/loop_gen.py", g, "_keybat", "--bars", "4", "--seed", "3"],
                   capture_output=True)
    truth = json.load(open(f"{tmp}.json"))["key"]
    subprocess.run([M1, "render", f"{tmp}.json", f"{tmp}.wav"], capture_output=True)
    est = estimate(engine, f"{tmp}.wav")
    ok = same_key(est, truth); hits += ok
    print(f"  {g:10} {truth:10} -> {str(est):10} {'OK' if ok else 'MISS'}")
n_total = len(GENRES)
if sweep:
    # FORCED-KEY TRANSPOSITION SWEEP: kills any tonic-name bias (the 3/12 v1
    # answered 'C' to almost everything) and proves transposition invariance —
    # same material, truth keys forced off the genre's common_key.
    sw_hits = sw_n = 0
    for g in GENRES:
        base = None
        for semis in (3, -4):
            if base is None:
                subprocess.run([PY, f"{ROOT}/tools/loop_gen.py", g, "_keybat",
                                "--bars", "4", "--seed", "3"], capture_output=True)
                base = json.load(open(f"{tmp}.json"))["key"]
            forced = transpose_key(base, semis)
            subprocess.run([PY, f"{ROOT}/tools/loop_gen.py", g, "_keybat", "--bars", "4",
                            "--seed", "3", "--key", forced], capture_output=True)
            truth = json.load(open(f"{tmp}.json"))["key"]
            subprocess.run([M1, "render", f"{tmp}.json", f"{tmp}.wav"], capture_output=True)
            est = estimate(engine, f"{tmp}.wav")
            ok = same_key(est, truth); sw_hits += ok; sw_n += 1
            print(f"  {g:10} {truth:10} -> {str(est):10} {'OK' if ok else 'MISS'}  (forced {semis:+d})")
    print(f"key battery sweep [{engine}]: {sw_hits}/{sw_n}")
    hits += sw_hits; n_total += sw_n
for f in (f"{tmp}.json", f"{tmp}.wav"):
    if os.path.exists(f): os.remove(f)
print(f"key battery [{engine}]: {hits}/{n_total}")
FLOOR = 9 if not sweep else 26
sys.exit(0 if hits >= FLOOR else 1)
