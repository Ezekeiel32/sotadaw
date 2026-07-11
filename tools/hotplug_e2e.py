#!/usr/bin/env python3
"""R4 THE CONNECTION LAW — plug ANY midi gear -> playing FAST, measured.

Boots the real sotadaw binary peerless (--snapshot; never touches the screen)
with SOTADAW_HOTPLUG_E2E=<hold s>. Then, N times, births a brand-new virtual
ALSA midi source (m1 midi-src = a new seq client, exactly what a USB cable
does to the kernel announce port) that fires notes immediately, and reads the
app's stamps off stdout:

  MIDISRC_UP     t0  the "cable" appeared
  HOTPLUG_LIVE   t1  the watcher enabled+monitored+routed it (plug -> LIVE)
  HOTPLUG_MSG    t2  a note SOUNDED through it        (plug -> PLAYING)

Gates: p95(live) <= 500ms proves the ANNOUNCE wake (the 2s poll belt alone
cannot pass this); p95(sound) <= 900ms; every probe heard.

Usage: python3 tools/hotplug_e2e.py [N]
"""
import os
import re
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")
M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 5


def main():
    scratch = tempfile.mkdtemp(prefix="hotplug_e2e_")
    env = dict(os.environ,
               SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",
               SOTADAW_HOTPLUG_E2E=str(10 + 6 * N),
               SOTADAW_IPC=os.path.join(scratch, "ipc"),
               SOTADAW_SONG="demo_track")
    os.makedirs(env["SOTADAW_IPC"], exist_ok=True)
    app = subprocess.Popen([APP, "--snapshot", os.path.join(scratch, "snap")],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           text=True, env=env)
    stamps, lock = [], threading.Lock()

    def reader():
        for line in app.stdout:
            line = line.strip()
            for kind in ("HOTPLUG_ARMED", "HOTPLUG_LIVE", "HOTPLUG_MSG"):
                if line.startswith(kind):
                    mm = re.search(r"t_ms=(\d+)", line)
                    if "-v" in sys.argv:
                        print("   [app]", line)
                    with lock:
                        stamps.append((kind, int(mm.group(1)) if mm else 0))

    threading.Thread(target=reader, daemon=True).start()

    def wait_for(kind, after_idx, timeout):
        t_end = time.time() + timeout
        while time.time() < t_end:
            with lock:
                for i in range(after_idx, len(stamps)):
                    if stamps[i][0] == kind:
                        return i, stamps[i][1]
            time.sleep(0.005)
        return -1, 0

    try:
        if wait_for("HOTPLUG_ARMED", 0, 30)[0] < 0:
            print("FAIL: app never armed (binary stale? build first)")
            return 1
        time.sleep(2.5)          # let the boot device sweep settle (boot != news)
        lives, sounds = [], []
        for k in range(N):
            with lock:
                idx0 = len(stamps)
            t0 = time.time() * 1000.0
            src = subprocess.Popen([M1, "midi-src", f"hotprobe{k}", "4", "30"],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
            i1, t1 = wait_for("HOTPLUG_LIVE", idx0, 6)
            i2, t2 = wait_for("HOTPLUG_MSG", max(i1, idx0), 6)
            src.wait(timeout=10)
            if t1:
                lives.append(t1 - t0)
            if t2:
                sounds.append(t2 - t0)
            print(f"  probe {k}: plug->live "
                  f"{(t1 - t0):6.0f} ms   plug->SOUND {(t2 - t0):6.0f} ms"
                  if t1 and t2 else f"  probe {k}: MISSED (live={t1} msg={t2})")
            time.sleep(1.2)      # distinct clients; let unplug settle
        ok = len(lives) == N and len(sounds) == N
        if ok:
            lives.sort(), sounds.sort()
            p95l = lives[int(0.95 * (N - 1))]
            p95s = sounds[int(0.95 * (N - 1))]
            print(f"plug->live   p50 {lives[N // 2]:.0f} ms  p95 {p95l:.0f} ms")
            print(f"plug->SOUND  p50 {sounds[N // 2]:.0f} ms  p95 {p95s:.0f} ms")
            ok = p95l <= 500 and p95s <= 900
            print("HOTPLUG E2E:", "PASS — the announce wake is live"
                  if ok else "FAIL — latency gate missed (poll-belt speed?)")
        else:
            print(f"HOTPLUG E2E: FAIL — heard {len(lives)}/{N} live, "
                  f"{len(sounds)}/{N} sound")
        return 0 if ok else 1
    finally:
        app.terminate()
        try:
            app.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app.kill()


if __name__ == "__main__":
    sys.exit(main())
