#!/usr/bin/env python3
"""ABLETON LINK E2E — two REAL app instances share one session clock.

Boots TWO SOTA DAW instances (isolated IPC, distinct scratch songs) with Link
enabled: they must DISCOVER each other on localhost (peers >= 1 both sides),
and when the driver instance requests 97 bpm through Link, the listener's song
BPM must follow — the W14 room, proven on one box.

Usage: python3 tools/link_e2e.py [runs=3]
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
BIN = os.path.join(ROOT, "app", "build", "sotadaw_artefacts", "Release", "SOTA DAW")

def spawn(tag, mode, song):
    json.dump({"version": 2, "bpm": 120, "lengthBars": 4, "masterGainDb": 0.0,
               "master": [], "tracks": [
                   {"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
                    "gainDb": -6, "notes": [{"start": float(i), "len": 0.2,
                                             "pitch": 36, "vel": 0.8} for i in range(8)]}]},
              open(os.path.join(SONGS, f"{song}.json"), "w"))
    env = dict(os.environ, SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1", SOTADAW_SNAP_LINK=mode,
               SOTADAW_SONG=song, SOTADAW_IPC=tempfile.mkdtemp(prefix=f"link_{tag}_"))
    out = tempfile.mkdtemp(prefix=f"linkpng_{tag}_")
    return subprocess.Popen([BIN, "--snapshot", out], env=env, cwd=ROOT,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True), song

def parse(stdout):
    ticks = []
    for m in re.finditer(r"\[link\] t(\d+) peers=(\d+) bpm=([\d.]+) playing=(\d)", stdout):
        ticks.append((int(m.group(1)), int(m.group(2)), float(m.group(3)), int(m.group(4))))
    return ticks

def run_once(idx):
    checks = []
    def ok(cond, msg):
        checks.append((bool(cond), msg))
    a, sa = spawn("listen", "listen", "_link_a")
    time.sleep(1.0)
    b, sb = spawn("drive", "drive:97", "_link_b")
    try:
        oa = a.communicate(timeout=60)[0]
        ob = b.communicate(timeout=60)[0]
    except subprocess.TimeoutExpired:
        a.kill(); b.kill()
        oa = a.communicate()[0]; ob = b.communicate()[0]
    finally:
        for s in (sa, sb):
            p = os.path.join(SONGS, f"{s}.json")
            os.path.exists(p) and os.remove(p)
    ta, tb = parse(oa), parse(ob)
    ok(len(ta) >= 10 and len(tb) >= 10, f"both instances ticked ({len(ta)}/{len(tb)})")
    ok(any(p >= 1 for _, p, _, _ in ta) and any(p >= 1 for _, p, _, _ in tb),
       f"DISCOVERY: peers>=1 both sides (max a={max((p for _, p, _, _ in ta), default=0)}, "
       f"b={max((p for _, p, _, _ in tb), default=0)})")
    ok(any(abs(bpm - 97.0) < 0.5 for _, _, bpm, _ in ta[6:]),
       f"TEMPO FOLLOWS: listener reached 97 (tail bpms {[x[2] for x in ta[-4:]]})")
    ok(all(abs(bpm - 120.0) < 0.5 for _, _, bpm, _ in ta[:2]),
       "listener started at its own 120 (the change came over the wire)")
    la = {t: pl for t, _, _, pl in ta}
    ok(all(la.get(t, 0) == 0 for t in (0, 1, 2) if t in la),
       "listener idle before the driver plays")
    ok(any(la.get(t, 0) == 1 for t in (7, 8, 9)),
       f"START FOLLOWS: listener transport ROLLS after the driver's play ({[la.get(t) for t in range(6, 12)]})")
    ok(any(la.get(t, 1) == 0 for t in (10, 11)),
       f"STOP FOLLOWS: listener stops after the driver's stop ({[la.get(t) for t in (10, 11)]})")
    fails = [m for okk, m in checks if not okk]
    print(f"== run {idx}: {'PASS' if not fails else 'FAIL'} ({len(checks) - len(fails)}/{len(checks)})")
    for okk, m in checks:
        print(f"   {'ok ' if okk else 'FAIL'} {m}")
    return not fails

if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    bad = sum(0 if run_once(i + 1) else 1 for i in range(runs))
    print(f"\nABLETON LINK: {'ALL GREEN' if bad == 0 else f'{bad} RUN(S) RED'} over {runs}")
    sys.exit(bad)
