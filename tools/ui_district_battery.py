#!/usr/bin/env python3
"""UI DISTRICT BATTERY (THE HUNDRED pages 87-100) — camera guardians.

Runs the district's proof cameras against the REAL binary (peerless
--snapshot) and asserts the pixels each wave promised:

  P95 SOTADAW_SNAP_FOCUSRING : an accent ring outlines the play button
  P94 SOTADAW_SNAP_DROPVEIL  : the veil card renders (center-screen glass
                               brighter than the dimmed canvas around it)
  P89 SOTADAW_SNAP_ERRORS    : the error stack testifies bottom-right
                               (bad-red edge pixels present)

RED when a camera stops producing its png or the promised pixels vanish —
the district's waves cannot silently rot. SKIP (green) when the binary
predates a camera (strings-probe) so older checkouts never fake-fail.
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app", "build", "sotadaw_artefacts", "Release", "SOTA DAW")

if not os.path.exists(APP):
    print("ui district battery: SKIP (sotadaw binary not built)")
    sys.exit(0)

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("ui district battery: SKIP (PIL/numpy not available — use .venv/bin/python)")
    sys.exit(0)


def binary_has(literal: str) -> bool:
    out = subprocess.run(["strings", APP], capture_output=True, text=True)
    return literal in out.stdout


def shoot(env_key: str, png: str):
    d = tempfile.mkdtemp(prefix="ui_district_")
    env = dict(os.environ, SOTADAW_SONG="demo_track", **{env_key: "1"})
    subprocess.run([APP, "--snapshot", d], capture_output=True, text=True,
                   timeout=150, env=env)
    p = os.path.join(d, png)
    return np.array(Image.open(p).convert("RGB")).astype(int) if os.path.exists(p) else None


checks, fails = 0, []


def check(name, ok):
    global checks
    checks += 1
    print(("PASS  " if ok else "FAIL  ") + name)
    if not ok:
        fails.append(name)


# ---- P95: the focus ring wears accent around the play tile ----------------
if binary_has("SOTADAW_SNAP_FOCUSRING"):
    img = shoot("SOTADAW_SNAP_FOCUSRING", "focusring.png")
    check("p95 ring camera produced focusring.png", img is not None)
    if img is not None:
        # the ring lives on the play tile's outline (~x 222-268, y 40-76 at
        # 1680x1020); accent = violet-ish: blue notably above green
        band = img[36:82, 216:276]
        violet = ((band[:, :, 2] - band[:, :, 1] > 40) & (band[:, :, 2] > 120)).sum()
        check(f"p95 accent ring pixels present ({int(violet)})", violet > 40)

# ---- P94: the drop veil card renders over a dimmed canvas -----------------
if binary_has("SOTADAW_SNAP_DROPVEIL"):
    img = shoot("SOTADAW_SNAP_DROPVEIL", "dropveil.png")
    check("p94 veil camera produced dropveil.png", img is not None)
    if img is not None:
        card = img[430:600, 570:1110].mean()
        ring = img[150:250, 570:1110].mean()
        check(f"p94 veil card brighter than dimmed canvas ({card:.0f} vs {ring:.0f})",
              card > ring + 4)
        # the refusal row wears bad-red: red clearly above green in the card
        rows = img[430:620, 570:1110]
        red = ((rows[:, :, 0] - rows[:, :, 1] > 50) & (rows[:, :, 0] > 110)).sum()
        check(f"p94 refusal red present ({int(red)})", red > 30)

# ---- P89: the error stack testifies bottom-right --------------------------
if binary_has("SOTADAW_SNAP_ERRORS"):
    img = shoot("SOTADAW_SNAP_ERRORS", "errors.png")
    check("p89 stack camera produced errors.png", img is not None)
    if img is not None:
        region = img[700:1000, 1290:1670]
        red = ((region[:, :, 0] - region[:, :, 1] > 50) & (region[:, :, 0] > 110)).sum()
        check(f"p89 bad-edge pixels present ({int(red)})", red > 60)
else:
    print("      (p89 camera not in this binary yet — waves land in order)")

if checks == 0:
    print("ui district battery: SKIP (no district cameras in this binary)")
    sys.exit(0)
if fails:
    print(f"ui district battery: RED — {len(fails)}/{checks} failed: {fails}")
    sys.exit(1)
print(f"ui district battery: GREEN ({checks} checks)")
sys.exit(0)
