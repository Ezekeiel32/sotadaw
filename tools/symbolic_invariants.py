#!/usr/bin/env python3
"""SYMBOLIC INVARIANTS — wave 63 (r-32 item 182): the reference-free
theory metrics only a symbolic DAW can compute. The existing courts
already own scale adherence (court_key), chord-tone ratios
(harmony_court) and progression grammar (court_progression) — one
resolver each; THIS module adds the four that existed nowhere:

  parallel_motion(song)      parallel fifths/octaves between voice pairs
  vl_smoothness(song)        mean semitone motion between adjacent
                             chord-lane voicings (voice-leading cost)
  pitch_entropy(song)        pitch-class histogram entropy (high =
                             unstable tonality, low = drone)
  invariants(song)           the bundle + advisory bands (extremes only)
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _melodic_lanes(song):
    out = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted") or not t.get("notes"):
            continue
        nm = str(t.get("name", "")).lower()
        if any(w in nm for w in ("kick", "snare", "clap", "hat", "perc",
                                 "cym", "tom", "shaker", "crash",
                                 "_sketch", "_identity")):
            continue
        out.append(t)
    return out


def _beat_pitches(track, grid=1.0):
    """beat index -> sorted pitches sounding at that grid point."""
    out = {}
    for n in track.get("notes") or []:
        try:
            s = float(n.get("start", 0))
            p = int(n.get("pitch", 60))
        except Exception:
            continue
        out.setdefault(int(s / grid), []).append(p)
    return {k: sorted(v) for k, v in out.items()}


def parallel_motion(song):
    """Count parallel PERFECT intervals (P5/P8) between the top notes
    of every melodic lane pair moving in the same direction — the
    classical independence breach (advisory: idiomatic in power-chord
    genres; the caller's genre gate decides)."""
    lanes = _melodic_lanes(song)
    count, pairs = 0, 0
    for i in range(len(lanes)):
        for j in range(i + 1, len(lanes)):
            a = _beat_pitches(lanes[i])
            b = _beat_pitches(lanes[j])
            beats = sorted(set(a) & set(b))
            prev = None
            for bt in beats:
                pa, pb = a[bt][-1], b[bt][-1]
                iv = abs(pa - pb) % 12
                if prev is not None:
                    ppa, ppb = prev
                    piv = abs(ppa - ppb) % 12
                    if iv == piv and iv in (0, 7) and pa != ppa and \
                            (pa - ppa) * (pb - ppb) > 0:
                        count += 1
                pairs += 1
                prev = (pa, pb)
    return {"parallel_perfects": count, "moments": pairs}


def vl_smoothness(song):
    """Mean semitone motion between ADJACENT chord voicings on the
    song's chordal lane — <=2.0 = smooth (common tones held), >4 =
    leaping comp."""
    for t in _melodic_lanes(song):
        nm = str(t.get("name", "")).lower()
        if not any(w in nm for w in ("keys", "piano", "chord", "pad",
                                     "rhodes", "organ", "comp")):
            continue
        bars = {}
        for n in t.get("notes") or []:
            try:
                bars.setdefault(int(float(n.get("start", 0)) // 4),
                                []).append(int(n.get("pitch", 60)))
            except Exception:
                continue
        keys = sorted(k for k, v in bars.items() if len(v) >= 2)
        moves = []
        for k1, k2 in zip(keys, keys[1:]):
            va, vb = sorted(bars[k1]), sorted(bars[k2])
            m = min(len(va), len(vb))
            if not m:
                continue
            moves.append(sum(abs(x - y) for x, y in
                             zip(va[-m:], vb[-m:])) / m)
        if moves:
            return {"lane": t.get("name"),
                    "mean_semitone_motion": round(sum(moves) /
                                                  len(moves), 2),
                    "transitions": len(moves)}
    return None


def pitch_entropy(song):
    """Duration-weighted pitch-class entropy in bits (max log2(12) ~
    3.58). >3.3 = unstable tonality; <1.0 = a drone."""
    hist = [0.0] * 12
    for t in _melodic_lanes(song):
        for n in t.get("notes") or []:
            try:
                hist[int(n.get("pitch", 60)) % 12] += \
                    max(float(n.get("len", 0.25) or 0.25), 0.05)
            except Exception:
                continue
    total = sum(hist)
    if total <= 0:
        return None
    ps = [h / total for h in hist if h > 0]
    return round(-sum(p * math.log2(p) for p in ps), 3)


def invariants(song, genre=""):
    g = str(genre or "").lower()
    power_ok = any(w in g for w in ("metal", "punk", "rock", "grunge",
                                    "hardcore"))
    pm = parallel_motion(song)
    vl = vl_smoothness(song)
    ent = pitch_entropy(song)
    advisories = []
    if pm["moments"] >= 24 and pm["parallel_perfects"] > \
            max(6, pm["moments"] * 0.2) and not power_ok:
        advisories.append({
            "kind": "parallel_perfects", **pm,
            "why": (f"{pm['parallel_perfects']} parallel fifth/octave "
                    "moves between lanes — voices moving in lockstep "
                    "perfect intervals collapse into ONE thick voice; "
                    "give a lane contrary or oblique motion (idiomatic "
                    "only in power-chord genres)")})
    if vl and vl["transitions"] >= 6 and vl["mean_semitone_motion"] > 4.0:
        advisories.append({
            "kind": "leaping_comp", **vl,
            "why": (f"'{vl['lane']}' jumps {vl['mean_semitone_motion']}"
                    " semitones per chord change on average — hold the "
                    "common tones; smooth voice leading is what makes "
                    "changes sound intended")})
    if ent is not None and ent > 3.35:
        advisories.append({
            "kind": "unstable_tonality", "entropy_bits": ent,
            "why": (f"pitch-class entropy {ent} bits (max 3.58) — the "
                    "take uses nearly every pitch class equally; "
                    "tonality reads as accidental, not chromatic")})
    return {"court": "symbolic_invariants", "ok": True,
            "advisories": advisories, "parallel": pm,
            "voice_leading": vl, "entropy_bits": ent}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="SYMBOLIC INVARIANTS (w63)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    a = ap.parse_args()
    print(json.dumps(invariants(json.load(open(a.song)), a.genre),
                     indent=1))
