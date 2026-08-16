#!/usr/bin/env python3
"""THE HARMONY MIND (PRODUCER MIND backlog wave 13; R-1/R-23/R-24/R-25/R-26).

Deterministic harmony courts + heals over song.json's chords[] spine and
harmonic lanes. Sources: docs/research_producer_mind/r-{1,23,24,25,26}.json.

  court_chord_tones(song, genre)   R-1: every melodic note classified vs the
                                   SOUNDING chord (chord_tone/tension/avoid/
                                   outside); only SUSTAINED STRONG-BEAT avoid
                                   notes escalate (color never convicts)
  court_lil(song)                  R-26: LOW-INTERVAL-LIMIT muddiness — walk
                                   simultaneities bottom-up; flag intervals
                                   voiced below their LIL bottom note
  heal_lil(song, v)                open muddy SAME-LANE stacks (upper note +12)
  court_extensions(song, genre)    R-23/R-21: chord-symbol richness vs genre
                                   floor (neo-soul wants maj7/9/13; deep house
                                   wants the m7; punk wants triads)
  heal_extensions(song, genre, v)  upgrade symbols to the diatonic 7th + land
                                   the 7th in same-bar chord-lane stacks
  court_modal(song, genre)         R-24/R-25: psy/goa leads must live in the
                                   dark collections; maqam membership for the
                                   global lineages; nearest-degree heal
  court_progression(song, genre)   R-1: canon-derived per-family Markov over
                                   roman-numeral transitions; flags chains no
                                   idiom would write; suggest_next() helper
  cadence_report(song)             R-1: functional regions + cadence types at
                                   section ends (info; conviction only for
                                   functional families with zero cadences)
  court_harmony(song, genre, ...)  aggregate; heal_harmony applies the safe
                                   heals (LIL stacks, avoid resolutions,
                                   modal snaps, extension lands)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theory as T  # noqa: E402
import meter as METER  # noqa: E402
import music_court as MC  # noqa: E402

MAX_LIST = 40


# ------------------------------------------------------------------ helpers
def _chords(song):
    rows = []
    for r in song.get("chords") or []:
        ch = T.parse_chord(r.get("chord"))
        if ch:
            rows.append({"bar": float(r.get("bar", 1)), "chord": ch,
                         "text": str(r.get("chord"))})
    return sorted(rows, key=lambda r: r["bar"])


def harmonic_lanes(song):
    """Lanes the harmony courts may read: melodic-role, note-carrying."""
    return [t for t in song.get("tracks", []) or []
            if isinstance(t, dict) and not t.get("muted")
            and MC.court_role(t) == "melodic" and (t.get("notes") or [])]


def _is_bass_lane(t):
    nm = str(t.get("name", "")).lower()
    return any(w in nm for w in ("bass", "808", "sub"))


# ===================================================== R-1 CHORD-TONE COURT
def court_chord_tones(song, genre=""):
    """Classify every melodic note against the sounding chord. Conviction
    evidence = SUSTAINED (>=1 beat) STRONG-BEAT avoid notes; ratio floor 8%
    of judged notes per lane (R-1: only ESCALATE avoid notes — tensions and
    passing color are the idiom, not the crime)."""
    rows = _chords(song)
    if not rows:
        return {"court": "chord_tones", "ok": True, "skipped": "no chords[] spine"}
    mtr = METER.song_meter(song)
    lanes = harmonic_lanes(song)
    flags, per_lane = [], {}
    for t in lanes:
        name = t.get("name", "?")
        counts = {"chord_tone": 0, "tension": 0, "avoid": 0, "outside": 0}
        held_avoid = []
        for n in t.get("notes", []) or []:
            try:
                p = int(n.get("pitch", 60))
                s = float(n.get("start", 0.0))
                dur = float(n.get("len", n.get("length", 0.25)))
            except Exception:
                continue
            bar1 = int(METER.bar_at_q(mtr, s)) + 1
            ch = T.chord_at(song.get("chords"), bar1)
            cls = T.classify_vs_chord(p, ch)
            counts[cls] += 1
            if cls == "avoid" and dur >= 1.0:
                beat = s - METER.bar_start_q(mtr, bar1 - 1)
                strong = abs(beat - round(beat)) < 1e-6 and \
                    int(round(beat)) % 2 == 0
                if strong and len(held_avoid) < MAX_LIST:
                    held_avoid.append({
                        "bar": bar1, "pitch": p, "name": T.midi_to_name(p),
                        "start": s, "chord": (ch or {}).get("name", "?"),
                        "resolve_to": p - 1})
        judged = sum(counts.values())
        if judged:
            per_lane[name] = {**counts,
                              "avoid_ratio": round(counts["avoid"] / judged, 4)}
        if held_avoid and counts["avoid"] / max(judged, 1) > 0.08:
            flags.append({"kind": "avoid_notes", "track": name,
                          "notes": held_avoid,
                          "why": f"{name}: {len(held_avoid)} sustained "
                                 "strong-beat avoid notes (a semitone over a "
                                 "chord tone, held) — resolve down a semitone "
                                 "into the chord"})
    return {"court": "chord_tones", "ok": not flags, "flags": flags,
            "per_lane": per_lane}


def heal_chord_tones(song, genre="", verdict=None):
    """Resolve convicted held avoid notes DOWN a semitone (the suspension's
    own physics). Mutates song; returns edit ledger."""
    v = verdict or court_chord_tones(song, genre)
    edits = []
    targets = {}
    for f in v.get("flags", []):
        if f.get("kind") == "avoid_notes":
            targets[f["track"]] = {(o["start"], o["pitch"]) for o in f["notes"]}
    if not targets:
        return edits
    for t in song.get("tracks", []) or []:
        name = t.get("name", "?")
        if name not in targets:
            continue
        for n in t.get("notes", []) or []:
            try:
                key_ = (float(n.get("start", 0)), int(n.get("pitch", 60)))
            except Exception:
                continue
            if key_ in targets[name]:
                n["pitch"] = int(n["pitch"]) - 1
                edits.append({"track": name, "start": key_[0],
                              "old": T.midi_to_name(key_[1]),
                              "new": T.midi_to_name(key_[1] - 1),
                              "kind": "avoid_resolve"})
    return edits


# ================================================== R-26 LOW-INTERVAL LIMITS
# interval (semitones) -> lowest permitted BOTTOM note (MIDI). Orchestration
# canon (R-26 numbers: m2->E3, m3->C3, M3->Bb2, P4->Bb2, P5->Bb1; octaves
# free). Between-values from standard orchestration practice.
LIL = {1: 52, 2: 51, 3: 48, 4: 46, 5: 46, 6: 46, 7: 35,
       8: 44, 9: 41, 10: 41, 11: 41}


def _simultaneities(song, step=0.5):
    """(time, [(pitch, lane_idx, note_ref)]) sounding stacks across harmonic
    lanes, sampled on a step grid. Bass lanes included (mud lives there)."""
    lanes = harmonic_lanes(song)
    events = []
    for li, t in enumerate(lanes):
        for n in t.get("notes", []) or []:
            try:
                s = float(n.get("start", 0.0))
                d = max(float(n.get("len", n.get("length", 0.25))), 0.05)
                p = int(n.get("pitch", 60))
            except Exception:
                continue
            events.append((s, s + d, p, li, n))
    if not events:
        return [], lanes
    t_end = max(e[1] for e in events)
    out = []
    t0 = 0.0
    while t0 < min(t_end, 512.0):
        sound = [(p, li, n) for (s, e, p, li, n) in events
                 if s - 1e-6 <= t0 < e - 1e-6]
        if len(sound) >= 2:
            out.append((t0, sorted(sound, key=lambda x: (x[0], x[1]))))
        t0 += step
    return out, lanes


# genres whose identity IS low filtered dyads — thirds below the acoustic
# limit are the sound there (dub techno D2+F2 pads, dark garage stabs), so
# thirds demote to advisories; low SECONDS stay mud everywhere.
_LIL_DARK = ("dub_techno", "dubtechno", "techno", "deep_house", "deephouse",
             "ambient", "drone", "psy", "goa", "dark", "industrial", "garage",
             "ukg", "2step", "dubstep", "grime", "trance", "idm", "downtempo")


def court_lil(song, genre=""):
    """Flag interval pairs voiced below their low-interval limit. CALIBRATED
    2026-07-14 twice (the raw acoustic-orchestration table convicted 8 eval
    winners; the survivors were dark-electronic idiom):
      CONVICTIONS: SAME-LANE seconds (1-2 st) >=2 under limit, >=6 steps —
        mud in every genre; SAME-LANE thirds/tritone (3,4,6 st) likewise
        UNLESS the genre is dark-electronic (their filtered low dyads are
        the sound).
      ADVISORIES: everything else below limit (cross-lane pairs live in the
        mixing domain — filters and levels the symbolic court cannot see)."""
    g = str(genre or "").lower()
    dark = any(k in g for k in _LIL_DARK)
    stacks, lanes = _simultaneities(song)
    if not stacks:
        return {"court": "lil", "ok": True, "skipped": "no simultaneities"}
    offenders = {}
    for t0, sound in stacks:
        for i in range(len(sound) - 1):
            (p1, l1, n1), (p2, l2, n2) = sound[i], sound[i + 1]
            iv = p2 - p1
            if iv <= 0 or iv >= 12:
                continue
            limit = LIL.get(iv)
            if limit and p1 < limit:
                key = (p1, p2, l1, l2)
                offenders.setdefault(key, {"count": 0})
                offenders[key]["count"] += 1
    flags, advisories = [], []
    for (p1, p2, l1, l2), info in sorted(offenders.items()):
        iv = p2 - p1
        hard_iv = (1, 2) if dark else (1, 2, 3, 4, 6)
        hard = l1 == l2 and iv in hard_iv and p1 <= LIL[iv] - 2 \
            and info["count"] >= 6
        row = {"kind": "lil", "bottom": T.midi_to_name(p1),
               "top": T.midi_to_name(p2), "interval": iv,
               "limit": T.midi_to_name(LIL[iv]),
               "lane_a": lanes[l1].get("name", "?"),
               "lane_b": lanes[l2].get("name", "?"),
               "same_lane": l1 == l2, "steps": info["count"],
               "why": f"{T.midi_to_name(p1)}+{T.midi_to_name(p2)} "
                      f"({iv}st) below its low-interval limit "
                      f"({T.midi_to_name(LIL[iv])}) for "
                      f"{info['count']} steps — mud, not weight"}
        if hard and len(flags) < MAX_LIST:
            flags.append(row)
        elif info["count"] >= 4 and len(advisories) < MAX_LIST:
            advisories.append(row)
    return {"court": "lil", "ok": not flags, "flags": flags,
            "advisories": advisories}


def heal_lil(song, verdict=None):
    """Open muddy SAME-LANE stacks: the upper note of a convicted pair moves
    +12 (cross-lane pairs are arrangement decisions — verdict only)."""
    v = verdict or court_lil(song)
    edits = []
    by_lane = {t.get("name", "?"): t for t in harmonic_lanes(song)}
    for f in v.get("flags", []):
        if f.get("kind") != "lil" or not f.get("same_lane"):
            continue
        t = by_lane.get(f["lane_a"])
        if not t:
            continue
        top_pitch = T.name_to_midi(f["top"])
        bot_pitch = T.name_to_midi(f["bottom"])
        for n in t.get("notes", []) or []:
            try:
                p = int(n.get("pitch", 60))
            except Exception:
                continue
            if p == top_pitch and p + 12 <= 127:
                # only when the bottom partner actually sounds at this start
                s = float(n.get("start", 0))
                partner = any(
                    abs(float(m.get("start", 0)) - s) < 0.51
                    and int(m.get("pitch", -1)) == bot_pitch
                    for m in t.get("notes", []) or [])
                if partner:
                    n["pitch"] = p + 12
                    edits.append({"track": f["lane_a"], "start": s,
                                  "old": f["top"],
                                  "new": T.midi_to_name(p + 12),
                                  "kind": "lil_open"})
    return edits


# ============================================== R-23/R-21 EXTENSION COURT
_EXT_RICH = ("jazz", "neosoul", "neo_soul", "gospel", "city_pop", "citypop",
             "rnb", "r_b", "soul", "bossa", "fusion", "lofi", "jazzhop")
_EXT_M7 = ("deep_house", "deephouse", "dub_techno", "dubtechno", "liquid")
_EXT_PLAIN = ("punk", "metal", "hard_rock", "hardrock", "grunge", "trance",
              "hardstyle", "gabber", "rocknroll")


def _is_extended(ch):
    q = ch.get("quality", "")
    return any(x in q for x in ("7", "9", "11", "13", "6")) or len(ch["pcs"]) >= 4


def court_extensions(song, genre=""):
    rows = _chords(song)
    if len(rows) < 2:
        return {"court": "extensions", "ok": True, "skipped": "no chords[] spine"}
    g = str(genre or "").lower()
    ext = sum(1 for r in rows if _is_extended(r["chord"]))
    ratio = ext / len(rows)
    flags, advisories = [], []
    if any(k in g for k in _EXT_RICH) and ratio < 0.6:
        flags.append({"kind": "thin_harmony", "ratio": round(ratio, 3),
                      "floor": 0.6,
                      "why": f"only {ext}/{len(rows)} chords carry a 7th+ — "
                             f"'{genre}' is a maj7/9/13 language; plain "
                             "triads read as a beginner take"})
    elif any(k in g for k in _EXT_M7) and ratio < 0.5:
        flags.append({"kind": "thin_harmony", "ratio": round(ratio, 3),
                      "floor": 0.5,
                      "why": f"'{genre}' wants m7/sus color (Am7 is the "
                             "deep-house floor); bare triads FAIL"})
    elif any(k in g for k in _EXT_PLAIN) and ratio > 0.5:
        advisories.append({"kind": "over_extended", "ratio": round(ratio, 3),
                           "why": f"'{genre}' speaks triads/power chords; "
                                  f"{ext}/{len(rows)} extended chords may "
                                  "read outside the idiom"})
    return {"court": "extensions", "ok": not flags, "flags": flags,
            "advisories": advisories, "extended_ratio": round(ratio, 3)}


def heal_extensions(song, genre="", verdict=None):
    """Upgrade plain triads to the DIATONIC 7th in the declared key (symbol
    edit) + land that 7th inside same-bar chord-lane stacks (>=3-note stacks
    only — a triad pad becomes a 7th pad; leads are never touched)."""
    v = verdict or court_extensions(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    key = T.parse_key(song.get("key"))
    edits = []
    mtr = METER.song_meter(song)
    for row in song.get("chords") or []:
        ch = T.parse_chord(row.get("chord"))
        if not ch or _is_extended(ch):
            continue
        # diatonic 7th: minor7 over minor triads, maj7/dom by scale membership
        root = ch["root_pc"]
        if "m" == ch["quality"] or ch["quality"] == "min":
            new = str(row["chord"]).strip() + "7"
            seventh = (root + 10) % 12
        else:
            maj7_pc = (root + 11) % 12
            in_scale = key and maj7_pc in key["scale_pcs"]
            new = str(row["chord"]).strip() + ("maj7" if in_scale else "7")
            seventh = maj7_pc if in_scale else (root + 10) % 12
        old = row["chord"]
        row["chord"] = new
        edits.append({"kind": "chord_symbol", "bar": row.get("bar"),
                      "old": old, "new": new})
        # land the 7th into same-bar stacks on chord lanes
        bar = float(row.get("bar", 1))
        q0 = METER.bar_start_q(mtr, int(bar) - 1)
        q1 = METER.bar_start_q(mtr, int(bar))
        for t in harmonic_lanes(song):
            if _is_bass_lane(t):
                continue
            notes = t.get("notes", []) or []
            starts = {}
            for n in notes:
                s = float(n.get("start", -1))
                if q0 - 1e-6 <= s < q1:
                    starts.setdefault(s, []).append(n)
            for s, stack in starts.items():
                if len(stack) < 3:
                    continue
                pcs = {int(n.get("pitch", 0)) % 12 for n in stack}
                if seventh in pcs:
                    continue
                top = max(int(n.get("pitch", 60)) for n in stack)
                new_p = top - ((top - seventh) % 12)
                if new_p <= top - 12:
                    new_p += 12
                ref = dict(stack[0])
                ref["pitch"] = new_p
                notes.append(ref)
                edits.append({"kind": "land_7th", "track": t.get("name", "?"),
                              "start": s, "pitch": T.midi_to_name(new_p)})
    return edits


# ================================================ R-24/R-25 MODAL/MAQAM LAW
_PSY = ("psytrance", "psy_trance", "goa", "darkpsy", "forest", "full_on",
        "fullon", "hitech", "hi_tech", "psycore", "zenon", "psybreaks")
_PSY_ALLOWED = ("phrygian", "phrygian_dominant", "harmonic_minor", "minor",
                "double_harmonic", "hungarian_minor", "minor_pentatonic")
_MAQAM_GENRES = ("arabic", "oriental", "balkan", "romani", "flamenco",
                 "klezmer", "turkish", "dabke", "rai", "shaabi", "mizrahi")


def _collection_fit(notes, pcs_set, tonic_pc):
    """Duration-weighted fraction of notes INSIDE the collection."""
    tot = inside = 0.0
    legal = {(tonic_pc + p) % 12 for p in pcs_set}
    for n in notes:
        try:
            d = max(float(n.get("len", n.get("length", 0.25))), 0.05)
            p = int(n.get("pitch", 60)) % 12
        except Exception:
            continue
        tot += d
        if p in legal:
            inside += d
    return (inside / tot) if tot else 1.0


def court_modal(song, genre=""):
    """Psy-family lead/acid lanes must live in the dark collections; maqam
    families must fit a maqam set. Verdict + nearest-degree heal targets."""
    g = str(genre or "").lower()
    is_psy = any(k in g for k in _PSY)
    is_maqam = any(k in g for k in _MAQAM_GENRES)
    if not (is_psy or is_maqam):
        return {"court": "modal", "ok": True, "skipped": "genre outside modal law"}
    key = T.parse_key(song.get("key"))
    tonic = key["tonic_pc"] if key else 0
    allowed = _PSY_ALLOWED if is_psy else tuple(T.MAQAM_12TET)
    lanes = [t for t in harmonic_lanes(song)
             if not _is_bass_lane(t) and len(t.get("notes") or []) >= 8]
    flags, per_lane = [], {}
    for t in lanes:
        notes = t.get("notes") or []
        fits = {}
        for name in allowed:
            pcs = T.MODES.get(name) or T.MAQAM_12TET.get(name, {}).get("pcs")
            if not pcs:
                continue
            fits[name] = _collection_fit(notes, pcs, tonic)
        if not fits:
            continue
        best = max(fits, key=fits.get)
        major_fit = _collection_fit(notes, T.MODES["major"], tonic)
        per_lane[t.get("name", "?")] = {"best": best,
                                        "fit": round(fits[best], 3),
                                        "major_fit": round(major_fit, 3)}
        if fits[best] < 0.9 and major_fit > fits[best] + 0.05 and is_psy:
            flags.append({"kind": "major_lead", "track": t.get("name", "?"),
                          "why": f"{t.get('name', '?')}: sits closer to MAJOR "
                                 f"({major_fit:.2f}) than any dark collection "
                                 f"(best {best} {fits[best]:.2f}) — psy leads "
                                 "live in phrygian/harmonic-minor space",
                          "snap_to": best})
        elif fits[best] < 0.85:
            flags.append({"kind": "off_collection", "track": t.get("name", "?"),
                          "why": f"{t.get('name', '?')}: only {fits[best]:.2f} "
                                 f"of note-time inside the best allowed "
                                 f"collection ({best}) — re-quantize to the "
                                 "mode", "snap_to": best})
    return {"court": "modal", "ok": not flags, "flags": flags,
            "per_lane": per_lane, "tonic": tonic}


def heal_modal(song, genre="", verdict=None):
    """Snap flagged lanes' off-collection notes to the nearest degree of the
    lane's best collection (gravity down on ties)."""
    v = verdict or court_modal(song, genre)
    if v.get("skipped") or v.get("ok", True):
        return []
    tonic = v.get("tonic", 0)
    edits = []
    by_name = {t.get("name", "?"): t for t in harmonic_lanes(song)}
    for f in v.get("flags", []):
        t = by_name.get(f.get("track"))
        mode = f.get("snap_to")
        pcs = T.MODES.get(mode) or T.MAQAM_12TET.get(mode, {}).get("pcs")
        if not t or not pcs:
            continue
        legal = {(tonic + p) % 12 for p in pcs}
        for n in t.get("notes", []) or []:
            try:
                p = int(n.get("pitch", 60))
            except Exception:
                continue
            if p % 12 in legal:
                continue
            cands = [c for c in range(p - 2, p + 3)
                     if 0 <= c <= 127 and c % 12 in legal and c != p]
            if not cands:
                continue
            newp = min(cands, key=lambda c: (abs(c - p), c > p))
            old = n["pitch"]
            n["pitch"] = newp
            edits.append({"track": f["track"], "start": n.get("start"),
                          "old": T.midi_to_name(old),
                          "new": T.midi_to_name(newp), "kind": "modal_snap"})
    return edits


