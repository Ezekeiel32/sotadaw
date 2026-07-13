#!/usr/bin/env python3
"""THE SCALPEL — the surgical-edit kernel (pure python, zero deps).

Everything here is symbolic and deterministic. Three jobs:

  1. ADDRESS   — resolve any human coordinate (timestamp, bar, beat, section name,
                 pitch/velocity/grid filters, "the 3rd hit") into concrete note refs
                 inside a song dict. TempoClock integrates the tempoMap so "1:23"
                 lands on the right beat even across tempo steps and ramps.
  2. CUT       — apply_ops mutates ONLY the resolved notes (set/shift/scale/quantize/
                 humanize/stretch/velocity_ramp/split/strum/arp/delete/insert/replace/retrack) and
                 emits a RECEIPT: exact before/after note keys, counts, summary.
  3. PROVE     — semantic_diff(base, prop) + containment(diff, receipts) verifies a
                 proposal changed nothing beyond what the receipts declare. This is
                 the SCOPE LAW: "surgical" is enforced, not vibes.

Note identity is the natural key (trackName, round(start,4), pitch) — song.json has
no note ids and doesn't need them. A vel/len tweak keeps its key (reported as
"changed"); a move is remove+add (both keys land in the receipt's touched set).

Beats are pre-swing grid positions (swing is applied at the engine). Bar<->beat
crossings route through tools/meter.py — THE WORLD GRID (#1): meterMap[] redefines
what a bar is; mapless songs are bit-exact 4/4 identity (grid_lint is the law).
"""
import bisect, json, math, os, random, re, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from meter import bar_start_q, bar_at_q, song_meter   # the ONE bar<->beat resolver

# ---------------------------------------------------------------- pitch names
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_FLAT = {"DB": 1, "EB": 3, "GB": 6, "AB": 8, "BB": 10}

def pitch_name(p):
    """MIDI -> name, C4=60 convention."""
    p = int(p)
    return f"{_NOTE_NAMES[p % 12]}{p // 12 - 1}"

def parse_pitch_class(s):
    """'F#'/'Gb'/'f' -> 0..11, or None."""
    s = str(s).strip().upper().replace("♯", "#").replace("♭", "B")
    if s in _FLAT:
        return _FLAT[s]
    if s in _NOTE_NAMES:
        return _NOTE_NAMES.index(s)
    return None

def parse_pitch_name(s):
    """'F#2' / 'Gb-1' -> MIDI (C4=60), or None."""
    m = re.fullmatch(r"([A-Ga-g][#b♯♭]?)(-?\d+)", str(s).strip())
    if not m:
        return None
    pc = parse_pitch_class(m.group(1))
    if pc is None:
        return None
    midi = (int(m.group(2)) + 1) * 12 + pc
    return midi if 0 <= midi <= 127 else None

# ---------------------------------------------------------------- tempo clock
def _shape(u, c):
    """Tracktion-style segment shape: c=0 linear, c->1 late (hold-then-move),
    c->-1 early (jump-then-settle). Exact at c in {0}; monotone approximation else."""
    if c >= 0.999:
        return 0.0          # pure hold: value stays at segment start until the next point
    if c <= -0.999:
        return 1.0          # pure jump
    if abs(c) < 1e-9:
        return u
    k = 1.0 + 4.0 * abs(c)
    return u ** k if c > 0 else 1.0 - (1.0 - u) ** k

class TempoClock:
    """beats <-> seconds under song.bpm + tempoMap[{bar,bpm,curve}].
    Span [P_i, P_i+1) is shaped by P_i's curve (engine law: curve rides the span
    LEAVING the point; default 1 = hold-then-step, 0 = linear ramp)."""

    def __init__(self, song):
        base = float(song.get("bpm", 120.0))
        mm = song_meter(song)     # tempoMap points land TRUE under changing meters (#1)
        pts = [{"beat": 0.0, "bpm": base, "curve": 1.0}]
        for p in sorted(song.get("tempoMap") or [], key=lambda q: float(q.get("bar", 0))):
            b = bar_start_q(mm, float(p.get("bar", 0)))
            if b <= 0:
                pts[0] = {"beat": 0.0, "bpm": float(p.get("bpm", base)),
                          "curve": float(p.get("curve", 1.0))}
            else:
                pts.append({"beat": b, "bpm": float(p.get("bpm", base)),
                            "curve": float(p.get("curve", 1.0))})
        self.total_beats = max(bar_start_q(mm, float(song.get("lengthBars", 4))),
                               pts[-1]["beat"] + 4.0)
        self.segs = []            # (b0, b1, bpm0, bpm1, curve) — bpm1 = value at b1
        self._cum = [0.0]         # seconds at each segment start
        for i, p in enumerate(pts):
            b0 = p["beat"]
            b1 = pts[i + 1]["beat"] if i + 1 < len(pts) else max(self.total_beats, b0 + 4.0)
            bpm1 = pts[i + 1]["bpm"] if i + 1 < len(pts) else p["bpm"]
            self.segs.append((b0, b1, p["bpm"], bpm1, p["curve"]))
        for s in self.segs:
            self._cum.append(self._cum[-1] + self._seg_seconds(s, s[1]))
        self._starts = [s[0] for s in self.segs]

    def _bpm_at(self, seg, b):
        b0, b1, v0, v1, c = seg
        if b1 <= b0 or v0 == v1:
            return v0
        u = min(1.0, max(0.0, (b - b0) / (b1 - b0)))
        return v0 + (v1 - v0) * _shape(u, c)

    def _seg_seconds(self, seg, up_to_beat):
        """Seconds spent inside seg from its start up to up_to_beat (clamped)."""
        b0, b1, v0, v1, c = seg
        hi = min(up_to_beat, b1)
        if hi <= b0:
            return 0.0
        if v0 == v1 or c >= 0.999:                      # constant
            return (hi - b0) * 60.0 / v0
        if c <= -0.999:                                 # instant jump to v1
            return (hi - b0) * 60.0 / v1
        if abs(c) < 1e-9 and v1 != v0:                  # linear in bpm: analytic
            frac = (hi - b0) / (b1 - b0)
            va, vb = v0, v0 + (v1 - v0) * frac
            return 60.0 * (hi - b0) / (vb - va) * math.log(vb / va) if vb != va else (hi - b0) * 60.0 / va
        n = 64                                          # shaped: Simpson
        h = (hi - b0) / n
        acc = 0.0
        for i in range(n + 1):
            w = 1 if i in (0, n) else (4 if i % 2 else 2)
            acc += w * 60.0 / self._bpm_at(seg, b0 + i * h)
        return acc * h / 3.0

    def seconds_at(self, beat):
        beat = max(0.0, float(beat))
        i = max(0, bisect.bisect_right(self._starts, beat) - 1)
        return self._cum[i] + self._seg_seconds(self.segs[i], beat)

    def beat_at(self, seconds):
        seconds = max(0.0, float(seconds))
        lo, hi = 0.0, self.total_beats
        while self.seconds_at(hi) < seconds and hi < 16384:
            hi *= 2                                     # beyond song end: extrapolate
        for _ in range(60):
            mid = (lo + hi) / 2
            if self.seconds_at(mid) < seconds:
                lo = mid
            else:
                hi = mid
        return round((lo + hi) / 2, 4)

    def bpm_at(self, beat):
        i = max(0, bisect.bisect_right(self._starts, float(beat)) - 1)
        return self._bpm_at(self.segs[i], float(beat))

def parse_timestamp(s):
    """'1:23' | '1:23.45' | '83.5s' | '83.5' -> seconds, or None."""
    s = str(s).strip().lower()
    m = re.fullmatch(r"(\d+):(\d{1,2}(?:\.\d+)?)", s)
    if m:
        return int(m.group(1)) * 60 + float(m.group(2))
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*s(?:ec(?:onds?)?)?", s)
    if m:
        return float(m.group(1))
    try:
        return float(s)
    except ValueError:
        return None

