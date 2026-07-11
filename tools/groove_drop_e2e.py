#!/usr/bin/env python3
"""GROOVE DROP E2E — drag a FEEL onto a lane, the take rides the proposal rails.

Drives the REAL sidecar with a {"type":"verb","verb":"groove"} request (exactly
what the lane drop writes): on-grid hats + the dilla profile -> a PROPOSAL whose
hats moved off-grid with shaped velocities, scope-law CLEAN (the one-line verb
registry receipt covers the notes), base untouched until accept.

Usage: python3 tools/groove_drop_e2e.py [runs=3]
"""
import json, os, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_groove_e2e"

def scrub():
    for n in (f"{SONG}.json", f"_prop_{SONG}.json", f"_prop_{SONG}.ghost.json",
              f"_prop_{SONG}.wav", f"{SONG}.wav"):
        p = os.path.join(SONGS, n)
        os.path.exists(p) and os.remove(p)

def run_once(idx):
    checks = []
    def ok(cond, msg):
        checks.append((bool(cond), msg))
    scrub()
    base = {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0.0,
            "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": [
                {"name": "kick", "source": {"kind": "faust", "id": "hardkick"}, "gainDb": -3,
                 "notes": [{"start": float(i), "len": 0.2, "pitch": 36, "vel": 0.95}
                           for i in range(8)]},
                {"name": "hats", "source": {"kind": "faust", "id": "hat"}, "gainDb": -12,
                 "notes": [{"start": i * 0.25, "len": 0.1, "pitch": 42, "vel": 0.6}
                           for i in range(32)]}]}
    json.dump(base, open(os.path.join(SONGS, f"{SONG}.json"), "w"), indent=1)
    ipc = tempfile.mkdtemp(prefix="groove_ipc_")
    env = dict(os.environ, SOTADAW_SANDBOX="1", SOTADAW_IPC=ipc)
    proc = subprocess.Popen([sys.executable, os.path.join(ROOT, "agent", "sidecar.py")],
                            env=env, cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.5)
        json.dump({"id": 1, "type": "verb", "verb": "groove", "song": SONG,
                   "args": {"track": "hats", "groove": "dilla", "amount": 1.0}},
                  open(os.path.join(ipc, "request.json"), "w"))
        deadline = time.time() + 120
        events = []
        while time.time() < deadline:
            time.sleep(0.5)
            ep = os.path.join(ipc, "events.jsonl")
            if os.path.exists(ep):
                events = [json.loads(l) for l in open(ep) if l.strip()]
                if any(e.get("kind") == "done" for e in events):
                    break
        errs = [e for e in events if e.get("kind") == "error"]
        prop_ev = next((e for e in events if e.get("kind") == "proposal"), None)
        ok(not errs, f"zero errors ({[e.get('text', '')[:50] for e in errs]})")
        ok(prop_ev is not None, "proposal event landed (verb rides the rails)")
        sur = (prop_ev or {}).get("surgical") or {}
        ok(sur.get("clean") is True, f"scope law CLEAN (registry receipt held: {sur.get('out_of_scope', '?')})")
        pj = os.path.join(SONGS, f"_prop_{SONG}.json")
        ok(os.path.exists(pj), "prop exists; base untouched until accept")
        if os.path.exists(pj):
            prop = json.load(open(pj))
            ph = next(t for t in prop["tracks"] if t["name"] == "hats")
            bh = base["tracks"][1]["notes"]
            moved = sum(1 for a, b in zip(sorted(n["start"] for n in ph["notes"]),
                                          sorted(n["start"] for n in bh))
                        if abs(a - b) > 1e-6)
            ok(moved >= 8, f"the FEEL landed: {moved} hat starts moved off-grid")
            ok(ph.get("groove", {}).get("name") == "dilla", "groove provenance stamped on the track")
            pk = next(t for t in prop["tracks"] if t["name"] == "kick")
            ok(all(abs(n["start"] - round(n["start"])) < 1e-6 for n in pk["notes"]),
               "kick untouched (only the dropped lane changed)")
        bj = json.load(open(os.path.join(SONGS, f"{SONG}.json")))
        ok(bj == base, "BASE byte-untouched (proposal discipline)")

        # ---- run B on the SAME sidecar: a HOT base (no wall, +12 gains) must get
        # the CLIP WALL on the verb lane too, and the lanes must hear about it ----
        scrub()
        hot = json.loads(json.dumps(base))
        hot["master"] = []
        for t in hot["tracks"]:
            t["gainDb"] = 12.0
        json.dump(hot, open(os.path.join(SONGS, f"{SONG}.json"), "w"), indent=1)
        ep = os.path.join(ipc, "events.jsonl")
        offset = os.path.getsize(ep) if os.path.exists(ep) else 0
        json.dump({"id": 2, "type": "verb", "verb": "groove", "song": SONG,
                   "args": {"track": "hats", "groove": "dilla", "amount": 1.0}},
                  open(os.path.join(ipc, "request.json"), "w"))
        deadline = time.time() + 120
        ev2 = []
        while time.time() < deadline:
            time.sleep(0.5)
            if os.path.exists(ep):
                with open(ep) as fh:
                    fh.seek(offset)
                    ev2 = [json.loads(l) for l in fh if l.strip()]
                if any(e.get("kind") == "done" for e in ev2):
                    break
        ok(any("CLIP WALL" in str(e.get("text", "")) for e in ev2),
           "hot base: the CLIP WALL fired on the VERB lane")
        anal = [e for e in ev2 if e.get("kind") == "analysis"]
        ok(anal and int(anal[-1].get("clipped", 1)) == 0,
           f"hot base: final render CLEAN (clipped {anal[-1].get('clipped') if anal else '?'})")
        kinds = [e.get("kind") for e in ev2]
        ok("proposal" in kinds and "proposal_progress" in kinds
           and kinds.index("proposal_progress") > kinds.index("proposal"),
           "post-wall progress refresh follows the instant proposal")
        pj2 = json.load(open(os.path.join(SONGS, f"_prop_{SONG}.json")))
        ok(pj2.get("master") and pj2["master"][-1].get("id") == "fx_truepeak",
           "the walled prop carries fx_truepeak LAST")
    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        scrub()
        shutil.rmtree(ipc, ignore_errors=True)
    fails = [m for okk, m in checks if not okk]
    print(f"== run {idx}: {'PASS' if not fails else 'FAIL'} ({len(checks) - len(fails)}/{len(checks)})")
    for okk, m in checks:
        print(f"   {'ok ' if okk else 'FAIL'} {m}")
    return not fails

if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    bad = sum(0 if run_once(i + 1) else 1 for i in range(runs))
    print(f"\nGROOVE DROP: {'ALL GREEN' if bad == 0 else f'{bad} RUN(S) RED'} over {runs}")
    sys.exit(bad)