# ============================================ R-1 PROGRESSION GRAMMAR (canon)
# Canonical progressions per family, ROMAN DEGREES relative to the tonic
# (semitones, quality). The Markov tables are DERIVED from these — canon
# seeds today, corpus mining refines later (provenance: standard repertoire
# tables; Hooktheory-scale mining is the ledger's noted upgrade).
PROG_LIBRARY = {
    # r-26 THE PIRATES CLASS (w40): modal minor cycle, no leading tone
    # in the loop — the single harmonic-minor V lives at the cadence
    "epic": [["i", "VI", "VII", "III"], ["i", "VII", "VI", "VII"],
             ["i", "VI", "III", "VII"]],
    "pop": [  # Axis family + rotations + 50s + Andalusian-lite
        [(0, ""), (7, ""), (9, "m"), (5, "")],
        [(9, "m"), (5, ""), (0, ""), (7, "")],
        [(0, ""), (9, "m"), (5, ""), (7, "")],
        [(5, ""), (0, ""), (7, ""), (9, "m")],
        [(0, ""), (9, "m"), (2, "m"), (7, "")],
        [(0, ""), (5, ""), (9, "m"), (7, "")],
    ],
    "jpop": [  # Royal Road (IVmaj7-V7-iii7-vi) + ii-V-I
        [(5, "maj7"), (7, "7"), (4, "m7"), (9, "m")],
        [(2, "m7"), (7, "7"), (0, "maj7"), (0, "maj7")],
        [(5, "maj7"), (7, "7"), (0, ""), (9, "m")],
    ],
    "jazz": [  # ii-V-I majors/minors, turnarounds, iii-VI-ii-V
        [(2, "m7"), (7, "7"), (0, "maj7"), (0, "maj7")],
        [(0, "maj7"), (9, "7"), (2, "m7"), (7, "7")],
        [(4, "m7"), (9, "7"), (2, "m7"), (7, "7")],
        [(2, "m7b5"), (7, "7"), (0, "m7"), (0, "m7")],
    ],
    "gospel": [  # 2-5-1, 3-6-2-5-1, passing motion
        [(2, "m7"), (7, "7"), (0, "maj7"), (0, "maj7")],
        [(4, "m7"), (9, "m7"), (2, "m7"), (7, "7")],
        [(0, ""), (5, ""), (0, ""), (7, "7")],
    ],
    "blues": [  # 12-bar skeleton transitions
        [(0, "7"), (0, "7"), (0, "7"), (0, "7")],
        [(5, "7"), (5, "7"), (0, "7"), (0, "7")],
        [(7, "7"), (5, "7"), (0, "7"), (7, "7")],
    ],
    "edm": [  # minor loops: i-VI-III-VII family + i-VII-VI
        [(0, "m"), (8, ""), (3, ""), (10, "")],
        [(0, "m"), (10, ""), (8, ""), (10, "")],
        [(0, "m"), (5, "m"), (8, ""), (10, "")],
        [(0, "m"), (8, ""), (10, ""), (0, "m")],
    ],
    "andalusian": [
        [(0, "m"), (10, ""), (8, ""), (7, "")],
    ],
}
_PROG_FAMILY = {
    "pop": ("pop", "kpop", "k_pop", "indie", "rock", "country", "ballad",
            "singer", "folk"),
    "jpop": ("jpop", "j_pop", "city_pop", "citypop", "anime"),
    "jazz": ("jazz", "bebop", "swing", "bossa", "fusion", "neosoul",
             "neo_soul", "lofi", "jazzhop"),
    "gospel": ("gospel", "soul", "rnb", "r_b", "motown"),
    "blues": ("blues", "boogie", "rocknroll"),
    "andalusian": ("flamenco", "latin", "reggaeton"),
    "edm": ("house", "techno", "trance", "edm", "dnb", "garage", "dubstep",
            "trap", "drill", "phonk", "hiphop", "hip_hop", "electro",
            "hardstyle", "synthwave", "ambient"),
}