# ---------------------------------------------------------------- sections
def section_spans(song):
    """[(name, startBeat, endBeat)] — end = next section start or song end."""
    secs = sorted(song.get("sections") or [], key=lambda s: float(s.get("startBar", 0)))
    mm = song_meter(song)
    total = bar_start_q(mm, float(song.get("lengthBars", 4)))
    out = []
    for i, s in enumerate(secs):
        b0 = bar_start_q(mm, float(s.get("startBar", 0)))
        b1 = bar_start_q(mm, float(secs[i + 1].get("startBar", 0))) if i + 1 < len(secs) else total
        out.append((str(s.get("name", f"section{i}")), b0, b1))
    return out

def section_at(song, beat):
    """(name, b0, b1, index) of the section containing beat, or None."""
    for i, (nm, b0, b1) in enumerate(section_spans(song)):
        if b0 <= beat < b1:
            return (nm, b0, b1, i)
    return None

def find_section(song, name, occurrence=1):
    name = str(name).strip().lower()
    hits = [sp for sp in section_spans(song) if sp[0].strip().lower() == name]
    if not hits:
        hits = [sp for sp in section_spans(song) if name in sp[0].strip().lower()]
    if not hits:
        return None
    occurrence = int(occurrence)
    idx = occurrence - 1 if occurrence > 0 else occurrence
    try:
        return hits[idx]
    except IndexError:
        return hits[-1]

# ---------------------------------------------------------------- roles
_ROLE_TOKENS = [
    ("kick", ("kick", "bd", "bassdrum")), ("bass", ("bass", "sub", "808", "reese", "low")),
    ("snare", ("snare", "sd", "rim", "clap")), ("hat", ("hat", "hh", "hihat", "shaker", "ride", "cymbal", "crash")),
    ("perc", ("perc", "conga", "bongo", "tom", "cowbell", "rimshot", "clave", "tamb")),
    ("pad", ("pad", "string", "strings", "choir", "drone", "atmo", "ambient", "swell")),
    ("lead", ("lead", "melody", "pluck", "arp", "solo", "hook", "whistle")),
    ("keys", ("keys", "piano", "rhodes", "organ", "epiano", "wurli", "clav")),
    ("chords", ("chord", "stab", "chords", "comp")),
    ("vocal", ("vocal", "vox", "voice", "adlib", "choir")),
    ("fx", ("fx", "riser", "sweep", "impact", "noise", "downlifter", "uplifter", "crash")),
]
ADJECTIVES = {   # descriptor words -> tokens that corroborate a candidate
    "squelchy": ("acid", "303", "filter", "reso", "tb"), "acid": ("303", "acid", "filter"),
    "punchy": ("kick", "punch", "comp", "transient"), "boomy": ("808", "sub", "bass", "kick"),
    "bright": ("hat", "lead", "bell", "high", "pluck"), "dark": ("pad", "sub", "low", "minor"),
    "warm": ("pad", "keys", "rhodes", "analog", "tape"), "airy": ("pad", "choir", "breath", "air"),
    "gritty": ("saturate", "dist", "drive", "grime"), "wobbly": ("wobble", "lfo", "reese", "dubstep"),
    "plucky": ("pluck", "arp", "stab"), "dreamy": ("pad", "reverb", "chorus", "shimmer"),
}

def _track_tokens(t):
    toks = set(re.split(r"[^a-z0-9#]+", str(t.get("name", "")).lower()))
    src = t.get("source") or {}
    for v in (src.get("id"), src.get("kit"), src.get("plugin"), src.get("preset")):
        if v:
            toks |= set(re.split(r"[^a-z0-9]+", str(v).lower()))
    for f in t.get("fx") or []:
        toks |= set(re.split(r"[^a-z0-9]+", str(f.get("id", "")).lower()))
    toks.discard("")
    return toks

