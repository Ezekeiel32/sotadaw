#!/usr/bin/env python3
"""THE NAM RAIL battery (V51) — a .nam amp/pedal capture is a session object:
  fx: {"id": "nam:<capture.nam>"} on any track/bus/master.

Proof at the render level (the only level that matters):
  1) the model LOADS (SOTADAW_FX_DEBUG reports capture rate),
  2) the render carries real signal (an amp, not silence),
  3) the transform is APPLIED (wet differs from dry: waveform + spectrum move),
  4) deterministic (two wet renders -> one sha, the physics seal),
  5) library ingest: index tool surfaces .nam captures.

SKIP-green when m1 or the vendored example captures are absent.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
VENV_PY = os.path.join(ROOT, ".venv", "bin", "python")
NAM = os.path.join("app", "third_party", "nam-core", "example_models", "wavenet.nam")

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)
    print(f"  {'OK ' if cond else 'XX '}{msg}")


def analyze(wav):
    py = VENV_PY if os.path.exists(VENV_PY) else "python3"
    p = subprocess.run([py, os.path.join(ROOT, "tools", "analyze2.py"), wav],
                       capture_output=True, text=True, timeout=180)
    return json.loads(p.stdout)


def render(song, wav, debug=False):
    env = dict(os.environ)
    if debug:
        env["SOTADAW_FX_DEBUG"] = "1"
    return subprocess.run([M1, "render", song, wav], capture_output=True,
                          text=True, timeout=300, env=env)


def main():
    if not os.path.exists(M1) or not os.path.exists(os.path.join(ROOT, NAM)):
        print("SKIP: m1 or the vendored example .nam absent")
        return 0
    print("== THE NAM RAIL BATTERY (V51) ==")
    work = tempfile.mkdtemp(prefix="nam_battery_")
    riff = [{"start": b + o, "len": l, "pitch": p, "vel": v}
            for b in (0.0, 4.0, 8.0, 12.0)
            for o, l, p, v in ((0.0, 0.9, 40, 0.85), (1.0, 0.4, 43, 0.7),
                               (1.5, 0.4, 45, 0.75), (2.0, 1.4, 47, 0.8),
                               (3.5, 0.4, 43, 0.6))]
    base = {"version": 2, "bpm": 100, "lengthBars": 4, "masterGainDb": 0.0,
            "master": [], "tracks": [{
                "name": "di", "source": {"kind": "faust", "id": "guitar_grit"},
                "gainDb": -6.0, "notes": riff}]}
    dry_j, wet_j = os.path.join(work, "dry.json"), os.path.join(work, "wet.json")
    dry_w, wet_w = os.path.join(work, "dry.wav"), os.path.join(work, "wet.wav")
    json.dump(base, open(dry_j, "w"))
    wet = json.loads(json.dumps(base))
    wet["tracks"][0]["fx"] = [{"id": f"nam:{NAM}", "params": {"output_db": -6.0}}]
    json.dump(wet, open(wet_j, "w"))

    r1 = render(dry_j, dry_w)
    r2 = render(wet_j, wet_w, debug=True)
    ok(r1.returncode == 0 and r2.returncode == 0, "renders complete (dry + wet)")
    ok("[nam]" in r2.stderr and "up (capture rate" in r2.stderr,
       "the capture LOADS (fx-debug reports its rate)")

    da, wa = analyze(dry_w), analyze(wet_w)
    ok(wa["peak_dbfs"] > -40, f"wet carries real signal (peak {wa['peak_dbfs']:.1f} dBFS)")
    ok(wa["clipped_samples"] < 2000,
       f"amp gain staged sanely ({wa['clipped_samples']} clipped)")
    cd = abs((wa.get("spectral_centroid_hz") or 0) - (da.get("spectral_centroid_hz") or 0))
    bands_moved = sum(abs(wa["band_energy_pct"][k] - da["band_energy_pct"][k])
                      for k in wa["band_energy_pct"])
    ok(cd > 30 or bands_moved > 6,
       f"the TRANSFORM is applied (centroid moved {cd:.0f} Hz, bands {bands_moved:.1f} pp)")
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    s1 = sha(wet_w)
    render(wet_j, wet_w)
    ok(sha(wet_w) == s1, "deterministic: two wet renders -> one sha (the physics seal)")

    # library ingest: the indexer surfaces .nam captures (pure-python check —
    # run build() into a scratch OUT so the shared library.json is untouched)
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import index_library
    real_out = index_library.OUT
    try:
        index_library.OUT = os.path.join(work, "lib.json")
        lib = index_library.build([])
        caps = {c["name"] for c in lib.get("nam_captures", [])}
        ok("wavenet" in caps and len(caps) >= 3,
           f"index_library ingests .nam captures ({len(caps)} found)")
    finally:
        index_library.OUT = real_out

    print(f"nam battery: {PASS}/{PASS + len(FAIL)} " + ("clean" if not FAIL else "RED"))
    for f in FAIL:
        print("FAIL:", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
