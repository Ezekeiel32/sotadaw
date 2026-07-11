#!/usr/bin/env python3
"""CLIP WALL battery — a clipping proposal never ships untreated.

Pure cases (render mocked): wall-present (ceiling forced <= -1.2, moved LAST),
legacy brickwall/limiter upgraded in place, missing wall appended, masterGainDb
zeroed, clean/unreadable passthrough. Then the REAL-AUDIO proof: a deliberately
clipping 2-bar song through the REAL m1 render + analyze2 -> clipped N -> 0.

Usage: python3 tools/clip_wall_battery.py            (pure only)
       .venv/bin/python tools/clip_wall_battery.py --real   (+ real render)
"""
import json, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["SOTADAW_IPC"] = tempfile.mkdtemp(prefix="clipwall_ipc_")
sys.path.insert(0, os.path.join(ROOT, "agent"))
import sidecar as sc

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

SONG = "_clipwall_e2e"
PJ = os.path.join(sc.SONGS, f"{SONG}.json")

def doc_with(master, gain=0.0):
    return {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": gain,
            "master": master,
            "tracks": [{"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
                        "gainDb": 12.0,
                        "notes": [{"start": i * 0.5, "len": 0.3, "pitch": 36, "vel": 1.0}
                                  for i in range(16)]}]}

def run_case(master, gain=0.0, clipped=999):
    json.dump(doc_with(master, gain), open(PJ, "w"), indent=1)
    rendered = []
    real = sc.render_and_analyze
    sc.render_and_analyze = lambda rid, s, l: (rendered.append(s), {"clipped_samples": 0})[1]
    try:
        out = sc.clip_wall(0, SONG, {"clipped_samples": clipped, "peak_dbfs": 0.4})
    finally:
        sc.render_and_analyze = real
    return json.load(open(PJ)), rendered, out

def main():
    # 1) wall present but mid-chain with a soft ceiling: forced <= -1.2, moved LAST
    d, rend, out = run_case([{"id": "fx_truepeak", "params": {"ceiling": -0.3}},
                             {"id": "fx_trim", "params": {"level": 2.0}}])
    ok(d["master"][-1]["id"] == "fx_truepeak", "wall moved LAST")
    ok(d["master"][-1]["params"]["ceiling"] <= -1.2, "ceiling forced <= -1.2")
    ok(rendered_once(rend), "exactly ONE re-render")
    # 2) legacy brickwall upgraded in place
    d, _, _ = run_case([{"id": "fx_brickwall", "params": {"ceiling": -1.0}}])
    ok(d["master"][-1] == {"id": "fx_truepeak", "params": {"ceiling": -1.2}},
       "legacy brickwall upgraded to fx_truepeak -1.2")
    # 3) deprecated type:limiter upgraded
    d, _, _ = run_case([{"type": "limiter", "params": {"ceiling": -1.0, "drive": 0}}])
    ok(d["master"][-1].get("id") == "fx_truepeak", "type:limiter upgraded")
    # 4) NO wall at all: appended
    d, _, _ = run_case([{"id": "fx_trim", "params": {"level": 3.0}}])
    ok(d["master"][-1]["id"] == "fx_truepeak", "missing wall appended last")
    # 5) masterGainDb re-opens headroom: forced 0
    d, _, _ = run_case([{"id": "fx_truepeak", "params": {"ceiling": -1.2}}], gain=4.0)
    ok(d.get("masterGainDb") == 0.0, "masterGainDb forced to 0")
    # 6) clean take: untouched passthrough (no render, no rewrite)
    json.dump(doc_with([{"id": "fx_trim", "params": {"level": 9.9}}]), open(PJ, "w"))
    before = open(PJ).read()
    out = sc.clip_wall(0, SONG, {"clipped_samples": 0, "peak_dbfs": -1.4})
    ok(out == {"clipped_samples": 0, "peak_dbfs": -1.4} and open(PJ).read() == before,
       "clean take passes through untouched")
    # 7) unreadable analysis: passthrough
    ok(sc.clip_wall(0, SONG, True) is True, "non-dict analysis passes through")
    os.remove(PJ)

    if "--real" in sys.argv:
        # REAL AUDIO: hot gains, no wall -> render clips -> clip_wall -> clean
        json.dump(doc_with([{"id": "fx_trim", "params": {"level": 6.0}}]), open(PJ, "w"), indent=1)
        a0 = sc.render_and_analyze(0, SONG, "proposal")
        ok(isinstance(a0, dict) and int(a0.get("clipped_samples", 0)) > 0,
           f"fixture really CLIPS pre-wall (clipped {a0 if not isinstance(a0, dict) else a0.get('clipped_samples')})")
        a1 = sc.clip_wall(0, SONG, a0)
        ok(isinstance(a1, dict) and int(a1.get("clipped_samples", 1)) == 0,
           f"REAL render after the wall: clipped -> 0 (got {a1 if not isinstance(a1, dict) else a1.get('clipped_samples')})")
        d = json.load(open(PJ))
        ok(d["master"][-1]["id"] == "fx_truepeak", "real prop carries the wall LAST")
        for p in (PJ, PJ.replace(".json", ".wav")):
            os.path.exists(p) and os.remove(p)

def rendered_once(r):
    return len(r) == 1

if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"clip-wall battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
