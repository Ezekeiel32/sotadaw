#!/usr/bin/env python3
"""THE PARSE LANE — typed scalpel asks compiled to the exact kernels. Zero tokens.

ZPE_TRANSFER_ROADMAP.md T1 (§4): a deterministic CANONICAL PARSE of the typed ask,
compiled into the machinery that already exists and is battery-proven — surgical.py
selectors + apply_ops, track fields, song meta, the verb bus registry — with HONEST
MISS to the cloud rail. The prompt bar is a typed, turn-delimited, bounded-domain
channel: exactly the regime where canonical parsing beats generative routing (ZPE
rungs A-C), feeding only links that are individually proven.

THE POLARITY LAW (QTAG, 0.986 with zero false positives): precision first.
A false compile costs trust; a miss costs nothing (the cloud rail exists).
Concretely:
  - a pattern must FULLMATCH the normalized ask — trailing clauses kill the parse;
  - every content word of a track phrase must be EVIDENCED by the winning track
    (tokens/role/adjective/substring), or the parse misses — loose captures are
    safe because unconsumed words are fatal;
  - ambiguity (two candidate tracks inside the score margin, two sections with the
    same name and no ordinal, a chord needing two different diatonic deltas,
    pitch running off 0..127, a missing song key) => MISS, never a guess;
  - every non-verb plan is PROBED against a scratch copy at compile time: it must
    apply cleanly AND change the song (the no-op honesty law) or it misses.

THE SAFETY INVARIANT: a parsed edit lands as an ORDINARY PROPOSAL — ghost diff,
receipts (surgical exact-key / coarse-field grammar), scope law, locks, audition,
git Time Machine. The worst parse error is a proposal the user rejects in seconds.

Wiring (T1-R3, sidecar handle() prompt branch, behind SOTADAW_PARSE, coordinate
with the sidecar lane owner first):
    plan = parse_lane.compile(text, song_doc, context)
    if plan is None: fall through to real_propose byte-identically
    verb actions  -> the existing handle_verb execution path
    other actions -> copy base to _prop_, surgical.clear_receipts(),
                     parse_lane.apply_plan(prop_doc, plan, song_name=prop_name),
                     save, enforce_locks, scope_check, INSTANT proposal event
                     (emit "[parse] "+plan["summary"] activity; parsed:true).

Deps: stdlib + surgical.py only. Battery: tools/parse_battery.py (bars: 100%%
precision, honest coverage, compile <50ms).
"""
import copy, os, re, sys, time

try:
    import surgical
except ImportError:                                    # imported from tools/ etc.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import surgical


class Miss(Exception):
    """A refusal to parse. .reason is a short machine tag for telemetry."""
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


# ---------------------------------------------------------------- normalize
_POLITE_LEAD = re.compile(r"^(?:please |pls |hey |yo |ok |okay |now |just |can you |"
                          r"could you |would you |go ahead and )+")
_POLITE_TAIL = re.compile(r"(?:,? ?(?:please|pls|thanks|thank you|ty))+$")

def normalize(text):
    s = str(text or "").strip().lower()
    s = re.sub(r"[.!?]+$", "", s).strip()
    s = re.sub(r"[’']", "", s)
    s = re.sub(r"\s+", " ", s)
    s = _POLITE_LEAD.sub("", s)
    s = _POLITE_TAIL.sub("", s).strip()
    s = re.sub(r"(-?\d+(?:\.\d+)?) ?db\b", r"\1db", s)      # "3 db" -> "3db"
    return s


# ---------------------------------------------------------------- amounts
_SMALL = r"(?:slightly|subtly|gently|a (?:little|bit|touch|tad|hair))"
_BIG = r"(?:a lot|way|much|really|heavily)"
_GRID = {"8th": 0.5, "eighth": 0.5, "16th": 0.25, "sixteenth": 0.25,
         "32nd": 0.125, "64th": 0.0625, "quarter": 1.0}
_ORDINAL = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3,
            "fourth": 4, "4th": 4, "last": -1}
_WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}

def _num(tok):
    tok = str(tok).strip()
    return int(tok) if tok.isdigit() else _WORDNUM.get(tok)

def _interval_delta(iv):
    """'an octave'|'2 octaves'|'a semitone'|'two semitones'|'a tone'|'3' -> semis."""
    if "octave" in iv:
        n = re.match(r"(\d+|" + "|".join(_WORDNUM) + r")", iv)
        return 12 * ((_num(n.group(1)) or 1) if n else 1)
    if "tone" in iv and "semitone" not in iv:
        return 2
    n = re.match(r"(\d+|" + "|".join(_WORDNUM) + r")", iv)
    if not n or _num(n.group(1)) is None:
        raise Miss(f"interval:{iv}")
    return _num(n.group(1))
_DEGREES = {"second": 1, "third": 2, "fourth": 3, "fifth": 4, "sixth": 5, "seventh": 6}

def _size(amt_text):
    """None|'a little '|'much ' -> 'small'|'big'|'default'."""
    t = (amt_text or "").strip()
    if not t:
        return "default"
    if re.fullmatch(_SMALL, t):
        return "small"
    if re.fullmatch(_BIG, t):
        return "big"
    return "default"


# ---------------------------------------------------------------- key math
_MODE_IV = {"major": (0, 2, 4, 5, 7, 9, 11), "minor": (0, 2, 3, 5, 7, 8, 10)}

def parse_key(key):
    """'F minor'|'Fm'|'c# maj' -> (root_pc, scale_pcs sorted) or None."""
    m = re.fullmatch(r"([a-g][#b♯♭]?)\s*(major|minor|maj|min|m)?",
                     str(key or "").strip().lower())
    if not m:
        return None
    root = surgical.parse_pitch_class(m.group(1))
    if root is None:
        return None
    mode = {"maj": "major", "min": "minor", "m": "minor", None: "major"}.get(
        m.group(2), m.group(2))
    return root, sorted((root + i) % 12 for i in _MODE_IV[mode])

def diatonic_shift(pitch, key, steps):
    """Semitone delta moving `steps` scale degrees from pitch inside key.
    Miss if the pitch class is not in the scale (never guess chromatically)."""
    _, scale = key
    pc = int(pitch) % 12
    if pc not in scale:
        raise Miss(f"pitch_not_in_key:{surgical.pitch_name(pitch)}")
    octs, j = divmod(scale.index(pc) + int(steps), len(scale))
    return (scale[j] - pc) + 12 * octs


# ---------------------------------------------------------------- resolvers
_STOP = {"the", "a", "an", "that", "this", "sound", "at", "in", "on", "of",
         "one", "track", "it", "its"}

_RESOLUTIONS = None    # per-compile collector; compile() is single-threaded by law
_HISTORY = None        # per-compile history channel ({"last_plan": ...} or None)
_CTX = None            # per-compile UI context ({"selections": [...]}) — SELECTION =
                       # CONTEXT reaches the instant lane too (2026-08-08 rung)

def _record_resolution(key, name):
    """Non-trivial phrase->track links (key != the track's own name) are the
    facts an ACCEPT later confirms into the session store (T2 refers_to)."""
    if _RESOLUTIONS is not None and key and key != str(name).lower():
        _RESOLUTIONS[key] = str(name)

# SELECTION = CONTEXT, instant-lane edition (2026-08-08; live evidence: 'make it
# quieter' x3 + 'make it darker' missed as track_empty:it while the UI was
# pointing at a track). Pronouns resolve through the UI's pointing hand — never
# recorded as sticky aliases (deictic words must stay deictic).
_PRONOUNS = {"it", "this", "that", "this one", "this track", "that track",
             "the selected track", "selected track", "the selection", "selection"}
_SONG_WIDE = {"everything", "song", "whole song", "mix", "whole mix",
              "whole thing", "all tracks", "every track"}

def _selected_track_names(song):
    """Track names the UI selection points at (notes/tracks/slot/track-fx
    selections name their track). -> (sorted unique names, name->index map)."""
    names = []
    for s in ((_CTX or {}).get("selections") or []):
        if not isinstance(s, dict):
            continue
        k = s.get("type")
        if k == "notes" and s.get("track"):
            names.append(str(s["track"]))
        elif k == "tracks":
            names.extend(str(n) for n in (s.get("names") or []) if n)
        elif k == "slot" and s.get("track"):
            names.append(str(s["track"]))
        elif k == "fx" and s.get("scope", "track") == "track" and s.get("owner"):
            names.append(str(s["owner"]))
    have = {str(t.get("name", f"#{i}")): i
            for i, t in enumerate(song.get("tracks", []))}
    return sorted({n for n in names if n in have}), have

def _pronoun_track(song, p):
    """'it'/'this' -> the ONE selected track, or an honest Miss (no guessing)."""
    uniq, have = _selected_track_names(song)
    if not uniq:
        raise Miss(f"pronoun_no_selection:{p}")
    if len(uniq) > 1:
        raise Miss(f"pronoun_multi_selection:{p}")
    return have[uniq[0]], f"'{p}' = the selected track '{uniq[0]}'"

