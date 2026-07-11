#!/usr/bin/env python3
"""THE EARS BUS battery (E3 R1-R3, docs/EARS_BUS_DESIGN.md).

R1: the REAL m1 binary renders a bass fixture with SOTADAW_IPC isolated ->
    ears.jsonl carries valid, fresh, beat-monotone, low-dominant frames.
R2: listen_live summarizes the recorded frames (and reports silence on an empty
    rig); sidecar's ears_now_line renders a fresh frame into the NOW block and
    refuses stale ones.
R3: the dj_listener verdict kernel consumes frames 1:1 — synthetic PLATEAU and
    CLIFF sequences trigger through frames_to_feats, a rising arc stays clean,
    and the CLI --frames lane round-trips.

SKIP-green when the m1 binary is absent (fresh box) — R2/R3 still run on
synthetic frames. Exit code IS the verdict.
"""
import json
import math
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "agent"))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)
    print(f"  {'OK ' if cond else 'XX '}{msg}")


def synth_frames(rms_seq, sec_per=1.0, bands=(-12.0, -20.0, -28.0, -40.0)):
    """Ears frames with a given rms trajectory (playing, low-dominant)."""
    t0 = time.time()
    return [{"t": t0 + i, "beat": i * 2.0, "sec": i * sec_per, "playing": True,
             "rms_db": [r, r], "peak_db": [r + 8, r + 8], "dbtp_q": r + 8,
             "bands_db": list(bands), "crest_db": 8.0}
            for i, r in enumerate(rms_seq)]


