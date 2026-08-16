#!/usr/bin/env python3
"""LANGUAGE RAIL battery (P9) — per-language coverage + honesty, no GPU.

Every language's core-vocabulary words must map to REAL bank phonemes with
zero misses (espeak symbol drift — the y/ʌ/ɑ/tʃʲ class — lands HERE, not in
a dead take). Hebrew rides the ru-bridge. detect_lang script routing exact.
Determinism law: same word -> same phonemes.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sing_lang as SL  # noqa: E402

N = [0]


def ok(cond, msg):
    N[0] += 1
    if not cond:
        print(f"FAIL #{N[0]}: {msg}")
        sys.exit(1)


WORDS = {
    "ru": ["мы", "поднимаемся", "в", "ночи", "держим", "свет", "всегда",
           "любовь", "сердце", "огонь", "небо", "звезда"],
    "es": ["corazón", "noche", "fuego", "amor", "cielo", "luz", "vida",
           "siempre", "bailamos", "estrella"],
    "de": ["liebe", "nacht", "feuer", "herz", "licht", "immer", "himmel",
           "wir", "tanzen", "stern"],
    "fr": ["amour", "nuit", "feu", "lumière", "toujours", "ciel", "coeur",
           "nous", "dansons", "étoile"],
    "it": ["amore", "notte", "fuoco", "cuore", "luce", "sempre", "cielo",
           "noi", "balliamo", "stella"],
    "pt": ["amor", "noite", "fogo", "coração", "luz", "sempre", "céu",
           "nós", "dançamos", "estrela"],
    "pl": ["miłość", "noc", "ogień", "serce", "światło", "zawsze", "niebo",
           "my", "gwiazda"],
    "uk": ["ми", "ніч", "вогонь", "серце", "світло", "завжди", "небо",
           "любов", "зірка"],
    "ja": ["こころ", "ひかり", "よる", "ほのお", "そら", "いつも", "ほし",
           "あい", "おどる"],
    "ko": ["사랑", "밤", "불", "마음", "빛", "언제나", "하늘", "별"],
    "he": ["שלום", "אהבה", "לילה", "אור", "לב", "תמיד", "שמים", "כוכב"],
    "ar": ["حب", "ليل", "نار", "قلب", "نور", "دائما", "سماء", "نجمة"],
}

inv = SL.bank_inventory()
lang_ids = SL.bank_languages()

for lang, words in WORDS.items():
    missed = []
    for w in words:
        phs = SL.phonemes_for(w, lang)
        if not phs:
            missed.append(w)
            continue
        for p in phs:
            if p in ("SP", "AP", "cl", "vf"):
                continue
            ok("/" in p, f"{lang} '{w}': bare token '{p}' (must be namespaced)")
            ns, bare = p.split("/", 1)
            ok(ns in lang_ids, f"{lang} '{w}': namespace '{ns}' unknown to bank")
            ok(bare in inv.get(ns, set()),
               f"{lang} '{w}': phoneme '{p}' not in bank inventory")
        # determinism law
        ok(phs == SL.phonemes_for(w, lang), f"{lang} '{w}' nondeterministic")
    ok(not missed, f"{lang}: unmapped core vocabulary {missed} "
                   "(espeak symbol drift — extend IPA_MAPS)")
    print(f"[{lang}] {len(words)} words fully mapped")

# script detection
for w, want in (("любовь", "ru"), ("שלום", "he"), ("حب", "ar"), ("사랑", "ko"),
                ("こころ", "ja"), ("光", "zh"), ("สวัสดี", "th"), ("love", "en")):
    ok(SL.detect_lang(w) == want, f"detect '{w}' -> {SL.detect_lang(w)} != {want}")
# Latin words stay the song default
ok(SL.detect_lang("corazón", default="es") == "es", "latin keeps song default")

# the hebrew bridge rides ru namespace only (until a he bank lands)
phs = SL.phonemes_for("שלום", "he")
ok(phs and all(p.split("/")[0] == "ru" for p in phs), f"he bridge via ru: {phs}")

# ja segmentation exactness (dict-driven longest match incl. small kana)
ok(SL.phonemes_for("こころ", "ja") == ["ja/k", "ja/o", "ja/k", "ja/o", "ja/r", "ja/o"],
   "ja kokoro exact")
ph = SL.phonemes_for("きょう", "ja")
ok(ph and ph[0] == "ja/ky", f"ja kyou palatalized cluster: {ph}")

# ko jamo math exact
ok(SL.phonemes_for("사랑", "ko") == ["ko/s", "ko/a", "ko/r", "ko/a", "ko/NG"],
   "ko sarang exact")

# zh pinyin path (romanized input works bare)
ph = SL.phonemes_for("ni", "zh")
ok(ph and all(p.startswith("zh/") for p in ph), f"zh pinyin ni: {ph}")

# langs_available reports at least the proven set
avail = set(SL.langs_available())
ok({"en", "ja", "ko", "ru", "es", "de"} <= avail, f"available shrank: {avail}")

print(f"SING LANG BATTERY PASS — {N[0]} checks green "
      f"({len(WORDS)} languages, {sum(len(w) for w in WORDS.values())} words)")
