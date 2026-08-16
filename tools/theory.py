#!/usr/bin/env python3
"""THE THEORY KERNEL (PRODUCER MIND P1, docs/SPEC_PRODUCER_MIND.md).

ONE pure module for keys/scales/chords/degrees/voice-leading/tension math.
Every music court and heal imports THIS; the five drifted parse_key twins
(gold_bank/suggest_chords/retune/loop_gen/parse_lane) migrate here over time —
this kernel is a SUPERSET of all of them (verified in theory_battery.py).

Zero deps beyond stdlib. Deterministic. No I/O.

Vocabulary:
  pc      pitch class 0..11 (C=0)
  pitch   MIDI note number 0..127
  key     {"tonic_pc", "mode", "scale_pcs", "scale_names", "name"}
  chord   {"root_pc", "quality", "pcs", "bass_pc", "name"}
"""

# ---------------------------------------------------------------- pitch names
PC_OF = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}
SHARPS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLATS = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# modes as semitone sets from the tonic
MODES = {
    "major":          (0, 2, 4, 5, 7, 9, 11),
    "ionian":         (0, 2, 4, 5, 7, 9, 11),
    "minor":          (0, 2, 3, 5, 7, 8, 10),
    "aeolian":        (0, 2, 3, 5, 7, 8, 10),
    "harmonic_minor": (0, 2, 3, 5, 7, 8, 11),
    "melodic_minor":  (0, 2, 3, 5, 7, 9, 11),
    "dorian":         (0, 2, 3, 5, 7, 9, 10),
    "phrygian":       (0, 1, 3, 5, 7, 8, 10),
    "lydian":         (0, 2, 4, 6, 7, 9, 11),
    "mixolydian":     (0, 2, 4, 5, 7, 9, 10),
    "locrian":        (0, 1, 3, 5, 6, 8, 10),
    "major_pentatonic": (0, 2, 4, 7, 9),
    "minor_pentatonic": (0, 3, 5, 7, 10),
    "blues":          (0, 3, 5, 6, 7, 10),
    "chromatic":      tuple(range(12)),
    # R-24/R-25 modal law (wave 13): the psy/goa + global-lineage collections
    "phrygian_dominant": (0, 1, 4, 5, 7, 8, 10),   # hijaz / flamenco / psy lead
    "double_harmonic":   (0, 1, 4, 5, 7, 8, 11),   # Byzantine / double-harm major
    "hungarian_minor":   (0, 2, 3, 6, 7, 8, 11),
}

# R-24 MAQAM SYMBOLIC SUPPORT (wave 13): nearest-12TET foldings + which
# degrees are truly HALF-FLAT (-50c) in performance practice. Integer sets
# drive membership courts today; the quarter_flat list is the forward map for
# microtonal rendering (pitch-bend lanes) and widens court tolerance there.
MAQAM_12TET = {
    "hijaz":    {"pcs": (0, 1, 4, 5, 7, 8, 10), "quarter_flat": ()},
    "kurd":     {"pcs": (0, 1, 3, 5, 7, 8, 10), "quarter_flat": ()},
    "nahawand": {"pcs": (0, 2, 3, 5, 7, 8, 10), "quarter_flat": ()},
    "rast":     {"pcs": (0, 2, 4, 5, 7, 9, 10), "quarter_flat": (4, 11)},
    "bayati":   {"pcs": (0, 2, 3, 5, 7, 8, 10), "quarter_flat": (3,)},
    "saba":     {"pcs": (0, 2, 3, 4, 7, 8, 10), "quarter_flat": (3,)},
    "sikah":    {"pcs": (0, 3, 5, 7, 8, 11), "quarter_flat": (0,)},
}

# common alias words seen in song.json "key" fields across the corpus
_MODE_ALIASES = {
    "maj": "major", "m": "minor", "min": "minor", "natural minor": "minor",
    "harm minor": "harmonic_minor", "harmonic": "harmonic_minor",
    "melodic": "melodic_minor", "pent": "major_pentatonic",
}


