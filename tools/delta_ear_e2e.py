#!/usr/bin/env python3
"""#22 THE Δ EAR E2E — a revise take auto-attaches ONE measured sentence vs the
take it replaced ("[Δ ear] vs the previous take: …" activity + swept .prev.wav).

Protocol-seam proof through the REAL sidecar loop, zero tokens (mock lane),
fully isolated: SOTADAW_IPC scratch dir (own lockfile/request/events), scratch
song name, exact-pid kill, scrub after. Run: python3 tools/delta_ear_e2e.py
"""
import json, os, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
PY = sys.executable

N = {"pass": 0, "fail": 0}
def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name
          + (f"  [{detail}]" if detail and not cond else ""), flush=True)

def main():
    name = f"_deltaear{os.getpid()}"
    ipc = tempfile.mkdtemp(prefix="deltaear_ipc_")
    base_json = os.path.join(SONGS, f"{name}.json")
    prop_json = os.path.join(SONGS, f"_prop_{name}.json")
    prop_wav = os.path.join(SONGS, f"_prop_{name}.wav")
    prev_wav = os.path.join(SONGS, f"_prop_{name}.prev.wav")
    pid = None
    try:
        song = {"version": 2, "bpm": 120, "lengthBars": 2, "key": "Am",
                "masterGainDb": 0, "master": [],
                "tracks": [{"name": "kick",
                            "source": {"kind": "faust", "id": "kick_808"},
                            "gainDb": -6, "pan": 0,
                            "notes": [{"start": float(b), "len": 0.2,
                                       "pitch": 36, "vel": 0.9}
                                      for b in range(8)]}]}
        json.dump(song, open(base_json, "w"), indent=1)
        # the PENDING take: a valid prop json + its render (the wav the revise
        # must be judged against)
        pend = json.loads(json.dumps(song))
        pend["tracks"][0]["gainDb"] = -5.0
        json.dump(pend, open(prop_json, "w"), indent=1)
        r = subprocess.run([M1, "render", base_json, prop_wav],
                           capture_output=True, text=True, timeout=180)
        check("seed render (the previous take's wav)",
              r.returncode == 0 and os.path.exists(prop_wav),
              (r.stdout + r.stderr)[-160:])
        env = dict(os.environ, SOTADAW_IPC=ipc, SOTADAW_MOCK="1",
                   SOTADAW_CHRONICLE="0")
        sc = subprocess.Popen([PY, os.path.join(ROOT, "agent", "sidecar.py")],
                              env=env, stdout=open(os.path.join(ipc, "out.log"), "w"),
                              stderr=subprocess.STDOUT, start_new_session=True)
        pid = sc.pid
        time.sleep(2.0)
        json.dump({"id": 7, "type": "prompt", "text": "make it quieter",
                   "song": name, "revise": True},
                  open(os.path.join(ipc, "request.json"), "w"))
        ev_path = os.path.join(ipc, "events.jsonl")
        delta_line, done_ok, deadline = "", False, time.time() + 300
        while time.time() < deadline:
            if os.path.exists(ev_path):
                evs = [json.loads(l) for l in open(ev_path)
                       if l.strip().startswith("{")]
                for e in evs:
                    t = str(e.get("text", ""))
                    if "[Δ ear]" in t or "[Δ ear]" in t:
                        delta_line = t
                    if e.get("kind") == "done" or e.get("type") == "done":
                        done_ok = bool(e.get("ok"))
                if delta_line and done_ok:
                    break
                if any((e.get("kind") == "done" or e.get("type") == "done")
                       for e in evs):
                    break
            time.sleep(2.0)
        check("Δ ear line attached to the revise take", bool(delta_line),
              "no [Δ ear] activity in events (see %s)" % ev_path)
        sent = delta_line.split(":", 1)[-1].strip() if delta_line else ""
        check("the sentence is measured, non-empty", len(sent) > 3, delta_line[:120])
        check("run finished ok", done_ok)
        check("prev wav swept after the diff", not os.path.exists(prev_wav))
        if delta_line:
            print("   sentence:", sent[:140])
    finally:
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1.0)
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        for p in (base_json, prop_json, prop_wav, prev_wav,
                  os.path.join(SONGS, f"_prop_{name}.ghost.json"),
                  os.path.join(SONGS, f"{name}.wav")):
            if os.path.exists(p):
                os.remove(p)
        tele = os.path.join(ROOT, "telemetry", "proposals.jsonl")
        try:   # scrub any telemetry the scratch run filed
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
