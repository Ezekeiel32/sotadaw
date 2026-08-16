#!/usr/bin/env python3
"""MUSIC COURTS E2E — the real seam, the real render (PRODUCER MIND P2/P4).

Plants a sour, misaligned proposal in songs/, then drives sidecar's ACTUAL
render_and_analyze (SOTADAW_IPC-isolated rig, real m1 render) and asserts:
  1. the sour notes were HEALED on disk (D#4 class snapped in key)
  2. the shadow-pair drift (keys 0.06 late vs lead) was aligned
  3. a 'courts' event landed in events.jsonl with key_ok true after heal
  4. the wav rendered (the healed truth is what gets heard)
  5. base songs are untouched by the courts (guard proof)
Cleans up after itself. Exit 0 = proof.
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
PROP = "_prop_courtrig"
BASE = "courtrig_base"


def mknote(start, pitch, ln=0.5, vel=0.9):
    return {"start": float(start), "len": ln, "pitch": int(pitch), "vel": vel}


def planted_song():
    lead = [mknote(s, p) for s, p in
            [(0, 69), (1, 72), (2, 71), (3, 69), (4, 64), (5, 65), (6, 67), (7, 69)]]
    lead[1] = mknote(1, 70, ln=1.0)     # A#4 long: sour in A minor
    lead[5] = mknote(5, 63, ln=1.0)     # D#4 long: sour
    keys = [mknote(float(n["start"]) + 0.06, int(n["pitch"]) - 12) for n in lead]
    return {"version": 2, "bpm": 120, "lengthBars": 2, "key": "A minor",
            "tracks": [
                {"name": "lead", "source": {"id": "pluck_soft"}, "notes": lead},
                {"name": "keys", "source": {"id": "warm_epiano"}, "notes": keys}]}


def main():
    ipc = tempfile.mkdtemp(prefix="courtrig_ipc_")
    os.environ["SOTADAW_IPC"] = ipc
    prop_j = os.path.join(SONGS, f"{PROP}.json")
    base_j = os.path.join(SONGS, f"{BASE}.json")
    fails = []
    try:
        json.dump(planted_song(), open(prop_j, "w"), indent=1)
        json.dump(planted_song(), open(base_j, "w"), indent=1)
        sys.path.insert(0, os.path.join(ROOT, "agent"))
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import sidecar  # noqa: E402  (IPC redirected; import is side-effect-light)

        # P8: the CURRENT ask rides request-scoped — judge the take against it
        sidecar._EMIT_CTX.ask = "make a full 10 minute epic in A minor"
        ok_render = sidecar.render_and_analyze("courtrig", PROP, "proposal")
        if not ok_render:
            fails.append("render_and_analyze returned falsy on the prop")

        healed = json.load(open(prop_j))
        if not healed.get("chords"):
            fails.append("CHORD SPINE LAW: no chords[] inferred on the prop")
        lead = next(t for t in healed["tracks"] if t["name"] == "lead")
        pcs = {int(n["pitch"]) % 12 for n in lead["notes"]}
        am = {9, 11, 0, 2, 4, 5, 7}
        if not pcs <= am | {8}:   # leading tone pardoned
            fails.append(f"sour pitches survived on disk: {sorted(pcs - am)}")
        keys = next(t for t in healed["tracks"] if t["name"] == "keys")
        la = sorted(float(n["start"]) for n in lead["notes"])
        lb = sorted(float(n["start"]) for n in keys["notes"])
        if la != lb:
            fails.append(f"shadow drift survived: {lb[:4]} vs {la[:4]}")

        ev_path = os.path.join(ipc, "events.jsonl")
        courts_evs = []
        if os.path.exists(ev_path):
            for line in open(ev_path):
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                if e.get("kind") == "courts":
                    courts_evs.append(e)
        if not courts_evs:
            fails.append("no 'courts' event in events.jsonl")
        else:
            ev = courts_evs[0]
            if not (ev.get("key_ok") and ev.get("healed", 0) >= 2):
                fails.append(f"courts event not green/healed: {ev}")
            # the 2-bar take cannot satisfy a 10-minute ask — honesty must ride
            if ev.get("contracts_ok") is not False or not any(
                    str(u).startswith("duration") for u in ev.get("unmet", [])):
                fails.append(f"instruction court missed the 10-minute contract: {ev}")

        wav = os.path.join(SONGS, f"{PROP}.wav")
        if not (os.path.exists(wav) and os.path.getsize(wav) > 1000):
            fails.append("prop wav missing — heal must land in the render")

        # base guard: rendering the BASE song must NOT mutate it
        before = open(base_j).read()
        sidecar.render_and_analyze("courtrig2", BASE, "base")
        if open(base_j).read() != before:
            fails.append("BASE song mutated — the proposal guard is broken")
    finally:
        for p in (prop_j, base_j,
                  os.path.join(SONGS, f"{PROP}.wav"),
                  os.path.join(SONGS, f"{BASE}.wav")):
            if os.path.exists(p):
                os.remove(p)
        shutil.rmtree(ipc, ignore_errors=True)
    if fails:
        print("MUSIC COURT E2E FAIL:\n  - " + "\n  - ".join(fails))
        return 1
    print("MUSIC COURT E2E PASS — planted sour+drift healed at the real seam, "
          "courts event green, wav carries the healed truth, base untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
