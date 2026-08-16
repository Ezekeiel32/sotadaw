#!/usr/bin/env python3
"""THE MUSIC COURTS (PRODUCER MIND P2/P4/P8, docs/SPEC_PRODUCER_MIND.md).

A law without a court is a wish; a court without a heal is a nag.
Zero-token, deterministic verdicts + heals on a song dict:

  court_key(song, genre)          P2 — every melodic pitch vs the declared key
  heal_key(song, genre)               voice-leading-aware snap (theory.snap_pitch)
  court_pocket(song, genre)       P4 — grid stragglers + "meant together, landed
                                       apart" cross-track shadow pairs (the
                                       keys-vs-violin class, untitled_46)
  heal_pocket(song, genre, v)         micro-shift to intent (engine-swing aware:
                                       mirrors SongLoader.h applySwing exactly)
  court_instruction(ask, song, a) P8 — the ask is a contract: duration/bars/bpm/
                                       key/elements/vocals parsed + verified
  run_courts(path, genre, ...)        aggregate; CLI below

Conservative by construction: a court that cries wolf is worse than no court.
Verdicts cap their offender lists; heals return edit ledgers for honest lines.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theory as T  # noqa: E402
import meter as METER  # noqa: E402  (THE WORLD GRID: the one bar<->beat resolver)
from gold_bank import track_role  # noqa: E402  (THE house role classifier)

MAX_LIST = 50


# ------------------------------------------------------------------ helpers
def _bar1_of(mtr, q):
    """1-based bar containing quarter-beat q (chords[] spine convention)."""
    return int(METER.bar_at_q(mtr, float(q))) + 1


def song_key(song, melodic_notes=None):
    """Declared key first (always outranks); Krumhansl inference fallback."""
    k = T.parse_key(song.get("key"))
    if k:
        return k, "declared"
    k = T.infer_key(melodic_notes or [])
    return k, ("inferred" if k else "none")


# THE WITNESS LAW: imported transcription lanes (stems-import sketches /
# identity lanes) are witnesses of real audio, not compositions — the court
# never judges them. FX lanes (risers/sweeps) carry gestures, not melody.
_WITNESS_SUFFIX = ("_sketch", "_identity", "_ref", "_witness")
_WITNESS_PREFIX = ("spectral_",)   # SPECTRAL CAPTURE reconstruction lanes
# provenance words that make a lane a WITNESS: it carries someone else's
# notes (an import, a user's pasted tab, an engraved score) — the courts
# may report on it, never rewrite it.
_WITNESS_PROV = ("import", "transcri", "chart", "tab", "score", "verbatim")
_FX_WORDS = ("riser", "sweep", "fx", "impact", "downlifter", "uplifter",
             "noise", "foley", "swoosh", "whoosh", "texture", "drone_fx")


def court_role(t):
    """drums | witness | fx | melodic — what the KEY/POCKET courts may judge."""
    nm = str(t.get("name", "")).lower().strip()
    prov = str(t.get("provenance", "")).lower()
    if (nm.endswith(_WITNESS_SUFFIX) or nm.startswith(_WITNESS_PREFIX)
            or any(w in prov for w in _WITNESS_PROV)):
        return "witness"
    base = nm.replace("-", "_")
    if any(w == base or w in base.split("_") or w in nm for w in _FX_WORDS):
        return "fx"
    return track_role(t)


def melodic_tracks(song):
    return [t for t in song.get("tracks", []) or []
            if isinstance(t, dict) and court_role(t) == "melodic"
            and (t.get("notes") or [])]


def _bar_beat(start, mtr):
    b0 = int(METER.bar_at_q(mtr, float(start)))
    return b0 + 1, round(float(start) - METER.bar_start_q(mtr, b0), 3)


def swing_pos(start, song):
    """Mirror of SongLoader.h applySwing (0.5=straight; odd on-grid subs late)."""
    sw = song.get("swing") or {}
    amt = float(sw.get("amount", 0.5) or 0.5)
    if amt <= 0.5:
        return start
    sub = 0.5 if sw.get("grid") == "8th" else 0.25
    idx = round(start / sub)
    if abs(start - idx * sub) > 1e-6:
        return start
    if idx % 2 == 0:
        return start
    return start + (amt - 0.5) * 2.0 * sub


# ================================================================ P2 KEY COURT
def court_key(song, genre=""):
    """Verdict on melodic key conformance. ok = sour ratio <= 2% AND <= 6 notes."""
    mel = melodic_tracks(song)
    all_notes = [n for t in mel for n in t["notes"]]
    key, key_src = song_key(song, all_notes)
    if key is None:
        return {"court": "key", "ok": True, "skipped": "no key, no notes"}
    prof = T.allowance_for(genre)
    generous = prof.get("passing") == "generous"
    legal = T.allowed_pcs(key, genre)
    soft = T.soft_pcs(key, genre)
    mtr = METER.song_meter(song)
    chords = song.get("chords") or []
    total = sour = 0
    offenders = []
    per_track = {}
    for t in mel:
        notes = sorted(t["notes"], key=lambda n: float(n.get("start", 0)))
        t_total = t_sour = 0
        for i, n in enumerate(notes):
            try:
                p = int(n.get("pitch", 60))
            except Exception:
                continue
            t_total += 1
            if p % 12 in legal:
                continue
            prev_n = notes[i - 1] if i else None
            next_n = notes[i + 1] if i + 1 < len(notes) else None
            _s = float(n.get("start", 0))
            if T.is_passing_forgivable(
                    n, prev_n, next_n,
                    METER.beats_in_bar(mtr, METER.bar_at_q(mtr, _s)), generous):
                continue
            if p % 12 in soft:
                # SUPERMODE gate (R-1): mixture degrees convict only when
                # long + strong-beat + against the SOUNDING chord.
                _dur = float(n.get("len", n.get("length", 0.25)))
                _bar0 = METER.bar_at_q(mtr, _s)
                _beat = _s - METER.bar_start_q(mtr, int(_bar0))
                _strong = abs(_beat - round(_beat)) < 1e-6 and \
                    int(round(_beat)) % 2 == 0
                _ch = T.chord_at(chords, int(_bar0) + 1)
                if not (_dur >= 1.0 and _strong and _ch
                        and p % 12 not in _ch["pcs"]):
                    continue
            t_sour += 1
            if len(offenders) < MAX_LIST:
                bar, beat = _bar_beat(_s, mtr)
                ch = T.chord_at(chords, bar)
                sug = T.snap_pitch(p, key, genre, chord=ch,
                                   prev_pitch=int(prev_n["pitch"]) if prev_n else None,
                                   next_pitch=int(next_n["pitch"]) if next_n else None)
                offenders.append({"track": t.get("name", "?"), "bar": bar,
                                  "beat": beat, "pitch": p,
                                  "name": T.midi_to_name(p),
                                  "suggest": sug,
                                  "suggest_name": T.midi_to_name(sug)})
        # THE AVOID-NOTE LAW (R-1, jazz pedagogy): in the generous families a
        # SUSTAINED STRONG-BEAT note one semitone above a chord tone is the
        # one thing that still convicts (the 4 over a maj7 held on the one).
        if generous and chords:
            for n in notes:
                try:
                    p = int(n.get("pitch", 60))
                except Exception:
                    continue
                _dur = float(n.get("len", n.get("length", 0.25)))
                if _dur < 1.5:
                    continue
                _s = float(n.get("start", 0))
                _bar0 = METER.bar_at_q(mtr, _s)
                _beat = _s - METER.bar_start_q(mtr, int(_bar0))
                if not (abs(_beat - round(_beat)) < 1e-6
                        and int(round(_beat)) % 2 == 0):
                    continue
                _ch = T.chord_at(chords, int(_bar0) + 1)
                if _ch and p % 12 not in _ch["pcs"] \
                        and (p - 1) % 12 in _ch["pcs"]:
                    t_sour += 1
                    if len(offenders) < MAX_LIST:
                        offenders.append({
                            "track": t.get("name", "?"),
                            "bar": int(_bar0) + 1, "beat": round(_beat, 3),
                            "pitch": p, "name": T.midi_to_name(p),
                            "suggest": p - 1,
                            "suggest_name": T.midi_to_name(p - 1),
                            "law": "avoid-note"})
        total += t_total
        sour += t_sour
        if t_total:
            per_track[t.get("name", "?")] = round(1.0 - t_sour / t_total, 3)
    ratio = (sour / total) if total else 0.0
    # abs cap scales with song size: a 5-sour loop fails, 0.4% of an epic passes
    cap = max(6, total // 150)
    return {"court": "key", "ok": sour == 0 or (ratio <= 0.02 and sour <= cap),
            "key": key["name"], "key_src": key_src,
            "in_key_pct": round(1.0 - ratio, 4), "sour": sour, "total": total,
            "per_track": per_track, "offenders": offenders}


def heal_key(song, genre=""):
    """Snap every non-forgivable sour melodic note (voice-leading aware).
    Mutates song; returns the edit ledger."""
    v = court_key(song, genre)
    if v.get("skipped") or not v.get("offenders") is not None and v["ok"]:
        return []
    key = T.parse_key(song.get("key")) or T.infer_key(
        [n for t in melodic_tracks(song) for n in t["notes"]])
    if key is None:
        return []
    prof = T.allowance_for(genre)
    generous = prof.get("passing") == "generous"
    legal = T.allowed_pcs(key, genre)
    soft = T.soft_pcs(key, genre)
    mtr = METER.song_meter(song)
    chords = song.get("chords") or []
    edits = []
    for t in melodic_tracks(song):
        notes = sorted(t["notes"], key=lambda n: float(n.get("start", 0)))
        for i, n in enumerate(notes):
            try:
                p = int(n.get("pitch", 60))
            except Exception:
                continue
            if p % 12 in legal:
                continue
            prev_n = notes[i - 1] if i else None
            next_n = notes[i + 1] if i + 1 < len(notes) else None
            _s = float(n.get("start", 0))
            if T.is_passing_forgivable(
                    n, prev_n, next_n,
                    METER.beats_in_bar(mtr, METER.bar_at_q(mtr, _s)), generous):
                continue
            if p % 12 in soft:
                _dur = float(n.get("len", n.get("length", 0.25)))
                _bar0 = METER.bar_at_q(mtr, _s)
                _beat = _s - METER.bar_start_q(mtr, int(_bar0))
                _strong = abs(_beat - round(_beat)) < 1e-6 and \
                    int(round(_beat)) % 2 == 0
                _ch = T.chord_at(chords, int(_bar0) + 1)
                if not (_dur >= 1.0 and _strong and _ch
                        and p % 12 not in _ch["pcs"]):
                    continue
            bar, _ = _bar_beat(_s, mtr)
            ch = T.chord_at(chords, bar)
            _nm = str(t.get("name", "")).lower()
            _is_bass = any(w in _nm for w in ("808", "sub", "bass"))
            newp = T.snap_pitch(p, key, genre, chord=ch,
                                prev_pitch=int(prev_n["pitch"]) if prev_n else None,
                                next_pitch=int(next_n["pitch"]) if next_n else None,
                                bass=_is_bass)
            if newp != p:
                n["pitch"] = newp
                edits.append({"track": t.get("name", "?"), "bar": bar,
                              "old": T.midi_to_name(p), "new": T.midi_to_name(newp)})
    return edits


# ============================================================= P4 POCKET COURT
def _grid_of(notes):
    """Dominant grid step from onsets: 0.25 / 0.5 / 1.0 / third-beat. None when
    the track is too free to have one (performance intent — court exempts)."""
    if len(notes) < 4:
        return None
    best, best_hits = None, 0
    for sub in (0.25, 1.0 / 3.0, 0.5, 1.0):
        hits = sum(1 for n in notes
                   if abs(float(n.get("start", 0)) / sub
                          - round(float(n.get("start", 0)) / sub)) < 0.02)
        if hits > best_hits:
            best, best_hits = sub, hits
    if best is None or best_hits / len(notes) < 0.55:
        return None
    return best


def court_pocket(song, genre=""):
    """(a) grid stragglers: a mostly-on-grid melodic track's few slightly-off
    notes (sloppiness, not intent — swing-aware via the engine's own formula);
    (b) shadow pairs: two melodic tracks repeatedly landing NEAR-together
    (0 < gap <= 0.12 beats) = meant together, landed apart."""
    mel = melodic_tracks(song)
    stragglers, pairs = [], []
    grids = {}
    for t in mel:
        notes = sorted(t["notes"], key=lambda n: float(n.get("start", 0)))
        grid = _grid_of(notes)
        grids[t.get("name", "?")] = grid
        if grid is None:
            continue
        offs = []
        for n in notes:
            s = float(n.get("start", 0))
            snapped = round(s / grid) * grid
            d = abs(s - snapped)
            # floor 0.01 beats (~5ms): below it is float rounding, not feel —
            # a 1e-6 floor once "healed" 115.6667->115.6667 every render pass
            if 0.01 < d <= grid * 0.25:
                # engine swing puts odd subs late ON PURPOSE — expected position
                if abs(s - swing_pos(snapped, song)) < 1e-6:
                    continue
                offs.append((n, snapped, d))
        # the straggler signature: a FEW slightly-off notes on a gridded track
        if offs and len(offs) / max(len(notes), 1) <= 0.15:
            for n, snapped, d in offs[:MAX_LIST - len(stragglers)]:
                stragglers.append({"track": t.get("name", "?"),
                                   "start": float(n.get("start", 0)),
                                   "snap_to": round(snapped, 4),
                                   "off_by": round(d, 4)})
    mtr = METER.song_meter(song)
    for i in range(len(mel)):
        for j in range(i + 1, len(mel)):
            # the alignment TARGET (the denser 'leader' the heal snaps onto)
            # must itself be gridded: aligning a clean lane onto a humanized/
            # free leader spreads the jitter (831 fiddle notes dragged onto a
            # ±12ms-humanized banjo, untitled_65). A free FOLLOWER uniformly
            # shifted off a gridded leader stays convictable (copy-drift).
            lead_name = (mel[i] if len(mel[i]["notes"]) >= len(mel[j]["notes"])
                         else mel[j]).get("name", "?")
            if grids.get(lead_name) is None:
                continue
            a = sorted((float(n.get("start", 0)) for n in mel[i]["notes"]))
            b = sorted((float(n.get("start", 0)) for n in mel[j]["notes"]))
            if len(a) < 4 or len(b) < 4:
                continue
            near = exact = 0
            examples = []
            bi = 0
            for s in a:
                while bi < len(b) and b[bi] < s - 0.13:
                    bi += 1
                for bb in b[bi:bi + 3]:
                    d = abs(bb - s)
                    if d <= 0.01:      # together at audio resolution = exact
                        exact += 1
                        break
                    if d <= 0.12:
                        near += 1
                        if len(examples) < 4:
                            examples.append({"bar": _bar1_of(mtr, s),
                                             "a": round(s, 3), "b": round(bb, 3)})
                        break
            denom = min(len(a), len(b))
            # band-interplay exemption (eval_blues guitars, 2026-07-14): parts
            # that often land EXACTLY together and drift elsewhere are doing
            # push-pull on purpose; the copy-drift signature locks NEVER.
            if denom and near / denom > 0.3 and near >= 4 \
                    and exact < max(2, near // 3):
                pairs.append({"a": mel[i].get("name", "?"),
                              "b": mel[j].get("name", "?"),
                              "near": near, "exact": exact,
                              "near_ratio": round(near / denom, 3),
                              "examples": examples})
    return {"court": "pocket", "ok": not stragglers and not pairs,
            "stragglers": stragglers, "shadow_pairs": pairs, "grids": grids}


def heal_pocket(song, genre="", verdict=None):
    """Stragglers snap to their own grid (engine swing then re-applies the
    genre's intended lateness); shadow pairs: the sparser track's near-miss
    onsets align to the denser leader's. Mutates song; returns edit ledger."""
    v = verdict or court_pocket(song, genre)
    edits = []
    by_track = {t.get("name", "?"): t for t in melodic_tracks(song)}
    for s in v.get("stragglers", []):
        t = by_track.get(s["track"])
        if not t:
            continue
        for n in t["notes"]:
            if abs(float(n.get("start", 0)) - s["start"]) < 1e-9:
                n["start"] = s["snap_to"]
                edits.append({"track": s["track"], "kind": "grid",
                              "from": s["start"], "to": s["snap_to"]})
                break
    for p in v.get("shadow_pairs", []):
        ta, tb = by_track.get(p["a"]), by_track.get(p["b"])
        if not ta or not tb:
            continue
        # leader = denser track; follower aligns
        lead, follow = (ta, tb) if len(ta["notes"]) >= len(tb["notes"]) else (tb, ta)
        lead_starts = sorted(float(n.get("start", 0)) for n in lead["notes"])
        for n in follow["notes"]:
            s = float(n.get("start", 0))
            best = min(lead_starts, key=lambda x: abs(x - s), default=None)
            if best is not None and 0.01 < abs(best - s) <= 0.12:
                n["start"] = best
                edits.append({"track": follow.get("name", "?"), "kind": "align",
                              "from": round(s, 4), "to": round(best, 4),
                              "with": lead.get("name", "?")})
    return edits


# ======================================================== P8 INSTRUCTION COURT
_ELEMENT_WORDS = ("cowbell", "808", "piano", "violin", "guitar", "choir", "bell",
                  "pad", "arp", "pluck", "brass", "string", "sax", "flute",
                  "organ", "rhodes", "log drum", "logdrum", "supersaw", "reese",
                  "wobble", "stab", "vox", "kalimba", "sitar", "koto", "timpani")
# words whose plain \b form collides with ordinary talk about an instrument's
# anatomy ("the 2nd string", "a 5-string banjo") — the section is the PLURAL.
_ELEMENT_PAT = {"string": r"\bstrings\b|\bstring (?:section|ensemble|pad|line)\b"}
_ELEMENT_PRE = re.compile(
    r"(?:\d\s*-\s*|\b\d+\s*(?:st|nd|rd|th)\s+|\bthe\s+\d\S*\s+)$")
# THE WORD-BOUNDARY LAW (2026-08-02): this was a naive substring test, so
# "IMPROVISING a full song" contained "sing" and every instrumental take got
# CONTRACT UNMET - vocals, on every render pass, forever. Bare "words" is
# gone with it — "in other words" is not a vocal request.
_VOCAL_RE = re.compile(
    r"\b(?:vocals?|lyrics?|sings?|singing|sung|voices?|topline|"
    r"a\s?capella|acapella)\b")


def _song_duration_s(song, analysis=None):
    if analysis and analysis.get("duration_s"):
        return float(analysis["duration_s"])
    bpm = float(song.get("bpm", 120) or 120)
    bars = float(song.get("lengthBars", 8) or 8)
    mtr = METER.song_meter(song)
    return METER.bar_start_q(mtr, bars) * 60.0 / bpm


def _has_vocal_presence(song):
    lyr = song.get("lyrics")
    if isinstance(lyr, (list, dict)) and lyr:
        return True
    for t in song.get("tracks", []) or []:
        nm = str(t.get("name", "")).lower()
        srcid = str((t.get("source") or {}).get("id", "")).lower()
        if any(w in nm for w in ("vocal", "vox", "topline", "choir", "voice")):
            if t.get("notes") or t.get("audioClips") or "audio" in str(
                    (t.get("source") or {}).get("kind", "")):
                return True
        if "vocal" in srcid or "voice" in srcid:
            return True
        for c in t.get("audioClips") or []:
            if "vocal" in str(c.get("file", "")).lower():
                return True
    return False


_STRING_DATA_CTX = re.compile(r"\b(?:tabs?|tuning|tuned|frets?|digits|gauge)\b")


def _element_hit(w, text):
    """True when the ask really REQUESTS element w (not just mentions its name
    inside a pasted chart's anatomy: "5-string banjo", "the 2nd string")."""
    pat = _ELEMENT_PAT.get(w, rf"\b{re.escape(w)}s?\b")
    for m in re.finditer(pat, text):
        if _ELEMENT_PRE.search(text[max(0, m.start() - 14):m.start()]):
            continue
        if w == "string":
            # sentence-scoped anatomy veto: "exact strings", "the strings are
            # tuned...", "fret numbers ... strings" = tab talk about an
            # instrument's own strings, not a string-section request
            s0 = max(text.rfind(".", 0, m.start()),
                     text.rfind("\n", 0, m.start()),
                     text.rfind("(", 0, m.start())) + 1
            ends = [text.find(c, m.end()) for c in (".", "\n", ")")]
            s1 = min([x for x in ends if x != -1], default=len(text))
            if _STRING_DATA_CTX.search(text[s0:s1]):
                continue
        return True
    return False


def court_instruction(ask, song, analysis=None, genre=""):
    """Parse the ask into verifiable contracts; verdict each against the take.

    THE PASTED-ARTIFACT FENCE: only the user's INSTRUCTION text is parsed —
    a pasted tab/chart/log is DATA. Reading the paste as instruction is how
    a banjo tab once demanded "16 bars" (a bars-regex that spanned a newline
    between "...repeat of bars 15-16" and "bars 21-22") and an "element:
    string" that meant a 5-string banjo."""
    try:
        import ask_fence
        text = ask_fence.instruction_of(ask).lower()
    except Exception:
        text = str(ask or "").lower()
    contracts = []

    def add(kind, want, got, ok, note=""):
        contracts.append({"kind": kind, "want": want, "got": got,
                          "ok": bool(ok), **({"note": note} if note else {})})

    # duration: "10 minute(s)", "2:20", "2.20 long", "full length"
    dur_s = None
    m = re.search(r"(\d{1,2})\s*(?:minutes?|mins?)\b", text)
    if m:
        dur_s = int(m.group(1)) * 60
    m2 = re.search(r"\b(\d)[:.](\d{2})\b(?:\s*(?:long|length|minutes?))?", text)
    if m2 and not m:
        mm, ss = int(m2.group(1)), int(m2.group(2))
        if ss < 60 and (m2.group(0).endswith(("long", "length")) or ":" in m2.group(0)
                        or "long" in text[m2.end():m2.end() + 12]):
            dur_s = mm * 60 + ss
    if dur_s:
        got = _song_duration_s(song, analysis)
        add("duration", f"{dur_s}s", f"{round(got)}s",
            abs(got - dur_s) <= max(0.1 * dur_s, 15))
    elif re.search(r"full[- ]length|whole song|full song", text):
        got = _song_duration_s(song, analysis)
        add("duration", ">=150s (full length)", f"{round(got)}s", got >= 150)

    # [ \t]* NOT \s* — the old form spanned newlines, so a chart's
    # "...repeat of bars 15-16\n\n  bars 21-22" asked for "16 bars".
    # (?<![-\d/]) keeps the tail of a range ("15-16") from becoming a count.
    m = re.search(r"(?<![-\d/])(\d{1,3})[ \t]*bars\b", text)
    if m:
        want = int(m.group(1))
        got = int(song.get("lengthBars", 0) or 0)
        add("bars", want, got, got == want)

    m = re.search(r"(\d{2,3})\s*bpm\b|\bat\s+(\d{2,3})\b", text)
    if m:
        want = int(m.group(1) or m.group(2))
        if 40 <= want <= 220:
            got = float(song.get("bpm", 0) or 0)
            add("bpm", want, got, abs(got - want) <= 1.0)

    m = re.search(r"\bin\s+([a-g][#b]?)\s*(major|minor|m\b)?", text)
    if m and (m.group(2) or not re.search(r"\bin\s+[a-g][#b]?\s+(?:the|a|an)\b", text)):
        want_k = T.parse_key(f"{m.group(1)} {m.group(2) or 'major'}")
        got_k = T.parse_key(song.get("key"))
        if want_k:
            add("key", want_k["name"], (got_k or {}).get("name", "none"),
                bool(got_k and got_k["tonic_pc"] == want_k["tonic_pc"]
                     and got_k["mode"] == want_k["mode"]))

    if _VOCAL_RE.search(text):
        add("vocals", "sounding vocal presence", _has_vocal_presence(song),
            _has_vocal_presence(song))

    tracks_blob = " ".join(
        (str(t.get("name", "")) + " " + str((t.get("source") or {}).get("id", "")))
        for t in song.get("tracks", []) or []).lower()
    for w in _ELEMENT_WORDS:
        if _element_hit(w, text):
            present = w.replace(" ", "") in tracks_blob.replace(" ", "") or \
                w in tracks_blob
            add("element", w, present, present)

    # WAVE 19 THE SEMANTIC TIER (R-28): producer words become measured
    # contracts — (term x effect-context x scope) via semantic_map, with
    # the agreement gate (LOW-agreement words ride as ambiguities, a
    # one-tap ask-back instead of a wrong render). Verdicts only fire
    # when the analysis carries the correlate (post-render); pre-render
    # they ride as 'unmeasured' notes carrying the recipe.
    ambiguities = []
    try:
        import semantic_map
        sc = semantic_map.contract(text, genre, song)   # fenced text, not raw
        contracts.extend(semantic_map.verdict_semantics(
            sc["semantic_goals"], analysis, genre))
        ambiguities = sc.get("ambiguities") or []
    except Exception:
        pass

    unmet = [c for c in contracts if not c["ok"]]
    return {"court": "instruction", "ok": not unmet,
            "contracts": contracts, "unmet": unmet,
            **({"ambiguities": ambiguities} if ambiguities else {})}


# =================================================================== aggregate
def run_courts(song_or_path, genre="", ask=None, analysis=None, heal=False,
               verbatim=None):
    """The one call sidecar lanes make. Returns verdicts (+heal ledgers when
    heal=True — caller re-saves the song dict it passed).

    THE TRANSCRIPTION FENCE (2026-08-02, untitled_65): verbatim=True means the
    notes came from the USER (a pasted tab/chart, an imported score) — the
    courts still SIT (verdicts ride the take) but no heal may touch pitch or
    timing. Healing a transcription destroys the only thing that was asked
    for: that run re-pitched 92 of the user's own notes (A3->G#3 "in key")
    and nudged 831 timings off the chart, three passes running.
    verbatim=None infers it from the ask (ask_fence.has_chart)."""
    if isinstance(song_or_path, str):
        with open(song_or_path) as f:
            song = json.load(f)
    else:
        song = song_or_path
    if verbatim is None:
        try:
            import ask_fence
            verbatim = ask_fence.has_chart(ask or "")
        except Exception:
            verbatim = False
    if verbatim:
        heal = False              # verdicts yes, note surgery never
    out = {"key": court_key(song, genre), "pocket": court_pocket(song, genre),
           "verbatim": bool(verbatim)}
    if ask:
        out["instruction"] = court_instruction(ask, song, analysis, genre)
    try:                          # P6 arrangement narrative + (wave 27)
        import arc_court          # the hook-teaser heal for late hooks
        out["arc"] = arc_court.court_arc(song, genre, analysis)
        if heal and not out["arc"].get("ok", True):
            eds = arc_court.heal_late_hook(song, out["arc"], genre)
            if eds:
                out.setdefault("heals", {})["arc"] = eds
                out["arc_after"] = arc_court.court_arc(song, genre,
                                                       analysis)
    except Exception:
        pass
    try:                          # wave 49 (the holes decree): full-band
        import flow_court         # dead air convicts; the bridge heals it
        fv = flow_court.court_flow(song)
        if not fv.get("skipped"):
            out["flow"] = fv
            if heal and not fv.get("ok", True):
                eds = flow_court.heal_flow(song, fv)
                if eds:
                    out.setdefault("heals", {})["flow"] = eds
                    out["flow_after"] = flow_court.court_flow(song)
    except Exception:
        pass
    try:                          # R-2 melodic mind (wave 12): BANDS + wanderers
        import melody_court
        out["melody"] = melody_court.court_melody(song, genre)
    except Exception:
        pass
    try:                          # wave 13 harmony mind: chord-tone/LIL/ext/
        import harmony_court      # modal/progression/cadence (+ its own heals)
        out["harmony"] = harmony_court.court_harmony(song, genre, heal=heal)
    except Exception:
        pass
    try:                          # wave 14 groove engine: tempo/kick/backbeat/
        import groove_court       # swing/hats/masks/fills (+ its own heals)
        out["groove"] = groove_court.court_groove(song, genre, heal=heal)
    except Exception:
        pass
    try:                          # wave 15 low-end court: interlock/KBBB/808
        import lowend_court       # env/sub-width/foley (+ its own heals)
        out["lowend"] = lowend_court.court_lowend(song, genre, heal=heal)
    except Exception:
        pass
    try:                          # wave 17 lyric courts: singability/prosody/
        import lyric_court        # vowel/form (+ authorship-guarded heals)
        lv = lyric_court.court_lyrics(song, genre, heal=heal)
        if not lv.get("skipped"):
            out["lyrics"] = lv
    except Exception:
        pass
    try:                          # wave 18 tension arc: climax/shape/drop
        import tension            # (+ the pre-drop dip heal)
        out["tension"] = tension.court_tension(song, genre, heal=heal)
    except Exception:
        pass
    try:                          # wave 44: form conformance + signature
        import form_court         # voice (both advisory-only)
        fv = form_court.court_form_conformance(song, genre)
        sv = form_court.court_signature(song, genre)
        ov = form_court.court_outro(song, genre)
        rv = form_court.court_ritual(song, genre)
        if fv.get("advisories") or sv.get("advisories") or \
                ov.get("advisories") or rv.get("advisories"):
            out["form_sig"] = {"form": fv, "signature": sv, "outro": ov,
                               "ritual": rv, "ok": True}
    except Exception:
        pass
    try:                          # wave 68: breath court (sung lanes)
        import vocal_chain as _vch
        bv = _vch.court_breath(song, genre)
        if bv.get("advisories"):
            out["breath"] = bv
            if heal:
                eds = _vch.heal_breath(song, bv, genre)
                if eds:
                    out.setdefault("heals", {})["breath"] = eds
    except Exception:
        pass
    try:                          # wave 63: symbolic invariants
        import symbolic_invariants
        siv = symbolic_invariants.invariants(song, genre)
        if siv.get("advisories"):
            out["invariants"] = siv
    except Exception:
        pass
    try:                          # wave 62: attack-class contracts
        import voice_character
        acv = voice_character.court_attack_class(song)
        if acv.get("advisories"):
            out["attack_class"] = acv
    except Exception:
        pass
    try:                          # wave 58: metal mix-heal (genre-gated)
        import metal_heal
        mmv = metal_heal.court_metal_mix(song, genre)
        if mmv.get("advisories"):
            out["metal_mix"] = mmv
            if heal:
                eds = metal_heal.heal_metal_mix(song, mmv, genre)
                if eds:
                    out.setdefault("heals", {})["metal_mix"] = eds
                    out["metal_mix_after"] = metal_heal.court_metal_mix(
                        song, genre)
    except Exception:
        pass
    try:                          # wave 53: movement is mandatory
        import movement_court     # (static archetype lanes -> journey)
        mvv = movement_court.court_movement(song, genre)
        if mvv.get("advisories"):
            out["movement"] = mvv
            if heal:
                eds = movement_court.heal_movement(song, mvv)
                if eds:
                    out.setdefault("heals", {})["movement"] = eds
    except Exception:
        pass
    try:                          # wave 51: phrase-grid/repetition/
        import structure_court    # contrast/vocabulary (advisory tier)
        sv = structure_court.court_structure(song, genre)
        if sv.get("advisories"):
            out["structure"] = sv
    except Exception:
        pass
    try:                          # wave 21 compose-time masking prevention
        import masking_court      # (mud-zone crowding, advisory-only;
        mv = masking_court.court_compose_masking(song, genre)
        if mv.get("advisories"):  # the stems MSR court is on-demand)
            out["masking"] = mv
    except Exception:
        pass
    try:                          # A2-T2 (SPEC_TRANSCENDENCE): the user's own
        import artist_model       # standing laws judge the take — explicit
        cv = artist_model.court_constitution(song, genre)   # "never: X" only;
        if not cv.get("skipped"):                           # no heal (taste
            out["constitution"] = cv                        # advises, never
    except Exception:                                       # operates)
        pass
    if heal:
        heals = out.get("heals", {})   # arc's teaser heal may already sit here
        if not out["key"].get("ok", True):
            heals["key"] = heal_key(song, genre)
            out["key_after"] = court_key(song, genre)
        if not out["pocket"].get("ok", True):
            heals["pocket"] = heal_pocket(song, genre, out["pocket"])
            out["pocket_after"] = court_pocket(song, genre)
        if not out.get("melody", {}).get("ok", True):
            try:
                import melody_court
                heals["melody"] = melody_court.heal_melody(
                    song, genre, out["melody"])
                out["melody_after"] = melody_court.court_melody(song, genre)
            except Exception:
                pass
        out["heals"] = heals
    out["ok"] = all(v.get("ok", True) for k, v in out.items()
                    if isinstance(v, dict) and "ok" in v and not k.endswith("_after"))
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE MUSIC COURTS (P2/P4/P8)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--ask", default=None)
    ap.add_argument("--heal", action="store_true",
                    help="apply heals and SAVE the song in place")
    args = ap.parse_args()
    with open(args.song) as f:
        song = json.load(f)
    out = run_courts(song, args.genre, ask=args.ask, heal=args.heal)
    if args.heal and out.get("heals"):
        with open(args.song, "w") as f:
            json.dump(song, f, indent=1)
        out["saved"] = args.song
    print(json.dumps(out, indent=1))
    return 0 if out["ok"] or args.heal else 1


if __name__ == "__main__":
    sys.exit(main())
