#!/usr/bin/env python3
"""THE TRANSITION OPS — the arranger's boundary vocabulary (wave 26;
R-15 items 072/073/075).

Deterministic ops that build the three canonical section-boundary
gestures from song.json primitives (voices riser/rev_crash/crash_noise
+ the automation DSL gainDb|fx[i].<param>). Ops RETURN/mutate song
material — courts and agents compose them; heal_drop's gap (w18) is the
sibling gesture.

  riser(boundary_beat, bars, bpm, kind)  -> a lane dict: one note ending
        AT the boundary on the riser (tonal, self-sweeping) or rev_crash
        (noise swell) voice, with a late-bloom gainDb swell (curve>0 =
        the build shape the engine verifies).
  filter_sweep(track, f0, f1, start_beat, bars)  -> appends fx[i].cutoff
        automation on the track's fx_filter (inserted before the first
        wall-ish fx if absent) — the build reveal: dark -> open, landing
        exactly at the boundary.
  gap_impact(song, boundary_beat, gap_beats)  -> negative space: clears
        non-exempt lanes' notes inside the gap window before the
        boundary, then lands a crash_noise impact ON the downbeat
        ('impact' lane, idempotent). The r-15 silence-then-hit law.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_GAP_EXEMPT = ("riser", "uplifter", "sweep", "fx", "impact", "crash",
               "vocal", "vox")


def riser(boundary_beat, bars=2, bpm=120, kind="tonal", gain_db=-6.0):
    """One lane, one note, ends AT the boundary. kind='tonal' rides the
    riser voice (self-sweeping resonant rise); 'noise' rides rev_crash
    (reverse swell into the hit)."""
    length = float(bars) * 4.0
    start = float(boundary_beat) - length
    spb = 60.0 / max(float(bpm), 1.0)
    if kind == "noise":
        src = {"id": "rev_crash"}
    else:
        src = {"id": "riser",
               "params": {"sweep": round(min(max(length * spb, 0.5), 20.0),
                                         2),
                          "range": 24, "q": 1.6}}
    return {
        "name": f"riser_{kind}_{int(boundary_beat)}",
        "source": src, "gainDb": gain_db, "pan": 0.0,
        "notes": [{"start": round(start, 4), "len": round(length, 4),
                   "pitch": 45, "vel": 0.85}],
        "automation": [{"target": "gainDb",
                        "points": [
                            {"beat": round(start, 4), "v": gain_db - 12.0},
                            {"beat": round(boundary_beat, 4), "v": gain_db,
                             "curve": 0.6}]}]}


def filter_sweep(track, f0, f1, start_beat, bars=2):
    """Item 073: the build reveal — fx_filter cutoff automation f0 -> f1
    landing at start_beat + bars*4. Inserts fx_filter if the track has
    none (before any wall-ish fx). Mutates; returns the ledger."""
    fx = track.setdefault("fx", [])
    idx = None
    for i, f in enumerate(fx):
        if str(f.get("id", "")) == "fx_filter":
            idx = i
            break
    if idx is None:
        idx = 0
        for i, f in enumerate(fx):
            if str(f.get("id", f.get("type", "")) or "").startswith(
                    ("fx_truepeak", "fx_brickwall")):
                idx = i
                break
        fx.insert(idx, {"id": "fx_filter",
                        "params": {"cutoff": float(f0), "res": 1.2}})
    end_beat = float(start_beat) + float(bars) * 4.0
    auto = track.setdefault("automation", [])
    auto.append({"target": f"fx[{idx}].cutoff",
                 "points": [{"beat": round(float(start_beat), 4),
                             "v": float(f0)},
                            {"beat": round(end_beat, 4), "v": float(f1),
                             "curve": 0.5}]})
    return [{"kind": "filter_sweep", "fx_index": idx,
             "f0": float(f0), "f1": float(f1),
             "beats": [float(start_beat), end_beat]}]


def gap_impact(song, boundary_beat, gap_beats=0.5):
    """Item 075: negative space then the hit. Clears non-exempt lanes'
    onsets inside [boundary-gap, boundary), trims tails crossing in,
    lands crash_noise ON the downbeat (idempotent 'impact' lane).
    Mutates; returns the ledger."""
    b = float(boundary_beat)
    lo = b - float(gap_beats)
    cleared = trimmed = 0
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if any(w in nm for w in _GAP_EXEMPT):
            continue
        keep = []
        for n in t.get("notes", []) or []:
            s = float(n.get("start", 0))
            ln = float(n.get("len", 0.25))
            if lo <= s < b:
                cleared += 1
                continue
            if s < lo < s + ln:
                n["len"] = round(max(lo - s, 0.05), 4)
                trimmed += 1
            keep.append(n)
        t["notes"] = keep
    tracks = song.setdefault("tracks", [])
    imp = next((t for t in tracks
                if str(t.get("name", "")) == "impact"), None)
    if imp is None:
        imp = {"name": "impact", "source": {"id": "crash_noise"},
               "gainDb": -4.0, "notes": []}
        tracks.append(imp)
    if not any(abs(float(n.get("start", 0)) - b) < 1e-6
               for n in imp["notes"]):
        imp["notes"].append({"start": round(b, 4), "len": 2.0,
                             "pitch": 60, "vel": 0.9})
    return [{"kind": "gap_impact", "boundary": b, "gap_beats": gap_beats,
             "cleared": cleared, "trimmed": trimmed}]


# W85 (r-15 item 242): arrangement-level DJ FX — one op, style-keyed,
# composing the house gestures (never re-encoded).
DJ_TRANSITION_STYLES = {
    "edm_lift":  ("riser", "gap_impact"),
    "dub_drop":  ("reverse_swell", "tape_stop"),
    "radio_cut": ("gap_impact",),
    "psy_wash":  ("reverse_swell", "riser"),
    "club_slam": ("riser", "tape_stop"),
}


def dj_transition(song, boundary_beat, style="edm_lift"):
    """Stamp a named transition ONTO a boundary: each style composes
    the standing gesture ops. Mutates; returns the combined ledger."""
    if style not in DJ_TRANSITION_STYLES:
        return [{"kind": "error",
                 "why": f"unknown style '{style}' — "
                        f"{sorted(DJ_TRANSITION_STYLES)}"}]
    bpm = float((song or {}).get("bpm", 120) or 120)
    edits = []
    for g in DJ_TRANSITION_STYLES[style]:
        if g == "riser":
            lane = riser(boundary_beat, 2, bpm, kind="tonal")
            song.setdefault("tracks", []).append(lane)
            edits.append({"kind": "riser", "lane": lane["name"]})
        elif g == "reverse_swell":
            lane = reverse_swell(boundary_beat, 1, bpm)
            song.setdefault("tracks", []).append(lane)
            edits.append({"kind": "reverse_swell", "lane": lane["name"]})
        elif g == "gap_impact":
            edits += gap_impact(song, boundary_beat, 0.5)
        elif g == "tape_stop":
            edits += tape_stop(song, max(boundary_beat - 2.0, 0.0), 2.0)
    edits.append({"kind": "dj_transition", "style": style,
                  "at": boundary_beat,
                  "why": (f"'{style}' stamped at beat {boundary_beat:g} "
                          f"({' + '.join(DJ_TRANSITION_STYLES[style])})")})
    return edits


def reverse_swell(boundary_beat, bars_ahead=1, bpm=120, gain_db=-7.0):
    """W61 (item 208): the reverse-cymbal swell INTO a boundary — the
    one-resolver path: riser(kind='noise') IS the rev_crash swell; this
    op names the gesture and defaults it to the tight 1-bar pre-roll
    the catalog uses."""
    return riser(boundary_beat, bars_ahead, bpm, kind="noise",
                 gain_db=gain_db)


def tape_stop(song, at_beat, len_beats=2.0, depth=0.9):
    """W61 (item 209): the tape-stop GESTURE in this house's vocabulary
    — masterGainDb dives with an early-jump curve while the master
    djfilter knob plunges dark (a SWEEP, exempt from the parked-dark
    trap by the doctor's own law), a subdrop lands the pitch-fall
    illusion at the floor, and BOTH resume clean one beat later. True
    varispeed needs an engine pitch fx — named gap, the gesture reads
    on every system today. Mutates; returns the ledger."""
    a, b = float(at_beat), float(at_beat) + float(len_beats)
    master = song.setdefault("master", [])
    fi = next((i for i, f in enumerate(master)
               if str(f.get("id")) == "fx_djfilter"), None)
    if fi is None:
        wall = next((i for i, f in enumerate(master)
                     if "truepeak" in str(f.get("id", ""))
                     or "brickwall" in str(f.get("id", ""))), len(master))
        master.insert(wall, {"id": "fx_djfilter",
                             "params": {"knob": 0.0, "res": 1.0}})
        fi = wall
    auto = song.setdefault("automation", [])
    auto.append({"target": f"master[{fi}].knob",
                 "points": [{"beat": a, "v": 0.0},
                            {"beat": b, "v": -abs(depth), "curve": -0.4},
                            {"beat": b + 1.0, "v": 0.0}]})
    auto.append({"target": "masterGainDb",
                 "points": [{"beat": a, "v": 0.0},
                            {"beat": b, "v": -24.0, "curve": -0.5},
                            {"beat": b + 1.0, "v": 0.0}]})
    lane = {"name": f"tapestop_{int(a)}",
            "source": {"id": "subdrop"}, "gainDb": -8.0, "pan": 0.0,
            "notes": [{"start": round(b - 0.5, 4), "len": 1.0,
                       "pitch": 36, "vel": 0.9}]}
    song.setdefault("tracks", []).append(lane)
    return [{"kind": "tape_stop", "at": a, "len": float(len_beats),
             "why": (f"beats {a:.0f}-{b:.0f}: master dives dark + quiet "
                     "(early-jump curves), the subdrop lands the fall, "
                     "everything snaps back a beat later — the stop "
                     "that makes the next downbeat hit twice as hard")}]


_NOTE_NAMES = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A",
               "Bb", "B")
_MAJ = (0, 2, 4, 5, 7, 9, 11)
# W59 (r-15 item 133): per-bar turnaround templates — the harmonic
# gesture that RETURNS the form to its top. Degree, quality.
TURNAROUNDS = {
    "jazz": (("ii", "m7"), ("V", "7")),
    "blues": (("I", "7"), ("V", "7")),
    "gospel": (("vi", "m7"), ("V", "7")),
    "soul": (("vi", "m7"), ("V", "7")),
    "default": (("IV", ""), ("V", "")),
}
_DEG = {"I": 0, "ii": 1, "iii": 2, "IV": 3, "V": 4, "vi": 5, "vii": 6}


def _tn_family(genre):
    g = str(genre or "").lower()
    for fam in ("jazz", "blues", "gospel", "soul"):
        if fam in g:
            return fam
    if any(w in g for w in ("swing", "bebop", "bossa", "neo_soul",
                            "neosoul", "rnb", "funk")):
        return "jazz"
    return "default"


def royal_road(song, start_bar=1, cycles=2):
    """W88 (r-24 item 247): the J-pop ROYAL ROAD as a one-click spine —
    IVmaj7 -> V7 -> iii7 -> vi (one chord per bar, transposed to the
    song's key; the V -> iii move IS the deceptive cadence that makes
    it float). Writes chords[]; declared-key-or-no-op."""
    import theory as _t
    key = _t.parse_key((song or {}).get("key"))
    if not key:
        return []
    tonic = int(key.get("tonic_pc", 0))
    degs = ((5, "maj7"), (7, "7"), (4, "m7"), (9, "m"))
    chords = song.setdefault("chords", [])
    bar = int(start_bar)
    span = set(range(bar, bar + 4 * int(cycles)))
    chords[:] = [c for c in chords if int(c.get("bar", 0)) not in span]
    names = []
    for cy in range(int(cycles)):
        for off, qual in degs:
            pc = (tonic + off) % 12
            sym = _NOTE_NAMES[pc] + qual
            chords.append({"bar": bar, "chord": sym, "conf": 1.0})
            names.append(sym)
            bar += 1
    chords.sort(key=lambda c: int(c.get("bar", 0)))
    return [{"kind": "royal_road", "bars": [int(start_bar), bar],
             "cycle": names[:4],
             "why": (f"the Royal Road lands bars {start_bar}-{bar - 1}: "
                     f"{'-'.join(names[:4])} — the V->iii deceptive "
                     "cadence is the float")}]


def final_lift(song, semis=1):
    """W88 (item 247 + the w76 gospel-reprise remainder): the +1/+2
    semitone MODULATION into the final hook — the last hook section's
    notes (all unmuted melodic lanes) and its chords[] rows transpose
    up. The oldest lift in the book, still undefeated. Idempotent."""
    if (song or {}).get("final_lift"):
        return []
    import form_court as _fc
    secs = sorted((s for s in (song or {}).get("sections", []) or []
                   if isinstance(s, dict)),
                  key=lambda s: float(s.get("startBar", 0)))
    hooks = [i for i, s in enumerate(secs)
             if _fc._sec_class(s.get("name")) == "hook"]
    if len(hooks) < 2:
        return []                       # ONE chorus has nothing to lift
    i = hooks[-1]
    a = float(secs[i].get("startBar", 0))
    b = float(secs[i + 1].get("startBar",
                              song.get("lengthBars", a + 8)))         if i + 1 < len(secs) else float(song.get("lengthBars", a + 8))
    moved = 0
    for t in song.get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted") or not t.get("notes"):
            continue
        nm = str(t.get("name", "")).lower()
        if any(w in nm for w in ("kick", "snare", "clap", "hat", "perc",
                                 "cym", "tom", "shaker", "_")):
            continue
        for n in t["notes"]:
            try:
                s = float(n.get("start", 0))
            except Exception:
                continue
            if a * 4.0 <= s < b * 4.0:
                n["pitch"] = int(n.get("pitch", 60)) + int(semis)
                moved += 1
    for c in song.get("chords", []) or []:
        if a < float(c.get("bar", 0)) <= b:
            import theory as _t
            ch = _t.parse_chord(c.get("chord"))
            if ch:
                root = (int(ch["root_pc"]) + int(semis)) % 12
                tail = str(c["chord"])[_root_len(c["chord"]):]
                c["chord"] = _NOTE_NAMES[root] + tail
    if not moved:
        return []
    song["final_lift"] = int(semis)
    return [{"kind": "final_lift", "semis": int(semis),
             "fromBar": a, "toBar": b, "notes": moved,
             "why": (f"the final '{secs[i].get('name')}' lifts "
                     f"+{semis} semitone{'s' if semis > 1 else ''} "
                     f"({moved} notes + its chords) — the reprise "
                     "modulation, gospel to K-pop, still undefeated")}]


def _root_len(sym):
    s = str(sym)
    return 2 if len(s) > 1 and s[1] in "b#" else 1


def turnaround(song, genre="", top_bar=None, tritone_sub=False):
    """W59 (item 133): write the genre's turnaround into the LAST TWO
    BARS before the form's top — chords[] entries + a comped voicing on
    the song's chordal lane (voice-led via theory.voice_chord). The V
    may take the tritone sub (jazz flavor). Returns the edit ledger."""
    import theory as _t
    key = _t.parse_key((song or {}).get("key"))
    if not key:
        return []
    bars_total = int((song or {}).get("lengthBars", 0) or 0)
    if bars_total < 4:
        return []
    top = int(top_bar or (bars_total + 1))     # 1-based bar the form re-enters
    b1, b2 = top - 2, top - 1
    if b1 < 1:
        return []
    tonic = int(key.get("tonic_pc", 0))
    minor = "min" in str(key.get("mode", ""))
    fam = _tn_family(genre)
    syms = []
    for i, (deg, qual) in enumerate(TURNAROUNDS[fam]):
        pc = (tonic + _MAJ[_DEG[deg]]) % 12
        if minor and deg in ("IV", "V") and not qual:
            qual = "m" if deg == "IV" else ""   # minor keys: iv, V stays major
        if tritone_sub and i == len(TURNAROUNDS[fam]) - 1 and "7" in qual:
            pc = (pc + 6) % 12                  # the subV
        syms.append(_NOTE_NAMES[pc] + qual)
    chords = song.setdefault("chords", [])
    chords[:] = [c for c in chords
                 if int(c.get("bar", 0)) not in (b1, b2)]
    chords.append({"bar": b1, "chord": syms[0], "conf": 1.0})
    chords.append({"bar": b2, "chord": syms[1], "conf": 1.0})
    chords.sort(key=lambda c: int(c.get("bar", 0)))
    edits = [{"kind": "turnaround_chords", "bars": [b1, b2],
              "chords": syms, "family": fam,
              "why": (f"bars {b1}-{b2}: {'-'.join(syms)} — the {fam} "
                      "turnaround walks the form back to its top"
                      + (" (tritone sub)" if tritone_sub else ""))}]
    # comp the voicing on the song's chordal lane
    lane = None
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if any(w in nm for w in ("keys", "piano", "rhodes", "organ",
                                 "chord", "pad", "ep_", "comp")):
            lane = t
            break
    if lane is not None:
        a_beat, z_beat = (b1 - 1) * 4.0, (b2) * 4.0
        lane.setdefault("notes", [])
        lane["notes"] = [n for n in lane["notes"]
                         if not (a_beat <= float(n.get("start", 0))
                                 < z_beat)]
        prev = None
        placed = 0
        for i, sym in enumerate(syms):
            ch = _t.parse_chord(sym)
            if not ch:
                continue
            voic = _t.voice_chord(ch, register=(48, 72),
                                  prev_voicing=prev)
            prev = voic
            for p in voic:
                lane["notes"].append({"start": a_beat + i * 4.0,
                                      "len": 4.0, "pitch": int(p),
                                      "vel": 92})
                placed += 1
        lane["notes"].sort(key=lambda n: float(n.get("start", 0)))
        edits.append({"kind": "turnaround_comp", "track": lane.get("name"),
                      "notes": placed,
                      "why": (f"'{lane.get('name')}' comps the turnaround "
                              "(voice-led, register 48-72)")})
    return edits


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE TRANSITION OPS (wave 26)")
    ap.add_argument("song")
    ap.add_argument("op", choices=["riser", "gap_impact", "turnaround",
                                   "dj_transition"])
    ap.add_argument("--style", default="edm_lift")
    ap.add_argument("--boundary", type=float, default=None)
    ap.add_argument("--bars", type=int, default=2)
    ap.add_argument("--kind", default="tonal")
    ap.add_argument("--gap", type=float, default=0.5)
    ap.add_argument("--genre", default="")
    ap.add_argument("--top-bar", type=int, default=None)
    ap.add_argument("--tritone-sub", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song))
    if args.op == "dj_transition":
        if args.boundary is None:
            ap.error("dj_transition needs --boundary")
        out = dj_transition(song, args.boundary, args.style)
    elif args.op == "turnaround":
        out = turnaround(song, args.genre, args.top_bar, args.tritone_sub)
    elif args.op == "riser":
        if args.boundary is None:
            ap.error("riser needs --boundary")
        lane = riser(args.boundary, args.bars,
                     float(song.get("bpm", 120) or 120), args.kind)
        song.setdefault("tracks", []).append(lane)
        out = [{"kind": "riser", "lane": lane["name"]}]
    else:
        if args.boundary is None:
            ap.error("gap_impact needs --boundary")
        out = gap_impact(song, args.boundary, args.gap)
    json.dump(song, open(args.song, "w"), indent=1)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