def _song_wide_phrase(song, phrase):
    """'everything'/'the mix' as a SONG-scope idiom — unless a real track owns
    that exact name (the artifact outranks the idiom)."""
    p = re.sub(r"^(?:the |our |my )", "", str(phrase or "").strip().lower()).strip()
    if p not in _SONG_WIDE:
        return False
    return p not in {str(t.get("name", "")).strip().lower()
                     for t in song.get("tracks", [])}

def _word_hits(track, word, role):
    toks = surgical._track_tokens(track)
    if word in toks or word == role:
        return True
    if word in surgical.ADJECTIVES and set(surgical.ADJECTIVES[word]) & toks:
        return True
    if len(word) > 2 and any(word in tk for tk in toks):
        return True
    if len(word) > 3 and word.endswith("s"):
        return _word_hits(track, word[:-1], role)
    return False

def resolve_track_phrase(song, phrase, facts=None):
    """Free phrase -> exactly ONE track index, or Miss.
    Order: T2 alias facts > exact name > unique substring name > scored with a
    margin — and EVERY content word must be evidenced by the winner."""
    phrase = str(phrase).strip()
    if facts:
        for cand in (phrase, re.sub(r"^the ", "", phrase)):
            if cand in facts:
                phrase = str(facts[cand])
                break
    p = phrase.strip().lower()
    if p in _PRONOUNS and p not in {str(t.get("name", "")).strip().lower()
                                    for t in song.get("tracks", [])}:
        return _pronoun_track(song, p)     # the pointing hand (never a sticky alias)
    words = [w for w in re.split(r"[^a-z0-9#]+", phrase.lower())
             if w and w not in _STOP]
    if not words:
        raise Miss(f"track_empty:{phrase}")
    tracks = song.get("tracks", [])
    names = [str(t.get("name", f"#{i}")) for i, t in enumerate(tracks)]
    joined = " ".join(words)
    exact = [i for i, n in enumerate(names) if n.lower() == joined]
    if len(exact) == 1:
        return exact[0], f"'{joined}' = track name"
    sub = [i for i, n in enumerate(names) if joined in n.lower()]
    if len(sub) == 1:
        _record_resolution(joined, names[sub[0]])
        return sub[0], f"'{joined}' in '{names[sub[0]]}'"
    ranked = surgical.score_track_query(song, joined)
    if not ranked:
        raise Miss(f"track_unresolved:{phrase}")
    if len(ranked) > 1 and ranked[0][0] < ranked[1][0] + 1.5:
        raise Miss(f"track_ambiguous:{names[ranked[0][1]]}|{names[ranked[1][1]]}")
    ti = ranked[0][1]
    role = surgical.track_role(tracks[ti])[0]
    if not all(_word_hits(tracks[ti], w, role) for w in words):
        raise Miss(f"track_words_unconsumed:{phrase}")
    _record_resolution(joined, names[ti])
    return ti, f"'{phrase}' -> '{names[ti]}' ({ranked[0][2]})"

def resolve_track_list(song, list_text, facts=None):
    """'the bass and the pad' / 'kick, hats and snare' -> [(idx, name)], all-or-miss."""
    out, seen = [], set()
    for part in re.split(r",| and ", str(list_text)):
        part = part.strip()
        if not part:
            continue
        ti, _ = resolve_track_phrase(song, part, facts)
        if ti not in seen:
            seen.add(ti)
            out.append((ti, str(song["tracks"][ti].get("name", f"#{ti}"))))
    if not out:
        raise Miss(f"track_list_empty:{list_text}")
    return out

def resolve_section_phrase(song, phrase):
    """'verse' | 'second verse' | 'last chorus' -> (name, b0, b1) or Miss.
    Two same-named sections with no ordinal = ambiguous = Miss."""
    words = str(phrase or "").strip().lower().split()
    occ = 0
    if words and words[0] in _ORDINAL:
        occ = _ORDINAL[words[0]]
        words = words[1:]
    name = " ".join(w for w in words if w not in ("the",))
    if not name:
        raise Miss("section_empty")
    spans = surgical.section_spans(song)
    hits = [sp for sp in spans if sp[0].strip().lower() == name] or \
           [sp for sp in spans if name in sp[0].strip().lower()]
    if not hits:
        raise Miss(f"section_unresolved:{phrase}")
    if occ == 0:
        if len(hits) > 1:
            raise Miss(f"section_ambiguous:{phrase}")
        return hits[0]
    try:
        return hits[occ - 1 if occ > 0 else occ]
    except IndexError:
        raise Miss(f"section_occurrence:{phrase}")

def _resolved_notes(song, selector):
    """Compile-time dry-run of a selector. Miss on errors or an empty match."""
    try:
        r = surgical.resolve(song, selector)
    except ValueError as e:
        raise Miss(f"selector:{e}")
    if not r.refs:
        raise Miss("empty_match")
    return r

def _pitch_bounds(refs, delta):
    for _, n in refs:
        p = int(n["pitch"]) + int(delta)
        if not 0 <= p <= 127:
            raise Miss(f"pitch_out_of_range:{p}")


# ---------------------------------------------------------------- builders
# Each builder: (match, song, ctx, facts) -> (actions, summary, explain).
# Actions:
#   {"kind":"track_field","track":nm,"field":f,"mode":"set"|"add","value":v}
#   {"kind":"meta_field","key":k,"value":v}
#   {"kind":"track_fx_add","track":nm,"fx":{"id":...}}
#   {"kind":"surgical","selector":sel,"ops":[...]}   (op "__double__" is lowered
#                                                     by apply_plan at execute)
#   {"kind":"verb","verb":v,"args":{...}}            (execute via the verb bus)

def _tname(song, ti):
    return str(song["tracks"][ti].get("name", f"#{ti}"))

def b_mute(m, song, ctx, facts):
    want = m.group("un") is None
    if _song_wide_phrase(song, m.group("list")):   # 'mute everything' = every lane
        got = [(i, _tname(song, i)) for i in range(len(song.get("tracks", [])))]
        if not got:
            raise Miss("no_tracks")
    else:
        got = resolve_track_list(song, m.group("list"), facts)
    acts = [{"kind": "track_field", "track": nm, "field": "muted",
             "mode": "set", "value": want} for _, nm in got]
    names = " + ".join(nm for _, nm in got)
    return acts, f"{'mute' if want else 'unmute'} {names}", [f"tracks: {names}"]

def b_gain_or_scoped_vel(m, song, ctx, facts):
    g = m.groupdict()
    phrase = g.get("track") or g.get("trackb") or g.get("trackc") or g.get("trackd")
    # SONG SCOPE (2026-08-08): 'everything'/'the mix' — and a bare pronoun with
    # NOTHING selected ('make it quieter') — mean the whole mix, moved as ONE
    # fader (uniform per-track trim keeps every balance). A pronoun with one
    # selection targets it; 2+ selected = honest miss (no scope surprises).
    wide, ti, ev = _song_wide_phrase(song, phrase), None, ""
    if wide:
        ev = f"'{phrase}' = the whole mix"
    else:
        try:
            ti, ev = resolve_track_phrase(song, phrase, facts)
        except Miss as e:
            if not str(e.reason).startswith("pronoun_no_selection"):
                raise
            wide = True
            ev = f"'{phrase}' with nothing selected = the whole mix"
    nm = None if wide else _tname(song, ti)
    if g.get("half"):                       # "half as loud" / "twice as loud"
        up = "twice" in g["half"]
        db = 6.0                            # amplitude halving/doubling
    elif g.get("dir"):
        up = g["dir"] == "louder"
    elif g.get("ud"):
        up = g["ud"] == "up"
    else:
        up = g.get("rl") == "raise"
    db = None if not g.get("half") else db
    for k in ("db", "db2", "db3", "db4"):
        if g.get(k):
            db = float(g[k])
    size = _size(g.get("amt"))
    if db is None:
        db = {"small": 1.5, "default": 3.0, "big": 6.0}[size]
    sect = g.get("sect") or g.get("sectb")
    if sect:                                    # scoped => velocity, gain untouched
        sec = resolve_section_phrase(song, sect)
        sel = {"section": sec[0]} if wide else {"tracks": [nm], "section": sec[0]}
        r = _resolved_notes(song, sel)
        factor = round(10.0 ** ((db if up else -db) / 20.0), 4)
        who = "the whole mix" if wide else nm
        acts = [{"kind": "surgical", "selector": sel,
                 "ops": [{"op": "scale", "vel": factor}]}]
        return (acts, f"{who}: velocity x{factor:g} in '{sec[0]}' ({len(r.refs)} notes)",
                [ev, f"section '{sec[0]}' beats [{sec[1]:g},{sec[2]:g})"])
    delta = db if up else -db
    if wide:
        names = [_tname(song, i) for i in range(len(song.get("tracks", [])))]
        if not names:
            raise Miss("no_tracks")
        acts = [{"kind": "track_field", "track": n2, "field": "gainDb",
                 "mode": "add", "value": delta} for n2 in names]
        return (acts, f"the whole mix: gain {delta:+g} dB ({len(names)} tracks, "
                f"balance kept)", [ev])
    acts = [{"kind": "track_field", "track": nm, "field": "gainDb",
             "mode": "add", "value": delta}]
    return acts, f"{nm}: gain {delta:+g} dB", [ev]