def midi_to_name(pitch, flats=False):
    """60 -> 'C4' (octave -1-based like the rest of the house)."""
    pitch = int(pitch)
    table = FLATS if flats else SHARPS
    return f"{table[pitch % 12]}{pitch // 12 - 1}"


def name_to_midi(name):
    """'C4'->60, 'F#3'->54, 'Bb2'->46. None on garbage."""
    s = str(name or "").strip()
    if not s:
        return None
    head = s[0].lower()
    if head not in PC_OF:
        return None
    pc, i = PC_OF[head], 1
    while i < len(s) and s[i] in "#b♯♭":
        pc += 1 if s[i] in "#♯" else -1
        i += 1
    try:
        octave = int(s[i:])
    except ValueError:
        return None
    return (octave + 1) * 12 + (pc % 12)


def _pc_of_token(tok):
    """'F#'->6, 'Bb'->10, 'c'->0. None if not a note token."""
    s = str(tok or "").strip()
    if not s or s[0].lower() not in PC_OF:
        return None
    pc = PC_OF[s[0].lower()]
    for ch in s[1:]:
        if ch in "#♯":
            pc += 1
        elif ch in "b♭":
            pc -= 1
        else:
            return None
    return pc % 12


# ------------------------------------------------------------------- the key
def parse_key(text):
    """Any corpus key spelling -> key dict, or None.

    Accepts: 'F minor', 'F#m', 'Bb', 'c# min', 'D dorian', 'A harmonic minor',
    'Eb Major', 'Am', 'F# Minor (natural)'. A bare note = major (house corpus
    convention). Superset of the five drifted twins.
    """
    s = str(text or "").strip()
    if not s:
        return None
    s = s.replace("♯", "#").replace("♭", "b")
    # tonic token = leading note letter + accidentals
    i = 1
    if not s[0].isalpha() or s[0].lower() not in PC_OF:
        return None
    while i < len(s) and s[i] in "#b":
        i += 1
    tonic_pc = _pc_of_token(s[:i])
    rest = s[i:].strip().lower().strip("()").strip()
    # trailing 'm' glued to the tonic: 'F#m', 'Am7' is a CHORD not a key — keys
    # only ever carry mode words after the tonic, so a bare glued 'm' = minor.
    mode = None
    if rest == "m":
        mode = "minor"
    elif rest:
        rest = rest.replace("-", "_").replace(" ", "_")
        for cand in (rest, rest.rstrip("_")):
            if cand in MODES:
                mode = cand
                break
            if cand in _MODE_ALIASES:
                mode = _MODE_ALIASES[cand]
                break
        if mode is None:
            # tolerate noise words: 'f_minor_(natural)' etc — find a known word
            for w in rest.split("_"):
                if w in MODES:
                    mode = w
                    break
                if w in _MODE_ALIASES:
                    mode = _MODE_ALIASES[w]
                    break
        if mode is None:
            return None            # unknown mode word: refuse, never guess
    else:
        mode = "major"
    if tonic_pc is None:
        return None
    pcs = tuple((tonic_pc + off) % 12 for off in MODES[mode])
    prefer_flats = FLATS[tonic_pc] != SHARPS[tonic_pc] and "b" in s[:i]
    names = [(FLATS if prefer_flats else SHARPS)[p] for p in pcs]
    return {"tonic_pc": tonic_pc, "mode": mode, "scale_pcs": frozenset(pcs),
            "scale_names": names,
            "name": f"{(FLATS if prefer_flats else SHARPS)[tonic_pc]} {mode}"}


def in_scale(pitch, key):
    return (int(pitch) % 12) in key["scale_pcs"]


def degree_of(pitch, key):
    """1-based scale degree of pitch in key, or None if off-scale."""
    pc = int(pitch) % 12
    order = sorted((p - key["tonic_pc"]) % 12 for p in key["scale_pcs"])
    rel = (pc - key["tonic_pc"]) % 12
    return order.index(rel) + 1 if rel in order else None


