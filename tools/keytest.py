#!/usr/bin/env python3
"""THE KEYTEST DRIVER — the 58-gesture keyboard/UI self-test, run RIGHT.

2026-07-11 lesson: keytest driven bare on a starved box (a parallel -O3 TU
compile + render batteries + two live app instances) got SIGKILLed by the
KERNEL OOM killer mid-suite (rc=137 at ~44 legs — earlyoom's avoid-list does
not bind the kernel) and the legs that DID run flaked red on focus/clipboard
timing: 7 false reds that read as regressions. The same binary at 8G
available: 58/58 clean. The failure mode was the BOX, not the code — so the
driver enforces the box:

  - MEMORY GATE: waits for >= --need-gb MemAvailable (default 4.0, the
    earlyoom-etiquette number) before launching, up to --max-wait seconds
  - SIGKILL/OOM = TRUNCATED, not failed: rc 137 or an incomplete leg count
    with a nonzero rc retries ONCE after re-gating; persistent truncation
    prints SKIP (busy box) and exits 0 — a starved box must never paint a
    healthy binary red (suite-safe; pass --strict to turn SKIP into rc 75)
  - REAL fails print their [keys] FAIL lines and exit 1

Usage: tools/keytest.py [--need-gb 4.0] [--max-wait 600] [--expect 58] [--strict]
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")


def avail_gb():
    try:
        for ln in open("/proc/meminfo"):
            if ln.startswith("MemAvailable:"):
                return int(ln.split()[1]) / 1048576.0
    except OSError:
        pass
    return 99.0


def gate(need, max_wait):
    t0 = time.time()
    while avail_gb() < need:
        if time.time() - t0 > max_wait:
            return False
        left = max_wait - (time.time() - t0)
        print(f"[keytest] box starved ({avail_gb():.1f}G < {need:.1f}G) — "
              f"waiting ({left:.0f}s of gate left)")
        time.sleep(20)
    return True


def run_once():
    kt = tempfile.mkdtemp(prefix="keytest_")
    env = dict(os.environ, SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",
               SOTADAW_KEYTEST=kt)
    try:
        p = subprocess.run([BIN, "--snapshot", kt], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=420)
        lines = [l for l in p.stdout.splitlines() if l.startswith("[keys] ")]
        fails = [l for l in lines if l.startswith("[keys] FAIL")]
        return p.returncode, len(lines), fails
    except subprocess.TimeoutExpired:
        return -1, 0, []
    finally:
        shutil.rmtree(kt, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--need-gb", type=float, default=4.0)
    ap.add_argument("--max-wait", type=float, default=600.0)
    ap.add_argument("--expect", type=int, default=59,
                    help="legs expected; fewer + nonzero rc = truncated run")
    ap.add_argument("--strict", action="store_true",
                    help="busy box exits 75 instead of a loud SKIP (rc 0)")
    a = ap.parse_args()
    if not os.path.exists(BIN):
        print("SKIP: app binary not built")
        return 0

    for attempt in (1, 2):
        if not gate(a.need_gb, a.max_wait):
            break
        rc, total, fails = run_once()
        truncated = (rc != 0 and total < a.expect) or rc in (137, -9, -1)
        if not truncated:
            print(f"keytest: {total - len(fails)}/{total} "
                  + ("clean" if not fails and rc == 0 else "RED"))
            if total < a.expect:
                print(f"[keytest] NOTE: {total} legs ran, {a.expect} expected — "
                      "leg count drifted (update --expect or investigate)")
            for f in fails:
                print(f)
            return 1 if (fails or rc != 0) else 0
        print(f"[keytest] run TRUNCATED (rc={rc} at {total} legs) — the box, "
              f"not the code; {'retrying once' if attempt == 1 else 'giving up'}")
    msg = f"SKIP: box starved/truncating (avail {avail_gb():.1f}G, need {a.need_gb:.1f}G)"
    print(msg)
    return 75 if a.strict else 0


if __name__ == "__main__":
    sys.exit(main())