def b_pan(m, song, ctx, facts):
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    amt = 0.9 if (m.group("amt") or "").strip() == "hard" else \
        {"small": 0.15, "default": 0.25, "big": 0.5}[_size(m.group("amt"))]
    delta = -amt if m.group("side") == "left" else amt
    acts = [{"kind": "track_field", "track": nm, "field": "pan",
             "mode": "add", "value": delta}]
    return acts, f"{nm}: pan {delta:+g}", [ev]

def b_delete_scope(m, song, ctx, facts):
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    sects = [m.group("sect")]
    if m.groupdict().get("sect2"):          # "in the intro and the outro"
        sects.append(m.group("sect2"))
    acts, names, total = [], [], 0
    for sp in sects:
        sec = resolve_section_phrase(song, sp)
        sel = {"tracks": [nm], "section": sec[0]}
        r = _resolved_notes(song, sel)
        total += len(r.refs)
        names.append(sec[0])
        acts.append({"kind": "surgical", "selector": sel, "ops": [{"op": "delete"}]})
    return (acts, f"{nm}: delete {total} notes in " + " + ".join(f"'{s}'" for s in names),
            [ev])

def b_transpose(m, song, ctx, facts):
    g = m.groupdict()
    ti, ev = resolve_track_phrase(song, g["track"], facts)
    nm = _tname(song, ti)
    delta = _interval_delta(g["iv"])
    d = g.get("dir")
    if not d:
        if g.get("tv") == "drop":
            d = "down"                     # 'drop X an octave' — the verb IS down
        else:
            raise Miss("no_direction")     # 'transpose X an octave' = which way?
    if d == "down":
        delta = -delta
    sel = {"tracks": [nm]}
    where = ""
    if g.get("sect"):
        sec = resolve_section_phrase(song, g["sect"])
        sel["section"] = sec[0]
        where = f" in '{sec[0]}'"
    r = _resolved_notes(song, sel)
    _pitch_bounds(r.refs, delta)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "shift", "pitch": delta}]}]
    return acts, f"{nm}: pitch {delta:+d} st{where} ({len(r.refs)} notes)", [ev]

def b_nth_fix(m, song, ctx, facts):
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    sel = {"tracks": [nm], "nth": int(m.group("n"))}
    r = _resolved_notes(song, sel)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "quantize", "grid": 0.25, "strength": 1.0}]}]
    return (acts, f"{nm}: snap hit #{m.group('n')} to the 16th grid",
            [ev, f"onset at beat {r.onsets()[0]:g}"])

def b_quantize(m, song, ctx, facts):
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    grid = _GRID.get(m.group("g") or "", 0.25)
    sel = {"tracks": [nm]}
    _resolved_notes(song, sel)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "quantize", "grid": grid, "strength": 1.0}]}]
    return acts, f"{nm}: quantize to {grid:g}-beat grid", [ev]

def b_humanize(m, song, ctx, facts):
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    tj, vj = {"small": (0.015, 0.04), "default": (0.02, 0.05),
              "big": (0.04, 0.09)}[_size(m.group("amt"))]
    sel = {"tracks": [nm]}
    _resolved_notes(song, sel)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "humanize", "timing": tj, "vel": vj}]}]
    return acts, f"{nm}: humanize +-{tj:g}b +-{vj:.0%}", [ev]

def b_staccato(m, song, ctx, facts):
    g = m.groupdict()
    ti, ev = resolve_track_phrase(song, g.get("track") or g.get("track2"), facts)
    nm = _tname(song, ti)
    sel = {"tracks": [nm]}
    _resolved_notes(song, sel)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "scale", "len": 0.5}]}]
    return acts, f"{nm}: note length x0.5 (staccato)", [ev]

def b_double(m, song, ctx, facts):
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    delta = 12 if m.group("dir") == "up" else -12
    vscale = 0.7 if m.group("q") else 0.85
    sel = {"tracks": [nm]}
    r = _resolved_notes(song, sel)
    _pitch_bounds(r.refs, delta)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "__double__", "pitch": delta, "vel_scale": vscale}]}]
    return (acts, f"{nm}: double {len(r.refs)} notes at {delta:+d} st, vel x{vscale:g}",
            [ev])

def b_ramp(m, song, ctx, facts):
    g = m.groupdict()
    ti, ev = resolve_track_phrase(song, g["track"], facts)
    nm = _tname(song, ti)
    s1 = resolve_section_phrase(song, g["s1"])
    b0, b1 = s1[1], s1[2]
    into = ""
    if g.get("s2"):
        s2 = resolve_section_phrase(song, g["s2"])
        if s2[1] <= b0:
            raise Miss("ramp_span_backwards")
        b1 = s2[1]                              # ramp lands AT the next section
        into = f" into '{s2[0]}'"
    rising = g["dir"] in ("rising", "up")
    va, vb = (0.4, 0.95) if rising else (0.9, 0.35)
    sel = {"tracks": [nm], "beats": [b0, b1]}
    r = _resolved_notes(song, sel)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "velocity_ramp", "from": va, "to": vb}]}]
    return (acts, f"{nm}: velocity ramp {va:g}->{vb:g} through '{s1[0]}'{into} "
            f"({len(r.refs)} notes)", [ev])

def b_every_other(m, song, ctx, facts):
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    step = {"other": 2, "second": 2, "2nd": 2, "third": 3, "3rd": 3,
            "fourth": 4, "4th": 4}[m.group("step")]
    sel = {"tracks": [nm], "every": {"step": step, "phase": 1}}
    where = ""
    if m.group("sect"):
        sec = resolve_section_phrase(song, m.group("sect"))
        sel["section"] = sec[0]
        where = f" in '{sec[0]}'"
    r = _resolved_notes(song, sel)
    acts = [{"kind": "surgical", "selector": sel, "ops": [{"op": "delete"}]}]
    return acts, f"{nm}: delete every {step} onsets{where} ({len(r.refs)} notes)", [ev]

def b_last_note(m, song, ctx, facts):
    key = parse_key(song.get("key"))
    if key is None:
        raise Miss("needs_key")
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    steps = _DEGREES[m.group("iv")]
    if m.group("dir") == "down":
        steps = -steps
    sel = {"tracks": [nm], "nth": -1}
    r = _resolved_notes(song, sel)
    deltas = {diatonic_shift(int(n["pitch"]), key, steps) for _, n in r.refs}
    if len(deltas) != 1:
        raise Miss("mixed_diatonic_delta")
    delta = deltas.pop()
    _pitch_bounds(r.refs, delta)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "shift", "pitch": delta}]}]
    return (acts, f"{nm}: last note {delta:+d} st (a {m.group('iv')} in "
            f"{song.get('key')})", [ev])

def b_strip(m, song, ctx, facts):
    sec = resolve_section_phrase(song, m.group("sect"))
    keeps = {nm for _, nm in resolve_track_list(song, m.group("list"), facts)}
    others = [str(t.get("name", f"#{i}")) for i, t in enumerate(song.get("tracks", []))
              if str(t.get("name", f"#{i}")) not in keeps]
    if not others:
        raise Miss("strip_nothing_to_remove")
    sel = {"tracks": others, "section": sec[0]}
    r = _resolved_notes(song, sel)
    acts = [{"kind": "surgical", "selector": sel, "ops": [{"op": "delete"}]}]
    return (acts, f"'{sec[0]}': strip to {' + '.join(sorted(keeps))} "
            f"(delete {len(r.refs)} notes on {' + '.join(others)})", [])

def b_add_fx(m, song, ctx, facts):
    fxmap = {"reverb": "fx_reverb", "verb": "fx_reverb", "delay": "fx_delay",
             "echo": "fx_delay", "saturation": "fx_saturate",
             "distortion": "fx_saturate", "drive": "fx_saturate",
             "width": "fx_widen", "widener": "fx_widen", "widening": "fx_widen"}
    fid = fxmap[m.group("fx")]
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    t = song["tracks"][ti]
    nm = _tname(song, ti)
    role = surgical.track_role(t)[0]
    if fid == "fx_widen" and role in ("kick", "bass"):
        raise Miss("widen_low_forbidden")       # the automix mono-below-120 law
    if any(f.get("id") == fid for f in t.get("fx") or []):
        raise Miss(f"already_has:{fid}")        # stacking is the cloud's call
    acts = [{"kind": "track_fx_add", "track": nm, "fx": {"id": fid}}]
    return acts, f"{nm}: add {fid}", [ev]

