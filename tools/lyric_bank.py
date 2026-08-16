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

# THE STORY BANKS (PRODUCER MIND P10, 2026-07-14): each family is a real
# miniature SONG — verses that tell a story and ADVANCE, a pre that lifts,
# a chorus that is THE HOOK (title-led, repeats by construction), a bridge
# that turns. All words lowercase alpha, open-vowel heavy, CMU-safe.
# BANKS (below) derives as the union stream — the legacy sectionless walk
# reads the same story front to back, so nothing downstream changes shape.
STORIES = {
    "bright": {
        "verse": ("city lights are waking up the street is calling out my "
                  "name i feel the engine of the night begin to hum inside "
                  "my veins every window turns to gold the radio begins to "
                  "play and every heartbeat says we go we throw the doubt "
                  "away").split(),
        "prechorus": "hold on the sky is turning we are the fire burning".split(),
        "chorus": ("we rise we rise tonight and hold the light forever "
                   "young we shine we shine like gold on fire away into "
                   "the blue and never let it go").split(),
        "bridge": ("if the morning never comes we are already home the "
                   "night belongs to us alone").split(),
    },
    "warm": {
        "verse": ("i left a candle in the window for the day you walk this "
                  "road the coffee still remembers you the garden still is "
                  "growing slow i kept the letters in a shoebox every word "
                  "you ever wrote and when the evening settles down i hear "
                  "you humming every note").split(),
        "prechorus": "so come on home the door is open wide".split(),
        "chorus": ("oh my love come home to me i feel the light of day my "
                   "soul will rise and hold you close we sing away the "
                   "night and love will find a way").split(),
        "bridge": ("time may bend the both of us but never what is true "
                   "i was always coming back to you").split(),
    },
    "dark": {
        "verse": ("cold in the night we move through shadow lines the city "
                  "never sleeps it only waits concrete under streetlight "
                  "shine we slip between the gates no names no traces on "
                  "the wall we learned to read the rain every siren is a "
                  "call we rose up from the pain").split(),
        "prechorus": "they never see us coming till we gone".split(),
        "chorus": ("no fear inside the dark we run these streets of stone "
                   "the fire in my veins will never die alone we own the "
                   "night we own the cold").split(),
        "bridge": ("if i fall tonight then carry on the flame the dark "
                   "remembers every name").split(),
    },
    "drift": {
        "verse": ("we rise through night skies fall away in dreams of "
                  "light a slow horizon opens wide and time dissolves to "
                  "white i hear the planets in the low end breathing in "
                  "the drone every particle of sound becoming still "
                  "becoming home").split(),
        "prechorus": "slow waves carry us beyond the veil".split(),
        "chorus": ("burn slow deep inside the sound we breathe and drift "
                   "beyond the veil of time we glow we glow the light is "
                   "all we know").split(),
        "bridge": ("nothing here to hold nothing left to be only the "
                   "light inside of me").split(),
    },
}

# legacy union stream (the sectionless walk reads the story front to back);
# battery law: every sectioned word is a member of its family's BANKS.
BANKS = {fam: (s["verse"] + s["prechorus"] + s["chorus"] + s["bridge"])
         for fam, s in STORIES.items()}

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

    # THE STORY ROUTER (P10 v2): section class -> story part. Verses WALK ON
    # across the song (the story advances); chorus/pre restart their part
    # every time (lexical identity by construction — the HOOK LAW upgraded
    # from a cache to an invariant); bridge turns once.
    fam = next((f for f, keys in FAMILY.items()
                if any(k in str(genre or "").lower() for k in keys)), "drift")
    story = STORIES[fam]

    def part_of(base):
        if base in HOOK_BASES and base != "prechorus":
            return "chorus"
        if base == "prechorus":
            return "prechorus"
        if "bridge" in base:
            return "bridge"
        return "verse"

    from itertools import groupby
    out, hook_words = [], {}
    part_idx = {"verse": 0, "bridge": 0}
    for secname, grp in groupby(ns, key=lambda n: sec_of(float(n.get("start", 0)))):
        grp = list(grp)
        base = secname.rstrip("0123456789")
        part = part_of(base)
        pw = story[part]
        prot = rot % len(pw)
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
            j = part_idx.get(part, 0) if part in ("verse", "bridge") else 0
            for n in grp:
                b = float(n.get("start", 0))
                if last_b is not None and abs(b - last_b) < 1e-6:
                    texts.append(texts[-1])
                    continue
                texts.append(pw[(prot + j) % len(pw)])
                j, last_b = j + 1, b
            if part in ("verse", "bridge"):
                part_idx[part] = j
            if base in HOOK_BASES and base not in hook_words:
                hook_words[base] = texts
        out += [{"beat": float(n.get("start", 0)), "text": t}
                for n, t in zip(grp, texts)]
    return _apply_melisma(out, ns, genre, spans, rot)


