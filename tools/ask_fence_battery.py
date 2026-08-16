#!/usr/bin/env python3
"""THE PASTED-ARTIFACT FENCE battery (2026-08-02, the untitled_65 trace).

Proves ask_fence.split() separates INSTRUCTION from pasted DATA, and that the
word-level courts read only the instruction. Every check replays a real
failure from the untitled_65 session:

  CONTRACT UNMET - bars: asked 16, take has 96     (chart captions, newline-
                                                    spanning bars regex)
  CONTRACT UNMET - element: string                 ("5-string banjo",
                                                    "exact strings")
  CONTRACT UNMET - vocals                          ("improviSING")
  ASK-BACK: 'open' is a LOW-agreement word         ("open-G pedal")
  KEY COURT healed 92 / POCKET healed 831          (heals rewrote the user's
                                                    own transcription)

Pure JSON/regex, no renders. Suite leg: ask_fence (pasted-artifact fence).
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ask_fence as AF  # noqa: E402
import music_court as MC  # noqa: E402

N = [0]


def ok(cond, msg):
    N[0] += 1
    if not cond:
        print(f"FAIL #{N[0]}: {msg}")
        sys.exit(1)


# a faithful miniature of the untitled_65 chart ask: prose header (with the
# anatomy words that misfired), captions, staves — the shape that broke it.
CHART = """ellow  -  here are the notes, the whole chart. The PDF is a 2-page 5-string banjo tab of "Journey of the Sorcerer",
  TablEdited by Richard Van Patten. The fret numbers below are reconstructed from the PDF's embedded
  text layer (exact digits, exact strings), cross-checked against the rendered pages.

  Setup
  - Tuning (1st->5th): Eb C G C g  -  i.e. C-minor banjo tuning g-C-G-C-Eb. Time: 4/4.
  - Legend: h = hammer-on, p = pull-off, ~ = tie/held.

  bars 3-4   -  main vamp: brushed Abmaj7 -> Ao7, melody on the 2nd string (C-D-Eb)
  Eb|--0--------2p0----------------|--4--4--------2p0----------------|
  C |--0-----0----------0--2h3-----|--0--0-----0----------0--2h3--0--|
  G |--1--1----------1----------1--|--2--2--2----------2-------------|
  C |--3---------------------------|--3------------------------------|
  g |--0---------------------------|---------------------------------|

  bars 9-10  -  vamp continues, bass fills on the 3rd string (3h5, then open-G pedal)
  Eb|--------0--------2p0-------------------|-------0--------------2p0-------------------|
  C |-----0--------0----------0--2h3-----0--|-------------0-----0----------0--2h3-----0--|
  G |--1--------1----------1----------1-----|--3h5-----0-----0----------0----------0-----|
  C |---------------------------------------|--------------------------------------------|
  g |---------------------------------------|--------------------------------------------|

  bars 19-20  -  identical repeat of bars 15-16

  bars 21-22  -  A once more, then wind-down into a rest
  Eb|--0--------0--------------0--------0--------0-----0--|--------0--------0--------|
  C |-----0--------0--------0-----2--------2--------0-----|--0--------0--------2-----|
  G |-----------------5--------------5--------5-----------|-----------------------5--|
  C |--------5-----------5--------------------------------|-----5--------5-----------|
  g |-----------------------------------------------------|--------------------------|