# ----------------------------------------------------------------- the chord
_QUAL = {
    # quality -> semitone offsets from root
    "":        (0, 4, 7),          "maj":    (0, 4, 7),
    "m":       (0, 3, 7),          "min":    (0, 3, 7),
    "dim":     (0, 3, 6),          "aug":    (0, 4, 8),
    "sus2":    (0, 2, 7),          "sus4":   (0, 5, 7),
    "5":       (0, 7),
    "6":       (0, 4, 7, 9),       "m6":     (0, 3, 7, 9),
    "7":       (0, 4, 7, 10),      "maj7":   (0, 4, 7, 11),
    "m7":      (0, 3, 7, 10),      "mmaj7":  (0, 3, 7, 11),
    "dim7":    (0, 3, 6, 9),       "m7b5":   (0, 3, 6, 10),
    "7sus4":   (0, 5, 7, 10),
    "9":       (0, 4, 7, 10, 14),  "maj9":   (0, 4, 7, 11, 14),
    "m9":      (0, 3, 7, 10, 14),  "add9":   (0, 4, 7, 14),
    "madd9":   (0, 3, 7, 14),
    "11":      (0, 4, 7, 10, 14, 17), "m11":  (0, 3, 7, 10, 14, 17),
    "13":      (0, 4, 7, 10, 14, 21), "m13":  (0, 3, 7, 10, 14, 21),
    "7b9":     (0, 4, 7, 10, 13),  "7#9":    (0, 4, 7, 10, 15),
    "7#5":     (0, 4, 8, 10),      "7b5":    (0, 4, 6, 10),
}
# longest-first so 'maj7' wins over 'maj', 'm7b5' over 'm7'
_QUAL_KEYS = sorted((k for k in _QUAL if k), key=len, reverse=True)


def parse_chord(text):
    """'Am7' / 'F#m7b5' / 'Cmaj7' / 'G/B' / 'Dsus4' -> chord dict, or None.
    Unknown suffix lands on the major triad (SongLoader.h:153 same law —
    never drop a declared chord)."""
    s = str(text or "").strip().replace("♯", "#").replace("♭", "b")
    if not s:
        return None
    bass_pc = None
    if "/" in s:
        s, bass = s.split("/", 1)
        bass_pc = _pc_of_token(bass.strip())
    i = 1
    if not s or s[0].lower() not in PC_OF:
        return None
    while i < len(s) and s[i] in "#b":
        i += 1
    root_pc = _pc_of_token(s[:i])
    if root_pc is None:
        return None
    suffix = s[i:].strip()
    qual = None
    if suffix in _QUAL:
        qual = suffix
    else:
        for k in _QUAL_KEYS:
            if suffix.lower().startswith(k.lower()):
                qual = k
                break
    if qual is None:
        qual = ""                                    # unknown -> major triad
    pcs = frozenset((root_pc + off) % 12 for off in _QUAL[qual])
    return {"root_pc": root_pc, "quality": qual or "maj", "pcs": pcs,
            "bass_pc": bass_pc if bass_pc is not None else root_pc,
            "name": s + (f"/{FLATS[bass_pc]}" if bass_pc is not None else "")}


def chord_at(chords, bar):
    """The sounding chord dict at 1-BASED bar from the song's chords[] spine
    ({bar, chord} rows, SongLoader.h:120 law). Rows hold until the next row.
    None when the spine is empty or the bar precedes the first row."""
    best = None
    for row in sorted(chords or [], key=lambda r: float(r.get("bar", 1))):
        if float(row.get("bar", 1)) <= float(bar) + 1e-9:
            best = row
        else:
            break
    return parse_chord(best.get("chord")) if best else None


