#!/usr/bin/env python3
"""sing OOM-gate battery (§7.6) — the voice-model load must be GATED:
a machine-wide flock QUEUES concurrent renders (two HUM presses = 2x ~3GB at
the same instant) and a memory preflight SKIPS with one actionable STDOUT line
instead of a silent OOM kill (f158: no vocals, no error, nothing to act on).

Pure: no voice bank, no models, no GPU — gate logic only.

Usage: python3 tools/sing_preflight_battery.py
"""
import io
import os
import subprocess
import sys
import time
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)


def release(sing):
    """flock is per open-file-description: close OUR fd between checks or the
    battery deadlocks itself on the next acquire."""
    if sing._SING_LOCK is not None:
        try:
            sing._SING_LOCK.close()
        except Exception:
            pass
        sing._SING_LOCK = None


def gate(sing, **env):
    """Run _sing_gate under env overrides; return (exited, stdout_text)."""
    old = {k: os.environ.get(k) for k in env}
    os.environ.update({k: str(v) for k, v in env.items()})
    buf, exited = io.StringIO(), False
    try:
        with redirect_stdout(buf):
            sing._sing_gate()
    except SystemExit:
        exited = True
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return exited, buf.getvalue()


def hold_lock(path, secs):
    """Subprocess that flocks the sing lock for secs; returns once it HOLDS."""
    p = subprocess.Popen(
        [sys.executable, "-c",
         "import fcntl,sys,time; f=open(sys.argv[1],'w'); fcntl.flock(f,fcntl.LOCK_EX);"
         " print('HELD',flush=True); time.sleep(float(sys.argv[2]))",
         path, str(secs)],
        stdout=subprocess.PIPE, text=True)
    p.stdout.readline()
    return p


def main():
    import sing
    lockp = os.path.join(ROOT, "agent", "ipc", "sing.lock")

    # 1-2) memory measurement: plausible, and the dep-free fallback source agrees
    gb = sing._mem_avail_gb()
    ok(isinstance(gb, float) and 0.05 < gb < 4096, "mem: measurable, plausible GB")
    raw = None
    for line in open("/proc/meminfo"):
        if line.startswith("MemAvailable:"):
            raw = int(line.split()[1]) / (1 << 20)
            break
    ok(raw is not None and abs(raw - gb) < 1.5,
       "mem: /proc/meminfo fallback agrees with the psutil path")

    # 3) forced-high floor -> graceful skip ON STDOUT (both MCP lanes read stdout only)
    exited, out = gate(sing, SOTADAW_SING_MINGB="99999")
    ok(exited and "SINGING SKIPPED" in out and "GB" in out,
       "preflight: short RAM -> actionable skip line on stdout")
    release(sing)

    # 4-5) trivial floor passes; <=0 disables the check entirely
    exited, out = gate(sing, SOTADAW_SING_MINGB="0.01")
    ok(not exited, "preflight: enough RAM -> proceeds")
    release(sing)
    exited, out = gate(sing, SOTADAW_SING_MINGB="0")
    ok(not exited, "preflight: 0 disables the floor (force lane)")
    release(sing)

    # 6) mutex QUEUES: a holder keeps the flock ~2s; the gate waits it out, then proceeds
    holder = hold_lock(lockp, 2.0)
    t0 = time.time()
    exited, out = gate(sing, SOTADAW_SING_MINGB="0", SOTADAW_SING_LOCK_WAIT="30")
    dt = time.time() - t0
    ok(not exited and dt >= 1.2, f"mutex: concurrent render QUEUED ({dt:.1f}s) then proceeded")
    release(sing)
    holder.wait()

    # 7) mutex wait cap: holder outlives the cap -> graceful skip naming the lock
    holder = hold_lock(lockp, 6.0)
    exited, out = gate(sing, SOTADAW_SING_MINGB="0", SOTADAW_SING_LOCK_WAIT="1")
    ok(exited and "SINGING SKIPPED" in out and "lock" in out,
       "mutex: wait cap exceeded -> graceful skip")
    release(sing)
    holder.kill()
    holder.wait()

    # 8) wiring: render() gates BEFORE the weights load. The OOM class is model
    #    SESSIONS (InferenceSession pulls the voice bank into RAM), not the ort
    #    import — and the gate call is need_gb/cuda-aware (it reads
    #    ort.get_available_providers()), so it legitimately follows the import.
    #    The invariant that must never break: gate first, weights after.
    import inspect
    src8 = inspect.getsource(sing.render)
    gi, si = src8.find("_sing_gate("), src8.find("InferenceSession")
    ok(gi != -1 and (si == -1 or gi < si),
       "wiring: render() gates before any model session loads")

    # 9) CLI end-to-end: skip is one actionable stdout line, rc!=0, NO traceback
    #    (bank present -> the gate fires; bank absent -> require_bank's line, same law)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sing.py"),
                        "render", "__nosuchsong", "vocals"],
                       capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, SOTADAW_SING_MINGB="99999"))
    graceful = r.returncode != 0 and "Traceback" not in (r.stdout + r.stderr)
    surfaced = "SINGING SKIPPED" in r.stdout or "VOICE BANK NOT INSTALLED" in r.stdout
    ok(graceful and surfaced, "cli: graceful skip surfaces on STDOUT (no traceback)")

    # 10) W99 THE PARTIAL-VOCAL GUARD: the window synth is wrapped — a
    # vocoder OOM exits with an actionable SOTADAW_SING_CHUNK_S line, never
    # a bare traceback or a half-sung wav (tripwire against deletion)
    src = open(os.path.join(ROOT, "tools", "sing.py")).read()
    body = src[src.index("SELF-HEALING WINDOWS"):]
    ok("THE PARTIAL-VOCAL GUARD" in src
       and "self-split" in src and "queue[:0] = [grp[:mid], grp[mid:]]" in src
       and body.index("try:") < body.index("ac.run(None, feed)"),
       "W99/W100: self-healing windows armed (OOM splits + retries; 1-note floor guarded)")

    print(f"sing-preflight battery: {PASS}/{PASS + len(FAIL)} "
          + ("clean" if not FAIL else "RED"))
    for f in FAIL:
        print("FAIL:", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
