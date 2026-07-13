#!/usr/bin/env python3
"""THE WORLD GRID — the GENERATORS speak meter (BEST_DAW_30 #1, native_meter leg).

grid_battery proves the AGENT layer (surgical/daw_mcp/midi_bridge) reads bars
through the resolver. This proves the two things that WRITE songs — loop_gen
(birth) and arrange (form) — lay their bars in the genre's own meter, and that
every other genre is byte-for-byte untouched.

  A) kernel: parse_meter / default_groups / bar_heads16 (4/4 gives back the
     historical literals: 16 steps, [0,4,8,12] quarters)
  B) THE IDENTITY LAW: a take of a mapless genre carries NO meterMap, and a
     genre that declares "4/4" is BYTE-IDENTICAL to one that declares nothing
  C) loop_gen 7/8: meterMap stamped, bars laid at 3.5q, the cell's steps land
     EXACTLY where the grid put them (no step silently reinterpreted)
  D) THE BARLINE GUARD: a cell step past its own bar never lands in the next one
  E) every bass style stays inside its bar under 7/8, 9/8, 3/4 and 6/8
  F) arrange in 7/8: sections on real barlines, automation + notes inside the
     song, meterMap survives the form
  G) THE KG-FIELD LAW: native_meter rides the dna_cache (the no-graph path) —
     if it only rode the live query it would vanish on every other machine
  H) the curated genres: balkan_brass 7/8, rebetiko 9/8, math_rock 7/8, and
     their cells fit their bars

Pure python, KG-free (reads agent/dna_cache.json like a stranger's box would).
Run: python3 tools/meter_battery.py
"""
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ["SOTADAW_NO_KG"] = "1"          # the stranger's box: cache only

import meter                                                         # noqa: E402
import loop_gen                                                      # noqa: E402

N = {"pass": 0, "fail": 0}


def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""),
          flush=True)


def notes_of(song, lane=None):
    return [n for t in song["tracks"] if lane is None or t["name"] == lane
            for n in t.get("notes", [])]


def synth_dna(native_meter=None, **grid):
    """A minimal DNA blob — no graph, no cache, exactly the fields generate() reads."""
    g = {"bars": 1, "swing": 0.5, "bass_style": "roots",
         "kick": [0, 8], "snare": [4, 12], "hat": [2, 6, 10],
         "chords": [[0, 1]]}
    g.update(grid)
    return {"archetype": "probe", "grid": g, "bpm_lo": 120, "bpm_hi": 120,
            "key": "A minor", "voice": None, "band_order": None, "lufs_lo": None,
            "voicing": None, "groove": None, "native_meter": native_meter}


def gen(name, dna, bars=4, seed=5):
    """generate() with a FORCED dna (no KG, no cache) -> the song dict."""
    real = loop_gen.genre_dna
    loop_gen.genre_dna = lambda g: (copy.deepcopy(dna), None)
    try:
        out, msg = loop_gen.generate("probe_genre", name, bars=bars, seed=seed, bpm=120)
        assert out, msg
        return json.load(open(out)), out
    finally:
        loop_gen.genre_dna = real


