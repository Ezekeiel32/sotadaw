#!/usr/bin/env python3
"""Battery for agent/surgical.py — THE SCALPEL. Pure, fast, zero deps.
Run: python3 tools/surgical_battery.py   (exit 0 = all green)"""
import copy, json, math, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agent"))
import surgical as S

N = {"pass": 0, "fail": 0}
def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))

def approx(a, b, tol=1e-3):
    return abs(a - b) <= tol

# ---------------------------------------------------------------- fixture
def fixture():
    return {
        "version": 2, "bpm": 120.0, "key": "Fm", "lengthBars": 16, "masterGainDb": 0,
        "sections": [{"name": "intro", "startBar": 0}, {"name": "drop", "startBar": 4},
                     {"name": "verse", "startBar": 8}, {"name": "drop", "startBar": 12}],
        "tracks": [
            {"name": "Kick", "source": {"kind": "faust", "id": "kick_808"}, "gainDb": -6, "pan": 0,
             "notes": [{"start": float(b), "len": 0.2, "pitch": 36, "vel": 0.9} for b in range(0, 64, 1)]},
            {"name": "Sub Bass", "source": {"kind": "faust", "id": "bass_sub"}, "gainDb": -8, "pan": 0,
             "notes": [{"start": 16.0 + i * 2.0, "len": 1.5, "pitch": 29 + (i % 2) * 3, "vel": 0.8}
                       for i in range(8)]},
            {"name": "hats", "source": {"kind": "sample", "kit": "hats_909"}, "gainDb": -12, "pan": 0.1,
             "notes": [{"start": 16.0 + i * 0.5, "len": 0.1, "pitch": 42, "vel": 0.6 if i % 2 else 0.7}
                       for i in range(32)],
             "automation": [{"target": "gainDb", "points": [{"beat": 16, "v": -20}, {"beat": 32, "v": -6}]}]},
            {"name": "Dream Pad", "source": {"kind": "vst3", "plugin": "Surge XT"}, "gainDb": -10, "pan": -0.2,
             "notes": [{"start": 32.0, "len": 8.0, "pitch": 65, "vel": 0.5},
                       {"start": 32.0, "len": 8.0, "pitch": 68, "vel": 0.5},
                       {"start": 40.0, "len": 8.0, "pitch": 70, "vel": 0.55}]},
        ],
    }

# ---------------------------------------------------------------- pitch
check("pitch_name C4=60", S.pitch_name(60) == "C4")
check("pitch_name F1=29", S.pitch_name(29) == "F1")
check("parse_pitch_name F#2", S.parse_pitch_name("F#2") == 42)
check("parse_pitch_name Gb2 == F#2", S.parse_pitch_name("Gb2") == 42)
check("parse_pitch_class Bb", S.parse_pitch_class("Bb") == 10)

# ---------------------------------------------------------------- tempo clock
song = fixture()
clk = S.TempoClock(song)
check("clock const 120bpm: beat 64 -> 32s", approx(clk.seconds_at(64), 32.0))
check("clock inverse: 32s -> beat 64", approx(clk.beat_at(32.0), 64.0, 5e-3))

step = fixture(); step["tempoMap"] = [{"bar": 8, "bpm": 140}]           # default curve 1 = step at bar 8
ck = S.TempoClock(step)
check("step: beat 32 -> 16s", approx(ck.seconds_at(32), 16.0))
t_want = 16.0 + 32 * 60.0 / 140.0
check("step: beat 64 -> 16 + 32*60/140", approx(ck.seconds_at(64), t_want))
check("step inverse round-trip", approx(ck.beat_at(t_want), 64.0, 5e-3))
check("step bpm_at(40) = 140", approx(ck.bpm_at(40), 140.0))

