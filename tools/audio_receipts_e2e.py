#!/usr/bin/env python3
"""EB3 E2E — one REAL proposal carries surgical.audio_verified:true end-to-end.

Isolated-IPC recipe (CLAUDE.md law): own SOTADAW_IPC dir, scratch song name,
exact-pid kill, telemetry scrubbed after. Journey: verb-bus humanize on ONE track
(files a track_wild receipt, zero tokens) -> sidecar scope law says CLEAN ->
SOTADAW_AUDIO_RECEIPTS=1 arms the null court -> base+prop stems render, subtract ->
proposal event ships surgical.audio_verified. The negative case (air moves out of
scope) is proven at the kernel level by null_bench --selftest C3.

usage: audio_receipts_e2e.py [N]   (default 1 run; exit 0 = green)
"""
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_avr_song"

PASS, FAIL = [], []


def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f" — {d}" if d else ""), flush=True)


def mini_song():
    kick = [{"start": b, "len": 0.4, "pitch": 36, "vel": 0.95} for b in range(0, 8, 2)]
    hat = [{"start": b * 0.5, "len": 0.1, "pitch": 70, "vel": 0.6} for b in range(16)]
    bass = [{"start": i * 2.0, "len": 1.6, "pitch": 38, "vel": 0.8} for i in range(4)]
    mk = lambda nm, src, notes: {"name": nm, "source": {"kind": "faust", "id": src},
                                 "gainDb": -6.0, "notes": notes}
    return {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0, "master": [],
            "tracks": [mk("kick", "kick_808", kick), mk("hat", "hat", hat),
                       mk("bass", "bass_warm", bass)]}


def scrub():
    for f in os.listdir(SONGS):
        if SONG in f or f.startswith("_null_avr"):
            p = os.path.join(SONGS, f)
            (shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p))
    for tn in ("proposals.jsonl", "null_verdicts.jsonl"):
        tel = os.path.join(ROOT, "telemetry", tn)
        if os.path.exists(tel):
            lines = [l for l in open(tel) if SONG not in l]
            open(tel, "w").writelines(lines)


def one_run(i):
    ipc = tempfile.mkdtemp(prefix="avr_ipc_")
    env = dict(os.environ, SOTADAW_IPC=ipc, SOTADAW_AUDIO_RECEIPTS="1",
               SOTADAW_SANDBOX="1")
    with open(os.path.join(SONGS, f"{SONG}.json"), "w") as f:
        json.dump(mini_song(), f, indent=1)
    proc = subprocess.Popen([sys.executable, os.path.join(ROOT, "agent", "sidecar.py")],
                            env=env, cwd=ROOT, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.5)
        req = {"id": f"avr{i}", "type": "verb", "verb": "humanize", "song": SONG,
               "args": {"track": "hat", "amount": 0.5, "seed": 3}}
        with open(os.path.join(ipc, "request.json"), "w") as f:
            json.dump(req, f)
        ev_path = os.path.join(ipc, "events.jsonl")
        deadline = time.time() + 150
        prop_ev, null_line, done = None, None, False
        while time.time() < deadline and not done:
            time.sleep(0.5)
            if not os.path.exists(ev_path):
                continue
            for line in open(ev_path):
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                if ev.get("kind") == "proposal" and ev.get("song") == SONG:
                    prop_ev = ev
                if ev.get("kind") == "activity" and "[null]" in ev.get("text", ""):
                    null_line = ev["text"]
                if ev.get("kind") == "done":
                    done = True
        check(f"run{i} proposal event landed", prop_ev is not None)
        s = (prop_ev or {}).get("surgical") or {}
        check(f"run{i} scope law CLEAN (receipted verb)", s.get("clean") is True,
              json.dumps(s)[:140])
        check(f"run{i} audio_verified:true rides the event",
              s.get("audio_verified") is True, str(s.get("audio_verified")))
        check(f"run{i} [null] activity testified", null_line is not None
              and ("audio-proven" in null_line or "SURGICAL" in null_line),
              (null_line or "")[:120])
        # NullVerdict telemetry (E12): the live court wrote a jsonl line for THIS song
        nvp = os.path.join(ROOT, "telemetry", "null_verdicts.jsonl")
        nv = None
        if os.path.exists(nvp):
            for line in open(nvp):
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("song") == SONG:
                    nv = rec
        check(f"run{i} NullVerdict telemetry written (E12 live)",
              nv is not None and nv.get("audio_verified") is True,
              json.dumps(nv)[:120] if nv else "no line")
    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(ipc, ignore_errors=True)
        scrub()


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for i in range(n):
        one_run(i)
    print(f"\n== AUDIO RECEIPTS E2E: {len(PASS)} pass / {len(FAIL)} fail ==")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
