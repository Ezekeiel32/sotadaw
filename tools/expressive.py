#!/usr/bin/env python3
"""EXPRESSIVE — a MEASURABLE humanization (GrooVAE + GigaMIDI grounded).

  expressive.py <song> [--track name] [--amount 0.6] [--write]     # humanize
  expressive.py <song> --measure [--track name]                    # score only

Deep-research (firing 66) surfaced the SOTA symbolic-performance lane: Magenta's
GrooVAE/Drumify humanize by "reconstructing velocity and microtiming"; GigaMIDI
(TISMIR 2025) detects EXPRESSIVE vs mechanical MIDI via onset metric-level.

TWO COMPLEMENTARY METRICS (kept honest, firing 68):
  1. expressiveness() — OUR continuous score on GrooVAE's two axes (microtiming
     RMS + velocity CV). SENSITIVE: rises monotonically with subtle humanization
     (0 -> 15 -> 28 -> 42 across amount 0/0.4/0.7/1.0). The studio-feel meter.
  2. nomml_level() — a FAITHFUL median-metric-level classifier following GigaMIDI's
     DEFINITION. COARSE binary: dead grid -> mechanical, a real off-grid
     performance -> expressive. The is-this-a-performance-or-a-score classifier.
  They measure different things: subtle humanize moves (1) a lot and (2) little —
  by design. Neither is "NOMML with 100% accuracy" (that is their trained,
  dataset-specific threshold); we verify DISCRIMINATION on our own patterns.

HUMANIZE (the GrooVAE axes, rule-based + deterministic per seed):
  - a slow timing DRIFT (correlated push/pull, not white noise) + tiny per-note
    jitter, bounded so nothing crosses a beat
  - a metric ACCENT curve (downbeats loud, offbeats soft) + jitter
Never touches LOCKED tracks. Battery proves score RISES and stays musical.
"""
import argparse, json, math, os, re, sys
import songname

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def expressiveness(notes):
    """OUR continuous companion score (GrooVAE's two axes): microtiming RMS + velocity
    CV. Not NOMML — see nomml_level() for the metric-level classifier."""
    if len(notes) < 2:
        return 0.0
    devs = []
    for n in notes:
        q = round(n["start"] / 0.25) * 0.25
        devs.append((n["start"] - q) / 0.25)
    micro = math.sqrt(sum(d * d for d in devs) / len(devs))
    vels = [float(n.get("vel", 0.8)) for n in notes]
    mean_v = sum(vels) / len(vels)
    velcv = (math.sqrt(sum((v - mean_v) ** 2 for v in vels) / len(vels)) / mean_v) if mean_v > 1e-6 else 0.0
    return round(100.0 * (2.0 * micro + velcv), 2)


# metric-level hierarchy (coarse->fine): the subdivision an onset must align to.
# level = index; an onset on the beat is level 0, on the 8th level 1, ... a note
# that fits NO grid down to a 64th is "maximally expressive" (MAX_LEVEL).
_GRIDS = [1.0, 0.5, 0.25, 0.125, 0.0625, 1 / 3.0, 1 / 6.0, 1 / 12.0]  # + triplets
_MAX_LEVEL = len(_GRIDS)


def nomml_level(notes, eps=0.02):
    """NOMML — Note Onset Median Metric Level, FAITHFUL to GigaMIDI's DEFINITION
    (TISMIR 2025): per onset, the finest metric level it aligns to within eps
    beats; median across onsets. Mechanical (dead grid) -> low median; expressive
    (off-grid microtiming) -> high. We do NOT claim their exact trained level-12
    threshold (that is dataset-specific); we verify DISCRIMINATION on our patterns.
    Returns (median_level, classification) where expressive = median >= 3.5."""
    if len(notes) < 2:
        return 0.0, "n/a"
    levels = []
    for n in notes:
        pos = n["start"] % 4.0                       # position within the bar
        best = _MAX_LEVEL
        for lvl, g in enumerate(_GRIDS):
            if abs(pos / g - round(pos / g)) * g < eps:
                best = min(best, lvl)                # aligns at this (coarse) level
        levels.append(best if best < _MAX_LEVEL else _MAX_LEVEL)
    levels.sort()
    m = len(levels)
    median = levels[m // 2] if m % 2 else (levels[m // 2 - 1] + levels[m // 2]) / 2.0
    return round(median, 2), ("expressive" if median >= 3.5 else "mechanical")


def humanize(notes, amount=0.6, seed=0):
    import random
    rng = random.Random(f"human:{seed}:{len(notes)}")
    ordered = sorted(range(len(notes)), key=lambda i: notes[i]["start"])
    # slow correlated drift: a random-walk over the note sequence (bounded)
    drift, out = 0.0, [dict(n) for n in notes]
    max_shift = 0.06 * amount                         # beats; < a 16th so no reorder
    for k, i in enumerate(ordered):
        drift = max(-max_shift, min(max_shift, drift + rng.uniform(-1, 1) * max_shift * 0.5))
        jit = rng.uniform(-1, 1) * max_shift * 0.4
        beat_in_bar = notes[i]["start"] % 4.0
        # metric accent: beats 0,2 loud; the "and" soft; 16th offbeats softest
        pos16 = round((beat_in_bar % 1.0) / 0.25) % 4
        accent = {0: 1.0, 2: 0.9}.get(int(beat_in_bar), 0.72) if pos16 == 0 else (0.6 if pos16 == 2 else 0.5)
        base_v = float(notes[i].get("vel", 0.8))
        target_v = base_v * (1 - amount) + accent * amount
        target_v *= 1.0 + rng.uniform(-0.08, 0.08) * amount
        out[i]["start"] = round(max(0.0, notes[i]["start"] + drift + jit), 4)
        out[i]["vel"] = round(min(1.0, max(0.08, target_v)), 3)
    return out


def _melodic_or_drum(t):
    nm = str(t.get("name", "")).lower()
    return True   # humanize applies to any note track; caller filters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song"); ap.add_argument("--track", default=None)
    ap.add_argument("--amount", type=float, default=0.6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    path = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(path))
    targets = [t for t in song["tracks"]
               if (a.track is None or t.get("name") == a.track) and t.get("notes")
               and not t.get("locked")]
    if a.measure:
        out = {}
        for t in targets:
            e = expressiveness(t["notes"]); lvl, cls = nomml_level(t["notes"])
            out[t["name"]] = {"expressiveness": e, "nomml_level": lvl, "class": cls}
            print(f"  {t['name']:12} expressiveness {e} | NOMML {lvl} ({cls})")
        print("EXPRESSIVE_JSON " + json.dumps(out))
        return
    report = {}
    for t in targets:
        before = expressiveness(t["notes"])
        t["notes"] = humanize(t["notes"], a.amount, a.seed)
        after = expressiveness(t["notes"])
        lvl, cls = nomml_level(t["notes"])
        report[t["name"]] = {"before": before, "after": after, "nomml": lvl, "class": cls}
        print(f"  {t['name']:12} expressiveness {before} -> {after} | NOMML {lvl} ({cls})")
    if a.write:
        json.dump(song, open(path, "w"), indent=1)
        print(f"[expressive] humanized -> songs/{name}.json")
    print("EXPRESSIVE_JSON " + json.dumps(report))


if __name__ == "__main__":
    main()
