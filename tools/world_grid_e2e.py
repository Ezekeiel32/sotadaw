#!/usr/bin/env python3
"""#1 THE CONVERSION BOUNDARY E2E — den 8/16 meters are LIVE in the engine.
Engine BeatPositions are DENOMINATOR-beats; every arrangement position now
crosses quarter->engine through Song::engineBeat. Proof = measured audio:
kick onsets land where the QUARTER-beat ruler says bars start.
Run: python3 tools/world_grid_e2e.py"""
import json, os, struct, subprocess, sys, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")

N = {"pass": 0, "fail": 0}
def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""),
          flush=True)

def render(doc, name):
    sp = os.path.join(SONGS, f"{name}.json")
    wp = os.path.join(SONGS, f"{name}.wav")
    json.dump(doc, open(sp, "w"), indent=1)
    r = subprocess.run([M1, "render", sp, wp], capture_output=True, text=True,
                       timeout=180)
    if r.returncode != 0:
        raise RuntimeError("m1: " + (r.stdout + r.stderr)[-300:])
    return wp

def onsets(wp, thresh=0.08, refract_s=0.9):
    # refractory must outlast the kick's decay re-cross (~0.25s) and stay under
    # the tightest bar spacing in any fixture (1.5s)
    """kick onset times: rising edges of the abs-envelope (24-bit aware)."""
    w = wave.open(wp)
    sw, ch, sr, n = w.getsampwidth(), w.getnchannels(), w.getframerate(), w.getnframes()
    raw = w.readframes(n)
    w.close()
    if sw == 3:
        xs = [int.from_bytes(raw[i:i + 3], "little", signed=True) / 8388608.0
              for i in range(0, len(raw), 3 * ch)]
    else:
        xs = [s / 32768.0 for s in struct.unpack(f"<{n * ch}h", raw)[::ch]]
    hits, last = [], -1.0
    for i, v in enumerate(xs):
        t = i / sr
        if abs(v) > thresh and t - last > refract_s:
            hits.append(t)
            last = t
    return hits

def kick_song(meter, bars, bar_starts_q, length_bars, bpm=120):
    return {"version": 2, "bpm": bpm, "lengthBars": length_bars,
            "masterGainDb": 0, "master": [], "meterMap": meter,
            "tracks": [{"name": "kick", "source": {"kind": "faust", "id": "kick_808"},
                        "gainDb": -3, "pan": 0,
                        "notes": [{"start": q, "len": 0.4, "pitch": 36, "vel": 1.0}
                                  for q in bar_starts_q]}]}

def close(measured, want, tol=0.035):
    return len(measured) == len(want) and all(abs(a - b) <= tol
                                              for a, b in zip(measured, want))

def main():
    names = []
    try:
        # A) 7/8 x4 bars @120: bar = 3.5 q-beats = 1.75s. Kicks on every bar start.
        want = [0.0, 1.75, 3.50, 5.25]
        wp = render(kick_song([{"bar": 0, "num": 7, "den": 8}], 4,
                              [0.0, 3.5, 7.0, 10.5], 4), "_grid78")
        names.append("_grid78")
        got = onsets(wp)
        check("7/8: four bar-start kicks land at 1.75s bars", close(got, want),
              f"want {want} got {[round(t, 3) for t in got]}")

        # B) mid-song switch 4/4 (2 bars) -> 7/8 (2 bars): starts q 0,4,8,11.5
        #    times 0,2,4,5.75
        want = [0.0, 2.0, 4.0, 5.75]
        wp = render(kick_song([{"bar": 2, "num": 7, "den": 8}], 4,
                              [0.0, 4.0, 8.0, 11.5], 4), "_gridswitch")
        names.append("_gridswitch")
        got = onsets(wp)
        check("4/4->7/8 switch: onsets exact across the boundary", close(got, want),
              f"want {want} got {[round(t, 3) for t in got]}")

        # C) 6/8 x4 @120: bar = 3 q-beats = 1.5s
        want = [0.0, 1.5, 3.0, 4.5]
        wp = render(kick_song([{"bar": 0, "num": 6, "den": 8}], 4,
                              [0.0, 3.0, 6.0, 9.0], 4), "_grid68")
        names.append("_grid68")
        got = onsets(wp)
        check("6/8: 1.5s bars measured", close(got, want),
              f"want {want} got {[round(t, 3) for t in got]}")

        # D) den==4 regression: 3/4 bars = 1.5s (the shipped half must not move)
        want = [0.0, 1.5, 3.0, 4.5]
        wp = render(kick_song([{"bar": 0, "num": 3, "den": 4}], 4,
                              [0.0, 3.0, 6.0, 9.0], 4), "_grid34")
        names.append("_grid34")
        got = onsets(wp)
        check("3/4 regression: identical to before", close(got, want),
              f"want {want} got {[round(t, 3) for t in got]}")

        # E) mapless identity: engineBeat must be a no-op without a meterMap
        want = [0.0, 2.0, 4.0, 6.0]
        wp = render(kick_song([], 4, [0.0, 4.0, 8.0, 12.0], 4), "_gridnone")
        names.append("_gridnone")
        got = onsets(wp)
        check("no meterMap: pure 4/4 identity", close(got, want),
              f"want {want} got {[round(t, 3) for t in got]}")

        # F) 12/16 (den 16): bar = 3 q-beats = 1.5s
        want = [0.0, 1.5, 3.0]
        wp = render(kick_song([{"bar": 0, "num": 12, "den": 16}], 3,
                              [0.0, 3.0, 6.0], 3), "_grid1216")
        names.append("_grid1216")
        got = onsets(wp)
        check("12/16: den-16 bars real", close(got, want),
              f"want {want} got {[round(t, 3) for t in got]}")
    finally:
        for nm in names:
            for ext in (".json", ".wav"):
                p = os.path.join(SONGS, nm + ext)
                os.path.exists(p) and os.remove(p)
    print(f"\n{N['pass']} passed, {N['fail']} failed")
    sys.exit(1 if N["fail"] else 0)

if __name__ == "__main__":
    main()
