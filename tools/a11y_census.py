#!/usr/bin/env python3
"""THE SPOKEN DESK census — accessibility guardian (suite leg).

Boots the REAL app peerless (--snapshot, no window reaches a screen) with
SOTADAW_A11Y_CENSUS=1: the census walks the live component tree and counts
interactive widgets (buttons/sliders/combos/editors) a screen reader can
NAME (getTitle > button text > name). 2026-07-25 baseline: 128 interactive,
128 named — every lane fader/pan/mute/solo speaks its TRACK's name, the
prompt bar is "Ask the agent", genre/model/song/snap/swing/filters all
titled.

RED when any interactive control goes unnamed (the dump prints the exact
class + bounds = the fix worklist) or when the tree shrinks below the
sanity floor (an empty walk must never fake green).
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app", "build", "sotadaw_artefacts", "Release", "SOTA DAW")
FLOOR_INTERACTIVE = 60          # tree-sanity: a broken walk can't fake a green

if not os.path.exists(APP):
    print("a11y census: SKIP (sotadaw binary not built)")
    sys.exit(0)

snap = tempfile.mkdtemp(prefix="a11y_snap_")
env = dict(os.environ, SOTADAW_A11Y_CENSUS="1")
r = subprocess.run([APP, "--snapshot", snap], capture_output=True, text=True,
                   timeout=120, env=env)
line = next((l for l in r.stdout.splitlines() if l.startswith("[a11y] ")), "")
unnamed_rows = [l for l in r.stdout.splitlines() if l.startswith("[a11y-unnamed]")]
if not line:
    print("a11y census: RED — no census line from the app")
    print((r.stdout + r.stderr)[-600:])
    sys.exit(1)
stats = dict(kv.split("=") for kv in line.replace("[a11y] ", "").split()
             if "=" in kv)
interactive = int(stats.get("interactive", 0))
unnamed = int(stats.get("unnamed", 999))
print(line)
if "focusable" in stats:            # p95 companion metric (informational for now:
    # ring + traversal land first; the gate hardens once the sweep completes)
    print(f"a11y census: focusable {stats['focusable']}/{interactive} interactive "
          "controls reachable by keyboard")
for row in unnamed_rows[:20]:
    print(row)
if interactive < FLOOR_INTERACTIVE:
    print(f"a11y census: RED — tree too small ({interactive} < {FLOOR_INTERACTIVE}; "
          "the walk is broken, not the desk)")
    sys.exit(1)
if unnamed:
    print(f"a11y census: RED — {unnamed} interactive control(s) a screen reader "
          "cannot name (rows above = the worklist; title them where they are built)")
    sys.exit(1)
print(f"a11y census: GREEN — all {interactive} interactive controls speak")
sys.exit(0)
