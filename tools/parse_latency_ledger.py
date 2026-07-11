#!/usr/bin/env python3
"""PARSE LATENCY LEDGER — T1-R4: the lane ON, measured, graded (roadmap §4.4).

All 22 claimed scalpel sentences through the REAL sidecar, graded by the
suite's OWN verifiers (by sentence — the suite is a moving list), with the
numbers the roadmap demands: compile-ms, proposal-event-ms, done-s (render
included). Zero tokens: parse hits never reach any model, and the fallthrough
part runs against the mock rail.

Parts:
  A  HIT LEDGER   — 22/22 must verify + scope-clean; event-ms distribution
                    vs the ~85,000ms cloud baseline (ROADMAP_0.080 firing 107).
  B  FALLTHROUGH  — cloud-class sentences must show ZERO parse activity and
                    reach the (mock) cloud rail untouched.
  C  GATE READOUT — live route census from telemetry/asks.jsonl (the >=20
                    real-hits evidence trail; the lane is already default-on
                    by Chezy's direct order) + RECALL block byte cost on a
                    loaded store (S4's deferred prompt-bytes measurement).

Artifact: eval/parse_ledger.json. Exit 0 = A and B green.
"""
import json, os, re, shutil, signal, statistics, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_ledger"
sys.path.insert(0, os.path.join(ROOT, "agent"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import parse_battery as pb                  # noqa: E402 — for CLAIMED + SUITE (by sentence)
shutil.rmtree(pb.IPC, ignore_errors=True)   # its import-time temp IPC is unused here
import session_memory as sm                 # noqa: E402
from scalpel_suite import base_song, T      # noqa: E402

IPC = tempfile.mkdtemp(prefix="ledger_ipc_")
os.environ["SOTADAW_IPC"] = IPC
ASKS = os.path.join(ROOT, "telemetry", "asks.jsonl")
CLOUD_CLASS = ["open up the filter on the bass",       # state-dependent param math
               "add a shaker playing sixteenths",      # new-track palette choice
               "swap the lead sound for an epiano"]    # palette choice


class Bus:
    def __init__(self, ipc):
        self.ipc, self.rid = ipc, 990

    def events(self):
        try:
            return [json.loads(l) for l in open(os.path.join(self.ipc, "events.jsonl"))
                    if l.strip()]
        except FileNotFoundError:
            return []

    def prompt(self, text, timeout=150):
        self.rid += 1
        tmp = os.path.join(self.ipc, "request.json.tmp")
        with open(tmp, "w") as f:
            f.write(json.dumps({"type": "prompt", "text": text, "song": SONG,
                                "id": self.rid}))
        os.replace(tmp, os.path.join(self.ipc, "request.json"))
        t0 = time.time()
        while time.time() - t0 < timeout:
            evs = [e for e in self.events() if e.get("id") == self.rid]
            if any(e.get("kind") == "done" for e in evs):
                return evs, time.time() - t0
            time.sleep(0.2)
        return [e for e in self.events() if e.get("id") == self.rid], time.time() - t0


def fresh():
    for f in os.listdir(SONGS):
        if f.startswith(SONG) or f.startswith(f"_prop_{SONG}"):
            os.remove(os.path.join(SONGS, f))
    json.dump(base_song(), open(os.path.join(SONGS, f"{SONG}.json"), "w"), indent=1)
    p = os.path.join(sm.memory_dir(), f"{SONG}.jsonl")
    os.path.exists(p) and os.remove(p)


def main():
    fails, rows = [], []
    asks_before = sum(1 for _ in open(ASKS)) if os.path.exists(ASKS) else 0
    py = os.path.join(ROOT, ".venv", "bin", "python")
    if not os.path.exists(py):
        py = sys.executable
    side = subprocess.Popen([py, os.path.join(ROOT, "agent", "sidecar.py"), "--mock"],
                            env=dict(os.environ, SOTADAW_IPC=IPC, SOTADAW_NO_UPLINK="1"),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    bus = Bus(IPC)
    try:
        print(f"== A. hit ledger — {len(pb.CLAIMED)} claimed sentences, lane ON ==")
        for ask in pb.CLAIMED:
            fresh()
            base = base_song()
            evs, dt = bus.prompt(ask)
            ev = next((e for e in evs if e.get("kind") == "proposal"), None)
            acts = " | ".join(str(e.get("text")) for e in evs
                              if e.get("kind") == "activity")
            hit = ev is not None and (ev.get("parsed") or ev.get("verb"))
            ok = clean = False
            if hit:
                try:
                    prop = json.load(open(os.path.join(SONGS, f"_prop_{SONG}.json")))
                    ok = bool(pb.suite_v(ask)(base, prop))
                    clean = bool((ev.get("surgical") or {}).get("clean"))
                except Exception as e:
                    acts += f" | verify crashed: {e}"
            m = re.search(r"\((\d+(?:\.\d+)?)ms(?: compile)?\)", acts)
            row = {"ask": ask, "hit": bool(hit), "ok": ok, "clean": clean,
                   "kind": ("verb" if (ev or {}).get("verb") else "surgical"),
                   "compile_ms": float(m.group(1)) if m else None,
                   "event_ms": (ev or {}).get("ms"), "done_s": round(dt, 1)}
            rows.append(row)
            good = hit and ok and clean
            if not good:
                fails.append(f"A: {ask!r} hit={bool(hit)} ok={ok} clean={clean}")
            print(f"  [{'PASS' if good else 'FAIL'}] {row['kind']:8s} "
                  f"event {str(row['event_ms']):>6s}ms  done {row['done_s']:5.1f}s  {ask!r}")

        ems = [r["event_ms"] for r in rows if isinstance(r["event_ms"], (int, float))]
        med_e, max_e = (statistics.median(ems), max(ems)) if ems else (None, None)
        med_d = statistics.median([r["done_s"] for r in rows])
        print(f"  -> proposal-event ms: median {med_e:g}, max {max_e:g} "
              f"(cloud baseline ~85,000ms) | done median {med_d:.1f}s (render incl.)")
        if med_e is None or med_e >= 1000:
            fails.append(f"A: median event ms {med_e} >= 1000")

        print("\n== B. fallthrough — cloud-class asks must not parse ==")
        for ask in CLOUD_CLASS:
            fresh()
            evs, dt = bus.prompt(ask)
            ev = next((e for e in evs if e.get("kind") == "proposal"), None)
            acts = " | ".join(str(e.get("text")) for e in evs
                              if e.get("kind") == "activity")
            ok = "compile)" not in acts and "verb bus takes it" not in acts \
                and (ev is None or not ev.get("parsed"))
            if not ok:
                fails.append(f"B: {ask!r} leaked into the lane")
            print(f"  [{'PASS' if ok else 'FAIL'}] {ask!r} -> mock rail ({dt:.1f}s)")

        print("\n== C. gate readout (evidence, not a gate to pass) ==")
        for i in range(8):
            sm.write_fact(SONG, f"fact{i}", "sweet_spot", 700 + i, prov="receipt")
        rb = sm.recall_block(SONG)
        print(f"  RECALL block on an 8-fact store: {len(rb)} bytes, "
              f"{len(rb.splitlines())} lines (cap {sm.RECALL_CAP}+header)")
        census = {}
        if os.path.exists(ASKS):
            for l in list(open(ASKS))[:asks_before]:   # pre-run rows = REAL usage
                try:
                    r = json.loads(l)
                    if not str(r.get("song", "")).startswith(("_parsew", "_sessw",
                                                              "_histw", "_ledger")):
                        census[r.get("route")] = census.get(r.get("route"), 0) + 1
                except json.JSONDecodeError:
                    pass
        print(f"  live asks.jsonl route census (rig rows excluded): {census or '(empty yet)'}")
        print("  live gate: lane is DEFAULT-ON by Chezy's order; the >=20-hit/zero-"
              "wrong-report trail accumulates here.")

        os.makedirs(os.path.join(ROOT, "eval"), exist_ok=True)
        json.dump({"t": round(time.time(), 1), "rows": rows,
                   "median_event_ms": med_e, "max_event_ms": max_e,
                   "median_done_s": med_d, "cloud_baseline_ms": 85000,
                   "recall_block_bytes": len(rb), "live_route_census": census,
                   "fails": fails},
                  open(os.path.join(ROOT, "eval", "parse_ledger.json"), "w"), indent=1)
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
    print(f"\n== PARSE LATENCY LEDGER: {'ALL GREEN' if n == 0 else f'{n} FAILURE(S)'} "
          f"-> eval/parse_ledger.json ==")
    for f in fails:
        print("  - " + f)
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
