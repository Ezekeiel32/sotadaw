#!/usr/bin/env python3
"""PARSE WIRE E2E — T1-R3 proof: the parse lane INSIDE the real sidecar.

Real sidecar process, isolated SOTADAW_IPC, SOTADAW_MOCK=1 (misses hit the mock
composer — zero tokens end to end), scratch song `_parsew`. Five checks:

  1. HIT surgical: "mute the hats" -> proposal event carries parsed:true, the
     [parse] activity line shipped, _prop_ has hats muted, scope CLEAN, and the
     proposal event beat the render (instant-diff law).
  2. HIT verb: "make the pad warmer" -> [parse] activity + proposal via the verb
     bus (event carries verb:"color").
  3. PENDING GUARD: with a _prop_ on disk, "mute the bass" must NOT parse
     (revise conversation stays on the LLM rail) -> mock proposal, no parsed flag.
  4. HONEST MISS: "make it groove more" -> no [parse] compile, mock proposal.
  5. KILL SWITCH: sidecar restarted with SOTADAW_PARSE=0 -> "mute the hats"
     goes to the mock rail, no parsed flag.

Also asserts telemetry/asks.jsonl logged the routes (parse/mock), then scrubs
the _parsew rows + scratch songs (isolation law).
"""
import json, os, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_parsew"
sys.path.insert(0, os.path.join(ROOT, "tools"))
from scalpel_suite import base_song, T  # noqa: E402

ASKS = os.path.join(ROOT, "telemetry", "asks.jsonl")


class Bus:
    def __init__(self, ipc):
        self.ipc, self.rid = ipc, 900

    def events(self):
        try:
            return [json.loads(l) for l in open(os.path.join(self.ipc, "events.jsonl"))
                    if l.strip()]
        except FileNotFoundError:
            return []

    def send(self, text):
        self.rid += 1
        tmp = os.path.join(self.ipc, "request.json.tmp")
        with open(tmp, "w") as f:
            f.write(json.dumps({"type": "prompt", "text": text, "song": SONG,
                                "id": self.rid}))
        os.replace(tmp, os.path.join(self.ipc, "request.json"))
        return self.rid

    def wait_done(self, rid, timeout=180):
        t0 = time.time()
        while time.time() - t0 < timeout:
            evs = [e for e in self.events() if e.get("id") == rid]
            if any(e.get("kind") == "done" for e in evs):
                return evs
            time.sleep(0.25)
        return [e for e in self.events() if e.get("id") == rid]


