#!/usr/bin/env python3
"""THE FLOW COURT — no song ships with holes (wave 49, Chezy decree
2026-07-16: "PEER MODELS MAKE SONGS WITH HOLES! NO FLOW THROUGHPUT!").

The crime, seen live on untitled_54 (Haiku 4.5): duplicate_bars +
clear_bars carving left FULL-BAND DEAD AIR — interior bars where NOTHING
sounds on any unmuted lane. A breakdown keeps something breathing (a pad,
a voice, a riser); a hole is silence wearing a song's name. Zero-token,
model-independent, symbolic (pre-render).

  coverage(song)        per-beat "something sounds" map + per-bar occupancy
  court_flow(song)      convictions: dead_air holes (>=2 interior bars, or
                        a 1-bar gap that does NOT resolve into a downbeat);
                        advisory: stutter_flow (>=3 pardoned 1-bar cuts)
  heal_flow(song, v)    bridge each hole from the song's OWN material:
                        the least-dense sustained lane sounding at the
                        hole's edge tiles across it at reduced velocity
                        (pre-echo of the incoming bar when nothing
                        precedes). Bounded, deterministic, proposals only.

THE PARDON (real music law): the classic 1-bar CUT before a drop is
legal — full silence that resolves into a note ON the next downbeat.
Anything longer is dead air: energy leaves and nothing carries the ear
across. Leading/trailing silence never convicts (THE WORLD GROWS: tails
and pre-rolls are by design).
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_SUSTAIN_WORDS = ("pad", "keys", "chord", "string", "bass", "sub",
                  "drone", "atmo", "texture", "organ", "choir", "vox",
                  "vocal", "lead")


def _beats_per_bar(song):
    try:
        return max(int((song or {}).get("beatsPerBar", 4) or 4), 1)
    except Exception:
        return 4


def _sounding_tracks(song):
    out = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        if (t.get("notes") or t.get("audioClips")):
            out.append(t)
    return out


def coverage(song):
    """Per-beat boolean 'something sounds' + per-bar occupancy 0..1."""
    bpb = _beats_per_bar(song)
    bars = int((song or {}).get("lengthBars", 0) or 0)
    total = max(bars * bpb, 1)
    beat = [0.0] * total

    def mark(a, b):
        a = max(int(math.floor(a)), 0)
        b = min(int(math.ceil(b)), total)
        for i in range(a, b):
            beat[i] = 1.0

    for t in _sounding_tracks(song):
        for n in t.get("notes") or []:
            if not isinstance(n, dict):
                continue
            try:
                s = float(n.get("start", 0))
                ln = max(float(n.get("len", 0) or 0), 0.25)
            except Exception:
                continue
            mark(s, s + ln)
        for c in t.get("audioClips") or []:
            if not isinstance(c, dict):
                continue
            try:
                s = float(c.get("startBeat", 0))
                ln = float(c.get("lengthBeats", 0) or 0)
            except Exception:
                continue
            # lengthBeats absent/0 = engine derives from the FILE — the
            # symbolic court can't know it, and courts convict only the
            # provable: unknown length covers to song end (DJ decks;
            # in dubio pro reo — dj_listener owns the audio-domain truth)
            mark(s, s + ln if ln > 0 else total)
    occ = [sum(beat[b * bpb:(b + 1) * bpb]) / bpb
           for b in range(max(bars, 0))]
    return {"beat": beat, "bar_occupancy": occ, "beats_per_bar": bpb}


def _holes(occ, first, last):
    """Maximal runs of fully-silent bars strictly inside [first, last]."""
    runs, b = [], first
    while b <= last:
        if occ[b] <= 0.0:
            e = b
            while e + 1 <= last and occ[e + 1] <= 0.0:
                e += 1
            runs.append((b, e))
            b = e + 1
        else:
            b += 1
    return runs


def court_flow(song):
    cov = coverage(song)
    occ = cov["bar_occupancy"]
    bpb = cov["beats_per_bar"]
    alive = [i for i, v in enumerate(occ) if v > 0.0]
    if not alive:
        return {"court": "flow", "ok": True, "convictions": [],
                "advisories": [], "skipped": "no sounding material"}
    first, last = alive[0], alive[-1]
    convictions, pardoned = [], []
    for b0, b1 in _holes(occ, first, last):
        span = b1 - b0 + 1
        # the pre-drop CUT: exactly one bar, resolving into a note on
        # the very next downbeat
        nxt = (b1 + 1) * bpb
        resolves = (nxt < len(cov["beat"]) and cov["beat"][nxt] > 0.0)
        if span == 1 and resolves:
            pardoned.append(b0)
            continue
        convictions.append({
            "kind": "dead_air", "fromBar": b0, "toBar": b1 + 1,
            "bars": span,
            "why": (f"bars {b0}-{b1 + 1}: NOTHING sounds on any lane for "
                    f"{span} bar{'s' if span > 1 else ''} mid-song — a "
                    "breakdown keeps something breathing; this is a hole. "
                    "Flow dies where every lane stops at once.")})
    advisories = []
    if len(pardoned) >= 3:
        advisories.append({
            "kind": "stutter_flow", "bars": pardoned,
            "why": (f"{len(pardoned)} separate 1-bar full cuts "
                    f"(bars {pardoned}) — each is legal alone (the cut "
                    "before the drop) but stacked they read as stutter, "
                    "not flow. Keep one, bridge the rest.")})
    return {"court": "flow", "ok": not convictions,
            "convictions": convictions, "advisories": advisories,
            "first_bar": first, "last_bar": last,
            "occupancy": [round(v, 2) for v in occ]}


def _bar_notes(track, bar, bpb):
    a, b = bar * bpb, (bar + 1) * bpb
    out = []
    for n in track.get("notes") or []:
        try:
            s = float(n.get("start", 0))
        except Exception:
            continue
        if a <= s < b:
            out.append(n)
    return out


def _donor_for(song, b0, b1, bpb):
    """The lane that carries the bridge: sounding at the hole's leading
    edge, sustained-family preferred, LEAST dense (subtlest floor).
    Nothing before -> the incoming bar's lane (pre-echo)."""
    cands = []
    for t in _sounding_tracks(song):
        if not t.get("notes"):
            continue  # audio lanes never tile (no beat-safe copy)
        notes = _bar_notes(t, b0 - 1, bpb)
        if notes:
            nm = str(t.get("name", "")).lower()
            sus = any(w in nm for w in _SUSTAIN_WORDS)
            cands.append((0 if sus else 1, len(notes), t, b0 - 1, 0.75))
    if not cands:
        for t in _sounding_tracks(song):
            if not t.get("notes"):
                continue
            notes = _bar_notes(t, b1 + 1, bpb)
            if notes:
                nm = str(t.get("name", "")).lower()
                sus = any(w in nm for w in _SUSTAIN_WORDS)
                cands.append((0 if sus else 1, len(notes), t, b1 + 1, 0.6))
    if not cands:
        return None
    cands.sort(key=lambda c: (c[0], c[1], str(c[2].get("name", ""))))
    _, _, track, src_bar, vel_scale = cands[0]
    return track, src_bar, vel_scale