ramp = fixture(); ramp["bpm"] = 120.0
ramp["tempoMap"] = [{"bar": 0, "bpm": 120, "curve": 0}, {"bar": 8, "bpm": 160}]   # linear 120->160 over bars 0..8
rk = S.TempoClock(ramp)
analytic = 60.0 * 32 / 40.0 * math.log(160.0 / 120.0)
check("linear ramp analytic seconds", approx(rk.seconds_at(32), analytic, 1e-2), f"{rk.seconds_at(32)} vs {analytic}")
check("ramp inverse round-trip", approx(rk.beat_at(rk.seconds_at(20)), 20.0, 5e-3))
check("parse mm:ss", approx(S.parse_timestamp("1:23"), 83.0))
check("parse mm:ss.ms", approx(S.parse_timestamp("1:23.45"), 83.45))
check("parse 83.5s", approx(S.parse_timestamp("83.5s"), 83.5))
check("parse bare float", approx(S.parse_timestamp("12.25"), 12.25))

# ---------------------------------------------------------------- sections
spans = S.section_spans(song)
check("section spans count", len(spans) == 4)
check("drop #1 = beats 16..32", spans[1] == ("drop", 16.0, 32.0))
check("last section ends at song end", spans[-1][2] == 64.0)
check("find_section ci", S.find_section(song, "DROP")[1] == 16.0)
check("find_section occurrence 2", S.find_section(song, "drop", 2)[1] == 48.0)
check("section_at beat 20 = drop", S.section_at(song, 20)[0] == "drop")

# ---------------------------------------------------------------- roles + query
roles = {t["name"]: S.track_role(t)[0] for t in song["tracks"]}
check("role kick", roles["Kick"] == "kick")
check("role bass", roles["Sub Bass"] == "bass")
check("role hats", roles["hats"] == "hat")
check("role pad", roles["Dream Pad"] == "pad")
sc = S.score_track_query(song, "the boomy 808 sub")
check("query 'boomy 808 sub' -> Sub Bass or Kick first", sc and song["tracks"][sc[0][1]]["name"] in ("Sub Bass", "Kick"))
sc2 = S.score_track_query(song, "dreamy pad")
check("query 'dreamy pad' -> Dream Pad", sc2 and song["tracks"][sc2[0][1]]["name"] == "Dream Pad")

# ---------------------------------------------------------------- resolve
r = S.resolve(song, {"tracks": "kick", "bars": [4, 8]})
check("kick bars 4-8 -> 16 notes", len(r.refs) == 16, str(len(r.refs)))
r = S.resolve(song, {"tracks": {"role": "bass"}, "section": "drop"})
check("bass in drop -> 8 notes", len(r.refs) == 8, str(len(r.refs)))
r = S.resolve(song, {"tracks": "hats", "grid": {"step": 1.0, "phase": 0.5, "tol": 0.05}})
check("offbeat hats (phase .5 of beat) -> 16", len(r.refs) == 16, str(len(r.refs)))
r = S.resolve(song, {"tracks": "kick", "section": "drop", "nth": 3})
check("3rd kick of the drop = beat 18", len(r.refs) == 1 and r.refs[0][1]["start"] == 18.0)
r = S.resolve(song, {"tracks": "hats", "every": {"step": 2, "phase": 1}})
check("every 2nd hat (phase 1) -> 16", len(r.refs) == 16, str(len(r.refs)))
r = S.resolve(song, {"tracks": "Sub Bass", "pitch": {"classes": ["F"]}})
check("bass pitch-class F -> 4 notes", len(r.refs) == 4 and all(n["pitch"] == 29 for _, n in r.refs))
r = S.resolve(song, {"tracks": "Dream Pad", "pitch": "F4"})
check("pad pitch F4(65) by name -> 1", len(r.refs) == 1 and r.refs[0][1]["pitch"] == 65)
r = S.resolve(song, {"tracks": "kick", "time": ["0:08", "0:10"]})
check("kick 0:08-0:10 @120bpm = beats 16..20 -> 4", len(r.refs) == 4, str(len(r.refs)))
r = S.resolve(song, {"tracks": "kick", "around": {"time": "0:16", "widthBeats": 2}})
check("around 0:16 ±1 beat -> ~2 kicks", len(r.refs) == 2, str(len(r.refs)))
r = S.resolve(song, {"tracks": "hats", "indices": [0, 2, 4]})
check("indices form -> 3 notes", len(r.refs) == 3)
r = S.resolve(song, {"tracks": "hats", "vel": {"min": 0.65}})
check("hats vel>=.65 -> downbeat 16", len(r.refs) == 16, str(len(r.refs)))
try:
    S.resolve(song, {"tracks": "nonexistent"})
    check("bad track raises", False)