def b_color(m, song, ctx, facts):
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    word = {"warm": "warmer", "dark": "darker", "bright": "brighter",
            "wide": "wider"}.get(m.group("word"), m.group("word"))
    role = surgical.track_role(song["tracks"][ti])[0]
    if word == "wider" and role in ("kick", "bass"):
        raise Miss("widen_low_forbidden")
    amount = {"small": 0.3, "default": 0.5, "big": 0.8}[_size(m.group("amt"))]
    acts = [{"kind": "verb", "verb": "color",
             "args": {"word": word, "amount": amount, "track": nm}}]
    return acts, f"{nm}: color '{word}' {amount:g} (verb bus)", [ev]

def b_intensify(m, song, ctx, facts):
    g = m.groupdict()
    phrase = g.get("sect") or g.get("sect2") or g.get("sect3")
    sec = resolve_section_phrase(song, phrase)
    try:                                        # a track with the same name = ambiguous
        resolve_track_phrase(song, phrase, facts)
        raise Miss(f"track_section_clash:{phrase}")
    except Miss as e:
        if e.reason.startswith("track_section_clash"):
            raise
    amount = -0.5 if g.get("sect3") else 0.6
    acts = [{"kind": "verb", "verb": "intensify",
             "args": {"section": sec[0], "amount": amount}}]
    verb = "soften" if amount < 0 else "intensify"
    return acts, f"'{sec[0]}': {verb} {abs(amount):g} (verb bus)", []

def b_swing(m, song, ctx, facts):
    g = m.groupdict()
    phrase = g.get("track") or g.get("track2")
    ev = []
    if phrase and re.fullmatch(r"(?:the )?(?:groove|beat|song|mix|whole thing)",
                               phrase.strip()):
        phrase = None                      # global-swing idioms, not track refs
    if phrase:
        _, e = resolve_track_phrase(song, phrase, facts)
        ev.append(e)
    amount = {"small": 0.56, "default": 0.58, "big": 0.62}[_size(g.get("amt"))]
    acts = [{"kind": "meta_field", "key": "swing",
             "value": {"grid": "8th", "amount": amount}}]
    return acts, f"song swing 8th {amount:g} (engine swing is global)", ev

# ---- SOURCE SWAP (I1, docs/IMPROVEMENTS_2026_07_07.md): "swap the lead sound
# for an epiano" -> deterministic source replacement from the REAL inventory
# (instruments/*.dsp + kits/*/kit.json). Precision-first: exact id > exact kit >
# alias > component-set > word-subset > substring, each tier unique-or-Miss.
_VOICE_ALIASES = {          # only objectively-twin producer words — never taste
    "epiano": "rhodes", "e piano": "rhodes", "electric piano": "rhodes",
    "wurli": "rhodes", "wurlitzer": "rhodes", "rhodes piano": "rhodes",
    "el piano": "rhodes",
}
_NON_VOICES = {"master_limiter", "test_sine"}   # never fuzzy-resolved as a voice

def _voice_inventory():
    """(faust_ids, kit_names) from disk — the live truth, never a baked list."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    insts, kits = [], []
    try:
        insts = sorted(f[:-4] for f in os.listdir(os.path.join(root, "instruments"))
                       if f.endswith(".dsp") and not f.startswith("fx_"))
    except OSError:
        pass
    kdir = os.path.join(root, "kits")
    try:
        kits = sorted(d for d in os.listdir(kdir)
                      if os.path.exists(os.path.join(kdir, d, "kit.json")))
    except OSError:
        pass
    return insts, kits

def resolve_voice_phrase(song, phrase):
    """Sound phrase -> exactly ONE ("faust"|"sample", name) or Miss."""
    p = re.sub(r"^(?:a|an|the) ", "", str(phrase or "").strip().lower()).strip()
    if not p:
        raise Miss("voice_empty")
    p = _VOICE_ALIASES.get(p, p)
    tnames = {str(t.get("name", "")).strip().lower() for t in song.get("tracks", [])}
    if p in tnames:                        # "swap the bass for the sub" where 'sub'
        raise Miss(f"voice_is_track:{p}")  # is a TRACK = track-vs-sound ambiguity
    insts, kits = _voice_inventory()
    under = re.sub(r"[ -]+", "_", p)
    if under in insts:                     # an exact id is always reachable
        return ("faust", under), f"'{phrase}' = instrument {under}"
    if under in kits:
        return ("sample", under), f"'{phrase}' = kit {under}"
    words = set(under.split("_"))
    pool = ([("faust", i) for i in insts if i not in _NON_VOICES]
            + [("sample", k) for k in kits])
    for tier, hit in (("components", lambda n: set(n.split("_")) == words),
                      ("word_subset", lambda n: words <= set(n.split("_"))),
                      ("substring", lambda n: under in n)):
        cand = [(k, n) for k, n in pool if hit(n)]
        if len(cand) == 1:
            return cand[0], f"'{phrase}' -> {cand[0][1]} ({tier})"
        if len(cand) > 1:
            raise Miss("voice_ambiguous:" + "|".join(n for _, n in cand[:4]))
    raise Miss(f"voice_unresolved:{p}")

def b_source_swap(m, song, ctx, facts):
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    (kind, vid), vev = resolve_voice_phrase(song, m.group("voice"))
    cur = song["tracks"][ti].get("source") or {}
    if (cur.get("kind", "faust"), cur.get("id") or cur.get("kit")) == (kind, vid):
        raise Miss(f"voice_already:{vid}")
    src = {"kind": kind, ("kit" if kind == "sample" else "id"): vid}
    acts = [{"kind": "track_source", "track": nm, "source": src}]
    return (acts, f"{nm}: sound -> {vid} ({'kit' if kind == 'sample' else 'faust'})",
            [ev, vev])

def b_retarget(m, song, ctx, facts):
    """'do that to the X (too)' — deterministic RETARGET of the stored last
    parse hit: every reference to its primary track swaps to the new one, every
    law guard re-runs. Anything the swap can't PROVE misses to the cloud."""
    hp = (_HISTORY or {}).get("last_plan")
    if not hp:
        raise Miss("no_history")
    old = hp.get("track")
    if not old:
        raise Miss("not_retargetable")      # multi-track/section/meta last plan
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    new = _tname(song, ti)
    if new == old:
        raise Miss("same_target")
    role = surgical.track_role(song["tracks"][ti])[0]
    acts = copy.deepcopy(hp.get("actions") or [])
    if not acts:
        raise Miss("no_history_actions")
    for a in acts:
        k = a.get("kind")
        if k in ("track_field", "track_fx_add", "track_source"):
            if a.get("track") != old:
                raise Miss("not_retargetable")
            a["track"] = new
            if k == "track_fx_add" and (a.get("fx") or {}).get("id") == "fx_widen" \
                    and role in ("kick", "bass"):
                raise Miss("widen_low_forbidden")
        elif k == "surgical":
            sel = a.get("selector") or {}
            if sel.get("tracks") != [old]:
                raise Miss("not_retargetable")
            sel["tracks"] = [new]
            r = _resolved_notes(song, sel)  # fresh dry-run on the new target
            for op in a.get("ops") or []:
                if op.get("op") == "shift" and "pitch" in op:
                    _pitch_bounds(r.refs, op["pitch"])
        elif k == "verb":
            args = a.setdefault("args", {})
            if args.get("track") != old:
                raise Miss("not_retargetable")
            args["track"] = new
            if args.get("word") == "wider" and role in ("kick", "bass"):
                raise Miss("widen_low_forbidden")
        else:
            raise Miss("not_retargetable")
    return (acts, f"{new}: retarget of '{hp.get('ask', '?')}'",
            [ev, f"last hit was: {hp.get('summary', '?')}"])

def b_same_but(m, song, ctx, facts):
    """'same but wider' — the last hit's target, a different color word."""
    hp = (_HISTORY or {}).get("last_plan")
    if not hp:
        raise Miss("no_history")
    old = hp.get("track")
    if not old:
        raise Miss("not_retargetable")
    try:
        idxs, _ = surgical.resolve_tracks(song, old)
    except ValueError:
        raise Miss(f"track_unresolved:{old}")
    if len(idxs) != 1:
        raise Miss(f"track_ambiguous:{old}")
    word = {"warm": "warmer", "dark": "darker", "bright": "brighter",
            "wide": "wider"}.get(m.group("word"), m.group("word"))
    role = surgical.track_role(song["tracks"][idxs[0]])[0]
    if word == "wider" and role in ("kick", "bass"):
        raise Miss("widen_low_forbidden")
    acts = [{"kind": "verb", "verb": "color",
             "args": {"word": word, "amount": 0.5, "track": old}}]
    return acts, f"{old}: color '{word}' 0.5 (same target as last hit)", []

