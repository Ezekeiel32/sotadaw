#!/usr/bin/env python3
"""loop_variations — THE LOOP GENERATOR, done right (manifesto: most underrated
feature in every DAW). Take any loop region of a track and spin N musical
variations of it into launcher slots, instantly and deterministically — no
tokens, no waiting. The human jams through them in the Live view and keeps
what moves them (jam-capture materializes the winner into the arrangement).

  loop_variations.py <song> <track> <from_bar> <bars> [count]

Variations (seeded by song+track+bar, reproducible):
  A rotate    — pattern rotated by half a beat (new downbeat relationship)
  B thin      — weakest-velocity off-grid notes dropped (space = groove)
  C dense     — echo notes fill the gaps at -25% velocity (energy up)
  D recolor   — melodic: alternate 2-beat groups jump an octave;
                percussive (narrow pitch span): every 4th 16th accented
  E halftime  — note starts stretched 2x around the loop (instant switch-up)
  F humanize  — velocity +/-12% and subtle off-grid timing breath
  G dejavu    — Marbles law: clock locked, ~35% of notes re-roll their VALUE
                from the loop's own pool (familiar, never identical)
"""
import json, math, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _clone(notes):
    return [dict(n) for n in notes]


def var_rotate(notes, length, rng):
    out = _clone(notes)
    for n in out:
        n["start"] = round((n["start"] + 0.5) % length, 4)
    return out


def var_thin(notes, length, rng):
    if len(notes) < 4:
        return _clone(notes)
    vels = sorted(n.get("vel", 0.8) for n in notes)
    cut = vels[int(len(vels) * 0.3)]
    return [dict(n) for n in notes
            if n.get("vel", 0.8) > cut or abs(n["start"] - round(n["start"])) < 1e-6]


def var_dense(notes, length, rng):
    out = _clone(notes)
    starts = sorted(n["start"] for n in notes)
    for n in sorted(_clone(notes), key=lambda x: x["start"]):
        nxt = min((s for s in starts if s > n["start"]), default=length)
        if nxt - n["start"] >= 1.0:
            e = dict(n)
            e["start"] = round(n["start"] + 0.5, 4)
            e["vel"] = round(max(0.1, n.get("vel", 0.8) * 0.75), 3)
            if e["start"] < length:
                out.append(e)
    return out


