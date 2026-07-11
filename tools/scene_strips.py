#!/usr/bin/env python3
"""scene_strips.py — add PERFORMANCE STRIP scenes to any sceneful song.

  scene_strips.py <song.json> [--from-scene 0]

Takes one source scene (default: the fullest column) and appends the live-remix
staples as new scene columns:
  "Drums only"  — just the rhythm section (breakdown)
  "No drums"    — everything but drums (the acapella/musical moment)
  "Bass+Drums"  — the groove skeleton (DJ tool)
Track class comes from its NAME first (drums/kick/snare/hat/perc/bass/vocal...),
falling back to the sound tensor for unnamed audio slots. Non-destructive: only
appends scenes+cells; existing columns untouched. Verify with scene_bounce.
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

DRUM_WORDS = ("drum", "kick", "snare", "hat", "perc", "clap", "rim", "shaker", "cymbal", "tom", "808",
              "ride", "ghost", "crash", "conga", "bongo", "cowbell", "tamb", "clave", "cuica",
              "timbale", "agogo", "woodblock", "cabasa", "guiro", "triangle", "castanet")
BASS_WORDS = ("bass", "sub", "808")
VOX_WORDS = ("vocal", "vox", "voice", "lead vox", "acapella")


def classify_track(t):
    name = str(t.get("name", "")).lower()
    if any(w in name for w in DRUM_WORDS):
        return "drums"
    if any(w in name for w in BASS_WORDS):
        return "bass"
    if any(w in name for w in VOX_WORDS):
        return "vox"
    # audio slot fallback: the sound tensor
    for sl in t.get("slots", []) or []:
        if isinstance(sl, dict) and sl.get("audioFile"):
            try:
                from loop_machine import classify
                f = sl["audioFile"]
                if not os.path.isabs(f):
                    f = os.path.join(ROOT, f)
                c = classify(f)
                return {"perc": "drums", "melodic": "other", "fx": "other"}.get(c, c)
            except Exception:
                break
    return "other"


STRIPS = [("Drums only", lambda c: c == "drums"),
          ("No drums", lambda c: c != "drums"),
          ("Bass+Drums", lambda c: c in ("drums", "bass"))]


def add_strips(song_path, from_scene=None):
    song = json.load(open(song_path))
    scenes = song.get("scenes", [])
    if not scenes:
        raise SystemExit("song has no scenes — nothing to strip")
    if from_scene is None:
        # fullest column = most present cells
        counts = []
        for k in range(len(scenes)):
            n = sum(1 for t in song["tracks"]
                    if k < len(t.get("slots", []) or []) and isinstance((t.get("slots") or [])[k], dict))
            counts.append(n)
        from_scene = counts.index(max(counts))
    src_name = scenes[from_scene].get("name", str(from_scene))

    classes = {t.get("name", ""): classify_track(t) for t in song["tracks"]}
    added = []
    for label, keep in STRIPS:
        if any(label == s.get("name") for s in scenes):
            continue                                   # idempotent
        scenes.append({"name": label})
        col = len(scenes) - 1
        live = 0
        for t in song["tracks"]:
            sl = t.get("slots")
            if sl is None:
                sl = t["slots"] = []
            while len(sl) < col:
                sl.append(None)
            src = sl[from_scene] if from_scene < len(sl) else None
            if isinstance(src, dict) and keep(classes[t.get("name", "")]):
                cell = dict(src)
                cell["name"] = f"{t.get('name','t')} {label}"
                sl.append(cell); live += 1
            else:
                sl.append(None)
        added.append(f"{label} ({live} tracks)")
    song["scenes"] = scenes
    json.dump(song, open(song_path, "w"), indent=1)
    print(f"[strips] {os.path.basename(song_path)}: from '{src_name}' -> " + ", ".join(added))
    print("[strips] classes: " + ", ".join(f"{k}={v}" for k, v in classes.items()))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--from-scene", type=int, default=None)
    a = ap.parse_args()
    add_strips(a.song, a.from_scene)
