#!/usr/bin/env python3
"""R6 THE RELIABILITY CHIP — reader-side positive control, through the real binary.

The writer side is proven by render negative controls (every ears.jsonl frame
carries xruns:0 cpu:0.00 — EarsTapPlugin, commit 6f41152). This rig proves the
READER: the UI tails the ears bus and the chip fires on FRESH xruns only —
never on the session baseline, never on a device-restart count DROP.

Boots the real sotadaw peerless (--snapshot + SOTADAW_HOTPLUG_E2E hold rig),
feeds synthetic ears.jsonl frames into its isolated SOTADAW_IPC, and reads
EARSCHIP stamps (SOTADAW_EARS_E2E=1) off stdout:

  frame xruns=7   (first sight)     -> baseline, NO stamp     [boot noise law]
  frame xruns=10  (+3)              -> EARSCHIP fresh=3
  frame xruns=2   (count DROPPED)   -> re-baseline, NO stamp  [device restart law]
  frame xruns=3   (+1)              -> EARSCHIP fresh=4       [accumulates in window]
  ~8.5s silence                     -> EARSCHIP clear         [the flash decays]

Usage: python3 tools/ears_chip_e2e.py
"""
import os
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")


def main():
    scratch = tempfile.mkdtemp(prefix="ears_chip_e2e_")
    ipc = os.path.join(scratch, "ipc")
    os.makedirs(ipc, exist_ok=True)
    feed = os.path.join(scratch, "feed.jsonl")   # rig-owned: the app's OWN live tap
    env = dict(os.environ,                       # writes ipc/ears.jsonl at 10Hz even
               SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",   # idle — one writer per file
               SOTADAW_HOTPLUG_E2E="20", SOTADAW_EARS_E2E=feed,
               SOTADAW_IPC=ipc, SOTADAW_SONG="demo_track")
    app = subprocess.Popen([APP, "--snapshot", os.path.join(scratch, "snap")],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           text=True, env=env)
    stamps, lock = [], threading.Lock()

    def reader():
        for line in app.stdout:
            line = line.strip()
            if line.startswith(("EARSCHIP", "HOTPLUG_ARMED")):
                if "-v" in sys.argv:
                    print("   [app]", line)
                with lock:
                    stamps.append(line)

    threading.Thread(target=reader, daemon=True).start()

    def wait_for(prefix, timeout):
        t_end = time.time() + timeout
        seen = 0
        while time.time() < t_end:
            with lock:
                for s in stamps[seen:]:
                    if s.startswith(prefix):
                        return s
                seen = len(stamps)
            time.sleep(0.02)
        return None

    def frame(xruns, cpu=0.10):
        with open(feed, "a") as f:
            f.write('{"t":0,"beat":0,"sec":0,"playing":true,"rms_db":[-20,-20],'
                    '"peak_db":[-9,-9],"dbtp_q":-9.0,"bands_db":[-20,-30,-40,-50],'
                    f'"crest_db":11.0,"xruns":{xruns},"cpu":{cpu:.2f}}}\n')

    fails = []

    def check(name, ok):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            fails.append(name)

    try:
        if wait_for("HOTPLUG_ARMED", 30) is None:
            print("FAIL: app never armed (stale binary? build first)")
            return 1
        time.sleep(1.0)
        frame(7)                                   # first sight = baseline
        time.sleep(0.8)
        with lock:
            check("baseline frame is SILENT (boot-noise law)",
                  not any(s.startswith("EARSCHIP") for s in stamps))
        frame(10)                                  # +3 fresh
        s = wait_for("EARSCHIP fresh=3", 4)
        check("fresh xruns flash the chip (fresh=3)", s is not None)
        frame(2)                                   # count dropped: device restart
        time.sleep(0.8)
        with lock:
            check("count DROP re-baselines silently (restart law)",
                  not any("fresh=" in s and "fresh=3" not in s for s in stamps
                          if s.startswith("EARSCHIP")))
        frame(3)                                   # +1 on the new baseline
        s = wait_for("EARSCHIP fresh=4", 4)
        check("fresh xruns accumulate in the window (fresh=4)", s is not None)
        s = wait_for("EARSCHIP clear", 11)
        check("the flash decays (clear)", s is not None)
        print("EARS CHIP E2E:", "PASS — the reliability chip reads the bus"
              if not fails else f"FAIL — {fails}")
        return 0 if not fails else 1
    finally:
        app.terminate()
        try:
            app.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app.kill()


if __name__ == "__main__":
    sys.exit(main())
