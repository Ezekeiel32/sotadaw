#!/usr/bin/env python3
"""loop_machine.py — #33: any pile of loops -> a PLAYABLE loop machine (task board).

  loop_machine.py build <name> loop1.wav loop2.wav ... [--bpm N] [--preview]

Connects the existing pieces: audio slots (launcher), warp (sourceBpm), MIDI
hands (pads already launch scenes). Each loop becomes a track; hear.py's sound
tensor CLASSIFIES it (drums / bass / melodic / perc by band placement + onset
density); scenes are the live-set build: Drums -> +Bass -> +Keys -> FULL.
Slots warp to one master grid, so pads stay beat-locked at any tempo.

--preview also lays the FULL scene onto the timeline (bars 1-8) so the machine
is renderable/verifiable headless (launcher playback isn't exercised by
renderToFile — the known engine limitation)."""
import argparse, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hear import sound_tensor
from stems_import import estimate_bpm
from dj_mix import wav_seconds
import numpy as np

SCENES = ["Drums", "+Bass", "+Keys", "FULL"]
# which classes enter at which scene (index = scene)
ENTRY = {"drums": 0, "perc": 0, "bass": 1, "melodic": 2, "fx": 3}


def classify(wav):
    """Class from the sound tensor — boundaries CALIBRATED on known renders
    (7/7: sub/tal-bass->bass, hats->perc, tal-pad->melodic, 3 real beat loops->
    drums). The musical insight: a DRUM loop is defined by its top-end pulse
    (hats present: top4 > 1%%); pure bass has zero top; melodic material is
    harmonically WIDE (>=5 active rows); else it's a bassline."""
    t = sound_tensor(wav, rows=14, cols=48)
    g = np.array(t["grid"], dtype=float)
    rowsum = g.sum(axis=1)
    top4 = float(rowsum[-4:].sum() / (rowsum.sum() + 1e-9))
    active = int((rowsum > rowsum.max() * 0.3).sum())
    if top4 >= 0.5:
        return "perc"
    if top4 > 0.01:
        return "drums"
    if active >= 5:
        return "melodic"
    return "bass"


def build(name, paths, bpm=None, preview=False):
    paths = [os.path.abspath(p) for p in paths]
    infos = []
    for p in paths:
        b, conf = estimate_bpm(p)
        cls = classify(p)
        infos.append({"path": p, "bpm": round(b, 2), "conf": round(conf, 2), "cls": cls})
    master = bpm or infos[0]["bpm"]
    rel = lambda p: os.path.relpath(p, ROOT) if p.startswith(ROOT) else p

    tracks = []
    counts = {}
    for inf in infos:
        cls = inf["cls"]
        counts[cls] = counts.get(cls, 0) + 1
        tname = cls if counts[cls] == 1 else f"{cls}{counts[cls]}"
        entry = ENTRY.get(cls, 3)
        slots = []
        for s in range(len(SCENES)):
            if s >= entry:
                beats = max(4.0, round(wav_seconds(inf["path"]) * inf["bpm"] / 60.0 / 4.0) * 4.0)
                slots.append({"name": f"{tname} {SCENES[s]}", "lengthBeats": beats,
                              "audioFile": rel(inf["path"]),
                              "offsetSec": 0.0, "sourceBpm": inf["bpm"],
                              **({"follow": "next"} if s < len(SCENES) - 1 else {})})
            else:
                slots.append(None)      # empty cell before this class enters
        # schema: slots list w/ nulls = empty cells (loader skips non-dict entries)
        tracks.append({"name": tname, "source": {"kind": "audio", "id": tname},
                       "gainDb": 0, "notes": [],
                       "slots": [s for s in slots if s] if all(slots) else slots,
                       "audioClips": []})
    song = {"version": 2, "bpm": master, "lengthBars": 8, "masterGainDb": 0.0,
            "master": [{"id": "fx_brickwall", "params": {"ceiling": -1.2}}],
            "scenes": [{"name": n} for n in SCENES], "tracks": tracks}
    if preview:                          # FULL scene on the timeline = renderable proof
        for t in song["tracks"]:
            src = next((s for s in t["slots"] if isinstance(s, dict)), None)
            if src:
                t["audioClips"] = [{"file": src["audioFile"], "startBeat": 0.0,
                                    "lengthBeats": 32.0, "sourceBpm": src["sourceBpm"]}]
    out = os.path.join(ROOT, "songs", f"{name}.json")
    json.dump(song, open(out, "w"), indent=1)
    plan = " | ".join(f"{i['cls']}:{os.path.basename(i['path'])}@{i['bpm']}" for i in infos)
    print(f"[loop_machine] {out} @ {master}bpm — {len(tracks)} pads x {len(SCENES)} scenes")
    print(f"[loop_machine] {plan}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build"])
    ap.add_argument("name")
    ap.add_argument("loops", nargs="+")
    ap.add_argument("--bpm", type=float, default=None)
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    build(a.name, a.loops, a.bpm, a.preview)
