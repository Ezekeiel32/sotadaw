#!/usr/bin/env python3
"""scene_bounce.py — give the launcher EARS: render any scene column as audio.

  scene_bounce.py <song.json> <scene_index|scene_name> [--bars N] [--out x.wav]

renderToFile never exercises launcher playback (known engine limitation), so
this MATERIALIZES scene k onto the timeline of a scratch copy: each track's
slot k becomes looped audioClips (audio slots, warp preserved) or repeated
notes (MIDI slots) for N bars, then m1 renders it. The scratch song is kept
next to the output for inspection (_scene_<k>_<name>.json).
"""
import argparse, json, math, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")


def bounce(song_path, scene, bars=None, out=None):
    song = json.load(open(song_path))
    scenes = [s.get("name", str(i)) for i, s in enumerate(song.get("scenes", []))]
    if not scenes:
        raise SystemExit("song has no scenes")
    try:
        k = int(scene)
    except ValueError:
        k = next((i for i, n in enumerate(scenes) if scene.lower() in n.lower()), -1)
    if not (0 <= k < len(scenes)):
        raise SystemExit(f"no scene {scene!r} (have {scenes})")

    bpm = float(song.get("bpm", 120))
    # default length: the longest slot in the column, in bars (min 4)
    longest = 16.0
    for t in song.get("tracks", []):
        sl = (t.get("slots") or [None] * (k + 1))
        sl = sl[k] if k < len(sl) else None
        if isinstance(sl, dict):
            longest = max(longest, float(sl.get("lengthBeats", 16)))
    total_beats = (bars * 4.0) if bars else longest
    total_beats = max(4.0, math.ceil(total_beats / 4.0) * 4.0)

    b = {"version": 2, "bpm": bpm, "lengthBars": total_beats / 4.0,
         "masterGainDb": song.get("masterGainDb", 0.0),
         "master": song.get("master", []), "buses": song.get("buses", []),
         "comment": f"scene bounce: {scenes[k]!r} of {os.path.basename(song_path)}",
         "tracks": []}
    live = 0
    for t in song.get("tracks", []):
        sl = (t.get("slots") or [])
        sl = sl[k] if k < len(sl) else None
        nt = {"name": t.get("name", "t"), "source": t.get("source", {}),
              "gainDb": t.get("gainDb", 0), "pan": t.get("pan", 0),
              "fx": t.get("fx", []), "sends": t.get("sends", []), "notes": []}
        if isinstance(sl, dict) and sl.get("audioFile"):
            loop_beats = float(sl.get("lengthBeats", 16)) or 16.0
            clips, beat = [], 0.0
            while beat < total_beats:
                clips.append({"file": sl["audioFile"], "startBeat": beat,
                              "lengthBeats": min(loop_beats, total_beats - beat),
                              "offsetSec": float(sl.get("offsetSec", 0)),
                              "sourceBpm": float(sl.get("sourceBpm", 0))})
                beat += loop_beats
            nt["audioClips"] = clips
            nt["source"] = {"kind": "audio", "id": nt["name"]}
            live += 1
        elif isinstance(sl, dict) and sl.get("notes"):
            loop_beats = float(sl.get("lengthBeats", 16)) or 16.0
            reps = int(math.ceil(total_beats / loop_beats))
            for r in range(reps):
                for n in sl["notes"]:
                    s = n["start"] + r * loop_beats
                    if s < total_beats:
                        nt["notes"].append({"start": s, "len": n["len"],
                                            "pitch": n["pitch"], "vel": n.get("vel", 0.8)})
            live += 1
        else:
            continue                     # empty cell -> track absent from this scene
        b["tracks"].append(nt)

    base = os.path.splitext(os.path.basename(song_path))[0]
    scratch = os.path.join(ROOT, "songs", f"_scene_{k}_{base}.json")
    json.dump(b, open(scratch, "w"), indent=1)
    out = out or os.path.join(ROOT, "songs", f"_scene_{k}_{base}.wav")
    r = subprocess.run([M1, "render", scratch, out], capture_output=True, text=True)
    ok = "ok=1" in r.stdout + r.stderr
    print(f"[scene_bounce] scene {k} '{scenes[k]}': {live} live tracks, "
          f"{total_beats:.0f} beats -> {out} {'OK' if ok else 'RENDER FAILED'}")
    if not ok:
        print((r.stdout + r.stderr)[-300:])
        sys.exit(1)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("scene")
    ap.add_argument("--bars", type=int, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    bounce(a.song, a.scene, a.bars, a.out)
