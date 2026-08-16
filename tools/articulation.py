#!/usr/bin/env python3
"""ARTICULATIONS — wave 74 (r-26 item 161): the string/orchestral
articulation vocabulary as deterministic lane ops.

Two halves, both symbolic:
  (1) ENVELOPE PRESETS — attack/release zone targets per articulation
      (spiccato 5ms, staccato 8ms, marcato 15ms, legato 120ms, sustain
      200ms, sfz 3ms, swell 500ms rise) + note-length shaping
      (staccato plays 40% of written, legato touches the next note).
  (2) THE RENDER OFFSET — every articulation carries its measured
      attack latency; notes shift EARLIER by it (legato -110ms,
      spiccato/staccato -60ms, pizz -50ms) so the heard attack lands
      ON the grid. This alone removes the 'MIDI mockup' lag for free —
      it is exactly what mockup pros do by hand.

  apply_articulation(song, track_name, art, from_bar=None, to_bar=None)
      sets source.params (only when the voice exposes the zones),
      shapes lengths, shifts starts, stamps the marker. Idempotent per
      (lane, art) via the marker. Returns the edit ledger.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTR = os.path.join(ROOT, "instruments")

#           attack_s  release_s len_scale offset_ms
ARTICULATIONS = {
    "spiccato": (0.005, 0.06, 0.30, -60.0),
    "staccato": (0.008, 0.08, 0.40, -60.0),
    "marcato":  (0.015, 0.15, 0.75, -40.0),
    "legato":   (0.120, 0.25, 1.02, -110.0),
    "sustain":  (0.200, 0.40, 0.95, -80.0),
    "pizzicato": (0.004, 0.12, 0.25, -50.0),
    "sfz":      (0.003, 0.20, 0.60, -30.0),
    "swell":    (0.500, 0.60, 1.00, 0.0),
}


def _voice_zones(voice_id):
    p = os.path.join(INSTR, f"{voice_id}.dsp")
    try:
        src = open(p).read()
    except Exception:
        return set()
    return set(re.findall(r"hslider\s*\(\s*\"(\w+)\"", src))


def apply_articulation(song, track_name, art, from_bar=None, to_bar=None):
    if art not in ARTICULATIONS:
        return [{"kind": "error",
                 "why": f"unknown articulation '{art}' — "
                        f"{sorted(ARTICULATIONS)}"}]
    att, rel, len_scale, off_ms = ARTICULATIONS[art]
    t = next((x for x in (song or {}).get("tracks", []) or []
              if isinstance(x, dict) and x.get("name") == track_name),
             None)
    if t is None:
        return [{"kind": "error", "why": f"no track '{track_name}'"}]
    if t.get("articulation") == art:
        return []                                   # idempotent
    bpm = float((song or {}).get("bpm", 120) or 120)
    off_beats = off_ms / 60000.0 * bpm
    a_beat = (from_bar or 0) * 4.0
    b_beat = (to_bar * 4.0) if to_bar is not None else float("inf")
    edits = []
    src = t.get("source") or {}
    zones = _voice_zones(str(src.get("id", "")))
    landed_zones = {}
    if "attack" in zones:
        src.setdefault("params", {})["attack"] = att
        landed_zones["attack"] = att
    if "release" in zones:
        src.setdefault("params", {})["release"] = rel
        landed_zones["release"] = rel
    notes = sorted((n for n in t.get("notes") or []),
                   key=lambda n: float(n.get("start", 0)))
    shaped = shifted = 0
    for i, n in enumerate(notes):
        s = float(n.get("start", 0))
        if not (a_beat <= s < b_beat):
            continue
        ln = float(n.get("len", 0.25) or 0.25)
        if art == "legato" and i + 1 < len(notes):
            nxt = float(notes[i + 1].get("start", 0))
            if 0 < nxt - s <= 8.0:
                n["len"] = round((nxt - s) * len_scale, 4)
                shaped += 1
        else:
            n["len"] = round(max(ln * len_scale, 0.05), 4)
            shaped += 1
        n["start"] = round(max(s + off_beats, 0.0), 4)
        shifted += 1
    t["articulation"] = art
    t["articulation_offset_ms"] = off_ms
    edits.append({"kind": "articulation", "track": track_name,
                  "articulation": art, "zones": landed_zones,
                  "notes_shaped": shaped, "notes_shifted": shifted,
                  "offset_ms": off_ms,
                  "why": (f"'{track_name}' plays {art}: "
                          + (f"attack {att * 1000:.0f}ms/release "
                             f"{rel * 1000:.0f}ms, " if landed_zones
                             else "voice exposes no env zones "
                                  "(length/offset only), ")
                          + f"lengths x{len_scale}, notes pulled "
                          f"{-off_ms:.0f}ms early so the heard attack "
                          "lands ON the grid — the mockup-lag killer")})
    return edits


GLIDE_VOICES = ("lead_legato", "sub_808_slide")


def legato_ties(song, track_name, glide_ms=60):
    """W77 (r-26 item 162): TRUE legato — consecutive notes on the lane
    are tied into OVERLAPS (0.08-beat cross), and the lane must ride a
    glide voice (mono freq slew: the engine holds the gate through the
    overlap, the destination attack never retriggers — engine-proven
    66.7->83.3->100Hz through a join). Swaps the source to lead_legato
    when the current voice cannot glide (the swap is the point — a
    retriggering voice cannot speak legato). Mutates; returns ledger."""
    t = next((x for x in (song or {}).get("tracks", []) or []
              if isinstance(x, dict) and x.get("name") == track_name),
             None)
    if t is None:
        return [{"kind": "error", "why": f"no track '{track_name}'"}]
    if t.get("legato_tied"):
        return []
    notes = sorted((n for n in t.get("notes") or []),
                   key=lambda n: float(n.get("start", 0)))
    if len(notes) < 2:
        return []
    tied = 0
    for a, b in zip(notes, notes[1:]):
        sa, sb = float(a.get("start", 0)), float(b.get("start", 0))
        end_a = sa + float(a.get("len", 0.25) or 0.25)
        gap = sb - end_a
        if -0.5 <= gap <= 1.0:            # phrase-internal join
            a["len"] = round(sb - sa + 0.08, 4)
            tied += 1
    src_id = str((t.get("source") or {}).get("id", ""))
    swapped = None
    if src_id not in GLIDE_VOICES:
        swapped = src_id or "(none)"
        t["source"] = {"id": "lead_legato",
                       "params": {"glide": float(glide_ms)}}
    else:
        t.setdefault("source", {}).setdefault("params", {})["glide"] =             float(glide_ms)
    t["legato_tied"] = True
    return [{"kind": "legato_ties", "track": track_name, "tied": tied,
             "glide_ms": glide_ms,
             **({"voice_swapped_from": swapped} if swapped else {}),
             "why": (f"'{track_name}': {tied} joins tied into overlaps"
                     + (f", voice swapped {swapped} -> lead_legato "
                        "(a retriggering voice cannot speak legato)"
                        if swapped else "")
                     + f" — mono glide {glide_ms}ms carries the phrase, "
                     "destination attacks never retrigger")}]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="ARTICULATIONS (w74)")
    ap.add_argument("song")
    ap.add_argument("track")
    ap.add_argument("articulation",
                    choices=sorted(ARTICULATIONS) + ["true_legato"])
    ap.add_argument("--from-bar", type=int, default=None)
    ap.add_argument("--to-bar", type=int, default=None)
    a = ap.parse_args()
    song = json.load(open(a.song))
    if a.articulation == "true_legato":
        eds = legato_ties(song, a.track)
    else:
        eds = apply_articulation(song, a.track, a.articulation,
                                 a.from_bar, a.to_bar)
    if eds and eds[0].get("kind") != "error":
        json.dump(song, open(a.song, "w"), indent=1)
    print(json.dumps(eds, indent=1))
