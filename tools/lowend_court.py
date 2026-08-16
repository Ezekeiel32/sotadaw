#!/usr/bin/env python3
"""THE LOW-END COURT — symbolic side (backlog wave 15; R-4/R-5/R-21/R-25).

Deterministic kick/bass relationship courts on song.json (the audio-domain
twins live in tools/lowend_ears.py). Sources: r-{4,5,21,25}.json.

  court_interlock(song, genre)   R-4/R-21: four-on-floor genres want the bass
                                 OFF the kicks (offbeat) or a pump fx; 808
                                 genres want the kick transient / 808 sustain
                                 split. The universal 'muddy/fake' tell.
  heal_interlock(song, genre, v) insert tempo-locked fx_pump on the bass
                                 (sidechain kernel) — the classic fix
  court_kbbb(song, genre)        R-25: psy full-on/goa/dark — NO bass note
                                 may SOUND during a kick 16th; bass lives on
                                 16ths 2/3/4 and stays inside its window
  heal_kbbb(song, genre, v)      nudge offending bass onsets off the kick +
                                 clamp lengths to the 16th window
  sidechain_release_ms(bpm, ...) R-5 kernel: release = beat fraction, never
                                 an LLM guess; attack <10ms, depth by genre
  court_sidechain(song, genre)   pump genres: bass/bus carries fx_pump with
                                 a tempo-locked rate (advisory when off)
  court_808_env(song, genre)     R-5: source decay/glide params vs the KG
                                 genre window (trap sustained, drill tight)
  court_sub_width(song)          R-16: width on sub lanes = hard FAIL
                                 (mirrors doctor's trap as a court verdict)
  court_foley(song)              R-18: foley/texture lanes sit UNDER the kit
                                 (low gain) and out of the sub (HP'd)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drum_grammar as DG  # noqa: E402

# R-5 sidechain depth by genre family (dB of duck)
PUMP_DEPTH = (
    (("house", "techno", "trance", "edm", "electro", "festival", "big_room",
      "hardstyle", "french_house", "synthwave"), (6.0, 10.0)),
    (("hiphop", "hip_hop", "trap", "drill", "pop", "rnb", "r_b", "phonk",
      "boombap", "lofi"), (3.0, 6.0)),
)
_PUMP_GENRES = tuple(k for keys, _ in PUMP_DEPTH for k in keys)

# R-5 genre 808 envelope + glide windows (ms). CORPUS-CALIBRATED (the R-16
# self-measure law, 2026-07-15): Chezy's accepted drill-family takes run
# kick_808 decay 450ms, eval_drill (blind-judge winner) 1800ms — the
# research's 'drill tight' meant note CHOKE, not tail seconds. Windows are
# wide enough to hold every corpus winner and still catch the real crimes
# (sub-100ms choked trap 808s, 3s drones under 4x4).
ENV_808 = {
    "trap":  {"decay_ms": (300, 1200), "glide_ms": (80, 120)},
    "drill": {"decay_ms": (250, 2000), "glide_ms": (20, 120)},
    "phonk": {"decay_ms": (250, 900), "glide_ms": (40, 100)},
    "house": {"decay_ms": (80, 400)}, "techno": {"decay_ms": (80, 400)},
}


def bass_lanes(song):
    out = []
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if any(w in nm for w in ("bass", "808", "sub")) and \
                "sketch" not in nm and (t.get("notes") or []):
            out.append(t)
    return out


def kick_onsets(song):
    ons = []
    for role, t in [(DG.drum_role(t.get("name")), t)
                    for t in song.get("tracks", []) or []
                    if isinstance(t, dict) and not t.get("muted")]:
        if role == "kick":
            ons.extend(float(n.get("start", 0)) for n in t.get("notes") or [])
    return sorted(ons)


def _fx_ids(t):
    return [str(f.get("id", f.get("type", ""))).lower()
            for f in (t.get("fx") or []) if isinstance(f, dict)]


def _has_pump(song, t):
    if any("pump" in f for f in _fx_ids(t)):
        return True
    for b in song.get("buses", []) or []:
        if isinstance(b, dict) and any("pump" in str(f.get("id", f.get("type", ""))).lower()
                                       for f in (b.get("fx") or [])):
            return True
    return False


# ============================================== R-4/R-21 KICK<->BASS INTERLOCK
def court_interlock(song, genre=""):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    four = any(k in g for k in ("house", "techno", "trance", "hardstyle",
                                "disco", "edm", "electro", "gabber"))
    is808 = any(k in g for k in ("trap", "drill", "phonk", "hiphop", "hip_hop",
                                 "boombap", "rap", "grime"))
    if not (four or is808):
        return {"court": "interlock", "ok": True, "skipped": "no interlock law"}
    kicks = kick_onsets(song)
    lanes = bass_lanes(song)
    if not kicks or not lanes:
        return {"court": "interlock", "ok": True, "skipped": "needs kick + bass"}
    flags, advisories = [], []
    for t in lanes:
        notes = t.get("notes") or []
        overlap = 0
        for n in notes:
            s = float(n.get("start", 0))
            if any(abs(s - k) < 0.13 for k in kicks):
                overlap += 1
        ratio = overlap / max(len(notes), 1)
        if four and ratio > 0.5 and not _has_pump(song, t):
            flags.append({"kind": "kick_bass_pileup", "track": t.get("name", "?"),
                          "overlap": round(ratio, 3),
                          "why": f"{t.get('name', '?')}: {ratio:.0%} of bass "
                                 "onsets land ON the four-on-floor kicks with "
                                 "no sidechain pump — the universal mud tell; "
                                 "offbeat the bass or duck it"})
        if is808:
            # 808-as-kick-tail is a REAL production style (one-shot 808 under
            # every kick), so full shadowing is an ADVISORY, never a conviction
            same = sum(1 for n in notes
                       if any(abs(float(n.get("start", 0)) - k) < 0.02
                              for k in kicks))
            if len(notes) >= 6 and same == len(notes):
                advisories.append({
                    "kind": "shadow_808", "track": t.get("name", "?"),
                    "why": f"{t.get('name', '?')}: every 808 onset shadows a "
                           "kick 1:1 — consider letting the 808 phrase "
                           "independently (slides, pickups, rests)"})
    return {"court": "interlock", "ok": not flags, "flags": flags,
            "advisories": advisories}


def sidechain_release_ms(bpm, note_fraction=0.25):
    """R-5 KERNEL: release = 60000/bpm * fraction (1/8 = 0.5, 1/16 = 0.25).
    Tempo-locked, never guessed."""
    return 60000.0 / max(float(bpm), 1.0) * (note_fraction / 0.25) * 0.25


def pump_params(bpm, genre=""):
    """fx_pump params for the genre: rate (duck events/s at quarter = bpm/60),
    depth from the family table, release s tempo-locked to a 16th..8th."""
    g = str(genre or "").lower()
    depth_db = 6.0
    for keys, (lo, hi) in PUMP_DEPTH:
        if any(k in g for k in keys):
            depth_db = (lo + hi) / 2.0
            break
    rel_s = sidechain_release_ms(bpm, 0.5) / 1000.0
    return {"rate": round(float(bpm) / 60.0, 3),
            "depth": round(min(depth_db / 12.0, 1.0), 3),
            "release": round(max(min(rel_s, 0.7), 0.05), 3)}


def heal_interlock(song, genre="", verdict=None):
    """Insert a tempo-locked fx_pump on convicted bass lanes (the classic
    four-on-floor fix). Mutates; returns edit ledger."""
    v = verdict or court_interlock(song, genre)
    edits = []
    if v.get("ok", True) or v.get("skipped"):
        return edits
    params = pump_params(float(song.get("bpm", 120) or 120), genre)
    by_name = {t.get("name", "?"): t for t in bass_lanes(song)}
    for f in v.get("flags", []):
        if f.get("kind") != "kick_bass_pileup":
            continue
        t = by_name.get(f.get("track"))
        if not t or _has_pump(song, t):
            continue
        t.setdefault("fx", []).append({"id": "fx_pump", "params": dict(params)})
        edits.append({"track": f["track"], "kind": "pump_insert", **params})
    return edits


# ========================================================= R-25 KBBB COURT
_KBBB = ("full_on", "fullon", "goa", "darkpsy", "forest", "psytrance",
         "hitech", "psycore")


def court_kbbb(song, genre=""):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if not any(k in g for k in _KBBB):
        return {"court": "kbbb", "ok": True, "skipped": "not a psy-rolling genre"}
    kicks = kick_onsets(song)
    lanes = bass_lanes(song)
    if not kicks or not lanes:
        return {"court": "kbbb", "ok": True, "skipped": "needs kick + bass"}
    flags = []
    for t in lanes:
        bad_onset, bad_len = [], 0
        for n in t.get("notes") or []:
            s = float(n.get("start", 0))
            ln = float(n.get("len", n.get("length", 0.25)))
            if any(abs(s - k) < 0.11 for k in kicks):
                if len(bad_onset) < 24:
                    bad_onset.append(round(s, 3))
            if ln > 0.26:
                bad_len += 1
        if bad_onset or bad_len > 2:
            flags.append({"kind": "kbbb", "track": t.get("name", "?"),
                          "on_kick": bad_onset, "long_notes": bad_len,
                          "why": f"{t.get('name', '?')}: psy rolling bass "
                                 "lives on 16ths 2/3/4 BETWEEN kicks (found "
                                 f"{len(bad_onset)} on-kick onsets, {bad_len} "
                                 "notes longer than a 16th) — the KBBB law"})
    return {"court": "kbbb", "ok": not flags, "flags": flags}


def heal_kbbb(song, genre="", verdict=None):
    """Nudge on-kick bass onsets to the next free 16th + clamp lengths to
    the 16th window. Mutates; returns edit ledger."""
    v = verdict or court_kbbb(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    kicks = kick_onsets(song)
    edits = []
    by_name = {t.get("name", "?"): t for t in bass_lanes(song)}
    for f in v.get("flags", []):
        t = by_name.get(f.get("track"))
        if not t:
            continue
        taken = {round(float(n.get("start", 0)) * 4)
                 for n in t.get("notes") or []}
        for n in t.get("notes") or []:
            s = float(n.get("start", 0))
            ln = float(n.get("len", n.get("length", 0.25)))
            if any(abs(s - k) < 0.11 for k in kicks):
                for cand in (s + 0.25, s - 0.25, s + 0.5):
                    key = round(cand * 4)
                    if cand >= 0 and key not in taken and \
                            not any(abs(cand - k) < 0.11 for k in kicks):
                        taken.discard(round(s * 4))
                        taken.add(key)
                        edits.append({"track": f["track"], "kind": "nudge",
                                      "from": s, "to": round(cand, 4)})
                        n["start"] = round(cand, 4)
                        break
            if ln > 0.26:
                n["len"] = 0.22
                edits.append({"track": f["track"], "kind": "clamp_len",
                              "at": s})
    return edits


# ==================================================== R-5 SIDECHAIN COURT
def court_sidechain(song, genre=""):
    """Pump genres: when kick + bass coexist, SOME duck path should exist
    (fx_pump on bass/bus). Advisory-only court (mix taste varies)."""
    g = str(genre or "").lower()
    if not any(k in g for k in _PUMP_GENRES):
        return {"court": "sidechain", "ok": True, "skipped": "no pump law"}
    lanes = bass_lanes(song)
    kicks = kick_onsets(song)
    if not lanes or not kicks:
        return {"court": "sidechain", "ok": True, "skipped": "needs kick + bass"}
    advisories = []
    bpm = float(song.get("bpm", 120) or 120)
    for t in lanes:
        if _has_pump(song, t):
            for f in (t.get("fx") or []):
                if "pump" in str(f.get("id", "")).lower():
                    want = pump_params(bpm, genre)
                    got = float((f.get("params") or {}).get("rate", 0) or 0)
                    if got and abs(got - want["rate"]) > 0.55:
                        advisories.append({
                            "kind": "pump_rate_offgrid",
                            "track": t.get("name", "?"),
                            "why": f"fx_pump rate {got} vs tempo-locked "
                                   f"{want['rate']} (bpm/60) — the duck "
                                   "should breathe with the kick"})
        else:
            advisories.append({"kind": "no_pump", "track": t.get("name", "?"),
                               "why": f"'{genre}' usually ducks the bass "
                                      "under the kick (fx_pump, release "
                                      f"{pump_params(bpm, genre)['release']}s "
                                      "tempo-locked)"})
    return {"court": "sidechain", "ok": True, "advisories": advisories}


# ===================================================== R-5 808 ENV COURT
def court_808_env(song, genre=""):
    g = str(genre or "").lower()
    win = None
    for k, w in ENV_808.items():
        if k in g:
            win = w
            break
    if not win:
        return {"court": "env808", "ok": True, "skipped": "no 808 env law"}
    flags = []
    for t in bass_lanes(song):
        src = t.get("source") or {}
        sid = str(src.get("id", "")).lower()
        if "808" not in sid and "sub" not in sid:
            continue
        params = src.get("params") or {}
        decay_s = params.get("decay")
        if decay_s is not None and "decay_ms" in win:
            lo, hi = win["decay_ms"]
            ms = float(decay_s) * 1000.0
            if not (lo * 0.7 <= ms <= hi * 1.4):
                flags.append({"kind": "env808", "track": t.get("name", "?"),
                              "decay_ms": ms, "window": [lo, hi],
                              "why": f"{t.get('name', '?')}: 808 decay "
                                     f"{ms:.0f}ms vs '{g}' window "
                                     f"[{lo}-{hi}]ms (trap sustains, drill "
                                     "chokes)"})
        slide = params.get("slide")
        if slide is not None and "glide_ms" in win:
            lo, hi = win["glide_ms"]
            if not (lo * 0.5 <= float(slide) <= hi * 1.6):
                flags.append({"kind": "glide808", "track": t.get("name", "?"),
                              "slide_ms": float(slide), "window": [lo, hi],
                              "why": f"slide {slide}ms vs '{g}' glide window "
                                     f"[{lo}-{hi}]ms"})
    return {"court": "env808", "ok": not flags, "flags": flags}


def heal_env808(song, genre="", verdict=None):
    """Clamp out-of-window 808 decay/slide to the NEAREST window edge —
    deterministic, native units (decay seconds, slide ms). Mutates."""
    v = verdict or court_808_env(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    edits = []
    by_name = {t.get("name", "?"): t for t in bass_lanes(song)}
    for f in v.get("flags", []):
        t = by_name.get(f.get("track"))
        if not t:
            continue
        params = (t.get("source") or {}).setdefault("params", {})
        lo, hi = f["window"]
        if f["kind"] == "env808":
            new_s = round(min(max(f["decay_ms"], lo), hi) / 1000.0, 3)
            edits.append({"track": f["track"], "kind": "decay_clamp",
                          "old_s": params.get("decay"), "new_s": new_s})
            params["decay"] = new_s
        elif f["kind"] == "glide808":
            new_ms = round(min(max(f["slide_ms"], lo), hi), 1)
            edits.append({"track": f["track"], "kind": "slide_clamp",
                          "old_ms": params.get("slide"), "new_ms": new_ms})
            params["slide"] = new_ms
    return edits


# ============================================ 097 FREQUENCY-DIVISION COURT
def court_freq_division(song, genre=""):
    """Item 097 (r-25): psy kick/bass separation is by FREQUENCY
    DIVISION, never tuning — 'tuning the kick to the track key is one of
    the most damaging mistakes'. The bass owns the sub (<60Hz); the kick
    keeps click + punch (60-100Hz). Convicts a psy take whose kick lane
    rides a BOOM-class source (sub-heavy 808 family) with no carve;
    heal = fx_bell cut at the bass root's fundamental on the kick lane
    (surgical, catalog-lawful — fx_hipass on kicks is the general law's
    forbidden move, the bell is the psy exception's tool)."""
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    if not any(k in g for k in _KBBB):
        return {"court": "freq_division", "ok": True,
                "skipped": "not a psy genre"}
    lanes = bass_lanes(song)
    if not lanes:
        return {"court": "freq_division", "ok": True,
                "skipped": "no bass lane"}
    flags = []
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if "kick" not in nm or nm.endswith(("_sketch", "_identity")):
            continue
        sid = str((t.get("source") or {}).get("id", "")).lower()
        boomy = any(w in sid for w in ("808", "sub", "boom"))
        carved = any("bell" in f or "hipass" in f or "filter" in f
                     for f in _fx_ids(t))
        if boomy and not carved:
            flags.append({
                "kind": "kick_owns_sub", "track": t.get("name", "?"),
                "source": sid,
                "why": f"{t.get('name', '?')} rides a boom-class voice "
                       f"({sid}) into a psy take with no carve — the "
                       "BASS owns the sub; cut the kick at the bass "
                       "root's frequencies (frequency division, never "
                       "retuning)"})
    return {"court": "freq_division", "ok": not flags, "flags": flags}


def heal_freq_division(song, genre="", verdict=None):
    """fx_bell cut on the convicted kick at the bass root's fundamental
    (-4dB, q 2). The bass root = the bass lane's most common pitch.
    Idempotent (skips lanes already carrying a bell). Mutates."""
    v = verdict or court_freq_division(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    lanes = bass_lanes(song)
    pitches = [int(n.get("pitch", 33)) for t in lanes
               for n in t.get("notes") or []]
    if not pitches:
        return []
    root = max(set(pitches), key=pitches.count)
    hz = 440.0 * 2 ** ((root - 69) / 12.0)
    edits = []
    by_name = {str(t.get("name", "")): t
               for t in song.get("tracks", []) or [] if isinstance(t, dict)}
    for f in v.get("flags", []):
        t = by_name.get(f.get("track"))
        if t is None or any("bell" in x for x in _fx_ids(t)):
            continue
        t.setdefault("fx", []).insert(0, {
            "id": "fx_bell",
            "params": {"freq": round(hz, 1), "gain": -4.0, "q": 2.0}})
        edits.append({"track": f["track"], "kind": "kick_carve",
                      "hz": round(hz, 1)})
    return edits


# ==================================================== R-16 SUB WIDTH COURT
def court_sub_width(song):
    """Width on a sub lane = phase-cancellation on every club/phone system.
    The one genre-independent hard floor (doctor's trap, court-shaped)."""
    flags = []
    for t in bass_lanes(song):
        nm = str(t.get("name", "")).lower()
        if not any(w in nm for w in ("sub", "808")):
            continue
        pan = float(t.get("pan", 0) or 0)
        if abs(pan) > 0.12:
            flags.append({"kind": "panned_sub", "track": t.get("name", "?"),
                          "pan": pan,
                          "why": f"{t.get('name', '?')} panned {pan:+.2f} — "
                                 "the sub is a MONO CENTER instrument, "
                                 "always"})
        for f in (t.get("fx") or []):
            fid = str(f.get("id", f.get("type", ""))).lower()
            if "widen" in fid:
                flags.append({"kind": "widened_sub",
                              "track": t.get("name", "?"),
                              "why": f"fx_widen on {t.get('name', '?')} — "
                                     "side energy below 120Hz cancels on "
                                     "mono systems; width belongs above"})
    return {"court": "sub_width", "ok": not flags, "flags": flags}


def heal_sub_width(song, verdict=None):
    v = verdict or court_sub_width(song)
    if v.get("ok", True):
        return []
    edits = []
    by_name = {t.get("name", "?"): t for t in bass_lanes(song)}
    for f in v.get("flags", []):
        t = by_name.get(f.get("track"))
        if not t:
            continue
        if f["kind"] == "panned_sub":
            edits.append({"track": f["track"], "kind": "center",
                          "old_pan": t.get("pan")})
            t["pan"] = 0.0
        elif f["kind"] == "widened_sub":
            t["fx"] = [x for x in (t.get("fx") or [])
                       if "widen" not in str(x.get("id", x.get("type", ""))).lower()]
            edits.append({"track": f["track"], "kind": "unwiden"})
    return edits


# ================================================ 064 DELAY GRID COURT (w39)
_DIVISIONS = (("1/4", 1.0), ("1/8", 0.5), ("3/16", 0.75), ("1/16", 0.25),
              ("1/8T", 1.0 / 3.0), ("1/2", 2.0), ("3/8", 1.5))


def note_division_ms(bpm, division):
    """R-12 law verbatim: delay time = a NOTE DIVISION of the bpm,
    never raw ms (quarter = 60000/bpm; dotted x1.5; triplet x2/3)."""
    q = 60000.0 / max(float(bpm), 1.0)
    for name, mult in _DIVISIONS:
        if name == division:
            return round(q * mult, 2)
    return round(q, 2)


def court_delay_grid(song, genre=""):
    """Every fx_delay's time must sit ON a division of the song's bpm
    (+-5%) — the off-grid echo is the classic amateur tell (it fights
    the groove on every repeat). SLAPBACK EXEMPTION: 80-120ms with
    feedback ~0 is a time-domain effect, not a rhythmic one (r-12:
    rock/country staple). Heal snaps to the nearest division."""
    bpm = float((song or {}).get("bpm", 120) or 120)
    q = 60000.0 / bpm
    flags, advisories = [], []
    for scope in (song.get("tracks", []) or []) + \
            (song.get("buses", []) or []):
        if not isinstance(scope, dict) or scope.get("muted"):
            continue
        for f in scope.get("fx") or []:
            if str(f.get("id", "")) != "fx_delay":
                continue
            t = float((f.get("params") or {}).get("time", 375) or 375)
            fb = float((f.get("params") or {}).get("feedback", 0.35) or 0)
            if 80.0 <= t <= 120.0 and fb <= 0.1:
                continue                    # slapback: time-domain idiom
            best_name, best_ms = min(
                ((n, q * m) for n, m in _DIVISIONS),
                key=lambda x: abs(x[1] - t))
            if t < 20.0:
                # THE SECONDS BUG (w39, engine-proven): a sub-20 value
                # is IMPOSSIBLE ms (zone min 20) — the generator wrote
                # tempo-locked SECONDS and the engine clamps to a 20ms
                # comb; 106/135 corpus takes carried it silently
                flags.append({
                    "kind": "seconds_in_ms_zone",
                    "track": scope.get("name", "?"), "time_ms": t,
                    "nearest": best_name,
                    "nearest_ms": round(best_ms, 1),
                    "why": f"{scope.get('name', '?')}: fx_delay time "
                           f"{t} is below the zone's 20ms floor — "
                           "SECONDS written into the ms zone (the "
                           "engine clamps it to a comb; the echo never "
                           "sounded); x1000 restores the intent"})
            elif abs(best_ms - t) / best_ms > 0.05:
                advisories.append({
                    "kind": "offgrid_delay",
                    "track": scope.get("name", "?"), "time_ms": t,
                    "nearest": best_name,
                    "nearest_ms": round(best_ms, 1),
                    "why": f"{scope.get('name', '?')}: fx_delay {t:.0f}ms "
                           f"sits off every division of {bpm:.0f}bpm "
                           f"(nearest {best_name} = {best_ms:.0f}ms) — "
                           "eval winners carry off-grid echoes at low "
                           "mix, so this ADVISES; snap if the groove "
                           "fights"})
    return {"court": "delay_grid", "ok": not flags, "flags": flags,
            "advisories": advisories}


def heal_delay_grid(song, verdict=None):
    """Snap each off-grid fx_delay to its nearest division. Mutates."""
    v = verdict or court_delay_grid(song)
    if v.get("ok", True):
        return []
    by = {}
    for f in v.get("flags", []):
        by.setdefault(f["track"], f)
    edits = []
    for scope in (song.get("tracks", []) or []) + \
            (song.get("buses", []) or []):
        if not isinstance(scope, dict):
            continue
        f = by.get(scope.get("name", "?"))
        if not f:
            continue
        for fx in scope.get("fx") or []:
            if str(fx.get("id", "")) == "fx_delay" and \
                    abs(float((fx.get("params") or {}).get("time", 0))
                        - f["time_ms"]) < 0.5:
                # THE UNIT HEAL: seconds x1000 (the value was already
                # tempo-locked — restoring the unit restores the grid);
                # still-off values snap to the nearest division
                t_ms = f["time_ms"] * 1000.0 if f["time_ms"] < 20.0 \
                    else f["time_ms"]
                best = min(((n, m) for n, m in
                            zip([x[0] for x in _DIVISIONS],
                                [x[1] for x in _DIVISIONS])),
                           key=lambda x: abs(x[1] * 60000.0 /
                                             float(song.get("bpm", 120)
                                                   or 120) - t_ms))
                bq = 60000.0 / float(song.get("bpm", 120) or 120)
                to_ms = round(best[1] * bq, 1) \
                    if abs(best[1] * bq - t_ms) / (best[1] * bq) > 0.05 \
                    else round(t_ms, 1)
                fx.setdefault("params", {})["time"] = to_ms
                edits.append({"track": f["track"], "kind": "delay_unit_heal"
                              if f["time_ms"] < 20 else "delay_snap",
                              "from": f["time_ms"], "to_ms": to_ms})
    return edits


# ======================================================= R-18 FOLEY COURT
def court_foley(song):
    """Foley/texture lanes are GLUE: they sit under the kit (gain well below
    0, healable) — that's the conviction. A missing high-pass is only an
    ADVISORY (the sample itself may carry no sub energy at all; convicting
    on chain shape alone would wolf every clean crackle loop)."""
    flags, advisories = [], []
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if not any(w in nm for w in ("foley", "texture", "vinyl", "crackle",
                                     "room_tone", "tape_hiss")):
            continue
        gain = float(t.get("gainDb", 0) or 0)
        if gain > -6.0:
            flags.append({"kind": "foley_loud", "track": t.get("name", "?"),
                          "gainDb": gain,
                          "why": f"{t.get('name', '?')} at {gain:+.1f}dB — "
                                 "texture sits UNDER the drums (<= -6dB); "
                                 "it fills gaps, it never competes"})
        fids = _fx_ids(t)
        has_hp = any(("hipass" in f or "filter" in f) for f in fids)
        if not has_hp:
            advisories.append({
                "kind": "foley_in_sub", "track": t.get("name", "?"),
                "why": f"{t.get('name', '?')} has no high-pass — if the "
                       "sample carries rumble it muddies the kick's floor "
                       "(HP ~200-300Hz)"})
    return {"court": "foley", "ok": not flags, "flags": flags,
            "advisories": advisories}


def heal_foley(song, verdict=None):
    """Duck loud texture lanes to -8dB (under the kit). Mutates."""
    v = verdict or court_foley(song)
    if v.get("ok", True):
        return []
    edits = []
    by_name = {t.get("name", "?"): t for t in song.get("tracks", []) or []
               if isinstance(t, dict)}
    for f in v.get("flags", []):
        if f.get("kind") != "foley_loud":
            continue
        t = by_name.get(f.get("track"))
        if not t:
            continue
        edits.append({"track": f["track"], "kind": "duck_texture",
                      "old_gainDb": t.get("gainDb"), "new_gainDb": -8.0})
        t["gainDb"] = -8.0
    return edits


# ================================================================ aggregate
def court_lowend(song, genre="", heal=False):
    out = {"interlock": court_interlock(song, genre),
           "kbbb": court_kbbb(song, genre),
           "freq_division": court_freq_division(song, genre),
           "delay_grid": court_delay_grid(song, genre),
           "sidechain": court_sidechain(song, genre),
           "env808": court_808_env(song, genre),
           "sub_width": court_sub_width(song),
           "foley": court_foley(song)}
    if heal:
        heals = {}
        if not out["interlock"].get("ok", True):
            heals["interlock"] = heal_interlock(song, genre, out["interlock"])
            out["interlock_after"] = court_interlock(song, genre)
        if not out["kbbb"].get("ok", True):
            heals["kbbb"] = heal_kbbb(song, genre, out["kbbb"])
            out["kbbb_after"] = court_kbbb(song, genre)
        if not out["freq_division"].get("ok", True):
            heals["freq_division"] = heal_freq_division(
                song, genre, out["freq_division"])
            out["freq_division_after"] = court_freq_division(song, genre)
        if not out["delay_grid"].get("ok", True):
            heals["delay_grid"] = heal_delay_grid(song, out["delay_grid"])
            out["delay_grid_after"] = court_delay_grid(song, genre)
        if not out["env808"].get("ok", True):
            heals["env808"] = heal_env808(song, genre, out["env808"])
            out["env808_after"] = court_808_env(song, genre)
        if not out["sub_width"].get("ok", True):
            heals["sub_width"] = heal_sub_width(song, out["sub_width"])
            out["sub_width_after"] = court_sub_width(song)
        if not out["foley"].get("ok", True):
            heals["foley"] = heal_foley(song, out["foley"])
            out["foley_after"] = court_foley(song)
        out["heals"] = heals
    out["ok"] = all(v.get("ok", True) for k, v in out.items()
                    if isinstance(v, dict) and not k.endswith("_after"))
    return out


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description="THE LOW-END COURT (wave 15)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song))
    v = court_lowend(song, args.genre, heal=args.heal)
    if args.heal and v.get("heals"):
        with open(args.song, "w") as f:
            json.dump(song, f, indent=1)
        v["saved"] = args.song
    print(json.dumps(v, indent=1))
    return 0 if v["ok"] or args.heal else 1


if __name__ == "__main__":
    sys.exit(main())