# ------------------------------------------------- genre allowance profiles
# Which off-scale pitch classes are IDIOMATIC per genre family (relative to
# the key tonic), and how forgiving the court is of chromatic passing motion.
# Families route by substring like lyric_bank.FAMILY — R-1/R-21..25 research
# refines these tables; these seeds are conservative music-theory truth.
ALLOWANCE = {
    # blue notes vs MAJOR keys: b3, b5, b7; vs minor: b5 (the blues note)
    "blues":     {"major_extra": (3, 6, 10), "minor_extra": (6,),
                  "passing": "generous"},
    "jazz":      {"major_extra": (1, 3, 6, 8, 10), "minor_extra": (1, 4, 6, 9, 11),
                  "passing": "generous"},   # approach tones are the idiom
    "strict":    {"major_extra": (), "minor_extra": (), "passing": "normal"},
    # THE SUPERMODE LAW (R-1, Temperley MTO 17.4 researched 2026-07-14): in
    # rock/pop corpora every degree EXCEPT b2 and #4 is common — modal
    # mixture (b3/b6/b7 vs major) is idiom, not error. Those land in
    # soft_major: pardoned UNLESS long + strong-beat + against the sounding
    # chord (Temperley MTO 23.1: no threshold separates blue from wrong —
    # only the local-chord contradiction does). b2/#4 stay HARD everywhere
    # outside blues (#4 = THE blue note there) and jazz.
    "leading":   {"major_extra": (), "minor_extra": (11,),
                  "soft_major": (3, 8, 10), "passing": "normal"},
    "free":      {"major_extra": tuple(range(12)), "minor_extra": tuple(range(12)),
                  "passing": "generous"},   # atonal/noise/experimental: exempt
}
FAMILY = {
    "blues": ("blues", "rock", "rocknroll", "rockabilly", "country_blues",
              "boogie", "rnb_classic", "soul_blues", "funk", "gospel_blues",
              # borrowed-b7/b3 idiom families (bass rides mixolydian/pentatonic)
              "reggae", "dub", "ska", "dancehall", "soul", "motown", "gospel"),
    "jazz": ("jazz", "bebop", "swing", "bigband", "bossa", "fusion", "neosoul",
             "neo_soul", "lofi", "jazzhop"),
    "free": ("noise", "atonal", "experimental", "musique", "freeimprov",
             "harshnoise", "glitch_noise", "sound_art"),
}


def allowance_for(genre):
    g = str(genre or "").lower()
    for fam, keys in FAMILY.items():
        if any(k in g for k in keys):
            return ALLOWANCE[fam]
    # minor-key genres get the leading tone at no charge (harmonic minor use)
    return ALLOWANCE["leading"]


def _is_majorish(key):
    return "major" in key["mode"] or key["mode"] in (
        "ionian", "lydian", "mixolydian", "major_pentatonic")


def allowed_pcs(key, genre):
    """The full pardoned pitch-class set for melodic content in this key+genre."""
    prof = allowance_for(genre)
    extra = prof["major_extra"] if _is_majorish(key) else prof["minor_extra"]
    return frozenset(key["scale_pcs"] | {(key["tonic_pc"] + e) % 12 for e in extra})


def soft_pcs(key, genre):
    """SUPERMODE mixture degrees (R-1): pardoned unless long + strong + against
    the sounding chord. Empty for minor keys (their scale already carries
    b3/b6/b7) and for families with their own idiom tables."""
    prof = allowance_for(genre)
    if not _is_majorish(key):
        return frozenset()
    return frozenset((key["tonic_pc"] + e) % 12
                     for e in prof.get("soft_major", ()))


def is_passing_forgivable(note, prev_note, next_note, beats_per_bar=4.0,
                          generous=False):
    """A short, weak-beat, stepwise-approached-and-resolved off-scale note is
    a chromatic passing tone, not a wrong note. note dicts: start/length/pitch."""
    if note is None:
        return False
    ln = float(note.get("len", note.get("length", 0.25)))
    max_len = 0.75 if generous else 0.5
    if ln > max_len + 1e-9:
        return False
    pos = float(note.get("start", 0.0)) % beats_per_bar
    on_strong = abs(pos - round(pos)) < 1e-6 and int(round(pos)) % 2 == 0
    if on_strong and not generous:
        return False
    p = int(note.get("pitch", 60))
    ok_in = prev_note is not None and abs(int(prev_note.get("pitch", p)) - p) <= 2
    ok_out = next_note is not None and abs(int(next_note.get("pitch", p)) - p) <= 2
    return ok_in and ok_out


