#!/usr/bin/env python3
"""THE WORLD-CLASS FLOOR (2026-07-11, Chezy: "WE NEEDA MAKE SURE EVERY SONG
FROM EVERY MODEL, FOR EVERY REQUEST IS WORLD CLASS! EVERY ONE! AND FASTTTT!")

A pure, model-blind, zero-token quality gate that judges every proposal at
the clip wall's chokepoint — so every lane (prompt/MAKE/verb/parse/hum/
audio_to_midi) and every model inherits it automatically, in milliseconds.

HARD failures = a take no professional would ship, each an objective trap
class from standing law (docs/SPEC.md, doctor X-checks, mix-headroom):

  silent_take        notes/clips sound but the render is near-silence
  still_clipping     clipped samples AFTER the wall's re-render
  dark_master        X3: parked dark master filter, no automation (sweeps
                     exempt) — the 'barely audible' class          [heals]
  post_wall_gain     masterGainDb > 0 re-opens the wall's headroom [heals]
  trim_noop          X2: fx_trim {"gain"} is a silent no-op        [heals]
  legacy_limiter     deprecated type:"limiter"/bare brickwall      [heals]
  sub_stereo         M1: panned or widened kick/bass — mono death  [heals]

heal() fixes every [heals] class deterministically (zero tokens); the caller
re-renders ONCE. What can't be healed rides the verdict so the deck, the
telemetry, and the next prompt can say WHY. SOFT flags are taste, not law.

Kernel only — no engine, no network, no KG. The sidecar wires it.
"""
import copy

# Misnamed fx params the corpus actually writes (2026-07-12 sweep: 29x
# fx_filter 'mode', 6x 'resonance', 'threshold', 'wet') — deterministic
# renames ONLY, and only when the fx's real zone set contains the target
# (zone truth = doctor.FX_ZONES, imported lazily, fail-open).
PARAM_ALIASES = {"resonance": "res", "threshold": "thresh",
                 "outputDb": "makeup", "output_db": "makeup", "wet": "mix"}
_HP_WORDS = {"hp", "high", "highpass", "hi", "1", "1.0", "true"}



def ceiling_for(lufs):
    """W48 (item 121, Spotify's own rule): louder masters overshoot
    MORE on lossy encode (measured up to +1.73dB typical) — the wall's
    ceiling is loudness-aware, never a flat number: -1.0 dBTP when the
    integrated sits at/below -14 LUFS, -2.0 when hotter. Unknown
    loudness keeps the historic -1.2 (the safe middle)."""
    if lufs is None:
        return -1.2
    try:
        return -1.0 if float(lufs) <= -14.0 else -2.0
    except Exception:
        return -1.2


def _fx_zones(fid):
    try:
        import os as _os, sys as _sys
        _tp = _os.path.dirname(_os.path.abspath(__file__))
        if _tp not in _sys.path:
            _sys.path.insert(0, _tp)
        import doctor as _doc
        return _doc.FX_ZONES.get(fid)
    except Exception:
        return None


def _alias_walk(hard, where, ti, fi, f):
    """Misnamed-param convictions (X2 family) with deterministic heals:
    rename what has exactly one real home; fx_filter 'mode' either swaps to
    the hipass twin (hp intent) or drops the dead key (lp = already true)."""
    fid = f.get("id")
    params = f.get("params") or {}
    zones = _fx_zones(fid)
    if zones:
        for bad, good in PARAM_ALIASES.items():
            if bad in params and good in zones and good not in params \
                    and not (fid == "fx_trim" and bad == "gain"):
                hard.append({"code": "param_alias",
                             "heal": ("fx_param_rename", where, ti, fi, bad, good),
                             "why": f"{fid} param '{bad}' is not a zone — "
                                    f"the real knob is '{good}' (X2)"})
    if fid == "fx_filter" and "mode" in params:
        if str(params.get("mode")).strip().lower() in _HP_WORDS:
            hard.append({"code": "param_alias",
                         "heal": ("fx_to_hipass", where, ti, fi),
                         "why": "fx_filter has NO 'mode' zone — the hp "
                                "intent belongs to fx_hipass (X2)"})
        else:
            hard.append({"code": "param_alias",
                         "heal": ("fx_drop_param", where, ti, fi, "mode"),
                         "why": "fx_filter has NO 'mode' zone — dead key (X2)"})


