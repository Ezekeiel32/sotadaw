#!/usr/bin/env python3
"""MANY-TRACKS E2E — THE FOLD + density, headless, through the REAL app.

Boots the actual SOTA DAW binary in --snapshot mode (peerless) on a 21-track
fixture shaped like a real imported session (stems + sketches + kit pieces +
spectral capture + sung/true vocals). SOTADAW_SNAP_MANY=1 drives the camera
inside MainComponent: open -> fold-all -> density 1.8, printing one
machine-checkable [many] census line per state. This script owns fixtures,
assertions, cleanup.

What it proves (the "21 tracks = unreadable soup" indictment, dead):
  open    3 family GROUP BARS derive (sketches:3 kit:5 spectral:7), all 21
          lanes visible (one-line compact headers carry the density)
  folded  the 15 family lanes hide behind their bars; the 6 primary lanes
          keep the screen
  tall    ctrl+wheel density (laneScale 1.8) keeps every lane laid out

Usage: tools/manytracks_e2e.py [runs]      (default 3)
"""
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")
NAME = "_manytracks_e2e"

N = lambda s, l, p, v: {"start": s, "len": l, "pitch": p, "vel": v}

def trk(nm, vid="bass_warm", pitch=48):
    return {"name": nm, "source": {"kind": "faust", "id": vid}, "gainDb": -6,
            "pan": 0, "notes": [N(b, 0.4, pitch, 0.8) for b in range(4)]}

# the imported-session shape: same family layout as a real stems+spectral import
NAMES = ["drums", "bass", "other", "vocals",
         "bass_sketch", "other_sketch", "vocals_sketch",
         "Kick", "Snare", "Hats", "Perc", "Cymbals",
         "vocals_sung",
         "spectral_low", "spectral_mid", "spectral_high", "spectral_clicks",
         "spectral_noise", "spectral_mix", "spectral_residual",
         "vocals_true"]

def write_fixture():
    doc = {"version": 1, "bpm": 120, "lengthBars": 4, "masterGainDb": 0.0,
           "master": [], "tracks": [trk(n) for n in NAMES], "buses": []}
    with open(os.path.join(SONGS, NAME + ".json"), "w") as f:
        json.dump(doc, f, indent=1)

def cleanup():
    for f in (NAME + ".json", NAME + ".wav"):
        p = os.path.join(SONGS, f)
        if os.path.exists(p):
            os.remove(p)

def parse(line):  # "[many] open groups=3 sketches:3 kit:5 spectral:7 lanes=21 vis=21 hidden=0"
    m = re.match(r"\[many\] (\w+) (.*)", line)
    return (m.group(1), m.group(2)) if m else (None, None)

def check(states, pngs):
    r = []
    def expect(cond, msg):
        r.append((bool(cond), msg))
    st = dict(states)
    expect(set(st) == {"open", "folded", "tall"}, f"three census states (got {sorted(st)})")
    for tag in ("open", "folded", "tall"):
        if tag not in st:
            continue
        expect(st[tag].startswith("groups=3"), f"{tag}: 3 families derive ({st[tag][:40]!r})")
        for fam in ("sketches:3", "kit:5", "spectral:7"):
            expect(fam in st[tag], f"{tag}: {fam} present ({st[tag][:60]})")
        expect("lanes=21" in st[tag], f"{tag}: all 21 lanes exist ({st[tag]})")
    if "open" in st:
        expect("vis=21 hidden=0" in st["open"], f"open: nothing hidden ({st['open']})")
    if "folded" in st:
        expect("vis=6 hidden=15" in st["folded"],
               f"folded: 15 family lanes behind bars ({st['folded']})")
        expect("sketches:3(folded)" in st["folded"] and "kit:5(folded)" in st["folded"]
               and "spectral:7(folded)" in st["folded"],
               f"folded: every bar folded ({st['folded']})")
    if "tall" in st:
        # THE CLIP LAW (2026-07-11): rows scrolled past the lane area are
        # zero-sized, so at 1.8x density "vis" may drop below the unfolded 6 —
        # the invariant is the FOLD holding (>=15 hidden) with folded markers.
        m_h = re.search(r"hidden=(\d+)", st["tall"])
        expect("(folded)" in st["tall"] and m_h and int(m_h.group(1)) >= 15,
               f"tall: density keeps the fold ({st['tall']})")
    for png in ("many_open.png", "many_folded.png", "many_tall.png"):
        expect(png in pngs, f"{png} rendered")
    return r

def run_once(idx):
    write_fixture()
    ipc = tempfile.mkdtemp(prefix="many_e2e_ipc_")
    out = tempfile.mkdtemp(prefix="many_e2e_png_")
    env = dict(os.environ,
               SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1", SOTADAW_SNAP_MANY="1",
               SOTADAW_SNAP_ONLY="none", SOTADAW_SONG=NAME, SOTADAW_IPC=ipc)
    try:
        p = subprocess.run([BIN, "--snapshot", out], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=180)
        states = [parse(l) for l in p.stdout.splitlines() if l.startswith("[many]")]
        states = [s for s in states if s[0]]
        pngs = os.listdir(out)
        results = check(states, pngs)
        if p.returncode != 0:
            results.append((False, f"app exit {p.returncode}; tail: {p.stdout[-300:]} {p.stderr[-300:]}"))
        return results
    finally:
        cleanup()
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)

def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    total_fail = 0
    for i in range(1, runs + 1):
        results = run_once(i)
        fails = [m for ok, m in results if not ok]
        total_fail += len(fails)
        print(f"[run {i}] {len(results) - len(fails)}/{len(results)} checks"
              + (f"  FAILS: {fails}" if fails else ""))
    print("MANYTRACKS_E2E " + ("GREEN" if total_fail == 0 else f"RED ({total_fail} fails)"))
    return 0 if total_fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