def b_history_q(m, song, ctx, facts):
    """'what did we change (on the X)?' -> the memory verb, zero tokens.
    Section-form questions ('...in the hook') deliberately DON'T match — they
    ride the cloud rail, which now carries the RECALL block."""
    args, ev = {}, []
    if m.groupdict().get("track"):
        ti, e = resolve_track_phrase(song, m.group("track"), facts)
        args["track"] = _tname(song, ti)
        ev.append(e)
    where = f" on {args['track']}" if args.get("track") else ""
    return ([{"kind": "verb", "verb": "memory", "args": args}],
            f"recall{where} (memory verb)", ev)

def b_nudge(m, song, ctx, facts):
    g = m.groupdict()
    ti, ev = resolve_track_phrase(song, g["track"], facts)
    nm = _tname(song, ti)
    amt = _GRID.get((g.get("amt") or "32nd").replace(" beat", ""), 0.125)
    later = g["dir"] in ("later", "forward")
    delta = amt if later else -amt
    sel = {"tracks": [nm]}
    r = _resolved_notes(song, sel)
    if not later and min(float(n["start"]) for _, n in r.refs) + delta < 0:
        raise Miss("nudge_before_zero")
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "shift", "start": delta}]}]
    return acts, f"{nm}: shift {delta:+g} beats ({len(r.refs)} notes)", [ev]


_MELODIC_ROLES = ("bass", "lead", "pad", "keys", "chords", "vocal")

def b_transpose_all(m, song, ctx, facts):
    """'transpose everything down two semitones' — THE DRUM EXEMPTION LAW:
    drums are trigger-pitches (which sound in the kit), not notes; a global
    transpose moves ONLY melodic-role tracks (suite-verified semantics)."""
    delta = _interval_delta(m.group("iv"))
    if m.group("dir") == "down":
        delta = -delta
    names = [str(t.get("name", f"#{i}")) for i, t in enumerate(song.get("tracks", []))
             if surgical.track_role(t)[0] in _MELODIC_ROLES and t.get("notes")]
    if not names:
        raise Miss("no_melodic_tracks")
    sel = {"tracks": names}
    r = _resolved_notes(song, sel)
    _pitch_bounds(r.refs, delta)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "shift", "pitch": delta}]}]
    return (acts, f"melodic tracks ({' + '.join(names)}): pitch {delta:+d} st "
            f"(drums exempt — trigger-pitch law)", [])

def b_except_gain(m, song, ctx, facts):
    """'make everything except the bass quieter by 3 db' — negation scope."""
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    keep = _tname(song, ti)
    db = float(m.group("db")) if m.group("db") else 3.0
    if m.group("dir") == "quieter" or m.group("dir") == "softer":
        db = -db
    others = [str(t.get("name", f"#{i}")) for i, t in enumerate(song.get("tracks", []))
              if str(t.get("name", f"#{i}")) != keep]
    if not others:
        raise Miss("nothing_but_the_exception")
    acts = [{"kind": "track_field", "track": nm, "field": "gainDb",
             "mode": "add", "value": db} for nm in others]
    return (acts, f"everything except {keep}: gain {db:+g} dB ({len(others)} tracks)",
            [ev])

def b_flatten(m, song, ctx, facts):
    """'flatten the kick velocities' — robotic = one canonical machine velocity."""
    ti, ev = resolve_track_phrase(song, m.groupdict().get("track")
                                  or m.group("track2"), facts)
    nm = _tname(song, ti)
    sel = {"tracks": [nm]}
    _resolved_notes(song, sel)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "set", "vel": 0.9}]}]
    return acts, f"{nm}: velocities flattened to 0.9 (robotic)", [ev]

def b_accent(m, song, ctx, facts):
    """'accent every fourth hat' — every Nth onset (phase 0 = downbeat-first)
    gets a velocity lift; the rest stay untouched (suite-verified shape)."""
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    step = {"other": 2, "second": 2, "2nd": 2, "third": 3, "3rd": 3,
            "fourth": 4, "4th": 4}[m.group("step")]
    sel = {"tracks": [nm], "every": {"step": step, "phase": 0}}
    r = _resolved_notes(song, sel)
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "shift", "vel": 0.12}]}]
    return acts, f"{nm}: accent every {step} onsets (+0.12 vel, {len(r.refs)} notes)", [ev]

def b_widen(m, song, ctx, facts):
    """'widen the pad (but keep the bass mono)' — the mono clause is a
    CONSTRAINT: compile only when it already holds (verify, never mutate)."""
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    t = song["tracks"][ti]
    if surgical.track_role(t)[0] in ("kick", "bass"):
        raise Miss("widen_low_forbidden")
    if any(f.get("id") == "fx_widen" for f in t.get("fx") or []):
        raise Miss("already_has:fx_widen")
    explain = [ev]
    if m.groupdict().get("track2"):
        ti2, ev2 = resolve_track_phrase(song, m.group("track2"), facts)
        t2 = song["tracks"][ti2]
        if any(f.get("id") == "fx_widen" for f in t2.get("fx") or []) \
                or abs(float(t2.get("pan") or 0.0)) >= 0.05:
            raise Miss("mono_constraint_violated")   # can't PROVE it -> cloud
        explain.append(f"constraint holds: {_tname(song, ti2)} is mono")
    acts = [{"kind": "track_fx_add", "track": nm,
             "fx": {"id": "fx_widen", "params": {"width": 1.35}}}]
    return acts, f"{nm}: add fx_widen (width 1.35)", explain

def b_after_bar(m, song, ctx, facts):
    """'delete everything after bar 12' — the suite PINNED the convention:
    after bar N (1-based, complete bars) = beats >= N*4."""
    n = int(m.group("n"))
    total = float(song.get("lengthBars", 4)) * 4.0
    if not 0 < n * 4.0 < total:
        raise Miss(f"bar_out_of_range:{n}")
    sel = {"beats": [n * 4.0, total]}
    r = _resolved_notes(song, sel)
    acts = [{"kind": "surgical", "selector": sel, "ops": [{"op": "delete"}]}]
    return (acts, f"delete everything after bar {n} ({len(r.refs)} notes, "
            f"beats {n * 4:g}+)", [])

def b_tempo(m, song, ctx, facts):
    bpm = float(m.group("bpm"))
    if not 40 <= bpm <= 300:
        raise Miss(f"bpm_out_of_range:{bpm:g}")
    acts = [{"kind": "meta_field", "key": "bpm", "value": bpm}]
    return acts, f"tempo -> {bpm:g} bpm", []

def b_remove_track(m, song, ctx, facts):
    """'delete the pad track entirely' — the word 'track' resolves the
    notes-vs-track ambiguity that keeps bare 'delete the X' on the cloud."""
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    acts = [{"kind": "remove_track", "track": nm}]
    return acts, f"remove track '{nm}' entirely", [ev]

def b_reverse(m, song, ctx, facts):
    """'reverse the last four lead notes' — retrograde: same rhythm, pitch
    order flipped. Compiles only when the tail is unambiguous (no chords)."""
    n = _num(m.group("n"))
    if not n or n < 2:
        raise Miss(f"count:{m.group('n')}")
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    notes = sorted(song["tracks"][ti].get("notes") or [],
                   key=lambda x: float(x["start"]))
    if len(notes) < n:
        raise Miss(f"only_{len(notes)}_notes")
    tail = notes[-n:]
    if len({round(float(x["start"]), 4) for x in tail}) != n:
        raise Miss("chord_in_tail")            # ambiguous retrograde -> cloud
    lo = float(tail[0]["start"])
    sel = {"tracks": [nm], "beats": [lo, float(tail[-1]["start"]) + 1e-4]}
    r = _resolved_notes(song, sel)
    if len(r.refs) != n:
        raise Miss("tail_window_ambiguous")
    acts = [{"kind": "surgical", "selector": sel, "ops": [{"op": "__reverse__"}]}]
    return acts, f"{nm}: reverse the last {n} notes (retrograde)", [ev]


def b_fade_in(m, song, ctx, facts):
    """'fade the pad in over the intro' — authored gainDb automation: silence
    at the span start rising to the track's own level at span end."""
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    if not m.groupdict().get("sect"):
        raise Miss("needs_span")           # 'fade X in' — over WHAT? -> cloud
    sec = resolve_section_phrase(song, m.group("sect"))
    t = song["tracks"][ti]
    if any("gain" in str(a.get("target", "")).lower()
           for a in t.get("automation") or []):
        raise Miss("already_has:gain_automation")
    base = float(t.get("gainDb") or 0.0)
    acts = [{"kind": "add_automation", "track": nm, "target": "gainDb",
             "points": [{"beat": sec[1], "v": -60.0, "curve": 0},
                        {"beat": sec[2], "v": base, "curve": 0}]}]
    return (acts, f"{nm}: fade in over '{sec[0]}' (-60 -> {base:g} dB)",
            [ev, f"section '{sec[0]}' beats [{sec[1]:g},{sec[2]:g})"])

