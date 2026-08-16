#!/usr/bin/env python3
"""LYRIC COURT BATTERY — proves THE LYRIC COURTS (wave 17; R-10
009/010/011/062). Pure, deterministic, no renders, no models."""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lyric_court as LC  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def sung(words_beats, bpm=120, note_len=0.4, pitches=None, sections=None):
    """A song whose vocal lane carries one note per lyric word."""
    lyr, notes = [], []
    for i, (w, b) in enumerate(words_beats):
        lyr.append({"beat": float(b), "text": w})
        ln = note_len[i] if isinstance(note_len, (list, tuple)) else note_len
        p = pitches[i] if pitches else 60
        notes.append({"start": float(b), "len": float(ln), "pitch": p,
                      "vel": 0.9})
    s = {"bpm": bpm, "lyrics": lyr,
         "tracks": [{"name": "lead_vocals", "notes": notes}]}
    if sections:
        s["sections"] = sections
    return s


# ---------------------------------------------------------------- kernels
check("syllables: beautiful=3 (CMU)", LC.syllables("beautiful") == 3)
check("syllables: OOV runnin' via pyphen", LC.syllables("runnin'") == 2)
check("syllables: @phoneme token = None", LC.syllables("@l+aa") is None)
check("stresses: gasoline 1-0-2", LC.stresses("gasoline") == ["1", "0", "2"])
check("stressed_vowel: see=IY closed", LC.stressed_vowel("see") == "IY")
check("stressed_vowel: star=AA open", LC.stressed_vowel("star") == "AA")
check("is_content: 'the' False, 'fire' True",
      not LC.is_content("the") and LC.is_content("fire"))

s = sung([("love", 0), ("me", 1)])
check("vocal_lane: finds lead_vocals", LC.vocal_lane(s) is not None)
s2 = copy.deepcopy(s)
s2["tracks"].append({"name": "vocals_sketch", "notes": [{"start": 0}] * 9})
check("vocal_lane: never a _sketch lane",
      LC.vocal_lane(s2)["name"] == "lead_vocals")

import lyric_bank  # noqa: E402
bank_words = lyric_bank.bank_for("pop")
s = sung([(bank_words[i], i * 0.5) for i in range(8)])
check("bank_authored: all-bank lyrics True", LC.bank_authored(s, "pop"))
s["lyrics"][3]["text"] = "xyzzy"
check("bank_authored: one foreign word False",
      not LC.bank_authored(s, "pop"))

# ------------------------------------------------- 009 singability court
s = sung([("beautiful", 0), ("love", 1), ("night", 2)], note_len=0.5)
v = LC.court_singability(s, "pop")
check("singability: 3-syl word on 250ms CONVICTED (REFFLY floor)",
      not v["ok"] and v["flags"][0]["kind"] == "crammed_word", str(v))
s = sung([("beautiful", 0), ("love", 1), ("night", 2)], note_len=1.0)
check("singability: same word on 500ms pardoned",
      LC.court_singability(s, "pop")["ok"])
s = sung([("@l+aa", 0), ("@d+uu", 1)])
check("singability: hum take skipped",
      LC.court_singability(s, "pop").get("skipped", "").startswith("no word"))
imp = sung([("beautiful", 0)], note_len=0.25)
imp["tracks"].append({"name": "other_sketch", "notes": []})
check("singability: imported record skipped (witness law)",
      LC.court_singability(imp, "pop").get("skipped", "").startswith("imported"))

# heal: crammed BANK trisyllable swaps to a bank monosyllable
wb = [("forever", 0), ("lights", 1), ("street", 2), ("night", 3)]
s = sung(wb, note_len=[0.4, 1, 1, 1])
v = LC.court_singability(s, "pop")
check("singability: bank 'forever' on 200ms convicted", not v["ok"])
edits = LC.heal_singability(s, "pop", v)
check("singability heal: bank word swapped to a monosyllable",
      edits and edits[0]["kind"] == "word_swap" and
      LC.syllables(edits[0]["new"]) == 1, str(edits))
check("singability heal: re-court OK", LC.court_singability(s, "pop")["ok"])
d1 = LC.heal_singability(sung(wb, note_len=[0.4, 1, 1, 1]), "pop")
d2 = LC.heal_singability(sung(wb, note_len=[0.4, 1, 1, 1]), "pop")
check("singability heal: deterministic (same swap twice)",
      d1 == d2, f"{d1} vs {d2}")
