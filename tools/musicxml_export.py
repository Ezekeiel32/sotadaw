#!/usr/bin/env python3
"""song.json -> MusicXML (score-partwise) — THE SCORE tab's "download as notes" rail.

Mirrors app/ScoreEngrave.h law in miniature: display quantize (1/16 + per-beat
triplet election), metric-tree rhythm spelling with ties (den-4 syncopation
whitelist), key-signature pitch spelling, Weinberg drum mapping as unpitched
percussion with x noteheads, meterMap-aware measures. Output opens in
MuseScore/Dorico/Sibelius/Finale/Flat.

Usage: musicxml_export.py <song.json> <out.musicxml>
"""
import json
import math
import sys
from xml.sax.saxutils import escape

EPS = 1e-6
DIV = 480  # divisions per quarter

MELODIC_VETO = ("vox", "vocal", "voice", "choir", "lead", "bass", "pad", "key",
                "pluck", "chord", "arp", "piano", "organ", "guitar", "string",
                "brass", "flute", "bell", "sax", "synth", "melody", "sketch")
DRUM_ROLES = [  # (needle, staff-step on treble mapping, x-head)
    ("openhat", 9, "circle-x"), ("open_hat", 9, "circle-x"),
    ("kick", 1, None), ("bd_", 1, None), ("snare", 5, None), ("rim", 5, None),
    ("clap", 5, "x"), ("hat", 9, "x"), ("hh", 9, "x"), ("ride", 8, "x"),
    ("crash", 11, "x"), ("cym", 11, "x"), ("china", 11, "x"), ("splash", 11, "x"),
    ("floor", 3, None), ("tom", 6, None), ("shaker", 9, "x"), ("tamb", 9, "x"),
    ("guira", 9, "x"), ("cabasa", 9, "x"), ("maraca", 9, "x"), ("noise", 9, "x"),
    ("conga", 6, None), ("bongo", 6, None), ("darbuka", 6, None), ("dhol", 6, None),
    ("tabla", 6, None), ("djembe", 6, None), ("timbale", 6, None), ("block", 7, "x"),
    ("cowbell", 7, "x"), ("perc", 6, None), ("drum", 6, None),
]
NAT_PC = [0, 2, 4, 5, 7, 9, 11]
LETTERS = "CDEFGAB"


def drum_role(track):
    hay = (track.get("name", "") + " " + track.get("source", {}).get("id", "")).lower()
    if any(w in hay for w in MELODIC_VETO):
        return None
    for needle, step, head in DRUM_ROLES:
        if needle in hay:
            return (step, head)
    return None


def parse_key(key):
    s = (key or "").strip()
    if not s or s[0].upper() not in "ABCDEFG":
        return 0, False
    letter = {"A": 5, "B": 6, "C": 0, "D": 1, "E": 2, "F": 3, "G": 4}[s[0].upper()]
    i, alter = 1, 0
    while i < len(s) and s[i] in "#b":
        alter += 1 if s[i] == "#" else -1
        i += 1
    rest = s[i:].strip().lower()
    minor = rest.startswith("min") or rest == "m" or rest.startswith("m ") or \
        rest.startswith("aeol") or rest.startswith("dor")
    base = [0, 2, 4, -1, 1, 3, 5][letter]
    return max(-7, min(7, base + 7 * alter - (3 if minor else 0))), minor


def key_alter(fifths, letter):
    sharps = [3, 0, 4, 1, 5, 2, 6]
    for i in range(min(7, fifths)):
        if sharps[i] == letter:
            return 1
    for i in range(min(7, -fifths)):
        if sharps[6 - i] == letter:
            return -1
    return 0


