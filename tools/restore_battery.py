#!/usr/bin/env python3
"""RESTORE_AUDIO battery — pure DSP proofs (no m1 needed) + one real-stem QC
leg. A synthetic take (330 Hz phrases) is polluted with everything the QC
claims to see — 50 Hz hum + harmonics, broadband floor, DC — then each claim
and each fix is measured. Clean input must pass through as a byte-copy.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np
import soundfile as sf

from restore_audio import qc, restore, fix_hum, fix_dc, denoise  # noqa: E402

N = 0


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        print(f"FAIL {N} — {msg}")
        sys.exit(1)
    print(f"ok {N} — {msg}")


def band_db(y, sr, lo, hi):
    Y = np.abs(np.fft.rfft(y))
    f = np.fft.rfftfreq(len(y), 1 / sr)
    m = (f >= lo) & (f < hi)
    return 10 * np.log10(float((Y[m] ** 2).sum()) + 1e-12)


sr = 44100
t = np.arange(8 * sr) / sr
phrase = ((t % 2.0) < 1.0).astype(float)
rng = np.random.default_rng(11)
clean = 0.30 * np.sin(2 * np.pi * 330 * t) * phrase
hum = 0.02 * (np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 100 * t)
              + 0.3 * np.sin(2 * np.pi * 150 * t))
noise = 0.006 * rng.standard_normal(len(t))
dirty = clean + hum + noise + 0.02                       # + DC offset

# ---- QC sees every planted problem
r = qc(dirty, sr)
ok(abs(r["dc"] - 0.02) < 0.003, f"QC dc = {r['dc']} (planted 0.02)")
ok(r["hum"] and r["hum"]["base"] == 50.0 and r["hum"]["harmonics"] >= 2,
   f"QC hum = {r['hum']} (planted 50 Hz + 2 harmonics)")
# planted floor: hum+noise rms ~ -35..-40 dB; QC floor must land in that region
ok(-45 < r["noise_floor_db"] < -25, f"QC noise floor {r['noise_floor_db']} dB (in the planted region)")
rc = qc(clean + 1e-4 * rng.standard_normal(len(t)), sr)
ok(rc["hum"] is None and abs(rc["dc"]) < 1e-4, "QC on a clean take: no hum, no dc")

# ---- hum fix: comb kills the hum PEAKS (narrow bands, where hum dominates
# the broadband floor the notches must NOT touch) by >22 dB, body <0.8 dB
fh = fix_hum(dirty - 0.02, sr, 50.0)
peaks_before = sum(band_db(dirty - 0.02, sr, f0 - 1.5, f0 + 1.5) for f0 in (50, 100, 150))
peaks_after = sum(band_db(fh, sr, f0 - 1.5, f0 + 1.5) for f0 in (50, 100, 150))
hum_drop = (peaks_before - peaks_after) / 3.0
ok(hum_drop > 22, f"hum comb drops the 50/100/150 Hz peaks {hum_drop:.1f} dB avg (>22)")
body = abs(band_db(dirty - 0.02, sr, 300, 360) - band_db(fh, sr, 300, 360))
ok(body < 0.8, f"330 Hz body moves only {body:.2f} dB (<0.8)")

# ---- dc fix
fd = fix_dc(dirty, sr)
ok(abs(float(fd.mean())) < 1e-4, f"dc fix: |mean| = {abs(float(fd.mean())):.2e} (<1e-4)")

# ---- denoise: silent gaps drop hard, phrases hold
dn = denoise(clean + noise, sr, reduce_db=10)
gap = slice(int(1.2 * sr), int(1.9 * sr))
ph = slice(int(0.2 * sr), int(0.9 * sr))


def rms_db(x):
    return 20 * np.log10(float(np.sqrt((x ** 2).mean())) + 1e-12)


gap_drop = rms_db((clean + noise)[gap]) - rms_db(dn[gap])
ok(gap_drop > 6, f"denoise: silent gaps drop {gap_drop:.1f} dB (>6 at reduce 10)")
ph_shift = abs(rms_db((clean + noise)[ph]) - rms_db(dn[ph]))
ok(ph_shift < 1.5, f"denoise: phrases move only {ph_shift:.2f} dB (<1.5)")
ok(len(dn) == len(clean), "denoise preserves length exactly")

# ---- restore() auto policy end-to-end + determinism
out1, applied1, _ = restore(dirty, sr)
out2, applied2, _ = restore(dirty, sr)
ok(applied1 == applied2 and np.array_equal(out1, out2), f"deterministic (applied={applied1})")
ok("dc" in applied1 and any(a.startswith("hum50") for a in applied1)
   and any(a.startswith("denoise") for a in applied1),
   "auto policy applied dc + hum50 + denoise on the polluted take")
after = qc(out1, sr)
ok(after["hum"] is None and abs(after["dc"]) < 1e-3, "post-restore QC: hum gone, dc gone")

# ---- CLI: clean file = byte-copy passthrough; dirty file writes + reports
tmp = tempfile.mkdtemp(prefix="restore_")
cl = os.path.join(tmp, "clean.wav")
dt = os.path.join(tmp, "dirty.wav")
sf.write(cl, (clean * 0.9).astype(np.float32), sr, subtype="PCM_16")
sf.write(dt, np.clip(dirty, -1, 1).astype(np.float32), sr, subtype="PCM_24")
env = {**os.environ}
r1 = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "restore_audio.py"), cl],
                    capture_output=True, text=True, env=env, timeout=300)
j1 = json.loads([l for l in r1.stdout.splitlines() if l.startswith("RESTORE_JSON")][0][13:])
ok(r1.returncode == 0 and j1["applied"] == [] and
   open(j1["out"], "rb").read() == open(cl, "rb").read(),
   "CLI clean input: applied=[] and the output is a byte-copy")
r2 = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "restore_audio.py"), dt],
                    capture_output=True, text=True, env=env, timeout=300)
j2 = json.loads([l for l in r2.stdout.splitlines() if l.startswith("RESTORE_JSON")][0][13:])
y2, sr2 = sf.read(j2["out"])
ok(r2.returncode == 0 and len(j2["applied"]) >= 2 and sf.info(j2["out"]).subtype == "PCM_24"
   and len(y2) == len(dirty), "CLI dirty 24-bit input: fixes applied, 24-bit + length preserved")
ok(float(np.abs(y2).max()) <= 0.999 + 1e-4, "repair never creates clipping")

# ---- real-stem QC leg (shape sanity on product material)
stem = os.path.join(ROOT, "songs", "_anxrofo_stems", "vocals.wav")
if os.path.exists(stem):
    ys, srs = sf.read(stem, always_2d=False)
    rq = qc(ys[: min(len(ys), 60 * srs)], srs)
    ok(rq["peak_db"] <= 0.1 and rq["noise_floor_db"] < rq["rms_db"],
       f"real stem QC sane: peak {rq['peak_db']} floor {rq['noise_floor_db']} rms {rq['rms_db']}")
else:
    ok(True, "real stem absent — QC shape leg skipped green")

shutil.rmtree(tmp, ignore_errors=True)
print(f"PASS {N}/{N} restore battery")