def _prog_family(genre):
    if any(k in str(genre or "").lower() for k in
           ("cinematic", "orchestral", "epic", "trailer",
            "soundtrack", "score", "filmi")):
        return "epic"
    g = str(genre or "").lower()
    for fam, keys in _PROG_FAMILY.items():
        if any(k in g for k in keys):
            return fam
    return "pop"


def markov_for(genre):
    """1st-order transition table {(deg,qual)->{(deg,qual)->prob}} derived
    from the family's canonical loops (rotation-closed, Laplace-smoothed)."""
    fam = _prog_family(genre)
    counts = {}
    for prog in PROG_LIBRARY[fam]:
        for i, cur in enumerate(prog):
            nxt = prog[(i + 1) % len(prog)]
            counts.setdefault(cur, {}).setdefault(nxt, 0)
            counts[cur][nxt] += 1
    table = {}
    for cur, nxts in counts.items():
        tot = sum(nxts.values()) + 0.5 * len(nxts)
        table[cur] = {n: (c + 0.5) / tot for n, c in nxts.items()}
    return table


def _roman(ch, key):
    deg = (ch["root_pc"] - key["tonic_pc"]) % 12
    q = ch.get("quality", "")
    if q in ("maj", ""):
        q = ""
    elif q.startswith("m") and not q.startswith("maj"):
        q = "m" if q in ("m", "min") else q
    return (deg, q)


