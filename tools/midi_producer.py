#!/usr/bin/env python3
"""THE PORTABLE SCORE — producer-grade MIDI normalisation (song.json -> song.json).

Chezy 2026-08-03: "THEYRE ALL WAVY, NOT NORMALISED, IF I EXPORT THE .MID FILE
AND PUT IT IN ANY OTHER GENERIC DAW, IT SOUNDS BAD AND MESSY AS FUCK! IT
NEEDS TO BE NORMALISED WITH A PRODUCERS AWARENESS ... BY THE BOOK ... SO EVEN
IF I EXPORT .MID IN A GENERIC DAW WITH GENERIC INSTS, IT WILL NOTICEBLY STILL
BE THE SAME ORIGINAL SONG, AUDIBLE AND PLAUSIBLE TO ALL!"

Measured conviction (hourglass import, the complaint's own specimen):
vocals_sketch 667 notes / 59% wavy-pairs / 102ms median (vibrato shattered
into semitone confetti); guitar_lead + piano_lead velocity MEDIAN 0.05 —
the a2m sampler-dB refit writes OUR sampler's calibration into vel, which a
generic DAW plays as silence-and-slam; Kick 49% near-retriggers; and
export_midi emitted no program changes (everything lands as grand piano).

This kernel is a PROJECTION: export-time by default (the in-DAW lanes keep
the record-matched truth the a2m courts tuned), lane-side later behind a
re-render court. Passes, in producer order:

  dewave      cross-pitch fragment runs (vibrato/slides) -> sustained notes
  degun       same-pitch machine-gun retriggers -> the stronger hit
  pocket      partial-strength grid pull (feel kept, slop gone)
  gate        mono roles: overlap trim + legato; poly: voice cap
  density     per-bar salience ceiling (mush guard on generic playback)
  produce_velocity  monotone percentile remap into musical MIDI range
                    (rank + accent structure preserved, never flattened)
  GM identity drum pitches -> core GM map; melodic programs by lane name

Everything is pure + deterministic; produce() returns (song', receipts).
Battery: tools/midi_producer_battery.py.
"""
import copy
import json
import math
import os
import sys

# ------------------------------------------------------------------ roles
DRUM_LANES = ("kick", "snare", "hat", "perc", "cymbal", "tom")

# GM programs by lane family (0-based). Conservative "plausible to all"
# picks: real-instrument families keep their instrument, synth leads saw.
GM_PROGRAM = (
    ("bass", 33),        # Fingered Bass
    ("guitar", 26),      # Jazz/clean electric
    ("piano", 0),        # Acoustic Grand
    ("keys", 4),         # E.Piano 1
    ("vocals", 52),      # Choir Aahs
    ("string", 48),      # String Ensemble
    ("pad", 89),         # Warm Pad
    ("other_lead", 81),  # Saw Lead (synth lead family)
    ("other", 0),        # harmonic bed -> piano
)

# Our source-kit alt voices -> core GM drum pitches every GM module voices.
DRUM_GM_REMAP = {26: 46, 33: 35, 34: 38, 41: 42, 44: 42}


def role_of(name):
    n = str(name or "").lower()
    if any(n.startswith(d) for d in DRUM_LANES):
        return "drum"
    if n.startswith("bass"):
        return "bass"
    if n.startswith("vocal"):
        return "vocal"
    if n.endswith("_chords"):
        return "chords"
    if n.endswith("_lead"):
        return "lead"
    return "melodic"


def program_of(name):
    n = str(name or "").lower()
    for key, prog in GM_PROGRAM:
        if n.startswith(key) or n == key:
            return prog
    return 0


def _srt(ns):
    return sorted(ns, key=lambda x: (float(x["start"]), int(x["pitch"])))