except ValueError as e:
    check("bad track raises", "no track matching" in str(e))
try:
    S.resolve(song, {"tracks": "kick", "nth": 999})
    check("nth out of range raises", False)
except ValueError as e:
    check("nth out of range raises", "out of range" in str(e))

# ---------------------------------------------------------------- whats_at
w = S.whats_at(song, 33.0)
names = {t["track"]: t for t in w["tracks"]}
check("whats_at: pad sounding at 33", "Dream Pad" in names and len(names["Dream Pad"]["sounding"]) == 2)
check("whats_at: section verse", w["section"]["name"] == "verse")
check("whats_at: clock time", w["clockTime"] == "0:16.50")
w24 = S.whats_at(song, 24.0)
n24 = {t["track"]: t for t in w24["tracks"]}
check("whats_at: hats sounding at 24 with live automation value",
      "hats" in n24 and approx(n24["hats"]["automationNow"][0]["value"], -13.0, 0.01))
check("automation_value_at mid-curve", approx(
    S.automation_value_at([{"beat": 16, "v": -20}, {"beat": 32, "v": -6}], 24.0), -13.0, 0.01))
txt = S.render_whats_at(w)
check("render_whats_at mentions pad", "Dream Pad" in txt)

# ---------------------------------------------------------------- ops
s2 = fixture()
rc, _ = S.apply_ops(s2, {"tracks": "Sub Bass", "section": "drop"}, [{"op": "shift", "pitch": 2}])
check("transpose: all bass +2 in drop", all(n["pitch"] in (31, 34) for n in s2["tracks"][1]["notes"]))
check("receipt keys count", len(rc["removed_keys"]) == 8 and len(rc["added_keys"]) == 8)
check("receipt summary text", "Sub Bass" in rc["summary"])

s3 = fixture()
rc3, _ = S.apply_ops(s3, {"tracks": "hats", "grid": {"step": 1.0, "phase": 0.5, "tol": 0.05}},
                     [{"op": "scale", "vel": 0.5}])
offs = [n for n in s3["tracks"][2]["notes"] if (n["start"] - 0.5) % 1.0 < 0.05]
ons = [n for n in s3["tracks"][2]["notes"] if n["start"] % 1.0 < 0.05]
check("offbeat hats halved", all(approx(n["vel"], 0.3) for n in offs))
check("onbeat hats untouched", all(approx(n["vel"], 0.7) for n in ons))

s4a, s4b = fixture(), fixture()
S.apply_ops(s4a, {"tracks": "hats"}, [{"op": "humanize", "timing": 0.03, "vel": 0.1, "seed": "x"}])
S.apply_ops(s4b, {"tracks": "hats"}, [{"op": "humanize", "timing": 0.03, "vel": 0.1, "seed": "x"}])
check("humanize deterministic", json.dumps(s4a) == json.dumps(s4b))
s4c = fixture()
S.apply_ops(s4c, {"tracks": "hats"}, [{"op": "humanize", "timing": 0.03, "vel": 0.1, "seed": "y"}])
check("humanize seed matters", json.dumps(s4a) != json.dumps(s4c))

s5 = fixture()
S.apply_ops(s5, {"tracks": "hats"}, [{"op": "quantize", "grid": 0.5}, {"op": "quantize", "grid": 0.5}])
q1 = json.dumps(s5["tracks"][2]["notes"])
check("quantize idempotent", q1 == json.dumps(fixture()["tracks"][2]["notes"]))

# split — THE KNIFE's agent twin (mirrors the roll's hold-K)
s5s = fixture()
kick0 = len(s5s["tracks"][0]["notes"])
len0 = sum(n["len"] for n in s5s["tracks"][0]["notes"])
rc5s, _ = S.apply_ops(s5s, {"tracks": "Kick"}, [{"op": "split", "ratio": 0.5}])
kickNotes = s5s["tracks"][0]["notes"]
check("split ratio doubles the note count", len(kickNotes) == kick0 * 2)
check("split conserves total note length", approx(sum(n["len"] for n in kickNotes), len0, 1e-4))
check("split receipt authorizes the tails (scope law)",
      len(rc5s["added_keys"]) > len(rc5s["removed_keys"]))