def _qual_class(q):
    if not q or q == "maj":
        return "maj"
    if q.startswith("m") and not q.startswith("maj"):
        return "min"
    if "7" in q:
        return "dom"
    return q


def court_progression(song, genre=""):
    """Mean transition probability of the chords[] chain under the family's
    canon Markov. Degree-exact hits score fully; degree-hit/quality-miss at
    half; unseen transitions floor at epsilon. Flag = chain no idiom writes
    (mean p < 0.02 with >=4 distinct transitions). Advisory otherwise."""
    rows = _chords(song)
    key = T.parse_key(song.get("key"))
    if len(rows) < 3 or key is None:
        return {"court": "progression", "ok": True,
                "skipped": "needs chords[] + key"}
    table = markov_for(genre)
    eps = 0.004
    seq = [_roman(r["chord"], key) for r in rows]
    probs = []
    for cur, nxt in zip(seq, seq[1:]):
        if cur == nxt:
            continue                                  # holds are free
        p = None
        if cur in table:
            p = table[cur].get(nxt)
            if p is None:
                # degree match, quality mismatch: half credit of best match
                for cand, pv in table[cur].items():
                    if cand[0] == nxt[0]:
                        p = pv * 0.5
                        break
        if p is None:
            # unseen source chord: try degree-level lookup
            for src, nxts in table.items():
                if src[0] == cur[0]:
                    p = max((pv * 0.5 for cand, pv in nxts.items()
                             if cand[0] == nxt[0]), default=None)
                    if p:
                        break
        probs.append(max(p or eps, eps))
    if len(probs) < 3:
        return {"court": "progression", "ok": True,
                "skipped": "chain too short/static"}
    mean_p = 1.0
    for p in probs:
        mean_p *= p
    mean_p **= (1.0 / len(probs))
    fam = _prog_family(genre)
    verdict = {"court": "progression", "family": fam,
               "mean_p": round(mean_p, 4), "transitions": len(probs),
               "ok": mean_p >= 0.02}
    if not verdict["ok"]:
        verdict["flags"] = [{
            "kind": "alien_progression",
            "why": f"chord chain scores {mean_p:.3f} under the {fam} canon "
                   "grammar (floor 0.02) — no idiom writes these moves; "
                   "check the spine or the key"}]
    return verdict


