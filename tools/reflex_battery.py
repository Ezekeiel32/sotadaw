#!/usr/bin/env python3
"""THE BRAIN BR-B battery — reflex kernels replayed on deterministic streams
(fixture-pure: no daemon, no renders, no live ipc). Proves: each verdict fires
on its planted crime and ONLY then, cooldowns coalesce, torn tails never
poison, rotation restarts, the prompt rider gates on age, and the in-flight
scan advises capped + witness-blind + never-guesses-keyless."""
import json
import os
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reflex_court as rc

N = [0, 0]


def need(ok, what):
    N[1] += 1
    if ok:
        N[0] += 1
    else:
        print(f"  FAIL: {what}")
    return ok


def frames(n, t0=0.0, dt=0.1, **kw):
    base = {"playing": True, "peak_db": [-6.0], "crest_db": 12.0,
            "bands_db": [-20.0, -22.0, -24.0, -30.0], "beat": 1.0}
    out = []
    for i in range(n):
        fr = dict(base)
        fr.update(kw)
        if "rms_db" not in kw:
            # real ears breathe — a constant rms IS the flatline crime, so the
            # default fixture must move (music-shaped ±3dB wander)
            v = -14.0 + (i % 20) * 0.3
            fr["rms_db"] = [v, v]
        fr["t"] = t0 + i * dt
        out.append(fr)
    return out


def run(stream):
    r, ev = rc.Reflex(), []
    for fr in stream:
        ev.extend(r.feed(fr))
    return ev