# ------------------------------------------------------------------ the heal
def snap_pitch(pitch, key, genre="", chord=None, prev_pitch=None,
               next_pitch=None, bass=False):
    """The VOICE-LEADING-AWARE scale snap (never naive nearest).

    Candidates = pardoned pcs within +-2 semitones. Score (lower wins):
      distance from the original (voice-leading cost, x2)
      - chord-tone bonus (the note the harmony wants)
      - contour preservation bonus (keeps the melodic shape vs neighbors)
    Ties break DOWNWARD (gravity — resolves like a suspension).
    Returns the original pitch when it is already legal.
    """
    p = int(pitch)
    legal = allowed_pcs(key, genre)
    if p % 12 in legal:
        return p
    cands = [c for c in range(p - 2, p + 3)
             if 0 <= c <= 127 and c % 12 in legal and c != p]
    if not cands:
        return p                                     # nothing sane: refuse
    def contour_kept(c):
        kept = 0
        if prev_pitch is not None:
            want = (p > prev_pitch) - (p < prev_pitch)
            got = (c > prev_pitch) - (c < prev_pitch)
            kept += (want == got)
        if next_pitch is not None:
            want = (next_pitch > p) - (next_pitch < p)
            got = (next_pitch > c) - (next_pitch < c)
            kept += (want == got)
        return kept
    def score(c):
        s = 2.0 * abs(c - p)
        if chord and c % 12 in chord["pcs"]:
            s -= 1.5
        # THE 808 KEY-LOCK (R-22: off-key 808 = the #1 cross-genre AI tell):
        # bass-role snaps pull HARD toward the chord ROOT — the sub carries
        # the harmony's foundation, not a color tone.
        if bass and chord:
            if c % 12 == chord["bass_pc"]:
                s -= 2.5
            elif c % 12 == chord["root_pc"]:
                s -= 2.0
        s -= 0.5 * contour_kept(c)
        return (s, c > p, abs(c - p))                # gravity tie-break: down
    return min(cands, key=score)


# ---------------------------------------------------------- voice leading
def voice_leading_cost(voicing_a, voicing_b):
    """Minimal total semitone motion mapping voicing A (list of pitches) to B.
    Greedy nearest-pair (optimal for the small voicings we use; battery-checked
    against brute force up to 5 voices)."""
    a, b = sorted(int(x) for x in voicing_a), sorted(int(x) for x in voicing_b)
    if not a or not b:
        return 0
    # pad the smaller by duplicating nearest ends (common-tone doubling)
    while len(a) < len(b):
        a.append(a[-1])
    while len(b) < len(a):
        b.append(b[-1])
    import itertools
    best = None
    if len(b) <= 6:
        for perm in itertools.permutations(b):
            cost = sum(abs(x - y) for x, y in zip(a, perm))
            best = cost if best is None or cost < best else best
        return best
    return sum(abs(x - y) for x, y in zip(a, b))


def voice_chord(chord, register=(48, 72), prev_voicing=None):
    """A concrete voicing (list of MIDI pitches) for a chord dict inside a
    register, minimizing motion from prev_voicing when given. Root goes lowest
    (bass_pc honored)."""
    lo, hi = register
    pcs = sorted(chord["pcs"])
    bass = chord["bass_pc"]
    # bass: lowest legal placement of bass_pc
    bpitch = lo + ((bass - lo) % 12)
    upper_pcs = [pc for pc in pcs if pc != bass] or [bass]
    if prev_voicing is None:
        voicing, cur = [bpitch], bpitch + 3
        for pc in upper_pcs:
            nxt = cur + ((pc - cur) % 12)
            voicing.append(nxt)
            cur = nxt + 1
        return [min(max(v, lo), hi) for v in voicing]
    best, best_cost = None, None
    import itertools
    octset = range(lo, hi + 1)
    cands_per_pc = [[p for p in octset if p % 12 == pc] for pc in upper_pcs]
    for combo in itertools.product(*cands_per_pc):
        v = [bpitch] + sorted(combo)
        c = voice_leading_cost(prev_voicing, v)
        if best_cost is None or c < best_cost:
            best, best_cost = v, c
    return best or [bpitch]


