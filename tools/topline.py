#!/usr/bin/env python3
"""TOPLINE — the section-aware melody writer (f157; the vocal row's missing organ).

  topline.py <song> [--track topline] [--seed N] [--write]

Laws (songwriting canon, cited in stamp f157):
  HOOK LAW    — the first chorus's melody is CACHED and every later chorus/drop
                repeats it verbatim (bar-shifted): repetition IS memorability.
  LIFT LAW    — chorus/drop sits a fifth-to-octave above the verse register and
                CLIMBS to its peak note late in the phrase (the satisfying climb).
  TALK LAW    — verses are denser, lower, stepwise (conversational); each verse
                instance varies (seeded) while choruses never do.
  SPACE LAW   — intro/break/outro carry rests or a single pickup, not melody.
Notes land on chord tones at strong beats (chordvote field), scale tones between.
Deterministic per seed. Output: a 'topline' track (replace-if-exists on --write).
"""
import argparse, json, os, random, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from chordvote import chord_map
from reharm import parse_chord
from loop_gen import key_to_pcs
import songname

CHORUSY = ("chorus", "drop", "hook")
VERSY = ("verse", "build", "bridge", "inst")


def _sections(song):
    secs = sorted(song.get("sections", []), key=lambda s: float(s["startBar"]))
    total = float(song.get("lengthBars", 16))
    out = []
    for i, s in enumerate(secs):
        end = float(secs[i + 1]["startBar"]) if i + 1 < len(secs) else total
        base = re.sub(r"\d+$", "", str(s.get("name", "")).lower())
        out.append((base, float(s["startBar"]), end))
    return out or [("chorus", 0.0, total)]


def _chord_at(chords, bar):
    cur = None
    for c in chords:
        if c["bar"] - 1 <= bar:
            cur = c
    return cur or (chords[0] if chords else None)


def generate(song, seed=0):
    chords = song.get("chords") or chord_map(song)
    _, scale = key_to_pcs(str(song.get("key") or "A minor"))
    scale = sorted(scale)
    rng = random.Random(seed * 6271 + 5)
    verse_base, lift = 62, 7                     # verse center D4-ish; chorus +5th
    notes, hook_cache = [], None
    for name, b0, b1 in _sections(song):
        bars = int(b1 - b0)
        if bars <= 0 or any(k in name for k in ("intro", "outro", "break")):
            continue                              # SPACE LAW
        chorusy = any(k in name for k in CHORUSY)
        if chorusy and hook_cache is not None:    # HOOK LAW: verbatim, bar-shifted
            notes += [dict(n, start=round(n["start"] - hook_cache[0] + b0 * 4.0, 4))
                      for n in hook_cache[1]]
            continue
        sec_notes = []
        base = verse_base + (lift if chorusy else 0)
        step_grid = 1.0 if chorusy else 0.5       # TALK LAW density
        cur = base
        for bar in range(bars):
            c = _chord_at(chords, b0 + bar)
            if not c:
                continue
            r, q, d7 = parse_chord(c["chord"])
            ctones = sorted({(r + iv) % 12 for iv in ((0, 3, 7) if q == "min" else (0, 4, 7))})
            t = 0.0
            while t < 4.0 - 1e-6:
                strong = abs(t % 2.0) < 1e-6
                pcs = ctones if strong else scale
                cands = [p for p in range(base - 5, base + 10) if p % 12 in pcs]
                near = [p for p in cands if abs(p - cur) <= (4 if not chorusy else 7)]
                cur = rng.choice(near or cands)
                ln = step_grid * (2 if (chorusy and rng.random() < 0.4) else 1)
                ln = min(ln, 4.0 - t)
                if rng.random() < (0.82 if chorusy else 0.72):   # rests breathe
                    sec_notes.append({"start": round(b0 * 4 + bar * 4 + t, 4),
                                      "len": round(ln * 0.92, 4),
                                      "pitch": int(cur), "vel": 0.78 if chorusy else 0.66})
                t += ln
        if chorusy and sec_notes:
            # LIFT LAW: force the peak late in the first phrase — snapped UP to
            # the nearest scale tone (a raw +5 landed out of key; battery caught it)
            peak_i = min(len(sec_notes) - 1, int(len(sec_notes) * 0.7))
            want = max(n["pitch"] for n in sec_notes) + 4
            while want % 12 not in scale:
                want += 1
            sec_notes[peak_i]["pitch"] = want
            sec_notes[peak_i]["len"] = max(sec_notes[peak_i]["len"], 1.4)
            hook_cache = (b0 * 4.0, [dict(n) for n in sec_notes])
        notes += sec_notes
    return notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("--track", default="topline")
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    sp = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(sp))
    notes = generate(song, a.seed)
    secs = len(_sections(song))
    print(f"[topline] {len(notes)} notes over {secs} sections (hook law: choruses repeat)")
    print("TOPLINE_JSON " + json.dumps({"notes": len(notes), "sections": secs}))
    if a.write and notes:
        song["tracks"] = [t for t in song["tracks"] if t.get("name") != a.track]
        song["tracks"].append({"name": a.track, "source": {"kind": "faust", "id": "pluck"},
                               "gainDb": -8, "notes": notes})
        json.dump(song, open(sp, "w"), indent=1)
        print(f"[topline] wrote track '{a.track}'")


if __name__ == "__main__":
    main()