def b_pan_travel(m, song, ctx, facts):
    """'make the hats travel left to right across each bar' — a per-bar pan
    zigzag authored as automation points (deterministic, engine-interpolated)."""
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    t = song["tracks"][ti]
    if any("pan" in str(a.get("target", "")).lower()
           for a in t.get("automation") or []):
        raise Miss("already_has:pan_automation")
    bars = int(float(song.get("lengthBars", 4)))
    if bars < 1:
        raise Miss("no_bars")
    pts = []
    for k in range(bars):
        pts.append({"beat": k * 4.0, "v": -0.5, "curve": 0})
        pts.append({"beat": k * 4.0 + 3.75, "v": 0.5, "curve": 0})
    acts = [{"kind": "add_automation", "track": nm, "target": "pan",
             "points": pts}]
    return acts, f"{nm}: pan travels L->R each bar ({bars} bars)", [ev]

def b_send_space(m, song, ctx, facts):
    """'give the lead some space with a send to a reverb bus' — the pro
    paradigm: find-or-create the reverb return, add a send (never an insert)."""
    g = m.groupdict()
    ti, ev = resolve_track_phrase(song, g.get("track") or g.get("track2")
                                  or g.get("track3"), facts)
    nm = _tname(song, ti)
    t = song["tracks"][ti]
    rev = [bu.get("id") for bu in song.get("buses") or []
           if "verb" in str(bu.get("id", "")).lower()
           or any("reverb" in str(f.get("id", "")) for f in bu.get("fx") or [])]
    if any(sn.get("bus") in rev for sn in t.get("sends") or []):
        raise Miss("already_sends_to_reverb")
    acts = [{"kind": "add_send", "track": nm, "bus_kind": "reverb"}]
    return acts, f"{nm}: send to the reverb bus (find-or-create 'verb')", [ev]

def b_double_time(m, song, ctx, facts):
    """'double-time the hats in the bar before the drop' — zone fill: one new
    onset midway between each existing pair (deterministic, no generation)."""
    ti, ev = resolve_track_phrase(song, m.group("track"), facts)
    nm = _tname(song, ti)
    sec = resolve_section_phrase(song, m.group("sect"))
    if sec[1] < 4.0:
        raise Miss("no_bar_before")
    sel = {"tracks": [nm], "beats": [sec[1] - 4.0, sec[1]]}
    r = _resolved_notes(song, sel)
    if len(r.onsets()) < 2:
        raise Miss("zone_too_sparse")
    acts = [{"kind": "surgical", "selector": sel,
             "ops": [{"op": "__double_time__"}]}]
    return (acts, f"{nm}: double-time the bar before '{sec[0]}' "
            f"({len(r.refs)} notes -> ~x2)", [ev])


# ---------------------------------------------------------------- registry
_ART = r"(?:the |our |my )?"
_TR = r"(?P<track>[a-z0-9#][a-z0-9# _-]*?)"
_SECT = r"(?P<sect>[a-z0-9][a-z0-9 _-]*?)"

PATTERNS = [(name, re.compile(rx), fn) for name, rx, fn in [
    ("retarget",
     r"^(?:do|apply) (?:that|the same|it) (?:to|on) " + _ART + _TR +
     r"(?: too| as well)?$", b_retarget),
    ("retarget2",
     r"^same (?:thing )?(?:for|on) " + _ART + _TR + r"(?: too| as well)?$",
     b_retarget),
    ("same_but",
     r"^(?:the )?same,? but (?P<word>warmer|warm|darker|dark|brighter|bright|"
     r"wider|wide)$", b_same_but),
    ("history_q",
     r"^what (?:did (?:we|you)|have we) (?:change|changed|do|done)"
     r"(?: (?:on|to) " + _ART + _TR + r")?(?: lately| recently| so far)?$",
     b_history_q),
    ("nth_fix",
     r"^the (?P<n>\d+)(?:st|nd|rd|th) " + _TR +
     r"(?: hit| note)? is (?:a (?:bit|little|touch) )?(?:late|early|off|out of time)"
     r"(?:,? ?(?:please )?fix ?(?:it|that)?)?$", b_nth_fix),
    ("last_note",
     r"^(?:pitch|take|move|shift) the last " + _TR +
     r" note (?P<dir>up|down) a (?P<iv>second|third|fourth|fifth|sixth|seventh)$",
     b_last_note),
    ("every_other",
     r"^(?:delete|remove|drop|kill|thin) every (?P<step>other|second|2nd|third|3rd|"
     r"fourth|4th) " + _TR + r"(?: hit| note)?"
     r"(?: (?:in|from|during) " + _ART + _SECT + r")?$", b_every_other),
    ("strip",
     r"^strip " + _ART + _SECT + r"(?: down)? to (?:just |only )?(?P<list>.+)$",
     b_strip),
    ("transpose_all",      # MUST precede transpose: its TR would eat "everything"
     r"^(?:transpose|shift|pitch|move|take|drop) (?:everything|all tracks|the whole song)"
     r" (?P<dir>up|down)(?: by)? (?P<iv>an octave|\d+ octaves?|a semitone|"
     r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
     r" semitones?|a (?:whole )?tone)$", b_transpose_all),
    ("except_gain",        # MUST precede gain: negation scope
     r"^make everything (?:except|but) " + _ART + _TR +
     r" (?P<dir>quieter|louder|softer)(?: by)?(?: (?P<db>\d+(?:\.\d+)?)db)?$",
     b_except_gain),
    ("after_bar",
     r"^(?:delete|remove|clear|cut|kill) everything after bar (?P<n>\d+)$",
     b_after_bar),
    ("remove_track",
     r"^(?:delete|remove|kill) " + _ART + _TR +
     r" track(?: entirely| completely| altogether)?$", b_remove_track),
    ("flatten",
     r"^(?:flatten " + _ART + _TR + r" velocit(?:ies|y)"
     r"(?:,? ?(?:make (?:it|them) )?robotic)?"
     r"|make " + _ART + r"(?P<track2>[a-z0-9#][a-z0-9# _-]*?) velocit(?:ies|y) "
     r"(?:uniform|flat|robotic))$", b_flatten),
    ("accent",
     r"^accent every (?P<step>other|second|2nd|third|3rd|fourth|4th) " + _TR +
     r"(?: hit| note)?$", b_accent),
    ("widen",
     r"^widen " + _ART + _TR +
     r"(?:,? but keep " + _ART + r"(?P<track2>[a-z0-9#][a-z0-9# _-]*?) mono)?$",
     b_widen),
    ("tempo",
     r"^(?:bump|set|change|take|move|push) (?:the )?(?:tempo|bpm)"
     r"(?: (?:to|at|up to))? (?P<bpm>\d{2,3})(?: ?bpm)?$", b_tempo),
    ("source_swap",      # AFTER tempo: "change the bpm to 128" must win tempo
     r"^(?:swap|switch|change|replace) (?:out )?" + _ART + _TR +
     r"(?: (?:sound|instrument|voice|patch))?"
     r" (?:to|for|with|into) (?:a |an |the )?(?P<voice>[a-z0-9 _-]+?)"
     r"(?: (?:sound|instrument|voice|patch|kit))?$", b_source_swap),
    ("fade_in",
     r"^fade " + _ART + _TR + r" in(?: (?:over|during|through) " + _ART + _SECT +
     r")?$", b_fade_in),
    ("pan_travel",
     r"^make " + _ART + _TR + r" travel left to right"
     r"(?: (?:across|over) (?:each|every) bar)?$", b_pan_travel),
    ("send_space",
     r"^(?:give " + _ART + _TR + r" some (?:space|room) with a "
     r"(?:send to a )?reverb (?:bus|send)"
     r"|(?:add|create) a reverb (?:bus )?send (?:to|for|on) " + _ART +
     r"(?P<track2>[a-z0-9#][a-z0-9# _-]*?)"
     r"|send " + _ART + r"(?P<track3>[a-z0-9#][a-z0-9# _-]*?)"
     r" to (?:a |the )?reverb(?: bus)?)$", b_send_space),
    ("double_time",
     r"^double[- ]?time " + _ART + _TR + r" in the bar before " + _ART + _SECT +
     r"$", b_double_time),
    ("reverse",
     r"^reverse the last (?P<n>\d+|two|three|four|five|six|seven|eight) " + _TR +
     r" notes$", b_reverse),
    ("ramp",
     r"^(?:velocity |vel )?ramp " + _ART + _TR +
     r" (?P<dir>rising|falling|up|down)(?: ?through| ?across| ?over) " + _ART +
     r"(?P<s1>[a-z0-9 _-]+?)(?: into " + _ART + r"(?P<s2>[a-z0-9 _-]+?))?$", b_ramp),
    ("double",
     r"^double " + _ART + _TR + r" (?:an |1 )?octave (?P<dir>up|down)"
     r"(?:,? ?(?P<q>quieter|softer|lower))?$", b_double),
    ("delete_scope",
     r"^(?:delete|remove|kill|clear|cut) " + _ART + _TR +
     r"(?: notes| hits)? (?:in|from|during|out of) " + _ART + _SECT +
     r"(?: and (?:the )?(?P<sect2>[a-z0-9][a-z0-9 _-]*?))?$",
     b_delete_scope),
    ("transpose",
     r"^(?P<tv>transpose|shift|pitch|move|take|drop) " + _ART + _TR +
     r"(?: (?P<dir>up|down))?(?: by)? (?P<iv>an octave|\d+ octaves?|a semitone|"
     r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
     r" semitones?|\d+ semis?|a (?:whole )?tone|\d+)"
     r"(?: in " + _ART + _SECT + r")?(?: only)?$", b_transpose),
    ("nudge",
     r"^(?:nudge|push) " + _ART + r"(?:whole )?" + _TR +
     r" ?(?:slightly |a (?:bit|little|touch) )?(?P<dir>later|earlier|forward|back(?:wards?)?)"
     r"(?:,? ?(?:about |around |like )?(?:a |an )?(?P<amt>64th|32nd|16th|8th|"
     r"quarter(?: beat)?))?$", b_nudge),
    ("quantize",
     r"^(?:quantize|snap) " + _ART + _TR + r"(?: (?:tight(?:ly|er)?|hard))?(?: to)?"
     r"(?: the)?(?: (?P<g>8th|16th|32nd|eighth|sixteenth|quarter)s?"
     r"(?: notes?| grid)?| grid)?$", b_quantize),
    ("humanize",
     r"^(?:humanize|loosen(?: up)?) " + _ART + _TR +
     r"(?P<amt> a (?:bit|little|touch)| slightly| a lot)?$", b_humanize),
    ("staccato",
     r"^(?:shorten " + _ART + _TR + r"(?: notes)?(?:, make them staccato)?"
     r"|make " + _ART + r"(?P<track2>[a-z0-9#][a-z0-9# _-]*?)(?: notes)? "
     r"(?:staccato|shorter))$", b_staccato),
    ("add_fx",
     r"^(?:add|put|throw|slap) (?:some |a (?:little |bit of |touch of |splash of )?)?"
     r"(?P<fx>reverb|verb|delay|echo|saturation|distortion|drive|width|widener|"
     r"widening) (?:to|on|onto|over) " + _ART + _TR + r"$", b_add_fx),
    ("pan",
     r"^pan " + _ART + _TR + r" (?P<amt>a (?:little|bit|touch) |slightly |hard )?"
     r"(?:to (?:the )?|towards (?:the )?)?(?P<side>left|right)$", b_pan),
    ("mute",
     r"^(?P<un>un)?(?:mute|silence) (?P<list>.+)$", b_mute),
    ("swing",
     r"^(?:swing " + _ART + _TR + r"|add (?:some |a (?:little|bit) of )?swing"
     r"(?: to " + _ART + r"(?P<track2>[a-z0-9#][a-z0-9# _-]*?))?)"
     r"(?P<amt> a (?:little|bit|touch)| slightly| hard| a lot)?$", b_swing),
    ("intensify",
     r"^(?:make " + _ART + _SECT + r" (?:hit |go |slap )?(?:harder|bigger|slap|"
     r"punchier|more intense)|intensify " + _ART + r"(?P<sect2>[a-z0-9 _-]+?)|"
     r"(?:soften|calm|chill) (?:out )?" + _ART + r"(?P<sect3>[a-z0-9 _-]+?)"
     r"(?: (?:down|out))?)$", b_intensify),
    ("color",
     r"^make " + _ART + _TR + r" (?P<amt>a (?:little|bit|touch) |slightly |much |"
     r"way )?(?P<word>warmer|warm|darker|dark|brighter|bright|wider|wide)$", b_color),
    ("gain",
     r"^(?:make " + _ART + r"(?P<trackd>[a-z0-9#][a-z0-9# _-]*?) "
     r"(?P<half>(?:about |around )?half as loud|twice as loud)"
     r"(?: in " + _ART + r"(?P<sectb>[a-z0-9][a-z0-9 _-]*?))?(?: only)?"
     r"|(?:make|turn) " + _ART + _TR + r" (?P<amt>(?P<db>-?\d+(?:\.\d+)?)db |"
     + _SMALL + r" |" + _BIG + r" )?(?P<dir>louder|quieter|softer)"
     r"(?: by (?P<db4>\d+(?:\.\d+)?)db)?"
     r"(?: in " + _ART + _SECT + r")?(?: only)?"
     r"|turn " + _ART + r"(?P<trackb>[a-z0-9#][a-z0-9# _-]*?) (?P<ud>up|down)"
     r"(?: by)?(?: (?P<db2>\d+(?:\.\d+)?)db)?"
     r"|(?P<rl>raise|lower) " + _ART + r"(?P<trackc>[a-z0-9#][a-z0-9# _-]*?)"
     r"(?: by)? (?P<db3>\d+(?:\.\d+)?)db)$", b_gain_or_scoped_vel),
]]


