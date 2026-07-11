#!/usr/bin/env python3
"""SIDECAR SELF-REFRESH E2E — the daemon upgrades itself between requests.

Spawns the REAL sidecar (isolated IPC), bumps agent/sidecar.py's mtime (touch —
content untouched), and proves: the process execs into the new image with the
SAME PID (lockfile stays true), announces the refresh, and still serves a
zero-token verb request correctly afterward.

Usage: python3 tools/sidecar_refresh_e2e.py [runs=3]
"""
import json, os, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SIDE = os.path.join(ROOT, "agent", "sidecar.py")
SONG = "_refresh_e2e"

def events(ipc):
    ep = os.path.join(ipc, "events.jsonl")
    if not os.path.exists(ep):
        return []
    return [json.loads(l) for l in open(ep) if l.strip()]

def run_once(idx):
    checks = []
    def ok(cond, msg):
        checks.append((bool(cond), msg))
    json.dump({"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0.0,
               "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
               "tracks": [{"name": "hats", "source": {"kind": "faust", "id": "hat"},
                           "gainDb": -10,
                           "notes": [{"start": i * 0.25, "len": 0.1, "pitch": 42, "vel": 0.6}
                                     for i in range(16)]}]},
              open(os.path.join(SONGS, f"{SONG}.json"), "w"))
    ipc = tempfile.mkdtemp(prefix="refresh_ipc_")
    env = dict(os.environ, SOTADAW_SANDBOX="1", SOTADAW_IPC=ipc, SOTADAW_RESIDENT="0")
    proc = subprocess.Popen([sys.executable, SIDE], env=env, cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            if any(e.get("kind") == "status" and "online" in e.get("text", "")
                   for e in events(ipc)):
                break
            time.sleep(0.3)
        pid0 = proc.pid
        os.utime(SIDE)                       # the "new code landed" signal
        deadline = time.time() + 15
        refreshed = False
        while time.time() < deadline:
            if any("self-refresh" in e.get("text", "") for e in events(ipc)):
                refreshed = True
                break
            time.sleep(0.3)
        ok(refreshed, "daemon announced the self-refresh")
        ok(proc.poll() is None, "process alive across the exec")
        ok(proc.pid == pid0, f"SAME PID through execv ({pid0} — lockfile stays true)")
        # the reloaded image must come back online AND still do real work
        deadline = time.time() + 30
        online2 = False
        while time.time() < deadline:
            if sum(1 for e in events(ipc)
                   if e.get("kind") == "status" and "online" in e.get("text", "")) >= 2:
                online2 = True
                break
            time.sleep(0.3)
        ok(online2, "reloaded image back online")
        n0 = len(events(ipc))
        json.dump({"id": 9, "type": "verb", "verb": "groove", "song": SONG,
                   "args": {"track": "hats", "groove": "dilla", "amount": 1.0}},
                  open(os.path.join(ipc, "request.json"), "w"))
        deadline = time.time() + 90
        tail = []
        while time.time() < deadline:
            tail = events(ipc)[n0:]
            if any(e.get("kind") == "done" for e in tail):
                break
            time.sleep(0.5)
        ok(any(e.get("kind") == "proposal" for e in tail),
           "the REBORN daemon serves a verb proposal")
        ok(not any(e.get("kind") == "error" for e in tail), "zero errors post-refresh")
        # THE MEMO FAMILY SEAM (2026-07-11, his genre-less accept row): the verb
        # above stamped last_prompts[SONG] in the live image; a SECOND refresh
        # must persist the whole ask-context family through the execv save.
        n_ref = sum(1 for e in events(ipc) if "self-refresh" in e.get("text", ""))
        os.utime(SIDE)
        deadline = time.time() + 15
        while time.time() < deadline:
            if sum(1 for e in events(ipc)
                   if "self-refresh" in e.get("text", "")) > n_ref:
                break
            time.sleep(0.3)
        fs = {}
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                fs = json.load(open(os.path.join(ipc, "feedback_state.json")))
                if (fs.get("last_prompts") or {}).get(SONG):
                    break
            except Exception:
                pass
            time.sleep(0.3)
        ok((fs.get("last_prompts") or {}).get(SONG, "").startswith("[verb]"),
           "memo family (last_prompts) survives the execv save")
        ok("last_meta" in fs and "last_genres" in fs,
           "state file carries the whole ask-context family")
    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        for n in (f"{SONG}.json", f"_prop_{SONG}.json", f"_prop_{SONG}.ghost.json",
                  f"_prop_{SONG}.wav"):
            p = os.path.join(SONGS, n)
            os.path.exists(p) and os.remove(p)
        shutil.rmtree(ipc, ignore_errors=True)
    fails = [m for okk, m in checks if not okk]
    print(f"== run {idx}: {'PASS' if not fails else 'FAIL'} ({len(checks) - len(fails)}/{len(checks)})")
    for okk, m in checks:
        print(f"   {'ok ' if okk else 'FAIL'} {m}")
    return not fails

if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    bad = sum(0 if run_once(i + 1) else 1 for i in range(runs))
    print(f"\nSIDECAR SELF-REFRESH: {'ALL GREEN' if bad == 0 else f'{bad} RUN(S) RED'} over {runs}")
    sys.exit(bad)
