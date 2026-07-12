#!/usr/bin/env python3
"""#21c BLIND ROUND E2E — N zero-token takes land as anonymous variants, the
pick crowns THE proposal, losers retire. Real sidecar loop, isolated IPC,
--mock boot (no prewarm; the make/variants lane is zero-token by construction).
Run: python3 tools/blind_round_e2e.py"""
import json, os, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
PY = sys.executable

N = {"pass": 0, "fail": 0}
def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name
          + (f"  [{detail}]" if detail and not cond else ""), flush=True)

def events(path):
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path) if l.strip().startswith("{")]

def wait_done(ev_path, rid, deadline_s):
    t0 = time.time()
    while time.time() - t0 < deadline_s:
        evs = events(ev_path)
        if any(e.get("kind") == "done" and e.get("id") == rid for e in evs):
            return evs
        time.sleep(2.0)
    return events(ev_path)

def main():
    name = f"_blindround{os.getpid()}"
    ipc = tempfile.mkdtemp(prefix="blindround_ipc_")
    base_json = os.path.join(SONGS, f"{name}.json")
    pid = None
    try:
        json.dump({"version": 2, "bpm": 122, "lengthBars": 2, "key": "Am",
                   "masterGainDb": 0, "master": [],
                   "tracks": [{"name": "kick",
                               "source": {"kind": "faust", "id": "kick_808"},
                               "gainDb": -6, "pan": 0,
                               "notes": [{"start": float(b), "len": 0.2,
                                          "pitch": 36, "vel": 0.9}
                                         for b in range(8)]}]},
                  open(base_json, "w"), indent=1)
        env = dict(os.environ, SOTADAW_IPC=ipc, SOTADAW_CHRONICLE="0")
        sc = subprocess.Popen([PY, os.path.join(ROOT, "agent", "sidecar.py"),
                               "--mock"], env=env,
                              stdout=open(os.path.join(ipc, "out.log"), "w"),
                              stderr=subprocess.STDOUT, start_new_session=True)
        pid = sc.pid
        mock_up, t0 = False, time.time()
        while time.time() - t0 < 20:
            ol = os.path.join(ipc, "out.log")
            if os.path.exists(ol) and "up (mock=True)" in open(ol, errors="replace").read():
                mock_up = True
                break
            time.sleep(0.5)
        check("mock boot (no prewarm burn)", mock_up)
        if not mock_up:
            raise SystemExit("refusing: daemon not in mock boot")
        ev_path = os.path.join(ipc, "events.jsonl")

        json.dump({"id": 11, "type": "make_track", "song": name,
                   "genre": "house", "seed": 5, "variants": 2},
                  open(os.path.join(ipc, "request.json"), "w"))
        evs = wait_done(ev_path, 11, 600)
        var_ev = next((e for e in evs if e.get("kind") == "variants"), None)
        check("variants event landed", var_ev is not None)
        takes = (var_ev or {}).get("takes") or []
        check("2 blind takes offered", len(takes) == 2, str(len(takes)))
        check("labels are anonymous A/B",
              sorted(t["label"] for t in takes) == ["A", "B"],
              str([t.get("label") for t in takes]))
        check("blind flag set", bool((var_ev or {}).get("blind")))
        check("wav paths are label-named (no seed-order digit leaks the blind)",
              all(t["wav"].rsplit("_", 1)[-1].split(".")[0] in ("a", "b", "c", "d")
                  for t in takes), str([t.get("wav") for t in takes]))
        wavs_ok = all(os.path.exists(os.path.join(ROOT, t["wav"])) for t in takes)
        check("every offered wav exists (no card references audio it cannot play)",
              wavs_ok)
        check("no proposal minted by the round itself",
              not os.path.exists(os.path.join(SONGS, f"_prop_{name}.json")))

        json.dump({"id": 12, "type": "pick_variant", "song": name, "label": "A"},
                  open(os.path.join(ipc, "request.json"), "w"))
        evs = wait_done(ev_path, 12, 240)
        prop_ev = any(e.get("kind") == "proposal" and e.get("id") == 12 for e in evs)
        check("pick crowned a proposal event", prop_ev)
        check("winner json IS the proposal",
              os.path.exists(os.path.join(SONGS, f"_prop_{name}.json")))
        check("winner wav rides the proposal name",
              os.path.exists(os.path.join(SONGS, f"_prop_{name}.wav")))
        leftovers = [f for f in os.listdir(SONGS) if f.startswith(f"_var_{name}_")]
        check("losers retired (no _var_ leftovers)", not leftovers, str(leftovers))
        check("round map retired",
              not os.path.exists(os.path.join(ipc, f"variants_{name}.json")))

        # THE PROMPT DOOR: 'make 2 takes of house' routes to the round with
        # ZERO tokens (mock daemon would answer canned prose on the LLM rail —
        # a variants event proves the router fired, not the model)
        os.remove(os.path.join(SONGS, f"_prop_{name}.json"))
        os.remove(os.path.join(SONGS, f"_prop_{name}.wav"))
        json.dump({"id": 13, "type": "prompt", "song": name,
                   "text": "make 2 takes of house"},
                  open(os.path.join(ipc, "request.json"), "w"))
        evs = wait_done(ev_path, 13, 600)
        var2 = next((e for e in evs if e.get("kind") == "variants"
                     and e.get("id") == 13), None)
        check("prompt 'make 2 takes of house' routed to the blind round", var2 is not None)
        check("prompt round offered 2 takes",
              len((var2 or {}).get("takes") or []) == 2)
    finally:
        if N["fail"]:
            for f in ("events.jsonl", "out.log"):
                p = os.path.join(ipc, f)
                if os.path.exists(p):
                    print(f"--- {f} tail ---")
                    print("\n".join(open(p, errors="replace").read()
                                    .splitlines()[-14:]))
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1.0)
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        for f in os.listdir(SONGS):
            if name in f:
                p = os.path.join(SONGS, f)
                os.remove(p) if os.path.isfile(p) else shutil.rmtree(p, ignore_errors=True)
        tele = os.path.join(ROOT, "telemetry", "proposals.jsonl")
        try:
            if os.path.exists(tele):
                keep = [l for l in open(tele) if name not in l]
                open(tele, "w").writelines(keep)
        except Exception:
            pass
        shutil.rmtree(ipc, ignore_errors=True)
    print(f"\n{N['pass']} passed, {N['fail']} failed")
    sys.exit(1 if N["fail"] else 0)

if __name__ == "__main__":
    main()