# ---------------------------------------------------------------- execute
def _lower_reverse(song, selector):
    """Retrograde: matched notes keep rhythm (start/len/vel), pitch ORDER flips.
    Lowered to a replace op so the receipt carries exact before/after keys."""
    r = surgical.resolve(song, selector)
    if not r.refs:
        raise Miss("empty_match")
    refs = sorted(r.refs, key=lambda tn: float(tn[1]["start"]))
    pitches = [int(n["pitch"]) for _, n in refs][::-1]
    notes = [{"start": float(n["start"]), "len": float(n.get("len", 0.25)),
              "pitch": pitches[i], "vel": float(n.get("vel", 0.8)),
              "track": str(song["tracks"][ti].get("name", f"#{ti}"))}
             for i, (ti, n) in enumerate(refs)]
    return [{"op": "replace", "notes": notes}]


def _lower_double_time(song, selector):
    """Zone fill: one new onset midway between each consecutive pair (the last
    note reuses the previous spacing). Deterministic — no generation."""
    r = surgical.resolve(song, selector)
    if not r.refs:
        raise Miss("empty_match")
    refs = sorted(r.refs, key=lambda tn: float(tn[1]["start"]))
    b0, b1 = r.range if r.range else (None, None)
    notes, prev_gap = [], None
    for i, (ti, n) in enumerate(refs):
        s = float(n["start"])
        gap = (float(refs[i + 1][1]["start"]) - s) if i + 1 < len(refs) else prev_gap
        if not gap or gap <= 0.02:
            continue
        prev_gap = gap
        mid = s + gap / 2.0
        if b1 is not None and not (b0 - 1e-6 <= mid < b1):
            continue                       # the fill stays inside the zone
        notes.append({"start": mid, "len": float(n.get("len", 0.25)),
                      "pitch": int(n["pitch"]), "vel": float(n.get("vel", 0.8)) * 0.9,
                      "track": str(song["tracks"][ti].get("name", f"#{ti}"))})
    if not notes:
        raise Miss("zone_too_sparse")
    return [{"op": "insert", "notes": notes}]


def _lower_double(song, selector, op):
    r = surgical.resolve(song, selector)
    if not r.refs:
        raise Miss("empty_match")
    delta, vs = int(op.get("pitch", 12)), float(op.get("vel_scale", 0.85))
    notes = []
    for ti, n in r.refs:
        p = int(n["pitch"]) + delta
        if not 0 <= p <= 127:
            raise Miss(f"pitch_out_of_range:{p}")
        notes.append({"start": float(n["start"]), "len": float(n.get("len", 0.25)),
                      "pitch": p, "vel": float(n.get("vel", 0.8)) * vs,
                      "track": str(song["tracks"][ti].get("name", f"#{ti}"))})
    return [{"op": "insert", "notes": notes}]

