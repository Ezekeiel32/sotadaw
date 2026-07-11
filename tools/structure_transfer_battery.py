#!/usr/bin/env python3
"""STRUCTURE_TRANSFER battery — a planted 3-part reference must map onto the
bar grid with the right shape: boundaries near the planted cuts, energy arc
ordered like the planted levels, sections monotonic + 4-bar snapped + covering.
Deterministic (seeded noise, tempfile scratch).
"""
import json, os, subprocess, sys, tempfile, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np
from structure_transfer import plan

N = 0


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        print(f"FAIL {N} — {msg}")
        sys.exit(1)
    print(f"ok {N} — {msg}")


def make_ref(path, sr=22050):
    """45s, three 15s parts with DISTINCT spectra + levels: dark quiet (intro),
    fullband loud (drop), thin quiet highs (outro)."""
    rng = np.random.default_rng(7)
    t = np.arange(15 * sr) / sr
    a = 0.08 * np.convolve(rng.standard_normal(15 * sr), np.ones(64) / 64, "same")
    b = 0.5 * rng.standard_normal(15 * sr) + 0.2 * np.sin(2 * np.pi * 110 * t)
    hp = rng.standard_normal(15 * sr)
    c = 0.06 * (hp - np.convolve(hp, np.ones(32) / 32, "same"))
    x = np.concatenate([a, b, c])
    x = np.clip(x / (np.abs(x).max() + 1e-9) * 0.9, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


tmp = tempfile.mkdtemp(prefix="struct_bat_")
ref = os.path.join(tmp, "ref.wav")
make_ref(ref)

out = plan(ref, target_bars=64)
ok(out["available"] and out["target_bars"] == 64, "planted 45s reference plans onto a 64-bar grid")
ok(2 <= len(out["sections"]) <= 5, f"3-part reference yields a sane section count ({len(out['sections'])})")

starts = [s["startBar"] for s in out["sections"]]
ok(starts == sorted(set(starts)) and all(s % 4 == 0 for s in starts) and starts[0] == 0,
   f"sections monotonic, 4-bar snapped, starting at 0 ({starts})")
ok(all(m["bars"][1] > m["bars"][0] for m in out["moves"])
   and out["moves"][-1]["bars"][1] == 64,
   "moves cover the grid, last span closes at the target")

# planted cut at 15s/45s -> bar 64/3 ~ 21.3 -> snapped 20 or 24; at 30s -> ~42.7 -> 40/44
mids = [s for s in starts if s > 0]
ok(any(abs(s - 21.3) <= 4.1 for s in mids) and any(abs(s - 42.7) <= 4.1 for s in mids),
   f"both planted cuts recovered within one 4-bar snap ({mids})")

e = out["energy_arc"]
ok(len(e) >= 3 and max(e) == e[1 if len(e) == 3 else e.index(max(e))] and e.index(max(e)) not in (0, len(e) - 1),
   f"energy arc peaks in the middle part, not the edges ({e})")
first, last = out["moves"][0], out["moves"][-1]
peak = max(out["moves"], key=lambda m: m["energy"])
ok(peak["density"] in ("high", "rising") and first["density"] in ("low", "mid")
   and last["density"] in ("low", "mid"),
   f"density hints follow the arc (peak={peak['density']}, edges={first['density']}/{last['density']})")

ok(json.dumps(plan(ref, target_bars=64), sort_keys=True) == json.dumps(out, sort_keys=True),
   "deterministic: two plans byte-identical")
ok(plan(os.path.join(tmp, "missing.wav"))["available"] is False,
   "unreadable reference degrades clean (available:false)")

short = os.path.join(tmp, "short.wav")
with wave.open(short, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
    w.writeframes(b"\x00\x00" * 22050)
ok(plan(short)["available"] is False, "a 1s file has no structure to hear (available:false)")

r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "structure_transfer.py"),
                    ref, "--bars", "32"], capture_output=True, text=True, cwd=ROOT)
line = next((l for l in r.stdout.splitlines() if l.startswith("STRUCT_JSON ")), "")
ok(r.returncode == 0 and line and json.loads(line[12:])["target_bars"] == 32,
   "CLI leg: STRUCT_JSON parses, --bars honored, rc=0")

print(f"PASS {N}/{N} structure_transfer battery")