# ------------------------------------------------------------------ tension
# Plomp-Levelt-flavored interval roughness (semitone-class -> dissonance 0..1)
_ROUGH = {0: 0.0, 1: 1.0, 2: 0.65, 3: 0.25, 4: 0.2, 5: 0.1,
          6: 0.7, 7: 0.05, 8: 0.25, 9: 0.2, 10: 0.4, 11: 0.85}


def interval_roughness(a, b):
    return _ROUGH[abs(int(a) - int(b)) % 12]


def cluster_tension(pitches):
    """Mean pairwise roughness of simultaneous pitches (0 = consonant)."""
    ps = [int(p) for p in pitches]
    if len(ps) < 2:
        return 0.0
    tot = n = 0
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            tot += interval_roughness(ps[i], ps[j])
            n += 1
    return tot / n


def infer_key(notes, genre=""):
    """Krumhansl-Schmuckler over note dicts (duration-weighted) -> key dict.
    The fallback for imported/undeclared songs; declared keys always outrank.
    genre routes the pitch-class profile (R-1 wave 13: Aarden for folk/melodic,
    supermode for rock — one global profile is the 74%-accuracy trap)."""
    # Bellman-Budge profiles (R-1 researched: 91-95% vs raw K-S 74% —
    # Napoles Lopez et al., DLfM 2019); K-S kept as the tie-breaking blend.
    KK_MAJ = (16.80, 0.86, 12.95, 1.41, 13.49, 11.93, 1.25, 20.28, 1.80, 8.04, 0.62, 10.57)
    KK_MIN = (18.16, 0.69, 12.99, 13.34, 1.07, 11.15, 1.38, 21.07, 7.49, 1.53, 0.92, 10.21)
    gmaj, gmin = key_profiles_for(genre)
    if gmaj:
        KK_MAJ, KK_MIN = gmaj, gmin
    hist = [0.0] * 12
    for n in notes or []:
        try:
            hist[int(n.get("pitch", 0)) % 12] += max(
                float(n.get("len", n.get("length", 0.25))), 0.05)
        except Exception:
            continue
    if not any(hist):
        return None
    def corr(profile, rot):
        prof = [profile[(i - rot) % 12] for i in range(12)]
        mp = sum(prof) / 12.0
        mh = sum(hist) / 12.0
        num = sum((prof[i] - mp) * (hist[i] - mh) for i in range(12))
        dp = (sum((p - mp) ** 2 for p in prof) * sum((h - mh) ** 2 for h in hist)) ** 0.5
        return num / dp if dp else 0.0
    best = None
    for tonic in range(12):
        for mode, prof in (("major", KK_MAJ), ("minor", KK_MIN)):
            c = corr(prof, tonic)
            if best is None or c > best[0]:
                best = (c, tonic, mode)
    _, tonic, mode = best
    return parse_key(f"{SHARPS[tonic]} {mode}")


# ---------------------------------------------- R-1 chord-tone/tension/avoid
# Available tensions per chord quality (jazz pedagogy tables): pcs RELATIVE
# to the chord root. Anything a semitone above a chord tone that is NOT an
# available tension is an AVOID note (the ESCALATE class — R-1: only avoid
# notes convict; everything else is color).
_TENSIONS = {
    "maj":   (2, 6, 9),            # 9, #11, 13
    "maj7":  (2, 6, 9),
    "6":     (2, 6),
    "m":     (2, 5, 9),            # 9, 11, (dorian 13)
    "m7":    (2, 5, 9),
    "m6":    (2, 5),
    "mmaj7": (2, 5, 9),
    "7":     (1, 2, 3, 6, 8, 9),   # b9 9 #9 #11 b13 13 — dominants take all
    "7sus4": (1, 2, 9),
    "m7b5":  (2, 5, 8),            # 9, 11, b13
    "dim7":  (2, 5, 8, 11),
    "sus2":  (5, 9), "sus4": (2, 9), "5": (2, 4, 5, 9),
}