def main():
    ipc = tempfile.mkdtemp(prefix="ears_battery_")
    print("== THE EARS BUS BATTERY (E3) ==")

    # ---- R1: the real binary streams frames during a headless render ----
    frames = []
    if not os.path.exists(M1):
        print("  R1 SKIP: m1 binary not built on this box")
    else:
        song = {"version": 2, "bpm": 120, "lengthBars": 16, "masterGainDb": 0.0,
                "master": [], "tracks": [{
                    "name": "bass", "source": {"kind": "faust", "id": "hardkick"},
                    "gainDb": -6.0,
                    "notes": [{"start": float(b), "len": 0.5, "pitch": 36, "vel": 0.9}
                              for b in range(0, 64, 2)]}]}
        sp = os.path.join(ipc, "fixture.json")
        json.dump(song, open(sp, "w"))
        r = subprocess.run([M1, "render", sp, os.path.join(ipc, "fixture.wav")],
                           capture_output=True, text=True, timeout=300,
                           env=dict(os.environ, SOTADAW_IPC=ipc))
        ej = os.path.join(ipc, "ears.jsonl")
        ok(r.returncode == 0 and os.path.exists(ej),
           "R1: render ran and ears.jsonl exists")
        if os.path.exists(ej):
            for ln in open(ej):
                frames.append(json.loads(ln))          # raises = battery fails loudly
            live = [f for f in frames if f["playing"]]
            ok(len(live) >= 3, f"R1: >=3 live frames streamed ({len(live)})")
            beats = [f["beat"] for f in live]
            ok(beats == sorted(beats), "R1: beat advances monotonically")
            ok(all(abs(time.time() - f["t"]) < 300 for f in live),
               "R1: frame timestamps are wall-clock fresh")
            if live:
                # judge the LOUDEST frame — a fast render's wall-clock drains can
                # sample pre-roll or note-gap spans that are honestly silent
                loud = max(live, key=lambda f: sum(f["rms_db"]))
                b = loud["bands_db"]
                ok(b[0] == max(b) and b[0] > -60,
                   f"R1: bass fixture's loudest frame reads low-dominant ({b})")
                ok(-60 < sum(loud["rms_db"]) / 2 < 0,
                   f"R1: rms in a sane audible window ({sum(loud['rms_db'])/2:.1f})")

    # ---- R2: listen_live over the recorded frames + the silent path ----
    os.environ["SOTADAW_IPC"] = ipc
    import daw_mcp
    if frames:
        out = daw_mcp.t_listen_live({"seconds": 300})
        ok(out.startswith("HEARING") and "bands:" in out and "low" in out,
           "R2: listen_live summarizes live frames (rms/bands/beat)")
    empty = tempfile.mkdtemp(prefix="ears_silent_")
    os.environ["SOTADAW_IPC"] = empty
    out = daw_mcp.t_listen_live({"seconds": 5})
    ok("silent" in out, "R2: empty rig -> 'the ears are silent' (not an error)")
    ok("listen_live" in daw_mcp.CORE_TOOLS and "listen_live" in daw_mcp.TOOLS,
       "R2: listen_live registered on the core lane")

    # ---- R2: sidecar NOW-block line (fresh renders, stale refuses) ----
    os.environ["SOTADAW_IPC"] = ipc
    import sidecar
    sidecar.IPC = ipc                       # module may be cached from another rig
    fresh = synth_frames([-10.0])
    with open(os.path.join(ipc, "ears.jsonl"), "w") as f:
        f.write(json.dumps(fresh[0]) + "\n")
    line = sidecar.ears_now_line()
    ok(line.startswith("you are HEARING") and "low-dominant" in line,
       "R2: NOW block renders a fresh frame as one HEARING line")
    stale = dict(fresh[0], t=time.time() - 60)
    with open(os.path.join(ipc, "ears.jsonl"), "w") as f:
        f.write(json.dumps(stale) + "\n")
    ok(sidecar.ears_now_line() == "", "R2: stale frames never reach the prompt")

    # ---- R3: the verdict kernel over frames (live lane) ----
    import dj_listener
    # PLATEAU: 3min pinned at -10dB with real edges around it
    seq = [-30.0] * 10 + [-10.0] * 180 + [-14.0] * 20 + [-30.0] * 5
    feats = dj_listener.frames_to_feats(synth_frames(seq), hop=8.0)
    v = dj_listener.listen(feats, 8.0)
    ok(any(x["kind"] == "PLATEAU" for x in v),
       f"R3: pinned energy through the frames lane -> PLATEAU ({[x['kind'] for x in v]})")
    # CLIFF: 9dB one-hop drop mid-set
    seq = [-12.0] * 40 + [-21.0] * 40 + [-12.0] * 30
    feats = dj_listener.frames_to_feats(synth_frames(seq), hop=8.0)
    v = dj_listener.listen(feats, 8.0)
    ok(any(x["kind"] == "CLIFF" for x in v),
       f"R3: one-hop 9dB drop -> CLIFF ({[x['kind'] for x in v]})")
    # clean rising arc -> no PLATEAU/CLIFF
    seq = [-30.0 + 18.0 * math.sin(i / 25.0) + i * 0.05 for i in range(150)]
    feats = dj_listener.frames_to_feats(synth_frames(seq), hop=8.0)
    v = dj_listener.listen(feats, 8.0)
    ok(not any(x["kind"] in ("PLATEAU", "CLIFF") for x in v),
       f"R3: breathing arc stays clean ({[x['kind'] for x in v]})")
    # CLI --frames round-trip
    fp = os.path.join(ipc, "replay.jsonl")
    with open(fp, "w") as f:
        for fr in synth_frames([-30.0] * 10 + [-10.0] * 180 + [-30.0] * 5):
            f.write(json.dumps(fr) + "\n")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "dj_listener.py"),
                        "--frames", fp], capture_output=True, text=True, timeout=60)
    ok(r.returncode == 0 and "PLATEAU" in r.stdout,
       "R3: dj_listener --frames CLI replays the live lane")

    print(f"ears-bus battery: {PASS}/{PASS + len(FAIL)} " + ("clean" if not FAIL else "RED"))
    for f in FAIL:
        print("FAIL:", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
