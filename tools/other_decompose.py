#!/usr/bin/env python3
"""THE OTHER DECOMPOSITION — heal an existing import's harmonic bucket.

The 'other' stem holds many instruments (usually more than one lead plus
pads/chords — Chezy 2026-07-15), and until today the default import gave it
ONE starved lane (or none: the dereverb corpse, see mel_clean's dry-twin
health law). This CLI re-runs the modern rail on an already-imported song:

    6s microscope (htdemucs_6s, cached in <stems>/6s/)
      -> per-part wet transcription (basic-pitch tuned+salvage)
      -> editable pass -> chord prior -> plausibility court
      -> THE STREAM SPLIT (note_streams: chords/pad/lead when decisive)
      -> per-lane pitched kits (the record's own timbre per stream)
      -> REPLACES the song's old other-family lanes
      -> a2m_correct levels the new lanes against the record's stems

    .venv/bin/python tools/other_decompose.py <song> [--no-correct] [--force]

The base song file is edited IN PLACE with a .predecomp backup; audio stem
lanes are never touched. Refuses while the app runs (live-app stomp law)
unless --force.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SONGS = os.path.join(ROOT, "songs")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("song")
    ap.add_argument("--no-correct", action="store_true",
                    help="skip the a2m_correct level pass")
    ap.add_argument("--force", action="store_true",
                    help="proceed even if the app is running")
    a = ap.parse_args()

    import songname
    name = songname.resolve(a.song)
    path = os.path.join(SONGS, f"{name}.json")
    if not os.path.exists(path):
        sys.exit(f"no such song: {path}")
    stems_dir = os.path.join(SONGS, f"{name}_stems")
    other_wav = os.path.join(stems_dir, "other.wav")
    if not os.path.exists(other_wav):
        sys.exit(f"no other stem: {other_wav} (not an import?)")
    if not a.force:
        try:
            out = subprocess.run(["pgrep", "-x", "sotadaw"],
                                 capture_output=True, text=True)
            if out.stdout.strip():
                sys.exit("the app is RUNNING — an open song would stomp this "
                         "heal on its next save (live-app stomp law). Close "
                         "it or pass --force.")
        except FileNotFoundError:
            pass

    song = json.load(open(path))
    bpm = float(song.get("bpm") or 120.0)
    key = song.get("key")
    import torch  # noqa: F401  CUDA PRELOAD LAW (before basic_pitch)
    import stems_import as si
    import transcribe_stems as ts
    import midi_polish


    # ---- 1. the microscope (idempotent; ~1min GPU on a full song) ----
    stems = {s: os.path.join(stems_dir, f"{s}.wav")
             for s in ("drums", "bass", "other", "vocals")
             if os.path.exists(os.path.join(stems_dir, f"{s}.wav"))}
    parts = []                                  # (part_name, wav, fallback_src)
    try:
        assist = si.six_stem_assist(stems, stems_dir)
    except Exception as e:
        print(f"[decompose] 6s microscope unavailable ({e})", flush=True)
        assist = {}
    for s in ("guitar", "piano"):
        if s in assist and si._stem_audible(assist[s]):
            parts.append((s, assist[s],
                          {"kind": "sample", "kit": "piano"} if s == "piano"
                          else {"kind": "faust", "id": "pluck"}))
    if parts:
        if assist.get("other") and si._stem_audible(assist["other"]):
            parts.append(("other", assist["other"],
                          {"kind": "sample", "kit": "piano"}))
            print(f"[decompose] microscope: "
                  f"{'+'.join(p for p, _, _ in parts[:-1])} + residual other",
                  flush=True)
        else:
            print(f"[decompose] microscope: "
                  f"{'+'.join(p for p, _, _ in parts)} heard, residual ~empty "
                  f"-> fully decomposed", flush=True)
    else:
        parts.append(("other", other_wav, {"kind": "sample", "kit": "piano"}))
        print("[decompose] microscope heard no parts -> single wet rail",
              flush=True)

    # ---- 2. transcribe + polish + THE STREAM SPLIT (shared kernel) ----
    new_tracks, docket = [], []
    for part, wav, fallback in parts:
        notes, rec = ts.other_notes(wav, bpm, key=key)
        print(f"[decompose] {part} rail: {rec}", flush=True)
        if len(notes) < 4:
            print(f"[decompose] {part}: too sparse, no lane", flush=True)
            continue
        n0 = len(notes)
        notes = midi_polish.editable(notes, bpm=bpm)
        print(f"[decompose] editable pass: {part} {n0} -> {len(notes)}",
              flush=True)
        if song.get("chords"):
            c0 = midi_polish.chord_consistency(notes, song["chords"], key=key)
            notes = midi_polish.chord_snap(notes, song["chords"], key=key)
            c1 = midi_polish.chord_consistency(notes, song["chords"], key=key)
            print(f"[decompose] chord prior: {part} weak-note consistency "
                  f"{c0:.0%} -> {c1:.0%}", flush=True)
        new_tracks += si.melodic_lanes(part, wav, notes, fallback, name, bpm)

    if not new_tracks:
        sys.exit("[decompose] nothing transcribed — song left untouched")

    # ---- 3. the court judges ONLY the new lanes (scoped, receipted) ----
    try:
        import import_court
        tmp = {"key": key, "bpm": bpm, "tracks": new_tracks}
        docket = import_court.hold_court(tmp,
                                         courts=("key", "snap", "echo",
                                                 "length"))
        for r in docket:
            print(f"[court] {import_court.fmt(r)}", flush=True)
    except Exception as ce:
        print(f"[decompose] court skipped ({ce})", flush=True)

    # ---- 4. replace the old other-family lanes in place ----
    old = [t for t in song["tracks"] if si._other_family(t.get("name", ""))]
    keep = [t for t in song["tracks"]
            if not si._other_family(t.get("name", ""))]
    at = len(keep)                              # default: append at the end
    if old:                                     # where the family used to live
        first = song["tracks"].index(old[0])    # = kept tracks before it
        at = sum(1 for t in song["tracks"][:first]
                 if not si._other_family(t.get("name", "")))
    else:
        for i, t in enumerate(keep):            # after the 'other' audio ref
            if t.get("name") == "other":
                at = i + 1
                break
    song["tracks"] = keep[:at] + new_tracks + keep[at:]
    shutil.copy2(path, path + ".predecomp")
    json.dump(song, open(path, "w"), indent=1)
    print(f"[decompose] landed {len(new_tracks)} lanes "
          f"({', '.join(t['name'] for t in new_tracks)}) "
          f"replacing {len(old)} -> {os.path.basename(path)} "
          f"(.predecomp backup)", flush=True)
    if docket:
        cj = os.path.join(stems_dir, "court.json")
        try:
            cur = json.load(open(cj)) if os.path.exists(cj) else []
        except Exception:
            cur = []
        json.dump(cur + docket, open(cj, "w"), indent=1)

    # ---- 5. level the new lanes against the record's own stems ----
    if not a.no_correct:
        py = sys.executable
        rc = subprocess.run([py, os.path.join(ROOT, "tools", "a2m_correct.py"),
                             path, "--iters", "2"]).returncode
        if rc != 0:
            print(f"[decompose] a2m_correct exited {rc} — lanes landed at "
                  f"-1.5dB defaults", flush=True)


if __name__ == "__main__":
    main()
