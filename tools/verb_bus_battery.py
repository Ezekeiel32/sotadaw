#!/usr/bin/env python3
"""VERB BUS battery — the zero-token direct lane keeps every discipline of the
LLM lane while being ~instant.

Proves (against a REAL isolated sidecar, --mock, SOTADAW_IPC scratch dir):
  B1 instant diff: verb request -> proposal event in < 3s wall (kernel ms in event)
  B2 diff truth: only the named section changes; locked track byte-identical
  B3 scope law: the verb's receipt covers the diff (surgical.clean == True)
  B4 read-only verbs report without creating a proposal
  B5 unknown verb -> ERROR event (never silent)
  B6 unknown request TYPE -> ERROR event (the documented silent-consume trap, closed)
  B7 the prompt lane still works (mock regression)
  B8 a pending proposal blocks a second mutating verb (one-take law)

Exit 1 on any failure. Cleans up scratch song + IPC dir + exact-pid kill."""
import json, os, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_vbus"

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""))


def scratch_song():
    hats = [{"start": b * 0.5, "len": 0.1, "pitch": 42, "vel": 0.5} for b in range(64)]
    lead = [{"start": float(b), "len": 0.8, "pitch": 60 + (b % 5), "vel": 0.7} for b in range(32)]
    bass = [{"start": float(b), "len": 0.9, "pitch": 40, "vel": 0.6} for b in range(16, 32)]
    return {"version": 2, "bpm": 124, "lengthBars": 8, "masterGainDb": 0, "key": "C minor",
            "sections": [{"name": "intro", "startBar": 0}, {"name": "drop", "startBar": 4}],
            "tracks": [
                {"name": "hats", "source": {"kind": "faust", "id": "hat_metal"}, "gainDb": -8, "notes": hats},
                {"name": "lead", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -6, "notes": lead},
                {"name": "bass", "source": {"kind": "faust", "id": "bass_warm"}, "gainDb": -5,
                 "locked": True, "notes": bass}]}


class Bus:
    def __init__(self, ipc):
        self.ipc = ipc
        self.rid = 100
        self.offset = 0

    def events(self):
        p = os.path.join(self.ipc, "events.jsonl")
        if not os.path.exists(p):
            return []
        out = []
        for line in open(p):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return out

    def send(self, req):
        self.rid += 1
        req = dict(req, id=self.rid)
        with open(os.path.join(self.ipc, "request.json"), "w") as f:
            f.write(json.dumps(req))
        return self.rid, time.time()

    def wait(self, rid, kind, timeout=30):
        t0 = time.time()
        while time.time() - t0 < timeout:
            for e in self.events():
                if e.get("id") == rid and e.get("kind") == kind:
                    return e, time.time() - t0
            time.sleep(0.1)
        return None, time.time() - t0