def classify_vs_chord(pitch, chord):
    """'chord_tone' | 'tension' | 'avoid' | 'outside' for a pitch against a
    chord dict. Avoid = semitone above a chord tone and not an available
    tension (the note that makes the harmony seasick when held)."""
    if not chord:
        return "outside"
    rel = (int(pitch) - chord["root_pc"]) % 12
    rel_pcs = {(p - chord["root_pc"]) % 12 for p in chord["pcs"]}
    if rel in rel_pcs:
        return "chord_tone"
    tens = set(_TENSIONS.get(chord.get("quality", ""), (2, 9)))
    if rel in tens:
        return "tension"
    if any((rel - t) % 12 == 1 for t in rel_pcs):
        return "avoid"
    return "outside"


# --------------------------------------------- R-1 function + cadence kernel
def function_of(chord, key):
    """'T' | 'P' | 'D' | None — functional region of a chord in a key
    (Tonic {I,vi,iii}, Predominant {ii,IV}, Dominant {V,vii})."""
    if not chord or not key:
        return None
    deg = (chord["root_pc"] - key["tonic_pc"]) % 12
    major = _is_majorish(key)
    table = {0: "T", 9 if major else 8: "T", 4 if major else 3: "T",
             2: "P", 5: "P",
             7: "D", 11 if major else 10: "D"}
    return table.get(deg)


def cadence_of(prev_chord, final_chord, key, soprano_pc=None):
    """'PAC' | 'IAC' | 'plagal' | 'half' | 'deceptive' | None for the
    penultimate->final pair at a phrase end (R-1 rule-based kernel — skip
    the neural GNN entirely; rules cover the corpus)."""
    if not prev_chord or not final_chord or not key:
        return None
    pdeg = (prev_chord["root_pc"] - key["tonic_pc"]) % 12
    fdeg = (final_chord["root_pc"] - key["tonic_pc"]) % 12
    major = _is_majorish(key)
    dom = (7, 11) if major else (7, 10, 11)
    if pdeg in dom and fdeg == 0:
        if soprano_pc is not None and soprano_pc == key["tonic_pc"] \
                and prev_chord["quality"] in ("", "maj", "7"):
            return "PAC"
        return "IAC"
    if pdeg == 5 and fdeg == 0:
        return "plagal"
    if fdeg == 7:
        return "half"
    if pdeg in dom and fdeg == (9 if major else 8):
        return "deceptive"
    return None


# ------------------------------------- R-1 L1 cyclic-rotation voicing solver
def rotation_voicing(target_pcs, prev_voicing):
    """The EXACT R-1 minimal-motion kernel: given a target chord's pitch-class
    multiset and the previous voicing, evaluate all n cyclic rotations of the
    sorted pc list against the sorted previous voicing; score each by
    L1 = sum of mod-12 circular distances (each <= 6); pick the min (ties ->
    the rotation keeping the most common tones). Returns concrete pitches
    nearest to each previous voice."""
    prev = sorted(int(p) for p in prev_voicing or [])
    pcs = sorted(int(p) % 12 for p in target_pcs or [])
    if not prev or not pcs:
        return list(prev)
    # pad the shorter side by doubling (common-tone doubling law)
    voices = max(len(prev), len(pcs))
    while len(pcs) < voices:
        pcs.append(pcs[len(pcs) % max(len(set(pcs)), 1)])
    prev_p = list(prev)
    while len(prev_p) < voices:
        prev_p.append(prev_p[-1])

    def circ(a, b):
        d = abs(a - b) % 12
        return min(d, 12 - d)

    best = None
    for r in range(voices):
        rot = pcs[r:] + pcs[:r]
        cost = sum(circ(p % 12, pc) for p, pc in zip(prev_p, rot))
        common = sum(1 for p, pc in zip(prev_p, rot) if p % 12 == pc)
        if best is None or (cost, -common) < (best[0], -best[1]):
            best = (cost, common, rot)
    _, _, rot = best
    out = []
    for p, pc in zip(prev_p, rot):
        cands = [p + ((pc - p) % 12), p - ((p - pc) % 12)]
        out.append(min((c for c in cands if 0 <= c <= 127),
                       key=lambda c: abs(c - p)))
    return sorted(out)