# ------------------------------------------------------------------ passes
def dewave(ns, max_gap=0.12, max_len=0.35, max_dp=2, min_run=3):
    """Collapse WAVY runs — consecutive short notes hugging one pitch line
    (vibrato / slide fragments from f0-following transcription) — into ONE
    sustained note at the duration-weighted median pitch. Real melodic
    motion (larger intervals, longer notes) never clusters, so it survives."""
    ns = _srt(ns)
    out, run = [], []

    def flush():
        if len(run) >= min_run:
            tot = sum(float(m["len"]) for m in run) or 1e-9
            acc, target = 0.0, tot / 2
            pitch = int(run[-1]["pitch"])
            for m in sorted(run, key=lambda m: int(m["pitch"])):
                acc += float(m["len"])
                if acc >= target:
                    pitch = int(m["pitch"])
                    break
            start = float(run[0]["start"])
            end = max(float(m["start"]) + float(m["len"]) for m in run)
            vel = sorted(float(m.get("vel", 0.8)) for m in run)
            out.append({**run[0], "start": round(start, 3),
                        "len": round(end - start, 3), "pitch": pitch,
                        "vel": round(vel[max(0, int(len(vel) * 0.9) - 1)], 3)})
        else:
            out.extend(run)
        run.clear()

    for n in ns:
        if not run:
            run.append(n)
            continue
        prev = run[-1]
        gap = float(n["start"]) - (float(prev["start"]) + float(prev["len"]))
        # chain on the RUNNING pitch (drifting melisma walks semitone by
        # semitone) with a total-span guard so a real scale line survives
        span_lo = min(int(m["pitch"]) for m in run)
        span_hi = max(int(m["pitch"]) for m in run)
        p = int(n["pitch"])
        if (gap < max_gap and float(n["len"]) < max_len
                and float(prev["len"]) < max_len
                and abs(p - int(prev["pitch"])) <= max_dp
                and (max(span_hi, p) - min(span_lo, p)) <= 4):
            run.append(n)
        else:
            flush()
            run.append(n)
    flush()
    # second stage: same-pitch fragment merge (the stutter dewave leaves)
    merged = []
    for n in _srt(out):
        if merged:
            p = merged[-1]
            gap = float(n["start"]) - (float(p["start"]) + float(p["len"]))
            if (int(p["pitch"]) == int(n["pitch"]) and gap < max_gap
                    and float(p["len"]) < 0.6 and float(n["len"]) < 0.6):
                p = dict(p)
                p["len"] = round(float(n["start"]) + float(n["len"])
                                 - float(p["start"]), 3)
                p["vel"] = round(max(float(p.get("vel", 0.8)),
                                     float(n.get("vel", 0.8))), 3)
                merged[-1] = p
                continue
        merged.append(dict(n))
    return _srt(merged)


def degun(ns, min_dt=0.10):
    """Same-pitch retriggers closer than min_dt beats -> keep the stronger
    hit (its length stretched over the pair). Kills machine-gun kicks."""
    ns = _srt(ns)
    out = []
    last_onset = {}                      # pitch -> most recent ABSORBED onset:
    for n in ns:                         # a burst chains 0.06+0.06 even though
        p_pitch = int(n["pitch"])        # note 3 sits 0.12 from the kept note
        if out:
            p = out[-1]
            ref = last_onset.get(p_pitch, float(p["start"]))
            if (int(p["pitch"]) == p_pitch
                    and float(n["start"]) - ref < min_dt):
                keep = dict(p)
                if float(n.get("vel", 0)) > float(p.get("vel", 0)):
                    keep["vel"] = float(n.get("vel", 0))
                keep["start"] = round(float(p["start"]), 3)
                keep["len"] = round(max(
                    float(p["start"]) + float(p["len"]),
                    float(n["start"]) + float(n["len"])) - float(p["start"]), 3)
                out[-1] = keep
                last_onset[p_pitch] = float(n["start"])
                continue
        out.append(n)
        last_onset[p_pitch] = float(n["start"])
    return out