def main():
    # ---- R1: clean stream fires nothing
    need(run(frames(120)) == [], "clean 12s stream: zero events")
    need(run(frames(120, playing=False, rms_db=[-90, -90])) == [],
         "not playing: silence never convicts")

    # ---- ceiling: fires once, cooldown holds, refires after
    ev = run(frames(60, peak_db=[0.0]))
    need(len(ev) == 1 and ev[0]["kind"] == "ceiling", f"ceiling fires ONCE in 6s (got {len(ev)})")
    need(ev[0]["severity"] == "hard" and "-" not in ev[0]["line"].split(":")[0],
         "ceiling is hard with a numbered line")
    ev = run(frames(400, peak_db=[0.0]))
    need(len(ev) == 3, f"40s ceiling: cooldown paces to ~3 events (got {len(ev)})")

    # ---- dead output: needs 2s sustained
    ev = run(frames(15, rms_db=[-80, -80]))
    need(ev == [], "1.5s quiet: dead needs 2s")
    ev = run(frames(30, rms_db=[-80, -80]))
    need(len(ev) == 1 and ev[0]["kind"] == "dead", "3s quiet while playing: dead fires")
    ev = run(frames(30, rms_db=[-80, -80], beat=-0.9))
    need(ev == [], "PRE-ROLL PARDON: silent count-in (beat<0.5) never convicts "
                   "(first live wolf 2026-07-16)")

    # ---- crest collapse
    ev = run(frames(40, crest_db=4.0))
    need(len(ev) == 1 and ev[0]["kind"] == "crest" and ev[0]["severity"] == "advice",
         "4s of crest 4dB: squash advisory")
    need(run(frames(20, crest_db=4.0)) == [], "2s of low crest: under the 3s need")

    # ---- mud: lowmid dominance
    ev = run(frames(30, bands_db=[-30.0, -18.0, -28.0, -32.0]))
    need(len(ev) == 1 and ev[0]["kind"] == "mud", "lowmid +10dB for 3s: mud fires")
    need(run(frames(30, bands_db=[-20.0, -19.0, -22.0, -28.0])) == [],
         "lowmid within margin: no mud")

    # ---- stereo lean
    ev = run(frames(40, rms_db=[-10.0, -20.0]))
    need(len(ev) == 1 and ev[0]["kind"] == "lean", "10dB lean for 4s: lean fires")

    # ---- flatline: constant rms 12s fires; varying never
    ev = run(frames(120, rms_db=[-14.0, -14.0], peak_db=[-8.0]))
    need(any(e["kind"] == "flatline" for e in ev) and len(ev) == 1,
         f"12s constant rms: flatline (got {[e['kind'] for e in ev]})")
    vary = frames(120)
    for i, fr in enumerate(vary):
        fr["rms_db"] = [-14.0 + (i % 20) * 0.3, -14.0 + (i % 20) * 0.3]
    need(run(vary) == [], "moving rms: no flatline")

    # ---- broken frames never raise
    r = rc.Reflex()
    need(r.feed({}) == [] and r.feed({"rms_db": "junk"}) == [], "garbage frames -> []")

    with tempfile.TemporaryDirectory(prefix="reflex_bat_") as root:
        ipc = os.path.join(root, "agent", "ipc")
        os.makedirs(ipc, exist_ok=True)
        ep = os.path.join(ipc, "ears.jsonl")

        # ---- tail_frames: incremental, torn-tolerant, rotation-aware
        with open(ep, "w") as f:
            f.write(json.dumps({"t": 1.0}) + "\n" + '{"torn": \n')
        fr1, pos, ino = rc.tail_frames(ep)
        need(len(fr1) == 1 and fr1[0]["t"] == 1.0, "tail reads valid rows, skips torn")
        with open(ep, "a") as f:
            f.write(json.dumps({"t": 2.0}) + "\n")
        fr2, pos, ino = rc.tail_frames(ep, pos, ino)
        need(len(fr2) == 1 and fr2[0]["t"] == 2.0, "incremental tail reads only NEW rows")
        os.remove(ep)
        with open(ep, "w") as f:
            f.write(json.dumps({"t": 9.0}) + "\n")
        fr3, pos, ino = rc.tail_frames(ep, pos, ino)
        need(len(fr3) == 1 and fr3[0]["t"] == 9.0, "rotation restarts from head")
        need(rc.tail_frames(os.path.join(root, "void.jsonl")) == ([], 0, None),
             "missing file -> empty, never raises")

        # ---- state file + prompt rider
        rc._write_state(ipc, [{"t": time.time(), "kind": "mud", "severity": "advice",
                               "line": "lowmid-dominant: -18 dB vs low -30"}])
        ln = rc.state_line(ipc)
        need("REFLEXES flagged" in ln and "lowmid" in ln, "state_line rides fresh verdicts")
        rc._write_state(ipc, [{"t": time.time() - 500, "kind": "lean", "line": "old"}])
        need("old" not in rc.state_line(ipc), "stale events age out of the rider")
        with open(os.path.join(ipc, rc.STATE_NAME), "w") as f:
            json.dump({"t": time.time() - 500, "events": [{"t": 0, "line": "x"}]}, f)
        need(rc.state_line(ipc) == "", "stale state file -> empty rider")

        # ---- watch(): the glue loop end-to-end against fixture files
        # wall-clock frame times: production EarsTap stamps real epoch t, and
        # the state rider ages by the same clock
        with open(ep, "w") as f:
            for fr in frames(20, t0=time.time() - 2.0, peak_db=[0.0]):
                f.write(json.dumps(fr) + "\n")
        stop = threading.Event()
        got = []
        th = threading.Thread(target=rc.watch, args=(ipc, root),
                              kwargs={"emit_fn": got.append, "poll_s": 0.05,
                                      "stop": stop}, daemon=True)
        th.start()
        time.sleep(0.6)
        stop.set()
        th.join(timeout=2)
        need(len(got) >= 1 and got[0]["kind"] == "ceiling", "watch loop fires on planted clip")
        need(os.path.exists(os.path.join(root, "telemetry", rc.LOG_NAME)),
             "watch logs to telemetry/reflex.jsonl")
        need("ceiling" in rc.state_line(ipc, now=time.time()),
             "watch wrote the state the rider reads")

    # ---- R2: in-flight scan
    doc = {"key": "D minor", "bpm": 120,
           "tracks": [{"name": "bass", "notes": [
               {"start": float(i), "len": 1.0, "pitch": 50, "vel": 0.8}
               for i in range(6)]}]}
    sc = rc.InflightScan()
    need(sc.feed_doc(doc, now=1000.0) is None, "in-key stream: silent")
    sour = [{"start": 10.0 + i, "len": 1.0, "pitch": p, "vel": 0.8}
            for i, p in enumerate((63, 66, 68, 75, 78))]     # Eb F# Ab Eb F# vs D minor
    doc2 = {"key": "D minor", "bpm": 120,
            "tracks": [{"name": "bass", "notes": doc["tracks"][0]["notes"] + sour}]}
    ln = sc.feed_doc(doc2, now=1030.0)
    need(ln is not None and "outside D minor" in ln and "@bar" in ln,
         f"5 sour notes: ONE advisory line (got {ln!r})")
    need(sc.feed_doc(doc2, now=1031.0) is None, "same snapshot again: notes deduped, no re-fire")
    doc3 = {"key": "D minor", "bpm": 120,
            "tracks": [{"name": "bass", "notes": doc2["tracks"][0]["notes"] +
                        [{"start": 30.0 + i, "len": 1.0, "pitch": 63, "vel": 0.8}
                         for i in range(6)]}]}
    need(sc.feed_doc(doc3, now=1032.0) is None, "min-gap holds inside 20s")
    ln2 = sc.feed_doc(doc3, now=1060.0)
    need(ln2 is None or "outside" in ln2, "after the gap a second (capped) line may fire")
    sc2 = rc.InflightScan()
    wdoc = {"key": "D minor", "tracks": [
        {"name": "bass_sketch", "notes": sour * 3},
        {"name": "kick", "notes": sour * 3}]}
    need(sc2.feed_doc(wdoc, now=1.0) is None, "witness + drum lanes never testify")
    need(rc.InflightScan().feed_doc({"tracks": [{"name": "bass", "notes": sour}]},
                                    now=1.0) is None, "keyless doc: never guess, stay silent")
    need(rc.InflightScan().feed_doc("garbage") is None, "garbage doc -> None")

    print(f"reflex_battery: {N[0]}/{N[1]}")
    sys.exit(0 if N[0] == N[1] else 1)


if __name__ == "__main__":
    main()