def start_sidecar(ipc, extra_env=None):
    env = dict(os.environ, SOTADAW_IPC=ipc, SOTADAW_NO_UPLINK="1")
    env.update(extra_env or {})
    py = os.path.join(ROOT, ".venv", "bin", "python")
    if not os.path.exists(py):
        py = sys.executable
    p = subprocess.Popen([py, os.path.join(ROOT, "agent", "sidecar.py"), "--mock"],
                         env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    return p


def fresh_song():
    for f in os.listdir(SONGS):
        if f.startswith(SONG) or f.startswith(f"_prop_{SONG}"):
            os.remove(os.path.join(SONGS, f))
    json.dump(base_song(), open(os.path.join(SONGS, f"{SONG}.json"), "w"), indent=1)


def main():
    fails = []
    asks_before = 0
    if os.path.exists(ASKS):
        asks_before = sum(1 for _ in open(ASKS))
    ipc = tempfile.mkdtemp(prefix="parsew_ipc_")
    side = start_sidecar(ipc)
    bus = Bus(ipc)

    def check(cond, label):
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        if not cond:
            fails.append(label)

    try:
        # 1 — surgical hit
        fresh_song()
        rid = bus.send("mute the hats")
        evs = bus.wait_done(rid)
        prop_ev = next((e for e in evs if e.get("kind") == "proposal"), None)
        acts = " | ".join(str(e.get("text")) for e in evs if e.get("kind") == "activity")
        pp = os.path.join(SONGS, f"_prop_{SONG}.json")
        check(prop_ev is not None and prop_ev.get("parsed") is True,
              "1a proposal event carries parsed:true")
        check("[parse]" in acts, "1b [parse] activity line shipped")
        check(prop_ev is not None and int(prop_ev.get("ms", 9999)) < 3000,
              f"1c proposal event ms is instant-class ({prop_ev.get('ms') if prop_ev else '?'}ms)")
        check(os.path.exists(pp) and T(json.load(open(pp)), "hats").get("muted") is True,
              "1d _prop_ has hats muted")
        check(prop_ev is not None and (prop_ev.get("surgical") or {}).get("clean") is True,
              "1e scope verdict CLEAN")
        order_ok = False
        if prop_ev is not None:
            ana = next((e for e in evs if e.get("kind") == "analysis"), None)
            done = next(e for e in evs if e.get("kind") == "done")
            idx = [e.get("kind") for e in evs]
            order_ok = idx.index("proposal") < idx.index("done") and \
                (ana is None or idx.index("proposal") < idx.index("analysis"))
        check(order_ok, "1f instant diff: proposal event precedes render results")

        # 2 — verb hit
        fresh_song()
        rid = bus.send("make the pad warmer")
        evs = bus.wait_done(rid)
        prop_ev = next((e for e in evs if e.get("kind") == "proposal"), None)
        acts = " | ".join(str(e.get("text")) for e in evs if e.get("kind") == "activity")
        check("[parse]" in acts and "verb bus" in acts, "2a [parse] -> verb bus activity")
        check(prop_ev is not None and prop_ev.get("verb") == "color",
              "2b proposal shipped by the verb bus (verb=color)")

        # 3 — pending guard: a _prop_ on disk means the LLM rail owns the turn
        fresh_song()
        shutil.copy(os.path.join(SONGS, f"{SONG}.json"),
                    os.path.join(SONGS, f"_prop_{SONG}.json"))
        rid = bus.send("mute the bass")
        evs = bus.wait_done(rid)
        prop_ev = next((e for e in evs if e.get("kind") == "proposal"), None)
        acts = " | ".join(str(e.get("text")) for e in evs if e.get("kind") == "activity")
        check(prop_ev is not None and not prop_ev.get("parsed")
              and "compile" not in acts,
              "3  pending _prop_ defers to the (mock) cloud rail")

        # 4 — honest miss
        fresh_song()
        rid = bus.send("make it groove more")
        evs = bus.wait_done(rid)
        prop_ev = next((e for e in evs if e.get("kind") == "proposal"), None)
        acts = " | ".join(str(e.get("text")) for e in evs if e.get("kind") == "activity")
        check(prop_ev is not None and not prop_ev.get("parsed")
              and "[parse]" not in acts,
              "4  unparseable ask falls through byte-identically (mock rail)")

        # 5 — kill switch
        side.send_signal(signal.SIGTERM)
        side.wait(timeout=5)
        side = start_sidecar(ipc, {"SOTADAW_PARSE": "0"})
        fresh_song()
        rid = bus.send("mute the hats")
        evs = bus.wait_done(rid)
        prop_ev = next((e for e in evs if e.get("kind") == "proposal"), None)
        check(prop_ev is not None and not prop_ev.get("parsed"),
              "5  SOTADAW_PARSE=0 kills the lane (mock rail takes the same ask)")

        # asks.jsonl coverage log (T1-R1)
        routes = []
        if os.path.exists(ASKS):
            for line in list(open(ASKS))[asks_before:]:
                try:
                    r = json.loads(line)
                    if r.get("song") == SONG:
                        routes.append(r.get("route"))
                except json.JSONDecodeError:
                    pass
        check(routes[:2] == ["parse", "parse"] and "mock" in routes,
              f"6  asks.jsonl logged routes {routes}")
    finally:
        try:
            side.send_signal(signal.SIGTERM)
            side.wait(timeout=5)
        except Exception:
            side.kill()
        shutil.rmtree(ipc, ignore_errors=True)
        for f in os.listdir(SONGS):
            if f.startswith(SONG) or f.startswith(f"_prop_{SONG}"):
                os.remove(os.path.join(SONGS, f))
        if os.path.exists(ASKS):     # scrub the rig's telemetry rows (isolation law)
            keep = []
            for l in open(ASKS):
                try:
                    if json.loads(l).get("song") != SONG:
                        keep.append(l)
                except json.JSONDecodeError:
                    keep.append(l)
            if keep:
                with open(ASKS, "w") as f:
                    f.writelines(keep)
            else:
                os.remove(ASKS)
    n = len(fails)
    print(f"\n== PARSE WIRE E2E: {'ALL GREEN' if n == 0 else f'{n} FAILURE(S)'} ==")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
