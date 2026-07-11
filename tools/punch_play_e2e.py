#!/usr/bin/env python3
"""THE PUNCH-IN player half E2E — the crossfade at the bar line, through the
REAL binary's REAL JamPlayer (deviceless: pure DSP, no audio device touched).

The rig plays a 2s DC +0.5 phrase, punches a 1s DC -0.5 tail at frac 0.5, and
pumps the source by hand. Physics: a HARD swap at the line is a 1.0 step; the
16ms crossfade must step ~1/768 (~0.0013). Asserts: armed, pre/post plateau
means exact, max step < 0.02 anywhere (no click, ever), the sign crossing at
the fade's midpoint, and the >100ms-late punch DROPPED.

B6 TAIL + GAIN legs (same camera): a phrase whose wav runs PAST its musical
length must ring that remainder UNDER the next phrase (overlap-add: DC 0.5
tail 0.25 into DC 0.5 -> a 0.75 plateau), and the BAND fader must scale the
whole wire (gain 0.5 halves every plateau: 0.25 / 0.375 / 0.25).

Usage: tools/punch_play_e2e.py [runs]
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
    ipc = tempfile.mkdtemp(prefix="punchplay_ipc_")
    out = tempfile.mkdtemp(prefix="punchplay_png_")
    env = dict(os.environ, SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",
               SOTADAW_SNAP_PUNCHPLAY="1", SOTADAW_IPC=ipc)
    A = []

    def ok(cond, msg):
        A.append((bool(cond), msg))

    try:
        p = subprocess.run([BIN, "--snapshot", out], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=90)
        line = next((l for l in p.stdout.splitlines()
                     if l.startswith("[punchplay]")), "")
        d = dict(re.findall(r"(\w+)=(\S+)", line))
        ok(p.returncode == 0, f"app exited clean (rc {p.returncode})")
        ok(d.get("armed") == "1", f"punch ARMED ({line})")
        ok(abs(float(d.get("pre", "0")) - 0.5) < 0.02,
           f"pre-line plateau +0.5 ({d.get('pre')})")
        ok(abs(float(d.get("post", "0")) + 0.5) < 0.02,
           f"post-line plateau -0.5 ({d.get('post')})")
        ok(float(d.get("maxStep", "1")) < 0.02,
           f"NO CLICK: max step {d.get('maxStep')} (hard swap would be 1.0)")
        ok(44000 <= int(d.get("crossAt", "0")) <= 45500,
           f"the turn happens AT the bar line ({d.get('crossAt')})")
        ok(d.get("lateDrop") == "1", "a >100ms-late punch is DROPPED (moment gone)")
        ok(abs(float(d.get("tailHead", "0")) - 0.25) < 0.02,
           f"BAND fader halves the wire ({d.get('tailHead')} ~ 0.25)")
        ok(abs(float(d.get("tailMix", "0")) - 0.375) < 0.02,
           f"the tail RINGS UNDER the next phrase ({d.get('tailMix')} ~ 0.375)")
        ok(abs(float(d.get("tailAfter", "0")) - 0.25) < 0.02,
           f"the tail rings OUT, the phrase stands alone ({d.get('tailAfter')} ~ 0.25)")
        return A
    finally:
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    fails_total = 0
    for i in range(1, runs + 1):
        res = run_once(i)
        bad = [m for okk, m in res if not okk]
        if bad:
            fails_total += 1
            print(f"== run {i}/{runs}: FAIL")
            for okk, m in res:
                print(f"   {'ok ' if okk else 'FAIL'} {m}")
        else:
            print(f"== run {i}/{runs}: PASS ({len(res)}/{len(res)})")
    print("ALL GREEN" if fails_total == 0 else f"{fails_total} RUN(S) FAILED")
    sys.exit(1 if fails_total else 0)


if __name__ == "__main__":
    main()
