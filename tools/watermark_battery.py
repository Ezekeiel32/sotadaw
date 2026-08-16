#!/usr/bin/env python3
"""SOFT BINDING BATTERY — wave 82 (item 046). Synthetic; the mp3 leg
runs when ffmpeg is present (it is, on this box)."""
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import watermark as WM  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


SR = 44100
t = np.arange(SR * 50) / SR
rng = np.random.RandomState(4)
x = 0.25 * np.sin(2 * np.pi * 220 * t) + \
    0.2 * np.sin(2 * np.pi * 277 * t) + \
    0.15 * np.sin(2 * np.pi * 330 * t)
x += 0.1 * rng.randn(len(t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * t))
for h in np.arange(0, 50, 0.25):
    i = int(h * SR)
    x[i:i + 400] += 0.2 * rng.randn(400) * np.exp(-np.arange(400) / 80)
x = np.clip(x, -0.9, 0.9).reshape(-1, 1)
tmp = tempfile.mkdtemp(prefix="wmb_")
src = os.path.join(tmp, "src.wav")
marked = os.path.join(tmp, "marked.wav")
WM._write(src, x, SR, 2)

info = WM.embed(src, marked, 0xC0FFEE)
check("embed: >=4 payload repetitions on a 50s take",
      info["reps"] >= 4, str(info))
r = WM.detect(marked)
check("clean detect: exact payload", r.get("payload") == 0xC0FFEE, str(r))
check("no false positive on unmarked audio",
      not WM.detect(src)["found"])
xq, sr2, _ = WM._read(marked)
qp = os.path.join(tmp, "q.wav")
WM._write(qp, xq * 0.3, sr2, 2)
check("survives -10dB gain (differential design)",
      WM.detect(qp).get("payload") == 0xC0FFEE)

if shutil.which("ffmpeg"):
    mp3 = os.path.join(tmp, "m.mp3")
    back = os.path.join(tmp, "b.wav")
    subprocess.run(["ffmpeg", "-y", "-i", marked, "-b:a", "96k", mp3],
                   capture_output=True, check=True)
    subprocess.run(["ffmpeg", "-y", "-i", mp3, back],
                   capture_output=True, check=True)
    check("SURVIVES the re-encode (mp3 96k round trip — the whole "
          "point)", WM.detect(back).get("payload") == 0xC0FFEE)
else:
    print("[skip] mp3 leg (no ffmpeg)")

try:
    WM.embed(src, marked, 0x1)
    short = os.path.join(tmp, "s.wav")
    WM._write(short, x[:SR * 5], SR, 2)
    err = None
    try:
        WM.embed(short, marked, 0x1)
    except RuntimeError as e:
        err = str(e)
    check("too-short audio refuses LOUDLY (no undetectable binding)",
          err and "too short" in err)
except Exception as e:
    check("short-guard runs", False, str(e))

shutil.rmtree(tmp, ignore_errors=True)
print()
if FAILS:
    print(f"watermark_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("watermark_battery: ALL GREEN")
