#!/usr/bin/env python3
"""SESSION WIRE E2E — T2-S2/S3 proof: the fact store INSIDE the real sidecar.

Real sidecar process, isolated SOTADAW_IPC (the store namespaces under it),
SOTADAW_MOCK=1, scratch song `_sessw`, zero tokens, zero git (the accept hook
itself is unit-proven in session_memory_battery; here we prove the READ wires
and the stash across the process boundary):

  1. THE HEALER: a refers_to fact written BEFORE the sidecar starts (simulating
     a prior session's confirmed edit) makes "make the squelchy one 3db louder"
     — unanswerable bare — a parse HIT that lands on the right track. Memory is
     process-independent: finding B's fragmentation is structurally healed for
     the covered class.
  2. RECALL rides the prompt: ipc/context.json's rendered block carries the
     fact (zero-token observable of what real_propose would receive).
  3. The proposal event carries the plan's non-trivial `resolutions` (what an
     accept would confirm into the store).
  4. The `memory` verb answers from the store in a verb_report.
  5. asks.jsonl logged both hits as route=parse (scrubbed after).
"""
import json, os, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_sessw"
IPC = tempfile.mkdtemp(prefix="sessw_ipc_")
os.environ["SOTADAW_IPC"] = IPC            # BEFORE sm use: this process shares the store
sys.path.insert(0, os.path.join(ROOT, "agent"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import session_memory as sm                # noqa: E402
from scalpel_suite import base_song, T     # noqa: E402

ASKS = os.path.join(ROOT, "telemetry", "asks.jsonl")


class Bus:
    def __init__(self, ipc):
        self.ipc, self.rid = ipc, 950

    def events(self):
        try:
            return [json.loads(l) for l in open(os.path.join(self.ipc, "events.jsonl"))
                    if l.strip()]
        except FileNotFoundError:
            return []

    def send(self, req):
        self.rid += 1
        tmp = os.path.join(self.ipc, "request.json.tmp")
        with open(tmp, "w") as f:
            f.write(json.dumps(dict(req, id=self.rid)))
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


def main():
    fails = []

    def check(cond, label):
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        if not cond:
            fails.append(label)

    asks_before = sum(1 for _ in open(ASKS)) if os.path.exists(ASKS) else 0
    json.dump(base_song(), open(os.path.join(SONGS, f"{SONG}.json"), "w"), indent=1)
    # the "prior session": a confirmed refers_to fact already in the store
    sm.write_fact(SONG, "squelchy one", "refers_to", "bass",
                  prov="accepted: earlier session")

    py = os.path.join(ROOT, ".venv", "bin", "python")
    if not os.path.exists(py):
        py = sys.executable
    side = subprocess.Popen([py, os.path.join(ROOT, "agent", "sidecar.py"), "--mock"],
                            env=dict(os.environ, SOTADAW_IPC=IPC, SOTADAW_NO_UPLINK="1"),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    bus = Bus(IPC)
    try:
        # 1 — the healer
        rid = bus.send({"type": "prompt", "text": "make the squelchy one 3db louder",
                        "song": SONG})
        evs = bus.wait_done(rid)
        prop_ev = next((e for e in evs if e.get("kind") == "proposal"), None)
        pp = os.path.join(SONGS, f"_prop_{SONG}.json")
        check(prop_ev is not None and prop_ev.get("parsed") is True,
              "1a fact-only alias ask is a parse HIT across the process boundary")
        check(os.path.exists(pp)
              and abs(T(json.load(open(pp)), "bass")["gainDb"] + 3.0) < 0.01,
              "1b the edit landed on the fact's track (bass -6 -> -3)")
        # 2 — RECALL in the rendered context
        try:
            rendered = json.load(open(os.path.join(IPC, "context.json"))).get("rendered", "")
        except Exception:
            rendered = ""
        check("RECALL" in rendered and "squelchy one" in rendered,
              "2  RECALL block rides the prompt context (context.json rendered)")
        # 3 — resolutions on the proposal event
        for f in (f"_prop_{SONG}.json", f"_prop_{SONG}.wav", f"_prop_{SONG}.ghost.json"):
            p = os.path.join(SONGS, f)
            os.path.exists(p) and os.remove(p)
        rid = bus.send({"type": "prompt", "text": "quantize the pluck", "song": SONG})
        evs = bus.wait_done(rid)
        prop_ev = next((e for e in evs if e.get("kind") == "proposal"), None)
        check(prop_ev is not None and prop_ev.get("parsed") is True
              and prop_ev.get("resolutions") == {"pluck": "lead"},
              "3  proposal event carries the confirmable resolutions")
        # 4 — the memory verb
        rid = bus.send({"type": "verb", "verb": "memory", "song": SONG})
        evs = bus.wait_done(rid, timeout=60)
        rep = next((e for e in evs if e.get("kind") == "verb_report"), None)
        check(rep is not None and "squelchy one" in str(rep.get("text", "")),
              "4  `memory` verb answers from the store (zero tokens)")
        # 5 — route log
        routes = []
        if os.path.exists(ASKS):
            for line in list(open(ASKS))[asks_before:]:
                try:
                    r = json.loads(line)
                    if r.get("song") == SONG:
                        routes.append(r.get("route"))
                except json.JSONDecodeError:
                    pass
        check(routes == ["parse", "parse"], f"5  asks.jsonl routes {routes}")
    finally:
        try:
            side.send_signal(signal.SIGTERM)
            side.wait(timeout=5)
        except Exception:
            side.kill()
        shutil.rmtree(IPC, ignore_errors=True)
        for f in os.listdir(SONGS):
            if f.startswith(SONG) or f.startswith(f"_prop_{SONG}"):
                os.remove(os.path.join(SONGS, f))
        if os.path.exists(ASKS):
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
    print(f"\n== SESSION WIRE E2E: {'ALL GREEN' if n == 0 else f'{n} FAILURE(S)'} ==")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
