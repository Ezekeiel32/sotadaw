#!/usr/bin/env python3
"""THE STRANGER'S FIRST LOOP — W17's acceptance bar, machine-proven.

A fresh box has NO ANTHROPIC_API_KEY and NO claude on PATH. The promise: the
MAKE button still lands a full, rendered, clean, acceptable take (zero tokens:
make_track -> loop_gen DNA -> arrange -> m1 render -> clip wall -> proposal).

This drives the REAL sidecar process (isolated SOTADAW_IPC, minimal PATH,
key stripped) with a real request.json, waits on real events.jsonl, and
asserts the whole journey. Cleans every artifact.

Usage: python3 tools/stranger_e2e.py [runs=3]
"""
import json, os, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_stranger_e2e"

def scrub():
    for n in (f"{SONG}.json", f"{SONG}.wav", f"_prop_{SONG}.json",
              f"_prop_{SONG}.ghost.json", f"_prop_{SONG}.wav", f"_mt_{SONG}.json"):
        p = os.path.join(SONGS, n)
        if os.path.exists(p):
            os.remove(p)

def run_once(idx):
    checks = []
    def ok(cond, msg):
        checks.append((bool(cond), msg))
    scrub()
    json.dump({"version": 2, "bpm": 124, "lengthBars": 4, "masterGainDb": 0.0,
               "master": [], "tracks": []},
              open(os.path.join(SONGS, f"{SONG}.json"), "w"))
    ipc = tempfile.mkdtemp(prefix="stranger_ipc_")
    env = {k: v for k, v in os.environ.items()
           if k not in ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY")}
    env["SOTADAW_IPC"] = ipc
    env["SOTADAW_SANDBOX"] = "1"   # verdict side effects stay out of the real repo
    # the stranger's PATH: an EMPTY dir — nothing resolvable at all (the whole
    # zero-token chain runs on absolute paths: venv python, m1, tool scripts)
    emptybin = tempfile.mkdtemp(prefix="stranger_bin_")
    env["PATH"] = emptybin
    ok(shutil.which("claude", path=env["PATH"]) is None, "no claude resolvable on the stranger's PATH")
    proc = subprocess.Popen([sys.executable, os.path.join(ROOT, "agent", "sidecar.py")],
                            env=env, cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    events_path = os.path.join(ipc, "events.jsonl")
    try:
        time.sleep(1.5)                        # boot + lockfile
        ok(proc.poll() is None, "sidecar boots WITHOUT credentials")
        json.dump({"id": 1, "type": "make_track", "song": SONG,
                   "genre": "house", "seed": 7},
                  open(os.path.join(ipc, "request.json"), "w"))
        deadline = time.time() + 300
        events = []
        got_proposal = got_done = False
        while time.time() < deadline and not got_done:
            time.sleep(1.0)
            if not os.path.exists(events_path):
                continue
            events = [json.loads(l) for l in open(events_path) if l.strip()]
            got_proposal = any(e.get("kind") == "proposal" for e in events)
            got_done = any(e.get("kind") == "done" for e in events)
        kinds = [e.get("kind") for e in events]
        errs = [e for e in events if e.get("kind") == "error"]
        ok(not errs, f"zero error events ({[e.get('text', '')[:60] for e in errs]})")
        ok(got_proposal, f"a PROPOSAL landed (kinds: {kinds[-6:]})")
        ok(got_done and any(e.get("kind") == "done" and e.get("ok") for e in events),
           "done ok=true")
        pj = os.path.join(SONGS, f"_prop_{SONG}.json")
        pw = os.path.join(SONGS, f"_prop_{SONG}.wav")
        ok(os.path.exists(pj), "proposal json exists (acceptable take)")
        ok(os.path.exists(pw) and os.path.getsize(pw) > 400000,
           f"proposal WAV rendered ({os.path.getsize(pw) if os.path.exists(pw) else 0} bytes)")
        anal = [e for e in events if e.get("kind") == "analysis"]
        ok(anal and int(anal[-1].get("clipped", 1)) == 0,
           f"final render CLEAN (clipped {anal[-1].get('clipped') if anal else '?'})")
        doc = json.load(open(pj)) if os.path.exists(pj) else {}
        ok(len(doc.get("tracks", [])) >= 4 and len(doc.get("sections", []) or []) >= 3,
           f"a real ARRANGED song ({len(doc.get('tracks', []))} tracks, "
           f"{len(doc.get('sections', []) or [])} sections)")
        elapsed = 300 - max(0, deadline - time.time())
        ok(elapsed < 300, f"first loop in {elapsed:.0f}s (the 5-minute bar)")
    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        scrub()
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(emptybin, ignore_errors=True)
    fails = [m for okk, m in checks if not okk]
    print(f"== run {idx}: {'PASS' if not fails else 'FAIL'} "
          f"({len(checks) - len(fails)}/{len(checks)})")
    for okk, m in checks:
        print(f"   {'ok ' if okk else 'FAIL'} {m}")
    return not fails

if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    bad = sum(0 if run_once(i + 1) else 1 for i in range(runs))
    print(f"\nSTRANGER'S FIRST LOOP: {'ALL GREEN' if bad == 0 else f'{bad} RUN(S) RED'} over {runs}")
    sys.exit(bad)