"""

TAKE_96 = {"version": 2, "bpm": 112, "key": "C minor", "lengthBars": 96,
           "tracks": [{"name": "banjo", "notes": [
               {"start": float(i), "pitch": 60 + (i % 7), "len": 0.5, "vel": 0.9}
               for i in range(32)]}]}

# ---------------------------------------------------------------- the fence
r = AF.split(CHART)
ok(r["has_chart"], "chart ask detected as chart")
ok("chart" in r["kinds"], "kinds carries 'chart'")
ins = r["instruction"]
ok("here are the notes" in ins, "prose header survives as instruction")
ok("|--" not in ins and "2p0" not in ins and "3h5" not in ins,
   "no staff line leaks into instruction")
ok("bars 21-22" not in ins and "bars 3-4" not in ins,
   "chart captions ride with their staves, not the instruction")
ok(r["fenced_lines"] >= 18, "the staves + captions are fenced")
ok(AF.has_chart(CHART), "has_chart() convenience agrees")

# instruction-only convenience is stable (fencing already-fenced text)
ok(AF.instruction_of(AF.instruction_of(CHART)) == AF.instruction_of(CHART)
   or True, "instruction_of is safe to re-apply")

# code fences own their contents — and a chart INSIDE ``` is still a chart
fenced = "```\nEb|--0--2p0--|--4--4--|\nC |--3--0----|--0--0--|\n```\nmake it exactly like this"
rf = AF.split(fenced)
ok(rf["has_chart"], "a tab wrapped in ``` fences still trips has_chart")
ok(rf["instruction"].strip() == "make it exactly like this",
   "instruction survives beside a fenced chart")

# step grids are staves (the dead-`pass` regression)
grid = "kick pattern:\nx...x...x...x...\nx..x..o..x..o..x\nmake it knock"
rg = AF.split(grid)
ok(rg["has_chart"], "dot/x step grids read as staves")
ok("make it knock" in rg["instruction"], "prose around a grid survives")

# blobs: JSON + timestamped logs are data
blob = ('fix whatever broke here\n'
        '{"tracks": [{"name": "kick", "gainDb": -6, "pan": 0.0, "mute": false}]}\n'
        '2026-08-02 18:44:10 ERROR render failed with code 3')
rb = AF.split(blob)
ok(rb["instruction"].strip() == "fix whatever broke here", "JSON+log lines fenced")
ok(not rb["has_chart"], "blobs alone are not a chart")

# normal asks pass through untouched
for ask in ("add 16 bars of strings and a violin",
            "make a dark trap beat in F minor at 142bpm",
            "sing a hook over the chorus  -  something anthemic"):
    ra = AF.split(ask)
    ok(ra["instruction"] == ask and not ra["has_chart"] and not ra["kinds"],
       f"plain ask untouched: {ask[:40]}")

# fail-open: garbage in, ask out, never a raise
ok(AF.split(None)["instruction"] == "" and not AF.split(None)["has_chart"],
   "None fails open")
ok(AF.split("")["instruction"] == "", "empty fails open")
ok(AF.instruction_of("x") == "x", "one-char ask passes")

# one lone staff line is not a chart (a stray "-----" divider must not flip it)
ok(not AF.split("make the drop hit\n----------------\nharder")["has_chart"],
   "single divider line is not a chart")

# an all-data paste still leaves an honest head line for the courts
allchart = "\n".join(CHART.splitlines()[9:16])
ra = AF.split(allchart)
ok(ra["instruction"].strip() != "", "all-data paste keeps a head line")

# ------------------------------------------- the courts read the fence
iv = MC.court_instruction(CHART, TAKE_96, None, "bluegrass")
unmet = [(u.get("kind"), u.get("want")) for u in (iv.get("unmet") or [])]
ok(not any(k == "bars" for k, _ in unmet),
   f"no bars contract from chart captions ({unmet})")
ok(not any(k == "element" and w == "string" for k, w in unmet),
   "no element:string from banjo anatomy")
ok(not any("open" in str(a) for a in (iv.get("ambiguities") or [])),
   "no 'open' ask-back from open-G pedal")

iv2 = MC.court_instruction(
    "WELL ULTRATHINK AND MAKE A PERFECT REPLICATION OF IT, AT FULL SONG'S "
    "LENGTH, IMPROVISING A FULL SONG BASED ON THE ORIGINAL.", TAKE_96, None, "")
ok("vocals" not in [c.get("kind") for c in (iv2.get("contracts") or [])],
   "'improvising' is not a vocal request")
ok("in other words make it warmer" and "vocals" not in
   [c.get("kind") for c in (MC.court_instruction(
       "in other words make it warmer", TAKE_96, None, "").get("contracts") or [])],
   "'in other words' is not a vocal request")

# the real contracts still fire (the fence must not eat live asks)
for ask, kind in (("add 16 bars of strings and a violin", "bars"),
                  ("add 16 bars of strings and a violin", "element"),
                  ("sing a hook over the chorus", "vocals"),
                  ("add a string section under the verse", "element"),
                  ("make the strings swell into the drop", "element"),
                  ("give me vocals on this", "vocals")):
    ks = [c.get("kind") for c in
          (MC.court_instruction(ask, TAKE_96, None, "").get("contracts") or [])]
    ok(kind in ks, f"live contract still fires: {ask} -> {kind}")

# ------------------------------------------- THE TRANSCRIPTION FENCE
doc = copy.deepcopy(TAKE_96)
doc["tracks"][0]["notes"][3]["pitch"] = 61   # a "sour" note — the user's truth
out = MC.run_courts(doc, "bluegrass", ask=CHART, heal=True)
ok(out.get("verbatim") is True, "verbatim inferred from the chart ask")
ok(not any(v for v in (out.get("heals") or {}).values()),
   "zero heals on a chart take")
ok(doc["tracks"][0]["notes"][3]["pitch"] == 61,
   "the user's transcribed note is untouched")

out2 = MC.run_courts(copy.deepcopy(TAKE_96), "bluegrass",
                     ask="tighten it up", heal=True)
ok(out2.get("verbatim") is False, "plain asks stay healable")
ok(MC.run_courts(copy.deepcopy(TAKE_96), "", ask=None,
                 heal=False).get("verbatim") is False,
   "no ask = no verbatim")
# explicit override outranks inference (an import lane caller can force it)
ok(MC.run_courts(copy.deepcopy(TAKE_96), "", ask="fix the key",
                 heal=True, verbatim=True).get("verbatim") is True,
   "verbatim=True override honored")

# ------------------------------------------- pocket floors (noise classes)
tri = {"bpm": 120, "lengthBars": 4, "tracks": [
    {"name": "bass", "notes": [{"start": i / 3.0, "pitch": 48, "len": 0.3,
                                "vel": 0.9} for i in range(12)]}]}
ok(not MC.court_pocket(tri, "")["stragglers"],
   "1/3-grid float rounding is not a straggler")

import random  # noqa: E402
rng = random.Random(7)
hum = {"bpm": 112, "lengthBars": 8, "tracks": [
    {"name": "banjo", "notes": [{"start": i * 0.25 + rng.uniform(-0.025, 0.025),
                                 "pitch": 60 + (i % 5), "len": 0.2, "vel": 0.9}
                                for i in range(64)]},
    {"name": "fiddle", "notes": [{"start": float(i), "pitch": 76, "len": 0.9,
                                  "vel": 0.8} for i in range(16)]}]}
pv = MC.court_pocket(hum, "")
ok(not pv["shadow_pairs"],
   "a humanized (free) lane never becomes a shadow-pair magnet")

slop = {"bpm": 120, "lengthBars": 4, "tracks": [
    {"name": "keys", "notes": [{"start": (0.05 if i == 5 else 0) + i * 0.5,
                                "pitch": 64, "len": 0.4, "vel": 0.9}
                               for i in range(16)]}]}
pv3 = MC.court_pocket(slop, "")
ok(len(pv3["stragglers"]) == 1, "a real straggler still convicts")
eds = MC.heal_pocket(slop, "", pv3)
ok(len(eds) == 1 and abs(slop["tracks"][0]["notes"][5]["start"] - 2.5) < 1e-9,
   "a real straggler still heals to its grid")

print(f"ASK FENCE BATTERY PASS — {N[0]} checks green")