# split 'at' a beat only cuts the note spanning it (Sub Bass note starts at 16, len 1.5)
s5a = fixture()
sub0 = len(s5a["tracks"][1]["notes"])
S.apply_ops(s5a, {"tracks": "Sub Bass"}, [{"op": "split", "at": 16.75}])
spanned = [n for n in s5a["tracks"][1]["notes"] if n["start"] in (16.0, 16.75)]
check("split at-beat cuts only the spanning note", len(s5a["tracks"][1]["notes"]) == sub0 + 1
      and len(spanned) == 2)

# edit_audio_clip — the agent twin of the hands' HB3.1 clip verbs
sc = fixture()
sc["tracks"][0]["audioClips"] = [{"file": "x.wav", "startBeat": 0.0, "lengthBeats": 4.0,
                                  "offsetSec": 0.0, "gainDb": 0.0}]
S.edit_audio_clip(sc, 0, 0, "move", 8.0)
check("clip move", sc["tracks"][0]["audioClips"][0]["startBeat"] == 8.0)
S.edit_audio_clip(sc, 0, 0, "fade_in", 999.0)          # must clamp to length (4)
check("clip fade_in clamps to length", sc["tracks"][0]["audioClips"][0]["fadeInBeats"] <= 4.0 + 1e-9)
S.edit_audio_clip(sc, 0, 0, "gain", -6.0)
check("clip gain", sc["tracks"][0]["audioClips"][0]["gainDb"] == -6.0)
S.edit_audio_clip(sc, 0, 0, "fade_in", 0.0)            # clean slate for split
n0 = len(sc["tracks"][0]["audioClips"])
S.edit_audio_clip(sc, 0, 0, "split", 10.0)             # clip 8..12 -> head 8..10, tail 10..12
clipset = sc["tracks"][0]["audioClips"]
tailc = [c for c in clipset if approx(c["startBeat"], 10.0)]
check("clip split makes 2 sharing the file", len(clipset) == n0 + 1
      and all(c["file"] == "x.wav" for c in clipset))
check("clip split tail offset picks up (2 beats @120bpm = 1.0s)",
      len(tailc) == 1 and approx(tailc[0]["offsetSec"], 1.0))
S.edit_audio_clip(sc, 0, 0, "remove", None)            # remove the head
check("clip remove", len(sc["tracks"][0]["audioClips"]) == n0)
try:
    S.edit_audio_clip(sc, 0, 0, "split", 999.0)        # out-of-clip beat must raise
    check("clip split rejects out-of-range beat", False)
except ValueError:
    check("clip split rejects out-of-range beat", True)

# per-note chance (HB5) — settable via the 'set' op, clamped to [0,1]
sch = fixture()
S.apply_ops(sch, {"tracks": "hats"}, [{"op": "set", "chance": 0.5}])
check("chance: set writes 0.5 on matched notes",
      all(abs(n.get("chance", 1.0) - 0.5) < 1e-9 for n in sch["tracks"][2]["notes"]))
S.apply_ops(sch, {"tracks": "hats", "indices": [0]}, [{"op": "set", "chance": 2.0}])  # over-range
check("chance: clamps to [0,1]", sch["tracks"][2]["notes"][0]["chance"] == 1.0)

s6 = fixture()
rc6, _ = S.apply_ops(s6, {"tracks": "kick", "bars": [4, 6]},
                     [{"op": "velocity_ramp", "from": 0.3, "to": 1.0}])
vs = [n["vel"] for n in s6["tracks"][0]["notes"] if 16 <= n["start"] < 24]
check("velocity_ramp monotone", all(vs[i] <= vs[i + 1] + 1e-9 for i in range(len(vs) - 1)) and approx(vs[0], 0.3))

s7 = fixture()
rc7, _ = S.apply_ops(s7, {"tracks": "kick", "bars": [4, 5]}, [{"op": "delete"}])
check("delete: bar 4 kicks gone", not [n for n in s7["tracks"][0]["notes"] if 16 <= n["start"] < 20])
check("delete receipt: 4 removed 0 added", len(rc7["removed_keys"]) == 4 and len(rc7["added_keys"]) == 0)

