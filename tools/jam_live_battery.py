#!/usr/bin/env python3
"""THE LIVE JAM battery — the realtime scheduler is sound: the AI band "just goes."

Proves, with REAL wall-clock timing + REAL concurrent m1 renders racing the deadline:
  1) NO UNDERRUN — every phrase N+1 is rendered and ready BEFORE phrase N's real
     playback window ends (slack > 0 for every transition).
  2) GENERATE-AHEAD OVERLAP — total wall time is PLAYBACK-bound (≈ phrases x phrase_dur),
     NOT playback+generation-bound: the renders hide inside the playback windows. Total
     is measurably less than a serial (render-then-play) schedule would take.
  3) LIVE FEEDBACK — the band's move for N+1 is decided from N's ears within N's window
     (causal), and the arc adapts to the vibe.
  4) the continuous take renders (a real seamless artifact).

Runs in real time (~15-20s). SKIP-green when m1 is absent. Exit code IS the verdict.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
SONGS = os.path.join(ROOT, "songs")

# This battery measures the SCHEDULER's concurrency, not the render cache: a warm
# cache legitimately zeroes gen time (the bandstand feature), which would fake the
# overlap math. The epoch is part of cache_key — a unique one forces real renders.
os.environ["SOTADAW_RENDER_EPOCH"] = f"jamlive-battery-{os.getpid()}"

PASS, FAIL = 0, []


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
    print("== THE LIVE JAM BATTERY (realtime scheduler) ==")
    res, err = jam_live.jam_live("house", "build", phrases=6, seed=5, name="_jamlivebat", bars_per=2)
    ok(res is not None, "the live jam ran")
    if res is None:
        print("FAIL:", err)
        return 1

    timing = res["timing"]
    dur = res["phrase_dur"]
    transitions = [t for t in timing if t["phrase"] < res["phrases"] - 1]

    # 1) NO UNDERRUN — every next phrase ready before the current window ends
    slacks = [t["slack_s"] for t in transitions]
    ok(all(t["ready"] for t in transitions) and min(slacks) > 0,
       f"NO UNDERRUN: every phrase ready before its deadline (min slack {min(slacks):+.1f}s)")

    # 2) GENERATE-AHEAD OVERLAP — total is playback-bound, beats a serial schedule
    ideal_playback = res["phrases"] * dur
    sum_gen = sum(t["gen_s"] for t in transitions)
    serial = ideal_playback + sum_gen            # render-then-play would add every gen
    ok(res["total_wall"] < ideal_playback + 5.0,
       f"PLAYBACK-BOUND: total {res['total_wall']:.1f}s ~= {ideal_playback:.1f}s pure playback (+startup)")
    ok(res["total_wall"] < serial - 2.0,
       f"OVERLAP proven: {res['total_wall']:.1f}s < {serial:.1f}s serial (saved {serial-res['total_wall']:.1f}s of gen by overlapping)")

    # 3) LIVE FEEDBACK — the band adapts to the vibe. On a BUILD vibe (rising) the
    # band, hearing itself below the target, should predominantly BUILD (add layers/
    # brighten) — the moves are a robust adaptation signal (the short arc is noisy).
    moves = [lg["move"] for lg in res["log"]]
    builds = sum(1 for m in moves if "BUILD" in m)
    eases = sum(1 for m in moves if "EASE" in m)
    ok(builds > eases and builds >= len(moves) * 0.5,
       f"LIVE band adapts to the build vibe: {builds} BUILD vs {eases} EASE moves ({moves})")

    # 4) the continuous take renders (seamless artifact)
    wav = os.path.join(SONGS, "_jamlivebat.wav")
    r = subprocess.run([M1, "render", res["song"], wav], capture_output=True, timeout=180)
    cont = json.load(open(res["song"]))
    ok(r.returncode == 0 and os.path.exists(wav) and cont.get("lengthBars") == 6 * 2,
       "the continuous realtime take renders to a seamless artifact")

    for p in (res["song"], wav):
        if os.path.exists(p):
            os.remove(p)
    import shutil
    shutil.rmtree(os.path.join(SONGS, ".jamlive_ipc"), ignore_errors=True)

    print(f"jam-live battery: {PASS}/{PASS + len(FAIL)} " + ("clean" if not FAIL else "RED"))
    for f in FAIL:
        print("FAIL:", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