def pocket(ns, strength=0.6, grid=0.25, tol=0.09):
    """Partial-strength grid pull: within tol of a 1/16 line, move
    `strength` of the way there. Feel survives, slop doesn't."""
    out = []
    for n in ns:
        s = float(n["start"])
        q = round(s / grid) * grid
        if abs(q - s) <= tol:
            s = s + strength * (q - s)
        out.append({**n, "start": round(s, 3)})
    return _srt(out)


def gate(ns, mono=True, min_len=0.12, legato_gap=0.5, max_poly=6):
    """Mono roles: trim overlaps, extend true gaps into legato lines, floor
    dust lengths. Poly roles: cap simultaneous voices (drop weakest)."""
    ns = _srt(ns)
    if mono:
        out = []
        for i, n in enumerate(ns):
            n = dict(n)
            if i + 1 < len(ns):
                gap = float(ns[i + 1]["start"]) - float(n["start"])
                if gap <= 0.01:
                    continue                      # chord dust on a mono lane
                ln = float(n["len"])
                if ln > gap - 0.01:
                    ln = gap - 0.01               # overlap trim
                elif gap - ln < legato_gap:
                    ln = max(ln, gap * 0.9)       # legato breath
                n["len"] = round(max(min_len, ln), 3)
            else:
                n["len"] = round(max(min_len, float(n["len"])), 3)
            out.append(n)
        return out
    active, out = [], []
    for n in _srt(ns):
        s = float(n["start"])
        active = [a for a in active
                  if float(a["start"]) + float(a["len"]) > s]
        if len(active) >= max_poly:
            weakest = min(active, key=lambda a: float(a.get("vel", 0)))
            if float(n.get("vel", 0)) <= float(weakest.get("vel", 0)):
                continue
            out.remove(weakest)
            active.remove(weakest)
        out.append(n)
        active.append(n)
    return _srt(out)