s8 = fixture()
try:
    S.apply_ops(s8, {"tracks": "kick", "bars": [4, 5]},
                [{"op": "insert", "notes": [{"start": 40.0, "pitch": 36, "vel": 0.9}]}])
    check("insert outside range rejected", False)
except ValueError as e:
    check("insert outside range rejected", "OUTSIDE" in str(e))
rc8, _ = S.apply_ops(s8, {"tracks": "kick", "bars": [4, 5]},
                     [{"op": "insert", "notes": [{"start": 16.5, "pitch": "F#1", "vel": 0.9}]}])
check("insert pitch-by-name lands", any(n["pitch"] == 30 and n["start"] == 16.5 for n in s8["tracks"][0]["notes"]))

s9 = fixture()
rc9, _ = S.apply_ops(s9, {"tracks": "Dream Pad", "pitch": "A#4"},
                     [{"op": "shift", "start": 24.0}])          # push last pad note past the end
check("auto-extend lengthBars", s9["lengthBars"] > 16 and "meta:lengthBars" in rc9["prop_changes"])

s10 = fixture()
rc10, _ = S.apply_ops(s10, {"tracks": "hats", "bars": [4, 5]}, [{"op": "retrack", "to": "Dream Pad"}])
check("retrack moved 8 hats to pad", sum(1 for n in s10["tracks"][3]["notes"] if n["pitch"] == 42) == 8
      and not [n for n in s10["tracks"][2]["notes"] if 16 <= n["start"] < 20])

s11 = fixture()
rc11, _ = S.apply_ops(s11, {"tracks": "Sub Bass", "section": {"name": "drop", "occurrence": 1}, "nth": 1},
                      [{"op": "replace", "notes": [{"start": 16.0, "len": 3.0, "pitch": 24, "vel": 0.95}]}])
check("replace 1st drop bass onset", any(n["pitch"] == 24 and n["len"] == 3.0 for n in s11["tracks"][1]["notes"]))

# ---------------------------------------------------------------- diff + LAW
base, prop = fixture(), fixture()
prop["tracks"][2]["notes"][0]["vel"] = 0.95                     # vel tweak = changed
prop["tracks"][0]["notes"] = prop["tracks"][0]["notes"][1:]     # kick removed
prop["tracks"][1]["gainDb"] = -5                                # prop change
prop["bpm"] = 124.0                                             # meta change
d = S.semantic_diff(base, prop)
check("diff meta bpm", d["meta"]["bpm"] == [120.0, 124.0])
check("diff kick note removed", d["tracks"]["changed"]["Kick"]["notes"]["detail"]["n_removed"] == 1)
check("diff hats note changed (not add+remove)", d["tracks"]["changed"]["hats"]["notes"]["detail"]["n_changed"] == 1
      and d["tracks"]["changed"]["hats"]["notes"]["detail"]["n_added"] == 0)
check("diff bass gainDb", d["tracks"]["changed"]["Sub Bass"]["props"]["gainDb"] == [-8, -5])

law = S.containment(d, [])
check("LAW: nothing receipted -> all out of scope", not law["clean"] and len(law["out_of_scope"]) == 4)

receipts = [
    {"removed_keys": [["Kick", 0.0, 36]], "added_keys": [], "scope": {"tracks": ["Kick"]}},
    {"removed_keys": [["hats", 16.0, 42]], "added_keys": [["hats", 16.0, 42]], "scope": {"tracks": ["hats"]}},
    {"fields": ["track:Sub Bass:gainDb", "meta:bpm"], "track_wild": []},
]
law2 = S.containment(d, receipts)
check("LAW: fully receipted -> clean", law2["clean"], "; ".join(law2["out_of_scope"]))

receipts_partial = receipts[:2]
law3 = S.containment(d, receipts_partial)
check("LAW: partial receipts -> gain+bpm flagged", not law3["clean"] and len(law3["out_of_scope"]) == 2)