def suggest_next(genre, current_chord, key):
    """Top-3 canon continuations for the composer (roman -> concrete names)."""
    ch = T.parse_chord(current_chord) if isinstance(current_chord, str) \
        else current_chord
    k = T.parse_key(key) if isinstance(key, str) else key
    if not ch or not k:
        return []
    table = markov_for(genre)
    cur = _roman(ch, k)
    nxts = table.get(cur)
    if not nxts:
        for src, cands in table.items():
            if src[0] == cur[0]:
                nxts = cands
                break
    if not nxts:
        return []
    out = []
    for (deg, q), p in sorted(nxts.items(), key=lambda kv: -kv[1])[:3]:
        root = (k["tonic_pc"] + deg) % 12
        name = T.SHARPS[root] + (q if q not in ("maj",) else "")
        out.append({"chord": name, "p": round(p, 3)})
    return out


# ===================================================== R-1 cadence report
_FUNCTIONAL = ("jazz", "gospel", "classical", "orchestral", "soul", "bossa",
               "swing", "bebop", "choro", "tango")


def cadence_report(song, genre=""):
    rows = _chords(song)
    key = T.parse_key(song.get("key"))
    if len(rows) < 2 or key is None:
        return {"court": "cadence", "ok": True, "skipped": "needs chords[] + key"}
    secs = sorted((s for s in song.get("sections", []) or []
                   if isinstance(s, dict)),
                  key=lambda s: float(s.get("startBar", 0)))
    marks = []
    boundaries = [float(s.get("startBar", 0)) for s in secs[1:]] + \
        [float(song.get("lengthBars", rows[-1]["bar"]))]
    for b in boundaries:
        before = [r for r in rows if r["bar"] < b - 1e-6]
        if len(before) >= 2:
            cad = T.cadence_of(before[-2]["chord"], before[-1]["chord"], key)
            marks.append({"at_bar": b, "pair": f"{before[-2]['text']}->"
                                               f"{before[-1]['text']}",
                          "cadence": cad})
    g = str(genre or "").lower()
    functional = any(k in g for k in _FUNCTIONAL)
    distinct = len({(r["chord"]["root_pc"], r["chord"]["quality"])
                    for r in rows})
    flags = []
    if functional and distinct >= 4 and marks and \
            not any(m["cadence"] for m in marks):
        flags.append({"kind": "no_cadence",
                      "why": f"'{genre}' is a functional-harmony language and "
                             "no section end lands a cadence — phrase ends "
                             "want V->I / ii-V motion"})
    return {"court": "cadence", "ok": not flags, "flags": flags,
            "marks": marks, "functions": [
                {"bar": r["bar"], "chord": r["text"],
                 "fn": T.function_of(r["chord"], key)} for r in rows[:24]]}