def main():
    made = []
    try:
        # ---- A) the kernel -------------------------------------------------
        check("A: meter selftest green", meter._selftest() == 0)
        check("A: bar_heads16 4/4 == the quarters [0,4,8,12]",
              loop_gen.bar_heads16(4, 4) == [0, 4, 8, 12])
        check("A: bar_heads16 7/8 aksak (2+2+3) == [0,4,8]",
              loop_gen.bar_heads16(7, 8) == [0, 4, 8])
        check("A: bar_heads16 9/8 zeibekiko (grid groups 2+2+2+3) == [0,4,8,12]",
              loop_gen.bar_heads16(9, 8, [2, 2, 2, 3]) == [0, 4, 8, 12],
              str(loop_gen.bar_heads16(9, 8, [2, 2, 2, 3])))
        check("A: bar_heads16 9/8 compound default (3+3+3) == [0,6,12]",
              loop_gen.bar_heads16(9, 8) == [0, 6, 12])
        check("A: bar_heads16 6/8 == [0,6]  3/4 == [0,4,8]",
              loop_gen.bar_heads16(6, 8) == [0, 6]
              and loop_gen.bar_heads16(3, 4) == [0, 4, 8])
        check("A: junk groups (don't sum to num) fall back to the default",
              loop_gen.bar_heads16(7, 8, [5, 5]) == [0, 4, 8])

        # ---- B) THE IDENTITY LAW -------------------------------------------
        s_map, p_map = gen("_meter_probe_a", synth_dna(None))
        s_44, p_44 = gen("_meter_probe_b", synth_dna("4/4"))
        made += [p_map, p_44]
        check("B: a mapless take carries NO meterMap key", "meterMap" not in s_map)
        check("B: a take declaring 4/4 carries no meterMap either",
              "meterMap" not in s_44)
        a = json.load(open(p_map)); b = json.load(open(p_44))
        a.pop("_loop"); b.pop("_loop")
        check("B: declared-4/4 == mapless, BYTE for byte", a == b)
        check("B: 4 mapless bars = 16 quarters (the historical grid)",
              max(n["start"] for n in notes_of(s_map)) < 16.0
              and max(n["start"] for n in notes_of(s_map)) >= 12.0)
        # a junk meter falls back to 4/4 rather than inventing a grid
        s_junk, p_junk = gen("_meter_probe_j", synth_dna("5/6"))   # den 6: no 16th grid
        made.append(p_junk)
        check("B: an unrenderable meter (5/6) falls back to 4/4, not to nonsense",
              "meterMap" not in s_junk)

        # ---- C) loop_gen in 7/8 --------------------------------------------
        s78, p78 = gen("_meter_probe_78", synth_dna("7/8", groups=[2, 2, 3]))
        made.append(p78)
        mm = meter.song_meter(s78)
        bq = meter.beats_in_bar(mm, 0)
        check("C: meterMap stamped [{bar:0,num:7,den:8}]",
              s78.get("meterMap") == [{"bar": 0, "num": 7, "den": 8}])
        check("C: a 7/8 bar is 3.5 quarters", bq == 3.5)
        check("C: 4 bars = 14.0 quarters (a 4/4 read would say 16.0)",
              meter.bar_start_q(mm, s78["lengthBars"]) == 14.0)
        end = meter.bar_start_q(mm, s78["lengthBars"])
        outside = [n["start"] for n in notes_of(s78) if n["start"] >= end]
        check("C: not one note past the song's real end", not outside, str(outside[:4]))
        # the CELL survives: kick steps [0,8] -> within-bar quarters {0.0, 2.0}
        kq = sorted({round(n["start"] % bq, 3) for n in notes_of(s78, "kick")})
        check("C: the kick cell lands EXACTLY on its steps (0,8 -> 0.0q, 2.0q)",
              kq == [0.0, 2.0], str(kq))
        check("C: every bar carries the cell (4 bars x 2 kicks)",
              len(notes_of(s78, "kick")) == 8, str(len(notes_of(s78, "kick"))))
        # hats BREATHE by design (one onset shifted/dropped per bar, +-0.25) and
        # carry humanize drift — so the cell is proven by the GRID it lands on,
        # never by equality (kick/snare are the steady lanes; they ARE exact).
        hq = sorted(round(n["start"] % bq, 3) for n in notes_of(s78, "hat"))
        check("C: every hat sits on a 16th of ITS OWN bar",
              all(min(abs(o - k * 0.25) for k in range(14)) < 0.06 for o in hq),
              str(hq[:6]))
        check("C: no hat within a 16th of either barline — the cell has none "
              "there, so nothing spilled across (barlines are real)",
              all(min(o, bq - o) > 0.15 for o in hq), str(hq[:4]))

        # ---- D) THE BARLINE GUARD ------------------------------------------
        # a 16-step 4/4 cell forced into a 7/8 bar: steps 14/15 do NOT reappear
        # as phantom downbeats in the next bar (the whole class this item kills)
        sov, pov = gen("_meter_probe_ov",
                       synth_dna("7/8", kick=[0, 4, 8, 12], hat=[2, 6, 10, 14],
                                 snare=[15]))
        made.append(pov)
        koff = sorted({round(n["start"] % 3.5, 3) for n in notes_of(sov, "kick")})
        hoff = sorted(round(n["start"] % 3.5, 3) for n in notes_of(sov, "hat"))
        check("D: kick steps 0/4/8/12 all fit a 14-step bar (0,1,2,3 q)",
              koff == [0.0, 1.0, 2.0, 3.0], str(koff))
        # step 14 * 0.25 == 3.5q == the NEXT bar's downbeat: the phantom this
        # whole item exists to kill. It is dropped, never re-homed.
        check("D: hat step 14 lands on NO barline (the phantom downbeat is gone)",
              all(min(o, 3.5 - o) > 0.15 for o in hoff), str(hoff[:4]))
        check("D: and the lane thinned to 3 hats a bar, not 4",
              len(notes_of(sov, "hat")) <= 15, str(len(notes_of(sov, "hat"))))
        check("D: snare step 15 (past the barline) never sounds",
              not notes_of(sov, "snare"))

        # ---- E) the bass styles under four meters --------------------------
        import random
        for mtr, spb, hd in (("7/8", 14, [0, 4, 8]), ("9/8", 18, [0, 4, 8, 12]),
                             ("3/4", 12, [0, 4, 8]), ("6/8", 12, [0, 6])):
            bad = []
            for style in ("offbeat", "roots", "sliding", "psy_rolling", "wub",
                          "sustained", "sub", "walking", "tumbao", "log"):
                _, ns = loop_gen.bass_notes(style, 9, [9, 11, 0, 2, 4, 5, 7], 4,
                                            random.Random("m"), [0, 4, 8, 12],
                                            bar_degrees=[1, 6, 4, 5],
                                            bar_steps=spb, heads=hd)
                bq2 = spb * 0.25
                for n in ns:
                    # an ONSET must sit inside a bar it belongs to (never in the
                    # dead zone a 4/4 offset would create past a short barline)
                    step = round(n["start"] / 0.25)
                    if step % spb >= spb or n["start"] >= 4 * bq2:
                        bad.append((style, n["start"]))
            check(f"E: every bass style stays inside its bar in {mtr}", not bad,
                  str(bad[:3]))

        # ---- F) arrange in 7/8 ---------------------------------------------
        import arrange
        out78 = arrange.arrange(p78, genre="balkan_brass", seed=3)
        made.append(out78)
        f78 = json.load(open(out78))
        fmm = meter.song_meter(f78)
        fend = meter.bar_start_q(fmm, f78["lengthBars"])
        check("F: the form keeps the meter", f78.get("meterMap") == s78["meterMap"])
        check("F: the arranged song's bars are 3.5q (a 4/4 read would run it "
              f"{f78['lengthBars'] * 4.0 - fend:.0f}q long)",
              meter.beats_in_bar(fmm, 0) == 3.5
              and fend == f78["lengthBars"] * 3.5)
        late = [n["start"] for n in notes_of(f78) if n["start"] >= fend]
        check("F: no note past the arranged song's end", not late, str(late[:3]))
        secs = [x["startBar"] for x in f78.get("sections", [])]
        check("F: sections land on whole bars", all(float(b).is_integer() for b in secs),
              str(secs[:6]))
        auto = [p["beat"] for t in f78["tracks"] for a in t.get("automation", [])
                for p in a["points"]]
        check("F: automation points live inside the song",
              not auto or max(auto) <= fend, f"max {max(auto) if auto else 0} / {fend}")

        # ---- G/H) the KG-FIELD LAW + the curated genres ---------------------
        cache = json.load(open(os.path.join(ROOT, "agent", "dna_cache.json")))["genres"]
        for g, m in (("balkan_brass", "7/8"), ("rebetiko", "9/8"), ("math_rock", "7/8")):
            check(f"G: dna_cache carries {g} native_meter={m} (the no-graph path)",
                  cache.get(g, {}).get("native_meter") == m,
                  str(cache.get(g, {}).get("native_meter")))
            dna, err = loop_gen.genre_dna(g)          # SOTADAW_NO_KG=1 -> the cache
            check(f"G: genre_dna projects it for {g}",
                  dna is not None and dna.get("native_meter") == m, str(err))
            num, den = meter.parse_meter(m)
            spb = num * 16 // den
            grid = cache[g]["grid"]
            over = [(k, s) for k in ("kick", "snare", "hat", "clap", "ride")
                    for s in (grid.get(k) or []) if s >= spb]
            check(f"H: {g}'s cell fits its {m} bar ({spb} steps)", not over, str(over))
        check("H: the other genres stay mapless (the identity law)",
              sum(1 for v in cache.values() if v.get("native_meter")) == 3,
              str(sum(1 for v in cache.values() if v.get("native_meter"))))
        # the aksak is REAL: balkan's kick sits on the 2+2+3 group heads
        bb = cache["balkan_brass"]["grid"]
        check("H: balkan_brass kicks the aksak heads (0,8), not four-on-the-floor",
              bb["kick"] == [0, 8] and bb.get("groups") == [2, 2, 3], str(bb["kick"]))
    finally:
        for p in made:
            if p and os.path.exists(p):
                os.remove(p)

    print(f"\n{N['pass']} passed, {N['fail']} failed")
    sys.exit(1 if N["fail"] else 0)


if __name__ == "__main__":
    main()