def density(ns, cap_per_bar=16, beats_per_bar=4.0):
    """Per-bar salience ceiling: a generic instrument turns overdense bars
    into mush — keep the notes that carry the bar."""
    bars = {}
    for n in _srt(ns):
        bars.setdefault(int(float(n["start"]) // beats_per_bar), []).append(n)
    out = []
    for _b, group in sorted(bars.items()):
        if len(group) > cap_per_bar:
            group = sorted(group, key=lambda n: -(float(n.get("vel", 0))
                                                  + 0.5 * float(n["len"])))
            group = group[:cap_per_bar]
        out.extend(group)
    return _srt(out)


VEL_BAND = {"drum:kick": (0.75, 0.95), "drum:snare": (0.72, 0.92),
            "drum:hat": (0.45, 0.75), "drum:perc": (0.50, 0.80),
            "drum:cymbal": (0.60, 0.85), "drum:tom": (0.60, 0.88),
            "bass": (0.55, 0.90), "vocal": (0.50, 0.90),
            "chords": (0.45, 0.80), "lead": (0.50, 0.90),
            "melodic": (0.45, 0.88)}


def produce_velocity(ns, role, lane_name=""):
    """Monotone percentile remap into a musical MIDI band: p15->band_lo,
    p85->band_hi, clamped band_lo-0.15 .. band_hi+0.05. Rank order (the
    accent STRUCTURE) is preserved exactly; only the calibration moves.
    Near-constant lanes sit at band middle; hat lanes get the offbeat dip."""
    if not ns:
        return ns
    band = VEL_BAND.get(role)
    if role == "drum":
        piece = next((d for d in DRUM_LANES
                      if str(lane_name).lower().startswith(d)), "perc")
        band = VEL_BAND.get(f"drum:{piece}", (0.5, 0.85))
    lo_out, hi_out = band or (0.45, 0.88)
    vels = sorted(float(n.get("vel", 0.8)) for n in ns)
    p15 = vels[max(0, int(len(vels) * 0.15) - 1)]
    p85 = vels[min(len(vels) - 1, int(len(vels) * 0.85))]
    out = []
    flat = (p85 - p15) < 0.05
    for n in ns:
        v = float(n.get("vel", 0.8))
        if flat:
            nv = (lo_out + hi_out) / 2
        else:
            t = (v - p15) / (p85 - p15)
            nv = lo_out + t * (hi_out - lo_out)
        nv = max(lo_out - 0.15, min(hi_out + 0.05, nv))
        if role == "drum" and str(lane_name).lower().startswith("hat"):
            if int(round(float(n["start"]) * 2)) % 2 == 1:
                nv -= 0.12                        # offbeat hats breathe
        out.append({**n, "vel": round(max(0.20, min(0.98, nv)), 3)})
    return out


# ------------------------------------------------------------------ produce
POCKET_STRENGTH = {"drum": 0.7, "bass": 0.6, "vocal": 0.4, "chords": 0.5,
                   "lead": 0.55, "melodic": 0.55}


def _wavy_pairs(ns):
    ns = _srt(ns)
    c = 0
    for a, b in zip(ns, ns[1:]):
        if (abs(int(b["pitch"]) - int(a["pitch"])) <= 2
                and float(b["start"]) - (float(a["start"]) + float(a["len"])) < 0.25
                and float(a["len"]) < 0.4):
            c += 1
    return c


def produce_track(name, notes):
    """One lane through the producer chain. Returns (notes', receipt)."""
    role = role_of(name)
    before = {"notes": len(notes), "wavy": _wavy_pairs(notes),
              "vel_p50": (sorted(float(n.get("vel", 0.8)) for n in notes)
                          [len(notes) // 2] if notes else 0)}
    ns = [dict(n) for n in notes]
    if role in ("vocal", "bass", "lead", "melodic"):
        ns = dewave(ns)
    if role == "drum":
        # kick/snare machine-guns are transcription doubles; hat/perc ROLLS
        # that fast are music — per-piece thresholds keep the rolls alive
        piece = str(name).lower()
        dt = 0.12 if piece.startswith(("kick", "snare")) else 0.06
        ns = degun(ns, dt)
    else:
        ns = degun(ns, 0.10)
    ns = pocket(ns, POCKET_STRENGTH.get(role, 0.55))
    if role in ("bass", "vocal", "lead"):
        ns = gate(ns, mono=True)
    elif role in ("chords", "melodic"):
        ns = gate(ns, mono=False)
    if role != "drum":
        ns = density(ns, cap_per_bar=16)
    elif str(name).lower().startswith("hat"):
        ns = density(ns, cap_per_bar=20)
    ns = produce_velocity(ns, role, name)
    if role == "drum":
        ns = [{**n, "pitch": DRUM_GM_REMAP.get(int(n["pitch"]),
                                               int(n["pitch"]))} for n in ns]
    after = {"notes": len(ns), "wavy": _wavy_pairs(ns),
             "vel_p50": (sorted(float(n.get("vel", 0.8)) for n in ns)
                         [len(ns) // 2] if ns else 0)}
    return _srt(ns), {"role": role, "before": before, "after": after}


def produce(song):
    """The whole arrangement through the producer chain (pure copy).
    Audio-only lanes and empty lanes pass untouched."""
    song = copy.deepcopy(song)
    receipts = {}
    for t in song.get("tracks", []):
        notes = t.get("notes") or []
        if not notes:
            continue
        t["notes"], receipts[t.get("name", "?")] = produce_track(
            t.get("name", ""), notes)
    return song, receipts


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: midi_producer.py in_song.json out_song.json")
    song = json.load(open(sys.argv[1]))
    out, rec = produce(song)
    json.dump(out, open(sys.argv[2], "w"), indent=1)
    for name, r in rec.items():
        b, a = r["before"], r["after"]
        print(f"{name:22s} {r['role']:8s} {b['notes']:5d}->{a['notes']:5d} "
              f"wavy {b['wavy']:4d}->{a['wavy']:4d} "
              f"vel_p50 {b['vel_p50']:.2f}->{a['vel_p50']:.2f}")


if __name__ == "__main__":
    main()
