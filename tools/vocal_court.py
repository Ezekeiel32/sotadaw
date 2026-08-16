#!/usr/bin/env python3
"""THE VOCAL COURT (PRODUCER MIND P11, docs/SPEC_PRODUCER_MIND.md).

The words must be UNDERSTOOD — in every language. faster-whisper transcribes
the sung stem; word error rate vs the intended lyrics is the verdict. This is
the empirical judge of THE LANGUAGE RAIL (sing_lang.py): tables don't get to
claim intelligibility — the measured round-trip does.

  court_vocal(song_name, wav=None, lang=None) -> verdict dict
  wer(ref, hyp) -> word error rate (Levenshtein / len(ref))

Floors (bootstrap; R-11 research refines per language): WER <= 0.35 clean,
<= 0.55 flagged, above = red. Whisper degrades on singing vs speech — floors
are calibrated to the SUNG stem, and the stem (never the full mix) is judged.
Model: faster-whisper 'small' (multilingual, cached on this box).
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLAG_WER, RED_WER = 0.35, 0.55
# R-11 (researched 2026-07-14): Whisper on ISOLATED SUNG STEMS baselines —
# en 24.7-25.4% WER on commercial records (human listeners mishear ~25% of
# solo-sung words!), de ~13-16 (best), es ~18-20, fr ~25, ru ~39, it ~44
# (LyricWhiz polyphonic). Floors are per-language, calibrated to those.
LANG_FLOORS = {  # lang: (flag_wer, red_wer)
    "en": (0.35, 0.55), "de": (0.30, 0.50), "es": (0.35, 0.55),
    "fr": (0.40, 0.60), "pt": (0.40, 0.60), "it": (0.50, 0.70),
    "ru": (0.50, 0.70), "uk": (0.50, 0.70), "pl": (0.50, 0.70),
    "ja": (0.50, 0.75), "ko": (0.50, 0.75), "zh": (0.45, 0.70),
    "ar": (0.55, 0.75), "he": (0.60, 0.80), "th": (0.55, 0.75),
}

# WAVE 24 (item 012): floors AUTO-CALIBRATE on accepts — the literature
# seeds them, the user's accepted takes refine them (within bounds:
# flag may drift between the literature flag and red-0.05; red never
# moves — the literature red line is the hard law). Persisted overrides:
FLOORS_PATH = os.path.join(ROOT, "library", "vocal_floors.json")
_STOPWORDS = frozenset("""
a an the and or but if so of in on at to by with from as is am are was
were be do does did have has had will would can could it its this that i
you he she we they my your me him her us oh ooh yeah hey la na
""".split())


def calibrated_floors(lang):
    """Literature floors adjusted by persisted accept-calibration."""
    lit = LANG_FLOORS.get(str(lang or "en").lower(), (FLAG_WER, RED_WER))
    try:
        cal = json.load(open(FLOORS_PATH)).get(str(lang or "en").lower())
        if cal and "flag" in cal:
            # calibration may TIGHTEN (down to lit-0.1) or LOOSEN (up to
            # red-0.05); red itself never moves — the literature hard line
            flag = min(max(float(cal["flag"]), lit[0] - 0.1),
                       lit[1] - 0.05)
            return (round(flag, 3), lit[1])
    except Exception:
        pass
    return lit


def calibrate_floors(records):
    """PURE KERNEL: records = [{lang, wer, accepted}] from telemetry.
    Accepted takes define 'good enough': per language with >=4 accepts,
    flag' = p75(accepted wers) + 0.05, clamped inside
    [literature flag - 0.1, red - 0.05]. Returns the floors dict
    (caller persists to FLOORS_PATH)."""
    by_lang = {}
    for r in records or []:
        if not r.get("accepted") or r.get("wer") is None:
            continue
        by_lang.setdefault(str(r.get("lang") or "en").lower(), []).append(
            float(r["wer"]))
    out = {}
    for lang, wers in by_lang.items():
        if len(wers) < 4:
            continue
        wers.sort()
        p75 = wers[int(len(wers) * 0.75)]
        lit = LANG_FLOORS.get(lang, (FLAG_WER, RED_WER))
        flag = min(max(p75 + 0.05, lit[0] - 0.1), lit[1] - 0.05)
        out[lang] = {"flag": round(flag, 3), "n_accepts": len(wers),
                     "p75": round(p75, 3)}
    return out


def _soundex(w):
    """Classic Soundex — the deterministic phonetic tier (r-11: raw WER
    over-penalizes homophones; 'threw'~'through', 'burnin'~'burning')."""
    w = re.sub(r"[^a-z]", "", str(w).lower())
    if not w:
        return ""
    codes = {"b": "1", "f": "1", "p": "1", "v": "1",
             "c": "2", "g": "2", "j": "2", "k": "2", "q": "2", "s": "2",
             "x": "2", "z": "2", "d": "3", "t": "3", "l": "4",
             "m": "5", "n": "5", "r": "6"}
    out, prev = w[0].upper(), codes.get(w[0], "")
    for ch in w[1:]:
        c = codes.get(ch, "")
        if c and c != prev:
            out += c
        if ch not in "hw":
            prev = c
    return (out + "000")[:4]


def error_taxonomy(intended, heard):
    """W48 (item 127): ~75% of sung-word errors are CONSONANTS and ~1/3
    are vowel centralization on high notes — the heal order is fixed:
    consonants first, high-note vowels second, melisma third, language
    last. Greedy positional alignment; per-miss classification via the
    phonetic tiers already in this court."""
    misses = {"consonant_onset": 0, "vowel_center": 0, "missing": 0}
    got = list(heard)
    for w in intended:
        if w in _STOPWORDS or len(w) <= 2:
            continue
        if w in got:
            got.remove(w)
            continue
        # the nearest phonetic cousin among what WAS heard. Soundex
        # keys on the FIRST letter, so it is blind to exactly the
        # onset-error class this taxonomy exists for — the SUFFIX tier
        # sees golden/olden and fire/hire.
        sx = _soundex(w)
        cousin = next((h for h in got if _soundex(h) == sx), None)
        if cousin is None and len(w) >= 4:
            cousin = next((h for h in got if len(h) >= 4 and
                           w[-3:] == h[-3:]), None)
        if cousin is None:
            cousin = next(
                (h for h in got if len(h) > 3 and
                 abs(len(w) - len(h)) <= 1 and
                 sum(a != b for a, b in zip(w, h)) <= 2), None)
        if cousin is None:
            misses["missing"] += 1
            continue
        got.remove(cousin)
        if w[:1] != cousin[:1]:
            misses["consonant_onset"] += 1
        else:
            misses["vowel_center"] += 1
    plan = []
    if misses["consonant_onset"] or misses["missing"]:
        plan.append("1) consonants FIRST: raise consonant phoneme "
                    "duration/energy on the flagged onsets")
    if misses["vowel_center"]:
        plan.append("2) high-note vowels: transpose the phrase down or "
                    "re-voice toward open vowels")
    plan.append("3) shorten over-long melismas on flagged words")
    plan.append("4) verify the phoneme bank language matches the lyric")
    plan.append("re-render ONLY the flagged phrase (surgical)")
    return {"misses": misses, "heal_plan": plan}


def intelligibility(wer, recall, taxonomy=None):
    """W60 (r-11 item 125): the INTEGRATED score the amber zone deserves
    — raw WER punishes homophones and near-misses; recall alone misses
    word order; the taxonomy knows WHICH errors cost understanding
    (a missing word erases meaning; a consonant-onset slip usually
    keeps it; r-11: ~75% of sung-word errors are consonants and
    listeners still follow). 0..1, higher = understood.

      I = 0.50*recall + 0.35*(1 - wer) + 0.15*error_quality
    where error_quality weighs the miss mix: missing words cost full,
    onset slips cost little, vowel-center slips sit between."""
    if recall is None or wer is None:
        return None
    base = 0.50 * max(min(float(recall), 1.0), 0.0)         + 0.35 * (1.0 - max(min(float(wer), 1.0), 0.0))
    quality = 1.0
    m = (taxonomy or {}).get("misses") or {}
    total = sum(m.values())
    if total:
        cost = (m.get("missing", 0) * 1.0
                + m.get("vowel_center", 0) * 0.45
                + m.get("consonant_onset", 0) * 0.2) / total
        quality = 1.0 - cost
    return round(base + 0.15 * quality, 3)


def content_recall(intended, heard):
    """Amber-zone rescue (item 012's integrated-metric DETERMINISTIC
    core): order-free recall of stopword-excluded content words, with a
    phonetic tier — exact match OR edit-distance<=1 OR Soundex-equal
    counts (sung 'burnin' IS 'burning'; 'threw' IS 'through')."""
    want = [w for w in intended if w not in _STOPWORDS and len(w) > 2]
    if not want:
        return None
    got = set(heard)
    got_sx = {_soundex(w) for w in heard}

    def hit(w):
        if w in got:
            return True
        if _soundex(w) in got_sx:
            return True
        return any(len(w) > 3 and abs(len(w) - len(h)) <= 1 and
                   sum(a != b for a, b in zip(w, h)) <= 1
                   for h in got if h)
    return round(sum(1 for w in want if hit(w)) / len(want), 3)


def _norm_words(text, lang=""):
    """Casefold, strip punctuation/diacritic noise, split — melisma-aware
    callers pass the lyric words themselves (one entry per word)."""
    t = unicodedata.normalize("NFKC", str(text or "")).casefold()
    t = re.sub(r"[^\w\s']", " ", t, flags=re.UNICODE)
    return [w for w in t.split() if w and not w.startswith("@")]


def wer(ref_words, hyp_words):
    """Word error rate: Levenshtein(ref, hyp) / len(ref). 0.0 = perfect."""
    r, h = list(ref_words), list(hyp_words)
    if not r:
        return 0.0 if not h else 1.0
    prev = list(range(len(h) + 1))
    for i, rw in enumerate(r, 1):
        cur = [i] + [0] * len(h)
        for j, hw in enumerate(h, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1,
                         prev[j - 1] + (rw != hw))
        prev = cur
    return prev[-1] / len(r)


def cer(ref_words, hyp_words):
    """Character error rate — the fairer cross-language metric (inflection
    misses like ночи/ночь cost 1 char, not a whole word; melisma-stretched
    vowels normalize away). Verdict metric for non-space-poor languages."""
    r, h = " ".join(ref_words), " ".join(hyp_words)
    if not r:
        return 0.0 if not h else 1.0
    prev = list(range(len(h) + 1))
    for i, rc in enumerate(r, 1):
        cur = [i] + [0] * len(h)
        for j, hc in enumerate(h, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (rc != hc))
        prev = cur
    return prev[-1] / len(r)


def transcribe(wav, lang=None, model_size="small"):
    """Sung stem -> text via faster-whisper (language-hinted)."""
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="auto", compute_type="auto")
    kw = {"language": lang} if lang and lang not in ("auto", "he-bridge") else {}
    segments, info = model.transcribe(wav, beam_size=5, vad_filter=False, **kw)
    text = " ".join(s.text.strip() for s in segments)
    return text, getattr(info, "language", lang)


def court_vocal(song_name, wav=None, lang=None, model_size="small"):
    """Verdict on the sung take: WER vs intended lyrics[] on the vocal stem."""
    sj = os.path.join(ROOT, "songs", f"{song_name}.json")
    song = json.load(open(sj))
    lyr = song.get("lyrics") or []
    intended = _norm_words(" ".join(str(l.get("text", "")) for l in lyr))
    if not intended:
        return {"court": "vocal", "ok": True, "skipped": "no lyrics staged"}
    wav = wav or os.path.join(ROOT, "songs", f"{song_name}_vocal.wav")
    if not os.path.exists(wav):
        return {"court": "vocal", "ok": False, "red": True,
                "why": f"no sung stem at {os.path.basename(wav)} "
                       "(vocal_gap class: lyrics staged, nothing sings)"}
    lang = lang or song.get("lyrics_lang")
    heard_text, det_lang = transcribe(wav, lang, model_size)
    heard = _norm_words(heard_text)
    w, c = wer(intended, heard), cer(intended, heard)
    # judge on the KINDER of the two (word for analytic langs, char for
    # inflected/agglutinative), against ACCEPT-CALIBRATED per-lang floors
    flag_w, red_w = calibrated_floors(lang or det_lang or "en")
    red = w > red_w and c > 0.45
    clean = w <= flag_w or c <= 0.25
    verdict = "clean" if clean else ("red" if red else "flagged")
    recall = None
    tax = None
    if verdict in ("flagged", "red") or not (w <= flag_w or c <= 0.25):
        tax = error_taxonomy(intended, heard)
    # W67 (r-11 item 200): THE LENGTH GUARD — one wrong word in a
    # 5-word hook is 20% WER noise, not a verdict. RED needs >=15
    # lexical words of evidence; short takes downgrade to flagged with
    # low_confidence. (The prompt-cheat guard is STRUCTURAL: transcribe()
    # never passes initial_prompt/reference lyrics into the decode —
    # battery-asserted so it can't quietly return.)
    low_confidence = False
    if verdict == "red" and len(intended) < 15:
        verdict = "flagged"
        low_confidence = True
    intel = None
    if verdict == "flagged":
        # W60 (item 125): the amber band escalates to the INTEGRATED
        # intelligibility score — recall carries meaning, WER carries
        # precision, the taxonomy prices the error mix. Partial
        # intelligibility is scored fairly instead of coin-flipped on
        # one metric.
        recall = content_recall(intended, heard)
        intel = intelligibility(w, recall, tax)
        if intel is not None and intel >= 0.62:
            verdict = "clean_by_content"
        elif recall is not None and recall >= 0.7 and intel is None:
            verdict = "clean_by_content"
    return {"court": "vocal", "ok": not red, "verdict": verdict,
            "wer": round(w, 3), "cer": round(c, 3), "lang": lang or det_lang,
            "detected_lang": det_lang,
            **({"content_recall": recall} if recall is not None else {}),
            **({"intelligibility": intel} if intel is not None else {}),
            **({"low_confidence": True} if low_confidence else {}),
            **({"taxonomy": tax} if tax else {}),
            "intended_words": len(intended),
            "heard": heard_text[:200],
            "intended": " ".join(intended)[:200]}


def main():
    import argparse
    ap = argparse.ArgumentParser(description="THE VOCAL COURT (P11)")
    ap.add_argument("song", nargs="?")
    ap.add_argument("--wav", default=None)
    ap.add_argument("--lang", default=None)
    ap.add_argument("--model", default="small")
    ap.add_argument("--calibrate", action="store_true",
                    help="refresh library/vocal_floors.json from accepted "
                         "takes' measured WERs in telemetry (item 012)")
    args = ap.parse_args()
    if args.calibrate:
        records = []
        try:
            for line in open(os.path.join(ROOT, "telemetry",
                                          "proposals.jsonl")):
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("wer") is not None:
                    records.append({"lang": r.get("lang") or
                                    r.get("lyrics_lang") or "en",
                                    "wer": r.get("wer"),
                                    "accepted": r.get("verdict") == "accept"
                                    or r.get("accepted")})
        except FileNotFoundError:
            pass
        floors = calibrate_floors(records)
        os.makedirs(os.path.dirname(FLOORS_PATH), exist_ok=True)
        json.dump(floors, open(FLOORS_PATH, "w"), indent=1)
        print(json.dumps({"calibrated": floors,
                          "path": FLOORS_PATH}, indent=1))
        return 0
    if not args.song:
        ap.error("song required (or --calibrate)")
    v = court_vocal(args.song, args.wav, args.lang, args.model)
    print(json.dumps(v, ensure_ascii=False, indent=1))
    return 0 if v.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
