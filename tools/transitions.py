#!/usr/bin/env python3
"""TRANSITIONS — the glue between sections (risers, impacts), placed by the map.

  transitions.py <song> [--track riser] [--impacts] [--preroll 2] [--write]

The section-aware harmonize made parts BREATHE; this makes the seams CONNECT.
Reading the song's sections[], it finds every boundary INTO a high-energy
section (drop/chorus/main/peak/finale) and:
  - RISER: a bandpass-swept noise build in the `preroll` bars before the drop,
    sweeping up to land exactly on the downbeat (riser voice: sweep=bars,
    freq=start, late-bloom gain env)
  - IMPACT (optional): a single low boom ON the drop downbeat (sub sine, fast)

Universal in electronic/pop; gated on the song actually having drop/build-type
labels so it never risers a jazz ballad. Battery: risers land bar-exact at
boundaries and a render shows rising energy into each drop.
"""
import argparse, json, os, re, sys
import songname

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HIGH = ("drop", "chorus", "main", "peak", "finale", "hook")
LOWERS = ("break", "breakdown", "intro", "outro", "quiet", "verse")


DRUMISH = ("kick", "snare", "hat", "perc", "clap", "drum", "808", "impact", "riser")


def _busiest_melodic(song, start_bar, end_bar):
    """the track with the most notes in [start_bar,end_bar) that isn't a drum —
    the one worth filtering out (the lead/pad carries the energy that drains)."""
    best, best_n = None, 0
    for t in song.get("tracks", []):
        nm = str(t.get("name", "")).lower()
        if any(d in nm for d in DRUMISH):
            continue
        n = sum(1 for x in t.get("notes", []) if start_bar * 4 <= x.get("start", 0) < end_bar * 4)
        if n > best_n:
            best, best_n = t, n
    return best


def _downlifter(song, out_track, boundary_bar, preroll, bpm):
    """close an fx_filter cutoff on out_track over the `preroll` bars into the
    boundary — 'filter the section out into the break'. Adds fx_filter if absent."""
    fx = out_track.setdefault("fx", [])
    idx = next((i for i, f in enumerate(fx) if f.get("id") == "fx_filter"), None)
    if idx is None:
        fx.insert(0, {"id": "fx_filter", "params": {"cutoff": 18000, "res": 0.9}})
        idx = 0
    a = (boundary_bar - preroll) * 4.0
    b = boundary_bar * 4.0
    out_track.setdefault("automation", []).append({
        "target": f"fx[{idx}].cutoff",
        "points": [{"beat": round(a, 4), "v": 18000, "curve": -0.6},   # early-jump close
                   {"beat": round(b, 4), "v": 420}]})
    return out_track.get("name", "?"), idx


def _snare_track(song):
    for t in song.get("tracks", []):
        nm = str(t.get("name", "")).lower()
        if "snare" in nm or "clap" in nm:
            return t
    return None


def _fill(song, drop_bar):
    """an accelerating snare roll in the last bar before the drop: 8ths -> 16ths ->
    32nds with a velocity crescendo, landing the last hit just before the downbeat."""
    sn = _snare_track(song)
    if sn is None or not sn.get("notes"):
        return None
    pitch = sn["notes"][0]["pitch"]
    fill_bar = drop_bar - 1
    if fill_bar < 0:
        return None
    # remove any existing snare notes IN the fill bar (the roll replaces them)
    sn["notes"] = [n for n in sn["notes"]
                   if not (fill_bar * 4 <= n["start"] < drop_bar * 4)]
    b0 = fill_bar * 4.0
    subdiv = [0.5] * 2 + [0.25] * 4 + [0.125] * 8       # 2 eighths, 4 16ths, 8 32nds
    t = b0
    added = 0
    for i, step in enumerate(subdiv):
        if t >= drop_bar * 4.0:
            break
        vel = round(0.45 + 0.5 * (i / len(subdiv)), 3)   # crescendo into the drop
        sn["notes"].append({"start": round(t, 4), "len": round(step * 0.85, 4),
                            "pitch": pitch, "vel": vel})
        t += step
        added += 1
    sn["notes"].sort(key=lambda n: n["start"])
    return (sn.get("name", "?"), added)