s = sung([("xylophonic", 0), ("night", 1)], note_len=0.4)
check("singability heal: NON-bank words never rewritten (authorship guard)",
      LC.heal_singability(s, "pop") == [])

# ---------------------------------------------------- 010 prosody court
# content words all on WEAK beats, function words on strong 0/2 grid
weak = []
for bar in range(4):
    weak += [("the", bar * 4 + 0.0), ("fire", bar * 4 + 1.0),
             ("is", bar * 4 + 2.0), ("burning", bar * 4 + 3.0)]
s = sung(weak, note_len=0.4)
v = LC.court_prosody(s, "pop")
check("prosody: content-on-weak CONVICTED below 0.80 floor",
      not v["ok"] and v["flags"][0]["kind"] == "weak_prosody", str(v))
sc0 = v["flags"][0]["score"]
strong = []
for bar in range(4):
    strong += [("fire", bar * 4 + 0.0), ("the", bar * 4 + 1.0),
               ("burning", bar * 4 + 2.0), ("is", bar * 4 + 3.0)]
check("prosody: content-on-strong pardoned",
      LC.court_prosody(sung(strong, note_len=0.4), "pop")["ok"])

bank_weak = []
fn = [w for w in bank_words if not LC.is_content(w)]
ct = [w for w in bank_words if LC.is_content(w)]
for bar in range(4):
    bank_weak += [(fn[bar % len(fn)], bar * 4 + 0.0),
                  (ct[bar % len(ct)], bar * 4 + 1.0),
                  (fn[(bar + 1) % len(fn)], bar * 4 + 2.0),
                  (ct[(bar + 1) % len(ct)], bar * 4 + 3.0)]
s = sung(bank_weak, note_len=0.4)
v = LC.court_prosody(s, "pop")
check("prosody: bank-authored weak placement convicted", not v["ok"], str(v))
edits = LC.heal_prosody(s, "pop", v)
after = LC.court_prosody(s, "pop")
check("prosody heal: swaps lift the take to the floor",
      edits and after["ok"],
      f"edits={len(edits)} score {v.get('flags', [{}])[0].get('score')} -> "
      f"{after.get('score')}")
words_before = sorted(w for w, _ in bank_weak)
words_after = sorted(str(l["text"]) for l in s["lyrics"])
check("prosody heal: word SET preserved (placement-only heal)",
      words_before == words_after)

# -------------------------------------------------- 011 vowel-long court
rows = [("star", i * 1.0) for i in range(11)] + [("see", 11.0)]
s = sung(rows, note_len=[0.4] * 11 + [2.0],
         pitches=[60] * 11 + [72])
v = LC.court_vowel_long(s, "pop")
check("vowel_long: closed IY on the long high note = advisory, ok True",
      v["ok"] and any(a["kind"] == "closed_vowel_long_note" and
                      a["word"] == "see" for a in v["advisories"]), str(v))
check("vowel_long: open AA words silent",
      all(a["word"] != "star" for a in v["advisories"]))

# --------------------------------------------------- 062 song-form court
def form_song(chorus2_words):
    words, sections = [], []
    v1 = ["walking", "down", "the", "street", "tonight", "alone"]
    ch = ["fire", "in", "my", "heart", "fire", "burning"]
    v2 = ["morning", "light", "is", "breaking", "over", "town"]
    for si, (name, ws) in enumerate([("verse", v1), ("chorus", ch),
                                     ("verse_2", v2),
                                     ("chorus_2", chorus2_words)]):
        sections.append({"name": name, "startBar": si * 2})
        for i, w in enumerate(ws):
            words.append((w, si * 8 + i * 1.0))
    return sung(words, note_len=0.5, sections=sections)


drift = ["water", "in", "my", "soul", "water", "rising"]
s = form_song(drift)
v = LC.court_form(s, "pop")
check("form: chorus drift CONVICTED (lyric-INVARIANT law)",
      not v["ok"] and v["flags"][0]["kind"] == "chorus_drift", str(v))
edits = LC.heal_form(s, "pop", v)
check("form heal: chorus 1 re-landed verbatim",
      edits and edits[0]["kind"] == "chorus_reland" and
      LC.court_form(s, "pop")["ok"], str(edits))
same = ["fire", "in", "my", "heart", "fire", "burning"]
check("form: verbatim chorus pardoned", LC.court_form(form_song(same), "pop")["ok"])
s = form_song(same)
for l in s["lyrics"]:
    if 16 <= l["beat"] < 24:   # verse_2 window -> clone verse 1
        pass
