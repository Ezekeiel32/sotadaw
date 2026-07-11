#!/usr/bin/env python3
"""RESTYLE — keep the MUSIC, swap the GENRE's palette + feel (Tier-3 #7, v1).

  restyle.py <song> <genre> [--bpm] [--write]

The one-gesture style morph: every note stays byte-identical; what changes is
the SOUND (role-mapped voices from the target genre's KG DNA) and the FEEL
(the genre's swing; --bpm also moves tempo into the genre's range — safe, all
timing is in beats). Mapping mirrors loop_gen's birth rules so a restyled song
sounds like the genre's MAKE would:
  kick   -> kick_808 when the genre slides (trap-family) else kick_punch
  bass   -> the genre's bass_style voice (offbeat=sub_clean, sustained=reese…)
  lead   -> the genre grid's lead voice
  pads/chords/keys/color -> the genre's recipe color voice (dna.voice)
  snare/hat/clap/perc    -> kept (genre-neutral lanes in our DNA)
HONEST SCOPE: only faust sources morph; vst3/preset/sample/audio tracks keep
their identity (a preset IS a sound choice — swapping it blind would lie);
locked tracks untouched. Graph-less machines use agent/dna_cache.json.
"""
import argparse, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import is_drum_track
from automix import role
import songname

BASS_VOICE = {"offbeat": "sub_clean", "roots": "bass_warm", "sliding": "kick_808",
              "walking": "bass_warm", "psy_rolling": "sub_clean",
              "sustained": "reese", "log": "log_drum"}
NEUTRAL_COLOR = "warmpad"          # when the recipe voice is a drum (amapiano log_drum)


def genre_dna(genre):
    try:
        from loop_gen import genre_dna as gd     # live graph first, cache inside
        dna, err = gd(genre)
        if dna:
            return dna
    except Exception:
        pass
    cache = json.load(open(os.path.join(ROOT, "agent", "dna_cache.json")))["genres"]
    if genre not in cache:
        raise SystemExit(f"unknown genre '{genre}' — have {len(cache)}: "
                         + ", ".join(sorted(cache)[:12]) + "…")
    return cache[genre]


def restyle(song, genre, retempo=False):
    dna = genre_dna(genre)
    grid = dna.get("grid") or {}
    kick_v = "kick_808" if grid.get("bass_style") == "sliding" else "kick_punch"
    bass_v = BASS_VOICE.get(grid.get("bass_style", "roots"), "bass_warm")
    lead_v = (grid.get("lead") or {}).get("voice") or "pluck2"
    color_v = dna.get("voice") or NEUTRAL_COLOR
    if color_v in ("kick_808", "log_drum"):
        color_v = NEUTRAL_COLOR
    rep = {"genre": genre, "tracks": {}, "skipped": {}, "feel": {}}
    for t in song.get("tracks", []):
        nm = t.get("name", "?")
        if t.get("locked"):
            rep["skipped"][nm] = "locked"
            continue
        src = t.get("source") or {}
        if src.get("kind") != "faust" or not src.get("id"):
            rep["skipped"][nm] = f"{src.get('kind', '?')}: keeps its identity (only faust voices morph)"
            continue
        old = src["id"]
        r = role(t)
        low = nm.lower()
        if r == "kick" or "kick" in low or "808" in low:
            new = kick_v
        elif r == "bass" or "bass" in low or "sub" in low or "reese" in low:
            new = bass_v
        elif is_drum_track(t):
            rep["skipped"][nm] = "genre-neutral drum lane (kept)"
            continue
        elif r in ("pad",) or any(k in low for k in ("pad", "chord", "keys", "color", "string", "organ")):
            new = color_v
        else:                                    # focal / lead / pluck / melodic rest
            new = lead_v
        if new != old:
            src["id"] = new
            rep["tracks"][nm] = f"{old} -> {new}"
    sw = grid.get("swing")
    if isinstance(sw, (int, float)) and sw > 0.5:
        song["swing"] = {"grid": "16th", "amount": round(float(sw), 3)}
        rep["feel"]["swing"] = song["swing"]
    elif song.get("swing"):
        song.pop("swing", None)
        rep["feel"]["swing"] = "removed (target genre is straight)"
    if retempo and dna.get("bpm_lo") and dna.get("bpm_hi"):
        old_bpm = song.get("bpm")
        song["bpm"] = int(round((float(dna["bpm_lo"]) + float(dna["bpm_hi"])) / 2))
        rep["feel"]["bpm"] = f"{old_bpm} -> {song['bpm']}"
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("genre")
    ap.add_argument("--bpm", action="store_true", help="move tempo into the genre's range")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    path = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(path))
    rep = restyle(song, re.sub(r"[^a-z0-9_]", "", a.genre.lower()), retempo=a.bpm)
    if a.write:
        json.dump(song, open(path, "w"), indent=1)
    for nm, ch in rep["tracks"].items():
        print(f"[restyle] {nm}: {ch}")
    for k, v in rep["feel"].items():
        print(f"[restyle] feel.{k}: {v}")
    for nm, why in rep["skipped"].items():
        print(f"[restyle] {nm}: kept — {why}")
    print("RESTYLE_JSON " + json.dumps(rep))


if __name__ == "__main__":
    main()
