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

total = PASS + len(FAIL)
print(f"LYRIC BANK battery: {PASS}/{total} " + ("ALL GREEN" if not FAIL else "RED"))
for m in FAIL:
    print(f"  FAIL {m}")
sys.exit(1 if FAIL else 0)
