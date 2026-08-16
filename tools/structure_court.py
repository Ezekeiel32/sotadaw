#!/usr/bin/env python3
"""THE STRUCTURE COURTS — wave 51 (R-29 item 170, the four missing of
six; cadence lives in harmony_court.court_progression, the density arc
in tension.court_tension_arc — one resolver per jurisdiction).

Zero-token, symbolic, ADVISORY-first (the wolf calibrates edges past
the corpus before anything convicts):

  court_phrase_grid   section lengths on the 2^n grid ({4,8,16,32,64};
                      12/24 legal for blues/jazz/folk families) — pop
                      breathes in powers of two
  court_repetition    A must recur: bar-fingerprint self-similarity
                      floor + section-class recurrence (through-composed
                      'pop' is a generated-music tell)
  court_contrast      verse vs chorus must DIFFER (density or register
                      or lane count) — sections that read identical are
                      names, not music
  court_vocabulary    rhythm n-gram spray: generated music over-sprays
                      unique patterns; real music speaks a vocabulary
  court_structure     the aggregate run_courts mounts
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_POW2 = (4, 8, 16, 32, 64)
_IRREGULAR_OK = ("blues", "jazz", "folk", "swing", "bebop", "gypsy",
                 "flamenco", "klezmer", "balkan", "odd", "prog")


def _sections(song):
    secs = [s for s in (song or {}).get("sections", []) or []
            if isinstance(s, dict) and s.get("name") is not None]
    secs.sort(key=lambda s: float(s.get("startBar", 0)))
    return secs


def _melodic_tracks(song):
    out = []
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted") or not t.get("notes"):
            continue
        nm = str(t.get("name", "")).lower()
        if any(w in nm for w in ("kick", "snare", "clap", "hat", "perc",
                                 "cym", "crash", "ride", "tom", "shaker",
                                 "_sketch", "_identity")):
            continue
        out.append(t)
    return out


def court_phrase_grid(song, genre=""):
    secs = _sections(song)
    if len(secs) < 2:
        return {"ok": True, "advisories": [], "skipped": "needs sections"}
    if any(str(s.get("name", "")).lower().startswith(("deck ", "bridge"))
           for s in secs):
        return {"ok": True, "advisories": [],
                "skipped": "DJ-set manifest (chapters, not form)"}
    g = str(genre or "").lower()
    allow_irreg = any(w in g for w in _IRREGULAR_OK)
    end = float((song or {}).get("lengthBars", 0) or 0)
    advisories = []
    for i, s in enumerate(secs):
        a = float(s.get("startBar", 0))
        b = float(secs[i + 1].get("startBar", end)) if i + 1 < len(secs) \
            else end
        span = int(round(b - a))
        if span <= 0:
            continue
        # WOLF LAW (305-song corpus, 2026-07-16): 2^n-only flagged 1791
        # spans — real sections run 20/24/40 bars constantly (4-bar
        # phrases in odd counts). The true crime is a span the 4-bar
        # phrase doesn't divide.
        ok = span % 4 == 0 or (allow_irreg and span in (3, 6, 12, 24))
        if not ok:
            advisories.append({
                "kind": "off_grid_section", "section": s.get("name"),
                "bars": span,
                "why": (f"'{s.get('name')}' runs {span} bars — not even "
                        "the 4-bar phrase divides it; it reads as a "
                        "truncated edit unless the genre speaks "
                        "irregular phrases")})
    if len(advisories) > 3:
        advisories = [{
            "kind": "off_grid_form", "count": len(advisories),
            "why": (f"{len(advisories)} sections sit off the 4-bar "
                    "phrase grid — detected/imported boundaries, or the "
                    "form itself is torn; re-section before judging "
                    "phrases")}]
    return {"ok": True, "advisories": advisories}


def _composed(track):
    """Jurisdiction (witness law): repetition/vocabulary judge COMPOSED
    lanes — grid-born notes. Performed/transcribed lanes (imports,
    hum captures) carry timing jitter that makes every bar's grid
    unique; humanized real playing is never 'typing'. A lane is
    composed when >=60% of onsets sit within 0.06 beats of the 16th
    grid."""
    notes = track.get("notes") or []
    if len(notes) < 8:
        return False
    snapped = 0
    for n in notes:
        try:
            s = float(n.get("start", 0))
        except Exception:
            continue
        if abs(s * 4 - round(s * 4)) <= 0.24:      # 0.06 beat * 4
            snapped += 1
    return snapped / max(len(notes), 1) >= 0.6


def _bar_fingerprint(track, bar, bpb=4):
    """Rhythm (16th onsets) + pitch-class set for one bar."""
    a, b = bar * bpb, (bar + 1) * bpb
    ons, pcs = [], set()
    for n in track.get("notes") or []:
        try:
            s = float(n.get("start", 0))
        except Exception:
            continue
        if a <= s < b:
            ons.append(int(round((s - a) * 4)))
            pcs.add(int(n.get("pitch", 0)) % 12)
    if not ons:
        return None
    return (tuple(sorted(set(ons))), tuple(sorted(pcs)))


def court_repetition(song, genre=""):
    bars = int((song or {}).get("lengthBars", 0) or 0)
    tracks = _melodic_tracks(song)
    if bars < 8 or not tracks:
        return {"ok": True, "advisories": [], "skipped": "too little"}
    recur, total = 0, 0
    tracks = [t for t in tracks if _composed(t)]
    for t in tracks:
        seen = {}
        fps = [_bar_fingerprint(t, b) for b in range(bars)]
        live = [f for f in fps if f is not None]
        if len(live) < 4:
            continue
        for f in live:
            seen[f] = seen.get(f, 0) + 1
        recur += sum(c for c in seen.values() if c >= 2)
        total += len(live)
    advisories = []
    sim = recur / total if total else 1.0
    if total >= 16 and sim < 0.35:
        advisories.append({
            "kind": "through_composed", "self_similarity": round(sim, 2),
            "why": (f"only {sim:.0%} of melodic bars ever recur — real "
                    "songs repeat themselves (the hook IS repetition); "
                    "a take that never restates reads as wandering, "
                    "not flowing")})
    secs = _sections(song)
    if len(secs) >= 4:
        import form_court as FCRT
        classes = [FCRT._sec_class(s.get("name")) for s in secs]
        body = [c for c in classes if c not in ("intro", "outro")]
        if body and len(set(body)) == len(body):
            advisories.append({
                "kind": "no_section_recurs", "classes": body,
                "why": ("every section class appears exactly once — no "
                        "verse returns, no chorus returns; that is a "
                        "medley, not a song")})
    return {"ok": True, "advisories": advisories,
            "self_similarity": round(sim, 2)}


def _section_stats(song, sec_bars, tracks):
    dens, lo, hi, lanes = 0, None, None, 0
    nbars = max(len(sec_bars), 1)
    for t in tracks:
        got = 0
        for n in t.get("notes") or []:
            try:
                b = int(float(n.get("start", 0)) // 4)
            except Exception:
                continue
            if b in sec_bars:
                got += 1
                p = int(n.get("pitch", 60))
                lo = p if lo is None else min(lo, p)
                hi = p if hi is None else max(hi, p)
        if got:
            lanes += 1
        dens += got
    return {"density": dens / nbars, "range": (hi - lo) if lo is not None
            else 0, "lanes": lanes}


def court_contrast(song, genre=""):
    secs = _sections(song)
    end = float((song or {}).get("lengthBars", 0) or 0)
    if len(secs) < 2 or not end:
        return {"ok": True, "advisories": [], "skipped": "needs sections"}
    import form_court as FCRT
    spans = {}
    for i, s in enumerate(secs):
        a = int(float(s.get("startBar", 0)))
        b = int(float(secs[i + 1].get("startBar", end))) if i + 1 < len(secs) \
            else int(end)
        cls = FCRT._sec_class(s.get("name"))
        spans.setdefault(cls, set()).update(range(a, b))
    # form_court's class table folds chorus/drop into HOOK — the pairs
    # speak that vocabulary (one resolver, never a re-encoded table)
    pairs = [("verse", "hook"), ("build", "hook"), ("quiet", "hook")]
    tracks = [t for t in _melodic_tracks(song) if _composed(t)]
    advisories = []
    for ca, cb in pairs:
        if ca not in spans or cb not in spans or not tracks:
            continue
        sa = _section_stats(song, spans[ca], tracks)
        sb = _section_stats(song, spans[cb], tracks)
        d_dens = abs(sa["density"] - sb["density"]) / max(sa["density"],
                                                          sb["density"], 1e-9)
        d_range = abs(sa["range"] - sb["range"])
        d_lanes = abs(sa["lanes"] - sb["lanes"])
        if d_dens < 0.10 and d_range < 3 and d_lanes == 0:
            advisories.append({
                "kind": "no_contrast", "pair": f"{ca}/{cb}",
                "why": (f"{ca} and {cb} carry the same density "
                        f"({sa['density']:.1f} vs {sb['density']:.1f} "
                        "notes/bar), register and lane count — the names "
                        "differ, the music doesn't; lift the "
                        f"{cb} (add a lane, open the register) or thin "
                        f"the {ca}")})
        break  # judge the first labeled pair only — one verdict, no pile
    return {"ok": True, "advisories": advisories}


def court_vocabulary(song, genre="", edge=0.82):
    """Unique 1-bar rhythm-grams / total. Generated music over-sprays;
    a real take speaks a vocabulary. Edge sits PAST the corpus (wolf-
    calibrated); advisory only."""
    bars = int((song or {}).get("lengthBars", 0) or 0)
    tracks = _melodic_tracks(song)
    advisories, worst = [], None
    for t in tracks:
        if not _composed(t):
            continue
        grams = []
        for b in range(bars):
            f = _bar_fingerprint(t, b)
            if f is not None:
                grams.append(f[0])          # rhythm only — pitch varies
        if len(grams) < 12:
            continue
        spray = len(set(grams)) / len(grams)
        if worst is None or spray > worst[1]:
            worst = (t.get("name"), spray)
        if spray > edge:
            advisories.append({
                "kind": "vocabulary_spray", "track": t.get("name"),
                "unique_ratio": round(spray, 2),
                "why": (f"'{t.get('name')}': {spray:.0%} of its bars "
                        "are rhythmically one-off — real parts restate "
                        "their figures; endless variation reads as "
                        "typing, not playing")})
    return {"ok": True, "advisories": advisories,
            "worst": worst and {"track": worst[0],
                                "unique_ratio": round(worst[1], 2)}}


def court_structure(song, genre=""):
    out = {"court": "structure", "ok": True}
    advisories = []
    for name, fn in (("phrase_grid", court_phrase_grid),
                     ("repetition", court_repetition),
                     ("contrast", court_contrast),
                     ("vocabulary", court_vocabulary)):
        try:
            v = fn(song, genre)
            out[name] = v
            advisories += v.get("advisories", [])
        except Exception:
            pass
    out["advisories"] = advisories
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="THE STRUCTURE COURTS (w51)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    a = ap.parse_args()
    print(json.dumps(court_structure(json.load(open(a.song)), a.genre),
                     indent=1))
