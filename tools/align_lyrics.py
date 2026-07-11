#!/usr/bin/env python3
"""align_lyrics.py — auto-melisma: make written lyrics COVER a melody (§7.6a).

sing.py aligns lyrics word->note by beat, and a line's LAST word can ride N extra
notes via "melisma": N (one vowel over a pitch run — real singing). When a topline
has MORE notes than a lyric line has words, those extra notes go UN-SUNG. This sets
each line's melisma so its words cover the melody notes in the line's span — so the
add_topline -> write_lyrics -> sing flow lands with no silent notes and proper melisma.

  align_lyrics.py <song> [--track topline] [--write]

Pure + deterministic (word-count vs notes-in-span; sing.py aligns per space-split
WORD, so melisma = notes - words on the line's last word). Reports lines short of
words (more words than notes) — those can't be covered by melisma alone.
"""
import argparse
import json
import os
import re
import sys
import songname

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def notes_of(song, track):
    for t in song.get("tracks", []):
        if t.get("name") == track:
            return sorted(t.get("notes", []), key=lambda n: float(n["start"]))
    return []


def align(song, track="topline"):
    """Set each lyric line's melisma so its words cover `track`'s notes in span.
    Returns (song, changed, short) — short = lines with more words than notes."""
    lyr = sorted(song.get("lyrics", []), key=lambda l: float(l["beat"]))
    notes = notes_of(song, track)
    if not lyr or not notes:
        return song, 0, 0
    changed, short = 0, 0
    for i, l in enumerate(lyr):
        b0 = float(l["beat"]) - 0.26                       # sing.py's claim window
        b1 = (float(lyr[i + 1]["beat"]) - 0.26) if i + 1 < len(lyr) else 1e18
        span = [n for n in notes if b0 <= float(n["start"]) < b1]
        words = len(str(l.get("text", "")).split())
        if words == 0:
            continue
        mel = max(0, len(span) - words)
        short += (len(span) < words)
        if int(l.get("melisma", 0)) != mel:
            l["melisma"] = mel
            changed += 1
    song["lyrics"] = lyr
    return song, changed, short


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--track", default="topline")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    sp = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(sp))
    song, changed, short = align(song, a.track)
    print(f"[align_lyrics] {changed} lines re-melisma'd to '{a.track}'"
          + (f"; {short} line(s) have MORE words than notes (add notes/words)" if short else ""))
    if a.write:
        json.dump(song, open(sp, "w"), indent=1)
        print(f"[align_lyrics] wrote songs/{name}.json")
    print("ALIGN_JSON " + json.dumps({"changed": changed, "short": short}))


if __name__ == "__main__":
    main()