# ================================================================ aggregate
def court_harmony(song, genre="", heal=False):
    out = {"chord_tones": court_chord_tones(song, genre),
           "lil": court_lil(song, genre),
           "extensions": court_extensions(song, genre),
           "modal": court_modal(song, genre),
           "progression": court_progression(song, genre),
           "cadence": cadence_report(song, genre)}
    if heal:
        heals = {}
        if not out["chord_tones"].get("ok", True):
            heals["chord_tones"] = heal_chord_tones(song, genre,
                                                    out["chord_tones"])
            out["chord_tones_after"] = court_chord_tones(song, genre)
        if not out["lil"].get("ok", True):
            heals["lil"] = heal_lil(song, out["lil"])
            out["lil_after"] = court_lil(song, genre)
        if not out["extensions"].get("ok", True):
            heals["extensions"] = heal_extensions(song, genre,
                                                  out["extensions"])
            out["extensions_after"] = court_extensions(song, genre)
        if not out["modal"].get("ok", True):
            heals["modal"] = heal_modal(song, genre, out["modal"])
            out["modal_after"] = court_modal(song, genre)
        out["heals"] = heals
    out["ok"] = all(v.get("ok", True) for k, v in out.items()
                    if isinstance(v, dict) and not k.endswith("_after"))
    return out


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description="THE HARMONY MIND (wave 13)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song))
    v = court_harmony(song, args.genre, heal=args.heal)
    if args.heal and v.get("heals"):
        with open(args.song, "w") as f:
            json.dump(song, f, indent=1)
        v["saved"] = args.song
    print(json.dumps(v, indent=1))
    return 0 if v["ok"] or args.heal else 1


if __name__ == "__main__":
    sys.exit(main())
