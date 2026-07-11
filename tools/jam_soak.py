#!/usr/bin/env python3
"""R6/R19 THE SOAK — the JAM's reliability measured, not assumed.

Boots the real sotadaw peerless, drives REAL audio through the live device for
a minute (virtual midi sources firing notes -> synth voices render in the
device callback — the same path the hotplug rig proved SOUNDS), and reads the
ears bus (ipc/ears.jsonl, the ONE production writer) the whole time:

  gates: feed alive the whole soak (max frame gap <= 1.5s)
         >= 8 frames/second sustained (the 10Hz tap held)
         xruns delta == 0   (the audio thread never starved)
         cpu p95 <= 0.90    (headroom held under polyphony)

Usage: python3 tools/jam_soak.py [seconds=60] [voices=3]
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")
M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")
SECS = int(sys.argv[1]) if len(sys.argv) > 1 else 60
VOICES = int(sys.argv[2]) if len(sys.argv) > 2 else 3


def main():
    scratch = tempfile.mkdtemp(prefix="jam_soak_")
    ipc = os.path.join(scratch, "ipc")
    os.makedirs(ipc, exist_ok=True)
    env = dict(os.environ,
               SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",
               SOTADAW_HOTPLUG_E2E=str(SECS + 25),
               SOTADAW_IPC=ipc, SOTADAW_SONG="demo_track")
    app = subprocess.Popen([APP, "--snapshot", os.path.join(scratch, "snap")],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           text=True, env=env)
    armed = threading.Event()

    def reader():
        for line in app.stdout:
            if line.startswith("HOTPLUG_ARMED"):
                armed.set()

    threading.Thread(target=reader, daemon=True).start()
    ears = os.path.join(ipc, "ears.jsonl")
    kids = []
    try:
        if not armed.wait(30):
            print("SOAK: FAIL — app never armed (stale binary?)")
            return 1
        time.sleep(2.0)                          # boot device sweep settles
        for k in range(VOICES):                  # the band walks in one by one
            kids.append(subprocess.Popen(
                [M1, "midi-src", f"soak{k}", str(SECS), "120"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            time.sleep(0.4)
        pos = os.path.getsize(ears) if os.path.exists(ears) else 0
        t_end = time.time() + SECS
        ts, cpus, xr = [], [], []
        while time.time() < t_end:
            time.sleep(0.25)
            if not os.path.exists(ears):
                continue
            size = os.path.getsize(ears)
            if size <= pos:
                continue
            with open(ears) as f:
                f.seek(pos)
                chunk = f.read(size - pos)
            nl = chunk.rfind("\n")
            if nl < 0:
                continue
            pos += len(chunk[:nl + 1].encode())
            for line in chunk[:nl].splitlines():
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                ts.append(float(d.get("t", 0)))
                cpus.append(float(d.get("cpu", 0)))
                xr.append(int(d.get("xruns", 0)))
        for k in kids:
            k.wait(timeout=15)
        if len(ts) < 10:
            print(f"SOAK: FAIL — only {len(ts)} ears frames in {SECS}s (feed dead?)")
            return 1
        gaps = [b - a for a, b in zip(ts, ts[1:])]
        cpus.sort()
        rate = len(ts) / (ts[-1] - ts[0]) if ts[-1] > ts[0] else 0.0
        maxgap = max(gaps) if gaps else 0.0
        dxr = xr[-1] - xr[0]
        p95 = cpus[int(0.95 * (len(cpus) - 1))]
        print(f"  frames {len(ts)}  rate {rate:.1f}/s  max gap {maxgap * 1000:.0f} ms")
        print(f"  xruns {xr[0]} -> {xr[-1]}  (delta {dxr})   cpu p50 "
              f"{cpus[len(cpus) // 2]:.2f}  p95 {p95:.2f}")
        checks = [("feed alive (max gap <= 1.5s)", maxgap <= 1.5),
                  ("tap held (>= 8 frames/s)", rate >= 8.0),
                  ("zero xruns under load", dxr == 0),
                  ("cpu p95 <= 0.90", p95 <= 0.90)]
        ok = True
        for name, c in checks:
            print(f"  [{'PASS' if c else 'FAIL'}] {name}")
            ok = ok and c
        print("JAM SOAK:", "PASS — the audio thread held for the whole set"
              if ok else "FAIL")
        return 0 if ok else 1
    finally:
        for k in kids:
            if k.poll() is None:
                k.kill()
        app.terminate()
        try:
            app.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app.kill()


if __name__ == "__main__":
    sys.exit(main())
