#!/usr/bin/env python3
"""THE LYRIC COURTS — words meet notes as law (wave 17; R-10 items
009/010/011/062).

Deterministic kernels over song.json lyrics[] + the sung lane's notes.
Sources (all cited in docs/research_producer_mind/r-10.json):
  REFFLY (NAACL 2025): singability is ASYMMETRIC — one note carrying a
    multi-syllable word = unsingable under-provisioning; one syllable
    over many notes (melisma) is fine and genre-desirable.
  arXiv 2412.04202 + LOAF-M2L 2307.02146: ~80% of KEYWORDS land on
    strong beats / long notes in human corpora — the 0.80 prominence
    floor; content-on-strong-beat outranks raw syllable stress by 0.27.
  voicescience.org / belting acoustics: closed vowels /i/ /u/ (low F1)
    physically cannot track 2f0 on high sustained notes; open /a/ /ae/
    sustain best — vowel-on-long-note is physics, not taste.
  Open Music Theory / PMC11098490: verse = lyric-VARIANT, chorus =
    lyric-INVARIANT (verbatim), bridge = one-time contrast.

THE AUTHORSHIP GUARD: heals may rewrite BANK-authored words only (every
word verifiably ∈ lyric_bank's family bank = provenance proof). User or
ASR words get advisories — the court never rewrites a human's lyric.
THE WITNESS LAW: stems-imported records are evidence, not defendants.

  syllables(word) / stresses(word) / is_content(word)   kernels
  court_singability + heal_singability   009: crammed polysyllables ->
        seeded monosyllable swap from the SAME family bank (bank-authored
        lyrics only)
  court_prosody + heal_prosody           010: content-on-prominence >=
        floor; heal swaps a strong-beat function word with the nearest
        weak-beat content word (word set preserved, placement fixed)
  court_vowel_long                       011: ADVISORY — closed vowel on
        long+high notes (F1 physics; meaning outranks, so never convicts)
  court_form + heal_form                 062: chorus drift convicts
        (heal: first chorus's words re-land on later instances); verse
        sameness advisories
  court_lyrics(song, genre, heal=False)  aggregate
"""
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# R-10 syllable-budget rec: ~7.5 sustained words/sec is the articulation
# feasibility ceiling; per-syllable that is ~133ms.
SYL_MIN_S = 1.0 / 7.5
# CORPUS-CALIBRATED (self-measure law, 9 sung takes, 2026-07-15): real
# accepted takes measure prosody 0.60-1.0 on THIS detector (untitled_43's
# rescued real vocals = 0.74), so the literature 0.80 floor CONVICTS only
# bank-authored lyrics (where the swap heal can act); user lyrics convict
# only below 0.55 (under every real take) and get an advisory in between.
PROMINENCE_FLOOR = 0.80      # arXiv 2412.04202: 80.8% keywords-on-strong
PROSODY_HARD_USER = 0.55     # corpus min real take = 0.60
# chorus rotation-disease measures 0.0-0.17 similarity (untitled_31/48,
# pre-hook-law takes = TRUE catches); intentional final-chorus variance
# measures ~0.75 (untitled_38) and must stay an advisory.
CHORUS_SIM_FLOOR = 0.50      # below = rotation disease, convicts
CHORUS_SIM_IDEAL = 0.95      # below ideal but above floor = advisory
VERSE_SIM_CEIL = 0.70        # verses should walk, not clone

_FUNCTION_WORDS = frozenset("""
a an the and or but if so nor for yet of in on at to by with from as is am
are was were be been being do does did have has had will would can could
shall should may might must it its this that these those i you he she we
they them his her my your our their me him us who whom what which when
where why how not no oh ooh ah yeah hey la na mm hmm uh whoa
""".split())

_OPEN_VOWELS = ("AA", "AE", "AO", "AH", "EH", "AW", "AY")   # high F1
_CLOSED_VOWELS = ("IY", "UW")                               # low F1

