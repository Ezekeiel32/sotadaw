#!/usr/bin/env python3
"""#1 face leg — the agent layer speaks meterMap (grid wiring proof).
Pure python, zero engine. Proof surface:
  A) meter.py <-> C++ mirror math (identity + 7/8 + inverse) via --selftest reuse
  B) surgical: section_spans / bars selector / TempoClock / whats_at / barOffset
     all route bars through the resolver on a 3/4 song (and stay 4/4 mapless)
  C) daw_mcp: get_song_region windows bars meter-aware on a scratch song
  D) midi_bridge exposes THE resolver (one implementation, aliased)
Run: python3 tools/grid_battery.py"""
import json, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "agent"))
os.environ["SOTADAW_IPC"] = tempfile.mkdtemp(prefix="gridipc_")  # isolate receipts/fence

import meter
import surgical
import midi_bridge

N = {"pass": 0, "fail": 0}
def check(name, cond, detail=""):
    N["pass" if cond else "fail"] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""),
          flush=True)

def waltz(**kw):
    """4 bars of 3/4 (12 quarter-beats), a note on every beat."""
    s = {"version": 2, "bpm": 120, "lengthBars": 4,
         "meterMap": [{"bar": 0, "num": 3, "den": 4}],
         "sections": [{"name": "verse", "startBar": 0}, {"name": "chorus", "startBar": 2}],
         "tracks": [{"name": "kick", "source": {"kind": "sample", "kit": "gm_drums"},
                     "gainDb": -6,
                     "notes": [{"start": float(b), "len": 0.4, "pitch": 36, "vel": 0.9}
                               for b in range(12)]}]}
    s.update(kw)
    return s

def main():
    # A) resolver selftest (the mirror math itself)
    check("A: meter.py selftest green", meter._selftest() == 0)

    # B) surgical on the waltz
    song = waltz()
    spans = surgical.section_spans(song)
    check("B: section_spans 3/4 (verse 0-6, chorus 6-12)",
          spans == [("verse", 0.0, 6.0), ("chorus", 6.0, 12.0)], str(spans))
    a, b, why = surgical.resolve_range(song, {"bars": [1, 2]})
    check("B: bars [1,2) selector = beats [3,6)", (a, b) == (3.0, 6.0), f"{a},{b} {why}")
    r = surgical.resolve(song, {"bars": [1, 2]})
    check("B: 3 notes inside bar 1 of 3/4", len(r.refs) == 3,
          str([n["start"] for _, n in r.refs]))
    # tempoMap point at bar 2 lands at beat 6 (mapless law would say 8):
    tsong = waltz(tempoMap=[{"bar": 2, "bpm": 60, "curve": 1}])
    clock = surgical.TempoClock(tsong)
    sec8 = clock.seconds_at(8.0)
    check("B: tempo switch at bar 2 = beat 6 (secs(8) = 3.0 + 2*1.0 = 5.0)",
          abs(sec8 - 5.0) < 1e-6, f"{sec8}")
    w = surgical.whats_at(song, 7.0)
    check("B: whats_at bar label meter-aware (7q = bar 2.333)",
          abs(w["bar"] - round(7.0 / 3.0, 3)) < 1e-3, str(w["bar"]))
    check("B: whats_at section bars in 3/4",
          w["section"] and w["section"]["bars"] == [2.0, 4.0], str(w.get("section")))
    bo = surgical.resolve_time_point(song, {"section": "verse", "barOffset": 1}, clock=None)
    check("B: section+barOffset crosses in bars (verse+1 = beat 3)", bo == 3.0, str(bo))
    # mapless identity: same asks on a no-map song = yesterday's numbers
    plain = waltz(); plain.pop("meterMap")
    a2, b2, _ = surgical.resolve_range(plain, {"bars": [1, 2]})
    check("B: mapless identity (bars [1,2) = beats [4,8))", (a2, b2) == (4.0, 8.0))

    # C) daw_mcp wiring: scratch song through the real tool
    import daw_mcp
    sp = os.path.join(ROOT, "songs", "_grid_probe.json")
    try:
        json.dump(waltz(), open(sp, "w"))
        out = json.loads(daw_mcp.t_get_song_region(
            {"song": "_grid_probe", "from_bar": 2, "to_bar": 2}))
        starts = [n["start"] for n in out["tracks"][0]["notes"]]
        check("C: get_song_region bar 2 of 3/4 = beats [3,6)",
              starts == [3.0, 4.0, 5.0], str(starts))
        json.dump(plain, open(sp, "w"))
        out = json.loads(daw_mcp.t_get_song_region(
            {"song": "_grid_probe", "from_bar": 2, "to_bar": 2}))
        starts = [n["start"] for n in out["tracks"][0]["notes"]]
        check("C: mapless get_song_region unchanged (beats [4,8))",
              starts == [4.0, 5.0, 6.0, 7.0], str(starts))
    finally:
        if os.path.exists(sp):
            os.remove(sp)
        shutil.rmtree(os.environ["SOTADAW_IPC"], ignore_errors=True)

    # D) one implementation: the bridge aliases THE resolver
    check("D: midi_bridge._bar_start_q IS meter.bar_start_q",
          midi_bridge._bar_start_q is meter.bar_start_q)

    print(f"\n{N['pass']} passed, {N['fail']} failed")
    sys.exit(1 if N["fail"] else 0)

if __name__ == "__main__":
    main()