v1w = [l for l in s["lyrics"] if l["beat"] < 8]
for l in s["lyrics"]:
    if 16 <= l["beat"] < 24:
        l["text"] = v1w[int(l["beat"]) - 16]["text"]
v = LC.court_form(s, "pop")
check("form: verse clone = advisory only",
      v["ok"] and any(a["kind"] == "verse_clone" for a in v["advisories"]),
      str(v))

# --------------------------------- wave 23: melisma emission + policy court
import lyric_bank  # noqa: E402


def run_notes(base_beat, pitches, ln=0.4, gap=0.05):
    out, b = [], base_beat
    for p in pitches:
        out.append({"start": round(b, 4), "len": ln, "pitch": p, "vel": 0.8})
        b += ln + gap
    return out


mel_notes = (run_notes(0, [60, 62, 60, 64]) +          # verse: no runs
             run_notes(8, [64, 65]) +                   # chorus start
             run_notes(10, [67, 66, 65, 64, 62]))       # cadence RUN (5)
secs = [{"name": "verse", "startBar": 0}, {"name": "chorus", "startBar": 2}]
ly = lyric_bank.lyrics_for("gospel", mel_notes, seed=3, sections=secs)
mel_entries = [l for l in ly if l.get("melisma")]
check("emission (056): gospel cadence run carries melisma",
      len(mel_entries) == 1 and mel_entries[0]["melisma"] >= 2,
      str(mel_entries))
check("emission: claimed notes' entries dropped (word count shrinks)",
      len(ly) == len(mel_notes) - mel_entries[0]["melisma"],
      f"{len(ly)} vs {len(mel_notes)}")
ly2 = lyric_bank.lyrics_for("gospel", mel_notes, seed=3, sections=secs)
check("emission: deterministic", ly == ly2)
ly_drill = lyric_bank.lyrics_for("drill", mel_notes, seed=3, sections=secs)
check("emission: syllabic family (drill) emits NO runs",
      not any(l.get("melisma") for l in ly_drill))
check("emission: policy table routes (gospel melismatic, pop neumatic)",
      lyric_bank.melisma_policy("gospel")[0] == 5 and
      lyric_bank.melisma_policy("pop")[0] == 2 and
      lyric_bank.melisma_policy("drill") is None)

# singability: a melisma word never crams (the run EXTENDS its vowel)
s = sung([("hallelujah", 0), ("light", 1), ("shine", 2)], note_len=0.4)
s["lyrics"][0]["melisma"] = 4
check("singability: melisma word skipped (REFFLY lawful direction)",
      LC.court_singability(s, "gospel")["ok"],
      str(LC.court_singability(s, "gospel")))

# court_melisma policy advisories (198)
def mel_song(genre, mel_on=(), n=12):
    s = sung([(f"word{i}", i) for i in range(n)], note_len=0.6)
    for i in mel_on:
        s["lyrics"][i]["text"] = "oh"
        s["lyrics"][i]["melisma"] = 5
    return s


v = LC.court_melisma(mel_song("drill", mel_on=(3,)), "drill")
check("melisma court: runs in a syllabic genre = offstyle advisory",
      any(a["kind"] == "melisma_offstyle" for a in v["advisories"]), str(v))
v = LC.court_melisma(mel_song("gospel"), "gospel")
check("melisma court: run-culture genre with zero runs = missing advisory",
      any(a["kind"] == "melisma_missing" for a in v["advisories"]), str(v))
v = LC.court_melisma(mel_song("gospel", mel_on=(3, 8)), "gospel")
check("melisma court: gospel WITH runs clean", not v["advisories"], str(v))
v = LC.court_melisma(mel_song("house", mel_on=(1, 3, 5, 7)), "house")
check("melisma court: 33% runs in a syllabic-default genre = heavy",
      any(a["kind"] == "melisma_heavy" for a in v["advisories"]), str(v))

# intelligibility composite (126)
clean = sung([("light", i) for i in range(10)], note_len=0.8)
r = LC.intelligibility_risk(clean, "pop")
check("intelligibility (126): clean take risk 0", r["risk"] == 0.0, str(r))
risky = sung([("beautiful", 0), ("gasoline", 1), ("light", 2),
              ("shine", 3), ("sun", 4), ("day", 5), ("way", 6),
              ("run", 7)], note_len=0.35)
r = LC.intelligibility_risk(risky, "pop")
check("intelligibility: crammed polysyllables raise the risk",
      r["risk"] > 0.15 and r["parts"]["crammed"] >= 2, str(r))

