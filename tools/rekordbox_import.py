#!/usr/bin/env python3
"""rekordbox_import.py — THE PRO-DJ BRIDGE: rekordbox collection.xml -> deck lists.

  rekordbox_import.py collection.xml                    # index every local track
  rekordbox_import.py collection.xml --playlist "peak"  # one playlist, in order
  rekordbox_import.py collection.xml --playlist "peak" --set-name friday

Rekordbox's analysis is AUTHORITATIVE: AverageBpm/TEMPO Bpm, Tonality (musical
"Am"/"F#m" or Camelot "08A" — both handled), and TEMPO Inizio = the first-beat
offset (real files start with silence/pickups; our grid needs the downbeat).
Tracks are merged into library.json under "dj_tracks" and a ready-to-run
dj_set command is printed (bpm/key/offset passed through — no re-detection).
"""
import argparse, json, os, sys, urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dj_mix import NOTE_PC
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tonality_to_camelot(t):
    """'Am'/'F#m'/'Bb' musical or '08A'/'12B' Camelot -> canonical Camelot."""
    if not t:
        return None
    t = t.strip()
    if len(t) >= 2 and t[-1] in "ABab" and t[:-1].isdigit():
        num = int(t[:-1])
        return f"{num}{t[-1].upper()}" if 1 <= num <= 12 else None
    minor = t.endswith("m")
    note = t[:-1] if minor else t
    pc = NOTE_PC.get(note)
    if pc is None:
        return None
    base = (pc - 9) * 7 if minor else pc * 7
    num = (base % 12 + 8 - 1) % 12 + 1
    return f"{num}{'A' if minor else 'B'}"


def location_to_path(loc):
    """file://localhost/URL-encoded-path -> filesystem path."""
    if not loc:
        return None
    p = urllib.parse.urlparse(loc)
    return urllib.parse.unquote(p.path) or None


def parse_collection(xml_path):
    root = ET.parse(xml_path).getroot()
    tracks = {}                               # TrackID -> entry
    for t in root.iter("TRACK"):
        if t.get("Location") is None:         # playlist refs are also <TRACK>
            continue
        path = location_to_path(t.get("Location"))
        bpm = float(t.get("AverageBpm") or 0) or None
        off = 0.0
        tempo = t.find("TEMPO")
        if tempo is not None:
            bpm = float(tempo.get("Bpm") or bpm or 0) or bpm
            off = float(tempo.get("Inizio") or 0)
        tracks[t.get("TrackID")] = {
            "path": path, "name": t.get("Name") or os.path.basename(path or "?"),
            "artist": t.get("Artist") or "", "bpm": bpm,
            "key": t.get("Tonality") or None,
            "camelot": tonality_to_camelot(t.get("Tonality")),
            "offset_sec": off,
            "cues": len(t.findall("POSITION_MARK")),
        }
    playlists = {}                            # name -> [TrackID...]
    for node in root.iter("NODE"):
        if node.get("Type") == "1":
            playlists[node.get("Name")] = [r.get("Key") for r in node.findall("TRACK")]
    return tracks, playlists


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xml")
    ap.add_argument("--playlist", default=None)
    ap.add_argument("--set-name", default="rekordbox_set")
    a = ap.parse_args()
    tracks, playlists = parse_collection(a.xml)
    if a.playlist is not None:
        ids = playlists.get(a.playlist)
        if ids is None:
            print(f"no playlist '{a.playlist}'. available: {sorted(playlists)}")
            sys.exit(1)
        chosen = [tracks[i] for i in ids if i in tracks]
    else:
        chosen = list(tracks.values())
    local = [t for t in chosen if t["path"] and os.path.exists(t["path"])]
    missing = [t for t in chosen if t not in local]
    for m in missing:
        print(f"[rekordbox] SKIP (file not found here): {m['name']} -> {m['path']}")

    # merge into library.json (additive: only the dj_tracks key is touched)
    lib_path = os.path.join(ROOT, "library.json")
    lib = json.load(open(lib_path)) if os.path.exists(lib_path) else {}
    known = {t["path"] for t in lib.get("dj_tracks", [])}
    lib.setdefault("dj_tracks", []).extend(t for t in local if t["path"] not in known)
    json.dump(lib, open(lib_path, "w"), indent=1)

    print(f"[rekordbox] {len(local)} local tracks ({len(missing)} skipped); "
          f"library.json dj_tracks = {len(lib['dj_tracks'])}")
    for t in local:
        print(f"  {t['bpm'] or '?':>6} bpm  {t['camelot'] or '??':>3}  "
              f"+{t['offset_sec']:.3f}s  {t['artist']} - {t['name']}")
    if len(local) >= 2:
        paths = " ".join(f'"{t["path"]}"' for t in local)
        bpms = ",".join(f"{t['bpm']:.2f}" if t["bpm"] else "0" for t in local)
        offs = ",".join(f"{t['offset_sec']:.3f}" for t in local)
        keys = ",".join(t["camelot"] or "-" for t in local)
        print(f"\n[rekordbox] ready:\n.venv/bin/python tools/dj_set.py {a.set_name} "
              f"{paths} --bpms {bpms} --offsets {offs} --keys {keys} --auto-order")


if __name__ == "__main__":
    main()
