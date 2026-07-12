#!/usr/bin/env python3
"""LYRIC BANK battery — the zero-token words lane's kernel contract.

W130 MAKE SINGS WORDS (2026-07-11, measured: arr+words 0.5899/80.3 beats
arr+hum 0.5741/78.1). sing.py's contract is ONE WORD PER NOTE; the bank
must be byte-deterministic, seed-varied, family-routed, and every word
dict-singable (lowercase alpha — no phoneme guessing).

Usage: python3 tools/lyric_bank_battery.py
"""
import sys
import os

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import lyric_bank as lb

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)


NOTES = [{"start": float(i), "len": 0.5, "pitch": 60 + i, "vel": 0.8}
         for i in range(10)]

a = lb.lyrics_for("psybient", NOTES, 7)
b = lb.lyrics_for("psybient", NOTES, 7)
ok(a == b, "byte-deterministic per (genre, notes, seed)")
ok(len(a) == len(NOTES), "exactly one word per note (sing.py's contract)")
ok([w["beat"] for w in a] == [n["start"] for n in NOTES],
   "beats are the notes' own starts, in order")
c = lb.lyrics_for("psybient", NOTES, 8)
ok(a != c, "a different seed rotates the phrase stream")
ok({w["text"] for w in a} <= set(lb.BANKS["drift"]),
   "psybient words come from the drift bank")

shuffled = list(reversed(NOTES))
d = lb.lyrics_for("psybient", shuffled, 7)
ok(d == a, "note order in the input never changes the output (sorted)")

ok({w["text"] for w in lb.lyrics_for("uk drill", NOTES, 0)} <= set(lb.BANKS["dark"]),
   "drill routes dark (substring membership)")
ok({w["text"] for w in lb.lyrics_for("gospel", NOTES, 0)} <= set(lb.BANKS["warm"]),
   "gospel routes warm")
ok({w["text"] for w in lb.lyrics_for("3step", NOTES, 0)} <= set(lb.BANKS["bright"]),
   "3step routes bright (Chezy's genre)")
ok(lb.bank_for("some_unheard_genre_2031") == lb.BANKS["drift"],
   "unknown genre falls to the MEASURED WINNER (drift)")
ok(lb.bank_for(None) == lb.BANKS["drift"], "None genre never raises")

ok(all(w.isalpha() and w == w.lower()
       for bank in lb.BANKS.values() for w in bank),
   "every bank word is lowercase alpha (dict-singable, no phoneme guessing)")
ok(all(len(bank) >= 16 for bank in lb.BANKS.values()),
   "banks long enough that 8-bar toplines don't loop audibly")

ok(lb.lyrics_for("pop", [], 0) == [], "no notes -> no lyrics (hum fallback fires)")
ok(lb.lyrics_for("pop", None, 0) == [], "None notes -> no lyrics, never raises")
ok(lb.lyrics_for("pop", [{"start": 2.0}, "junk", {"start": 1.0}], 0)[0]["beat"] == 1.0,
   "non-dict notes skipped; earliest beat first")

# THE HOOK LINE LAW (dr20/dr21, 2026-07-12): repeated hook sections REUSE
# the first hook's words (lexical identity); verses keep walking the stream.
_SECS = [{"name": "verse", "startBar": 0}, {"name": "chorus", "startBar": 2},
         {"name": "verse2", "startBar": 4}, {"name": "chorus2", "startBar": 6}]
_NS = [{"start": float(b)} for b in
       (0, 1, 2, 3, 8, 9, 10, 11, 16, 17, 18, 19, 24, 25, 26, 27)]
_W = [x["text"] for x in lb.lyrics_for("pop", _NS, 7, sections=_SECS)]
ok(_W[4:8] == _W[12:16], "HOOK LAW: chorus2 sings the chorus's words")
ok(_W[0:4] != _W[8:12], "STORY LAW: verse2 walks on (new words)")
ok(lb.lyrics_for("pop", _NS, 7, sections=_SECS)
   == lb.lyrics_for("pop", _NS, 7, sections=_SECS),
   "sectioned lyrics deterministic")
ok(len(lb.lyrics_for("pop", _NS, 7)) == 16
   and [x["text"] for x in lb.lyrics_for("pop", _NS, 7)][0:4] != [None] * 4,
   "sections=None keeps the legacy path")
_DBL = sorted(_NS[4:8] + [{"start": 8.0}], key=lambda n: n["start"])
_L2 = lb.lyrics_for("pop", _DBL, 7, sections=[{"name": "chorus", "startBar": 2}])
_SB = [x["text"] for x in _L2 if x["beat"] == 8.0]
ok(len(_SB) == 2 and _SB[0] == _SB[1],
   "octave double shares ONE word (never two words at once)")

total = PASS + len(FAIL)
print(f"LYRIC BANK battery: {PASS}/{total} " + ("ALL GREEN" if not FAIL else "RED"))
for m in FAIL:
    print(f"  FAIL {m}")
sys.exit(1 if FAIL else 0)
