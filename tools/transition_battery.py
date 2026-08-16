#!/usr/bin/env python3
"""TRANSITION BATTERY — proves THE TRANSITION OPS (wave 26; R-15
072/073/075). Pure, deterministic."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transition_ops as TO  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


# ------------------------------------------------------------- riser (072)
r = TO.riser(32.0, bars=2, bpm=120, kind="tonal")
n = r["notes"][0]
check("riser: one note ENDING at the boundary",
      n["start"] + n["len"] == 32.0 and n["start"] == 24.0, str(n))
check("riser: sweep matches the build length in seconds",
      r["source"]["params"]["sweep"] == 4.0, str(r["source"]))
pts = r["automation"][0]["points"]
check("riser: late-bloom gain swell (curve>0, lands at the boundary)",
      pts[-1]["beat"] == 32.0 and pts[-1]["curve"] > 0 and
      pts[0]["v"] < pts[-1]["v"], str(pts))
rn = TO.riser(16.0, kind="noise")
check("riser: noise kind rides rev_crash", rn["source"]["id"] == "rev_crash")
check("riser: deterministic",
      TO.riser(32.0, 2, 120) == TO.riser(32.0, 2, 120))

# ------------------------------------------------------ filter_sweep (073)
t = {"name": "pad", "fx": [], "notes": []}
led = TO.filter_sweep(t, 400, 12000, 24.0, bars=2)
check("sweep: fx_filter inserted when absent",
      t["fx"][0]["id"] == "fx_filter" and
      t["fx"][0]["params"]["cutoff"] == 400.0, str(t["fx"]))
a = t["automation"][0]
check("sweep: automation targets the right fx index, lands at boundary",
      a["target"] == "fx[0].cutoff" and a["points"][-1]["beat"] == 32.0 and
      a["points"][-1]["v"] == 12000.0, str(a))
t2 = {"name": "pad", "fx": [{"id": "fx_reverb", "params": {}},
                            {"id": "fx_filter", "params": {"cutoff": 800}},
                            {"id": "fx_truepeak", "params": {}}], "notes": []}
TO.filter_sweep(t2, 300, 9000, 0.0)
check("sweep: existing fx_filter reused at its true index",
      t2["automation"][0]["target"] == "fx[1].cutoff",
      str(t2["automation"]))
t3 = {"name": "bus", "fx": [{"id": "fx_truepeak", "params": {}}]}
TO.filter_sweep(t3, 300, 9000, 0.0)
check("sweep: absent filter inserts BEFORE the wall",
      t3["fx"][0]["id"] == "fx_filter" and
      t3["fx"][1]["id"] == "fx_truepeak", str(t3["fx"]))

# -------------------------------------------------------- gap_impact (075)
song = {"bpm": 128, "tracks": [
    {"name": "kick", "notes": [{"start": float(b), "len": 0.4, "pitch": 36,
                                "vel": 0.9} for b in range(28, 36)]},
    {"name": "pad", "notes": [{"start": 30.0, "len": 3.0, "pitch": 60,
                               "vel": 0.7}]},
    {"name": "riser_tonal_32", "notes": [{"start": 24.0, "len": 8.0,
                                          "pitch": 45, "vel": 0.85}]}]}
led = TO.gap_impact(song, 32.0, gap_beats=1.0)
kick = song["tracks"][0]["notes"]
check("gap: onsets inside [31,32) cleared",
      all(not (31.0 <= n["start"] < 32.0) for n in kick), str(led))
check("gap: the downbeat note itself survives",
      any(n["start"] == 32.0 for n in kick))
pad = song["tracks"][1]["notes"][0]
check("gap: tails crossing in are TRIMMED to the gap edge",
      pad["len"] == 1.0, str(pad))
check("gap: riser lanes exempt (they LIVE in the gap)",
      song["tracks"][2]["notes"][0]["len"] == 8.0)
imp = next(t for t in song["tracks"] if t["name"] == "impact")
check("gap: crash_noise impact lands ON the downbeat",
      imp["source"]["id"] == "crash_noise" and
      imp["notes"][0]["start"] == 32.0)
TO.gap_impact(song, 32.0, gap_beats=1.0)
check("gap: idempotent (one impact per boundary)",
      len(imp["notes"]) == 1)

# ------------------------------------------------ 133 turnaround (w59)
ts = {"bpm": 120, "lengthBars": 16, "key": "C major",
      "chords": [{"bar": 15, "chord": "F", "conf": 0.8}],
      "tracks": [{"name": "keys_warm", "notes": [
          {"start": 56.0, "len": 4.0, "pitch": 60, "vel": 90},
          {"start": 60.0, "len": 4.0, "pitch": 64, "vel": 90}]}]}
eds = TO.turnaround(ts, "jazz")
got = {c["bar"]: c["chord"] for c in ts["chords"]}
check("turnaround: jazz in C lands Dm7 -> G7 on the last two bars",
      got.get(15) == "Dm7" and got.get(16) == "G7", str(got))
check("turnaround: the comp lane re-voices those bars (old notes out, "
      "voicings in, len 4)",
      all(float(n["start"]) >= 56.0 for n in ts["tracks"][0]["notes"]) and
      len(ts["tracks"][0]["notes"]) >= 6 and
      any(n["pitch"] % 12 == 2 for n in ts["tracks"][0]["notes"]), str(eds))
tb = {"bpm": 100, "lengthBars": 12, "key": "A major", "tracks": []}
TO.turnaround(tb, "delta blues")
gb = {c["bar"]: c["chord"] for c in tb.get("chords", [])}
check("turnaround: blues in A = A7 -> E7 (bars 11-12)",
      gb.get(11) == "A7" and gb.get(12) == "E7", str(gb))
tg = {"bpm": 90, "lengthBars": 8, "key": "C major", "tracks": []}
TO.turnaround(tg, "gospel", tritone_sub=True)
gg = {c["bar"]: c["chord"] for c in tg.get("chords", [])}
check("turnaround: gospel w/ tritone sub = Am7 -> Db7 (the subV)",
      gg.get(7) == "Am7" and gg.get(8) == "Db7", str(gg))
check("turnaround: no declared key = no-op (never guesses harmony)",
      TO.turnaround({"bpm": 120, "lengthBars": 16, "tracks": []},
                    "jazz") == [])

# ------------------------------------------ 208/209 gesture ops (w61)
rs = TO.reverse_swell(32.0, bars_ahead=1, bpm=120)
check("reverse_swell: rev_crash lane ends AT the boundary (1-bar "
      "pre-roll)",
      rs["source"]["id"] == "rev_crash" and
      rs["notes"][0]["start"] == 28.0 and
      rs["notes"][0]["start"] + rs["notes"][0]["len"] == 32.0, str(rs))
tsong = {"bpm": 128, "lengthBars": 16, "master": [
    {"id": "fx_truepeak", "params": {"ceiling": -1.2}}], "tracks": []}
eds = TO.tape_stop(tsong, 24.0, 2.0)
knob = next(a for a in tsong["automation"]
            if a["target"].startswith("master[") and
            a["target"].endswith(".knob"))
mg = next(a for a in tsong["automation"] if a["target"] == "masterGainDb")
check("tape_stop: djfilter inserted BEFORE the wall, knob dives dark "
      "then snaps back",
      tsong["master"][0]["id"] == "fx_djfilter" and
      knob["target"] == "master[0].knob" and
      knob["points"][1]["v"] < -0.8 and knob["points"][2]["v"] == 0.0,
      str(tsong["master"]) + str(knob))
check("tape_stop: masterGainDb dives -24 (early-jump curve) and "
      "recovers; the subdrop lands the fall",
      mg["points"][1]["v"] == -24.0 and mg["points"][1]["curve"] < 0 and
      any(t["source"]["id"] == "subdrop" for t in tsong["tracks"]),
      str(mg))

print()
if FAILS:
    print(f"transition_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("transition_battery: ALL GREEN")
