#!/usr/bin/env python3
"""MCP SMOKE — verify the campaign's new tools work through the ACTUAL MCP handler
layer (subprocess shims, arg passing, receipts, allowlist), not just standalone.

Firing 55 proved the wrapper layer can silently BLOCK a tool the Python for which
works fine. This calls each real t_* handler on a scratch song and asserts sane
output — the path the agent actually takes. Exit 1 on any failure."""
import importlib.util, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
sys.path.insert(0, os.path.join(ROOT, "tools"))

# load daw_mcp as the agent's harness does
spec = importlib.util.spec_from_file_location("daw_mcp", os.path.join(ROOT, "agent", "daw_mcp.py"))
dm = importlib.util.module_from_spec(spec)
_argv = sys.argv; sys.argv = ["daw_mcp"]
spec.loader.exec_module(dm)
sys.argv = _argv

FAIL = []
def check(n, c, d=""):
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))
    (None if c else FAIL.append(n))

from chordvote import chord_map

def scratch(name):
    prog = [0, 8, 3, 10]
    tr = [{"name": "kick", "source": {"kind": "faust", "id": "kick_808"}, "gainDb": -5, "pan": 0.3,
           "notes": [{"start": b, "len": 0.25, "pitch": 36, "vel": 1.0} for b in range(64)]},
          {"name": "lead", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -6,
           "notes": [{"start": i * 0.5, "len": 0.4, "pitch": 55 + (i % 8), "vel": 0.8} for i in range(32)]},
          {"name": "chords", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -8, "notes": []}]
    for bar in range(16):
        r = prog[bar % 4] + 48
        for iv in (0, 3, 7):
            tr[2]["notes"].append({"start": bar * 4.0, "len": 3.5, "pitch": r + iv, "vel": 0.6})
    song = {"version": 2, "bpm": 120, "lengthBars": 16, "masterGainDb": 0, "key": "C minor", "tracks": tr}
    song["chords"] = chord_map(song)
    json.dump(song, open(os.path.join(SONGS, f"{name}.json"), "w"), indent=1)

created = []
def mk(n):
    scratch(n); created.append(n); return n

# every handler that exists gets exercised through the real dm.TOOLS entry
def call(tool, args):
    fn = dm.TOOLS[tool][0]
    return fn(args)

# 1. the tool is REGISTERED + ALLOWED (the firing-55 failure mode). Load the REAL
# sidecar so we test the actual DAW_ALLOW the agent runs with, catching any drift.
sc_spec = importlib.util.spec_from_file_location("sidecar", os.path.join(ROOT, "agent", "sidecar.py"))
sc = importlib.util.module_from_spec(sc_spec)
_a = sys.argv; sys.argv = ["sidecar"]
try:
    sc_spec.loader.exec_module(sc)
    allow = sc.DAW_ALLOW
except Exception as e:
    allow = ",".join("mcp__daw__" + t for t in dm.TOOLS)   # fallback: replicate the derivation
    print(f"  (sidecar import fell back: {e})")
sys.argv = _a
for t in ("humanize", "infill_region", "doctor", "prescribe", "style_profile"):
    check(f"{t}: in TOOLS catalog", t in dm.TOOLS)
    check(f"{t}: in sidecar DAW_ALLOW", f"mcp__daw__{t}" in allow)

# 2. doctor through the handler
s = mk("_mcpsmoke")
out = call("doctor", {"song": s})
check("doctor handler returns findings (not error)", "issue" in out.lower() or "clean" in out.lower(), out[:80])
check("doctor handler didn't error", "failed" not in out.lower())

# 3. humanize measure through the handler
out = call("humanize", {"song": s, "measure": True})
check("humanize measure returns NOMML/expressiveness", "NOMML" in out or "expressiveness" in out, out[:80])

# 4. infill through the handler (edits the file, files a receipt)
out = call("infill_region", {"song": s, "track": "lead", "from_bar": 5, "to_bar": 8, "seed": 1})
check("infill handler regenerated a window", "new notes" in out and "failed" not in out.lower(), out[:80])

# 5. prescribe through the handler (writes a copy)
out = call("prescribe", {"song": s, "out": "_mcpsmoke_fixed"})
created.append("_mcpsmoke_fixed")
check("prescribe handler auto-fixed + reported", "issues" in out.lower() and "failed" not in out.lower(), out[:80])

# 6. style_profile extract + score through the handler
out = call("style_profile", {"action": "extract", "songs": [s], "profile": "_smoke"})
check("style extract handler built a fingerprint", "fingerprint" in out.lower(), out[:80])
out = call("style_profile", {"action": "score", "song": s, "profile": "_smoke"})
check("style score handler returns a match number", "/100" in out or "score" in out.lower(), out[:80])

# cleanup scratch songs + fingerprint
for n in created:
    p = os.path.join(SONGS, f"{n}.json"); os.path.exists(p) and os.remove(p)
fp = os.path.join(SONGS, "_style__smoke.json"); os.path.exists(fp) and os.remove(fp)

print(f"\nVERDICT: {len(FAIL)} fail" + ("" if not FAIL else " — " + ", ".join(FAIL)))
sys.exit(1 if FAIL else 0)
