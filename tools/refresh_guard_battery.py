#!/usr/bin/env python3
"""THE REFRESH-GUARD BATTERY — pure proof of the self-refresh storm guard (2026-07-12).

Chezy screenshotted the chat feed alternating "agent online - 121 tools ready" /
"sidecar self-refresh: new code landed" ~7x in a minute. Cause: _self_refresh_due()
fired on ANY mtime bump, so with parallel sessions saving sidecar.py every few
seconds, every save was an instant execv — residents reaped + re-warmed, ipc/alive
blinked, the UI's 6s watchdog tripped and read out a STALE crash log as a fresh
"agent CRASHED: BrokenPipeError". Two diseases, one root.

The guard: a refresh needs (a) the disk mtime SETTLED (>=3s old — never exec into a
half-written file mid-save) and (b) >=60s since the last rebirth (ipc/.self_refresh_stamp,
which survives execv). A burst of saves costs ONE reload after the dust settles.

Pure: monkeypatches _SELF_PATH/_REFRESH_STAMP onto scratch files, so it never touches
the real sidecar.py (the LIVE daemon watches that file — touching it would refresh
Chezy's running session mid-work) and never spawns a daemon.

    python3 tools/refresh_guard_battery.py
"""
import importlib.util
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = tempfile.mkdtemp(prefix="refresh_guard_")

# isolate BEFORE import: IPC must never point at the real mailbox
os.environ["SOTADAW_IPC"] = SCRATCH
os.environ["SOTADAW_NO_UPLINK"] = "1"
os.environ["SOTADAW_NO_PREWARM"] = "1"

_spec = importlib.util.spec_from_file_location("_sc", os.path.join(ROOT, "agent", "sidecar.py"))
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)            # module level only — main() never runs

PASS = FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    ok = got == want
    PASS, FAIL = PASS + ok, FAIL + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {name}: got {got}, want {want}")


def age(path, seconds):
    """backdate a file's mtime by `seconds` (no sleeping in a battery)."""
    t = time.time() - seconds
    os.utime(path, (t, t))


fake = os.path.join(SCRATCH, "sidecar_under_test.py")
stamp = os.path.join(SCRATCH, ".self_refresh_stamp")
open(fake, "w").write("# v1\n")

# the running daemon loaded its image LONG ago (a save must look newer than it —
# backdating a file to fake "settled" without this makes it older than the image
# and the guard rightly says no: that mistake cost this battery its first run)
BOOTED_AGO = 1000.0

sc._SELF_PATH = fake
sc._REFRESH_STAMP = stamp
sc._SELF_MTIME = time.time() - BOOTED_AGO

print("== THE REFRESH-GUARD BATTERY ==")

# 1. quiet disk: the running image IS the disk image
age(fake, BOOTED_AGO)
check("unchanged file never refreshes", sc._self_refresh_due(), False)

# 2. a save that is still landing (mtime = now) must NOT be exec'd into:
#    a half-written file would exec a SyntaxError into the daemon's own PID
open(fake, "w").write("# v2\n")
check("fresh save (<3s) waits for the file to settle", sc._self_refresh_due(), False)

# 3. ...and once it has settled, it ships
age(fake, 5)
check("settled save (>=3s) refreshes", sc._self_refresh_due(), True)

# 4. THE STORM: the rebirth stamps, and further saves inside the cooldown are held.
#    (this is the whole disease — 7 execvs in a minute became 7 chat lines)
open(stamp, "w").close()
open(fake, "w").write("# v3\n")
age(fake, 5)                     # settled, but the cooldown is hot
check("save inside the 60s cooldown is HELD", sc._self_refresh_due(), False)

# 5. a whole burst inside the cooldown is still held — ONE reload, not seven
for i in range(7):
    open(fake, "w").write(f"# burst {i}\n")
    age(fake, 5)
check("a 7-save burst still refuses to storm", sc._self_refresh_due(), False)

# 6. cooldown expired: real new code still reaches the daemon (staleness must heal)
age(stamp, 90)
check("after the cooldown, new code ships", sc._self_refresh_due(), True)

# 7. a missing stamp (first refresh of a life) must not block
os.remove(stamp)
check("no stamp yet (first rebirth) refreshes", sc._self_refresh_due(), True)

# 8. a vanished file must not crash the loop (OSError -> False, never an exception)
os.remove(fake)
check("deleted file degrades to False (no throw)", sc._self_refresh_due(), False)

shutil.rmtree(SCRATCH, ignore_errors=True)
print(f"\nrefresh-guard: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
