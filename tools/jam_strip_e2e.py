#!/usr/bin/env python3
"""THE JAM STRIP E2E — the band's conversation as material, through the REAL app.

The rig paints a synthetic conversation (2-bar opener, follow-tinted 1-bar turn,
amber repeat block, a punch spark, real progress) on the Live view and dumps
machine truth. Also guards THE VIEW LAW this strip's build exposed: switching to
Live must leave ZERO arrange lanes visible (they used to be re-shown by
resized() and painted over the launcher after any lane rebuild).

Usage: tools/jam_strip_e2e.py [runs]
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")


def run_once(idx):
    ipc = tempfile.mkdtemp(prefix="jamstrip_ipc_")
    out = tempfile.mkdtemp(prefix="jamstrip_png_")
    env = dict(os.environ, SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",
               SOTADAW_SNAP_JAMSTRIP="1", SOTADAW_IPC=ipc)
    A = []

    def ok(cond, msg):
        A.append((bool(cond), msg))

    try:
        p = subprocess.run([BIN, "--snapshot", out], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=90)
        line = next((l for l in p.stdout.splitlines()
                     if l.startswith("[jamstrip]")), "")
        d = dict(re.findall(r"(\w+)=(\S+)", line))
        ok(p.returncode == 0, f"app exited clean (rc {p.returncode})")
        ok(d.get("blocks") == "3" and d.get("follow") == "1"
           and d.get("repeats") == "1" and d.get("punches") == "1",
           f"the conversation is material: 3 blocks / 1 follow / 1 repeat / 1 punch ({line})")
        ok(d.get("playedBeats") == "10.0",
           f"progress maps phrase units -> beats through variable bars ({d.get('playedBeats')})")
        ok(d.get("liveVis") == "1" and d.get("padVis") == "1" and d.get("stripVis") == "1",
           "live view + pads + strip all up")
        ok(d.get("lanesVisible") == "0",
           f"THE VIEW LAW: zero arrange lanes over the launcher ({d.get('lanesVisible')})")
        ok(d.get("vibeIdx") == "2",
           f"jam.vibe.next from a PAD cycles the arc (2 presses: build -> breakdown; idx {d.get('vibeIdx')})")
        ok(os.path.exists(os.path.join(out, "jamstrip.png")),
           "the PNG proof exists")
        return A
    finally:
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    bad_total = 0
    for i in range(1, runs + 1):
        res = run_once(i)
        bad = [m for okk, m in res if not okk]
        if bad:
            bad_total += 1
            print(f"== run {i}/{runs}: FAIL")
            for okk, m in res:
                print(f"   {'ok ' if okk else 'FAIL'} {m}")
        else:
            print(f"== run {i}/{runs}: PASS ({len(res)}/{len(res)})")
    print("ALL GREEN" if bad_total == 0 else f"{bad_total} RUN(S) FAILED")
    sys.exit(1 if bad_total else 0)


if __name__ == "__main__":
    main()
