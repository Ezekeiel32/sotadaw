#!/usr/bin/env python3
"""MIDI CLOCK E2E — external gear can follow OUR transport.

Boots the real app (--snapshot, SOTADAW_SNAP_CLOCK targets ALSA's always-present
'Midi Through'), rolls the REAL transport for 3.5s at 120bpm, and counts what a
piece of gear would hear on the wire via aseqdump: 24ppqn Clock (0xF8) at the
right RATE, plus Start/Continue framing.

  expected ticks ~= 3.5s * 120bpm/60 * 24 = 168 (wide band for start/stop slop)

Usage: python3 tools/midi_clock_e2e.py [runs=3]
"""
import json, os, re, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
BIN = os.path.join(ROOT, "app", "build", "sotadaw_artefacts", "Release", "SOTA DAW")
SONG = "_clock_e2e"

def run_once(idx):
    checks = []
    def ok(cond, msg):
        checks.append((bool(cond), msg))
    json.dump({"version": 2, "bpm": 120, "lengthBars": 8, "masterGainDb": 0.0,
               "master": [],
               "tracks": [{"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
                           "gainDb": -6,
                           "notes": [{"start": float(i), "len": 0.2, "pitch": 36, "vel": 0.8}
                                     for i in range(32)]}]},
              open(os.path.join(SONGS, f"{SONG}.json"), "w"))
    dump = subprocess.Popen(["aseqdump", "-p", "Midi Through"],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    time.sleep(0.5)
    ipc = tempfile.mkdtemp(prefix="clock_ipc_")
    out = tempfile.mkdtemp(prefix="clock_png_")
    env = dict(os.environ, SOTADAW_SNAPSHOT="1", SOTADAW_SANDBOX="1", SOTADAW_SNAP_CLOCK="Through",
               SOTADAW_SONG=SONG, SOTADAW_IPC=ipc)
    try:
        app = subprocess.run([BIN, "--snapshot", out], env=env, cwd=ROOT,
                             capture_output=True, text=True, timeout=90)
        ok("[clock] armed" in app.stdout, "clock armed on Midi Through")
        ok("[clock] transport rolling" in app.stdout, "transport rolled")
        time.sleep(0.5)
        dump.send_signal(signal.SIGINT)
        try:
            wire, _ = dump.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            dump.kill()
            wire, _ = dump.communicate()
        # HERMETIC ATTRIBUTION (suite red 2026-07-11: 311 clocks ~= TWO streams —
        # a LIVE app instance with clock out also feeds Midi Through; counting
        # the whole wire doubles). OUR app is the client that sent Start/Continue
        # DURING this window (a foreign always-running clock started long ago) —
        # count Clock only from that client. aseqdump lines lead with src:port.
        by_client = {}
        start_clients = set()
        for m in re.finditer(r"(?im)^\s*(\d+):\d+\s+(?:.*\b(clock)\b|.*\b(start|continue)\b)", wire):
            cli = m.group(1)
            if m.group(2):
                by_client[cli] = by_client.get(cli, 0) + 1
            else:
                start_clients.add(cli)
        ours = sorted(start_clients, key=lambda c: by_client.get(c, 0), reverse=True)
        clocks = by_client.get(ours[0], 0) if ours else sum(by_client.values())
        starts = len(re.findall(r"(?im)^.*\b(start|continue)\b.*$", wire))
        foreign = sum(v for c, v in by_client.items() if not ours or c != ours[0])
        ok(100 <= clocks <= 240,
           f"24ppqn on the wire: {clocks} Clock msgs in ~3.5s @120 (expect ~168"
           + (f"; {foreign} foreign clocks ignored" if foreign else "") + ")")
        ok(starts >= 1, f"transport framing on the wire (Start/Continue x{starts})")
    finally:
        if dump.poll() is None:
            dump.kill()
        p = os.path.join(SONGS, f"{SONG}.json")
        os.path.exists(p) and os.remove(p)
        shutil.rmtree(ipc, ignore_errors=True)
        shutil.rmtree(out, ignore_errors=True)
    fails = [m for okk, m in checks if not okk]
    print(f"== run {idx}: {'PASS' if not fails else 'FAIL'} ({len(checks) - len(fails)}/{len(checks)})")
    for okk, m in checks:
        print(f"   {'ok ' if okk else 'FAIL'} {m}")
    return not fails

if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    bad = sum(0 if run_once(i + 1) else 1 for i in range(runs))
    print(f"\nMIDI CLOCK: {'ALL GREEN' if bad == 0 else f'{bad} RUN(S) RED'} over {runs}")
    sys.exit(bad)
