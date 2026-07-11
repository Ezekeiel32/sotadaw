#!/usr/bin/env python3
"""B4 ENGINE CAPTURE E2E — audio records onto an armed lane, through the REAL app.

Boots the actual SOTA DAW binary in --snapshot mode with SOTADAW_SNAP_RECAUDIO=1.
The in-app rig selects/creates an audio lane ("mic"), arms the REAL Rec flow
(THE LANE'S KIND DECIDES), records ~1.4s from the box's wave input, stops, and
the harvest lands the take: a file in songs/takes/ + an audioClips entry in
song.json. This driver owns fixtures, assertions, cleanup.

HONESTY LAW: content energy is NOT asserted — a silent room is a legal take.
The MACHINERY is: wave-ins present, instances armed, a clip harvested, the file
real (> a header), the json mirroring it. Boxes with zero capture devices skip.

Usage: tools/audio_rec_e2e.py [runs]
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
BIN = os.path.join(ROOT, "app/build/sotadaw_artefacts/Release/SOTA DAW")
NAME = "_recaudio_e2e"


def write_fixture():
    doc = {"version": 2, "bpm": 120, "lengthBars": 4, "masterGainDb": 0.0, "master": [],
           "tracks": [{"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
                       "gainDb": -4, "pan": 0,
                       "notes": [{"start": b, "len": 0.2, "pitch": 36, "vel": 1}
                                 for b in range(4)]},
                      {"name": "mic", "source": {"kind": "audio"}, "gainDb": 0, "pan": 0,
                       "notes": [], "audioClips": []}]}
    with open(os.path.join(SONGS, f"{NAME}.json"), "w") as f:
        json.dump(doc, f, indent=1)


def cleanup(keep_takes=False):
    p = os.path.join(SONGS, f"{NAME}.json")
    if os.path.exists(p):
        os.remove(p)
    if not keep_takes:
        for fn in os.listdir(os.path.join(SONGS, "takes")) if os.path.isdir(
                os.path.join(SONGS, "takes")) else []:
            if fn.startswith(NAME):
                os.remove(os.path.join(SONGS, "takes", fn))


def run_once(idx):
    write_fixture()
    ipc = tempfile.mkdtemp(prefix="recaudio_ipc_")
    out = tempfile.mkdtemp(prefix="recaudio_png_")
    env = dict(os.environ, SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1",
               SOTADAW_SNAP_RECAUDIO="1", SOTADAW_SONG=NAME, SOTADAW_IPC=ipc)
    A = []

    def ok(cond, msg):
        A.append((bool(cond), msg))

    try:
        p = subprocess.run([BIN, "--snapshot", out], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        lines = [l for l in p.stdout.splitlines() if l.startswith("[recaudio]")]
        d = {}
        for l in lines:
            d.update(dict(re.findall(r"(\w+)=(\S+)", l)))
        if int(d.get("waveIns", "0")) == 0:
            print(f"== run {idx}: SKIP (no wave input devices on this box)")
            return None
        ok(p.returncode == 0, f"app exited clean (rc {p.returncode}; {p.stdout[-300:]})")
        ok(int(d.get("armed", "0")) >= 1, f"wave input ARMED onto the lane ({d.get('armed')})")
        ok(int(d.get("added", "0")) >= 1, f"take harvested ({d.get('added')})")
        f = d.get("file", "-")
        fp = os.path.join(ROOT, f)
        ok(f.startswith("songs/takes/") and os.path.exists(fp),
           f"take file real ({f})")
        ok(os.path.getsize(fp) > 1024 if os.path.exists(fp) else False,
           f"take bigger than a header ({os.path.getsize(fp) if os.path.exists(fp) else 0}b)")
        ok(float(d.get("lenBeats", "0")) >= 1.0,
           f"clip length sane ({d.get('lenBeats')} beats for ~1.4s @120)")
        doc = json.load(open(os.path.join(SONGS, f"{NAME}.json")))
        mic = next((t for t in doc["tracks"] if t["name"] == "mic"), {})
        ok(len(mic.get("audioClips", [])) == int(d.get("added", "0")),
           f"song.json mirrors the harvest ({len(mic.get('audioClips', []))})")
        ok(all(c["file"].startswith("songs/takes/") for c in mic.get("audioClips", [])),
           "clips point into songs/takes/")
        return A
    finally:
        cleanup()
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    total_fail = 0
    for i in range(1, runs + 1):
        results = run_once(i)
        if results is None:
            continue
        fails = [m for okk, m in results if not okk]
        if fails:
            total_fail += 1
            print(f"== run {i}/{runs}: FAIL ({len(results) - len(fails)}/{len(results)})")
            for okk, m in results:
                print(f"   {'ok ' if okk else 'FAIL'} {m}")
        else:
            print(f"== run {i}/{runs}: PASS ({len(results)}/{len(results)} checks)")
    print("ALL GREEN" if total_fail == 0 else f"{total_fail} RUN(S) FAILED")
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