# ---- THE MELISMA EMISSION (wave 23, item 056; r-10 f7 Grove taxonomy) ----
# syllabic = 1 note/syllable (pop-rock default), neumatic = 2-4 notes,
# melismatic = >4 (the gospel/soul/R&B signature — runs live on hook and
# cadence syllables). sing.py has carried {"melisma": N} since W96; this
# is the first emitter. (family keys, max extra notes per run, runs per
# hook-section instance)
MELISMA_POLICY = (
    (("gospel", "soul", "rnb", "r_b", "motown", "doo_wop", "doowop",
      "ballad", "afrobeat"), 5, 2),
    (("pop", "kpop", "jpop", "citypop", "house", "garage", "disco",
      "funk", "dance", "edm", "synthwave", "reggae", "amapiano"), 2, 1),
)


def melisma_policy(genre):
    g = str(genre or "").lower()
    for keys, max_extra, max_runs in MELISMA_POLICY:
        if any(k in g for k in keys):
            return (max_extra, max_runs)
    return None                     # syllabic family: no runs


def _apply_melisma(out, ns, genre, spans, seed):
    """Collapse the CADENCE run of each hook-class section into one word
    riding the pitch run: the run's first word gains {"melisma": N}, the
    claimed notes' entries are DROPPED (sing.py's one-word-per-note
    contract holds — claimed notes carry no word). Runs = consecutive
    notes, gaps < 0.4 beat, stepwise (|step| <= 2 st). Deterministic."""
    pol = melisma_policy(genre)
    if not pol or not spans or len(out) < 6:
        return out
    max_extra, max_runs = pol
    by_beat = {round(o["beat"], 6): o for o in out}
    notes = sorted((n for n in ns if round(float(n.get("start", 0)), 6)
                    in by_beat), key=lambda n: float(n.get("start", 0)))
    drop = set()
    for nm, b0, b1 in spans:
        base = str(nm).rstrip("0123456789").strip()
        if base not in HOOK_BASES or base == "prechorus":
            continue
        sec = [n for n in notes if b0 <= float(n.get("start", 0)) < b1]
        runs, cur = [], [0] if sec else []
        for i in range(1, len(sec)):
            gap = float(sec[i]["start"]) - (float(sec[i - 1]["start"])
                                            + float(sec[i - 1].get("len",
                                                                   0.25)))
            step = abs(int(sec[i].get("pitch", 60))
                       - int(sec[i - 1].get("pitch", 60)))
            if gap < 0.4 and 0 < step <= 2:
                cur.append(i)
            else:
                if len(cur) >= 3:
                    runs.append(cur)
                cur = [i]
        if len(cur) >= 3:
            runs.append(cur)
        # cadence-first: latest runs in the section carry the ornament
        runs.sort(key=lambda r: -float(sec[r[0]]["start"]))
        for run in runs[:max_runs]:
            extra = min(len(run) - 1, max_extra)
            head = by_beat.get(round(float(sec[run[0]]["start"]), 6))
            if head is None or head.get("melisma"):
                continue
            claimed = [round(float(sec[i]["start"]), 6)
                       for i in run[1:extra + 1]]
            if any(b in drop or b not in by_beat for b in claimed):
                continue
            head["melisma"] = extra
            drop.update(claimed)
    if not drop:
        return out
    return [o for o in out if round(o["beat"], 6) not in drop]


if __name__ == "__main__":
    import json
    import sys
    g = sys.argv[1] if len(sys.argv) > 1 else "pop"
    demo = [{"start": float(i)} for i in range(12)]
    print(json.dumps(lyrics_for(g, demo, int(sys.argv[2]) if len(sys.argv) > 2 else 0)))
