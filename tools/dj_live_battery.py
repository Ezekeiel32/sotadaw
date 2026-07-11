#!/usr/bin/env python3
"""DJ-LIVE R4 battery — the deck-swap advisor over live ears frames.

Kernel (pure): APPROACH fires inside the 20s pre-boundary window naming the
incoming record; RIDE replaces it when energy climbs into the handover;
listener verdicts (PLATEAU) pass through deck-tagged; dedupe holds; silence
says nothing. CLI replays a recorded ears.jsonl. Sidecar tick: a staged rig
(fresh frames + a setplan song) makes the coach SPEAK once, then hold its
tongue on the repeat (dedupe), and SOTADAW_DJ_LIVE=0 gags it.

Exit code IS the verdict.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)
    print(f"  {'OK ' if cond else 'XX '}{msg}")


def frames(rms_by_sec, t0=None):
    t0 = t0 if t0 is not None else time.time()
    return [{"t": t0 + s, "beat": s * 2.0, "sec": float(s), "playing": True,
             "rms_db": [r, r], "peak_db": [r + 8, r + 8], "dbtp_q": r + 8,
             "bands_db": [-12.0, -20.0, -28.0, -40.0], "crest_db": 8.0}
            for s, r in rms_by_sec]


PLAN = [{"artist": "", "song": "opener", "start": 0.0},
        {"artist": "", "song": "peak tune", "start": 40.0}]


def main():
    import dj_live
    print("== DJ-LIVE R4 BATTERY ==")

    # APPROACH: steady energy, frames reach 25s -> the 40s boundary is 15s out
    adv = dj_live.advise(frames([(s, -12.0) for s in range(0, 26)]), PLAN)
    app = [a for a in adv if a["kind"] == "APPROACH"]
    ok(bool(app) and "peak tune" in app[0]["text"] and "filter" in app[0]["text"],
       f"APPROACH names the incoming record + the bass-swap move ({len(adv)} advice)")

    # RIDE: energy climbs into the boundary -> ride, not approach
    climb = [(s, -18.0 + (0.5 * max(0, s - 13))) for s in range(0, 26)]
    adv = dj_live.advise(frames(climb), PLAN)
    ok(any(a["kind"] == "RIDE" for a in adv) and not any(a["kind"] == "APPROACH" for a in adv),
       "RIDE replaces APPROACH when energy climbs into the handover")

    # dedupe: 30 frames inside the window -> ONE approach line
    adv = dj_live.advise(frames([(20 + s * 0.2, -12.0) for s in range(30)]), PLAN)
    ok(len([a for a in adv if a["kind"] == "APPROACH"]) <= 1, "dedupe: one line per (kind, deck)")

    # PLATEAU passthrough, deck-tagged — pinned MID-set (the kernel rightly
    # ignores a run that touches intro/outro, so give it edges)
    long_plan = [{"song": "opener", "start": 0.0}, {"song": "closer", "start": 500.0}]
    shape = [(s, -30.0 + 2.0 * s) for s in range(0, 10)] \
        + [(s, -10.0) for s in range(10, 115)] \
        + [(s, -10.0 - 1.5 * (s - 115)) for s in range(115, 130)]
    adv = dj_live.advise(frames(shape), long_plan)
    pl = [a for a in adv if a["kind"] == "PLATEAU"]
    ok(bool(pl) and "deck A" in pl[0]["text"], "live PLATEAU verdict passes through deck-tagged")

    # silence: nothing plays -> nothing said
    silent = [dict(f, playing=False) for f in frames([(s, -12.0) for s in range(10)])]
    ok(dj_live.advise(silent, PLAN) == [], "silence -> no advice")

    # CLI replay
    work = tempfile.mkdtemp(prefix="djlive_")
    fp, sp = os.path.join(work, "ears.jsonl"), os.path.join(work, "plan.json")
    with open(fp, "w") as f:
        for fr in frames([(s, -12.0) for s in range(0, 26)]):
            f.write(json.dumps(fr) + "\n")
    json.dump(PLAN, open(sp, "w"))
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "dj_live.py"),
                        sp, "--frames", fp], capture_output=True, text=True, timeout=60)
    ok(r.returncode == 0 and "DJLIVE_JSON" in r.stdout and "APPROACH" in r.stdout,
       "CLI replays a recorded ears.jsonl")

    # ---- the sidecar tick: staged rig -> the coach speaks once ----
    ipc = tempfile.mkdtemp(prefix="djlive_ipc_")
    os.environ["SOTADAW_IPC"] = ipc
    os.environ.pop("SOTADAW_SANDBOX", None)
    os.environ.pop("SOTADAW_DJ_LIVE", None)
    sys.path.insert(0, os.path.join(ROOT, "agent"))
    import sidecar as sc
    sc.IPC = ipc
    said = []
    sc.emit = lambda rid, kind, **kw: said.append((kind, kw.get("text", "")))
    setp = os.path.join(sc.SONGS, "_djlive_bat.setplan.json")
    json.dump(PLAN, open(setp, "w"))
    try:
        sc.last_prompts["_djlive_bat"] = "play my set"
        with open(os.path.join(ipc, "ears.jsonl"), "w") as f:
            for fr in frames([(s, -12.0) for s in range(0, 26)]):
                f.write(json.dumps(fr) + "\n")
        sc._djlive["next"] = 0.0
        sc.dj_live_tick()
        ok(len(said) == 1 and "[dj-live]" in said[0][1] and "peak tune" in said[0][1],
           f"sidecar tick: the coach speaks ONE line ({said[:1]})")
        sc._djlive["next"] = 0.0
        sc.dj_live_tick()
        ok(len(said) == 1, "sidecar tick: dedupe holds on the repeat")
        os.environ["SOTADAW_DJ_LIVE"] = "0"
        sc._djlive["next"] = 0.0
        sc._djlive["said"] = set()
        sc.dj_live_tick()
        ok(len(said) == 1, "SOTADAW_DJ_LIVE=0 gags the coach")
    finally:
        os.environ.pop("SOTADAW_DJ_LIVE", None)
        os.path.exists(setp) and os.remove(setp)
        sc.last_prompts.pop("_djlive_bat", None)

    print(f"dj-live battery: {PASS}/{PASS + len(FAIL)} " + ("clean" if not FAIL else "RED"))
    for f in FAIL:
        print("FAIL:", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
