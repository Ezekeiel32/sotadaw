#!/usr/bin/env python3
"""REHARMONIZE — the chord lane becomes actionable (chordvote -> transform -> retune).

  reharm.py <song> --rotate N [--write] [--out other_song]
  reharm.py <song> --to "Eb,Fm,Ab,Db" [--write] [--out other_song]

The loop: vote the song's own chords (chordvote), transform the cycle —
--rotate N is wave-29's schema_rotation law ('one schema = four progressions:
start the cycle anywhere'), --to sets an explicit per-cycle target — then
retune melodic tracks bar-by-bar with the Cubase-teardown law: chord tones map
ROLE to ROLE (root->root, third->third(quality-aware), fifth->fifth, b7->b7)
choosing the octave that MOVES LEAST; non-chord tones (tensions/passing)
transpose by the root delta so contours survive. Drums and LOCKED tracks are
never touched. Verification is built into the design: chordvote AFTER reharm
must read the target progression.

Machine line: REHARM_JSON {...}
"""
import argparse, copy, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import chord_map, is_drum_track, PC
import songname

NAME2PC = {n: i for i, n in enumerate(PC)}
NAME2PC.update({"C#": 1, "D#": 3, "F#": 6, "G#": 8, "A#": 10})


def parse_chord(label):
    m = re.match(r"([A-G][b#]?)(m?)(7?)$", label.strip())
    if not m:
        raise SystemExit(f"can't parse chord '{label}'")
    r = NAME2PC[m.group(1)]
    q = "min" if m.group(2) == "m" else "maj"
    return r, q, bool(m.group(3))


def tones(r, q, dom7):
    t = {0: r, 1: (r + (3 if q == "min" else 4)) % 12, 2: (r + 7) % 12}
    if dom7:
        t[3] = (r + 10) % 12
    return t


def detect_cycle(labels):
    """smallest period that explains the bar-chord sequence (fallback: whole)."""
    n = len(labels)
    for p in range(1, n):
        if n % p == 0 and all(labels[i] == labels[i % p] for i in range(n)):
            return p
    return n


def retune_note(pitch, old, new):
    """role-map a note between chords with MINIMAL MOTION (the Cubase law)."""
    ot, nt = tones(*old), tones(*new)
    pc = pitch % 12
    role = next((k for k, v in ot.items() if v == pc), None)
    if role is None:                                   # tension/passing: root delta,
        delta = (new[0] - old[0]) % 12                 # folded to the nearest octave
        if delta > 6:
            delta -= 12
        return pitch + delta
    target_pc = nt.get(role, nt[0])
    cands = [pitch + ((target_pc - pc) % 12), pitch + ((target_pc - pc) % 12) - 12]
    return min(cands, key=lambda c: abs(c - pitch))


def reharm(song, targets_per_cycle=None, rotate=0):
    chords = song.get("chords") or chord_map(song)
    if not chords:
        raise SystemExit("no chords voteable in this song")
    labels = [c["chord"] for c in chords]
    bars = [c["bar"] for c in chords]
    period = detect_cycle(labels)
    cycle = labels[:period]
    if targets_per_cycle:
        tgt_cycle = targets_per_cycle
        if len(tgt_cycle) == len(labels):          # full-length per-bar plan:
            period = len(labels)                   # override the detected cycle
            cycle = labels
        elif len(tgt_cycle) != period:
            raise SystemExit(f"target has {len(tgt_cycle)} chords but the song's "
                             f"cycle is {period} ({cycle}); pass {len(labels)} "
                             f"chords for a full per-bar plan")
    else:
        tgt_cycle = cycle[rotate % period:] + cycle[:rotate % period]
    plan = {b: (parse_chord(labels[i]), parse_chord(tgt_cycle[i % period]))
            for i, b in enumerate(bars)}
    moved = total = 0
    for t in song.get("tracks", []):
        if is_drum_track(t) or t.get("locked"):
            continue
        for n in t.get("notes", []):
            b = int(float(n["start"]) // 4) + 1
            if b not in plan:
                continue
            old, new = plan[b]
            if old == new:
                continue
            p2 = retune_note(int(n["pitch"]), old, new)
            total += 1
            if p2 != n["pitch"]:
                n["pitch"] = int(p2)
                moved += 1
    song["chords"] = [{"bar": b, "chord": tgt_cycle[i % period],
                       "conf": chords[i]["conf"]} for i, b in enumerate(bars)]
    return {"cycle": cycle, "target": tgt_cycle, "period": period,
            "notes_touched": total, "notes_moved": moved}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--rotate", type=int, default=0)
    ap.add_argument("--to", default=None, help="explicit per-cycle chords, comma-sep")
    ap.add_argument("--out", default=None, help="write result as this song name")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    song = json.load(open(os.path.join(ROOT, "songs", f"{name}.json")))
    tgt = [x.strip() for x in a.to.split(",")] if a.to else None
    rep = reharm(song, tgt, a.rotate)
    print(f"[reharm] cycle {rep['cycle']} (period {rep['period']}) -> {rep['target']}"
          f" | {rep['notes_moved']}/{rep['notes_touched']} notes moved")
    out_name = re.sub(r"[^a-z0-9_]", "", a.out.lower()) if a.out else name
    if a.write or a.out:
        json.dump(song, open(os.path.join(ROOT, "songs", f"{out_name}.json"), "w"),
                  indent=1)
        print(f"[reharm] -> songs/{out_name}.json")
    print("REHARM_JSON " + json.dumps(rep))


if __name__ == "__main__":
    main()
