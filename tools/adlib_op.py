#!/usr/bin/env python3
"""THE AD-LIB LANE — the call gets its response (wave 43; R-12 item
130).

r-12: ad-libs are SHORT interjections, 2-3 PER SECTION MAX (more =
mud), panned L/R, often octave-up doubles, heavy verb on the throw.
The vocab lives in the wave-24 VocalTarget table (trap: yeah/uh/skrrt/
gang..., gospel: oh/yeah/hallelujah); THIS op places them: hook
sections, in the GAPS after lead phrases (call-and-response — never on
top of the lead), capped by the genre's adlib_per_section, seeded
rotation, panned alternating +-0.25, -6dB, the lead's own voice as the
proxy until re-sung.

  find_gaps(lead_notes, b0, b1)      phrase-end gaps >= 1 beat
  place_adlibs(song, genre, seed=0)  mutates: the 'adlibs' lane +
                                     lyrics entries; idempotent
  court_adlibs(song, genre)          the MUD CAP: >3 ad-libs landing in
                                     one section = advisory
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_HOOKISH = ("chorus", "drop", "hook", "theme")


def _policy(genre):
    try:
        import kg
        rows = kg.KG().q(
            "MATCH (v:VocalTarget {name: '"
            + str(genre or "").lower().replace("'", "") + "'}) "
            "RETURN v.adlib_vocab, v.adlib_per_section")
        if rows and rows[0][0] is not None:
            vocab = [w for w in str(rows[0][0]).split(",") if w]
            return vocab, int(rows[0][1] or 0)
    except Exception:
        pass
    import kg_seed_vocal as KV
    p = KV.PRESETS[KV.preset_for(genre or "pop")]
    return ([w for w in p["adlib_vocab"].split(",") if w],
            int(p["adlib_per_section"]))


def _lead(song):
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if nm.endswith(("_sketch", "_identity")) or "adlib" in nm:
            continue
        if any(w in nm for w in ("lead", "vocal", "vox", "topline")) \
                and (t.get("notes") or []):
            return t
    return None


def find_gaps(lead_notes, b0, b1, min_gap=1.0):
    """Phrase-end gaps inside [b0, b1): (gap_start, gap_len) after each
    lead phrase (call-and-response — the ad-lib answers, never talks
    over)."""
    ns = sorted((n for n in lead_notes
                 if b0 <= float(n.get("start", 0)) < b1),
                key=lambda n: float(n.get("start", 0)))
    gaps = []
    for a, b in zip(ns, ns[1:]):
        end_a = float(a.get("start", 0)) + float(a.get("len", 0.25))
        gap = float(b.get("start", 0)) - end_a
        if gap >= min_gap:
            gaps.append((round(end_a, 4), round(gap, 4)))
    if ns:
        end_last = float(ns[-1].get("start", 0)) + \
            float(ns[-1].get("len", 0.25))
        if b1 - end_last >= min_gap:
            gaps.append((round(end_last, 4), round(b1 - end_last, 4)))
    return gaps


def place_adlibs(song, genre="", seed=0):
    """Land the ad-lib lane. Idempotent (an existing 'adlibs' lane is
    refreshed). Returns the ledger."""
    vocab, per_sec = _policy(genre)
    if not vocab or per_sec <= 0:
        return []
    lead = _lead(song)
    if lead is None:
        return []
    secs = sorted((s for s in song.get("sections", []) or []
                   if isinstance(s, dict)),
                  key=lambda s: float(s.get("startBar", 0)))
    hooks = []
    for i, s in enumerate(secs):
        if not any(h in str(s.get("name", "")).lower() for h in _HOOKISH):
            continue
        b0 = float(s.get("startBar", 0)) * 4
        b1 = float(secs[i + 1].get("startBar", 1e9)) * 4 \
            if i + 1 < len(secs) else 1e9
        hooks.append((b0, min(b1, float(song.get("lengthBars", 8)) * 4)))
    if not hooks:
        return []
    notes, lyr_rows = [], []
    rot = int(seed or 0)
    lead_pitches = [int(n.get("pitch", 60)) for n in lead["notes"]]
    base_pitch = (sorted(lead_pitches)[len(lead_pitches) // 2]
                  if lead_pitches else 60) + 12       # octave-up idiom
    for b0, b1 in hooks:
        placed = 0
        for gs, gl in find_gaps(lead["notes"], b0, b1):
            if placed >= per_sec:
                break
            word = vocab[rot % len(vocab)]
            rot += 1
            ln = round(min(gl - 0.25, 1.0), 4)
            if ln < 0.4:
                continue
            notes.append({"start": round(gs + 0.125, 4), "len": ln,
                          "pitch": base_pitch, "vel": 0.75})
            lyr_rows.append({"beat": round(gs + 0.125, 4), "text": word})
            placed += 1
    if not notes:
        return []
    tracks = song.setdefault("tracks", [])
    lane = next((t for t in tracks
                 if str(t.get("name", "")) == "adlibs"), None)
    if lane is None:
        lane = {"name": "adlibs"}
        tracks.append(lane)
    lane.update({"notes": notes, "gainDb": -6.0,
                 "pan": 0.25 if (seed or 0) % 2 == 0 else -0.25,
                 "source": copy.deepcopy(lead.get("source") or {}),
                 "stack_of": lead.get("name", "lead")})
    lyr = [l for l in song.get("lyrics", []) or []
           if isinstance(l, dict)
           and not any(abs(float(l.get("beat", 0)) - r["beat"]) < 1e-6
                       for r in lyr_rows)]
    song["lyrics"] = sorted(lyr + lyr_rows,
                            key=lambda l: float(l.get("beat", 0)))
    return [{"kind": "adlibs", "placed": len(notes),
             "vocab": vocab[:3], "pan": lane["pan"]}]


def court_adlibs(song, genre=""):
    """THE MUD CAP (r-12: 2-3 per section MAX): count ad-lib onsets per
    section; >3 advises."""
    lane = next((t for t in (song or {}).get("tracks", []) or []
                 if isinstance(t, dict)
                 and "adlib" in str(t.get("name", "")).lower()), None)
    if lane is None:
        return {"court": "adlibs", "ok": True, "advisories": [],
                "skipped": "no ad-lib lane"}
    secs = sorted((s for s in song.get("sections", []) or []
                   if isinstance(s, dict)),
                  key=lambda s: float(s.get("startBar", 0)))
    advisories = []
    for i, s in enumerate(secs):
        b0 = float(s.get("startBar", 0)) * 4
        b1 = float(secs[i + 1].get("startBar", 1e9)) * 4 \
            if i + 1 < len(secs) else 1e9
        n = sum(1 for x in lane.get("notes") or []
                if b0 <= float(x.get("start", 0)) < b1)
        if n > 3:
            advisories.append({
                "kind": "adlib_mud", "section": s.get("name", "?"),
                "count": n,
                "why": f"{n} ad-libs inside '{s.get('name', '?')}' — "
                       "2-3 per section MAX (more = mud, r-12); thin "
                       "them to the strongest gaps"})
    return {"court": "adlibs", "ok": True, "advisories": advisories}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE AD-LIB LANE (wave 43)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    song = json.load(open(a.song))
    out = place_adlibs(song, a.genre, a.seed)
    if out:
        json.dump(song, open(a.song, "w"), indent=1)
    print(json.dumps({"landed": out}, indent=1))