wild = [{"track_wild": ["Kick", "hats"], "fields": ["meta:bpm", "track:Sub Bass:gainDb"]}]
law4 = S.containment(d, wild)
check("LAW: coarse track_wild explains note edits", law4["clean"], "; ".join(law4["out_of_scope"]))

# end-to-end: surgical edit produces a diff its OWN receipt fully explains
b2 = fixture()
p2 = copy.deepcopy(b2)
rc_e2e, _ = S.apply_ops(p2, {"tracks": "hats", "grid": {"step": 1.0, "phase": 0.5, "tol": 0.05}},
                        [{"op": "scale", "vel": 0.5}, {"op": "shift", "start": 0.02}])
rep = S.scope_report(b2, p2, [rc_e2e])
check("E2E: scalpel's own receipt satisfies the LAW", rep["clean"], "; ".join(rep.get("out_of_scope", [])))
p2["tracks"][0]["notes"][0]["vel"] = 0.2                        # sneak an unreceipted edit in
rep2 = S.scope_report(b2, p2, [rc_e2e])
check("E2E: sneaky kick edit CAUGHT", not rep2["clean"] and any("Kick" in o for o in rep2["out_of_scope"]))
check("E2E: report counts notes", rep2["note_changes"] >= 17)

rep3 = S.scope_report(b2, copy.deepcopy(b2), [])
check("identical songs -> empty clean report", rep3["clean"] and rep3.get("empty"))

# ------------------------------------- THE PROPOSAL-LIFETIME LAW (2026-07-11)
# receipts live as long as the proposal: per-song clears only, so a fresh ask
# on song B never orphans song A's pending-proposal ledger (the rhodes_aurora/
# sunrise/vocals_peak false-flag class — a revise wiped its own prop's history).
import tempfile
with tempfile.TemporaryDirectory() as _ipc:
    os.environ["SOTADAW_IPC"] = _ipc
    S.coarse_receipt("_prop_a", "set_track_fx", fields=["track:pads:fx"])
    S.coarse_receipt("_prop_b", "update_track", fields=["track:lead:gainDb"])
    S.clear_receipts("_prop_a")
    check("per-song clear drops only that song",
          not S.read_receipts("_prop_a") and len(S.read_receipts("_prop_b")) == 1)
    S.coarse_receipt("_prop_a", "automate", fields=["track:pads:fx.0.cutoff"])
    check("ledger reusable after a per-song clear",
          len(S.read_receipts("_prop_a")) == 1)
    S.clear_receipts()
    check("legacy full wipe still works",
          not S.read_receipts("_prop_a") and not S.read_receipts("_prop_b"))
    # the revise class end-to-end at the kernel seam: receipts filed in run 1
    # must still satisfy the LAW when the scope check re-runs in run 2
    S.coarse_receipt("_prop_r", "set_track_fx", fields=["track:rhodes_aurora:fx"])
    b4 = fixture(); p4 = copy.deepcopy(b4)
    b4["tracks"][0]["name"] = "rhodes_aurora"; p4["tracks"][0]["name"] = "rhodes_aurora"
    p4["tracks"][0]["fx"] = [{"id": "fx_filter", "params": {"cutoff": 2000}}]
    rep4 = S.scope_report(b4, p4, S.read_receipts("_prop_r"))
    check("revise class: run-1 receipt satisfies run-2 scope check",
          rep4["clean"], "; ".join(rep4.get("out_of_scope", [])))
    del os.environ["SOTADAW_IPC"]

# ------------------------------- THE SPELLING LAW (W115 generalized, 2026-07-11)
# a receipt's field spelling must never decide a verdict: bare meta keys
# ("masterGainDb" from auto_master) and bare track fields ("track:pads")
# cover the same ground as their namespaced twins. Notes stay exact/wild.
b5 = fixture(); p5 = copy.deepcopy(b5)
p5["masterGainDb"] = -3.0
rc_bare = {"tool": "auto_master", "fields": ["masterGainDb"], "track_wild": []}
rep5 = S.scope_report(b5, p5, [rc_bare])
check("bare meta spelling covers (masterGainDb)", rep5["clean"],
      "; ".join(rep5.get("out_of_scope", [])))