# ------------------------------------------------ rhyme court (wave 41)
import rhyme_court as RC  # noqa: E402
check("rhyme: dense multi chain outranks prose",
      RC.rhyme_factor("combat format doormat wombat".split() * 4) >
      RC.rhyme_factor("the quick brown fox jumps over lazy dogs".split()))
check("rhyme: scheme AABB read straight off end sounds",
      RC.scheme_of(["burning bright tonight", "hold me tight tonight",
                    "we fall like rain", "we rise through pain"]) == "AABB")
check("rhyme: scheme ABAB (single-vowel perfect rhymes count)",
      RC.scheme_of(["the fire glows", "we ride the wave",
                    "and no one knows", "the love we gave"]) == "ABAB")
rap_song = sung([(w, float(i)) for i, w in enumerate(
    "walking through the city late at night alone with all my thoughts "
    "and dreams fading while the world keeps turning slowly on".split())],
    note_len=0.5)
v = RC.court_rhyme(rap_song, "drill")
check("rhyme: prose-flat drill take = advisory (the bank-upgrade truth)",
      v["ok"] and any(a["kind"] == "prose_flat" for a in v["advisories"]),
      str(v))
check("rhyme: melodic families carry no rhyme-density law",
      not RC.court_rhyme(rap_song, "ambient")["advisories"])
check("rhyme: hum takes skipped",
      RC.court_rhyme(sung([("@l+aa", float(i)) for i in range(20)]),
                     "drill").get("skipped", "").startswith("too few"))

# --------------------------------------------------------------- aggregate
s = sung([("forever", 0), ("lights", 1), ("street", 2), ("night", 3)],
         note_len=[0.4, 1, 1, 1])
v = LC.court_lyrics(s, "pop", heal=True)
check("aggregate: heal ledger + after-court green",
      v["heals"].get("singability") and v["singability_after"]["ok"], str(v.get("heals")))
check("aggregate: no lyrics = skip",
      LC.court_lyrics({"bpm": 120, "tracks": []}, "pop").get("skipped") ==
      "no word lyrics")

# ------------------------------------------- w66: budgets + closure
import rhyme_court as RC
check("tier: rain/pain = perfect, rain/game = family, rain/day = "
      "assonance, rain/rock = none, rain/rain = identity",
      RC.rhyme_tier("rain", "pain") == "perfect" and
      RC.rhyme_tier("rain", "game") == "family" and
      RC.rhyme_tier("rain", "day") == "assonance" and
      RC.rhyme_tier("rain", "rock") == "none" and
      RC.rhyme_tier("rain", "rain") == "identity",
      str([RC.rhyme_tier("rain", x) for x in
           ("pain", "game", "day", "rock", "rain")]))
cls = {"bpm": 120, "lengthBars": 16,
       "sections": [{"name": "verse", "startBar": 0},
                    {"name": "chorus", "startBar": 8}],
       "lyrics": [{"beat": 34.0, "text": "we run all night"},
                  {"beat": 38.0, "text": "we chase the moon"},
                  {"beat": 42.0, "text": "hold my hand tight"},
                  {"beat": 46.0, "text": "the fire fades away"}]}
v = RC.court_closure(cls, "pop")
check("closure: a chorus ending tight/away (assonance-at-best) flags "
      "unresolved_closure",
      any(a["kind"] == "unresolved_closure" for a in v["advisories"]),
      str(v))
cls["lyrics"][-1]["text"] = "we own the night"
check("closure: ending tight/night (perfect) resolves — silent",
      not RC.court_closure(cls, "pop")["advisories"])

budg = {"bpm": 120, "lengthBars": 8, "lyrics": [
    {"beat": float(b * 4), "text":
     "supercalifragilistic expialidocious tonight everybody"}
    for b in range(6)]}
v = LC.court_syllable_budget(budg, "uk drill")
check("budget: six 17-syllable lines vs drill's 5-9 window = crammed",
      v["advisories"] and v["advisories"][0]["over"] == 6, str(v))
ok_lines = {"bpm": 120, "lengthBars": 8, "lyrics": [
    {"beat": float(b * 4), "text": "we ride the wave tonight"}
    for b in range(6)]}
check("budget: 6-syllable pop lines sit inside 6-10 (silent)",
      not LC.court_syllable_budget(ok_lines, "pop")["advisories"])
check("budget: unknown genre = skipped (no invented budgets)",
      LC.court_syllable_budget(ok_lines, "zzz").get("skipped"))

print()
if FAILS:
    print(f"lyric_court_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("lyric_court_battery: ALL GREEN")
