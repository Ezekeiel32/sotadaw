#!/usr/bin/env python3
"""THE HEADROOM LAW enforcer (voice-headroom law, ratified):

  the gain zone is engine-driven velocity; .dsp headroom must be STRUCTURAL
  (inside process); prove 0 clipped at vel 1.0 solo.

For each voice this tool:
  1. clones it to a scratch JIT name (zzhr<voice>) with a calibration trim
     (-12 dB) inserted before the final `<: _,_;` split,
  2. renders the SAME probe the certs use (dsp_bench voice, note 60, vel 1.0)
     and measures the true overshoot (the trim is the LAST stage, so the
     solve is exactly linear),
  3. solves the structural trim that lands the peak at --target dBFS,
  4. re-renders to VERIFY clipped==0 and the peak is in the healthy band,
  5. with --apply, writes the proven trim into the real .dsp
     (`: *(HR) <: _,_;` — uniform, auditable, composes with existing stages).

Scratch .dsp files live in instruments/ ONLY during the run (the JIT resolves
instruments/<id>.dsp by id) and are always deleted, even on failure.

Usage:
  voice_headroom.py [voice ...] [--target -0.8] [--apply] [--keep-going]
  no voices given -> every cert with headroom_pass_vel1 == false

Exit 0 = all voices solved (and applied, if --apply); nonzero otherwise.
NOTE: applied edits to AOT-baked voices need the nuke rebuild (see CLAUDE.md)
before re-certing — the JIT verify here is the proof of the .dsp math itself.
"""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTR = os.path.join(ROOT, "instruments")
CERTS = os.path.join(INSTR, "certs")
BENCH = os.path.join(ROOT, "tools", "dsp_bench.py")
PY = sys.executable

SPLIT_RE = re.compile(r"<:\s*_\s*,\s*_\s*;")
CAL_HR = 0.25                      # -12.04 dB calibration trim
CAL_HR_DEEP = 0.0625               # -24.08 dB fallback for resonant blowups
TRIM_COMMENT = "// headroom law: cert-calibrated, 0 clipped @ vel 1.0"


def _fails_from_certs():
    out = []
    for p in sorted(glob.glob(os.path.join(CERTS, "*.cert.json"))):
        d = json.load(open(p))
        if d.get("verdicts", {}).get("headroom_pass_vel1") is False:
            out.append(os.path.basename(p).replace(".cert.json", ""))
    return out


def _with_trim(src, hr):
    """Insert the trim stage before the FINAL mono split. Exactly one split
    must exist (the voice law's `<: _,_` ending)."""
    hits = list(SPLIT_RE.finditer(src))
    if len(hits) != 1:
        return None
    m = hits[0]
    return src[:m.start()] + f": *({hr}) " + src[m.start():]


def _bench_voice(name):
    r = subprocess.run([PY, BENCH, "voice", name, "--vel", "1.0"],
                       capture_output=True, text=True, cwd=ROOT, timeout=600)
    for ln in r.stdout.splitlines():
        if ln.startswith("BENCH_JSON "):
            return json.loads(ln[11:])
    return {"error": f"no BENCH_JSON (rc={r.returncode}): "
                     f"{(r.stdout + r.stderr)[-300:]}"}


def solve_voice(voice, target_db, apply_fix):
    real = os.path.join(INSTR, f"{voice}.dsp")
    if not os.path.exists(real):
        return {"voice": voice, "error": "no .dsp source"}
    src = open(real).read()
    if _with_trim(src, 1.0) is None:
        return {"voice": voice, "error": "no unique final `<: _,_;` split "
                                         "(hand-edit this one)"}
    scratch_id = f"zzhr{voice}"
    scratch = os.path.join(INSTR, f"{scratch_id}.dsp")
    try:
        # 1) calibrate
        cal_hr = CAL_HR
        open(scratch, "w").write(_with_trim(src, cal_hr))
        cal = _bench_voice(scratch_id)
        if "error" in cal:
            return {"voice": voice, "error": f"cal render: {cal['error']}"}
        if cal["clipped_samples"] > 0:                 # resonant blowup >12 dB
            cal_hr = CAL_HR_DEEP
            open(scratch, "w").write(_with_trim(src, cal_hr))
            cal = _bench_voice(scratch_id)
            if "error" in cal or cal["clipped_samples"] > 0:
                return {"voice": voice,
                        "error": f"clips even at -24 dB cal: {cal}"}
        peak_cal = cal["peak_dbfs"]
        if peak_cal is None or peak_cal <= -90:
            return {"voice": voice, "error": f"cal render silent ({peak_cal})"}
        # 2) linear solve (trim is the last stage -> exact)
        overshoot_db = peak_cal - 20.0 * __import__("math").log10(cal_hr)
        hr = round(cal_hr * 10.0 ** ((target_db - peak_cal) / 20.0), 3)
        if hr >= 1.0:
            return {"voice": voice, "skip": True, "overshoot_db": overshoot_db,
                    "note": "peaks under target already at unity"}
        # 3) verify
        open(scratch, "w").write(_with_trim(src, hr))
        ver = _bench_voice(scratch_id)
        if "error" in ver:
            return {"voice": voice, "error": f"verify render: {ver['error']}"}
        ok = (ver["clipped_samples"] == 0
              and -1.8 <= (ver["peak_dbfs"] or -200) <= -0.3)
        res = {"voice": voice, "hr": hr,
               "overshoot_db": round(overshoot_db, 2),
               "verified_peak_dbfs": ver["peak_dbfs"],
               "verified_clipped": ver["clipped_samples"], "pass": ok}
        # 4) land it (single-line edit + trailing law comment, auditable diff)
        if ok and apply_fix:
            fixed = _with_trim(src, hr)
            fixed = re.sub(r"(: \*\(" + re.escape(str(hr)) + r"\) <:\s*_\s*,\s*_\s*;)",
                           r"\1  " + TRIM_COMMENT, fixed, count=1)
            open(real, "w").write(fixed)
            res["applied"] = True
        return res
    finally:
        if os.path.exists(scratch):
            os.remove(scratch)


def main():
    a = sys.argv[1:]
    target = float(a[a.index("--target") + 1]) if "--target" in a else -0.8
    apply_fix = "--apply" in a
    keep_going = "--keep-going" in a
    voices = [x for x in a if not x.startswith("--")
              and x != (a[a.index("--target") + 1] if "--target" in a else None)]
    if not voices:
        voices = _fails_from_certs()
    if not voices:
        print("HEADROOM_JSON " + json.dumps({"voices": [], "all_pass": True}))
        return 0
    results, bad = [], 0
    for i, v in enumerate(voices, 1):
        r = solve_voice(v, target, apply_fix)
        results.append(r)
        tag = ("SKIP" if r.get("skip")
               else "ok" if r.get("pass") else "FAIL")
        print(f"  [{i}/{len(voices)}] {v:20s} {tag} "
              + (f"hr={r.get('hr')} overshoot={r.get('overshoot_db')}dB "
                 f"peak={r.get('verified_peak_dbfs')} "
                 f"clipped={r.get('verified_clipped')}"
                 if "error" not in r else f"ERROR: {r['error']}"),
              flush=True)
        if "error" in r or (not r.get("pass") and not r.get("skip")):
            bad += 1
            if not keep_going:
                break
    print("HEADROOM_JSON " + json.dumps(
        {"target_dbfs": target, "applied": apply_fix, "failed": bad,
         "results": results}))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