_cmu = None
_pyphen = None


def _lex():
    global _cmu, _pyphen
    if _cmu is None:
        try:
            import cmudict
            _cmu = cmudict.dict()
        except Exception:
            _cmu = {}
        try:
            import pyphen
            _pyphen = pyphen.Pyphen(lang="en_US")
        except Exception:
            _pyphen = False
    return _cmu, _pyphen


def _clean(word):
    return re.sub(r"[^a-z']", "", str(word or "").lower()).strip("'")


def is_phoneme_token(word):
    return str(word or "").startswith("@")


def syllables(word):
    """Deterministic syllable count: CMU -> pyphen -> vowel groups.
    Returns None for @phoneme tokens / empty."""
    if is_phoneme_token(word):
        return None
    w = _clean(word)
    if not w:
        return None
    cmu, pyp = _lex()
    prons = cmu.get(w)
    if prons:
        return len([p for p in prons[0] if p[-1].isdigit()])
    if pyp:
        return max(1, pyp.inserted(w).count("-") + 1)
    return max(1, len(re.findall(r"[aeiouy]+", w)))


def stresses(word):
    """CMU stress digits of the first pronunciation ('1'=primary), or
    None for OOV/phoneme tokens."""
    if is_phoneme_token(word):
        return None
    cmu, _ = _lex()
    prons = cmu.get(_clean(word))
    if not prons:
        return None
    return [p[-1] for p in prons[0] if p[-1].isdigit()]


def stressed_vowel(word):
    """The primary-stressed syllable's vowel phone (e.g. 'IY'), or None."""
    if is_phoneme_token(word):
        return None
    cmu, _ = _lex()
    prons = cmu.get(_clean(word))
    if not prons:
        return None
    vs = [p for p in prons[0] if p[-1].isdigit()]
    for v in vs:
        if v.endswith("1"):
            return v[:-1]
    return vs[0][:-1] if vs else None


def is_content(word):
    w = _clean(word)
    return bool(w) and w not in _FUNCTION_WORDS and not is_phoneme_token(word)


# ------------------------------------------------------------ song plumbing
def vocal_lane(song):
    """The sung lane: vocal-named track with notes (never *_sketch)."""
    best = None
    for t in (song or {}).get("tracks", []) or []:
        if not isinstance(t, dict) or t.get("muted"):
            continue
        nm = str(t.get("name", "")).lower()
        if nm.endswith("_sketch") or nm.endswith("_identity"):
            continue
        if any(w in nm for w in ("vocal", "vox", "lead_vox", "topline",
                                 "voice", "sing")) and (t.get("notes") or []):
            if best is None or len(t["notes"]) > len(best.get("notes") or []):
                best = t
    return best


def _is_imported(song):
    for t in (song or {}).get("tracks", []) or []:
        nm = str((t or {}).get("name", "")).lower() if isinstance(t, dict) else ""
        if nm.endswith("_sketch") or nm.endswith("_identity"):
            return True
    return False


def aligned(song):
    """lyrics[] joined to the vocal lane's notes by beat (eps 1/8).
    Returns list of {word, beat, note|None, dur_beats, n_words} in beat
    order. LINE MODE (corpus law): an entry carrying several words is a
    LINE staged at its phrase start — its window is the gap to the NEXT
    entry (the singer distributes syllables across the phrase's notes),
    never one note's length; a closing line rings 4 beats."""
    lyr = sorted((l for l in (song or {}).get("lyrics", []) or []
                  if isinstance(l, dict)), key=lambda l: float(l.get("beat", 0)))
    lane = vocal_lane(song)
    notes = sorted((n for n in (lane or {}).get("notes") or []),
                   key=lambda n: float(n.get("start", 0)))
    out = []
    for i, l in enumerate(lyr):
        b = float(l.get("beat", 0))
        text = str(l.get("text", ""))
        n_words = len(text.split())
        note = None
        for n in notes:
            if abs(float(n.get("start", 0)) - b) <= 0.125:
                note = n
                break
        nxt = float(lyr[i + 1].get("beat", b)) if i + 1 < len(lyr) else None
        # a wordless stretch after an entry belongs to THAT entry (ASR
        # words rarely coincide with note grid starts — untitled_43 law)
        gap = max(nxt - b, 0.125) if nxt is not None else \
            (4.0 if n_words > 1 else 2.0)
        if n_words > 1:
            dur = gap
        else:
            dur = float(note.get("len", 0.25)) if note else gap
        out.append({"word": text, "beat": b, "note": note,
                    "dur_beats": dur, "n_words": n_words, "idx": i,
                    "melisma": int(l.get("melisma", 0) or 0)})
    return out