def apply_plan(song, plan, song_name=None):
    """Execute a compiled plan's non-verb actions against `song` IN PLACE.
    Files receipts under `song_name` (surgical receipts IO) when given; always
    returns the receipt dicts. Verb actions raise Miss('verb_action') — route
    those through the verb bus (sidecar handle_verb / registry subprocess)."""
    receipts = []
    fields = []
    wild = []
    for a in plan["actions"]:
        kind = a["kind"]
        if kind == "verb":
            raise Miss("verb_action")
        if kind == "remove_track":
            idxs, _ = surgical.resolve_tracks(song, a["track"])
            if len(idxs) != 1:
                raise Miss(f"track_field_ambiguous:{a['track']}")
            song["tracks"].pop(idxs[0])
            wild.append(a["track"])
            continue
        if kind == "surgical":
            ops = a["ops"]
            if any(o.get("op") == "__double__" for o in ops):
                ops = _lower_double(song, a["selector"],
                                    next(o for o in ops if o.get("op") == "__double__"))
            elif any(o.get("op") == "__reverse__" for o in ops):
                ops = _lower_reverse(song, a["selector"])
            elif any(o.get("op") == "__double_time__" for o in ops):
                ops = _lower_double_time(song, a["selector"])
            receipt, _ = surgical.apply_ops(song, a["selector"], ops)
            if song_name:
                surgical.append_receipt(song_name, receipt)
            receipts.append(receipt)
        elif kind == "track_field":
            idxs, _ = surgical.resolve_tracks(song, a["track"])
            if len(idxs) != 1:
                raise Miss(f"track_field_ambiguous:{a['track']}")
            t = song["tracks"][idxs[0]]
            f, v = a["field"], a["value"]
            if a.get("mode") == "add":
                v = float(t.get(f) or 0.0) + float(v)
            if f == "gainDb":
                v = round(min(12.0, max(-60.0, float(v))), 2)
            elif f == "pan":
                v = round(min(1.0, max(-1.0, float(v))), 3)
            t[f] = v
            fields.append(f"track:{a['track']}:{f}")
        elif kind == "meta_field":
            song[a["key"]] = a["value"]
            fields.append(f"meta:{a['key']}")
        elif kind == "track_fx_add":
            idxs, _ = surgical.resolve_tracks(song, a["track"])
            if len(idxs) != 1:
                raise Miss(f"track_field_ambiguous:{a['track']}")
            song["tracks"][idxs[0]].setdefault("fx", []).append(dict(a["fx"]))
            fields.append(f"track:{a['track']}:fx")
        elif kind == "track_source":
            idxs, _ = surgical.resolve_tracks(song, a["track"])
            if len(idxs) != 1:
                raise Miss(f"track_field_ambiguous:{a['track']}")
            song["tracks"][idxs[0]]["source"] = dict(a["source"])
            fields.append(f"track:{a['track']}:source")
        elif kind == "add_automation":
            idxs, _ = surgical.resolve_tracks(song, a["track"])
            if len(idxs) != 1:
                raise Miss(f"track_field_ambiguous:{a['track']}")
            song["tracks"][idxs[0]].setdefault("automation", []).append(
                {"target": a["target"], "points": [dict(p) for p in a["points"]]})
            fields.append(f"track:{a['track']}:automation")
        elif kind == "add_send":
            idxs, _ = surgical.resolve_tracks(song, a["track"])
            if len(idxs) != 1:
                raise Miss(f"track_field_ambiguous:{a['track']}")
            buses = song.setdefault("buses", [])
            bid = next((bu.get("id") for bu in buses
                        if "verb" in str(bu.get("id", "")).lower()
                        or any("reverb" in str(f.get("id", ""))
                               for f in bu.get("fx") or [])), None)
            if bid is None:
                bid = "verb"
                buses.append({"id": bid, "gainDb": -3,
                              "fx": [{"id": "fx_reverb"}]})
            song["tracks"][idxs[0]].setdefault("sends", []).append(
                {"bus": bid, "gainDb": -12})
            fields.append("buses")
            fields.append(f"track:{a['track']}:sends")
        else:
            raise Miss(f"unknown_action:{kind}")
    if fields or wild:
        rc = {"ts": round(time.time(), 2), "tool": "parse_lane", "fields": fields,
              "track_wild": wild, "summary": plan.get("summary", "parse lane")}
        if song_name:
            surgical.append_receipt(song_name, rc)
        receipts.append(rc)
    return receipts


# ---------------------------------------------------------------- compile
def compile_debug(text, song, context=None, facts=None, history=None):
    """-> (plan, miss_reason). plan None = honest miss (route to the cloud rail).
    Plans carry: actions, summary (the '[parse] ...' chat line), explain,
    pattern, verb (True if the verb bus must execute it), resolutions, ms.
    `history` = session_memory.history(song): powers the retarget grammar.
    The question guard runs AFTER the patterns — specific question forms (the
    history_q pattern) may compile; everything else question-shaped misses."""
    t0 = time.time()
    s = normalize(text)
    if not s or len(s) > 200:
        return None, "empty_or_long"
    global _RESOLUTIONS, _HISTORY, _CTX
    _HISTORY = history or {}
    _CTX = context if isinstance(context, dict) else {}
    try:
        return _compile_inner(s, song, context, facts, t0)
    finally:
        _HISTORY = None
        _CTX = None


def _probe(song, actions):
    """Dry-run the actions on a scratch copy. -> miss reason or None (ok)."""
    probe = copy.deepcopy(song)
    try:
        apply_plan(probe, {"actions": actions})
    except Miss as e:
        return e.reason
    except (ValueError, KeyError, TypeError) as e:
        return f"probe:{e}"
    if surgical.diff_is_empty(surgical.semantic_diff(song, probe)):
        return "no_op"                     # honesty: never ship an empty diff
    return None


def _compile_inner(s, song, context, facts, t0, allow_compound=True):
    global _RESOLUTIONS
    first_miss = None
    for name, rx, build in PATTERNS:
        m = rx.fullmatch(s)
        if not m:
            continue
        _RESOLUTIONS = {}
        try:
            actions, summary, explain = build(m, song, context or {}, facts or {})
        except Miss as e:
            first_miss = f"{name}:{e.reason}"
            break                          # the compound fallback may still own it
        except (ValueError, KeyError, TypeError) as e:
            first_miss = f"{name}:builder:{e}"   # an error is a MISS, never a wrong compile
            break
        finally:
            resolutions, _RESOLUTIONS = dict(_RESOLUTIONS or {}), None
        is_verb = any(a["kind"] == "verb" for a in actions)
        if not is_verb:
            why = _probe(song, actions)
            if why:
                first_miss = f"{name}:{why}"
                break
        plan = {"actions": actions, "summary": summary, "explain": explain,
                "pattern": name, "verb": is_verb, "resolutions": resolutions,
                "ms": round((time.time() - t0) * 1000.0, 2)}
        return plan, ""
    # COMPOUND: "mute the hats and pan the lead hard left" — both clauses must
    # independently fullmatch-compile (non-verb), then prove TOGETHER on one
    # scratch copy. Any unprovable clause = the whole ask misses (all-or-nothing).
    if allow_compound and " and " in s:
        parts = s.split(" and ")
        for i in range(1, len(parts)):
            left, _ = _compile_inner(" and ".join(parts[:i]), song, context,
                                     facts, t0, allow_compound=False)
            if left is None or left["verb"]:
                continue
            right, _ = _compile_inner(" and ".join(parts[i:]), song, context,
                                      facts, t0, allow_compound=False)
            if right is None or right["verb"]:
                continue
            actions = left["actions"] + right["actions"]
            if _probe(song, actions):
                continue
            reso = dict(left.get("resolutions") or {})
            reso.update(right.get("resolutions") or {})
            return ({"actions": actions,
                     "summary": left["summary"] + " + " + right["summary"],
                     "explain": (left.get("explain") or []) + (right.get("explain") or []),
                     "pattern": "compound", "verb": False, "resolutions": reso,
                     "ms": round((time.time() - t0) * 1000.0, 2)}, "")
    if first_miss:
        return None, first_miss
    if re.match(r"^(what|why|how|when|where|which|who|whats|hows|is |are |do |does "
                r"|can |could |should |would )", s):
        return None, "question"
    return None, "no_pattern"


def primary_track(plan):
    """The single track a plan targets, or None. The sidecar stores this with
    last_plan; multi-track / section / meta plans are NOT retargetable."""
    names = set()
    for a in (plan or {}).get("actions") or []:
        k = a.get("kind")
        if k in ("track_field", "track_fx_add", "track_source"):
            names.add(a.get("track"))
        elif k == "surgical":
            tr = (a.get("selector") or {}).get("tracks")
            if isinstance(tr, list) and len(tr) == 1:
                names.add(tr[0])
            else:
                return None
        elif k == "verb":
            t = (a.get("args") or {}).get("track")
            if not t:
                return None
            names.add(t)
        else:
            return None
    names.discard(None)
    return names.pop() if len(names) == 1 else None


def compile(text, song, context=None, facts=None, history=None):   # noqa: A001
    """The sidecar entry point. -> plan dict, or None = fall through to the cloud."""
    plan, _ = compile_debug(text, song, context, facts, history)
    return plan


if __name__ == "__main__":
    import json
    if len(sys.argv) < 3:
        print("usage: parse_lane.py <song.json> <ask...>")
        sys.exit(2)
    doc = json.load(open(sys.argv[1]))
    ask = " ".join(sys.argv[2:])
    plan, why = compile_debug(ask, doc)
    if plan is None:
        print(f"MISS ({why}) -> cloud rail")
        sys.exit(1)
    print(f"HIT [{plan['pattern']}] {plan['ms']}ms — {plan['summary']}")
    for a in plan["actions"]:
        print("  ", json.dumps(a))
