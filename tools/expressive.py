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


# ===================================================================== v2
# THE KTH/DirectorMusices PORT (backlog wave 14, R-13: DM's rule set beat
# every neural system in RenCon 2025 prelim) + velocity-first law (RenCon:
# dynamics variability predicts perceived quality far better than rubato)
# + structured-timing-only law (Davies/Madison/Senn reversal: random jitter
# does NOT add groove; quantized rated >= randomly-humanized).
# Published k-values: HIGH LOUD 2.1, LEAP 1.9, MELODIC CHARGE per-pc table.

# distance-from-root on the circle of fifths -> melodic charge (DM table,
# condensed): chromatic/far degrees carry tension = play them louder.
_CHARGE = {0: 0.0, 7: 1.0, 5: 2.0, 2: 2.5, 10: 3.0, 9: 3.5, 4: 4.0,
           3: 4.5, 11: 5.0, 8: 5.5, 1: 6.0, 6: 6.5}

# R-13 genre expression policy (217): who gets rubato, who stays on the grid
GENRE_EXPRESSION = {
    "classical": {"rubato": 1.0, "vel_amount": 1.0, "arch": True},
    "jazz":      {"rubato": 0.5, "vel_amount": 1.0, "arch": True},
    "folk":      {"rubato": 0.6, "vel_amount": 0.9, "arch": True},
    "ballad":    {"rubato": 0.5, "vel_amount": 0.9, "arch": True},
    "soul":      {"rubato": 0.2, "vel_amount": 1.0, "arch": True},
    "edm":       {"rubato": 0.0, "vel_amount": 0.7, "arch": False},
    "default":   {"rubato": 0.0, "vel_amount": 0.9, "arch": True},
}
_EXPR_FAMILY = {
    "classical": ("classical", "orchestral", "cinematic", "piano", "chamber"),
    "jazz": ("jazz", "swing", "bebop", "bossa"),
    "folk": ("folk", "country", "acoustic", "singer"),
    "ballad": ("ballad", "rnb", "r_b"),
    "soul": ("soul", "gospel", "neosoul", "neo_soul", "funk", "blues"),
    "edm": ("house", "techno", "trance", "edm", "dnb", "trap", "drill",
            "phonk", "grime", "dubstep", "hardstyle", "garage", "electro",
            "hiphop", "hip_hop", "boombap", "amapiano", "reggaeton"),
}


def expression_policy(genre):
    g = str(genre or "").lower()
    for fam, keys in _EXPR_FAMILY.items():
        if any(k in g for k in keys):
            return GENRE_EXPRESSION[fam]
    return GENRE_EXPRESSION["default"]


def _metric_accent(start, beats_per_bar=4.0):
    """+2/+1/0 metric-level accent steps (R-13: +8/+4/0 on the 0-127 scale
    = +0.063/+0.031/0 in house 0..1 velocity)."""
    pos = start % beats_per_bar
    if abs(pos - round(pos)) < 1e-6:
        b = int(round(pos))
        return 0.063 if b == 0 else (0.031 if b % 2 == 0 else 0.016)
    if abs(pos * 2 - round(pos * 2)) < 1e-6:
        return 0.0
    return -0.016


