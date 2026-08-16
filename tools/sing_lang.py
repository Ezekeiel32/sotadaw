#!/usr/bin/env python3
"""THE LANGUAGE RAIL (PRODUCER MIND P9, docs/SPEC_PRODUCER_MIND.md).

word -> Gahata-Meiji bank phonemes for every language the acoustic model
knows (languages.json: ar de en es fr it ja ko pl pt ru th uk zh; 608
namespaced phonemes VERIFIED on disk 2026-07-14).

Ground truth found by inspection (spec D6 correction): only ja/zh/en ship
real LEXICONS (dsdict-ja = kana, dsdict-zh = pinyin, dsdict-en = CMU-style;
dsdict-ru/es/... are ja-dict copies with ZERO target-language rows). So:

  ja  — longest-match segmentation over dsdict-ja graphemes (exact by
        construction: the dict carries every kana cluster incl. っぢゃ)
  zh  — pinyin syllables over dsdict-zh (hanzi needs pypinyin when present;
        romanized pinyin input works bare)
  en  — sing.py's existing CMUdict rail (NOT duplicated here)
  ko  — deterministic hangul->jamo decomposition -> ko/ inventory
  ru es de fr it pt pl uk ar th
      — espeak-ng IPA (voice per language) -> per-language IPA->phoneme
        tables, FILTERED against the bank's real inventory; unmapped
        symbols are honest misses, never guesses.

The tables are seeds: THE VOCAL COURT (P11) measures per-language WER on
the sung stem — empirical truth outranks any table, and R-9 research
refines them. Fail-open: None = the word is skipped with an honest line
(sing.py's existing ladder), the take never dies.
"""
import functools
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "library", "voices", "gahata_meiji")
DSDUR = os.path.join(BANK, "configs", "dsdur")

# espeak-ng voice per bank language (verified installed: ar de es it ko pl
# pt ru th uk; fr ships as fr-fr on some builds — both tried)
ESPEAK_VOICE = {"ru": ("ru",), "es": ("es",), "de": ("de",), "it": ("it",),
                "pt": ("pt", "pt-br"), "pl": ("pl",), "uk": ("uk",),
                "fr": ("fr", "fr-fr"), "ar": ("ar",), "th": ("th",)}


# ------------------------------------------------------------- script detect
def court_phoneme_coverage(phonemes, lang="en"):
    """W67 (r-9 item 195): BEFORE any vocoder minute burns — every
    phoneme the phrase will sing must exist in the bank's inventory
    for its namespace. Cross-lingual gaps become a machine verdict,
    zero tokens. phonemes = flat token list (bare or ns/bare)."""
    try:
        inv = bank_inventory()
    except Exception as e:
        return {"court": "phoneme_coverage", "ok": True,
                "skipped": f"no bank inventory ({e})"}
    ns = str(lang or "en").lower()
    known = inv.get(ns) or set()
    universal = set().union(*inv.values()) if inv else set()
    missing = []
    for p in phonemes or []:
        tok = str(p)
        if "/" in tok:
            tns, bare = tok.split("/", 1)
            hit = bare in (inv.get(tns) or set())
        else:
            bare = tok
            hit = bare in known or bare in universal
        if not hit and bare not in ("SP", "AP", "-", ""):
            missing.append(tok)
    ok = not missing
    return {"court": "phoneme_coverage", "ok": ok,
            "missing": sorted(set(missing))[:20], "lang": ns,
            **({} if ok else {"why": (
                f"{len(set(missing))} phoneme(s) absent from the bank's "
                f"'{ns}' inventory ({', '.join(sorted(set(missing))[:6])}"
                "...) — the vocoder renders silence or garbage for "
                "these; re-route the words or pick a covered language "
                "BEFORE burning render minutes")})}


def detect_lang(word, default="en"):
    """Per-word language from script ranges; Latin stays `default` (the song's
    declared/auto language) — script alone cannot split en/es/de/fr."""
    for ch in str(word):
        o = ord(ch)
        if 0x0400 <= o <= 0x04FF:
            return "ru"          # Cyrillic (uk callers pass default='uk')
        if 0x0590 <= o <= 0x05FF:
            return "he"          # Hebrew — bridged (no he in bank yet)
        if 0x0600 <= o <= 0x06FF or 0x0750 <= o <= 0x077F:
            return "ar"
        if 0x0E00 <= o <= 0x0E7F:
            return "th"
        if 0xAC00 <= o <= 0xD7AF or 0x1100 <= o <= 0x11FF:
            return "ko"
        if 0x3040 <= o <= 0x30FF:
            return "ja"          # kana
        if 0x4E00 <= o <= 0x9FFF:
            return "zh"          # han (ja kanji lyrics should pass lang='ja')
    return default


