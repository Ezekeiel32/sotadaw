#!/usr/bin/env python3
"""VOCAL LANGUAGE E2E (P9+P11) — sings REAL words in N languages through the
actual DiffSinger rail and judges each stem with THE VOCAL COURT (whisper
round-trip). The empirical proof that 'all languages' means SUNG AND
UNDERSTOOD, not tables. GPU-preferring; ~10s per language. Cleans up.

    vocal_lang_e2e.py [langs]     default: ru,en   (--full suite runs more)
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
PY = os.path.join(ROOT, ".venv", "bin", "python")
RIG = "_langrig_e2e"

LYRICS = {
    "ru": ["мы", "поднимаемся", "в", "ночи", "мы", "держим", "свет", "всегда"],
    "en": ["we", "rise", "tonight", "and", "hold", "the", "light", "again"],
    "es": ["corazón", "de", "fuego", "bailamos", "toda", "la", "noche", "siempre"],
    "de": ["wir", "tanzen", "immer", "durch", "die", "nacht", "im", "licht"],
    "ja": ["こころ", "の", "ひかり", "よる", "を", "こえて", "いつも", "うたう"],
    "ko": ["사랑", "의", "빛", "밤", "을", "지나", "언제나", "노래"],
    "he": ["שלום", "אהבה", "לילה", "אור", "כוכב", "תמיד", "שמים", "לב"],
}
# whisper-on-singing floors per language (CER; bootstrap — R-11 refines).
# he rides a CROSS-LINGUAL BRIDGE (ru phonemes) — the floor is honest about it.
CER_FLOOR = {"ru": 0.45, "en": 0.30, "es": 0.45, "de": 0.50, "ja": 0.60,
             "ko": 0.60, "he": 0.75}


def main():
    langs = (sys.argv[1].split(",") if len(sys.argv) > 1 else ["ru", "en"])
    sj = os.path.join(ROOT, "songs", f"{RIG}.json")
    fails = []
    try:
        for lang in langs:
            words = LYRICS[lang]
            notes = [{"start": i * 2.0, "len": 1.5, "pitch": p, "vel": 0.9}
                     for i, p in enumerate([60, 62, 64, 62, 60, 62, 64, 60])]
            song = {"version": 2, "bpm": 80, "lengthBars": 4, "key": "C major",
                    "lyrics_lang": lang,
                    "lyrics": [{"beat": n["start"], "text": w}
                               for n, w in zip(notes, words)],
                    "tracks": [{"name": "lead", "source": {"id": "pluck_soft"},
                                "notes": notes}]}
            json.dump(song, open(sj, "w"), indent=1)
            r = subprocess.run([PY, os.path.join(ROOT, "tools", "sing.py"),
                                "render", RIG, "lead", "standard", lang],
                               capture_output=True, text=True, timeout=900)
            tail = (r.stdout.strip().splitlines() or ["?"])[-1]
            if r.returncode != 0 or "SUNG" not in r.stdout:
                fails.append(f"{lang}: sing failed: {tail[-160:]}")
                continue
            if "Unsung words" in r.stdout:
                fails.append(f"{lang}: words dropped: {tail[-160:]}")
                continue
            rc = subprocess.run(
                [PY, os.path.join(ROOT, "tools", "vocal_court.py"), RIG]
                + (["--lang", lang] if lang != "he" else []),
                capture_output=True, text=True, timeout=600)
            try:
                v = json.loads(rc.stdout)
            except Exception:
                fails.append(f"{lang}: court crashed: {rc.stderr[-160:]}")
                continue
            floor = CER_FLOOR.get(lang, 0.6)
            print(f"[{lang}] wer={v.get('wer')} cer={v.get('cer')} "
                  f"verdict={v.get('verdict')} heard='{v.get('heard', '')[:60]}'")
            if v.get("cer", 1.0) > floor:
                fails.append(f"{lang}: CER {v.get('cer')} > floor {floor} "
                             f"(heard: {v.get('heard', '')[:80]})")
    finally:
        for ext in (".json", ".wav", "_vocal.wav", ".ds"):
            p = os.path.join(ROOT, "songs", f"{RIG}{ext}")
            os.path.exists(p) and os.remove(p)
    if fails:
        print("VOCAL LANG E2E FAIL:\n  - " + "\n  - ".join(fails))
        return 1
    print(f"VOCAL LANG E2E PASS — {len(langs)} language(s) sung and understood")
    return 0


if __name__ == "__main__":
    sys.exit(main())