def _is_sub(track):
    nm = str(track.get("name", "")).lower()
    if any(k in nm for k in ("kick", "bass", "sub", "808")) and "808s" not in nm:
        return True
    # FREQUENCY TRUTH (M4 upstreamed, 2026-07-12): an 808 named 'melody' is
    # still a sub — median NOTE pitch <= E2 (MIDI 40) convicts whatever the
    # name says. Drum lanes exempt (GM numbers are not pitches); when
    # drum-ness can't be verified, stay name-only (fail-open).
    ns = [n.get("pitch", 60) for n in track.get("notes", []) or []]
    if len(ns) >= 4:
        try:
            import os as _os, sys as _sys
            _tp = _os.path.dirname(_os.path.abspath(__file__))
            if _tp not in _sys.path:
                _sys.path.insert(0, _tp)
            from chordvote import is_drum_track as _idt
            if _idt(track):
                return False
        except Exception:
            return False
        return sorted(ns)[len(ns) // 2] <= 40
    return False


def _has_sound(song):
    return any((t.get("notes") or t.get("audioClips"))
               for t in song.get("tracks", []) if not t.get("muted"))


def _automated_slots(song):
    slots = set()
    for a in song.get("automation", []) or []:
        slots.add(str(a.get("target", "")))
    return slots


def floor_verdict(song, analysis=None):
    """Judge one take. `analysis` = analyze2 dict (or None/True when the
    metrics never landed — structural checks still run). Returns
    {"pass": bool, "hard": [{code, why}], "soft": [{code, why}]}."""
    hard, soft = [], []
    a = analysis if isinstance(analysis, dict) else {}

    if _has_sound(song) and a:
        lufs = a.get("lufs_integrated")
        peak = a.get("peak_dbfs")
        try:
            if (lufs is not None and float(lufs) < -32.0) and \
               (peak is not None and float(peak) < -20.0):
                hard.append({"code": "silent_take",
                             "why": f"take renders near-silent (LUFS "
                                    f"{float(lufs):.1f}, peak {float(peak):.1f} "
                                    "dBFS) — sound exists on the lanes but not "
                                    "in the render"})
        except (TypeError, ValueError):
            pass
        # W64 (r-14 item 206): the LRA/DYNAMICS window — soft tier
        # (the heal is at the SOURCE per item 145, never a fx move)
        lra = a.get("lra")
        try:
            if lra is not None and float(lra) < 3.0:
                soft.append({"code": "lra_static",
                             "why": (f"LRA {float(lra):.1f} LU — under 3 no "
                                     "arc survived the master (dense pop/EDM "
                                     "live at 3.5-8, rock 8-12, folk 10-15); "
                                     "restore section contrast at the SOURCE "
                                     "(density/level per section), never by "
                                     "un-limiting the wall")})
        except (TypeError, ValueError):
            pass
        if int(a.get("clipped_samples") or 0) > 0:
            hard.append({"code": "still_clipping",
                         "why": f"{a['clipped_samples']} clipped samples AFTER "
                                "the release wall — staging is overdriving the "
                                "chain at the source"})
        try:
            if lufs is not None and -4.0 < float(lufs):
                hard.append({"code": "crushed",
                             "why": f"LUFS {float(lufs):.1f} — louder than any "
                                    "professional release; dynamics are gone"})
            elif lufs is not None and float(lufs) < -22.0 and _has_sound(song):
                soft.append({"code": "quiet",
                             "why": f"LUFS {float(lufs):.1f} is quiet for a "
                                    "take — staging headroom unused"})
        except (TypeError, ValueError):
            pass

    autos = _automated_slots(song)
    master = song.get("master", []) or []
    for i, f in enumerate(master):
        fid, params = f.get("id"), f.get("params", {}) or {}
        slot = f"fx[{i}]"
        automated = any(slot in s for s in autos) or any(
            str(k) in s for s in autos for k in params)
        if automated:
            continue                               # sweeps are performance
        _alias_walk(hard, "master", -1, i, f)
        try:
            # hp-INTENT filters exempt from X3: they aren't dark, they're
            # mis-homed — the alias walk swaps them to fx_hipass instead
            if fid == "fx_filter" and float(params.get("cutoff", 20000)) < 800 \
                    and str(params.get("mode", "")).strip().lower() not in _HP_WORDS:
                hard.append({"code": "dark_master", "heal": ("drop_master_fx", i),
                             "why": f"parked master fx_filter at "
                                    f"{params.get('cutoff')}Hz with no automation "
                                    "— the 'barely audible' trap (X3)"})
            if fid == "fx_djfilter" and float(params.get("knob", 0)) < -0.35:
                hard.append({"code": "dark_master", "heal": ("drop_master_fx", i),
                             "why": f"parked master djfilter knob "
                                    f"{params.get('knob')} with no automation — "
                                    "the 'barely audible' trap (X3)"})
        except (TypeError, ValueError):
            pass
        if fid == "fx_brickwall" or f.get("type") == "limiter":
            hard.append({"code": "legacy_limiter", "heal": ("upgrade_wall", i),
                         "why": "deprecated sample-limiter on master — "
                                "ISP-blind; the release wall is fx_truepeak"})

    try:
        mg = float(song.get("masterGainDb", 0) or 0)
        # brickwall counts: it's still a wall, and the legacy heal upgrades it
        # to fx_truepeak IN THIS SAME PASS — checking truepeak-only left the
        # healed song standing with the positive gain unflagged
        if mg > 0.0 and any(f.get("id") in ("fx_truepeak", "fx_brickwall")
                            for f in master):
            hard.append({"code": "post_wall_gain", "heal": ("zero_master_gain",),
                         "why": f"masterGainDb +{mg:g} AFTER the wall re-opens "
                                "the headroom the wall just closed"})
    except (TypeError, ValueError):
        pass

    def _fx_lists(t):
        yield "track", t.get("fx", []) or []

    for ti, t in enumerate(song.get("tracks", [])):
        for _kind, fxl in _fx_lists(t):
            for fi, f in enumerate(fxl):
                if f.get("id") == "fx_trim" and "gain" in (f.get("params") or {}) \
                        and "level" not in (f.get("params") or {}):
                    hard.append({"code": "trim_noop",
                                 "heal": ("trim_rename", ti, fi),
                                 "why": f"'{t.get('name')}' fx_trim uses "
                                        "\"gain\" — a silent no-op; the zone "
                                        "is \"level\" (X2)"})
        for fi, f in enumerate(t.get("fx", []) or []):
            _alias_walk(hard, "track", ti, fi, f)
        if _is_sub(t) and (t.get("notes") or t.get("audioClips")):
            try:
                if abs(float(t.get("pan", 0) or 0)) > 1e-6:
                    hard.append({"code": "sub_stereo",
                                 "heal": ("center_sub", ti),
                                 "why": f"'{t.get('name')}' (sub) panned "
                                        f"{t.get('pan')} — cancels in mono (M1)"})
            except (TypeError, ValueError):
                pass
            if any(f.get("id") == "fx_widen" for f in t.get("fx", []) or []):
                hard.append({"code": "sub_stereo", "heal": ("narrow_sub", ti),
                             "why": f"'{t.get('name')}' (sub) is WIDENED — "
                                    "mono cancellation (M1)"})

    return {"pass": not hard, "hard": hard, "soft": soft,
            "analysis": a}     # w48: the heal's loudness-aware ceiling reads it


def _session_genre():
    """The GENRE COURT's stamp — start_session writes the resolved
    genre to ipc/genre_resolved.json; the floor reads it as fallback
    (fail-open)."""
    try:
        import json as _j
        import os as _o
        root = _o.path.dirname(_o.path.dirname(_o.path.abspath(__file__)))
        p = _o.path.join(root, "agent", "ipc", "genre_resolved.json")
        return str(_j.load(open(p)).get("genre") or "")
    except Exception:
        return ""


def pre_wall_clipper(doc, genre, receipts):
    """W65 (r-8 item 194): loud genres soft-clip 1-2dB of transient
    peaks BEFORE the limiter so the wall works less and pumps less.
    Insert fx_softclip ahead of the LAST fx_truepeak when the genre's
    PSR floor <= 6 (EDM/trap/pop/metal class) and no clip stage rides
    yet. Drive 1.5dB — under the crest brake by construction."""
    g = genre or _session_genre()
    if not g:
        return
    try:
        import dynamics_ears as _de
        pf = _de.psr_floor_for(g)
        floor = float(pf[0] if isinstance(pf, (tuple, list)) else pf)
    except Exception:
        return
    if floor > 6.0:
        return
    m = doc.get("master", []) or []
    wall_i = next((i for i in range(len(m) - 1, -1, -1)
                   if m[i].get("id") == "fx_truepeak"), None)
    if wall_i is None:
        return
    if any(f.get("id") in ("fx_softclip", "fx_crush") for f in m):
        return
    m.insert(wall_i, {"id": "fx_softclip", "params": {"drive": 1.5}})
    receipts.append(f"pre-wall clipper landed (softclip 1.5dB — {g}'s "
                    f"PSR floor {floor:.0f} = loud-genre class; the "
                    "wall pumps less)")


def heal(song, verdict, genre=""):
    """Apply every deterministic heal in the verdict. Returns
    (healed_song, receipts) — receipts empty when nothing was healable.
    Pure: the input song is not mutated."""
    doc = copy.deepcopy(song)
    receipts = []
    drop_master = []
    for h in verdict.get("hard", []):
        fix = h.get("heal")
        if not fix:
            continue
        op = fix[0]
        if op == "drop_master_fx":
            drop_master.append(fix[1])
            receipts.append(f"removed parked dark master fx[{fix[1]}]")
        elif op == "upgrade_wall":
            f = doc.get("master", [])[fix[1]]
            f.clear()
            f.update({"id": "fx_truepeak", "params": {
                "ceiling": ceiling_for((verdict.get("analysis") or {})
                                       .get("lufs_integrated"))}})
            receipts.append("legacy limiter upgraded to fx_truepeak "
                            "(loudness-aware ceiling)")
        elif op == "zero_master_gain":
            doc["masterGainDb"] = 0.0
            receipts.append("post-wall masterGainDb -> 0")
        elif op == "trim_rename":
            f = doc["tracks"][fix[1]]["fx"][fix[2]]
            f.setdefault("params", {})["level"] = f["params"].pop("gain")
            receipts.append(f"fx_trim \"gain\" -> \"level\" on "
                            f"'{doc['tracks'][fix[1]].get('name')}'")
        elif op == "fx_param_rename":
            _, where, ti, fi, bad, good = fix
            fxl = (doc.get("master", []) if where == "master"
                   else doc["tracks"][ti].get("fx", []))
            p = fxl[fi].setdefault("params", {})
            if bad in p and good not in p:
                p[good] = p.pop(bad)
                receipts.append(f"{fxl[fi].get('id')} '{bad}' -> '{good}'")
        elif op == "fx_to_hipass":
            _, where, ti, fi = fix
            fxl = (doc.get("master", []) if where == "master"
                   else doc["tracks"][ti].get("fx", []))
            f = fxl[fi]
            f.setdefault("params", {}).pop("mode", None)
            f["id"] = "fx_hipass"
            receipts.append("fx_filter mode:hp -> fx_hipass (the intent's real home)")
        elif op == "fx_drop_param":
            _, where, ti, fi, key = fix
            fxl = (doc.get("master", []) if where == "master"
                   else doc["tracks"][ti].get("fx", []))
            (fxl[fi].get("params") or {}).pop(key, None)
            receipts.append(f"{fxl[fi].get('id')} dead param '{key}' dropped")
        elif op == "center_sub":
            doc["tracks"][fix[1]]["pan"] = 0.0
            receipts.append(f"'{doc['tracks'][fix[1]].get('name')}' sub "
                            "re-centered")
        elif op == "narrow_sub":
            t = doc["tracks"][fix[1]]
            t["fx"] = [f for f in t.get("fx", []) if f.get("id") != "fx_widen"]
            receipts.append(f"widener stripped from sub "
                            f"'{t.get('name')}'")
    if drop_master:
        doc["master"] = [f for i, f in enumerate(doc.get("master", []))
                         if i not in set(drop_master)]
        # a take healed of its dark filter still needs the wall to stand last
        if not any(f.get("id") == "fx_truepeak" for f in doc["master"]):
            doc["master"].append({"id": "fx_truepeak", "params": {
                "ceiling": ceiling_for((verdict.get("analysis") or {})
                                       .get("lufs_integrated"))}})
            receipts.append("release wall appended (chain lost its last "
                            "stage; loudness-aware ceiling)")
    if receipts:
        pre_wall_clipper(doc, genre, receipts)
    # WALL LAST, WALL ONCE: upgrade_wall converts the legacy limiter IN PLACE —
    # if it wasn't the chain's last stage, post-wall fx (a saturator, a trim up)
    # re-clip what the wall just caught; and an upgraded legacy next to an
    # existing truepeak leaves TWO walls in series. Normalize: exactly one
    # fx_truepeak, seated at the end. Only fires when a heal touched the wall.
    if receipts:
        m = doc.get("master", []) or []
        walls = [f for f in m if f.get("id") == "fx_truepeak"]
        if walls and (len(walls) > 1 or m[-1].get("id") != "fx_truepeak"):
            rest = [f for f in m if f.get("id") != "fx_truepeak"]
            keep = walls[-1]
            try:  # the tightest declared ceiling survives a merge
                keep_ceil = min(float((w.get("params") or {}).get("ceiling", -1.2))
                                for w in walls)
                keep.setdefault("params", {})["ceiling"] = keep_ceil
            except (TypeError, ValueError):
                pass
            doc["master"] = rest + [keep]
            receipts.append("release wall re-seated LAST (single wall)")
    return doc, receipts


def summary(verdict, healed=()):
    """One human line for the activity stream / deck tooltip."""
    if verdict["pass"] and not healed:
        return "world-class floor: PASS"
    bits = []
    if healed:
        bits.append("healed: " + "; ".join(healed))
    left = [h["why"] for h in verdict["hard"] if not h.get("heal")]
    if left:
        bits.append("standing: " + "; ".join(left))
    return "world-class floor: " + (" | ".join(bits) or "PASS")