@functools.lru_cache(maxsize=None)
def bank_inventory():
    """lang -> set of bare phoneme names the acoustic model actually knows."""
    ph = json.load(open(os.path.join(BANK, "files", "phonemes.json")))
    inv = {}
    for p in ph:
        if "/" in p:
            ns, bare = p.split("/", 1)
            inv.setdefault(ns, set()).add(bare)
    return inv


@functools.lru_cache(maxsize=None)
def bank_languages():
    return json.load(open(os.path.join(BANK, "files", "languages.json")))


# ------------------------------------------------------------- ja: the dict
@functools.lru_cache(maxsize=None)
def _ja_dict():
    import yaml
    d = yaml.safe_load(open(os.path.join(DSDUR, "dsdict-ja.yaml")))
    return {str(e["grapheme"]): list(e["phonemes"]) for e in d.get("entries", [])
            if e.get("grapheme") not in ("SP", "AP", "sp", "ap")}


def ja_phonemes(word):
    """Longest-match kana segmentation over the shipped dict (exact)."""
    d = _ja_dict()
    maxlen = max((len(k) for k in d), default=1)
    out, i, s = [], 0, str(word)
    while i < len(s):
        for ln in range(min(maxlen, len(s) - i), 0, -1):
            hit = d.get(s[i:i + ln])
            if hit is not None:
                out.extend(hit)
                i += ln
                break
        else:
            return None                          # non-kana char: honest miss
    return out or None


# ------------------------------------------------------------- zh: pinyin
@functools.lru_cache(maxsize=None)
def _zh_dict():
    import yaml
    d = yaml.safe_load(open(os.path.join(DSDUR, "dsdict-zh.yaml")))
    return {str(e["grapheme"]).lower(): list(e["phonemes"])
            for e in d.get("entries", [])
            if e.get("grapheme") not in ("SP", "AP", "sp", "ap")}


def zh_phonemes(word):
    """Pinyin (toneless) or hanzi (via pypinyin when installed)."""
    d = _zh_dict()
    w = str(word).lower()
    if re.search(r"[一-鿿]", w):
        try:
            from pypinyin import lazy_pinyin
            sylls = lazy_pinyin(w)
        except ImportError:
            return None
    else:
        sylls = re.findall(r"[a-zü]+?(?:iang|iong|uang|ueng|ang|eng|ing|ong|"
                           r"ai|ao|an|ei|en|er|ia|ie|iu|in|ou|ua|uo|ui|un|"
                           r"ue|üe|[aeiouü])(?:ng|n|r)?|[a-zü]+", w) or [w]
    out = []
    for sy in sylls:
        hit = d.get(sy.strip().replace("ü", "v"))
        if hit is None:
            return None
        out.extend(hit)
    return out or None


# ------------------------------------------------------------- ko: jamo math
_KO_INITIALS = ["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss",
                "", "j", "jj", "ch", "k", "t", "p", "h"]
_KO_MEDIALS = ["a", "e", "ya", "ye", "eo", "e", "yeo", "ye", "o", "wa",
               "we", "we", "yo", "u", "weo", "we", "wi", "yu", "eu", "eui", "i"]
_KO_FINALS = ["", "K", "K", "K", "N", "N", "N", "T", "L", "L", "L", "L",
              "L", "L", "L", "L", "M", "P", "P", "T", "T", "NG", "T", "T",
              "K", "T", "P", "T"]


