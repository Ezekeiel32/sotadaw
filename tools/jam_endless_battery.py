#!/usr/bin/env python3
"""B6 THE BANDSTAND battery — the ENDLESS jam as machinery, headless.

What it proves (the pieces Chezy called "complete shit", now laws):
  - phrases=0 = ENDLESS: the set outlives any fixed count and ends ONLY on the
    stop file (the JAM button's graceful STOP seam)
  - the SESSION event fires BEFORE the sound-check (the UI shows a live warming
    pane, never dead air)
  - LIVE VIBE: vibe.txt mid-set switches the arc — decides carry the old vibe
    before the flip and the new one after; a vibe_change event announces it
  - STOP -> done lands fast (<6s: no window sleep-out) and the take is REAL
    (lengthBars = the bars actually played, buses ride, tracks non-empty)
  - AUTOSAVE: the take json exists on disk MID-SET (a crash/hard-kill still
    leaves the tape on the desk)
  - phrase_ready carries dur_s (musical) + tail_s (the ring the player
    overlap-adds) — the speakers-wire contract for seamless sends

Usage: .venv/bin/python tools/jam_endless_battery.py
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
SONGS = os.path.join(ROOT, "songs")

PASS = 0
FAIL = []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)
    print(f"  {'OK ' if cond else 'XX '}{msg}")


def main():
    if not os.path.exists(M1):
        print("SKIP: m1 not built")
        return 0
    import jam_live
    print("== B6 THE BANDSTAND BATTERY (endless + live controls) ==")
    ipc = tempfile.mkdtemp(prefix="jamendless_ipc_")
    feed = os.path.join(ipc, "live.jsonl")
    take = os.path.join(SONGS, "_jamendbat.json")
    box = {}

    def run():
        box["res"], box["err"] = jam_live.jam_live(
            "house", "build", phrases=0, seed=5, name="_jamendbat", ipc=ipc)

    def events():
        try:
            return [json.loads(l) for l in open(feed)]
        except OSError:
            return []

    t = threading.Thread(target=run)
    t.start()
    t0 = time.time()
    while not any(e["ev"] == "session" for e in events()) and time.time() - t0 < 40:
        time.sleep(0.1)
    evs = events()
    ok(any(e["ev"] == "session" for e in evs), "session event fired")
    ok(next((e.get("endless") for e in evs if e["ev"] == "session"), False) is True,
       "session declares ENDLESS")
    ok(not any(e["ev"] == "phrase_ready" for e in evs),
       "session lands BEFORE the sound-check (warming pane has its cue)")

    while sum(1 for e in events() if e["ev"] == "decide") < 3 and time.time() - t0 < 90:
        time.sleep(0.2)
    autosaved_mid = os.path.exists(take)
    open(os.path.join(ipc, "vibe.txt"), "w").write("breakdown")
    while sum(1 for e in events() if e["ev"] == "decide") < 5 and time.time() - t0 < 140:
        time.sleep(0.2)
    open(os.path.join(ipc, "stop"), "w").write("1")
    stop_t = time.time()
    t.join(timeout=40)
    done_t = time.time()

    res = box.get("res")
    evs = events()
    dec = [(e["phrase"], e.get("vibe")) for e in evs if e["ev"] == "decide"]
    flips = [e["phrase"] for e in evs if e["ev"] == "vibe_change"]
    ok(not t.is_alive() and res is not None, "the endless set ENDED on the stop file")
    ok(len(dec) >= 5, f"the set outlived a fixed count ({len(dec)} decides)")
    ok(autosaved_mid, "AUTOSAVE: the take existed on disk MID-SET")
    ok(len(flips) == 1, f"vibe_change announced exactly once (at {flips})")
    if flips:
        ok(all(v == "build" for ph, v in dec if ph < flips[0]),
           "decides BEFORE the flip ride 'build'")
        ok(all(v == "breakdown" for ph, v in dec if ph >= flips[0]),
           "decides AFTER the flip ride 'breakdown'")
    ok(any(e["ev"] == "done" for e in evs), "done event fed (the take is announced)")
    ok(done_t - stop_t < 6.0, f"STOP -> done is FAST ({done_t - stop_t:.1f}s < 6s)")

    ph = [e for e in evs if e["ev"] == "phrase_ready"]
    ok(all(e.get("tail_s", 0) > 0 for e in ph),
       "every phrase_ready carries tail_s (the overlap-add ring)")
    ok(all(abs(e["dur_s"] - e["bars"] * ph[0]["dur_s"] / ph[0]["bars"]) < 0.01 for e in ph),
       "dur_s stays MUSICAL (bars * bar seconds, tail excluded)")

    d = json.load(open(take))
    played = sum(lg["bars"] for lg in res["log"]) if res else -1
    ok(d.get("lengthBars") == played and played > 0,
       f"take lengthBars == bars actually played ({d.get('lengthBars')} == {played})")
    ok(bool(d.get("buses")), "buses ride the take (sends are not dropped)")
    ok(bool(d.get("tracks")), "the take has real material")
    sec_names = [s["name"] for s in d.get("sections", [])]
    ok(any(n.startswith("build") for n in sec_names)
       and any(n.startswith("breakdown") for n in sec_names),
       f"sections remember BOTH vibes ({sec_names})")

    for p in (take, take.replace(".json", ".wav")):
        if os.path.exists(p):
            os.remove(p)
    shutil.rmtree(ipc, ignore_errors=True)
    print(f"bandstand battery: {PASS}/{PASS + len(FAIL)} " + ("clean" if not FAIL else "RED"))
    for f in FAIL:
        print("FAIL:", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
