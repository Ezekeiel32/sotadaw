#!/usr/bin/env python3
"""Full render-health eval sweep over the campaign's new genres (inline, zero tokens).
PASS = loop generates + renders + clipped_samples==0 + bpm inside the genre's KG range.
LUFS reported informationally (loops are pre-master; MixTargets bind FINISHED tracks)."""
import json, os, re, subprocess, sys

ROOT = "/home/chezy/AI_SOTA_DAW"
M1 = f"{ROOT}/app/build/m1_artefacts/Release/m1"
PY = f"{ROOT}/.venv/bin/python"
genres = sys.argv[1].split(",")
ok, bad = [], []
for g in genres:
    name = f"_gxs_{g}"; sj = f"{ROOT}/songs/{name}.json"; wav = f"{ROOT}/songs/{name}.wav"
    try:
        r = subprocess.run([PY, f"{ROOT}/tools/loop_gen.py", g, name, "--bars", "4", "--seed", "4"],
                           capture_output=True, text=True, timeout=60)
        m = re.search(r"@ ([\d.]+)bpm", r.stdout + r.stderr)
        bpm = float(m.group(1)) if m else -1
        r2 = subprocess.run([M1, "render", sj, wav], capture_output=True, text=True, timeout=120)
        if r2.returncode != 0 or not os.path.exists(wav):
            bad.append((g, "RENDER FAIL")); continue
        a = subprocess.run([PY, f"{ROOT}/tools/analyze2.py", wav], capture_output=True, text=True, timeout=60).stdout
        d = json.loads(a[a.index("{"):])
        clip = d.get("clipped_samples", -1); lufs = d.get("lufs_integrated")
        # bpm-in-range check against the KG
        q = subprocess.run([PY, "-c", f"""
import sys; sys.path.insert(0, "{ROOT}/tools")
from kg import KG
r = KG().q("MATCH (g:Genre {{name: '{g}'}}) RETURN g.bpm_lo, g.bpm_hi")
print(r[0][0], r[0][1])"""], capture_output=True, text=True, timeout=30).stdout.split()
        lo, hi = float(q[0]), float(q[1])
        in_range = lo - 0.5 <= bpm <= hi + 0.5
        if clip == 0 and in_range:
            ok.append((g, bpm, lufs))
            print(f"PASS {g:16} bpm={bpm:<6} lufs={lufs:<7} clip=0")
        else:
            bad.append((g, f"clip={clip} bpm={bpm} range={lo}-{hi}"))
            print(f"FAIL {g:16} clip={clip} bpm={bpm} range={lo}-{hi}")
    except Exception as e:
        bad.append((g, str(e)[:80])); print(f"FAIL {g:16} {str(e)[:80]}")
    finally:
        for f in (sj, wav):
            if os.path.exists(f): os.remove(f)
print(f"\n=== SWEEP: {len(ok)} PASS / {len(bad)} FAIL of {len(genres)} ===")
for g, why in bad: print(f"  FAIL {g}: {why}")