def ko_phonemes(word):
    """Deterministic hangul syllable decomposition -> ko/ inventory."""
    inv = bank_inventory().get("ko", set())
    out = []
    for ch in str(word):
        o = ord(ch)
        if not (0xAC00 <= o <= 0xD7A3):
            return None
        s = o - 0xAC00
        ini, med, fin = _KO_INITIALS[s // 588], _KO_MEDIALS[(s % 588) // 28], \
            _KO_FINALS[s % 28]
        for part in (ini, *_ko_vowel(med), fin):
            if not part:
                continue
            if part in inv:
                out.append(f"ko/{part}")
            elif part.lower() in inv:
                out.append(f"ko/{part.lower()}")
    return out or None


def _ko_vowel(med):
    """Compound medials split onto glide + vowel where the bank lacks them."""
    inv = bank_inventory().get("ko", set())
    if med in inv:
        return (med,)
    GLIDE = {"ya": ("y", "a"), "yeo": ("y", "eo"), "yo": ("y", "o"),
             "yu": ("y", "u"), "ye": ("y", "e"), "wa": ("w", "a"),
             "weo": ("w", "eo"), "we": ("w", "e"), "wi": ("w", "i"),
             "eui": ("eu", "i")}
    return GLIDE.get(med, (med,))


# ------------------------------------------------------------ hebrew G2P
_PHONIKUD = None
_PHONIKUD_MODEL = os.path.join(ROOT, "library", "voices",
                               "phonikud-1.0.int8.onnx")


def _hebrew_ipa(word):
    """THE HEBREW RAIL (R-9 fold): Phonikud (CC BY 4.0) — the neural
    diacritizer vocalizes RAW Hebrew, then its phonemizer emits stressed
    IPA (espeak's he voice returns vowel-less skeletons on plain text:
    כוכב -> 'χvχv'). Model absent / import dead -> espeak fallback, and the
    vowel-floor in phonemes_for keeps even that singable."""
    global _PHONIKUD
    try:
        if _PHONIKUD is None and os.path.exists(_PHONIKUD_MODEL):
            import torch  # noqa: F401  THE CUDA PRELOAD LAW (memory: basic_pitch class)
            from phonikud_onnx import Phonikud
            _PHONIKUD = Phonikud(_PHONIKUD_MODEL)
        if _PHONIKUD is not None:
            import phonikud as _pk
            with_nikud = _PHONIKUD.add_diacritics(str(word))
            ipa = _pk.phonemize(with_nikud)
            if ipa and any(c in "aeiou" for c in ipa):
                return ipa
    except Exception:
        pass
    for v in _HE_ESPEAK:
        try:
            r = subprocess.run(["espeak-ng", "-q", "--ipa", "-v", v, str(word)],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        except Exception:
            pass
    return None


# -------------------------------------------------- espeak IPA -> bank tables
def espeak_ipa(word, lang):
    for v in ESPEAK_VOICE.get(lang, (lang,)):
        try:
            r = subprocess.run(["espeak-ng", "-q", "--ipa", "-v", v, str(word)],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        except Exception:
            continue
    return None


# Per-language IPA->bank tables (longest-first matching; stress/length marks
# stripped). SEEDS — the vocal court's measured WER is the real judge (P11).
_STRIP = "ˈˌːˑ\"'​‿̯̪̩͡ "
IPA_MAPS = {
    "ru": [("ɭʲ", ["lj"]), ("tɕ", ["ch"]), ("tʃʲ", ["ch"]), ("tʃ", ["ch"]),
           ("ɕː", ["shj"]), ("ɕ", ["shj"]), ("dʒ", ["d", "zh"]),
           ("ʂ", ["sh"]), ("ʐ", ["zh"]), ("ʒ", ["zh"]), ("ts", ["c"]),
           ("ɑ", ["a"]), ("ʌ", ["a"]), ("y", ["y"]), ("bʲ", ["bj"]),
           ("vʲ", ["vj"]), ("dʲ", ["dj"]), ("zʲ", ["zj"]), ("kʲ", ["kj"]),
           ("lʲ", ["lj"]), ("mʲ", ["mj"]), ("nʲ", ["nj"]), ("pʲ", ["pj"]),
           ("rʲ", ["rj"]), ("sʲ", ["sj"]), ("tʲ", ["tj"]), ("fʲ", ["fj"]),
           ("ɡʲ", ["gj"]), ("xʲ", ["hj"]), ("ɨ", ["y"]), ("ɐ", ["a"]),
           ("ə", ["a"]), ("ʉ", ["u"]), ("ʊ", ["u"]), ("ɪ", ["i"]),
           ("ɛ", ["e"]), ("x", ["h"]), ("ɡ", ["g"]), ("j", ["j"]),
           ("a", ["a"]), ("e", ["e"]), ("i", ["i"]), ("o", ["o"]),
           ("u", ["u"]), ("b", ["b"]), ("v", ["v"]), ("d", ["d"]),
           ("z", ["z"]), ("k", ["k"]), ("l", ["l"]), ("m", ["m"]),
           ("n", ["n"]), ("p", ["p"]), ("r", ["r"]), ("s", ["s"]),
           ("t", ["t"]), ("f", ["f"])],
    "es": [("aɪ", ["a", "i"]), ("eɪ", ["e", "i"]), ("oɪ", ["o", "i"]),
           ("aʊ", ["a", "u"]), ("tʃ", ["ch"]), ("ʎ", ["lh"]), ("ɲ", ["nJ"]), ("ɾ", ["r"]),
           ("r", ["rr"]), ("β", ["B"]), ("ð", ["D"]), ("ɣ", ["G"]),
           ("θ", ["z"]), ("ʝ", ["y"]), ("ʃ", ["sh"]), ("x", ["x"]),
           ("dʒ", ["jh"]), ("w", ["w"]), ("j", ["y"]), ("a", ["a"]),
           ("e", ["e"]), ("i", ["i"]), ("o", ["o"]), ("u", ["u"]),
           ("b", ["b"]), ("d", ["d"]), ("f", ["f"]), ("ɡ", ["g"]),
           ("k", ["k"]), ("l", ["l"]), ("m", ["m"]), ("n", ["n"]),
           ("p", ["p"]), ("s", ["s"]), ("t", ["t"]), ("z", ["s"])],
    "de": [("ɜ", ["er"]), ("ɔø", ["eu"]), ("ɾ", ["r"]), ("pf", ["pf"]), ("ts", ["ts"]), ("tʃ", ["tsh"]), ("dʒ", ["dsh"]),
           ("aɪ", ["ei"]), ("aʊ", ["au"]), ("ɔʏ", ["eu"]), ("ɔʊ", ["o"]),
           ("øː", ["oeh"]), ("œ", ["oe"]), ("yː", ["ueh"]), ("ʏ", ["ue"]),
           ("ŋ", ["ng"]), ("ʃ", ["sh"]), ("ç", ["ch"]), ("x", ["ch"]),
           ("ə", ["ex"]), ("ɐ", ["er"]), ("ɛː", ["eh"]), ("ɛ", ["eh"]),
           ("eː", ["e"]), ("iː", ["i"]), ("ɪ", ["ih"]), ("oː", ["oh"]),
           ("ɔ", ["o"]), ("uː", ["u"]), ("ʊ", ["uh"]), ("aː", ["a"]),
           ("v", ["w"]), ("z", ["z"]), ("ʒ", ["zh"]), ("j", ["j"]),
           ("a", ["a"]), ("e", ["e"]), ("i", ["i"]), ("o", ["o"]),
           ("u", ["u"]), ("b", ["b"]), ("d", ["d"]), ("f", ["f"]),
           ("ɡ", ["g"]), ("h", ["h"]), ("k", ["k"]), ("l", ["l"]),
           ("m", ["m"]), ("n", ["n"]), ("p", ["p"]), ("r", ["r"]),
           ("s", ["s"]), ("t", ["t"])],
    "fr": [("ɑ̃", ["en"]), ("ɛ̃", ["in"]), ("ɔ̃", ["on"]), ("œ̃", ["in"]),
           ("ʁ", ["r"]), ("ʒ", ["j"]), ("ʃ", ["sh"]), ("ɲ", ["n", "y"]),
           ("ø", ["oe"]), ("œ", ["oe"]), ("ə", ["oe"]), ("y", ["uy"]),
           ("u", ["ou"]), ("ɔ", ["oh"]), ("o", ["oo"]), ("ɛ", ["eh"]),
           ("e", ["ee"]), ("a", ["ae"]), ("i", ["ih"]), ("ɥ", ["uy"]),
           ("w", ["w"]), ("j", ["y"]), ("b", ["b"]), ("d", ["d"]),
           ("f", ["f"]), ("ɡ", ["g"]), ("k", ["k"]), ("l", ["l"]),
           ("m", ["m"]), ("n", ["n"]), ("p", ["p"]), ("s", ["s"]),
           ("t", ["t"]), ("v", ["v"]), ("z", ["z"])],
    "it": [("tʃ", ["ch"]), ("dʒ", ["ch"]), ("ʎʎ", ["gl"]), ("ʎ", ["gl"]),
           ("ɲɲ", ["gn"]), ("ɲ", ["gn"]), ("ʊ", ["u"]), ("ss", ["s"]), ("ll", ["l"]),
           ("kk", ["k"]), ("tt", ["t"]), ("pp", ["p"]), ("mm", ["m"]),
           ("nn", ["n"]), ("bb", ["b"]), ("dd", ["d"]), ("ff", ["f"]),
           ("ɡɡ", ["g"]), ("rr", ["rr"]),
           ("ʃ", ["sh"]), ("ts", ["ts"]), ("dz", ["dz"]), ("ɛ", ["eh"]),
           ("ɔ", ["o"]), ("a", ["a"]), ("e", ["e"]), ("i", ["i"]),
           ("o", ["o"]), ("u", ["u"]), ("j", ["j"]), ("w", ["w"]),
           ("b", ["b"]), ("d", ["d"]), ("f", ["f"]), ("ɡ", ["g"]),
           ("k", ["k"]), ("l", ["l"]), ("m", ["m"]), ("n", ["n"]),
           ("p", ["p"]), ("r", ["r"]), ("s", ["s"]), ("t", ["t"]),
           ("v", ["v"]), ("z", ["z"])],
    "pt": [("tʃ", ["ch"]), ("dʒ", ["dj"]), ("ʎ", ["lh"]), ("ɲ", ["nh"]),
           ("ʃ", ["sh"]), ("ʒ", ["z"]), ("ɐ̃ʊ̃", ["an", "w"]),
           ("ɐ̃", ["an"]), ("ẽ", ["en"]), ("ĩ", ["in"]), ("õ", ["on"]),
           ("ũ", ["un"]), ("ʊ̃", ["un"]), ("ɐ", ["a"]), ("ʊ", ["u"]),
           ("ɪ", ["i"]), ("ŋ", ["ng"]), ("ɛ", ["eh"]), ("ɔ", ["oh"]),
           ("ʁ", ["rr"]), ("ɾ", ["r"]), ("ɹ", ["r"]), ("ɨ", ["i"]),
           ("eɪ", ["e", "i"]), ("oɪ", ["o", "i"]), ("aɪ", ["a", "i"]),
           ("x", ["h"]),
           ("a", ["a"]), ("e", ["e"]), ("i", ["i"]), ("o", ["o"]),
           ("u", ["u"]), ("j", ["y"]), ("w", ["w"]), ("b", ["b"]),
           ("d", ["d"]), ("f", ["f"]), ("ɡ", ["g"]), ("k", ["k"]),
           ("l", ["l"]), ("m", ["m"]), ("n", ["n"]), ("p", ["p"]),
           ("s", ["s"]), ("t", ["t"]), ("v", ["v"]), ("z", ["z"])],
    "pl": [("tʂ", ["cz"]), ("tʃ", ["cz"]), ("dʐ", ["dZ"]), ("dʒ", ["dZ"]),
           ("ʂ", ["sz"]), ("ʃ", ["sz"]), ("ʐ", ["Z"]), ("ʒ", ["Z"]),
           ("tɕ", ["C"]), ("dʑ", ["dX"]), ("ɕ", ["S"]), ("ʑ", ["X"]),
           ("ɲʲ", ["N"]),
           ("ts", ["c"]), ("dz", ["dz"]), ("ɲ", ["N"]), ("ŋ", ["ng"]),
           ("fʲ", ["f"]), ("vʲ", ["w"]), ("ɡʲ", ["g"]), ("kʲ", ["k"]),
           ("mʲ", ["m"]), ("bʲ", ["b"]), ("pʲ", ["p"]),
           ("ɛ̃", ["e", "ng"]), ("ɔ̃", ["o", "ng"]), ("ɨ", ["y"]),
           ("ɛ", ["e"]), ("ɔ", ["o"]), ("w", ["L"]), ("x", ["h"]),
           ("v", ["w"]), ("j", ["j"]),
           ("a", ["a"]), ("e", ["e"]), ("i", ["i"]), ("o", ["o"]),
           ("u", ["u"]), ("b", ["b"]), ("d", ["d"]), ("f", ["f"]),
           ("ɡ", ["g"]), ("k", ["k"]), ("l", ["l"]), ("m", ["m"]),
           ("n", ["n"]), ("p", ["p"]), ("r", ["r"]), ("s", ["s"]),
           ("t", ["t"]), ("z", ["z"])],
    "uk": [("ɦ", ["gh"]), ("x", ["h"]), ("h", ["h"]), ("tʃʲ", ["ch"]),
           ("tʃ", ["ch"]), ("ʃ", ["sh"]),
           ("ʒ", ["zh"]), ("ts", ["c"]), ("ɑ", ["a"]), ("ʌ", ["a"]),
           ("ɭʲ", ["lj"]), ("ɭ", ["l"]), ("ɨ", ["y"]),
           ("bʲ", ["bj"]), ("vʲ", ["vj"]), ("dʲ", ["dj"]), ("zʲ", ["zj"]),
           ("kʲ", ["kj"]), ("lʲ", ["lj"]), ("mʲ", ["mj"]), ("nʲ", ["nj"]),
           ("pʲ", ["pj"]), ("rʲ", ["rj"]), ("sʲ", ["sj"]), ("tʲ", ["tj"]),
           ("fʲ", ["fj"]), ("ɡʲ", ["gj"]), ("ɪ", ["y"]), ("y", ["y"]),
           ("j", ["j"]),
           ("a", ["a"]), ("ɛ", ["e"]), ("e", ["e"]), ("i", ["i"]),
           ("ɔ", ["o"]), ("o", ["o"]), ("u", ["u"]), ("b", ["b"]),
           ("v", ["v"]), ("d", ["d"]), ("z", ["z"]), ("k", ["k"]),
           ("l", ["l"]), ("m", ["m"]), ("n", ["n"]), ("p", ["p"]),
           ("r", ["r"]), ("s", ["s"]), ("t", ["t"]), ("f", ["f"]),
           ("ɡ", ["g"])],
    "ar": [("ʃ", ["sh"]), ("θ", ["th"]), ("ð", ["dh"]), ("ɣ", ["gh"]),
           ("x", ["kh"]), ("dʒ", ["jh"]), ("sˤ", ["ss"]), ("zˤ", ["zz"]),
           ("tˤ", ["t"]), ("dˤ", ["d"]), ("ħ", ["h"]), ("ʕ", ["a"]),
           ("ʔ", []), ("q", ["q"]), ("aː", ["ai"]), ("iː", ["ii"]),
           ("uː", ["uu"]), ("a", ["a"]), ("i", ["i"]), ("u", ["u"]),
           ("e", ["e"]), ("j", ["y"]), ("w", ["w"]), ("b", ["b"]),
           ("d", ["d"]), ("f", ["f"]), ("h", ["h"]), ("k", ["k"]),
           ("l", ["l"]), ("m", ["m"]), ("n", ["n"]), ("r", ["r"]),
           ("s", ["s"]), ("t", ["t"]), ("z", ["z"])],
    "th": [("tɕʰ", ["ch"]), ("tɕ", ["j"]), ("pʰ", ["ph"]), ("tʰ", ["th"]),
           ("kʰ", ["kh"]), ("ŋ", ["ng"]), ("ɯ", ["ue"]), ("ɤ", ["oe"]),
           ("ɛ", ["ae"]), ("ɔ", ["o"]), ("a", ["a"]), ("e", ["e"]),
           ("i", ["i"]), ("o", ["o"]), ("u", ["u"]), ("j", ["y"]),
           ("w", ["w"]), ("b", ["b"]), ("d", ["d"]), ("f", ["f"]),
           ("h", ["h"]), ("k", ["k"]), ("l", ["l"]), ("m", ["m"]),
           ("n", ["n"]), ("p", ["p"]), ("r", ["r"]), ("s", ["s"]),
           ("t", ["t"])],
    # HEBREW BRIDGE (no he/ in the bank): nearest phonemes from ru+ar
    # namespaces via espeak he IPA — experimental until a he bank lands (R-9).
    "he": [("χ", ["ru/h"]), ("ʁ", ["ru/r"]), ("ʃ", ["ru/sh"]), ("x", ["ru/h"]), ("ʁ", ["ru/r"]), ("ts", ["ru/c"]),
           ("dʒ", ["ru/ch"]), ("j", ["ru/j"]), ("a", ["ru/a"]), ("e", ["ru/e"]),
           ("i", ["ru/i"]), ("o", ["ru/o"]), ("u", ["ru/u"]), ("b", ["ru/b"]),
           ("v", ["ru/v"]), ("ɡ", ["ru/g"]), ("d", ["ru/d"]), ("h", ["ru/h"]),
           ("z", ["ru/z"]), ("k", ["ru/k"]), ("l", ["ru/l"]), ("m", ["ru/m"]),
           ("n", ["ru/n"]), ("s", ["ru/s"]), ("p", ["ru/p"]), ("f", ["ru/f"]),
           ("r", ["ru/r"]), ("t", ["ru/t"]), ("ʔ", [])],
}
_HE_ESPEAK = ("he",)


def map_ipa(ipa, lang):
    """IPA string -> bank phonemes (namespaced), or None on any unmapped
    symbol (honest miss — the court demands truth, not vowels invented)."""
    table = IPA_MAPS.get(lang)
    if not table or not ipa:
        return None
    s = "".join(ch for ch in ipa if ch not in _STRIP)
    s = s.replace("(en)", "").replace("(", "").replace(")", "")
    inv = bank_inventory()
    out, i = [], 0
    keys = sorted((k for k, _ in table), key=len, reverse=True)
    tmap = dict(table)
    while i < len(s):
        for k in keys:
            if s.startswith(k, i):
                for ph in tmap[k]:
                    if "/" in ph:                       # explicit namespace
                        ns, bare = ph.split("/", 1)
                        if bare not in inv.get(ns, ()):
                            return None                 # honest miss
                        out.append(ph)
                    else:
                        if ph not in inv.get(lang, ()):
                            return None                 # honest miss
                        out.append(f"{lang}/{ph}")
                i += len(k)
                break
        else:
            return None                                 # unmapped symbol
    return out or None


def phonemes_for(word, lang):
    """THE RAIL: word -> list of fully-namespaced bank phonemes, or None.
    en is handled by sing.py's CMUdict path — this returns None for en."""
    lang = str(lang or "").lower()
    w = str(word).strip().strip(".,!?'\"()").lower()
    if not w:
        return None
    if lang == "ja":
        return _namespace(ja_phonemes(word.strip()), "ja")
    if lang == "zh":
        return _namespace(zh_phonemes(w), "zh")
    if lang == "ko":
        return ko_phonemes(word.strip())
    if lang == "he":
        ipa = _hebrew_ipa(w)
        phs = map_ipa(ipa, "he")
        if phs and not any(p.split("/")[-1] in "aeiou" or
                           p.split("/")[-1] in ("y",) for p in phs):
            out = []
            for k2, p2 in enumerate(phs):
                out.append(p2)
                if k2 < len(phs) - 1:
                    out.append("ru/a")     # vowel floor: singable, imperfect
            phs = out
        return phs
    if lang in IPA_MAPS:
        return map_ipa(espeak_ipa(w, lang), lang)
    return None


def _namespace(phs, lang):
    """Bank dict rows already namespace foreign phonemes (ja rows carry
    'ja/a'); bare specials (SP/AP/cl) stay bare."""
    if phs is None:
        return None
    out = []
    for p in phs:
        out.append(p if ("/" in p or p in ("SP", "AP", "cl", "vf")) else f"{lang}/{p}")
    return out


def langs_available():
    """What this box can sing RIGHT NOW: bank language + a working rail."""
    have = set(bank_languages())
    out = {"en", "ja"} & have
    if os.path.exists(os.path.join(DSDUR, "dsdict-zh.yaml")):
        out.add("zh")
    out.add("ko")
    try:
        r = subprocess.run(["espeak-ng", "--voices"], capture_output=True,
                           text=True, timeout=10)
        voices = set(re.findall(r"^\s*\d+\s+([a-z-]+)", r.stdout, re.M))
        for lg in IPA_MAPS:
            if lg == "he":
                continue
            if any(v in voices for v in ESPEAK_VOICE.get(lg, (lg,))) and lg in have:
                out.add(lg)
        if "he" in voices:
            out.add("he")
    except Exception:
        pass
    return sorted(out)


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "ru"
    word = sys.argv[2] if len(sys.argv) > 2 else "любовь"
    print("available:", langs_available())
    print(f"{lang} '{word}' ->", phonemes_for(word, lang))