def transitions(song, riser_track="riser", impacts=False, preroll=2.0, downlifters=False,
                fills=False):
    secs = sorted(song.get("sections", []), key=lambda s: float(s["startBar"]))
    if len(secs) < 2:
        raise SystemExit("no sections to transition between (need sections[])")
    bpm = float(song.get("bpm", 120))
    labels = [str(s.get("name", "")).lower() for s in secs]
    if not any(any(h in l for h in HIGH) for l in labels):
        raise SystemExit("no high-energy sections (drop/chorus/...) — risers would "
                         "not suit this arrangement")
    riser_notes, impact_notes, placed, fill_reports = [], [], [], []
    for i, sc in enumerate(secs):
        label = labels[i]
        if not any(h in label for h in HIGH):
            continue
        # only riser INTO a lift (prev section is lower-energy, or it's the 1st drop)
        prev = labels[i - 1] if i > 0 else ""
        if i > 0 and any(h in prev for h in HIGH):
            continue                                    # drop->drop: no build needed
        drop_bar = float(sc["startBar"])
        if drop_bar < preroll:
            continue
        start_beat = (drop_bar - preroll) * 4.0
        # riser: one note, freq low, sweep = preroll in seconds, lands on downbeat
        sweep_s = preroll * 4.0 * 60.0 / bpm
        riser_notes.append({"start": round(start_beat, 4),
                            "len": round(preroll * 4.0, 4), "pitch": 60, "vel": 0.9,
                            "source_params": {"sweep": round(sweep_s, 2)}})
        if impacts:
            impact_notes.append({"start": round(drop_bar * 4.0, 4), "len": 1.0,
                                 "pitch": 24, "vel": 1.0})
        if fills:
            f = _fill(song, drop_bar)
            if f:
                fill_reports.append((f[0], int(drop_bar), f[1]))
        placed.append((sc.get("name", ""), int(drop_bar) + 1))

    # DOWNLIFTERS: filter-close at every high->low boundary (drop->break/outro)
    dls = []
    if downlifters:
        for i in range(len(secs) - 1):
            if any(h in labels[i] for h in HIGH) and any(l in labels[i + 1] for l in LOWERS):
                out_bar = float(secs[i]["startBar"])
                bnd = float(secs[i + 1]["startBar"])
                if bnd - preroll < out_bar:
                    continue
                tr = _busiest_melodic(song, out_bar, bnd)
                if tr:
                    dls.append(_downlifter(song, tr, bnd, preroll, bpm)
                               + (secs[i + 1].get("name", ""), int(bnd) + 1))

    if not riser_notes and not dls:
        raise SystemExit("no lift or drain boundaries found")
    if not riser_notes:
        return {"risers": 0, "impacts": 0, "downlifters": len(dls),
                "at": placed, "drains": [(d[0], d[3]) for d in dls]}
    # riser voice takes ONE sweep zone per track; per-note sweep varies via automation
    # instead — keep it simple: a track of riser hits, uniform sweep = preroll.
    song["tracks"] = [t for t in song.get("tracks", []) if t.get("name") != riser_track]
    song["tracks"].append({
        "name": riser_track, "source": {"kind": "faust", "id": "riser",
        "params": {"sweep": round(preroll * 4.0 * 60.0 / bpm, 2), "range": 20, "freq": 200}},
        "gainDb": -9, "pan": 0.0,
        "notes": [{k: v for k, v in n.items() if k != "source_params"} for n in riser_notes]})
    if impacts and impact_notes:
        song["tracks"] = [t for t in song["tracks"] if t.get("name") != "impact"]
        song["tracks"].append({"name": "impact",
            "source": {"kind": "faust", "id": "bass_warm"},
            "gainDb": -6, "pan": 0.0, "notes": impact_notes})
    return {"risers": len(riser_notes), "impacts": len(impact_notes) if impacts else 0,
            "downlifters": len(dls), "fills": len(fill_reports), "at": placed,
            "drains": [(d[0], d[3]) for d in dls]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--track", default="riser")
    ap.add_argument("--impacts", action="store_true")
    ap.add_argument("--downlifters", action="store_true", help="filter-close the outgoing track into breaks")
    ap.add_argument("--fills", action="store_true", help="accelerating snare roll before each drop")
    ap.add_argument("--preroll", type=float, default=2.0, help="build-up length in bars")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    name = songname.resolve(a.song)
    path = os.path.join(ROOT, "songs", f"{name}.json")
    song = json.load(open(path))
    rep = transitions(song, a.track, a.impacts, a.preroll, a.downlifters, a.fills)
    if a.write:
        json.dump(song, open(path, "w"), indent=1)
        rep["written"] = f"songs/{name}.json"
    print(f"[transitions] {rep['risers']} risers"
          + (f" + {rep['impacts']} impacts" if a.impacts else "")
          + (f" + {rep['downlifters']} downlifters" if rep.get('downlifters') else "")
          + (f" + {rep['fills']} fills" if rep.get('fills') else "")
          + " into: " + ", ".join(f"{n}@bar{b}" for n, b in rep["at"])
          + (" | drain: " + ", ".join(f"{t}@bar{b}" for t, b in rep.get("drains", [])) if rep.get("drains") else "")
          + (f" -> {rep['written']}" if a.write else " (dry-run; --write to keep)"))
    print("TRANSITIONS_JSON " + json.dumps({k: v for k, v in rep.items() if k != "at"}))


if __name__ == "__main__":
    main()
