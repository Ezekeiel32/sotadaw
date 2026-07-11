#!/usr/bin/env python3
"""LOOP INFILLING — "keep the fragments you like, regenerate the rest."

loop_infill.py <loop_song> <part> [--seed N] [--genre g] [--no-render]

The co-creation contract (Beyond-SOTA #3, the FL-beating move):
  - <part> = drums | bass | lead | color | <exact track name>
  - ONLY that part's NOTES are rerolled from the genre's KG DNA (new seed);
    every other track stays byte-identical.
  - Your MIX SURVIVES the reroll: the infilled track keeps ITS OWN gainDb/pan/fx —
    only the notes are new.
  - LOCKED tracks are never infilled (edit-lock law applies to generators too).
Genre comes from the loop's own _loop provenance (loop_gen stamps it) or --genre.
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import loop_gen  # noqa: E402

M1 = os.path.join(ROOT, "app/build/m1_artefacts/Release/m1")
DRUM_LANES = set(loop_gen.LANES.keys())
GROUPS = {"drums": DRUM_LANES, "bass": {"bass"}, "lead": {"lead"}, "color": {"color"}}


def infill(song_path, part, seed, genre=None, render=True):
    song = json.load(open(song_path))
    meta = song.get("_loop") or {}
    genre = genre or meta.get("genre")
    if not genre:
        return None, "no _loop provenance in this song — pass --genre (older loops predate the stamp)"
    group = GROUPS.get(part) or {part}
    have = {t.get("name") for t in song.get("tracks", [])}
    if not (group & have) and part not in GROUPS:
        return None, f"no track '{part}' here (tracks: {', '.join(sorted(have))})"

    donor_out, err = loop_gen.generate(genre, "_infill_donor", bars=int(song.get("lengthBars", 4)),
                                       seed=seed, bpm=song.get("bpm"), key=song.get("key"))
    if donor_out is None:
        return None, f"donor generation failed: {err}"
    donor_path = donor_out if isinstance(donor_out, str) and donor_out.endswith(".json") \
        else os.path.join(ROOT, "songs", "_infill_donor.json")
    donor = donor_out if isinstance(donor_out, dict) else json.load(open(donor_path))
    try:
        os.path.exists(donor_path) and os.remove(donor_path)
    except OSError:
        pass
    donor_tracks = {t["name"]: t for t in donor.get("tracks", [])}

    changed, kept_locked, cleared = [], [], []
    out_tracks = []
    for t in song.get("tracks", []):
        nm = t.get("name")
        if nm not in group:
            out_tracks.append(t)                     # untouched, byte-identical
            continue
        if t.get("locked"):
            kept_locked.append(nm)
            out_tracks.append(t)                     # the lock outranks the reroll
            continue
        d = donor_tracks.get(nm)
        if d is None:                                # reroll dropped this lane (prob-gated)
            t2 = dict(t, notes=[])
            cleared.append(nm)
            out_tracks.append(t2)
            continue
        t2 = dict(t)                                 # YOUR mix survives: gain/pan/fx/params stay
        t2["notes"] = d["notes"]                     # the NOTES are the reroll
        changed.append(nm)
        out_tracks.append(t2)
    for nm, d in donor_tracks.items():               # reroll introduced a lane we didn't have
        if nm in group and nm not in have:
            out_tracks.append(d)
            changed.append(nm + " (new)")
    if not changed and not cleared:
        return None, (f"nothing infilled: part '{part}' is fully locked" if kept_locked
                      else f"donor produced nothing for part '{part}'")

    song["tracks"] = out_tracks
    song.setdefault("_loop", {})["last_infill"] = {"part": part, "seed": seed}
    json.dump(song, open(song_path, "w"), indent=1)
    msg = (f"infilled '{part}' (seed {seed}): notes rerolled on " + ", ".join(changed)
           + (f"; cleared: {', '.join(cleared)}" if cleared else "")
           + (f"; LOCK HELD on: {', '.join(kept_locked)}" if kept_locked else "")
           + " — gains/pans/fx untouched, every other track byte-identical")
    if render:
        wav = song_path[:-5] + ".wav"
        r = subprocess.run([M1, "render", song_path, wav], capture_output=True, text=True)
        msg += " | render " + ("OK" if "ok=1" in r.stdout + r.stderr else "FAILED")
    return {"changed": changed, "cleared": cleared, "locked": kept_locked}, msg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("part")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--genre")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    p = a.song if a.song.endswith(".json") else os.path.join(ROOT, "songs", f"{a.song}.json")
    if not os.path.exists(p):
        sys.exit(f"no such song: {p}")
    res, msg = infill(p, a.part, a.seed, a.genre, render=not a.no_render)
    print(msg)
    if res is None:
        sys.exit(2)


if __name__ == "__main__":
    main()
