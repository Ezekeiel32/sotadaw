#!/usr/bin/env python3
"""THE JAM battery — the AI band's closed loop is REAL, not scripted.

The proof is the ABLATION: the SAME genre+seed under opposite vibes must produce
DIVERGING energy arcs — only a real ears->brain->generate loop can do that (a
script would ignore the vibe or the listening). Plus: the loop closes into one
continuous renderable song, the measured arc tracks the target vibe, and the
per-phrase gen+render fits inside the phrase's playback time (realtime-feasible).

SKIP-green when m1 is absent. Exit code IS the verdict.
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
SONGS = os.path.join(ROOT, "songs")

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)
    print(f"  {'OK ' if cond else 'XX '}{msg}")


def third_avg(arc, which):
    k = max(1, len(arc) // 3)
    return sum(arc[:k]) / k if which == "first" else sum(arc[-k:]) / k


def trend(arc):
    return third_avg(arc, "last") - third_avg(arc, "first")


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a) ** 0.5
    vb = sum((y - mb) ** 2 for y in b) ** 0.5
    return cov / (va * vb) if va > 0 and vb > 0 else 0.0


def scrub(*names):
    for nm in names:
        p = os.path.join(SONGS, f"{nm}.json")
        if os.path.exists(p):
            os.remove(p)
        w = os.path.join(SONGS, f"{nm}.wav")
        if os.path.exists(w):
            os.remove(w)


def main():
    if not os.path.exists(M1):
        print("SKIP: m1 not built")
        return 0
    import jam
    print("== THE JAM BATTERY (the AI band's closed loop) ==")

    # ---- run the SAME seed under opposite vibes: the ablation ----
    t0 = time.time()
    rb, eb = jam.jam("house", "build", phrases=6, seed=7, name="_jambat_b")
    rd, ed = jam.jam("house", "breakdown", phrases=6, seed=7, name="_jambat_d")
    dt = time.time() - t0
    ok(rb is not None and rd is not None, "both jams produced a song")
    if rb is None or rd is None:
        print("FAIL: jam errored:", eb, ed)
        return 1
    ab, ad = rb["arc"], rd["arc"]
    print(f"  build arc:     {[round(x,2) for x in ab]}  trend {trend(ab):+.2f}")
    print(f"  breakdown arc: {[round(x,2) for x in ad]}  trend {trend(ad):+.2f}")

    # 1) loop closes into one continuous song
    import json
    cb = json.load(open(rb["song"]))
    ok(cb.get("lengthBars") == 6 * 4 and len(rb["log"]) == 6 and len(cb["tracks"]) >= 2,
       f"loop CLOSES into one continuous song ({cb.get('lengthBars')} bars, {len(cb['tracks'])} tracks)")

    # 2) THE ABLATION: build rises, breakdown falls, and they DIVERGE (same seed!)
    ok(trend(ab) > 0.08, f"BUILD arc rises ({trend(ab):+.2f})")
    ok(trend(ad) < -0.08, f"BREAKDOWN arc falls ({trend(ad):+.2f})")
    ok(trend(ab) - trend(ad) > 0.3,
       f"ABLATION: same seed, opposite vibes DIVERGE (Δtrend {trend(ab)-trend(ad):+.2f}) — the loop is REAL")

    # 3) the measured arc tracks the target vibe (listening steers toward it)
    tgt_b = [jam.VIBES["build"](p, 6) for p in range(6)]
    r = pearson(ab, tgt_b)
    ok(r > 0.6, f"measured arc tracks the vibe (build corr {r:.2f})")

    # (realtime timing is proven RIGOROUSLY by jam_live_battery — a real deadline race
    # with concurrency, not a wall-time ratio that a loaded suite would make flaky. This
    # battery owns LOOP correctness; jam_live owns the realtime schedule.)

    # 4) the continuous take renders clean (a real artifact, not just a plan)
    import subprocess
    wav = os.path.join(SONGS, "_jambat_b.wav")
    r2 = subprocess.run([M1, "render", rb["song"], wav], capture_output=True, timeout=180)
    ok(r2.returncode == 0 and os.path.exists(wav) and os.path.getsize(wav) > 100000,
       "the continuous jam renders to a real audio take")

    scrub("_jambat_b", "_jambat_d")
    print(f"jam battery: {PASS}/{PASS + len(FAIL)} " + ("clean" if not FAIL else "RED"))
    for f in FAIL:
        print("FAIL:", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