def main():
    ipc = tempfile.mkdtemp(prefix="vbus_ipc_")
    base_path = os.path.join(SONGS, f"{SONG}.json")
    json.dump(scratch_song(), open(base_path, "w"), indent=1)
    env = dict(os.environ, SOTADAW_IPC=ipc, SOTADAW_NO_UPLINK="1")
    side = subprocess.Popen([sys.executable, os.path.join(ROOT, "agent", "sidecar.py"), "--mock"],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bus = Bus(ipc)
    try:
        # wait for readiness
        t0 = time.time()
        while time.time() - t0 < 15:
            if any(e.get("kind") == "status" and "online" in str(e.get("text", ""))
                   for e in bus.events()):
                break
            time.sleep(0.1)
        else:
            check("sidecar came up", False, "no 'agent online' status in 15s")
            return finish(side, ipc)

        # B6 unknown TYPE -> error (the trap, closed)
        rid, _ = bus.send({"type": "teleport", "song": SONG})
        e, _ = bus.wait(rid, "error", timeout=10)
        check("B6 unknown request TYPE errors (silent-consume trap closed)",
              e is not None and "unknown request type" in e.get("text", ""), str(e and e.get("text"))[:80])

        # B5 unknown verb -> error naming the registry
        rid, _ = bus.send({"type": "verb", "verb": "sparkle", "song": SONG})
        e, _ = bus.wait(rid, "error", timeout=10)
        check("B5 unknown verb errors with the registry list",
              e is not None and "unknown verb" in e.get("text", "") and "intensify" in e.get("text", ""))

        # B4 read-only verb: doctor -> verb_report, NO proposal file
        rid, _ = bus.send({"type": "verb", "verb": "doctor", "song": SONG})
        e, _ = bus.wait(rid, "verb_report", timeout=20)
        rt = (e or {}).get("text", "")
        check("B4 read-only doctor returns a HUMAN verb_report (machine tail stripped)",
              e is not None and ("issue" in rt or "CLEAN" in rt) and "DOCTOR_JSON" not in rt,
              f"ms={e and e.get('ms')}")
        check("B4b read-only verb creates NO proposal",
              not os.path.exists(os.path.join(SONGS, f"_prop_{SONG}.json")))

        # B1/B2/B3 the instant mutating verb
        base = json.load(open(base_path))
        rid, t_send = bus.send({"type": "verb", "verb": "intensify", "song": SONG,
                                "args": {"section": "drop", "amount": 0.7}})
        e, dt = bus.wait(rid, "proposal", timeout=15)
        check("B1 verb -> proposal event (instant diff, pre-render)",
              e is not None and e.get("verb") == "intensify", f"wall {dt:.2f}s")
        check("B1b proposal arrived in < 3s wall (vs prompt lane median 595s)",
              e is not None and dt < 3.0, f"{dt:.2f}s, kernel ms={e and e.get('ms')}")
        check("B1c kernel time in the event < 2500ms", e is not None and e.get("ms", 9e9) < 2500)

        prop = json.load(open(os.path.join(SONGS, f"_prop_{SONG}.json")))
        pb = {t["name"]: t for t in prop["tracks"]}
        bb = {t["name"]: t for t in base["tracks"]}
        in_drop = lambda n: 16.0 <= n["start"] < 32.0
        # ORIGINAL window notes must get louder (added 16ths carry vel*0.6 by design)
        hat_starts = {n["start"] for n in bb["hats"]["notes"] if in_drop(n)}
        vel_up = all(n["vel"] > 0.5 for n in pb["hats"]["notes"]
                     if in_drop(n) and n["start"] in hat_starts) \
             and all(n["vel"] > 0.7 for n in pb["lead"]["notes"] if in_drop(n))
        outside_same = ([n for n in pb["hats"]["notes"] if not in_drop(n)]
                        == [n for n in bb["hats"]["notes"] if not in_drop(n)]) \
                   and ([n for n in pb["lead"]["notes"] if not in_drop(n)]
                        == [n for n in bb["lead"]["notes"] if not in_drop(n)])
        check("B2 diff truth: drop harder, outside the section byte-identical",
              vel_up and outside_same)
        check("B2b LOCKED track untouched by the verb lane",
              json.dumps(pb["bass"], sort_keys=True) == json.dumps(bb["bass"], sort_keys=True))
        srep = e.get("surgical") or {}
        check("B3 scope law: the verb's receipt covers the whole diff (clean)",
              srep.get("clean") is True, json.dumps(srep)[:100])

        # B8 one-take law: a second mutating verb while pending -> error
        rid, _ = bus.send({"type": "verb", "verb": "humanize", "song": SONG,
                           "args": {"amount": 0.5}})
        e, _ = bus.wait(rid, "error", timeout=10)
        check("B8 pending proposal blocks a second mutating verb",
              e is not None and "pending" in e.get("text", ""))
        bus.wait(rid, "done", timeout=10)

        # clean the pending proposal directly (no accept/reject — keeps git clean)
        for f in (f"_prop_{SONG}.json", f"_prop_{SONG}.wav", f"_prop_{SONG}.ghost.json"):
            p = os.path.join(SONGS, f)
            os.path.exists(p) and os.remove(p)

        # B7 prompt-lane regression (mock, zero tokens)
        rid, _ = bus.send({"type": "prompt", "text": "make it quieter", "song": SONG})
        e, dt = bus.wait(rid, "proposal", timeout=120)
        check("B7 the prompt lane still proposes (mock regression)", e is not None, f"{dt:.1f}s")
        bus.wait(rid, "done", timeout=120)
    finally:
        return finish(side, ipc)


def finish(side, ipc):
    # exact-pid kill + scrub (isolation recipe)
    try:
        side.send_signal(signal.SIGTERM)
        side.wait(timeout=5)
    except Exception:
        side.kill()
    shutil.rmtree(ipc, ignore_errors=True)
    for f in os.listdir(SONGS):
        if f.startswith(SONG) or f.startswith(f"_prop_{SONG}"):
            os.remove(os.path.join(SONGS, f))
    print(f"\n== VERB BUS: {len(PASS)} pass / {len(FAIL)} fail ==")
    if FAIL:
        print("FAILURES:", ", ".join(FAIL))
        sys.exit(1)
    print("THE ZERO-TOKEN LANE IS LIVE (instant diffs, every discipline kept)")
    return 0


if __name__ == "__main__":
    main()