def bank_authored(song, genre):
    """THE AUTHORSHIP GUARD: True only when EVERY word is verifiably in
    the genre family's lyric bank (provenance proof — safe to heal)."""
    try:
        import lyric_bank
        bank = {w.lower() for w in lyric_bank.bank_for(genre)}
    except Exception:
        return False
    words = [str(l.get("text", "")) for l in (song or {}).get("lyrics", []) or []
             if isinstance(l, dict)]
    words = [w for w in words if not is_phoneme_token(w)]
    return bool(words) and all(w.lower() in bank for w in words)


def _spb(song):
    return 60.0 / max(float((song or {}).get("bpm", 120) or 120), 1.0)


# ===================================================== 009 SINGABILITY COURT
def court_singability(song, genre=""):
    rows = aligned(song)
    words = [r for r in rows if not is_phoneme_token(r["word"])]
    if not words:
        return {"court": "singability", "ok": True,
                "skipped": "no word lyrics (hum or none)"}
    if _is_imported(song):
        return {"court": "singability", "ok": True,
                "skipped": "imported record (witness law)"}
    spb = _spb(song)
    flags = []
    for r in words:
        if r.get("melisma"):
            # melisma = one syllable riding MORE notes — the lawful
            # direction (REFFLY asymmetry); never a cram candidate
            continue
        if r["n_words"] > 1:      # LINE MODE: judge the phrase's rate
            syl = sum(syllables(w) or 1 for w in r["word"].split())
            sec = r["dur_beats"] * spb
            if sec < syl * SYL_MIN_S:
                flags.append({
                    "kind": "crammed_line", "word": r["word"],
                    "beat": r["beat"], "syllables": syl,
                    "window_s": round(sec, 3),
                    "why": f"line '{r['word'][:40]}' packs {syl} syllables "
                           f"into {sec:.2f}s — over the ~7.5 syl/s "
                           "articulation ceiling; give the phrase more "
                           "beats or fewer words"})
            continue
        syl = syllables(r["word"])
        if not syl or syl < 2:
            continue
        sec = r["dur_beats"] * spb
        if sec < syl * SYL_MIN_S:
            flags.append({
                "kind": "crammed_word", "word": r["word"], "beat": r["beat"],
                "syllables": syl, "window_s": round(sec, 3),
                "why": f"'{r['word']}' ({syl} syllables) on a "
                       f"{sec * 1000:.0f}ms window — under "
                       f"{syl}x{SYL_MIN_S * 1000:.0f}ms articulation floor "
                       "(REFFLY: multi-syllable on one short note = "
                       "unsingable; melisma is the LAWFUL direction)"})
    return {"court": "singability", "ok": not flags, "flags": flags,
            "words": len(words)}