b6 = fixture(); p6 = copy.deepcopy(b6)
p6["tracks"][2]["gainDb"] = -6.0
p6["tracks"][2]["fx"] = [{"id": "fx_filter", "params": {"cutoff": 900}}]
rc_track = {"tool": "shape_track", "fields": ["track:hats"], "track_wild": []}
rep6 = S.scope_report(b6, p6, [rc_track])
check("bare track spelling covers props+fx", rep6["clean"],
      "; ".join(rep6.get("out_of_scope", [])))
p6["tracks"][2]["notes"][0]["vel"] = 0.99
rep7 = S.scope_report(b6, p6, [rc_track])
check("bare track spelling does NOT cover notes (scalpel core)",
      not rep7["clean"] and any("note" in o for o in rep7["out_of_scope"]))
# poisoned ledger line (track_wild=True bool, pre-2026-07-11) never kills the check
rep8 = S.scope_report(b6, p6, [{"tool": "old", "fields": ["*"], "track_wild": True}])
check("bool track_wild coerced, full-write receipt still honored",
      rep8["clean"] and rep8["full_write"])

# ---------------------------------------------------------------- strum / arp (#23c roll twins)
bs = fixture(); sel_pad = {"tracks": ["Dream Pad"]}
S.apply_ops(bs, sel_pad, [{"op": "strum", "spread_ms": 15}])
pad = next(t for t in bs["tracks"] if t["name"] == "Dream Pad")
n65 = next(n for n in pad["notes"] if n["pitch"] == 65)
n68 = next(n for n in pad["notes"] if n["pitch"] == 68)
n70 = next(n for n in pad["notes"] if n["pitch"] == 70)
check("strum up: low string holds", approx(n65["start"], 32.0))
check("strum up: 2nd string +15ms = 0.03b @120", approx(n68["start"], 32.03))
check("strum: release holds (note end constant)", approx(n68["start"] + n68["len"], 40.0))
check("strum: a single note is a finger, untouched",
      approx(n70["start"], 40.0) and approx(n70["len"], 8.0))
bs2 = fixture()
S.apply_ops(bs2, sel_pad, [{"op": "strum", "spread_ms": 15, "direction": "down"}])
pad2 = next(t for t in bs2["tracks"] if t["name"] == "Dream Pad")
check("strum down: high string holds, low string moves",
      approx(next(n for n in pad2["notes"] if n["pitch"] == 68)["start"], 32.0)
      and approx(next(n for n in pad2["notes"] if n["pitch"] == 65)["start"], 32.03))
ba = fixture()
S.apply_ops(ba, sel_pad, [{"op": "arp", "pattern": "up", "grid": 2.0}])
pad3 = next(t for t in ba["tracks"] if t["name"] == "Dream Pad")
arpn = sorted((n for n in pad3["notes"] if n["start"] < 40.0 - 1e-6),
              key=lambda n: n["start"])
check("arp up: 8b span at grid 2 -> 4 notes", len(arpn) == 4, str(len(arpn)))
check("arp up: pitches cycle 65,68,65,68",
      [n["pitch"] for n in arpn] == [65, 68, 65, 68],
      str([n["pitch"] for n in arpn]))
check("arp: starts land on the grid",
      all(approx(n["start"], 32.0 + i * 2.0) for i, n in enumerate(arpn)))
check("arp: the single at 40 survives",
      any(approx(n["start"], 40.0) and n["pitch"] == 70 for n in pad3["notes"]))
bu = fixture()
bu["tracks"][3]["notes"].append({"start": 32.0, "len": 8.0, "pitch": 72, "vel": 0.5})
S.apply_ops(bu, sel_pad, [{"op": "arp", "pattern": "updown", "grid": 1.0}])
pad4 = next(t for t in bu["tracks"] if t["name"] == "Dream Pad")
sq = [n["pitch"] for n in sorted((n for n in pad4["notes"] if n["start"] < 40 - 1e-6),
                                 key=lambda n: n["start"])]
check("arp updown: palindrome cycle 65,68,72,68", sq[:4] == [65, 68, 72, 68], str(sq[:4]))

# ---------------------------------------------------------------- verdict
print(f"\n{N['pass']} passed, {N['fail']} failed")
sys.exit(1 if N["fail"] else 0)