def parallel_perfects(voicing_a, voicing_b):
    """Parallel fifths/octaves between two SAME-SIZE voicings (index-paired
    voices): [(i, j, interval)] where both voices move and keep a perfect
    5th/octave. The counterpoint tripwire for the voicing battery."""
    a, b = list(voicing_a or []), list(voicing_b or [])
    hits = []
    for i in range(min(len(a), len(b))):
        for j in range(i + 1, min(len(a), len(b))):
            iv_a = abs(a[j] - a[i]) % 12
            iv_b = abs(b[j] - b[i]) % 12
            moved = a[i] != b[i] or a[j] != b[j]
            if moved and iv_a == iv_b and iv_a in (0, 7):
                hits.append((i, j, iv_a))
    return hits


# ------------------------------------------- R-26 spread voicing (wave 13)
def voice_spread(chord, top=72, low_register_limit=48):
    """Harmonic-series spacing (R-26): widest at bottom, closest at top; below
    ~C3 emit root+5th(+octave) ONLY — no 3rds in the mud. Returns pitches."""
    if not chord:
        return []
    root = chord["bass_pc"]
    bass = 36 + ((root - 36) % 12)
    out = [bass, bass + 7, bass + 12]                # root 5th oct — the floor
    color = [pc for pc in sorted(chord["pcs"])
             if pc not in {root % 12, (root + 7) % 12}]
    cur = max(low_register_limit, bass + 12) + 3
    for pc in color:
        nxt = cur + ((pc - cur) % 12)
        if nxt > top:
            nxt -= 12
        if nxt > out[-1] - 12:                       # keep upper structure tight
            out.append(nxt)
            cur = nxt + 1
    return sorted(dict.fromkeys(out))


# ------------------------------------ R-1 per-genre pitch-class key profiles
# Aarden-Essen (folk/melodic corpora) — Aarden 2003; Bellman-Budge already
# drives infer_key; supermode = near-flat rock profile (Temperley MTO 17.4).
_AARDEN_MAJ = (17.77, 0.15, 14.93, 0.16, 19.80, 11.36, 0.29,
               22.06, 0.15, 8.15, 0.23, 4.95)
_AARDEN_MIN = (18.26, 0.74, 14.05, 16.86, 0.70, 14.44, 0.70,
               18.62, 4.57, 1.93, 7.38, 1.76)
_SUPERMODE_MAJ = (14.0, 2.0, 11.0, 8.0, 11.0, 10.0, 2.0, 13.0, 6.0, 9.0, 8.0, 6.0)
_SUPERMODE_MIN = (14.0, 2.0, 10.0, 11.0, 6.0, 10.0, 2.0, 13.0, 8.0, 6.0, 9.0, 4.0)


def key_profiles_for(genre):
    """(major_profile, minor_profile) routed by genre family (R-1: one global
    profile is 74%-accurate; family profiles reach 91-94%)."""
    g = str(genre or "").lower()
    if any(k in g for k in ("folk", "country", "acoustic", "singer", "trad",
                            "celtic", "bluegrass", "sea", "shanty")):
        return _AARDEN_MAJ, _AARDEN_MIN
    if any(k in g for k in ("rock", "punk", "metal", "indie", "grunge",
                            "garage_rock", "emo")):
        return _SUPERMODE_MAJ, _SUPERMODE_MIN
    return None, None                                # Bellman-Budge default


if __name__ == "__main__":
    import json as _json
    import sys as _sys
    k = parse_key(" ".join(_sys.argv[1:]) or "F minor")
    print(_json.dumps({**k, "scale_pcs": sorted(k["scale_pcs"])}, indent=1))