def heal_singability(song, genre="", verdict=None):
    """Swap each crammed polysyllable for a MONOSYLLABLE from the same
    family bank (seeded by word+beat — deterministic). BANK-AUTHORED
    lyrics only (authorship guard). Mutates; returns edit ledger."""
    v = verdict or court_singability(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    if not bank_authored(song, genre):
        return []   # never rewrite a human's words
    try:
        import lyric_bank
        bank = [w for w in lyric_bank.bank_for(genre) if syllables(w) == 1]
    except Exception:
        return []
    if not bank:
        return []
    edits = []
    by_beat = {round(float(l.get("beat", 0)), 4): l
               for l in song.get("lyrics", []) or [] if isinstance(l, dict)}
    for f in v.get("flags", []):
        l = by_beat.get(round(float(f["beat"]), 4))
        if not l:
            continue
        h = int(hashlib.sha1(f"{f['word']}@{f['beat']}".encode()).hexdigest(), 16)
        new = bank[h % len(bank)]
        edits.append({"kind": "word_swap", "beat": f["beat"],
                      "old": l.get("text"), "new": new})
        l["text"] = new
    return edits


# ========================================================= 010 PROSODY COURT
def _prominent_note(rows, i):
    """Prominence per the research: strong grid beat (0/2 in 4/4) OR
    agogic (longer than both neighbors) OR local melodic peak."""
    r = rows[i]
    if (r["beat"] % 4.0) % 2.0 < 0.126:            # beats 0 and 2
        return True
    d = r["dur_beats"]
    dl = rows[i - 1]["dur_beats"] if i > 0 else 0
    dr = rows[i + 1]["dur_beats"] if i + 1 < len(rows) else 0
    if d > dl and d > dr:
        return True
    if r["note"] is not None:
        p = float(r["note"].get("pitch", 0))
        pl = float(rows[i - 1]["note"].get("pitch", p)) \
            if i > 0 and rows[i - 1]["note"] else p - 1
        pr = float(rows[i + 1]["note"].get("pitch", p)) \
            if i + 1 < len(rows) and rows[i + 1]["note"] else p - 1
        if p > pl and p > pr:
            return True
    return False


def prosody_score(song):
    """Fraction of CONTENT words landing on PROMINENT notes (the metric
    the 0.80 corpus floor speaks about). Single-word entries only — a
    LINE's internal stresses need phoneme alignment we don't have."""
    rows = aligned(song)
    rows = [r for r in rows
            if not is_phoneme_token(r["word"]) and r["n_words"] == 1]
    content_idx = [i for i, r in enumerate(rows) if is_content(r["word"])]
    if len(content_idx) < 6:
        return None
    hits = sum(1 for i in content_idx if _prominent_note(rows, i))
    return hits / len(content_idx)


def court_prosody(song, genre=""):
    """Two-tier by AUTHORSHIP (corpus law): bank lyrics convict below the
    0.80 literature floor (the swap heal can act); user lyrics convict
    only below 0.55 (under every real corpus take) and whisper between."""
    if _is_imported(song):
        return {"court": "prosody", "ok": True,
                "skipped": "imported record (witness law)"}
    s = prosody_score(song)
    if s is None:
        return {"court": "prosody", "ok": True,
                "skipped": "too few single-word content entries to score"}
    bank = bank_authored(song, genre)
    hard = PROMINENCE_FLOOR if bank else PROSODY_HARD_USER
    flags, advisories = [], []
    if s < hard:
        flags.append({"kind": "weak_prosody", "score": round(s, 3),
                      "floor": hard,
                      "why": f"only {s:.0%} of meaning-bearing words land "
                             "on prominent notes (strong beat / long / "
                             "peak) vs the ~80% human-corpus law — the "
                             "words fight the melody"})
    elif s < PROMINENCE_FLOOR:
        advisories.append({
            "kind": "prosody_below_ideal", "score": round(s, 3),
            "why": f"{s:.0%} of content words sit on prominent notes "
                   "(human corpus ~80%) — consider moving key words onto "
                   "downbeats / long notes"})
    return {"court": "prosody", "ok": not flags, "flags": flags,
            "advisories": advisories, "score": round(s, 3),
            "bank_authored": bank}


def heal_prosody(song, genre="", verdict=None):
    """Swap strong-beat FUNCTION words with nearby weak-beat CONTENT words
    (<= 2 beats away). Word set preserved; placement healed. BANK-AUTHORED
    only. Iterates until the floor holds or no swap helps. Mutates."""
    v = verdict or court_prosody(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    if not bank_authored(song, genre):
        return []
    lyr = [l for l in song.get("lyrics", []) or [] if isinstance(l, dict)]
    edits = []
    for _round in range(12):
        rows = [r for r in aligned(song) if not is_phoneme_token(r["word"])]
        score = prosody_score(song)
        if score is None or score >= PROMINENCE_FLOOR:
            break
        prom = {i: _prominent_note(rows, i) for i in range(len(rows))}
        swap = None
        for i, r in enumerate(rows):
            if not prom[i] or is_content(r["word"]):
                continue
            for j, r2 in enumerate(rows):
                if prom[j] or not is_content(r2["word"]):
                    continue
                if abs(r2["beat"] - r["beat"]) <= 2.0:
                    swap = (r, r2)
                    break
            if swap:
                break
        if not swap:
            break
        a, b = swap
        la = next((l for l in lyr
                   if abs(float(l.get("beat", 0)) - a["beat"]) < 1e-6), None)
        lb = next((l for l in lyr
                   if abs(float(l.get("beat", 0)) - b["beat"]) < 1e-6), None)
        if not la or not lb:
            break
        la["text"], lb["text"] = lb["text"], la["text"]
        edits.append({"kind": "prosody_swap", "beats": [a["beat"], b["beat"]],
                      "now_strong": lb["text"], "now_weak": la["text"]})
    return edits


# ==================================================== 011 VOWEL-LENGTH COURT
def court_vowel_long(song, genre=""):
    """ADVISORY — F1 physics is real but meaning outranks: never convict
    a lyric for its vowel; whisper where a closed vowel meets a long+high
    note so the agent can prefer open-vowel words there next time."""
    rows = [r for r in aligned(song)
            if not is_phoneme_token(r["word"]) and r["note"] is not None]
    if len(rows) < 8:
        return {"court": "vowel_long", "ok": True,
                "skipped": "too few sung word-notes"}
    durs = sorted(r["dur_beats"] for r in rows)
    pitches = sorted(float(r["note"].get("pitch", 60)) for r in rows)
    long_edge = durs[int(len(durs) * 0.75)]
    high_edge = pitches[int(len(pitches) * 0.7)]
    advisories = []
    for r in rows:
        if r["dur_beats"] < long_edge or \
                float(r["note"].get("pitch", 60)) < high_edge:
            continue
        v = stressed_vowel(r["word"])
        if v in _CLOSED_VOWELS:
            advisories.append({
                "kind": "closed_vowel_long_note", "word": r["word"],
                "beat": r["beat"], "vowel": v,
                "why": f"'{r['word']}' ({v}) sustains a long high note — "
                       "closed vowels' low F1 cannot track 2f0 up there "
                       "(belting physics); an open-vowel word carries "
                       "better"})
    return {"court": "vowel_long", "ok": True,
            "advisories": advisories[:6]}


# ======================================================= 062 SONG-FORM COURT
def _section_words(song):
    """words per section instance: [(name, [words...]), ...] in order."""
    secs = sorted((s for s in (song or {}).get("sections", []) or []
                   if isinstance(s, dict)),
                  key=lambda s: float(s.get("startBar", 0)))
    if not secs:
        return []
    lyr = sorted((l for l in (song or {}).get("lyrics", []) or []
                  if isinstance(l, dict)), key=lambda l: float(l.get("beat", 0)))
    out = []
    for i, s in enumerate(secs):
        b0 = float(s.get("startBar", 0)) * 4.0
        b1 = float(secs[i + 1].get("startBar", 0)) * 4.0 \
            if i + 1 < len(secs) else float("inf")
        ws = [str(l.get("text", "")) for l in lyr
              if b0 <= float(l.get("beat", 0)) < b1
              and not is_phoneme_token(l.get("text"))]
        out.append((str(s.get("name", "")).lower(), b0, b1, ws))
    return out


def _sim(a, b):
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    same = sum(1 for x, y in zip(a[:n], b[:n]) if x.lower() == y.lower())
    return same / max(len(a), len(b))


_HOOKISH = ("chorus", "drop", "hook", "theme")


def court_form(song, genre=""):
    if _is_imported(song):
        return {"court": "form", "ok": True,
                "skipped": "imported record (witness law)"}
    secs = _section_words(song)
    hooks = [s for s in secs if any(h in s[0] for h in _HOOKISH) and s[3]]
    verses = [s for s in secs if "verse" in s[0] and s[3]]
    if len(hooks) < 2 and len(verses) < 2:
        return {"court": "form", "ok": True,
                "skipped": "needs repeated sections with words"}
    flags, advisories = [], []
    for i in range(1, len(hooks)):
        s = _sim(hooks[0][3], hooks[i][3])
        if s < CHORUS_SIM_FLOOR:
            flags.append({"kind": "chorus_drift", "instance": i + 1,
                          "similarity": round(s, 3),
                          "why": f"chorus {i + 1} sings {s:.0%} of chorus 1's "
                                 "words — the hook is lyric-INVARIANT "
                                 "(verbatim repeats build identity)"})
        elif s < CHORUS_SIM_IDEAL:
            advisories.append({
                "kind": "chorus_variance", "instance": i + 1,
                "similarity": round(s, 3),
                "why": f"chorus {i + 1} varies {1 - s:.0%} from chorus 1 — "
                       "fine as intentional final-chorus lift; drift if "
                       "unintended"})
    for i in range(1, len(verses)):
        s = _sim(verses[0][3], verses[i][3])
        if s > VERSE_SIM_CEIL:
            advisories.append({
                "kind": "verse_clone", "instance": i + 1,
                "similarity": round(s, 3),
                "why": f"verse {i + 1} repeats {s:.0%} of verse 1 — verses "
                       "advance the story; new scene each pass"})
    return {"court": "form", "ok": not flags, "flags": flags,
            "advisories": advisories}


def heal_form(song, genre="", verdict=None):
    """Re-land chorus 1's words verbatim on later chorus instances
    (note-count aware: reuse by position). The hook-line law, court-side.
    Safe for ANY authorship — it copies the song's OWN chorus. Mutates."""
    v = verdict or court_form(song, genre)
    if v.get("ok", True) or v.get("skipped"):
        return []
    secs = _section_words(song)
    hooks = [s for s in secs if any(h in s[0] for h in _HOOKISH) and s[3]]
    if len(hooks) < 2:
        return []
    first = hooks[0][3]
    lyr = sorted((l for l in song.get("lyrics", []) or []
                  if isinstance(l, dict)), key=lambda l: float(l.get("beat", 0)))
    edits = []
    for name, b0, b1, ws in hooks[1:]:
        slot = [l for l in lyr if b0 <= float(l.get("beat", 0)) < b1
                and not is_phoneme_token(l.get("text"))]
        changed = 0
        for k, l in enumerate(slot):
            want = first[k % len(first)]
            if str(l.get("text", "")) != want:
                l["text"] = want
                changed += 1
        if changed:
            edits.append({"kind": "chorus_reland", "section": name,
                          "at_bar": b0 / 4.0, "words_changed": changed})
    return edits


# ================================================ 198 MELISMA POLICY COURT
_MELISMATIC = ("gospel", "soul", "rnb", "r_b", "motown", "doo_wop",
               "doowop")
_SYLLABIC = ("rap", "drill", "grime", "trap", "phonk", "hiphop", "hip_hop",
             "boombap", "memphis")


def court_melisma(song, genre=""):
    """r-10 f7: melisma is a TRIPARTITE, genre-diagnostic control —
    pop-rock defaults syllabic (<=20% words on >1 note), gospel/soul/R&B
    SANCTION runs (>4 notes/syllable on hook/cadence syllables).
    ADVISORY both ways (performance taste; the emitter already follows
    policy — this court catches imports/hand edits drifting off-genre)."""
    rows = [r for r in aligned(song)
            if not is_phoneme_token(r["word"]) and r["n_words"] == 1]
    if len(rows) < 8:
        return {"court": "melisma", "ok": True, "skipped": "too few words"}
    if _is_imported(song):
        return {"court": "melisma", "ok": True,
                "skipped": "imported record (witness law)"}
    n_mel = sum(1 for r in rows if r["melisma"])
    frac = n_mel / len(rows)
    longest = max((r["melisma"] for r in rows), default=0)
    g = str(genre or "").lower()
    advisories = []
    if any(k in g for k in _SYLLABIC) and n_mel:
        advisories.append({
            "kind": "melisma_offstyle", "frac": round(frac, 2),
            "why": f"{n_mel} melisma runs in a syllabic genre — rap "
                   "families speak in rhythm; runs read off-style"})
    elif any(k in g for k in _MELISMATIC) and n_mel == 0:
        advisories.append({
            "kind": "melisma_missing",
            "why": "no melisma runs in a run-culture genre — gospel/"
                   "soul/R&B place 4-9-note runs on hook and cadence "
                   "syllables (r-10 Grove taxonomy)"})
    elif frac > 0.2 and not any(k in g for k in _MELISMATIC):
        advisories.append({
            "kind": "melisma_heavy", "frac": round(frac, 2),
            "why": f"{frac:.0%} of words carry runs vs the ~20% "
                   "syllabic-default ceiling"})
    return {"court": "melisma", "ok": True, "advisories": advisories,
            "frac": round(frac, 3), "longest_run": longest}


# ====================================== 126 INTELLIGIBILITY RISK (composite)
def intelligibility_risk(song, genre=""):
    """Pre-render composite: fraction of sung words at intelligibility
    risk — crammed (singability flags), closed-vowel-on-long-high
    (vowel court advisories), or inside heavy melisma (>4-note runs
    blur text; r-11). Returns {risk, parts} — advisory-grade signal the
    sing lane can read BEFORE spending a render."""
    rows = [r for r in aligned(song)
            if not is_phoneme_token(r["word"]) and r["n_words"] == 1]
    if not rows:
        return {"risk": 0.0, "parts": {}, "words": 0}
    sv = court_singability(song, genre)
    vv = court_vowel_long(song, genre)
    crammed = len(sv.get("flags", [])) if not sv.get("skipped") else 0
    closed = len(vv.get("advisories", [])) if not vv.get("skipped") else 0
    heavy_mel = sum(1 for r in rows if r["melisma"] > 4)
    n = len(rows)
    risk = min(1.0, (crammed + closed + heavy_mel) / n)
    return {"risk": round(risk, 3), "words": n,
            "parts": {"crammed": crammed, "closed_vowel_high": closed,
                      "heavy_melisma": heavy_mel}}


# ---------------------------------------------------------------- aggregate
# W66 (r-10 item 197): per-genre syllable budgets — SOFT targets +-2
# (Pattison: deliberate line-length variation is a spotlight, so a few
# outliers NEVER flag; the court speaks only when >40% of lines breach).
# Bar-metered genres stage one entry per bar-phrase (the bank's
# convention), so 'line' counts serve both.
SYLLABLE_BUDGETS = {
    "pop": (6, 10), "country": (7, 9), "rnb": (6, 10), "rock": (6, 10),
    "rap": (10, 13), "hiphop": (10, 13), "hip_hop": (10, 13),
    "boom_bap": (8, 12), "trap": (6, 10), "drill": (5, 9),
    "uk_drill": (5, 9), "folk": (7, 11), "soul": (6, 10),
}


def syllable_budget(genre):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    for k, v in SYLLABLE_BUDGETS.items():
        if k in g:
            return v
    return None


def court_syllable_budget(song, genre=""):
    bud = syllable_budget(genre)
    if bud is None:
        return {"court": "syllable_budget", "ok": True, "advisories": [],
                "skipped": "no budget for genre"}
    lo, hi = bud
    lines = [str(l.get("text", "")) for l in
             (song or {}).get("lyrics", []) or []
             if isinstance(l, dict) and
             len(str(l.get("text", "")).split()) > 1 and
             not is_phoneme_token(l.get("text"))]
    if len(lines) < 4:
        return {"court": "syllable_budget", "ok": True, "advisories": [],
                "skipped": "too few lines"}
    counts = [sum(syllables(w) for w in ln.split()) for ln in lines]
    over = sum(1 for c in counts if c > hi + 2)
    under = sum(1 for c in counts if c < lo - 2)
    advisories = []
    frac = (over + under) / len(counts)
    if frac > 0.4:
        advisories.append({
            "kind": "syllable_budget", "lines": len(counts),
            "over": over, "under": under, "window": [lo, hi],
            "why": (f"{over + under}/{len(counts)} lines sit outside the "
                    f"genre's syllable budget ({lo}-{hi} +-2 tolerance) — "
                    "a few outliers are spotlights; this many reads as "
                    f"{'cramming' if over >= under else 'thin lines'}; "
                    "the melody should offer that many notes, the bank "
                    "should request that many words")})
    return {"court": "syllable_budget", "ok": True,
            "advisories": advisories,
            "median": sorted(counts)[len(counts) // 2]}


def court_lyrics(song, genre="", heal=False):
    lyr = [l for l in (song or {}).get("lyrics", []) or []
           if isinstance(l, dict) and not is_phoneme_token(l.get("text"))]
    if not lyr:
        return {"ok": True, "skipped": "no word lyrics"}
    out = {"singability": court_singability(song, genre),
           "prosody": court_prosody(song, genre),
           "vowel_long": court_vowel_long(song, genre),
           "form": court_form(song, genre),
           "melisma": court_melisma(song, genre)}
    try:                       # wave 41: the rhyme court (advisory)
        import rhyme_court
        out["rhyme"] = rhyme_court.court_rhyme(song, genre)
        cv = rhyme_court.court_closure(song, genre)   # w66 (199)
        if cv.get("advisories"):
            out["closure"] = cv
    except Exception:
        pass
    sb = court_syllable_budget(song, genre)           # w66 (197)
    if sb.get("advisories"):
        out["syllable_budget"] = sb
    out["intelligibility"] = intelligibility_risk(song, genre)
    if heal:
        heals = {}
        if not out["singability"].get("ok", True):
            heals["singability"] = heal_singability(song, genre,
                                                    out["singability"])
            if heals["singability"]:
                out["singability_after"] = court_singability(song, genre)
        if not out["prosody"].get("ok", True):
            heals["prosody"] = heal_prosody(song, genre, out["prosody"])
            if heals["prosody"]:
                out["prosody_after"] = court_prosody(song, genre)
        if not out["form"].get("ok", True):
            heals["form"] = heal_form(song, genre, out["form"])
            if heals["form"]:
                out["form_after"] = court_form(song, genre)
        out["heals"] = {k: v for k, v in heals.items() if v}
    out["ok"] = all(v.get("ok", True) for k, v in out.items()
                    if isinstance(v, dict) and not k.endswith("_after"))
    return out


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description="THE LYRIC COURTS (wave 17)")
    ap.add_argument("song")
    ap.add_argument("--genre", default="")
    ap.add_argument("--heal", action="store_true")
    args = ap.parse_args()
    song = json.load(open(args.song))
    v = court_lyrics(song, args.genre, heal=args.heal)
    if args.heal and v.get("heals"):
        with open(args.song, "w") as f:
            json.dump(song, f, indent=1)
        v["saved"] = args.song
    print(json.dumps(v, indent=1))
    return 0 if v["ok"] or args.heal else 1


if __name__ == "__main__":
    sys.exit(main())