def var_recolor(notes, length, rng):
    out = _clone(notes)
    if not out:
        return out
    pitches = [n["pitch"] for n in out]
    if max(pitches) - min(pitches) >= 5:          # melodic: octave color
        for n in out:
            if int(n["start"] // 2) % 2 == 1:
                n["pitch"] = n["pitch"] + 12 if n["pitch"] <= 108 else n["pitch"] - 12
    else:                                          # percussive: accent cycle
        for n in out:
            slot = int(round(n["start"] / 0.25))
            n["vel"] = round(min(1.0, n.get("vel", 0.8) * (1.25 if slot % 4 == 0 else 0.9)), 3)
    return out


def var_halftime(notes, length, rng):
    out = _clone(notes)
    for n in out:
        n["start"] = round((n["start"] * 2.0) % length, 4)
        n["len"] = min(n.get("len", 0.25) * 2.0, length - n["start"])
    return out


def var_humanize(notes, length, rng):
    out = _clone(notes)
    for n in out:
        n["vel"] = round(min(1.0, max(0.05, n.get("vel", 0.8) * rng.uniform(0.88, 1.12))), 3)
        if abs(n["start"] - round(n["start"])) > 1e-6:   # keep downbeats anchored
            n["start"] = round(max(0.0, min(length - 0.05, n["start"] + rng.uniform(-0.03, 0.03))), 4)
    return out


def var_dejavu(notes, length, rng):
    """Marbles' DEJA VU knob as a variation: the clock stays LOCKED, ~35% of
    notes re-roll their VALUE from the loop's own pool (pitch for melodic
    material, velocity-accent for percussive) — familiar but never the same."""
    out = _clone(notes)
    pool = [n["pitch"] for n in notes]
    melodic = len(set(pool)) >= 3
    concurrent = {}
    for n in notes:                           # chord safety: never re-roll ONTO a
        concurrent.setdefault(round(n["start"], 4), set()).add(n["pitch"])
    for n in out:
        if rng.random() >= 0.35:
            continue                          # locked: replay as-is
        if melodic:
            taken = concurrent.get(round(n["start"], 4), set())
            options = [p_ for p_ in pool if p_ not in taken or p_ == n["pitch"]]
            if len(set(options)) <= 1:
                continue                      # nowhere new to go at this instant
            new_p = rng.choice(options)
            taken.discard(n["pitch"]); taken.add(new_p)
            n["pitch"] = new_p
        else:
            n["vel"] = round(min(1.0, max(0.15,
                (1.0 if rng.random() < 0.4 else 0.55) * n.get("vel", 0.8) + 0.1)), 3)
    return out


VARIANTS = [("rotate", var_rotate), ("thin", var_thin), ("dense", var_dense),
            ("recolor", var_recolor), ("halftime", var_halftime), ("humanize", var_humanize),
            ("dejavu", var_dejavu)]


def generate(song_path, track_name, from_bar, bars, count=7):
    song = json.load(open(song_path))
    tr = next((t for t in song["tracks"] if t.get("name") == track_name), None)
    if tr is None:
        return f"no track '{track_name}'"
    a, length = from_bar * 4.0, bars * 4.0
    seed = [dict(n, start=round(n["start"] - a, 4)) for n in tr.get("notes", [])
            if a <= n["start"] < a + length]
    if not seed:
        return f"no notes in bars {from_bar}..{from_bar + bars} of '{track_name}'"
    rng = random.Random(f"{os.path.basename(song_path)}:{track_name}:{from_bar}:{bars}")
    slots = tr.setdefault("slots", [])
    scenes = song.setdefault("scenes", [])
    base = len(slots)
    made = []
    sig = lambda ns: tuple(sorted((n["start"], n["pitch"], round(n.get("vel", 0.8), 3)) for n in ns))
    seed_sig = sig(seed)
    for i, (vname, fn) in enumerate(VARIANTS[:count]):
        notes = fn(seed, length, rng)
        if sig(notes) == seed_sig:          # identity (e.g. dense on 16th-grid material):
            vname = vname + "-gap"          # carve space instead — drop every 4th 16th
            notes = [n for n in _clone(notes) if int(round(n["start"] / 0.25)) % 4 != 3]
        dedup = {}
        for n in notes:                     # wrap collisions (halftime): keep the louder
            k = (round(n["start"], 4), n["pitch"])
            if k not in dedup or n.get("vel", 0.8) > dedup[k].get("vel", 0.8):
                dedup[k] = n
        notes = sorted(dedup.values(), key=lambda n: (n["start"], n["pitch"]))
        for n in notes:                     # safety: clamp into the loop
            n["start"] = max(0.0, min(length - 0.01, n["start"]))
            n["len"] = max(0.05, min(n.get("len", 0.25), length - n["start"]))
        sc = base + i
        while len(slots) <= sc:
            slots.append(None)
        while len(scenes) <= sc:
            scenes.append({"name": f"Scene {len(scenes) + 1}"})
        slots[sc] = {"name": f"{track_name} {vname}", "lengthBeats": length, "notes": notes}
        scenes[sc]["name"] = f"Var {chr(65 + i)} {vname}"
        made.append(f"{vname}({len(notes)}n)")
    json.dump(song, open(song_path, "w"), indent=1)
    return (f"OK: {len(made)} loop variations of '{track_name}' bars {from_bar}-{from_bar + bars} "
            f"-> scenes {base + 1}..{base + len(made)}: {', '.join(made)}. "
            f"Jam them in the Live view; jam-capture keeps the winner.")


if __name__ == "__main__":
    p = sys.argv[1]
    if not os.path.isabs(p):
        p = os.path.join(ROOT, "songs", p if p.endswith(".json") else p + ".json")
    print(generate(p, sys.argv[2], float(sys.argv[3]), float(sys.argv[4]),
                   int(sys.argv[5]) if len(sys.argv) > 5 else 6))
