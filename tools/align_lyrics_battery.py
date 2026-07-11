#!/usr/bin/env python3
"""align_lyrics_battery.py — auto-melisma (§7.6a) proof.

Asserts align_lyrics sets each line's melisma = (notes in the line's span) -
(words), so the words cover the melody; flags lines with more words than notes;
no-ops safely without a melody. Pure + deterministic. Exit code IS the verdict.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def build():
    notes = [{"start": float(b), "len": 0.9, "pitch": 60 + b % 5, "vel": 0.7}
             for b in range(8)]                      # 8 notes at beats 0..7
    return {"version": 2, "bpm": 120, "key": "C major", "lengthBars": 2,
            "tracks": [{"name": "topline", "source": {"kind": "faust", "id": "pluck"},
                        "notes": notes}],
            "lyrics": [{"beat": 0, "text": "hello world"},        # 2 words, 4 notes -> mel 2
                       {"beat": 4, "text": "one two three"}]}     # 3 words, 4 notes -> mel 1


def main():
    import align_lyrics
    print("== ALIGN_LYRICS BATTERY (auto-melisma) ==")
    fails = 0
    song, changed, short = align_lyrics.align(build(), "topline")
    ly = {float(l["beat"]): l for l in song["lyrics"]}
    m0, m4 = ly[0].get("melisma"), ly[4].get("melisma")
    for beat, txt, got, want in [(0, "hello world", m0, 2), (4, "one two three", m4, 1)]:
        ok = got == want
        fails += not ok
        print(f"  {'OK ' if ok else 'XX '}line@{beat} {txt!r} -> melisma {got} (want {want})")

    # more words than notes -> flagged short, no negative melisma
    song2 = {"version": 2, "bpm": 120, "lengthBars": 1,
             "tracks": [{"name": "topline", "notes": [{"start": 0, "len": 0.9, "pitch": 60, "vel": 0.7}]}],
             "lyrics": [{"beat": 0, "text": "too many words here"}]}
    s2, _, short2 = align_lyrics.align(song2, "topline")
    ok2 = short2 == 1 and s2["lyrics"][0].get("melisma", 0) == 0
    fails += not ok2
    print(f"  {'OK ' if ok2 else 'XX '}more-words-than-notes flagged short={short2}, melisma>=0")

    # no melody -> no-op, no crash
    _, c3, _ = align_lyrics.align({"lyrics": [{"beat": 0, "text": "x"}], "tracks": []}, "topline")
    ok3 = c3 == 0
    fails += not ok3
    print(f"  {'OK ' if ok3 else 'XX '}no-melody no-op (changed={c3})")

    print("PASS" if fails == 0 else f"REGRESSION ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