def heal_flow(song, verdict=None):
    """Bridge every convicted hole from the song's own material. The
    hole span is empty by definition — nothing to overwrite, hand work
    sacred by construction."""
    v = verdict or court_flow(song)
    bpb = _beats_per_bar(song)
    actions = []
    for c in v.get("convictions", []):
        if c.get("kind") != "dead_air":
            continue
        b0, b1 = int(c["fromBar"]), int(c["toBar"]) - 1
        donor = _donor_for(song, b0, b1, bpb)
        if donor is None:
            actions.append({"kind": "flow_bridge_skipped",
                            "fromBar": b0, "toBar": b1 + 1,
                            "why": "no MIDI lane sounds at either edge"})
            continue
        track, src_bar, vel_scale = donor
        src = _bar_notes(track, src_bar, bpb)
        added = 0
        for bar in range(b0, b1 + 1):
            shift = (bar - src_bar) * bpb
            for n in src:
                nn = dict(n)
                nn["start"] = round(float(n.get("start", 0)) + shift, 4)
                # never spill past the hole's end into sounding land
                end_cap = (b1 + 1) * bpb
                ln = max(float(n.get("len", 0) or 0), 0.25)
                nn["len"] = round(min(ln, max(end_cap - nn["start"],
                                              0.25)), 4)
                try:
                    nn["vel"] = max(int(round(
                        float(n.get("vel", 96)) * vel_scale)), 1)
                except Exception:
                    pass
                track["notes"].append(nn)
                added += 1
        track["notes"].sort(key=lambda x: float(x.get("start", 0)))
        actions.append({
            "kind": "flow_bridge", "fromBar": b0, "toBar": b1 + 1,
            "lane": track.get("name"), "notes_added": added,
            "why": (f"bridged bars {b0}-{b1 + 1} with "
                    f"'{track.get('name')}' tiled from bar {src_bar} at "
                    f"vel x{vel_scale} — the floor carries through; "
                    "restyle it, never re-silence it")})
    return actions


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE FLOW COURT (wave 49)")
    ap.add_argument("song")
    ap.add_argument("--heal", action="store_true")
    a = ap.parse_args()
    song = json.load(open(a.song))
    v = court_flow(song)
    if a.heal and v.get("convictions"):
        v["healed"] = heal_flow(song, v)
        json.dump(song, open(a.song, "w"), indent=1)
        v["re_court"] = {"ok": court_flow(song)["ok"]}
    v.pop("occupancy", None)
    print(json.dumps(v, indent=1))