def spell(pitch, fifths, minor):
    tonic_letter = next(L for L in range(7)
                        for _ in [0]
                        if [0, 2, 4, -1, 1, 3, 5][L] + 7 * key_alter(fifths, L) - 0 is not None) if False else None
    # tonic letter from fifths: invert base+7*alter-(minor?3) — walk all 7x5 spellings
    want = fifths + (3 if minor else 0)
    tonic = 0
    for L in range(7):
        for a in (-1, 0, 1):
            if [0, 2, 4, -1, 1, 3, 5][L] + 7 * a == want:
                tonic, _ = L, a
    tonic_pc = (NAT_PC[tonic] + key_alter(fifths, tonic)) % 12
    off = (pitch % 12 - tonic_pc) % 12
    majT = [(0, 0), (0, 1), (1, 0), (2, -1), (2, 0), (3, 0), (3, 1), (4, 0), (5, -1), (5, 0), (6, -1), (6, 0)]
    minT = [(0, 0), (1, -1), (1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (4, 0), (5, 0), (5, 1), (6, 0), (6, 1)]
    lo, ra = (minT if minor else majT)[off]
    if not minor and off == 1 and fifths < 0:
        lo, ra = 1, -1
    letter = (tonic + lo) % 7
    alter = max(-2, min(2, key_alter(fifths, letter) + ra))
    octave = round((pitch - (NAT_PC[letter] + alter)) / 12)
    return letter, alter, octave


def groups_for(num, den):
    if den == 8 and num % 3 == 0:
        return [1.5] * (num // 3)
    if den == 8:
        g = [1.5]
        left = num - 3
        while left >= 2:
            g.append(1.0)
            left -= 2
        if left == 1:
            g.append(0.5)
        return g
    return [4.0 / den] * num


LEGAL = [4, 3, 2, 1.5, 1, 0.75, 0.5, 0.375, 0.25, 0.125]
TRIP = [1 / 3, 2 / 3, 1 / 6]


def near_mult(v, grid):
    return abs(v / grid - round(v / grid)) < 1e-5


def val_of(d, trip):
    table = TRIP if trip else LEGAL
    for x in table:
        if abs(d - x) < 1e-5:
            return x
    return None


def can_single(t, d, bounds, beats, num, den, trip_beat, is_rest):
    if is_rest and abs(t) < EPS and abs(d - beats) < EPS:
        return True
    if trip_beat:
        b0 = math.floor(t + EPS)
        if t + d > b0 + 1 + EPS:
            return False
        return val_of(d, True) is not None and near_mult(t - b0, 1 / 6)
    if val_of(d, False) is None:
        return None is not None if False else False
    if is_rest:
        if den == 4 and abs(d - round(d)) > EPS and abs(d - 2) > EPS and d not in (0.5, 0.25, 0.125, 1.0):
            pass
        if den == 4 and val_of(d, False) in (3, 1.5, 0.75, 0.375):
            return False
        if num == 4 and den == 4 and abs(d - 2) < EPS:
            return abs(t) < EPS or abs(t - 2) < EPS
    else:
        for i, b in enumerate(bounds[:-1]):
            if abs(t - b) < EPS:
                acc = 0.0
                for j in range(i, len(bounds) - 1):
                    acc += bounds[j + 1] - bounds[j]
                    if abs(d - acc) < EPS:
                        return True
        if den == 4:
            if abs(d - 3) < EPS or abs(d - 2) < EPS:
                return near_mult(t, 1) and t + d <= beats + EPS
            if abs(d - 1.5) < EPS:
                return near_mult(t, 0.5) and t + d <= beats + EPS
            if abs(d - 1) < EPS:
                return near_mult(t, 0.25) and t + d <= beats + EPS
    for i in range(len(bounds) - 1):
        if t >= bounds[i] - EPS and t + d <= bounds[i + 1] + EPS:
            v = val_of(d, False)
            base = None
            for den2, dur in ((1, 4), (2, 2), (4, 1), (8, 0.5), (16, 0.25), (32, 0.125)):
                if abs(v - dur) < EPS:
                    base = dur
                if abs(v - dur * 1.5) < EPS:
                    return near_mult(t - bounds[i], dur / 2 if not is_rest else dur * 10)
            if base is not None:
                return near_mult(t - bounds[i], min(base, 0.25) if not is_rest else base)
    return False


def split_point(t0, t1, bounds, trip_beat, num, den):
    grid = 1 / 6 if trip_beat else 0.125
    best, best_rank = None, -1
    x = (math.floor(t0 / grid + 1 + 1e-9)) * grid
    while x < t1 - EPS:
        if x > t0 + EPS:
            rank = 0
            if num == 4 and den == 4 and abs(x - 2) < EPS:
                rank = 5
            elif any(abs(x - b) < EPS for b in bounds):
                rank = 4
            elif near_mult(x, 0.5):
                rank = 3
            elif near_mult(x, 0.25) or near_mult(x, 1 / 3) or near_mult(x, 1 / 6):
                rank = 2
            elif near_mult(x, 0.125):
                rank = 1
            if rank > best_rank:
                best_rank, best = rank, x
        x += grid
    return best if best is not None else (t0 + t1) / 2


def spell_span(t0, t1, bounds, beats, num, den, trip_flags, is_rest, out, depth=0):
    if t1 - t0 < EPS:
        return
    trip_beat = trip_flags[min(len(trip_flags) - 1, int(t0 + EPS))] if trip_flags else False
    if depth > 24:
        out.append((t0, t1 - t0, trip_beat))
        return
    if can_single(t0, t1 - t0, bounds, beats, num, den, trip_beat, is_rest):
        out.append((t0, t1 - t0, trip_beat and abs(t1 - t0 - 1) > EPS and t1 - t0 < 1 - EPS))
        return
    x = split_point(t0, t1, bounds, trip_beat, num, den)
    if x <= t0 + EPS or x >= t1 - EPS:
        out.append((t0, t1 - t0, trip_beat))
        return
    spell_span(t0, x, bounds, beats, num, den, trip_flags, is_rest, out, depth + 1)
    spell_span(x, t1, bounds, beats, num, den, trip_flags, is_rest, out, depth + 1)


def type_of(d, trip):
    m = {4: "whole", 3: "half", 2: "half", 1.5: "quarter", 1: "quarter", 0.75: "eighth",
         0.5: "eighth", 0.375: "16th", 0.25: "16th", 0.125: "32nd"}
    if trip:
        return {2 / 3: "quarter", 1 / 3: "eighth", 1 / 6: "16th"}.get(
            min(TRIP, key=lambda x: abs(x - d)), "eighth"), False
    v = min(LEGAL, key=lambda x: abs(x - d))
    return m[v], v in (3, 1.5, 0.75, 0.375)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    with open(sys.argv[1]) as f:
        song = json.load(f)
    fifths, minor = parse_key(song.get("key", ""))
    meter = sorted(song.get("meterMap", []), key=lambda m: m.get("bar", 0))

    def bar_meter(b):
        num, den = 4, 4
        for mp in meter:
            if mp.get("bar", 0) <= b + EPS:
                num, den = int(mp.get("num", 4)), int(mp.get("den", 4))
        return num, den

    def bar_start(b):
        if not meter:
            return b * 4.0
        beat, prev, per = 0.0, 0.0, 4.0
        for mp in meter:
            mb = mp.get("bar", 0)
            if mb >= b:
                break
            if mb > prev:
                beat += (mb - prev) * per
                prev = mb
            per = int(mp.get("num", 4)) * 4.0 / int(mp.get("den", 4))
        return beat + (b - prev) * per

    tracks = [t for t in song.get("tracks", []) if t.get("notes")
              and t.get("source", {}).get("kind") != "audio"]
    if not tracks:
        print("no note tracks to export")
        sys.exit(1)
    last_end = max(n["start"] + n.get("len", 0.25) for t in tracks for n in t["notes"])
    nbars = max(1, int(math.ceil(song.get("lengthBars", 4))))
    while bar_start(nbars) < last_end - EPS and nbars < 512:
        nbars += 1

    parts = []
    for ti, t in enumerate(tracks):
        role = drum_role(t)
        # per-beat triplet election
        nbeats = int(math.ceil(bar_start(nbars))) + 1
        per_beat = [[] for _ in range(nbeats)]
        for n in t["notes"]:
            b = int(n["start"] + EPS)
            if 0 <= b < nbeats:
                per_beat[b].append(n["start"] - b)
        trip = [False] * nbeats
        for b, v in enumerate(per_beat):
            if len(v) < 2:
                continue
            e16 = sum(abs(f - round(f * 4) / 4) for f in v)
            e12 = sum(abs(f - round(f * 3) / 3) for f in v)
            if e12 * 1.15 < e16 - 1e-9:
                trip[b] = True

        def snap(x):
            b = min(len(trip) - 1, max(0, int(x + EPS)))
            g = 1 / 3 if trip[b] else 0.25
            return round(x / g) * g

        # quantize + chord-merge + monophonic display stream
        evs = []
        for n in sorted(t["notes"], key=lambda n: (n["start"], n["pitch"])):
            qs = max(0.0, snap(n["start"]))
            g = 1 / 3 if trip[min(len(trip) - 1, int(qs + EPS))] else 0.25
            qe = qs + g if role else max(qs + g, snap(n["start"] + n.get("len", 0.25)))
            if evs and abs(evs[-1][0] - qs) < EPS:
                evs[-1][2].append(n["pitch"])
                evs[-1][1] = max(evs[-1][1], qe)
            else:
                evs.append([qs, qe, [n["pitch"]]])
        for i in range(len(evs) - 1):
            evs[i][1] = min(evs[i][1], evs[i + 1][0])
        evs = [e for e in evs if e[1] - e[0] > EPS]

        # slice into measures + spell
        measures = []
        for b in range(nbars):
            num, den = bar_meter(b)
            beats = num * 4.0 / den
            m0 = bar_start(b)
            bounds = [0.0]
            for g in groups_for(num, den):
                bounds.append(bounds[-1] + g)
            local_trip = [trip[min(len(trip) - 1, int(m0 + i))] for i in range(int(math.ceil(beats)) + 1)]
            content = []           # (start, dur, pitches|None, tie_from, tie_to, triplet)
            for qs, qe, pitches in evs:
                s0, s1 = max(qs, m0), min(qe, m0 + beats)
                if s1 - s0 < EPS:
                    continue
                pieces = []
                spell_span(s0 - m0, s1 - m0, bounds, beats, num, den, local_trip, False, pieces)
                for pi, (ps, pd, ptr) in enumerate(pieces):
                    content.append((ps, pd, pitches,
                                    qs < m0 - EPS or pi > 0,
                                    qe > m0 + beats + EPS or pi + 1 < len(pieces), ptr))
            content.sort()
            cur, filled = 0.0, []
            for ps, pd, pitches, tf, tt, ptr in content:
                if ps > cur + EPS:
                    rp = []
                    spell_span(cur, ps, bounds, beats, num, den, local_trip, True, rp)
                    filled += [(a, b2, None, False, False, c) for (a, b2, c) in rp]
                filled.append((ps, pd, pitches, tf, tt, ptr))
                cur = max(cur, ps + pd)
            if beats > cur + EPS:
                rp = []
                spell_span(cur, beats, bounds, beats, num, den, local_trip, True, rp)
                filled += [(a, b2, None, False, False, c) for (a, b2, c) in rp]
            filled.sort()
            measures.append((num, den, filled))
        parts.append((t.get("name", f"track{ti}"), role, measures))

    # ---- emit
    o = []
    o.append('<?xml version="1.0" encoding="UTF-8"?>')
    o.append('<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
             '"http://www.musicxml.org/dtds/partwise.dtd">')
    o.append('<score-partwise version="4.0">')
    o.append(f'  <work><work-title>{escape(sys.argv[1].split("/")[-1].rsplit(".", 1)[0])}</work-title></work>')
    o.append('  <part-list>')
    for i, (name, _, _) in enumerate(parts):
        o.append(f'    <score-part id="P{i + 1}"><part-name>{escape(name)}</part-name></score-part>')
    o.append('  </part-list>')
    for i, (name, role, measures) in enumerate(parts):
        o.append(f'  <part id="P{i + 1}">')
        for mi, (num, den, filled) in enumerate(measures):
            o.append(f'    <measure number="{mi + 1}">')
            if mi == 0:
                o.append('      <attributes>')
                o.append(f'        <divisions>{DIV}</divisions>')
                o.append(f'        <key><fifths>{fifths}</fifths><mode>{"minor" if minor else "major"}</mode></key>')
                o.append(f'        <time><beats>{num}</beats><beat-type>{den}</beat-type></time>')
                if role:
                    o.append('        <clef><sign>percussion</sign><line>2</line></clef>')
                o.append('      </attributes>')
                if i == 0:   # the tempo travels (import + every notation app reads it)
                    o.append(f'      <direction><sound tempo="{song.get("bpm", 120)}"/></direction>')
            for (ps, pd, pitches, tf, tt, ptr) in filled:
                dur = max(1, round(pd * DIV))
                ty, dot = type_of(pd, ptr)
                if pitches is None:
                    o.append(f'      <note><rest/><duration>{dur}</duration><type>{ty}</type>'
                             + ('<dot/>' if dot else '') + '</note>')
                    continue
                for pi2, p in enumerate(sorted(set(pitches))):
                    n = ['      <note>']
                    if pi2 > 0:
                        n.append('<chord/>')
                    if role:
                        step_abs = 30 + role[0]
                        n.append(f'<unpitched><display-step>{LETTERS[step_abs % 7]}</display-step>'
                                 f'<display-octave>{step_abs // 7}</display-octave></unpitched>')
                    else:
                        L, alt, octv = spell(p, fifths, minor)
                        n.append(f'<pitch><step>{LETTERS[L]}</step>'
                                 + (f'<alter>{alt}</alter>' if alt else '')
                                 + f'<octave>{octv}</octave></pitch>')
                    n.append(f'<duration>{dur}</duration>')
                    if tf:
                        n.append('<tie type="stop"/>')
                    if tt:
                        n.append('<tie type="start"/>')
                    n.append(f'<type>{ty}</type>')
                    if dot:
                        n.append('<dot/>')
                    if ptr:
                        n.append('<time-modification><actual-notes>3</actual-notes>'
                                 '<normal-notes>2</normal-notes></time-modification>')
                    if role and role[1]:
                        n.append(f'<notehead>{"circle-x" if role[1] == "circle-x" else "x"}</notehead>')
                    if tf or tt:
                        n.append('<notations>'
                                 + ('<tied type="stop"/>' if tf else '')
                                 + ('<tied type="start"/>' if tt else '') + '</notations>')
                    n.append('</note>')
                    o.append(''.join(n))
            o.append('    </measure>')
        o.append('  </part>')
    o.append('</score-partwise>')
    with open(sys.argv[2], "w") as f:
        f.write("\n".join(o) + "\n")
    print(f"[musicxml] {len(parts)} parts, {nbars} bars -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
