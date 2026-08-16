#!/usr/bin/env python3
"""THE RECORD COURT (A4-T1, docs/SPEC_TRANSCENDENCE.md) — the unit of
creation grows from the song to THE RECORD: an ordered body of tracks judged
as ONE work. Render-free, symbolic, advisory (a record is taste; the court
informs the sequence, it never rewrites a song).

KERNELS (all pure, all from song.json):
  key_journey — circle-of-fifths distance between consecutive tracks;
                relative/parallel/adjacent = smooth, a cold jump flags
  tempo_arc   — the bpm journey classified (rise/fall/wave/flat); adjacent
                whiplash flags UNLESS the hop is a musical ratio (halftime/
                double/dotted) — the DJ lane's own law at album scale
  thread      — motif recurrence ACROSS tracks (shared interval 4-grams
                between lead lanes): a record with a thread is a BODY of
                work; absence is reported honestly, never punished hard
  pacing      — running lengths; two adjacent marathon tracks advise

THE MANIFEST: songs/.records/<name>.json {"name": ..., "songs": [names]}
(gitignored beside the artist dir — a record is the user's own object).

CLI:  record_court.py <song.json> <song.json> ...   (order = the sequence)
      record_court.py --manifest songs/.records/<name>.json
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_PC = {"c": 0, "c#": 1, "db": 1, "d": 2, "d#": 3, "eb": 3, "e": 4, "f": 5,
       "f#": 6, "gb": 6, "g": 7, "g#": 8, "ab": 8, "a": 9, "a#": 10,
       "bb": 10, "b": 11}
# circle-of-fifths position per pitch class (C=0, G=1, ... F=11)
_FIFTH_POS = {pc: (pc * 7) % 12 for pc in range(12)}


def parse_key(s):
    """'A minor'/'F# major'/'Bb m'/'F#m'/'C' -> (pc, minor?) or None.
    Anchored whole-string: 'garbage' must never parse as G."""
    m = re.match(r"^\s*([a-g][#b]?)\s*(m|min|minor|maj|major)?\s*$",
                 str(s or "").lower())
    if not m or m.group(1) not in _PC:
        return None
    return _PC[m.group(1)], m.group(2) in ("m", "min", "minor")


def key_distance(a, b):
    """Producer-shaped distance between keys: 0 same, 0.5 relative/parallel,
    else circle-of-fifths steps between the keys' MAJOR homes (minor folds
    onto its relative major — the Camelot idea without the branding)."""
    if a is None or b is None:
        return None
    (pa, ma), (pb, mb) = a, b
    if (pa, ma) == (pb, mb):
        return 0.0
    if ma != mb and (pb - pa) % 12 == (3 if ma and not mb else
                                       9 if not ma and mb else 99):
        return 0.5                     # relative major/minor
    if pa == pb and ma != mb:
        return 0.5                     # parallel
    ha = (pa + 3) % 12 if ma else pa   # minor's relative-major home
    hb = (pb + 3) % 12 if mb else pb
    d = abs(_FIFTH_POS[ha] - _FIFTH_POS[hb])
    return float(min(d, 12 - d))


def court_key_journey(docs, names):
    hops, flags = [], []
    keys = [parse_key(d.get("key")) for d in docs]
    for i in range(len(docs) - 1):
        d = key_distance(keys[i], keys[i + 1])
        hops.append({"from": names[i], "to": names[i + 1],
                     "keys": [str(docs[i].get("key", "?")),
                              str(docs[i + 1].get("key", "?"))],
                     "distance": d})
        if d is not None and d > 2:
            flags.append(f"{names[i]} -> {names[i + 1]}: cold key jump "
                         f"({docs[i].get('key')} -> {docs[i + 1].get('key')}, "
                         f"{d:g} fifths) — consider a bridge track or a "
                         "re-key")
    return {"ok": not flags, "hops": hops, "flags": flags}


_RATIOS = (0.5, 2.0, 2 / 3, 3 / 2, 0.75, 4 / 3)


def court_tempo_arc(docs, names):
    bpms = [float(d.get("bpm") or 0) for d in docs]
    flags = []
    for i in range(len(bpms) - 1):
        a, b = bpms[i], bpms[i + 1]
        if a <= 0 or b <= 0:
            continue
        drift = abs(b - a) / a
        ratio_ok = any(abs(b / a - r) < 0.02 for r in _RATIOS)
        if drift > 0.25 and not ratio_ok:
            flags.append(f"{names[i]} -> {names[i + 1]}: tempo whiplash "
                         f"({a:g} -> {b:g}, {drift:.0%}) with no musical "
                         "ratio — a halftime/double hop or a bridge reads "
                         "as intent; this reads as a skip")
    if len([b for b in bpms if b > 0]) >= 3:
        rise = sum(1 for i in range(len(bpms) - 1) if bpms[i + 1] > bpms[i])
        fall = sum(1 for i in range(len(bpms) - 1) if bpms[i + 1] < bpms[i])
        shape = ("flat" if rise == 0 and fall == 0 else
                 "rise" if fall == 0 else "fall" if rise == 0 else "wave")
    else:
        shape = "short"
    return {"ok": not flags, "bpms": bpms, "shape": shape, "flags": flags}


def _lead_intervals(doc):
    """The record's melodic voice per song: lead-class lane else the densest
    pitched non-drum lane -> interval sequence."""
    best, best_notes = None, []
    for t in doc.get("tracks") or []:
        nm = str(t.get("name", "")).lower()
        notes = t.get("notes") or []
        if not notes or any(w in nm for w in ("kick", "snare", "hat", "perc",
                                              "clap", "drum", "cym")):
            continue
        if any(w in nm for w in ("lead", "hook", "melody", "top")):
            best, best_notes = nm, notes
            break
        if len(notes) > len(best_notes):
            best, best_notes = nm, notes
    seq = [int(n.get("pitch", 0)) for n in
           sorted(best_notes, key=lambda n: float(n.get("start", 0)))]
    return [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]


def _grams(iv, n=4):
    out = set()
    for i in range(len(iv) - n + 1):
        g = tuple(iv[i:i + n])
        if any(g):                     # all-zero = a held/repeated note, not a motif
            out.add(g)
    return out


def court_thread(docs, names):
    grams = [_grams(_lead_intervals(d)) for d in docs]
    shared, pairs = set(), []
    for i in range(len(docs)):
        for j in range(i + 1, len(docs)):
            common = grams[i] & grams[j]
            if len(common) >= 2:
                pairs.append({"a": names[i], "b": names[j],
                              "shared_motifs": len(common)})
                shared |= common
    has = bool(pairs)
    return {"ok": True, "has_thread": has, "pairs": pairs,
            "note": (f"the record carries a thread — {len(shared)} interval "
                     f"motifs recur across {len(pairs)} track pair(s)" if has
                     else "no melodic motif recurs across tracks — a "
                     "reprise/interlude quoting the strongest hook would "
                     "bind the record (advisory, absence is a style too)")}


def court_pacing(docs, names):
    mins, flags = [], []
    for d in docs:
        bpm = float(d.get("bpm") or 120)
        bars = float(d.get("lengthBars") or 0)
        mins.append(bars * 4 * 60 / bpm / 60 if bpm > 0 else 0)
    for i in range(len(mins) - 1):
        if mins[i] > 6 and mins[i + 1] > 6:
            flags.append(f"{names[i]} + {names[i + 1]}: back-to-back "
                         f"marathons ({mins[i]:.1f}m, {mins[i + 1]:.1f}m) — "
                         "sequencing a breather between them keeps the ear")
    return {"ok": not flags, "minutes": [round(m, 2) for m in mins],
            "flags": flags}


def court_record(docs, names=None):
    names = names or [f"track{i + 1}" for i in range(len(docs))]
    if len(docs) < 2:
        return {"skipped": "a record needs >=2 tracks"}
    out = {"key_journey": court_key_journey(docs, names),
           "tempo_arc": court_tempo_arc(docs, names),
           "thread": court_thread(docs, names),
           "pacing": court_pacing(docs, names)}
    out["ok"] = all(v.get("ok", True) for v in out.values()
                    if isinstance(v, dict))
    return out


def _load(path):
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(0)
    if a[0] == "--manifest":
        man = _load(a[1])
        names = man.get("songs") or []
        paths = [os.path.join(ROOT, "songs", f"{n}.json") for n in names]
    else:
        paths = a
        names = [os.path.splitext(os.path.basename(p))[0] for p in paths]
    docs = [_load(p) for p in paths]
    print(json.dumps(court_record(docs, names), indent=1))