def humanize_v2(notes, genre="", key_root_pc=None, seed=0, amount=1.0,
                jitter=0.0, phrase_fn=None):
    """VELOCITY-FIRST deterministic humanize (KTH port). Timing: STRUCTURED
    only (phrase-arch rubato where the genre allows; NO random jitter unless
    jitter>0, and then bounded to <=60% of the natural human SD per the R-3
    court law). Returns a NEW note list.

    Rules ported (published k-values): metric accent (+8/+4/0), phrase
    dynamic arch (parabolic to the apex), HIGH LOUD (k 2.1), MELODIC CHARGE,
    DURATION CONTRAST, LEAP articulation micropause (k 1.9), PUNCTUATION
    (phrase-final shortening)."""
    if not notes:
        return []
    pol = expression_policy(genre)
    va = pol["vel_amount"] * amount
    out = [dict(n) for n in sorted(notes, key=lambda n: float(n.get("start", 0)))]
    # phrases: caller may supply a splitter (melody_court.phrases); fallback =
    # gap-based (rest >= 1 beat starts a new phrase)
    spans = []
    if phrase_fn:
        try:
            phs = phrase_fn(out)
            idx = 0
            for ph in phs:
                spans.append((idx, idx + len(ph) - 1))
                idx += len(ph)
        except Exception:
            spans = []
    if not spans:
        s0 = 0
        for i in range(1, len(out)):
            prev = out[i - 1]
            gap = float(out[i]["start"]) - (float(prev["start"])
                                            + float(prev.get("len", 0.25)))
            if gap >= 1.0:
                spans.append((s0, i - 1))
                s0 = i
        spans.append((s0, len(out) - 1))
    rng = None
    if jitter > 0:
        import random
        rng = random.Random(f"h2:{seed}:{len(out)}")
    for (a, b) in spans:
        span_n = max(b - a, 1)
        apex = a + int(span_n * 0.618)               # golden-section apex
        for i in range(a, b + 1):
            n = out[i]
            v = float(n.get("vel", 0.8))
            # metric accent hierarchy
            v += _metric_accent(float(n["start"])) * va
            # phrase dynamic arch (parabolic crescendo to apex)
            if pol["arch"] and span_n >= 3:
                x = (i - a) / span_n
                xa = (apex - a) / span_n or 0.5
                arch = 1.0 - ((x - xa) / max(xa, 1.0 - xa)) ** 2
                v += 0.10 * va * arch
            # HIGH LOUD (k 2.1): ~+2.1 MIDI vel per octave above C4
            v += (2.1 / 127.0) * ((int(n.get("pitch", 60)) - 60) / 12.0) * va
            # MELODIC CHARGE vs the key root (when known)
            if key_root_pc is not None:
                ch = _CHARGE[(int(n.get("pitch", 60)) - key_root_pc) % 12]
                v += (ch / 6.5) * 0.045 * va
            # DURATION CONTRAST: short notes lighter, long notes carry
            ln = float(n.get("len", n.get("length", 0.25)))
            v += (0.02 if ln >= 1.0 else (-0.02 if ln <= 0.15 else 0.0)) * va
            if rng is not None:
                # bounded seeded jitter, <=60% of natural SD (court law);
                # natural SD ~0.02 beats -> vel analog kept tiny
                v += rng.uniform(-1, 1) * 0.03 * min(jitter, 0.6)
                n["start"] = round(max(0.0, float(n["start"])
                                       + rng.uniform(-1, 1) * 0.012
                                       * min(jitter, 0.6)), 4)
            n["vel"] = round(min(1.0, max(0.06, v)), 3)
        # LEAP articulation (k 1.9): micropause before leaps > perfect 4th
        for i in range(a + 1, b + 1):
            leap = abs(int(out[i].get("pitch", 60))
                       - int(out[i - 1].get("pitch", 60)))
            if leap > 5:
                prev = out[i - 1]
                prev["len"] = round(max(float(prev.get("len", 0.25)) * 0.82,
                                        0.05), 4)
                out[i]["vel"] = round(min(1.0, float(out[i]["vel"])
                                          + 0.019 * leap / 12.0 * va), 3)
        # PUNCTUATION: phrase-final note shortens (micropause into the breath)
        last = out[b]
        last["len"] = round(max(float(last.get("len", 0.25)) * 0.85, 0.05), 4)
        # phrase-arch RUBATO (structured timing): accel to apex, ritard out
        if pol["rubato"] > 0 and span_n >= 4:
            depth = 0.02 * pol["rubato"] * amount     # beats at the extremes
            for i in range(a, b + 1):
                x = (i - a) / span_n
                # negative = early (accel) rising to late at the phrase end
                off = depth * (x ** 2) - depth * 0.35 * (1 - abs(2 * x - 1))
                out[i]["start"] = round(max(0.0, float(out[i]["start"]) + off), 4)
    return out


# ------------------------------------------------ R-13 GigaMIDI courts (076)
def gigamidi_courts(notes, tpqn=960):
    """DNVR / DNODR / NOMML with GigaMIDI's published floors (velocities are
    house 0..1 -> mapped to 0-127). Returns the three numbers + verdicts."""
    if not notes:
        return {"ok": True, "skipped": "no notes"}
    vels = {int(round(float(n.get("vel", 0.8)) * 127)) for n in notes}
    dnvr = len(vels) / 127.0 * 100.0
    devs = set()
    for n in notes:
        s = float(n.get("start", 0))
        q = round(s / 0.25) * 0.25
        devs.add(int(round(abs(s - q) * tpqn)))
    dnodr = len(devs) / tpqn * 100.0
    lvl, cls = nomml_level([dict(n) for n in notes])
    return {"dnvr": round(dnvr, 3), "dnvr_floor": 40.965,
            "dnodr": round(dnodr, 3), "dnodr_floor": 4.175,
            "nomml": lvl, "class": cls,
            "mechanical": bool(dnvr < 40.965 and dnodr < 4.175
                               and cls == "mechanical")}


# ------------------------------------------- R-13 kinematic final ritard
def final_ritard(song, genre="", v_end=0.68, q=2.5, over_beats=None):
    """Append tempoMap rows for the last phrase: v(x)=[1+(v_end^q-1)x]^(1/q)
    (Friberg/Sundberg kinematic stop). Genre-gated: EDM/hiphop get none.
    Returns the rows added (caller decides to save)."""
    pol = expression_policy(genre)
    if pol["rubato"] <= 0:
        return []
    bpm = float(song.get("bpm", 120) or 120)
    bars = float(song.get("lengthBars", 8) or 8)
    span = over_beats if over_beats else 8.0
    start_bar = max(bars - span / 4.0, 0.0)
    rows = song.setdefault("tempoMap", [])
    added = []
    steps = 6
    for i in range(steps + 1):
        x = i / steps
        v = (1.0 + (v_end ** q - 1.0) * x) ** (1.0 / q)
        row = {"bar": round(start_bar + x * span / 4.0 + 1.0, 3),
               "bpm": round(bpm * v, 2), "curve": 0}
        rows.append(row)
        added.append(row)
    return added


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
