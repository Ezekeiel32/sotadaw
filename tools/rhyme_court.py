#!/usr/bin/env python3
"""THE RHYME COURT — rhyme density and scheme as measurable craft
(wave 41; R-10 item 124).

Raplyzer (Malmi et al.): the RHYME FACTOR = the average length of the
longest matching VOWEL sequence per word, assonance-based, ignoring
word boundaries, within a 15-word window, counting matches of >= 2
vowels. Elite rappers measure 1.15-1.19; the metric ranks rappers above
classical poets. Vowels come from the same CMU lexicon the lyric courts
already trust (one resolver); OOV words fall back to grapheme vowels.

  vowel_stream(word)        CMU vowel phones (stress stripped)
  rhyme_factor(words)       the Raplyzer number over a word list
  scheme_of(lines)          end-rhyme letters per line (AABB/ABAB...)
  court_rhyme(song, genre)  ADVISORY-only: rap families under their
                            measured floor read prose-flat; hook lines
                            that never end-rhyme read unresolved
                            (Pattison closure). Floors are SELF-MEASURED
                            from the bank (see calibration note below).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_RAP = ("rap", "hiphop", "hip_hop", "trap", "drill", "grime", "boombap",
        "memphis", "phonk")
WINDOW = 15
MIN_MATCH = 2


def vowel_stream(word):
    import lyric_court as LC
    if LC.is_phoneme_token(word):
        return []
    cmu, _ = LC._lex()
    prons = cmu.get(LC._clean(word))
    if prons:
        return [p[:-1] if p[-1].isdigit() else p
                for p in prons[0] if p[-1].isdigit()]
    return re.findall(r"[aeiouy]+", LC._clean(word))


def _longest_suffix_match(v, prev_streams):
    """Longest common vowel SUFFIX of v against any window stream."""
    best = 0
    for u in prev_streams:
        k = 0
        while k < min(len(v), len(u)) and v[-1 - k] == u[-1 - k]:
            k += 1
        best = max(best, k)
    return best


def rhyme_factor(words):
    """The Raplyzer number: mean longest >=2-vowel suffix match per
    word vs its 15-word lookback."""
    streams = [vowel_stream(w) for w in words]
    scores = []
    for i, v in enumerate(streams):
        if not v:
            continue
        window = [u for u in streams[max(0, i - WINDOW):i] if u]
        if not window:
            continue
        m = _longest_suffix_match(v, window)
        scores.append(m if m >= MIN_MATCH else 0)
    return round(sum(scores) / len(scores), 3) if scores else 0.0


def end_sound(word):
    """Phones from the LAST vowel onward (rain -> EY N): the perfect-
    rhyme unit — scheme detection needs single-vowel rhymes too."""
    import lyric_court as LC
    cmu, _ = LC._lex()
    prons = cmu.get(LC._clean(word))
    if not prons:
        m = re.search(r"[aeiouy]+[^aeiouy]*$", LC._clean(word))
        return [m.group(0)] if m else []
    phones = [p[:-1] if p[-1].isdigit() else p for p in prons[0]]
    vowel_idx = [i for i, p in enumerate(prons[0]) if p[-1].isdigit()]
    return phones[vowel_idx[-1]:] if vowel_idx else []


def scheme_of(lines):
    """End-rhyme letters per line (AABB / ABAB read straight off) —
    judged on end_sound (last vowel + coda), so rain/pain rhyme."""
    ends = [end_sound(str(ln).split()[-1]) if str(ln).split() else []
            for ln in lines]
    letters = []
    for i, v in enumerate(ends):
        found = None
        for j in range(i):
            if v and ends[j] and v == ends[j]:
                found = letters[j]
                break
        if found is None:
            found = chr(ord("A") + len(set(letters)))
        letters.append(found)
    return "".join(letters)


# SELF-MEASURED (2026-07-15): the kernel is FAITHFUL Raplyzer — a
# multis detector (cat/hat scores 0 by design; elite corpora 1.15+).
# THE BANK'S OWN rap verses measure 0.02 — a TRUE finding: MAKE's rap
# lyrics lack multi-syllable chains (the bank upgrade is the named
# follow-up). The advisory floor sits where real rap craft begins;
# firing on bank output is honest — it tells the revising agent to
# densify multis.
RAP_FLOOR = 0.15


# W66 (r-10 item 199): the Pattison CLOSURE LADDER — rhyme type is a
# MEANING knob. Consonant classes for the family tier:
_C_CLASS = {"P": "plosive", "B": "plosive", "T": "plosive", "D": "plosive",
            "K": "plosive", "G": "plosive",
            "F": "fric", "V": "fric", "S": "fric", "Z": "fric",
            "SH": "fric", "ZH": "fric", "TH": "fric", "DH": "fric",
            "HH": "fric", "M": "nasal", "N": "nasal", "NG": "nasal",
            "L": "liquid", "R": "liquid", "CH": "affric", "JH": "affric",
            "W": "glide", "Y": "glide"}


def rhyme_tier(w1, w2):
    """perfect > family > assonance > none — the closure ladder rungs."""
    e1, e2 = end_sound(w1), end_sound(w2)
    if not e1 or not e2:
        return "none"
    import lyric_court as LC
    if LC._clean(w1) == LC._clean(w2):
        return "identity"                 # same word = not a rhyme
    if e1 == e2:
        return "perfect"
    if e1[0] == e2[0]:                    # same last vowel
        c1 = [_C_CLASS.get(p) for p in e1[1:] if p in _C_CLASS]
        c2 = [_C_CLASS.get(p) for p in e2[1:] if p in _C_CLASS]
        if c1 and c1 == c2:
            return "family"               # rain/game class: vowel + coda class
        return "assonance"
    return "none"


def court_closure(song, genre=""):
    """Resolved positions (hook/chorus section ENDS) want perfect or
    family rhyme — the 'answer' line closes. Verse bodies keep their
    slant freedom (destabilizing there is the tool, never a crime)."""
    lyr = [l for l in (song or {}).get("lyrics", []) or []
           if isinstance(l, dict) and
           len(str(l.get("text", "")).split()) > 1]
    secs = [s for s in (song or {}).get("sections", []) or []
            if isinstance(s, dict)]
    if len(lyr) < 4 or not secs:
        return {"court": "closure", "ok": True, "advisories": [],
                "skipped": "needs lines + sections"}
    import form_court as FCRT
    secs.sort(key=lambda s: float(s.get("startBar", 0)))
    end_bar = float((song or {}).get("lengthBars", 0) or 0)
    advisories = []
    for i, s in enumerate(secs):
        if FCRT._sec_class(s.get("name")) != "hook":
            continue
        a = float(s.get("startBar", 0)) * 4
        b = (float(secs[i + 1].get("startBar", end_bar)) * 4
             if i + 1 < len(secs) else end_bar * 4)
        inside = [l for l in lyr if a <= float(l.get("beat", 0)) < b]
        if len(inside) < 2:
            continue
        inside.sort(key=lambda l: float(l.get("beat", 0)))
        last = str(inside[-1].get("text", "")).split()[-1]
        prev = str(inside[-2].get("text", "")).split()[-1]
        tier = rhyme_tier(prev, last)
        if tier in ("assonance", "none"):
            advisories.append({
                "kind": "unresolved_closure", "section": s.get("name"),
                "pair": [prev, last], "tier": tier,
                "why": (f"'{s.get('name')}' closes on '{prev}/{last}' "
                        f"({tier}) — the chorus's final couplet is the "
                        "ANSWER line; Pattison's ladder wants perfect/"
                        "family rhyme at resolved positions (slant "
                        "belongs in verse bodies, where instability "
                        "is the tool)")})
    return {"court": "closure", "ok": True, "advisories": advisories}


def court_rhyme(song, genre=""):
    g = str(genre or "").lower().replace("-", "_").replace(" ", "_")
    import lyric_court as LC
    if LC._is_imported(song):
        return {"court": "rhyme", "ok": True, "advisories": [],
                "skipped": "imported record (witness law)"}
    words = [str(l.get("text", "")) for l in
             (song or {}).get("lyrics", []) or []
             if isinstance(l, dict)
             and not LC.is_phoneme_token(l.get("text"))
             and len(str(l.get("text", "")).split()) == 1]
    if len(words) < 16:
        return {"court": "rhyme", "ok": True, "advisories": [],
                "skipped": "too few sung words to measure"}
    rf = rhyme_factor(words)
    advisories = []
    if any(k in g for k in _RAP) and rf < RAP_FLOOR:
        advisories.append({
            "kind": "prose_flat", "rhyme_factor": rf,
            "why": f"rhyme factor {rf} sits under the rap-family floor "
                   f"({RAP_FLOOR}) — the words read as prose wearing "
                   "rap's name (elite corpora measure 1.15+; assonance "
                   "chains and multis raise it)"})
    return {"court": "rhyme", "ok": True, "advisories": advisories,
            "rhyme_factor": rf}


if __name__ == "__main__":
    import json
    import sys as _s
    song = json.load(open(_s.argv[1]))
    print(json.dumps(court_rhyme(song, _s.argv[2] if len(_s.argv) > 2
                                 else ""), indent=1))
