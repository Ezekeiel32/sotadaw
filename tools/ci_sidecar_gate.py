#!/usr/bin/env python3
"""P5 gate (PORT_SPEC.md): the agent sidecar BOOTS on this OS (mock mode,
zero tokens). Portable timeout probe: alive after 6s = green, early exit = red."""
import os, subprocess, sys, tempfile, time

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ipc = tempfile.mkdtemp(prefix="sd_ipc_")
env = dict(os.environ, SOTADAW_IPC=ipc, SOTADAW_NO_UPLINK="1")
p = subprocess.Popen([sys.executable, os.path.join(root, "agent", "sidecar.py"), "--mock"],
                     env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
time.sleep(6)
alive = p.poll() is None
out = b""
if not alive:
    out = p.stdout.read()
else:
    p.terminate()
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill()
print("SIDECAR GATE:", "BOOTS (alive at 6s)" if alive else "DIED")
if not alive:
    sys.stdout.write(out.decode(errors="replace")[-2000:])
    sys.exit(1)