def track_role(t):
    """(role, evidence) — name/source tokens first, register+rhythm heuristics second."""
    toks = _track_tokens(t)
    toks = toks | {tk[:-1] for tk in toks if len(tk) > 3 and tk.endswith("s")}
    for role, keys in _ROLE_TOKENS:
        hit = toks & set(keys)
        if hit:
            return role, f"token '{sorted(hit)[0]}'"
    notes = t.get("notes") or []
    if not notes:
        return ("audio" if t.get("audioClips") or (t.get("source") or {}).get("kind") == "audio"
                else "?"), "no notes"
    pitches = sorted(n["pitch"] for n in notes)
    med = pitches[len(pitches) // 2]
    lens = sorted(n.get("len", 0.25) for n in notes)
    med_len = lens[len(lens) // 2]
    distinct = len(set(pitches))
    if med < 45:
        return ("kick" if distinct <= 2 and med_len < 0.35 else "bass"), f"register (median {pitch_name(med)})"
    if distinct <= 3 and med_len <= 0.3:
        return "perc", f"repeated short notes at {pitch_name(med)}"
    if med_len >= 1.5:
        return "pad", f"long notes (median len {med_len:g})"
    return ("lead" if med >= 65 else "chords"), f"register (median {pitch_name(med)})"

def score_track_query(song, query):
    """Rank tracks against free words: token overlap + role + adjective corroboration.
    -> [(score, track_index, evidence_str)] best-first (score>0 only)."""
    words = [w for w in re.split(r"[^a-z0-9#]+", str(query).lower()) if w and w not in
             ("the", "a", "an", "that", "this", "sound", "at", "in", "on", "of", "one")]
    out = []
    for ti, t in enumerate(song.get("tracks", [])):
        toks = _track_tokens(t)
        role, rev = track_role(t)
        score, ev = 0.0, []
        for w in words:
            if w in toks:
                score += 3; ev.append(f"'{w}'∈tokens")
            elif w == role:
                score += 2.5; ev.append(f"role={role} ({rev})")
            elif w in ADJECTIVES:
                cor = set(ADJECTIVES[w]) & toks
                if cor:
                    score += 1.5; ev.append(f"'{w}'→{sorted(cor)[0]}")
            elif any(w in tk for tk in toks if len(w) > 2):
                score += 1; ev.append(f"'{w}'~substr")
        if score > 0:
            out.append((score, ti, "; ".join(ev)))
    return sorted(out, key=lambda x: (-x[0], x[1]))

# ---------------------------------------------------------------- selector
NOTE_KEY_DP = 4

def note_key(track_name, n):
    return (str(track_name), round(float(n["start"]), NOTE_KEY_DP), int(n["pitch"]))

def resolve_time_point(song, spec, clock=None):
    """One point in time -> beat. spec: number (beats) | {'beat':x}|{'bar':x}|
    {'time':'1:23'|secs}|{'section':name[,'barOffset':k]} | '1:23' string."""
    clock = clock or TempoClock(song)
    if isinstance(spec, (int, float)):
        return float(spec)
    if isinstance(spec, str):
        sec = parse_timestamp(spec)
        if sec is None:
            raise ValueError(f"can't parse time '{spec}'")
        return clock.beat_at(sec)
    if isinstance(spec, dict):
        if "beat" in spec:
            return float(spec["beat"])
        if "bar" in spec:
            return bar_start_q(song_meter(song), float(spec["bar"]))
        if "time" in spec:
            sec = spec["time"] if isinstance(spec["time"], (int, float)) else parse_timestamp(spec["time"])
            if sec is None:
                raise ValueError(f"can't parse time '{spec['time']}'")
            return clock.beat_at(float(sec))
        if "section" in spec:
            sp = find_section(song, spec["section"], spec.get("occurrence", 1))
            if not sp:
                raise ValueError(f"no section '{spec['section']}' (have: "
                                 f"{[s[0] for s in section_spans(song)]})")
            mm = song_meter(song)
            return bar_start_q(mm, bar_at_q(mm, sp[1]) + float(spec.get("barOffset", 0)))
    raise ValueError(f"bad time spec: {spec!r}")

def _num_range(spec, lo_def, hi_def):
    """29 | [lo,hi] | {'min','max','eq'} -> (lo, hi_inclusive)."""
    if spec is None:
        return (lo_def, hi_def)
    if isinstance(spec, (int, float)):
        return (float(spec), float(spec))
    if isinstance(spec, (list, tuple)) and len(spec) == 2:
        return (float(spec[0]), float(spec[1]))
    if isinstance(spec, dict):
        if "eq" in spec:
            return (float(spec["eq"]), float(spec["eq"]))
        return (float(spec.get("min", lo_def)), float(spec.get("max", hi_def)))
    raise ValueError(f"bad numeric range: {spec!r}")

class Resolution:
    def __init__(self):
        self.track_idxs = []      # resolved track indices (order = song order)
        self.refs = []            # [(ti, note_dict)] matched notes (live object refs)
        self.range = None         # (b0, b1) beats, or None = whole song
        self.explain = []         # human trail of every resolution step
        self.selector = None

    def onsets(self):
        return sorted({round(float(n["start"]), NOTE_KEY_DP) for _, n in self.refs})

    def tracks(self, song):
        return [song["tracks"][i].get("name", f"#{i}") for i in self.track_idxs]

    def span(self):
        if not self.refs:
            return self.range
        ss = [float(n["start"]) for _, n in self.refs]
        return (min(ss), max(float(n["start"]) + float(n.get("len", 0)) for _, n in self.refs))

def resolve_tracks(song, spec):
    """'all' | name | [names] | {'match': substr} | {'role': 'bass'} -> (idxs, explain)."""
    tracks = song.get("tracks", [])
    names = [t.get("name", f"#{i}") for i, t in enumerate(tracks)]
    if spec in (None, "all", "*"):
        return list(range(len(tracks))), "tracks: all"
    def find_one(nm):
        nml = str(nm).strip().lower()
        exact = [i for i, n in enumerate(names) if n.lower() == nml]
        if exact:
            return exact
        return [i for i, n in enumerate(names) if nml in n.lower()]
    if isinstance(spec, str):
        idxs = find_one(spec)
        if not idxs:
            raise ValueError(f"no track matching '{spec}'. tracks: {names}")
        return idxs, f"tracks: '{spec}' -> {[names[i] for i in idxs]}"
    if isinstance(spec, list):
        idxs = []
        for nm in spec:
            got = find_one(nm)
            if not got:
                raise ValueError(f"no track matching '{nm}'. tracks: {names}")
            idxs += [g for g in got if g not in idxs]
        return idxs, f"tracks: {[names[i] for i in idxs]}"
    if isinstance(spec, dict):
        if "match" in spec:
            idxs = find_one(spec["match"])
            if not idxs:
                raise ValueError(f"no track matching '{spec['match']}'. tracks: {names}")
            return idxs, f"tracks ~'{spec['match']}': {[names[i] for i in idxs]}"
        if "role" in spec:
            want = str(spec["role"]).lower()
            idxs = [i for i, t in enumerate(tracks) if track_role(t)[0] == want]
            if not idxs:
                raise ValueError(f"no track with role '{want}'. roles: "
                                 f"{[(names[i], track_role(t)[0]) for i, t in enumerate(tracks)]}")
            return idxs, f"tracks role={want}: {[names[i] for i in idxs]}"
    raise ValueError(f"bad tracks spec: {spec!r}")

def resolve_range(song, sel, clock=None):
    """beats/bars/section/time/around -> (b0, b1, explain) or (None, None, note)."""
    clock = clock or TempoClock(song)
    mm = song_meter(song)
    total = bar_start_q(mm, float(song.get("lengthBars", 4)))
    if sel.get("beats") is not None:
        a, b = float(sel["beats"][0]), float(sel["beats"][1])
        return a, b, f"beats [{a:g}, {b:g})"
    if sel.get("bars") is not None:
        a, b = bar_start_q(mm, float(sel["bars"][0])), bar_start_q(mm, float(sel["bars"][1]))
        return a, b, f"bars [{sel['bars'][0]:g}, {sel['bars'][1]:g}) = beats [{a:g}, {b:g})"
    if sel.get("section") is not None:
        spec = sel["section"]
        nm, occ = (spec.get("name"), spec.get("occurrence", 1)) if isinstance(spec, dict) else (spec, 1)
        sp = find_section(song, nm, occ)
        if not sp:
            raise ValueError(f"no section '{nm}' (have: {[s[0] for s in section_spans(song)]})")
        return sp[1], sp[2], f"section '{sp[0]}' = bars [{bar_at_q(mm, sp[1]):g}, {bar_at_q(mm, sp[2]):g}) = beats [{sp[1]:g}, {sp[2]:g})"
    if sel.get("time") is not None:
        tv = sel["time"]
        if isinstance(tv, (list, tuple)) and len(tv) == 2:
            a = resolve_time_point(song, {"time": tv[0]}, clock)
            b = resolve_time_point(song, {"time": tv[1]}, clock)
            return a, b, f"time [{tv[0]}, {tv[1]}] = beats [{a:g}, {b:g})"
        beat = resolve_time_point(song, {"time": tv}, clock)
        bb = math.floor(bar_at_q(mm, beat))
        a, b = bar_start_q(mm, bb), bar_start_q(mm, bb + 1)
        return a, b, f"time {tv} = beat {beat:g} (sec {clock.seconds_at(beat):.2f}) -> bar [{bb:g},{bb + 1:g})"
    if sel.get("around") is not None:
        ar = dict(sel["around"])
        w = float(ar.pop("widthBeats", 2.0))
        c = resolve_time_point(song, ar, clock)
        return max(0.0, c - w / 2), c + w / 2, f"around beat {c:g} ±{w/2:g}"
    return None, None, "range: whole song (0..%g)" % total

def resolve(song, sel):
    """Selector dict -> Resolution. Raises ValueError with a helpful message on miss."""
    sel = sel or {}
    clock = TempoClock(song)
    r = Resolution()
    r.selector = sel
    idxs, tex = resolve_tracks(song, sel.get("tracks"))
    r.track_idxs = idxs
    r.explain.append(tex)
    b0, b1, rex = resolve_range(song, sel, clock)
    r.range = (b0, b1) if b0 is not None else None
    r.explain.append(rex)

    p_lo, p_hi = 0.0, 127.0
    if sel.get("pitch") is not None:
        ps = sel["pitch"]
        if isinstance(ps, dict) and ("classes" in ps or "names" in ps):
            classes = {parse_pitch_class(c) for c in ps.get("classes", [])} - {None}
            exact = {parse_pitch_name(nm) for nm in ps.get("names", [])} - {None}
            pit_ok = lambda p: (p % 12 in classes) or (p in exact)
            r.explain.append(f"pitch classes {sorted(ps.get('classes', []))} names {sorted(ps.get('names', []))}")
        else:
            if isinstance(ps, str):
                mp = parse_pitch_name(ps)
                if mp is None:
                    raise ValueError(f"bad pitch '{ps}' (want e.g. 'F#2' or MIDI number)")
                ps = mp
            p_lo, p_hi = _num_range(ps, 0, 127)
            pit_ok = lambda p: p_lo <= p <= p_hi
            r.explain.append(f"pitch {pitch_name(int(p_lo))}({int(p_lo)})"
                             + (f"..{pitch_name(int(p_hi))}({int(p_hi)})" if p_hi != p_lo else ""))
    else:
        pit_ok = lambda p: True
    v_lo, v_hi = _num_range(sel.get("vel"), 0.0, 1.0)
    l_lo, l_hi = _num_range(sel.get("len"), 0.0, 1e9)
    if sel.get("vel") is not None:
        r.explain.append(f"vel {v_lo:g}..{v_hi:g}")
    if sel.get("len") is not None:
        r.explain.append(f"len {l_lo:g}..{l_hi:g}")
    grid = sel.get("grid")
    if grid:
        gstep = float(grid.get("step", 0.25))
        gphase = float(grid.get("phase", 0.0))
        gtol = float(grid.get("tol", 0.03))
        r.explain.append(f"grid step {gstep:g} phase {gphase:g} ±{gtol:g}")

    want_idx = None
    if sel.get("indices") is not None:          # the UI's native address form
        want_idx = {int(i) for i in sel["indices"]}
        if len(idxs) != 1:
            raise ValueError("indices selector needs exactly ONE track")
        r.explain.append(f"indices {sorted(want_idx)} (UI selection order)")
    for ti in idxs:
        for ni, n in enumerate(song["tracks"][ti].get("notes", [])):
            if want_idx is not None and ni not in want_idx:
                continue
            s = float(n["start"])
            if r.range and not (r.range[0] <= s < r.range[1]):
                continue
            if not pit_ok(int(n["pitch"])):
                continue
            if not (v_lo <= float(n.get("vel", 1.0)) <= v_hi):
                continue
            if not (l_lo <= float(n.get("len", 0.25)) <= l_hi):
                continue
            if grid:
                d = (s - gphase) % gstep
                if min(d, gstep - d) > gtol:
                    continue
            r.refs.append((ti, n))

    # onset-group operators (nth / count / every) — a chord is ONE moment
    if any(sel.get(k) is not None for k in ("nth", "count", "every")):
        groups = {}
        for ti, n in r.refs:
            groups.setdefault(round(float(n["start"]), NOTE_KEY_DP), []).append((ti, n))
        starts = sorted(groups)
        keep = list(starts)
        if sel.get("every") is not None:
            ev = sel["every"]
            step, phase = (int(ev.get("step", 2)), int(ev.get("phase", 0))) if isinstance(ev, dict) else (int(ev), 0)
            keep = [s for i, s in enumerate(keep) if i % step == phase]
            r.explain.append(f"every {step} (phase {phase}) of {len(starts)} onsets -> {len(keep)}")
        if sel.get("nth") is not None:
            k = int(sel["nth"])
            i = k - 1 if k > 0 else len(keep) + k
            if not 0 <= i < len(keep):
                raise ValueError(f"nth={k} out of range: only {len(keep)} matching onsets")
            keep = [keep[i]]
            r.explain.append(f"nth {k} -> onset at beat {keep[0]:g}")
        if sel.get("count") is not None:
            keep = keep[:max(0, int(sel["count"]))]
            r.explain.append(f"count -> first {len(keep)} onsets")
        kept = set(keep)
        r.refs = [(ti, n) for ti, n in r.refs if round(float(n["start"]), NOTE_KEY_DP) in kept]

    r.explain.append(f"matched {len(r.refs)} notes ({len(r.onsets())} onsets) "
                     f"on {len(set(ti for ti, _ in r.refs))} track(s)")
    return r

# ---------------------------------------------------------------- evidence
def automation_value_at(points, beat):
    """Interpolate an automation curve (same shape law as tempo/engine) at beat."""
    if not points:
        return None
    pts = sorted(points, key=lambda p: float(p.get("beat", 0)))
    if beat <= float(pts[0]["beat"]):
        return float(pts[0]["v"])
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if float(a["beat"]) <= beat <= float(b["beat"]):
            span = float(b["beat"]) - float(a["beat"])
            u = 0.0 if span <= 0 else (beat - float(a["beat"])) / span
            return float(a["v"]) + (float(b["v"]) - float(a["v"])) * _shape(u, float(a.get("curve", 0)))
    return float(pts[-1]["v"])

def whats_at(song, beat, halo=1.0):
    """The NOW snapshot: what is sounding / about to hit at `beat`, per track."""
    clock = TempoClock(song)
    mm = song_meter(song)
    beat = float(beat)
    sec = clock.seconds_at(beat)
    out = {"beat": round(beat, 3), "bar": round(bar_at_q(mm, beat), 3), "seconds": round(sec, 3),
           "clockTime": f"{int(sec // 60)}:{sec % 60:05.2f}", "bpm": round(clock.bpm_at(beat), 2),
           "section": None, "tracks": []}
    sc = section_at(song, beat)
    if sc:
        out["section"] = {"name": sc[0],
                          "barInSection": round(bar_at_q(mm, beat) - bar_at_q(mm, sc[1]), 2),
                          "bars": [bar_at_q(mm, sc[1]), bar_at_q(mm, sc[2])]}
    for ti, t in enumerate(song.get("tracks", [])):
        role, _ = track_role(t)
        sounding, upcoming = [], []
        for n in t.get("notes", []):
            s, ln = float(n["start"]), float(n.get("len", 0.25))
            if s <= beat < s + ln:
                sounding.append(n)
            elif beat < s <= beat + halo:
                upcoming.append(n)
        clips = []
        for c in t.get("audioClips", []) or []:
            cs, cl = float(c.get("startBeat", 0)), float(c.get("lengthBeats", 0))
            if cs <= beat < cs + cl:
                clips.append({"file": os.path.basename(str(c.get("file", "?"))),
                              "intoBeats": round(beat - cs, 2)})
        autos, auto_moving = [], False
        for a in t.get("automation", []) or []:
            v = automation_value_at(a.get("points", []), beat)
            if v is not None:
                autos.append({"target": a.get("target"), "value": round(v, 3)})
                va = automation_value_at(a.get("points", []), beat - halo)
                vb = automation_value_at(a.get("points", []), beat + halo)
                if abs(vb - va) > 1e-6:
                    auto_moving = True
        entry = {"track": t.get("name", f"#{ti}"), "index": ti, "role": role,
                 "source": (t.get("source") or {}).get("id") or (t.get("source") or {}).get("kit")
                           or (t.get("source") or {}).get("plugin") or "?"}
        if t.get("muted"):
            entry["muted"] = True
        if t.get("locked"):
            entry["locked"] = True
        if sounding:
            entry["sounding"] = [{"pitch": pitch_name(n["pitch"]), "midi": int(n["pitch"]),
                                  "start": round(float(n["start"]), 3),
                                  "vel": round(float(n.get("vel", 1)), 2)} for n in sounding[:6]]
        if upcoming:
            entry["nextOnset"] = round(min(float(n["start"]) for n in upcoming), 3)
        if clips:
            entry["clips"] = clips
        if autos:
            entry["automationNow"] = autos
        if sounding or upcoming or clips or auto_moving:
            out["tracks"].append(entry)
    return out

def render_whats_at(w):
    lines = [f"NOW: beat {w['beat']} (bar {w['bar']}, {w['clockTime']}, {w['bpm']} bpm)"
             + (f" — section '{w['section']['name']}' bar {w['section']['barInSection']} of "
                f"{w['section']['bars'][1] - w['section']['bars'][0]:g}" if w.get("section") else "")]
    for t in w["tracks"]:
        bits = [f"[{t['role']}] {t['track']} ({t['source']})"]
        if t.get("muted"):
            bits.append("MUTED")
        if t.get("locked"):
            bits.append("LOCKED")
        if t.get("sounding"):
            bits.append("sounding " + ", ".join(f"{s['pitch']} v{s['vel']}" for s in t["sounding"]))
        elif t.get("clips"):
            bits.append("clip " + ", ".join(f"{c['file']} +{c['intoBeats']}b" for c in t["clips"]))
        if t.get("nextOnset") is not None:
            bits.append(f"next hit @ {t['nextOnset']}")
        if t.get("automationNow"):
            bits.append("auto " + ", ".join(f"{a['target']}={a['value']}" for a in t["automationNow"]))
        lines.append("  " + " · ".join(bits))
    if not w["tracks"]:
        lines.append("  (silence — nothing sounding within a beat of here)")
    return "\n".join(lines)

# ---------------------------------------------------------------- ops
def _clamp_note(n):
    n["start"] = max(0.0, round(float(n["start"]), 6))
    n["len"] = max(0.01, round(float(n.get("len", 0.25)), 6))
    n["pitch"] = int(min(127, max(0, round(float(n["pitch"])))))
    n["vel"] = min(1.0, max(0.01, round(float(n.get("vel", 0.8)), 6)))
    if "chance" in n:                                    # HB5: per-note inclusion probability
        n["chance"] = min(1.0, max(0.0, round(float(n["chance"]), 6)))
    return n

def apply_ops(song, sel, ops, seed="scalpel"):
    """Resolve sel, apply ops IN ORDER to exactly the matched notes.
    Returns (receipt, resolution). Mutates song in place. Raises ValueError on bad ops.
    Ops: set/shift/scale/quantize/humanize/stretch/velocity_ramp/split/strum/arp/delete/insert/replace/retrack."""
    r = resolve(song, sel)
    tracks = song["tracks"]
    tname = lambda ti: tracks[ti].get("name", f"#{ti}")
    before_keys = sorted({note_key(tname(ti), n) for ti, n in r.refs})
    matched = list(r.refs)                     # (ti, note-object) — identity survives edits
    prop_changes = []
    op_log = []
    b0, b1 = r.range if r.range else (None, None)

    def default_insert_track():
        tis = sorted(set(ti for ti, _ in matched)) or r.track_idxs
        if len(tis) != 1:
            raise ValueError(f"insert/replace needs ONE resolved track (got "
                             f"{[tname(i) for i in tis]}) — pass 'track' on each note or narrow the selector")
        return tis[0]

    def do_insert(notes):
        added = []
        for spec in notes:
            spec = dict(spec)
            want = spec.pop("track", None)
            ti = default_insert_track() if want is None else resolve_tracks(song, want)[0][0]
            n = _clamp_note({"start": float(spec["start"]), "len": float(spec.get("len", 0.25)),
                             "pitch": spec["pitch"] if isinstance(spec["pitch"], (int, float))
                             else parse_pitch_name(spec["pitch"]),
                             "vel": float(spec.get("vel", 0.8))})
            if n["pitch"] is None:
                raise ValueError(f"bad pitch in insert: {spec!r}")
            if b0 is not None and not (b0 - 1e-6 <= n["start"] < b1 + 1e-6):
                raise ValueError(f"insert at beat {n['start']:g} is OUTSIDE the resolved range "
                                 f"[{b0:g},{b1:g}) — widen the selector or fix the note")
            tracks[ti].setdefault("notes", []).append(n)
            added.append((ti, n))
        return added

    for op in ops:
        kind = str(op.get("op", "")).lower()
        if kind == "set":
            fields = {k: op[k] for k in ("start", "len", "pitch", "vel", "chance") if k in op}
            if not fields:
                raise ValueError("set: give start/len/pitch/vel/chance")
            for ti, n in matched:
                for k, v in fields.items():
                    n[k] = parse_pitch_name(v) if k == "pitch" and isinstance(v, str) else float(v)
                _clamp_note(n)
            op_log.append(f"set {fields} on {len(matched)}")
        elif kind == "shift":
            for ti, n in matched:
                if "pitch" in op:
                    n["pitch"] = n["pitch"] + int(op["pitch"])
                if "start" in op:
                    n["start"] = float(n["start"]) + float(op["start"])
                if "vel" in op:
                    n["vel"] = float(n.get("vel", 0.8)) + float(op["vel"])
                _clamp_note(n)
            op_log.append("shift " + ", ".join(f"{k}{op[k]:+g}" for k in ("pitch", "start", "vel") if k in op)
                          + f" on {len(matched)}")
        elif kind == "scale":
            for ti, n in matched:
                if "vel" in op:
                    n["vel"] = float(n.get("vel", 0.8)) * float(op["vel"])
                if "len" in op:
                    n["len"] = float(n.get("len", 0.25)) * float(op["len"])
                _clamp_note(n)
            op_log.append("scale " + ", ".join(f"{k}×{op[k]:g}" for k in ("vel", "len") if k in op)
                          + f" on {len(matched)}")
        elif kind == "quantize":
            step = float(op.get("grid", 0.25))
            strength = min(1.0, max(0.0, float(op.get("strength", 1.0))))
            phase = float(op.get("phase", 0.0))
            for ti, n in matched:
                s = float(n["start"])
                q = phase + round((s - phase) / step) * step
                n["start"] = s + (q - s) * strength
                _clamp_note(n)
            op_log.append(f"quantize grid {step:g} str {strength:g} on {len(matched)}")
        elif kind == "humanize":
            tj = float(op.get("timing", 0.02))
            vj = float(op.get("vel", 0.05))
            sd = str(op.get("seed", seed))
            for ti, n in matched:
                rng = random.Random(f"{sd}:{tname(ti)}:{round(float(n['start']), 4)}:{int(n['pitch'])}")
                n["start"] = float(n["start"]) + rng.uniform(-tj, tj)
                n["vel"] = float(n.get("vel", 0.8)) * (1.0 + rng.uniform(-vj, vj))
                _clamp_note(n)
            op_log.append(f"humanize ±{tj:g}b ±{vj:.0%} on {len(matched)}")
        elif kind == "stretch":
            factor = float(op["factor"])
            if factor <= 0:
                raise ValueError("stretch factor must be > 0")
            anchor = float(op.get("anchor", b0 if b0 is not None else
                                  (min(float(n["start"]) for _, n in matched) if matched else 0)))
            for ti, n in matched:
                n["start"] = anchor + (float(n["start"]) - anchor) * factor
                n["len"] = float(n.get("len", 0.25)) * factor
                _clamp_note(n)
            op_log.append(f"stretch ×{factor:g} anchor {anchor:g} on {len(matched)}")
        elif kind == "velocity_ramp":
            va, vb = float(op.get("from", 0.5)), float(op.get("to", 1.0))
            if matched:
                ss = [float(n["start"]) for _, n in matched]
                lo = b0 if b0 is not None else min(ss)
                hi = b1 if b1 is not None else max(ss) + 1e-9
                for ti, n in matched:
                    u = 0.0 if hi <= lo else (float(n["start"]) - lo) / (hi - lo)
                    n["vel"] = va + (vb - va) * min(1.0, max(0.0, u))
                    _clamp_note(n)
            op_log.append(f"velocity_ramp {va:g}->{vb:g} on {len(matched)}")
        elif kind == "delete":
            for ti, n in matched:
                try:
                    tracks[ti]["notes"].remove(n)
                except ValueError:
                    pass
            op_log.append(f"delete {len(matched)}")
            matched = []
        elif kind == "insert":
            added = do_insert(op.get("notes", []))
            matched += added
            op_log.append(f"insert {len(added)}")
        elif kind == "replace":
            for ti, n in matched:
                try:
                    tracks[ti]["notes"].remove(n)
                except ValueError:
                    pass
            deleted = len(matched)
            matched = do_insert(op.get("notes", []))
            op_log.append(f"replace {deleted} -> {len(matched)}")
        elif kind == "retrack":
            dst = resolve_tracks(song, op["to"])[0][0]
            moved = 0
            for ti, n in matched:
                if ti == dst:
                    continue
                try:
                    tracks[ti]["notes"].remove(n)
                except ValueError:
                    continue
                tracks[dst].setdefault("notes", []).append(n)
                moved += 1
            matched = [(dst if any(n is m for m in tracks[dst].get("notes", [])) else ti, n)
                       for ti, n in matched]
            op_log.append(f"retrack {moved} -> '{tname(dst)}'")
        elif kind == "split":
            # THE KNIFE's agent twin (mirrors the roll's hold-K): cut each matched note
            # into two. {op:'split','at':beat} splits notes spanning that beat; else
            # {op:'split','ratio':0..1} (default 0.5) cuts each at its own fraction. The
            # head keeps its key (start+pitch), the tail gets a new one — the receipt's
            # added_keys authorizes the tail, so the SCOPE LAW stays satisfied.
            at = op.get("at")
            ratio = float(op.get("ratio", 0.5))
            out = []
            made = 0
            for ti, n in matched:
                s = float(n["start"])
                ln = float(n.get("len", 0.25))
                cut = float(at) if at is not None else s + ln * ratio
                if cut <= s + 1e-4 or cut >= s + ln - 1e-4:
                    out.append((ti, n))
                    continue
                tail = dict(n)
                tail["start"] = round(cut, 6)
                tail["len"] = round(s + ln - cut, 6)
                n["len"] = round(cut - s, 6)
                tracks[ti].setdefault("notes", []).append(tail)
                out.append((ti, n))
                out.append((ti, tail))
                made += 1
            matched = out
            op_log.append(f"split {made}")
        elif kind == "strum":
            # #23c the roll's Strum twin: notes sharing a start (a STACK, 1e-3 beats)
            # spread like a hand — k-th string +k*spread; releases HOLD (len shrinks
            # so every string rings to the same end). Stacks of one are left alone.
            ms = float(op.get("spread_ms", 15.0))
            up = str(op.get("direction", "up")) != "down"
            spread = ms * float(song.get("bpm", 120.0)) / 60000.0
            stacks = []
            for ti, n in matched:
                for st in stacks:
                    if abs(st[0] - float(n["start"])) < 1e-3:
                        st[1].append((ti, n))
                        break
                else:
                    stacks.append((float(n["start"]), [(ti, n)]))
            hands = 0
            for s0, grp in stacks:
                if len(grp) < 2:
                    continue
                hands += 1
                grp.sort(key=lambda tn: int(tn[1]["pitch"]), reverse=not up)
                for k, (ti, n) in enumerate(grp):
                    if k == 0:
                        continue
                    d = spread * k
                    n["start"] = float(n["start"]) + d
                    n["len"] = max(0.05, float(n.get("len", 0.25)) - d)
                    _clamp_note(n)
            op_log.append(f"strum {'up' if up else 'down'} {ms:g}ms on {hands} stacks")
        elif kind == "arp":
            # #23c the roll's Arp twin: each stack becomes a LINE at the grid —
            # pattern up/down/updown cycles the stack's pitches across its span.
            # New notes ride the receipt's added_keys (scope law, like split).
            pattern = str(op.get("pattern", "up"))
            grid = float(op.get("grid", 0.25))
            if grid <= 0:
                raise ValueError("arp grid must be > 0")
            stacks = []
            for ti, n in matched:
                for st in stacks:
                    if abs(st[0] - float(n["start"])) < 1e-3:
                        st[1].append((ti, n))
                        break
                else:
                    stacks.append((float(n["start"]), [(ti, n)]))
            out, born = [], 0
            for s0, grp in stacks:
                if len(grp) < 2:
                    out.extend(grp)
                    continue
                ti0 = grp[0][0]
                span = max(float(n.get("len", 0.25)) for _, n in grp)
                vel = sum(float(n.get("vel", 0.8)) for _, n in grp) / len(grp)
                ps = sorted(int(n["pitch"]) for _, n in grp)
                seq = list(ps)
                if pattern == "down":
                    seq.reverse()
                elif pattern in ("updown", "up-down"):
                    seq = ps + ps[-2:0:-1]
                for ti, n in grp:
                    try:
                        tracks[ti]["notes"].remove(n)
                    except ValueError:
                        pass
                j = 0
                while s0 + j * grid < s0 + span - 1e-6:
                    nn = {"start": round(s0 + j * grid, 6),
                          "len": round(min(grid, span - j * grid), 6),
                          "pitch": int(seq[j % len(seq)]),
                          "vel": round(vel, 3)}
                    _clamp_note(nn)
                    tracks[ti0].setdefault("notes", []).append(nn)
                    out.append((ti0, nn))
                    born += 1
                    j += 1
            matched = out
            op_log.append(f"arp {pattern} grid {grid:g} -> {born} notes")
        else:
            raise ValueError(f"unknown op '{kind}' (ops: set shift scale quantize humanize "
                             f"stretch velocity_ramp split strum arp delete insert replace "
                             f"retrack)")

    touched_tis = sorted(set(ti for ti, _ in matched) | set(ti for ti, _ in r.refs))
    for ti in touched_tis:
        tracks[ti].get("notes", []).sort(key=lambda n: (float(n["start"]), int(n["pitch"])))
    # keep the song valid if edits pushed past the end
    end = max([float(n["start"]) + float(n.get("len", 0)) for _, n in matched] or [0.0])
    mm = song_meter(song)
    total = bar_start_q(mm, float(song.get("lengthBars", 4)))
    if end > total:
        song["lengthBars"] = int(math.ceil(bar_at_q(mm, end)))
        prop_changes.append("meta:lengthBars")

    after_keys = sorted({note_key(tname(ti), n) for ti, n in matched})
    receipt = {
        "ts": round(time.time(), 2), "tool": "surgical_edit",
        "scope": {"tracks": [tname(i) for i in touched_tis],
                  "range": [round(b0, 4), round(b1, 4)] if b0 is not None else None,
                  "selector": sel},
        "matched": len(before_keys), "onsets": len(r.onsets()) or len({k[1] for k in after_keys}),
        "ops": op_log,
        "removed_keys": [list(k) for k in before_keys],
        "added_keys": [list(k) for k in after_keys],
        "prop_changes": prop_changes,
    }
    receipt["summary"] = summarize_receipt(receipt)
    return receipt, r


def edit_audio_clip(song, ti, ci, op, value=None):
    """Per-clip audio edit — the agent twin of the hands' HB3.1 clip verbs (the C++
    MainComponent::editClip). Mutates song in place; returns a one-line summary.
    Raises ValueError on a bad op / index. value meaning: move/trim_left = new
    startBeat; trim_right = new lengthBeats; fade_in/fade_out = beats; gain = dB;
    curve = 'linear|convex|concave|s'; clone = new startBeat; split = beat; remove = -.
    Left-trim keeps the audio anchored (offsetSec moves with the edge); split makes two
    clips SHARING the file with contiguous offsets (mirrors the roll knife)."""
    tracks = song["tracks"]
    if ti < 0 or ti >= len(tracks):
        raise ValueError(f"track {ti} out of range")
    clips = tracks[ti].setdefault("audioClips", [])
    if not clips:
        raise ValueError(f"track '{tracks[ti].get('name', ti)}' has no audio clips")
    if ci < 0 or ci >= len(clips):
        raise ValueError(f"clip {ci} out of range (0..{len(clips) - 1})")
    ac = clips[ci]
    total = bar_start_q(song_meter(song), float(song.get("lengthBars", 4)))
    bpm = float(song.get("bpm", 120) or 120)
    spb = 60.0 / (float(ac.get("sourceBpm", 0) or 0) or bpm)   # sec/beat at the clip's rate
    start = float(ac.get("startBeat", 0))
    lenB = float(ac.get("lengthBeats") or 0) or max(0.5, total - start)
    op = str(op)

    def clamp(x, lo, hi):
        return max(lo, min(hi, x))

    if op == "move":
        ac["startBeat"] = clamp(float(value), 0.0, max(0.0, total - 0.25))
    elif op == "trim_left":
        ns = clamp(float(value), 0.0, start + lenB - 0.25)
        dB = ns - start
        ac["offsetSec"] = max(0.0, float(ac.get("offsetSec", 0)) + dB * spb)
        ac["lengthBeats"] = max(0.25, lenB - dB)
        ac["startBeat"] = ns
    elif op == "trim_right":
        ac["lengthBeats"] = clamp(float(value), 0.25, max(0.25, total - start))
        ac["fadeOutBeats"] = min(float(ac.get("fadeOutBeats", 0)), ac["lengthBeats"])
    elif op == "fade_in":
        ac["fadeInBeats"] = clamp(float(value), 0.0, lenB)
    elif op == "fade_out":
        ac["fadeOutBeats"] = clamp(float(value), 0.0, lenB)
    elif op == "gain":
        ac["gainDb"] = clamp(float(value), -60.0, 12.0)
    elif op == "curve":
        if str(value) not in ("linear", "convex", "concave", "s"):
            raise ValueError("curve must be linear|convex|concave|s")
        ac["fadeCurve"] = str(value)
    elif op == "clone":
        cp = dict(ac)
        cp["startBeat"] = clamp(float(value), 0.0, max(0.0, total - 0.25))
        clips.append(cp)
    elif op == "split":
        cut = float(value)
        if cut <= start + 0.1 or cut >= start + lenB - 0.1:
            raise ValueError(f"split beat {cut} is not inside the clip [{start}, {start + lenB}]")
        tail = dict(ac)
        tail["startBeat"] = cut
        tail["offsetSec"] = float(ac.get("offsetSec", 0)) + (cut - start) * spb
        tail["lengthBeats"] = start + lenB - cut
        tail["fadeInBeats"] = 0
        ac["lengthBeats"] = cut - start
        ac["fadeOutBeats"] = min(float(ac.get("fadeOutBeats", 0)), ac["lengthBeats"])
        clips.append(tail)
    elif op == "remove":
        clips.pop(ci)
    else:
        raise ValueError(f"unknown clip op '{op}' (move/trim_left/trim_right/fade_in/"
                         f"fade_out/gain/curve/clone/split/remove)")
    return f"clip {op}"

def summarize_receipt(rc):
    sc = rc.get("scope", {})
    where = ""
    if sc.get("range"):
        a, b = sc["range"]
        where = f" in bars {a/4:g}–{b/4:g}"   # grid-ok: receipt rows carry no song context
    return (f"{'+'.join(sc.get('tracks') or ['?'])}: {'; '.join(rc.get('ops') or ['(no ops)'])}"
            f"{where} [{len(rc.get('removed_keys', []))}→{len(rc.get('added_keys', []))} notes]")

# ---------------------------------------------------------------- receipts IO
def ipc_dir():
    return os.environ.get("SOTADAW_IPC") or os.path.join(ROOT, "agent", "ipc")

def receipts_path():
    return os.path.join(ipc_dir(), "receipts.jsonl")

def append_receipt(song_name, receipt):
    receipt = dict(receipt)
    receipt["song"] = song_name
    os.makedirs(ipc_dir(), exist_ok=True)
    with open(receipts_path(), "a") as f:
        f.write(json.dumps(receipt) + "\n")

def coarse_receipt(song_name, tool, fields=None, track_wild=None, summary=""):
    """For blunt tools (update_track, clear_bars, automate...): declare WHAT KIND of
    change is authorized, not per-note keys. fields: ['meta:bpm','track:X:fx',...];
    track_wild: track names whose NOTES may change wholesale."""
    append_receipt(song_name, {"ts": round(time.time(), 2), "tool": tool,
                               "fields": fields or [], "track_wild": track_wild or [],
                               "summary": summary})

def read_receipts(song_name):
    out = []
    try:
        for line in open(receipts_path()):
            line = line.strip()
            if not line:
                continue
            try:
                rc = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rc.get("song") == song_name:
                out.append(rc)
    except FileNotFoundError:
        pass
    return out

def clear_receipts(song_name=None):
    """song_name given: drop only THAT song's receipts (other live proposals
    keep their ledgers — a fresh ask on song B must not orphan song A's
    cumulative receipts). None = legacy full wipe. THE PROPOSAL-LIFETIME LAW
    (2026-07-11): receipts live as long as the proposal — a REVISE re-enters
    an existing prop carrying prior runs' edits, so revise paths never clear."""
    try:
        if song_name is None:
            os.remove(receipts_path())
            return
        path = receipts_path()
        keep = []
        for line in open(path):
            try:
                if json.loads(line).get("song") == song_name:
                    continue
            except (json.JSONDecodeError, AttributeError):
                pass
            keep.append(line if line.endswith("\n") else line + "\n")
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            f.writelines(keep)
        os.replace(tmp, path)
    except FileNotFoundError:
        pass

# ---------------------------------------------------------------- diff + law
_META_KEYS = ("bpm", "key", "lengthBars", "masterGainDb", "swing", "tempoMap", "sections",
               "scenes", "lyrics")
_TRACK_PROPS = ("gainDb", "pan", "muted", "locked")
_TRACK_KNOWN = ("name", "notes", "fx", "sends", "source", "automation", "audioClips",
                "instrument") + _TRACK_PROPS
_SONG_KNOWN = ("version", "tracks", "buses", "master", "automation") + _META_KEYS

def _note_multiset(track):
    from collections import Counter
    return Counter((round(float(n["start"]), NOTE_KEY_DP), int(n["pitch"]),
                    round(float(n.get("vel", 0.8)), 3), round(float(n.get("len", 0.25)), 3))
                   for n in track.get("notes", []) or [])

def _canon(x):
    """W119: numeric-identity canonicalization — a float->int JSON round-trip
    (180.0 -> 180, 0.0 -> 0) is NOT a change. Chezy's live run drowned in
    2180 false OUT-OF-SCOPE flags after a tool re-serialized the song and
    numerics re-typed. bool stays bool (it is an int subclass)."""
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, list):
        return [_canon(v) for v in x]
    if isinstance(x, dict):
        return {k: _canon(v) for k, v in x.items()}
    return x


def _jeq(a, b):
    return json.dumps(_canon(a), sort_keys=True) == json.dumps(_canon(b), sort_keys=True)


def semantic_diff(a, b):
    """Entity-level diff of two song dicts. Every entry is addressable by the LAW."""
    d = {"meta": {}, "master": None, "buses": {"added": [], "removed": [], "changed": []},
         "tracks": {"added": [], "removed": [], "changed": {}}}
    extra = (set(a) | set(b)) - set(_SONG_KNOWN)
    for k in tuple(_META_KEYS) + tuple(sorted(extra)):   # catch-all: NOTHING changes invisibly
        if not _jeq(a.get(k), b.get(k)):
            d["meta"][k] = [a.get(k), b.get(k)]
    if not _jeq(a.get("master"), b.get("master")):
        d["master"] = {"before": [m.get("id") or m.get("type") for m in a.get("master") or []],
                       "after": [m.get("id") or m.get("type") for m in b.get("master") or []]}
    if not _jeq(a.get("automation"), b.get("automation")):
        d["meta"]["automation"] = [[x.get("target") for x in a.get("automation") or []],
                                   [x.get("target") for x in b.get("automation") or []]]
    ab = {bs.get("id"): bs for bs in a.get("buses") or []}
    bb = {bs.get("id"): bs for bs in b.get("buses") or []}
    d["buses"]["added"] = sorted(set(bb) - set(ab))
    d["buses"]["removed"] = sorted(set(ab) - set(bb))
    d["buses"]["changed"] = sorted(k for k in set(ab) & set(bb)
                                   if not _jeq(ab[k], bb[k]))
    at = {t.get("name", f"#{i}"): t for i, t in enumerate(a.get("tracks") or [])}
    bt = {t.get("name", f"#{i}"): t for i, t in enumerate(b.get("tracks") or [])}
    d["tracks"]["added"] = sorted(set(bt) - set(at))
    d["tracks"]["removed"] = sorted(set(at) - set(bt))
    for nm in sorted(set(at) & set(bt)):
        ta, tb = at[nm], bt[nm]
        ch = {}
        props = {}
        for k in _TRACK_PROPS:
            if not _jeq(ta.get(k), tb.get(k)):
                props[k] = [ta.get(k), tb.get(k)]
        if props:
            ch["props"] = props
        t_extra = (set(ta) | set(tb)) - set(_TRACK_KNOWN)
        for k in ("fx", "sends", "source", "automation", "audioClips") + tuple(sorted(t_extra)):
            if not _jeq(ta.get(k), tb.get(k)):
                ch[k] = True
        ma, mb = _note_multiset(ta), _note_multiset(tb)
        removed = list((ma - mb).elements())
        added = list((mb - ma).elements())
        rem_by_key = {}
        for e in removed:
            rem_by_key.setdefault((e[0], e[1]), []).append(e)
        changed = []
        pure_added = []
        for e in added:
            k = (e[0], e[1])
            if rem_by_key.get(k):
                old = rem_by_key[k].pop(0)
                changed.append({"start": e[0], "pitch": e[1],
                                "vel": [old[2], e[2]] if old[2] != e[2] else None,
                                "len": [old[3], e[3]] if old[3] != e[3] else None})
            else:
                pure_added.append(e)
        pure_removed = [e for lst in rem_by_key.values() for e in lst]
        if pure_added or pure_removed or changed:
            ch["notes"] = {"added": [[nm, e[0], e[1]] for e in pure_added],
                           "removed": [[nm, e[0], e[1]] for e in pure_removed],
                           "changed": [[nm, c["start"], c["pitch"]] for c in changed],
                           "detail": {"n_added": len(pure_added), "n_removed": len(pure_removed),
                                      "n_changed": len(changed)}}
        if ch:
            d["tracks"]["changed"][nm] = ch
    return d

def diff_is_empty(d):
    return (not d["meta"] and not d["master"] and not any(d["buses"].values())
            and not d["tracks"]["added"] and not d["tracks"]["removed"]
            and not d["tracks"]["changed"])

def containment(diff, receipts):
    """THE SCOPE LAW: every diff entry must be explained by a receipt.
    -> {clean, explained[], out_of_scope[], summary}"""
    touched = set()
    wild_tracks = set()
    fields = set()
    for rc in receipts:
        for k in rc.get("removed_keys", []) + rc.get("added_keys", []):
            touched.add((str(k[0]), round(float(k[1]), NOTE_KEY_DP), int(k[2])))
        # coerce: pre-2026-07-11 ledgers hold one track_wild=True (bool) line —
        # set(True) raises and a poisoned line must never kill the whole check
        tw = rc.get("track_wild", [])
        wild_tracks |= set(tw if isinstance(tw, (list, tuple, set)) else [])
        fl = rc.get("fields", [])
        fields |= set(fl if isinstance(fl, (list, tuple, set)) else [])
        fields |= set(rc.get("prop_changes", []) or [])
        for tn in (rc.get("scope", {}) or {}).get("tracks", []):
            fields.add(f"track:{tn}:notes")     # a surgical edit may reorder-only (no key change)
    full_write = "*" in fields
    explained, out_of = [], []
    def judge(entry, ok):
        (explained if ok else out_of).append(entry)
    for k, ab in diff["meta"].items():
        # both spellings cover (W115 generalized 2026-07-11: auto_master files
        # bare "masterGainDb" — meta keys are namespaced by construction, so a
        # bare key in fields can only mean that meta key)
        judge(f"meta:{k} {json.dumps(ab[0])[:40]} -> {json.dumps(ab[1])[:40]}",
              full_write or f"meta:{k}" in fields or k in fields)
    if diff["master"]:
        # W115: update_song_meta files "meta:master" — both spellings cover
        # (the literal-"master"-only match flagged every legitimate master
        # edit OUT OF SCOPE on Chezy's live take, 2026-07-11)
        judge(f"master chain {diff['master']['before']} -> {diff['master']['after']}",
              full_write or "master" in fields or "meta:master" in fields)
    for verb in ("added", "removed", "changed"):
        for nm in diff["buses"][verb]:
            judge(f"bus:{nm} {verb}", full_write or f"bus:{nm}" in fields or "buses" in fields)
    for nm in diff["tracks"]["added"]:
        judge(f"track:{nm} ADDED", full_write or f"track:{nm}" in fields or nm in wild_tracks)
    for nm in diff["tracks"]["removed"]:
        judge(f"track:{nm} REMOVED", full_write or f"track:{nm}" in fields or nm in wild_tracks)
    for nm, ch in diff["tracks"]["changed"].items():
        # bare "track:{nm}" authorizes the whole track's PROPERTIES (several
        # tools file that spelling; W115-class generalization 2026-07-11).
        # Notes stay exact-key/wild — the scalpel's precision core.
        for k, ab in (ch.get("props") or {}).items():
            judge(f"track:{nm} {k} {ab[0]} -> {ab[1]}",
                  full_write or f"track:{nm}:{k}" in fields
                  or f"track:{nm}" in fields or nm in wild_tracks)
        for k in ch:
            if k in ("props", "notes"):
                continue
            judge(f"track:{nm} {k} changed",
                  full_write or f"track:{nm}:{k}" in fields
                  or f"track:{nm}" in fields or nm in wild_tracks)
        nd = ch.get("notes")
        if nd:
            for kind in ("added", "removed", "changed"):
                for key in nd[kind]:
                    kk = (str(key[0]), round(float(key[1]), NOTE_KEY_DP), int(key[2]))
                    judge(f"note {kind[:-1] if kind != 'changed' else 'changed'} "
                          f"{key[0]} @{key[1]:g} {pitch_name(key[2])}",
                          full_write or kk in touched or key[0] in wild_tracks)
    n_out = len(out_of)
    summary = ("SURGICAL: every change is receipted." if n_out == 0 else
               f"OUT OF SCOPE: {n_out} unreceipted change(s) — " + "; ".join(out_of[:5])
               + ("…" if n_out > 5 else ""))
    if full_write and n_out == 0:
        summary = "FULL WRITE receipted (write_song/macro) — not a surgical proposal."
    return {"clean": n_out == 0, "full_write": full_write, "explained": explained,
            "out_of_scope": out_of, "summary": summary}

def scope_report(base_song, prop_song, receipts):
    """One call for the sidecar: diff + law + human line."""
    d = semantic_diff(base_song, prop_song)
    if diff_is_empty(d):
        return {"clean": True, "empty": True, "summary": "proposal is identical to base",
                "receipts": [r.get("summary", r.get("tool", "?")) for r in receipts],
                "out_of_scope": []}
    law = containment(d, receipts)
    n_notes = sum((ch.get("notes", {}).get("detail", {}).get("n_added", 0)
                   + ch.get("notes", {}).get("detail", {}).get("n_removed", 0)
                   + ch.get("notes", {}).get("detail", {}).get("n_changed", 0))
                  for ch in d["tracks"]["changed"].values())
    law.update({"empty": False,
                "touched_tracks": sorted(set(list(d["tracks"]["changed"]) + d["tracks"]["added"]
                                             + d["tracks"]["removed"])),
                "note_changes": n_notes,
                "receipts": [r.get("summary", r.get("tool", "?")) for r in receipts]})
    return law
