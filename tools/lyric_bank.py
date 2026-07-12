#!/usr/bin/env python3
"""THE LYRIC BANK — seeded micro-lyrics for the zero-token sing lanes.

MEASURED (2026-07-11, psybient seed-11 arrangement, CLAP vs the real-record
cloud): real words beat the wordless hum at every level tried —
    loop 0.5041/68.6 < arr 0.5288/72.0 < arr+hum 0.5741/78.1
    < arr+WORDS 0.5899/80.3   (the board's crown)
and the loop-level ladder agreed earlier (0.525 < 0.534 < 0.5455). Voice is
the biggest single realism lever; WORDS are the top of the voice.

This bank keeps the words lane zero-token: short coherent phrase streams of
common singable words (open vowels, all in dsdict-en/CMUdict — sing.py's
letter-rule fallback never has to guess), one word per melody note, seeded
rotation for variety, byte-deterministic per (genre, notes, seed).

    lyrics_for(genre, notes, seed) -> [{"beat": start, "text": word}, ...]

The DRIFT bank is verbatim the measured winner. The user swaps in real
writing any time via write_lyrics + sing_lyrics — this is the strong
default, not the ceiling.
"""

# each bank reads as a continuous phrase stream; cycling stays coherent
BANKS = {
    "bright": ("we rise tonight and hold the light we run for ever young "
               "we shine like gold on fire we fly away into the blue "
               "and never let it go").split(),
    "warm": ("oh my love come home to me i feel the light of day "
             "my soul will rise and hold you close we sing away the night "
             "and love will find a way").split(),
    "dark": ("cold in the night we move through shadow lines "
             "no fear inside the dark we run these streets of stone "
             "the fire in my veins will never die alone").split(),
    "drift": ("we rise through night skies fall away in dreams of light "
              "burn slow deep inside the sound we breathe and drift beyond "
              "the veil of time we glow").split(),
}

FAMILY = {
    "bright": ("pop", "kpop", "jpop", "citypop", "hyperpop", "house",
               "garage", "ukgarage", "2step", "3step", "disco", "funk",
               "edm", "dance", "eurodance", "synthwave", "electro"),
    "warm": ("soul", "gospel", "rnb", "motown", "doo_wop", "doowop",
             "jazz", "blues", "reggae", "bossa", "ballad"),
    "dark": ("trap", "drill", "grime", "phonk", "techno", "industrial",
             "dnb", "drum_and_bass", "dubstep", "hardstyle", "gqom",
             "memphis", "horrorcore", "darkwave"),
    "drift": ("ambient", "psybient", "psychill", "chillout", "downtempo",
              "triphop", "lofi", "idm", "dub", "meditation", "drone",
              "berlin_school", "space"),
}


def bank_for(genre):
    """Family routing by substring membership; unknown genres get the
    MEASURED-WINNER drift bank (it is genre-neutral evocative)."""
    g = str(genre or "").lower()
    for fam, keys in FAMILY.items():
        if any(k in g for k in keys):
            return BANKS[fam]
    return BANKS["drift"]


# prechorus joined 2026-07-12 (dr25): real records repeat the pre-chorus
# words each time just like the hook.
HOOK_BASES = {"chorus", "drop", "hook", "theme", "prechorus"}


def lyrics_for(genre, notes, seed=0, sections=None):
    """One word per melody note (sing.py's exact contract), beats = the
    notes' own starts, seeded rotation through the family's phrase stream.
    Deterministic: same (genre, notes, seed, sections) -> same lyrics.

    THE HOOK LINE LAW (ledger dr20/dr21, 2026-07-12): the rotation used to
    run CONTINUOUSLY across the whole track, so chorus2 sang different words
    than chorus — the hook had no lexical identity. With sections given,
    repeated HOOK-class sections (chorus/drop/hook/theme) REUSE the first
    instance's words note-for-note; verses keep walking the stream (verses
    tell the story — new words there are correct). Same-beat notes (the
    final-chorus octave double) share ONE word — never two words at once.
    sections=None keeps the exact legacy behavior."""
    words = bank_for(genre)
    ns = sorted((n for n in notes or [] if isinstance(n, dict)),
                key=lambda n: float(n.get("start", 0)))
    if not ns:
        return []
    rot = int(seed or 0) % len(words)
    spans = []
    if sections:
        try:
            secs = sorted((s for s in sections if isinstance(s, dict)),
                          key=lambda s: float(s.get("startBar", 0)))
            for i, s in enumerate(secs):
                b0 = float(s.get("startBar", 0)) * 4.0
                b1 = (float(secs[i + 1].get("startBar", 0)) * 4.0
                      if i + 1 < len(secs) else float("inf"))
                spans.append((str(s.get("name", "")), b0, b1))
        except Exception:
            spans = []
    if not spans:
        return [{"beat": float(n.get("start", 0)),
                 "text": words[(rot + i) % len(words)]}
                for i, n in enumerate(ns)]

    def sec_of(beat):
        for nm, b0, b1 in spans:
            if b0 <= beat < b1:
                return nm
        return ""

    from itertools import groupby
    out, idx, hook_words = [], 0, {}
    for secname, grp in groupby(ns, key=lambda n: sec_of(float(n.get("start", 0)))):
        grp = list(grp)
        base = secname.rstrip("0123456789")
        texts, last_b = [], None
        if base in HOOK_BASES and base in hook_words:
            ws, j = hook_words[base], 0
            for n in grp:
                b = float(n.get("start", 0))
                if last_b is not None and abs(b - last_b) < 1e-6:
                    texts.append(texts[-1])
                    continue
                texts.append(ws[j % len(ws)])
                j, last_b = j + 1, b
        else:
            for n in grp:
                b = float(n.get("start", 0))
                if last_b is not None and abs(b - last_b) < 1e-6:
                    texts.append(texts[-1])
                    continue
                texts.append(words[(rot + idx) % len(words)])
                idx, last_b = idx + 1, b
            if base in HOOK_BASES and base not in hook_words:
                hook_words[base] = texts
        out += [{"beat": float(n.get("start", 0)), "text": t}
                for n, t in zip(grp, texts)]
    return out


if __name__ == "__main__":
    import json
    import sys
    g = sys.argv[1] if len(sys.argv) > 1 else "pop"
    demo = [{"start": float(i)} for i in range(12)]
    print(json.dumps(lyrics_for(g, demo, int(sys.argv[2]) if len(sys.argv) > 2 else 0)))
