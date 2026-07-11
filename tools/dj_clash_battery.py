#!/usr/bin/env python3
"""dj_clash_battery.py — DJ key-clash auto-fix (§7.7) proof.

On a Camelot key CLASH, dj_set now DEEPENS the incoming deck's djfilter bass-kill
(knob 0.85 — the EQ bass-swap remedy) instead of only warning; compatible keys
keep the default ride (0.62). Uses 2 real song renders as decks (bpms + camelots
provided -> no heavy key/bpm detection). Exit code IS the verdict.
"""
import contextlib
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def knobs(nm):
    d = json.load(open(os.path.join(ROOT, "songs", f"{nm}.json")))
    o = []
    for t in d["tracks"]:
        for a in t.get("automation", []):
            if a["target"] == "fx[0].knob":
                o += [round(p["v"], 2) for p in a["points"]]
    return o


def main():
    from dj_mix import harmonic_verdict
    import dj_set
    cams = [f"{n}{ab}" for n in range(1, 13) for ab in "AB"]
    clashp = next(((a, b) for a in cams for b in cams
                   if a != b and "CLASH" in harmonic_verdict(a, b)), None)
    compatp = next(((a, b) for a in cams for b in cams
                    if a != b and "CLASH" not in harmonic_verdict(a, b)), None)
    wavs = [w for w in sorted(glob.glob(os.path.join(ROOT, "songs", "*.wav")))
            if os.path.getsize(w) > 100000][:2]
    if len(wavs) < 2 or not clashp or not compatp:
        print("SKIP: need 2 song wavs + camelot pairs")
        return 0
    print("== DJ KEY-CLASH AUTO-FIX BATTERY (§7.7) ==")
    with contextlib.redirect_stdout(io.StringIO()):        # hush dj_set's plan prints
        dj_set.build_set("_djclash_bat", wavs, bpms=[120, 124], camelots=list(clashp), blend_bars=8)
        dj_set.build_set("_djok_bat", wavs, bpms=[120, 124], camelots=list(compatp), blend_bars=8)
    kc, ko = knobs("_djclash_bat"), knobs("_djok_bat")
    ok1 = 0.85 in kc
    ok2 = (0.85 not in ko) and (0.62 in ko)
    fails = (not ok1) + (not ok2)
    print(f"  {'OK ' if ok1 else 'XX '}clash {clashp} -> bass-kill 0.85 applied ({kc})")
    print(f"  {'OK ' if ok2 else 'XX '}compat {compatp} -> stays 0.62, no over-fix ({ko})")
    for nm in ("_djclash_bat", "_djok_bat"):
        for e in (".json", ".setplan.json"):
            p = os.path.join(ROOT, "songs", f"{nm}{e}")
            if os.path.exists(p):
                os.remove(p)
    print("PASS" if fails == 0 else f"REGRESSION ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
