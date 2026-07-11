#!/usr/bin/env python3
"""B6 THE BANDSTAND E2E — the whole live-band lifecycle through the REAL binary.

The SOTADAW_SNAP_JAMLIVE camera presses JAM (an ENDLESS set: real scheduler,
real m1 renders), watches the pane warm, chains real phrases on the REAL
JamPlayer (deviceless pump), flips the vibe LIVE through the box, ends the set
gracefully through the button, and the take lands KEPT in the shop. This
driver asserts every milestone plus the kept take's musical truth (both vibes
in its sections, buses riding, real material) and cleans the shop after.

Usage: tools/jam_pod_e2e.py [runs]
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")
SONGS = os.path.join(ROOT, "songs")


def run_once(idx):
    ipc = tempfile.mkdtemp(prefix="jampod_ipc_")
    out = tempfile.mkdtemp(prefix="jampod_png_")
    env = dict(os.environ, SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",
               SOTADAW_SNAP_JAMLIVE="1", SOTADAW_IPC=ipc)
    before = set(glob.glob(os.path.join(SONGS, "jam_house_*.json")))
    A = []

    def ok(cond, msg):
        A.append((bool(cond), msg))

    try:
        p = subprocess.run([BIN, "--snapshot", out], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=180)
        lines = {m.group(1): m.group(2) for m in
                 (re.match(r"\[jamlive\] (\w+) (.*)", l)
                  for l in p.stdout.splitlines()) if m}

        def field(stage, key):
            d = dict(re.findall(r"(\w+)=(\S+)", lines.get(stage, "")))
            return d.get(key)

        ok(p.returncode == 0, f"app exited clean (rc {p.returncode})")
        ok("TIMEOUT" not in lines, "no timeout: the lifecycle completed")
        ok(field("begin", "btn") == "STOP" and field("begin", "running") == "1",
           f"JAM press -> the endless set is LIVE ({lines.get('begin')})")
        ok(field("begin", "phrases") == "0",
           "begin = sound check (no phrases yet, the pane warms)")
        ok(int(field("flip", "phrases") or 0) >= 2,
           f"real phrases chained before the flip ({field('flip', 'phrases')})")
        ok(field("stop", "ending") == "1" and field("stop", "btn") == "ENDING",
           f"graceful STOP: the band ENDS ON THE PHRASE ({lines.get('stop')})")
        kept = field("done", "kept") or "-"
        ok(field("done", "running") == "0" and field("done", "btn") == "JAM",
           f"the set closed and the pod is idle again ({lines.get('done')})")
        ok(kept.startswith("jam_house_"), f"the take was KEPT ({kept})")
        take = os.path.join(SONGS, kept + ".json")
        if os.path.exists(take):
            d = json.load(open(take))
            secs = [s["name"] for s in d.get("sections", [])]
            ok(any(n.startswith("build") for n in secs)
               and any(n.startswith("breakdown") for n in secs),
               f"the LIVE vibe flip is in the take's sections ({secs})")
            ok(bool(d.get("buses")) and bool(d.get("tracks")),
               "the take carries buses + real material")
        else:
            ok(False, f"kept take file missing ({take})")
        return A
    finally:
        for f in set(glob.glob(os.path.join(SONGS, "jam_house_*.json"))) - before:
            os.remove(f)
        for f in (os.path.join(SONGS, "_jamlive.json"),):
            if os.path.exists(f):
                os.remove(f)
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 1
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
