#!/usr/bin/env python3
"""ACTION WIRE E2E — the agent-mode action stream through the REAL protocol seam.

Chezy's law (2026-07-07): EVERY single action the agent does streams in,
immediately, as a consistent DAW component. The wire: each tool_use block the
sidecar pumps (and each mock-lane move) emits a structured
    {"kind":"action", "tool", "family", "summary", "track"}
event BEFORE the legacy activity line. This proves it end to end with zero
tokens: real sidecar process, isolated SOTADAW_IPC, SOTADAW_MOCK=1 +
SOTADAW_PARSE=0 (forces the mock composer rail, which fires the same
emit_action() kernel the real stream pumps use).

Checks:
  1. the run lands a proposal (the mock rail is unbroken by the wire)
  2. action events flowed, and every one carries tool+family+summary(+track)
  3. the expected mock moves are all present as actions:
     get_song(read) -> set_track_fx(fx, tracked) -> automate(fx) -> set_buses(master)
  4. IMMEDIACY: the first action lands BEFORE the proposal event (streams
     during the run, not as a post-hoc report)
  5. family map is total: no action shipped an empty family

Scrubs the scratch song + _prop_ + ipc dir after (isolation law).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_actwire"


def base_song():
    return {
        "version": 2, "bpm": 124, "lengthBars": 4, "key": "A minor",
        "masterGainDb": 0.0,
        "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
        "tracks": [
            {"name": "kick", "source": {"kind": "faust", "id": "kick808"},
             "gainDb": -6, "notes": [{"start": float(b), "len": 0.5, "pitch": 36, "vel": 0.9}
                                     for b in range(16)]},
            {"name": "pads", "source": {"kind": "faust", "id": "warmpad"},
             "gainDb": -10, "notes": [{"start": 0.0, "len": 8.0, "pitch": 57, "vel": 0.6}]},
        ],
    }


def events(ipc, rid):
    try:
        return [e for e in (json.loads(l) for l in open(os.path.join(ipc, "events.jsonl"))
                            if l.strip()) if e.get("id") == rid]
    except FileNotFoundError:
        return []


def main():
    fails = []

    def check(cond, label):
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        if not cond:
            fails.append(label)

    for f in os.listdir(SONGS):
        if f.startswith(SONG) or f.startswith(f"_prop_{SONG}"):
            os.remove(os.path.join(SONGS, f))
    json.dump(base_song(), open(os.path.join(SONGS, f"{SONG}.json"), "w"), indent=1)

    ipc = tempfile.mkdtemp(prefix="actwire_ipc_")
    py = os.path.join(ROOT, ".venv", "bin", "python")
    if not os.path.exists(py):
        py = sys.executable
    env = dict(os.environ, SOTADAW_IPC=ipc, SOTADAW_NO_UPLINK="1", SOTADAW_PARSE="0")
    side = subprocess.Popen([py, os.path.join(ROOT, "agent", "sidecar.py"), "--mock"],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    rid = 4001
    try:
        tmp = os.path.join(ipc, "request.json.tmp")
        with open(tmp, "w") as f:
            f.write(json.dumps({"type": "prompt", "id": rid, "song": SONG,
                                "text": "add motion and space to the pads"}))
        os.replace(tmp, os.path.join(ipc, "request.json"))
        t0 = time.time()
        evs = []
        while time.time() - t0 < 120:
            evs = events(ipc, rid)
            if any(e.get("kind") == "done" for e in evs):
                break
            time.sleep(0.25)

        kinds = [e.get("kind") for e in evs]
        check("proposal" in kinds, "the mock rail still lands a proposal")

        acts = [e for e in evs if e.get("kind") == "action"]
        check(len(acts) >= 4, f"action events flowed ({len(acts)} of them)")
        check(all(e.get("tool") and "summary" in e and "track" in e for e in acts),
              "every action carries tool + summary + track")
        check(all(e.get("family") for e in acts), "the family map is total (no blanks)")

        by_tool = {e.get("tool"): e for e in acts}
        check(by_tool.get("get_song", {}).get("family") == "read",
              "get_song streamed as a read action")
        fx = by_tool.get("set_track_fx", {})
        check(fx.get("family") == "fx" and fx.get("track") == "pads"
              and "filter" in fx.get("summary", ""),
              f"set_track_fx streamed on the target track ({fx.get('summary', '?')!r})")
        check(by_tool.get("automate", {}).get("family") == "fx"
              and "motion" in by_tool.get("automate", {}).get("summary", ""),
              "automate streamed with its point count")
        check(by_tool.get("set_buses", {}).get("family") == "master",
              "set_buses streamed as a master action")

        if acts and "proposal" in kinds:
            check(kinds.index("action") < kinds.index("proposal"),
                  "IMMEDIACY: the first action beat the proposal event")
    finally:
        side.send_signal(15)
        try:
            side.wait(timeout=6)
        except subprocess.TimeoutExpired:
            side.kill()
        for f in os.listdir(SONGS):
            if f.startswith(SONG) or f.startswith(f"_prop_{SONG}"):
                os.remove(os.path.join(SONGS, f))
        shutil.rmtree(ipc, ignore_errors=True)

    n_ok = 9 - len(fails)
    print(f"action-wire e2e: {n_ok}/9 " + ("clean" if not fails else "RED " + str(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
