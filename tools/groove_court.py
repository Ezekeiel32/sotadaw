#!/usr/bin/env python3
"""THE GROOVE COURT (PRODUCER MIND backlog wave 14; R-3/R-4/R-21/R-22/R-24).

Deterministic rhythm-authenticity courts + heals over song.json drum lanes.
Sources: docs/research_producer_mind/r-{3,4,21,22,24}.json (32-agent corpus).

  court_tempo(song, genre)        R-21/R-22: per-genre micro-range gate w/ the
                                  HALFTIME DOUBLE-COUNT resolver (backbeat step
                                  + hat rate decide FELT vs notated)
  court_kick(song, genre)         R-21: four-on-floor REQUIRED vs FORBIDDEN
  court_backbeat(song, genre)     R-22: snare 2&4 / trap snare-on-3 / element
  court_swing(song, genre)        R-21: dead-straight grid = the #1 fake tell
                                  in swung genres; measured off-16th fraction
  heal_swing(song, genre, v)      groove-template offsets onto hats/perc/snare
                                  ONLY (kick+bass anchored — R-24 role law)
  court_hats(song, genre)         R-22: trap/drill roll + 3+3+2 polyrhythm +
                                  velocity-variance floor
  heal_hats(song, genre, v)       velocity humanization + roll injection
  court_jitter(song, genre)       R-3: random timing SD capped at <=60% of the
                                  measured human SD (over-humanize subtracts)
  court_dna_mask(song, genre)     R-24: canonical onset masks (dembow, maqsoum,
                                  baladi, saidi, one-drop, tresillo, son clave)
  heal_dna_mask(song, genre, v)   snap off-mask onsets to the nearest slot
  court_clave(song, genre)        R-24: 2-3 vs 3-2 consistency (cruzao = the
                                  cardinal Latin authenticity fail)
  court_fills(song, genre)        R-4: verse->chorus & build->drop boundaries
                                  MUST carry a fill (p=0.95 class)
  heal_fills(song, genre, v)      drum_grammar.fill into the boundary
  court_ghosts(song, genre)       R-4: funk/neo-soul snare lanes want ghosts
  court_layering(song, genre)     R-4: frequency-zone lane caps (<=2 sub,
                                  <=3 mid, <=3 top)
  court_ai_tells(song, genre)     R-22 composite: the authenticity meta-score
  court_groove(song, genre, heal) aggregate + heals
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drum_grammar as DG  # noqa: E402
import pocket_dna as PD  # noqa: E402

MAX_LIST = 24


# ------------------------------------------------------------------ lanes
def drum_lanes(song):
    # THE DRUM-MICROSCOPE WITNESS RULE: stems-imported songs carry piece
    # lanes (Kick/Snare/...) sampled from a REAL recording (source.kind
    # "sample" + an import kit, with *_sketch siblings) — their human
    # timing is evidence, never a defendant.
    imported_song = any(str(t.get("name", "")).lower().endswith("_sketch")
                        for t in song.get("tracks", []) or []
                        if isinstance(t, dict))
    out = []
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        try:                        # THE WITNESS LAW (music_court): imported
            import music_court      # transcriptions carry human performance
            if music_court.court_role(t) == "witness":
                continue            # timing — never defendants here
        except Exception:
            pass
        src = t.get("source") or {}
        if imported_song and src.get("kind") == "sample" and src.get("kit"):
            continue
        role = DG.drum_role(t.get("name"))
        if role != "other" and (t.get("notes") or []):
            out.append((role, t))
    return out


def _onsets(t):
    return sorted(float(n.get("start", 0)) for n in t.get("notes") or [])


def _bar_pos(onsets, beats_per_bar=4.0):
    return [s % beats_per_bar for s in onsets]


# ============================================ R-21/R-22 TEMPO + FEEL COURT
# verified micro-ranges (R-21/R-22/R-24/R-25 numbers tables, 2026-07-14)
TEMPO_RANGES = {
    "house": (120, 128), "deep_house": (118, 125), "deephouse": (118, 125),
    "tech_house": (124, 128), "techno": (125, 140), "hard_techno": (145, 160),
    "ukgarage": (130, 135), "ukg": (130, 135), "2step": (130, 135),
    "speed_garage": (130, 138), "grime": (138, 142), "dubstep": (138, 142),
    "trance": (132, 142), "hardstyle": (145, 155), "gabber": (160, 200),
    "dnb": (170, 180), "drum_and_bass": (170, 180), "jungle": (155, 170),
    "dub": (118, 130), "dub_techno": (110, 125),
    "trap": (130, 170), "drill": (138, 150), "uk_drill": (138, 150),
    "boombap": (85, 98), "boom_bap": (85, 98), "phonk": (130, 170),
    "lofi": (70, 92), "hiphop": (85, 105),
    "reggaeton": (88, 100), "amapiano": (108, 115), "afro_house": (118, 125),
    "gqom": (120, 127), "afrobeats": (100, 115), "dancehall": (90, 104),
    "one_drop": (70, 90), "reggae": (60, 118),
    "latin_trap": (130, 150), "cumbia": (90, 110), "salsa": (150, 250),
    "kpop": (100, 132), "k_pop": (100, 132),
    "full_on": (142, 146), "fullon": (142, 146), "goa": (135, 150),
    "psytrance": (138, 148), "progressive_psy": (138, 144),
    "darkpsy": (148, 158), "forest": (148, 158), "hitech": (170, 220),
    "psybient": (70, 120), "trip_hop": (70, 90), "downtempo": (60, 110),
    "footwork": (155, 165), "juke": (155, 165),
    "jersey_club": (130, 145), "jerseyclub": (130, 145),   # KG name is the fused form
    "disco": (110, 125), "funk": (95, 115), "synthwave": (80, 118),
}


def tempo_window(genre):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if g in TEMPO_RANGES:
        return TEMPO_RANGES[g]
    for k, w in sorted(TEMPO_RANGES.items(), key=lambda kv: -len(kv[0])):
        if k in g:
            return w
    return None


def _backbeat_profile(song):
    """(backbeat_beats, hat_rate_per_beat): where the snare/clap family lands
    within the bar + hat event density (the halftime detector's two eyes)."""
    lanes = drum_lanes(song)
    bb_pos = []
    hat_rate = 0.0
    for role, t in lanes:
        if role in ("snare", "clap", "rim"):
            pos = _bar_pos(_onsets(t))
            for p in pos:
                if abs(p - round(p)) < 0.09:
                    bb_pos.append(int(round(p)) % 4)
        if role in ("hat", "ohat", "shaker"):
            ons = _onsets(t)
            if len(ons) >= 4:
                span = max(ons[-1] - ons[0], 1e-6)
                hat_rate = max(hat_rate, (len(ons) - 1) / span)
    from collections import Counter
    c = Counter(bb_pos)
    return c, hat_rate


def court_tempo(song, genre=""):
    win = tempo_window(genre)
    if not win:
        return {"court": "tempo", "ok": True, "skipped": f"no window for '{genre}'"}
    bpm = float(song.get("bpm", 0) or 0)
    if bpm <= 0:
        return {"court": "tempo", "ok": True, "skipped": "no bpm"}
    lo, hi = win
    if lo <= bpm <= hi:
        return {"court": "tempo", "ok": True, "bpm": bpm, "window": [lo, hi]}
    # HALFTIME RESOLVER (R-22): snare on beat 3 with hats at 2-4x = halftime;
    # validate the NOTATED window against 2x bpm (drill written at 70 = 140)
    c, hat_rate = _backbeat_profile(song)
    felt = None
    if c and c.get(2, 0) >= max(c.get(1, 0), c.get(3, 0)) and c.get(2, 0) > 0:
        felt = "halftime"
        for cand in (bpm * 2.0, bpm / 2.0):
            if lo <= cand <= hi:
                return {"court": "tempo", "ok": True, "bpm": bpm,
                        "felt": cand, "feel": "halftime", "window": [lo, hi]}
    return {"court": "tempo", "ok": False, "bpm": bpm, "window": [lo, hi],
            "feel": felt,
            "flags": [{"kind": "tempo_range",
                       "why": f"{bpm:g} bpm outside '{genre}' window "
                              f"[{lo}-{hi}] (halftime/double checked) — "
                              "genre tempo is identity, not preference"}]}


# ===================================================== R-21 KICK TOPOLOGY
_KICK_4X4 = ("house", "deep_house", "deephouse", "tech_house", "techno",
             "trance", "hardstyle", "hard_house", "gabber", "speed_garage",
             "disco", "hard_techno", "full_on", "fullon", "goa", "psytrance",
             "darkpsy", "hitech", "amapiano_main", "gqom_4x4")
_KICK_NO_4X4 = ("ukgarage", "ukg", "2step", "dnb", "drum_and_bass", "jungle",
                "breaks", "breakbeat", "trap", "drill", "boombap", "boom_bap",
                "hiphop", "footwork", "reggaeton", "dancehall",
                "jersey_club", "jerseyclub", "dubstep", "grime")   # one-drop's empty beat 1
                # is the DNA-mask court's law; steppers reggae is 4x4 idiom


def _kick_grid(song):
    """fraction of bars whose kick hits all four quarters; kick onset count."""
    kicks = [t for role, t in drum_lanes(song) if role == "kick"]
    if not kicks:
        return None, 0
    ons = sorted(s for t in kicks for s in _onsets(t))
    if not ons:
        return None, 0
    bars = {}
    for s in ons:
        b = int(s // 4)
        q = s % 4.0
        if abs(q - round(q)) < 0.09:
            bars.setdefault(b, set()).add(int(round(q)) % 4)
    if not bars:
        return 0.0, len(ons)
    full = sum(1 for qs in bars.values() if qs == {0, 1, 2, 3})
    return full / len(bars), len(ons)


def court_kick(song, genre=""):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    req = any(k == g or k in g for k in _KICK_4X4)
    forb = any(k == g or k in g for k in _KICK_NO_4X4)
    if not (req or forb):
        return {"court": "kick", "ok": True, "skipped": "no topology law"}
    ratio, n = _kick_grid(song)
    if ratio is None or n < 4:
        return {"court": "kick", "ok": True, "skipped": "no kick lane"}
    flags = []
    if req and ratio < 0.7:
        flags.append({"kind": "kick_topology",
                      "why": f"'{genre}' REQUIRES four-on-the-floor; only "
                             f"{ratio:.0%} of bars carry all four quarters"})
    if forb and ratio > 0.5:
        flags.append({"kind": "kick_topology",
                      "why": f"'{genre}' FORBIDS four-on-the-floor "
                             f"({ratio:.0%} of bars are 4x4) — the genre's "
                             "kick is syncopated/halftime by identity"})
    return {"court": "kick", "ok": not flags, "flags": flags,
            "four_on_floor_ratio": round(ratio, 3)}


# ======================================================= R-22 BACKBEAT LAW
_BB_24 = ("boombap", "boom_bap", "hiphop", "funk", "rock", "soul", "disco",
          "house", "pop", "rnb", "indie", "gospel", "motown", "lofi")
_BB_3 = ("trap", "drill", "phonk", "grime", "crunk", "memphis")


def court_backbeat(song, genre=""):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    want24 = any(k in g for k in _BB_24)
    want3 = any(k in g for k in _BB_3)
    if not (want24 or want3):
        return {"court": "backbeat", "ok": True, "skipped": "no backbeat law"}
    c, _ = _backbeat_profile(song)
    if not c:
        return {"court": "backbeat", "ok": True, "skipped": "no backbeat lane"}
    top = c.most_common(2)
    flags = []
    if want3 and not want24:
        if c.get(2, 0) < max(c.get(1, 0), c.get(3, 0)):
            flags.append({"kind": "backbeat",
                          "why": f"'{genre}' wants the halftime snare on "
                                 f"beat 3; measured backbeat histogram {dict(c)}"
                                 " — this is the wrong skeleton"})
    elif want24:
        good = c.get(1, 0) + c.get(3, 0)
        if good < c.get(0, 0) + c.get(2, 0):
            flags.append({"kind": "backbeat",
                          "why": f"'{genre}' wants snare/clap on 2&4; "
                                 f"measured histogram {dict(c)}"})
    return {"court": "backbeat", "ok": not flags, "flags": flags,
            "histogram": dict(c), "top": top}


# ========================================================= R-21 SWING COURT
# swing windows as OFF-16TH POSITION within the 8th pair (0.5 = straight);
# (window_lo, window_hi, dead_floor) per genre family. R-21: hats/perc within
# ~1 tick of straight in a swung genre = the #1 'screams fake' tell.
SWING_WINDOWS = {
    "ukgarage": (0.56, 0.70), "ukg": (0.56, 0.70), "2step": (0.56, 0.70),
    "speed_garage": (0.54, 0.66),
    "house": (0.52, 0.58), "deep_house": (0.53, 0.60), "deephouse": (0.53, 0.60),
    "boombap": (0.55, 0.62), "boom_bap": (0.55, 0.62),
    "hiphop": (0.54, 0.62), "neosoul": (0.54, 0.64), "neo_soul": (0.54, 0.64),
    "dilla": (0.55, 0.66), "lofi": (0.53, 0.64),
    "jungle": (0.52, 0.62), "breaks": (0.52, 0.62),
    "amapiano": (0.52, 0.60), "afrobeats": (0.52, 0.60),
    "swing": (0.58, 0.72), "jazz": (0.56, 0.72), "bebop": (0.55, 0.70),
    "funk": (0.51, 0.58), "disco": (0.51, 0.57),
}
_SWING_ROLES = ("hat", "ohat", "shaker", "perc", "ride")


def measured_swing(song, roles=_SWING_ROLES):
    """Mean off-16th position within its 8th pair across swing-carrying
    lanes: 0.5 = straight, 0.58 = MPC 58%. None when too few off-slots."""
    vals = []
    for role, t in drum_lanes(song):
        if role not in roles:
            continue
        for s in _onsets(t):
            pair = int(s / 0.5)
            frac = (s - pair * 0.5) / 0.5
            if 0.3 <= frac <= 0.85:                   # the off-16th zone
                vals.append(frac)
    if len(vals) < 6:
        return None
    return sum(vals) / len(vals)


def court_swing(song, genre=""):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    win = None
    for k, w in sorted(SWING_WINDOWS.items(), key=lambda kv: -len(kv[0])):
        if k in g:
            win = w
            break
    if not win:
        return {"court": "swing", "ok": True, "skipped": "straight-grid genre"}
    sw = measured_swing(song)
    if sw is None:
        return {"court": "swing", "ok": True, "skipped": "no swing-carrying offbeats"}
    lo, hi = win
    flags = []
    if sw < 0.52:
        flags.append({"kind": "dead_grid",
                      "why": f"off-16ths sit at {sw:.3f} (dead straight) — "
                             f"'{genre}' swings {lo:.2f}-{hi:.2f}; a "
                             "quantized grid is the #1 fake tell"})
    elif not (lo - 0.015 <= sw <= hi + 0.015):
        flags.append({"kind": "swing_window",
                      "why": f"measured swing {sw:.3f} outside '{genre}' "
                             f"window [{lo:.2f}-{hi:.2f}]"})
    return {"court": "swing", "ok": not flags, "flags": flags,
            "swing": round(sw, 4), "window": list(win)}


def heal_swing(song, genre="", verdict=None):
    """Apply the genre's swing as per-slot offsets to hats/perc/snare ONLY
    (kick+bass anchored — R-24). Off-grid onsets untouched. Edit ledger."""
    v = verdict or court_swing(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    lo, hi = v["window"]
    target = (lo + hi) / 2.0
    delay = (target - 0.5) * 0.5                      # beats late on off-16ths
    off = [0.0, delay, 0.0, delay] * 4
    vel = [1.0] * 16
    edits = []
    for role, t in drum_lanes(song):
        if role not in ("hat", "ohat", "shaker", "perc", "ride", "snare"):
            continue
        moved = 0
        for n in t.get("notes", []) or []:
            s = float(n.get("start", 0))
            slot_f = s / 0.25
            slot = int(round(slot_f))
            if abs(slot_f - slot) > 0.06 or slot % 2 == 0:
                continue
            n["start"] = round(slot * 0.25 + delay, 4)
            moved += 1
        if moved:
            edits.append({"track": t.get("name", "?"), "kind": "swing",
                          "target": round(target, 3), "moved": moved})
    return edits


# ==================================================== R-22 HI-HAT LANGUAGE
def court_hats(song, genre=""):
    g = str(genre or "").lower()
    lanes = [(r, t) for r, t in drum_lanes(song) if r in ("hat", "ohat")]
    if not lanes:
        return {"court": "hats", "ok": True, "skipped": "no hat lane"}
    flags = []
    machine = any(k in g for k in (
        "techno", "synthwave", "electro", "minimal", "gabber", "hardstyle",
        "industrial", "hitech", "psy", "goa", "trance", "dub_techno",
        "eurodance", "italo"))       # the machine IS the aesthetic there
    vels = [float(n.get("vel", 0.8)) for _, t in lanes
            for n in t.get("notes", [])]
    if len(vels) >= 12 and not machine:
        mean_v = sum(vels) / len(vels)
        sd = (sum((v - mean_v) ** 2 for v in vels) / len(vels)) ** 0.5
        if sd < 0.015:
            flags.append({"kind": "flat_velocity",
                          "why": f"hat velocities are near-constant (SD "
                                 f"{sd:.4f}) — the flattest AI tell; real "
                                 "hats breathe (ghosts 15-30% down)"})
    if any(k in g for k in ("trap", "drill", "phonk", "grime")):
        fine = False
        for _, t in lanes:
            ons = _onsets(t)
            for a, b in zip(ons, ons[1:]):
                gap = b - a
                if 0.05 < gap < 0.19 or abs(gap - 1.0 / 6.0) < 0.02 \
                        or abs(gap - 1.0 / 12.0) < 0.02:
                    fine = True
                    break
            if fine:
                break
        if not fine:
            flags.append({"kind": "no_rolls",
                          "why": f"'{genre}' hats carry 1/32 or triplet "
                                 "ROLLS into the snares — none found; the "
                                 "lane reads as a beginner grid"})
    if any(k in g for k in ("uk_drill", "ukdrill", "ny_drill", "grime")) \
            or g == "drill":
        want = {0, 3, 6, 9, 12, 15} & {0, 3, 6}
        got = set()
        for _, t in lanes:
            for s in _onsets(t):
                slot = round((s % 4.0) / 0.25)
                got.add(int(slot) % 16)
        # 3+3+2: steps {0,3,6} then {8,11,14} (R-22 drill polyrhythm)
        pattern = {0, 3, 6, 8, 11, 14}
        overlap = len(got & pattern) / len(pattern)
        if overlap < 0.5 and len(got) > 2:
            flags.append({"kind": "no_332",
                          "why": "drill/grime hats speak the 3+3+2 "
                                 f"polyrhythm (steps 0,3,6,8,11,14); overlap "
                                 f"{overlap:.0%}"})
    return {"court": "hats", "ok": not flags, "flags": flags}


def heal_hats(song, genre="", verdict=None, seed=11):
    """Velocity humanization (accent grammar from pocket_dna) + roll
    injection before snare backbeats for the roll genres."""
    v = verdict or court_hats(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    edits = []
    kinds = {f["kind"] for f in v.get("flags", [])}
    k = seed
    for role, t in drum_lanes(song):
        if role not in ("hat", "ohat"):
            continue
        if "flat_velocity" in kinds:
            for n in t.get("notes", []) or []:
                s = float(n.get("start", 0))
                pos16 = round((s % 1.0) / 0.25) % 4
                base = 0.82 if pos16 == 0 else (0.62 if pos16 == 2 else 0.55)
                k = (k * 1103515245 + 12345) & 0x7fffffff
                n["vel"] = round(min(1.0, max(0.1,
                                              base + ((k >> 8) % 100 - 50) / 100.0 * 0.16)), 3)
            edits.append({"track": t.get("name", "?"), "kind": "vel_grammar"})
        if "no_rolls" in kinds:
            snares = [tt for r2, tt in drum_lanes(song) if r2 in ("snare", "clap")]
            targets = []
            for st in snares[:1]:
                ons = _onsets(st)
                targets = [s for s in ons if s >= 1.0][:4]
            pitch = int((t.get("notes") or [{}])[0].get("pitch", 42))
            for tb in targets:
                t["notes"].extend(DG.hat_roll(tb - 0.5, 0.5, pitch=pitch,
                                              start_vel=0.4, end_vel=0.85,
                                              subdiv=0.125))
            if targets:
                edits.append({"track": t.get("name", "?"), "kind": "rolls",
                              "count": len(targets)})
    return edits


# ======================================================== R-3 JITTER COURT
def court_jitter(song, genre=""):
    """Random timing SD (residual after grid+swing) must stay <=60% of the
    genre's natural human SD (R-3 court law: over-humanize SUBTRACTS)."""
    # scale=1.0 clamps to 0.6 inside pocket_dna: cap = 60% of the natural SD
    cap = PD.humanize_sd_beats(genre, float(song.get("bpm", 120) or 120),
                               scale=1.0)
    flags, per_lane = [], {}
    for role, t in drum_lanes(song):
        ons = _onsets(t)
        if len(ons) < 8:
            continue
        # residual vs nearest 16th MINUS the per-slot-class median: groove
        # templates put STRUCTURE per slot (ghost early, backbeat late) —
        # only what remains after the slot model is random jitter (R-3)
        by_slot = {}
        for s in ons:
            q = round(s / 0.25) * 0.25
            d = s - q
            if abs(d) < 0.13:
                by_slot.setdefault(int(round(q / 0.25)) % 16, []).append(d)
        res = []
        for slot, ds in by_slot.items():
            med = sorted(ds)[len(ds) // 2]
            res.extend(d - med for d in ds)
        if len(res) < 8:
            continue
        var = sum(d * d for d in res) / len(res)
        sd = var ** 0.5
        per_lane[t.get("name", "?")] = round(sd, 4)
        if sd > max(cap, 0.008) and sd > 0.02:
            flags.append({"kind": "over_humanized", "track": t.get("name", "?"),
                          "sd": round(sd, 4), "cap": round(cap, 4),
                          "why": f"{t.get('name', '?')}: random timing SD "
                                 f"{sd:.3f} beats > 60% of the human SD "
                                 f"({cap:.3f}) — random jitter does not add "
                                 "groove; structure does"})
    return {"court": "jitter", "ok": not flags, "flags": flags,
            "cap": round(cap, 4), "per_lane": per_lane}


# ================================================= R-24 RHYTHMIC DNA MASKS
# 16-step onset masks per genre role (R-24 verified patterns)
DNA_MASKS = {
    "reggaeton": {"rim": {3, 6, 11, 14}, "perc": {3, 6, 11, 14},
                  "snare": {3, 6, 11, 14}},          # dembow
    "dembow": {"rim": {3, 6, 11, 14}},
    "maqsoum": {"kick": {0, 8}, "perc": {2, 6, 12}},
    "baladi": {"kick": {0, 2, 8}, "perc": {6, 12}},
    "saidi": {"kick": {0, 6, 8}, "perc": {2, 12}},
    "one_drop": {"kick": {8}, "rim": {8}},
    "reggae": {"kick": {8}},
    "malfuf": {"kick": {0, 6, 12}},                  # tresillo skeleton
    "son": {"clave": {0, 3, 6, 10, 12}},
    "jersey_club": {"kick": {0, 4, 8, 11, 14}},      # the 5-kick signature
    "jerseyclub": {"kick": {0, 4, 8, 11, 14}},       # …under the KG's fused name too
}


def court_dna_mask(song, genre=""):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    masks = None
    for k, m in DNA_MASKS.items():
        if k in g:
            masks = m
            break
    if not masks:
        return {"court": "dna_mask", "ok": True, "skipped": "no DNA mask"}
    flags, detail = [], {}
    for role, t in drum_lanes(song):
        if role not in masks:
            continue
        mask = masks[role]
        got = set()
        for s in _onsets(t):
            slot = round((s % 4.0) / 0.25)
            got.add(int(slot) % 16)
        if not got:
            continue
        hit = len(got & mask) / len(mask)
        extra = len(got - mask) / max(len(got), 1)
        detail[t.get("name", "?")] = {"hit": round(hit, 3),
                                      "extra": round(extra, 3),
                                      "mask": sorted(mask)}
        if hit < 0.6:
            flags.append({"kind": "dna_mask", "track": t.get("name", "?"),
                          "role": role,
                          "why": f"{t.get('name', '?')} hits only {hit:.0%} "
                                 f"of the '{g}' {role} DNA (steps "
                                 f"{sorted(mask)}) — the genre's skeleton is "
                                 "its identity"})
    return {"court": "dna_mask", "ok": not flags, "flags": flags,
            "detail": detail}


def heal_dna_mask(song, genre="", verdict=None):
    """Snap the flagged role lane's off-mask onsets to the nearest mask slot
    (never adds or deletes — conservative)."""
    v = verdict or court_dna_mask(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    edits = []
    by_name = {t.get("name", "?"): t for _, t in drum_lanes(song)}
    for f in v.get("flags", []):
        t = by_name.get(f.get("track"))
        if not t:
            continue
        mask = sorted(v["detail"][f["track"]]["mask"])
        for n in t.get("notes", []) or []:
            s = float(n.get("start", 0))
            bar = int(s // 4)
            slot = (s % 4.0) / 0.25
            if abs(slot - round(slot)) > 0.06:
                continue
            slot = int(round(slot)) % 16
            if slot in mask:
                continue
            nearest = min(mask, key=lambda m: min(abs(m - slot), 16 - abs(m - slot)))
            new_s = bar * 4.0 + nearest * 0.25
            edits.append({"track": f["track"], "from": s, "to": new_s,
                          "kind": "mask_snap"})
            n["start"] = round(new_s, 4)
    return edits


# ========================================================== R-24 CLAVE LAW
_CLAVE_32 = {0, 3, 6, 10, 12}
_CLAVE_23 = {2, 4, 8, 11, 14}


def court_clave(song, genre=""):
    g = str(genre or "").lower()
    if not any(k in g for k in ("salsa", "son", "timba", "bossa", "mambo",
                                "rumba", "latin_jazz", "songo")):
        return {"court": "clave", "ok": True, "skipped": "no clave law"}
    votes = {}
    for role, t in drum_lanes(song):
        if role not in ("perc", "rim", "clap") and "clave" not in \
                str(t.get("name", "")).lower():
            continue
        got = set()
        for s in _onsets(t):
            slot = round((s % 4.0) / 0.25)
            got.add(int(slot) % 16)
        if len(got) < 3:
            continue
        f32 = len(got & _CLAVE_32) / len(_CLAVE_32)
        f23 = len(got & _CLAVE_23) / len(_CLAVE_23)
        if max(f32, f23) >= 0.5:
            votes[t.get("name", "?")] = "3-2" if f32 >= f23 else "2-3"
    dirs = set(votes.values())
    flags = []
    if len(dirs) > 1:
        flags.append({"kind": "cruzao", "votes": votes,
                      "why": f"clave direction disagreement {votes} — a "
                             "cruzao (crossed-clave) take is the single "
                             "most-recognizable Latin authenticity fail"})
    return {"court": "clave", "ok": not flags, "flags": flags, "votes": votes}


# ========================================================= R-4 FILL COURT
def court_fills(song, genre=""):
    secs = sorted((s for s in song.get("sections", []) or []
                   if isinstance(s, dict)),
                  key=lambda s: float(s.get("startBar", 0)))
    if len(secs) < 2:
        return {"court": "fills", "ok": True, "skipped": "no sections"}
    must = []
    for a, b in zip(secs, secs[1:]):
        an = str(a.get("name", "")).lower()
        bn = str(b.get("name", "")).lower()
        if (("verse" in an and ("chorus" in bn or "hook" in bn))
                or ("build" in an and "drop" in bn)
                or ("pre" in an and ("chorus" in bn or "drop" in bn))):
            must.append((a, b))
    if not must:
        return {"court": "fills", "ok": True, "skipped": "no MUST boundaries"}
    drums = [t for _, t in drum_lanes(song)]
    length_beats = float(song.get("lengthBars", 8) or 8) * 4.0
    fx_lanes = [t for t in song.get("tracks", []) or []
                if isinstance(t, dict) and any(
                    w in str(t.get("name", "")).lower()
                    for w in ("riser", "sweep", "fx", "impact", "noise",
                              "uplifter", "swoosh", "crash"))]
    flags = []
    for a, b in must:
        bnd = float(b.get("startBar", 0)) * 4.0
        if bnd >= length_beats - 4.0:
            continue                     # the "drop" at the END is an outro tag
        pre = [s for t in drums for s in _onsets(t) if bnd - 2.0 <= s < bnd]
        base = [s for t in drums for s in _onsets(t) if bnd - 6.0 <= s < bnd - 4.0]
        fill_rise = len(pre) >= max(len(base) * 1.3, 4)
        gap_idiom = base and len(pre) <= len(base) * 0.4   # the pre-drop GAP
        fx_signal = any(
            (bnd - 8.0 <= float(n.get("start", -99)) < bnd + 0.5)
            for t in fx_lanes for n in (t.get("notes") or [])) or any(
            (bnd - 8.0 <= float(c.get("startBeat", -99)) + float(c.get("lengthBeats", 0)) <= bnd + 1.0)
            for t in fx_lanes for c in (t.get("audioClips") or []))
        if not (fill_rise or gap_idiom or fx_signal):
            flags.append({"kind": "no_fill", "boundary": b.get("name", "?"),
                          "at_bar": float(b.get("startBar", 0)),
                          "why": f"{a.get('name', '?')} -> {b.get('name', '?')} "
                                 "has NO transition signal (no fill rise, no "
                                 "pre-drop gap, no riser/crash) — this seam "
                                 "is a p=0.95 fill site"})
    return {"court": "fills", "ok": not flags, "flags": flags}


def heal_fills(song, genre="", verdict=None):
    v = verdict or court_fills(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    edits = []
    snare = next((t for r, t in drum_lanes(song) if r in ("snare", "clap")), None)
    # crash lanes are often EMPTY until the first fill lands — scan all tracks
    crash = next((t for t in song.get("tracks", []) or []
                  if isinstance(t, dict) and not t.get("muted")
                  and DG.drum_role(t.get("name")) == "crash"), None)
    if not snare:
        return []
    pitch = int((snare.get("notes") or [{}])[0].get("pitch", 38))
    for f in v.get("flags", []):
        bnd = float(f["at_bar"]) * 4.0
        notes, crash_note = DG.fill(genre, bnd, kind="half", snare_pitch=pitch)
        snare["notes"].extend(notes)
        if crash is not None:
            cp = int((crash.get("notes") or [{"pitch": 49}])[0].get("pitch", 49))
            crash_note["pitch"] = cp
            crash.setdefault("notes", []).append(crash_note)
        edits.append({"kind": "fill", "boundary": f["boundary"],
                      "notes": len(notes), "crash": crash is not None})
    return edits


# ========================================================= R-4 GHOST COURT
_GHOST_GENRES = ("funk", "neosoul", "neo_soul", "dilla", "dnb", "boombap",
                 "boom_bap", "soul", "gospel")


def court_ghosts(song, genre=""):
    g = str(genre or "").lower()
    if not any(k in g for k in _GHOST_GENRES):
        return {"court": "ghosts", "ok": True, "skipped": "no ghost law"}
    snares = [t for r, t in drum_lanes(song) if r == "snare"
              and not any(w in str(t.get("name", "")).lower()
                          for w in ("_body", "_top", "_layer", "_crack",
                                    "_air", "_room"))]
    if not snares:
        return {"court": "ghosts", "ok": True, "skipped": "no snare lane"}
    snares = [max(snares, key=lambda t: len(t.get("notes") or []))]
    flags = []
    for t in snares:
        vels = [float(n.get("vel", 0.8)) for n in t.get("notes", [])]
        if len(vels) < 4:
            continue
        soft = sum(1 for v in vels if v < 0.5)
        if soft == 0:
            flags.append({"kind": "no_ghosts", "track": t.get("name", "?"),
                          "why": f"'{genre}' snare wants GHOST notes "
                                 "(0.30-0.45x taps around the backbeat) — "
                                 "every hit here is a main hit"})
    return {"court": "ghosts", "ok": not flags, "flags": flags}


def heal_ghosts(song, genre="", verdict=None):
    v = verdict or court_ghosts(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    edits = []
    by_name = {t.get("name", "?"): t for _, t in drum_lanes(song)}
    for f in v.get("flags", []):
        t = by_name.get(f.get("track"))
        if not t:
            continue
        ghosts = DG.ghost_snares(t.get("notes"), int(song.get("lengthBars", 8)),
                                 genre=genre)
        t["notes"].extend(ghosts)
        edits.append({"track": f["track"], "kind": "ghosts", "added": len(ghosts)})
    return edits


# ====================================================== R-4 LAYERING COURT
_ZONE = {"kick": "sub", "snare": "mid", "clap": "mid", "rim": "mid",
         "tom": "mid", "perc": "mid", "cowbell": "mid",
         "hat": "top", "ohat": "top", "ride": "top", "crash": "top",
         "shaker": "top"}
_ZONE_CAP = {"sub": 2, "mid": 4, "top": 4}


def court_layering(song, genre=""):
    counts = {}
    for role, t in drum_lanes(song):
        z = _ZONE.get(role)
        if z:
            counts[z] = counts.get(z, 0) + 1
    flags = []
    for z, cap in _ZONE_CAP.items():
        if counts.get(z, 0) > cap:
            flags.append({"kind": "zone_stack", "zone": z,
                          "count": counts[z], "cap": cap,
                          "why": f"{counts[z]} active {z}-zone drum lanes "
                                 f"(cap {cap}) — extra same-zone layers "
                                 "multiply phase risk, not power"})
    return {"court": "layering", "ok": not flags, "flags": flags,
            "zones": counts}


# ================================================= R-22 AI-TELL COMPOSITE
def court_ai_tells(song, genre=""):
    """One authenticity meta-verdict: each tell = evidence from a sub-court.
    Score = 1 - tells/possible. Conviction only at >=3 tells (the composite
    is a REPORT; individual courts carry their own convictions)."""
    tells = []
    sub = {"swing": court_swing(song, genre),
           "hats": court_hats(song, genre),
           "backbeat": court_backbeat(song, genre),
           "kick": court_kick(song, genre),
           "jitter": court_jitter(song, genre)}
    if any(f["kind"] == "dead_grid" for f in sub["swing"].get("flags", [])):
        tells.append("dead_straight_grid")
    if any(f["kind"] == "flat_velocity" for f in sub["hats"].get("flags", [])):
        tells.append("flat_hat_velocity")
    if not sub["backbeat"].get("ok", True):
        tells.append("wrong_backbeat")
    if not sub["kick"].get("ok", True):
        tells.append("wrong_kick_topology")
    if not sub["jitter"].get("ok", True):
        tells.append("random_jitter_overdose")
    # per-4-bar variation (R-22: no change every 4 bars = generated feel)
    drums = [t for _, t in drum_lanes(song)]
    if drums:
        sigs = []
        length = int(float(song.get("lengthBars", 8) or 8))
        for w in range(0, max(length - 3, 1), 4):
            sig = []
            for t in drums:
                slots = sorted(round((s - w * 4.0) / 0.25)
                               for s in _onsets(t)
                               if w * 4.0 <= s < (w + 4) * 4.0)
                sig.append(tuple(slots))
            sigs.append(tuple(sig))
        if len(sigs) >= 3 and len(set(sigs)) == 1 and any(s for s in sigs[0]):
            tells.append("no_4bar_variation")
    score = round(1.0 - len(tells) / 6.0, 3)
    return {"court": "ai_tells", "ok": len(tells) < 3, "tells": tells,
            "authenticity": score}


# ================================================================ aggregate
def court_groove(song, genre="", heal=False):
    out = {"tempo": court_tempo(song, genre),
           "kick": court_kick(song, genre),
           "backbeat": court_backbeat(song, genre),
           "swing": court_swing(song, genre),
           "hats": court_hats(song, genre),
           "jitter": court_jitter(song, genre),
           "dna_mask": court_dna_mask(song, genre),
           "clave": court_clave(song, genre),
           "fills": court_fills(song, genre),
           "ghosts": court_ghosts(song, genre),
           "layering": court_layering(song, genre)}
    if heal:
        heals = {}
        for name, healer, courter in (
                ("swing", heal_swing, court_swing),
                ("hats", heal_hats, court_hats),
                ("dna_mask", heal_dna_mask, court_dna_mask),
                ("fills", heal_fills, court_fills),
                ("ghosts", heal_ghosts, court_ghosts)):
            if not out[name].get("ok", True):
                heals[name] = healer(song, genre, out[name])
                out[f"{name}_after"] = courter(song, genre)
        out["heals"] = heals
    out["ai_tells"] = court_ai_tells(song, genre)
    out["ok"] = all(v.get("ok", True) for k, v in out.items()
                    if isinstance(v, dict) and not k.endswith("_after"))
    return out


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description="THE GROOVE COURT (wave 14)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song))
    v = court_groove(song, args.genre, heal=args.heal)
    if args.heal and v.get("heals"):
        with open(args.song, "w") as f:
            json.dump(song, f, indent=1)
        v["saved"] = args.song
    print(json.dumps(v, indent=1))
    return 0 if v["ok"] or args.heal else 1


if __name__ == "__main__":
    sys.exit(main())
