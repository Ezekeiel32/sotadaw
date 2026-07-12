#!/usr/bin/env python3
"""EARS-ON-WRITE battery — write_song returns its own critique; the agent can no
longer be oblivious. Dispatches through daw_mcp.TOOLS (the server's own table —
the exact seam every live session uses), three planted-defect songs + a clean
control (cry-wolf check) + a sketch (noise-budget check). Deterministic.

Usage: python3 tools/ears_on_write_battery.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "agent"))
# tools/ deliberately NOT inserted here: the server process doesn't have it either,
# and pre-inserting it once masked a fail-open import bug (the proto E2E caught it)
import daw_mcp

PASS, FAIL = 0, []
def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)

N = lambda s, l, p, v: {"start": s, "len": l, "pitch": p, "vel": v}

def write(name, song):
    return daw_mcp.TOOLS["write_song"][0]({"name": name, "song": song})

def scrub(*names):
    for n in names:
        p = os.path.join(ROOT, "songs", f"{n}.json")
        if os.path.exists(p):
            os.remove(p)

def main():
    # A) DIRTY: panned+widened sub, empty master, fx_trim 'gain' trap, robot hats
    dirty = {"version": 2, "bpm": 128, "lengthBars": 4, "masterGainDb": 0.0, "master": [],
             "tracks": [
                 {"name": "sub", "source": {"kind": "faust", "id": "sub_clean"},
                  "gainDb": -5, "pan": 0.4,
                  "fx": [{"id": "fx_widen", "params": {"width": 0.8}},
                         {"id": "fx_trim", "params": {"gain": -3.0}}],
                  "notes": [N(i * 2.0, 1.5, 33, 0.8) for i in range(8)]},
                 {"name": "hats", "source": {"kind": "faust", "id": "hat"}, "gainDb": -12,
                  "notes": [N(i * 0.5, 0.1, 42, 0.7) for i in range(32)]},
                 {"name": "lead", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -9,
                  "notes": [N(i * 1.0, 0.7, 64 + (i * 3) % 14, 0.8) for i in range(16)]}]}
    r = write("_ears_a", dirty)
    ok(r.startswith("OK:"), "A: the critic never blocks the write")
    ok("DOCTOR:" in r, "A: verdict present")
    ok("[M1]" in r, f"A: panned/widened sub called out ({r.splitlines()[-1][:90]})")
    ok("[X1]" in r or "no master limiter" in r, "A: missing release wall called out")
    ok("hard" in r and "open" in r, "A: tiered counts present")

    # A2) the zone trap alone (fx_trim 'gain' does NOTHING) must be a hard item
    trap = {"version": 2, "bpm": 120, "lengthBars": 8, "masterGainDb": 0.0,
            "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
            "tracks": [
                {"name": "kick", "source": {"kind": "faust", "id": "kick_punch"}, "gainDb": -3,
                 "notes": [N(float(i), 0.2, 36, 0.95) for i in range(8)]},
                {"name": "bass", "source": {"kind": "faust", "id": "bass_warm"}, "gainDb": -6,
                 "fx": [{"id": "fx_trim", "params": {"gain": 2.0}}],
                 "notes": [N(i * 0.5, 0.4, 35 + (i % 2) * 3, 0.5 + 0.04 * (i % 5)) for i in range(16)]},
                {"name": "keys", "source": {"kind": "faust", "id": "rhodes"}, "gainDb": -10,
                 "notes": [N(i * 2.0 + 0.02 * (i % 3), 1.8, 55 + [0, 3, 7, 10][i % 4], 0.5 + 0.05 * (i % 6)) for i in range(16)]}]}
    r = write("_ears_b", trap)
    ok("[X2]" in r and "level" in r, f"B: fx_trim 'gain' zone-trap caught as hard ({r.splitlines()[-1][:90]})")

    # A3) deprecated limiter type = hard
    lim = dict(trap)
    lim["master"] = [{"type": "limiter", "params": {"ceiling": -1.0}}]
    r = write("_ears_c", lim)
    ok("[X2]" in r and "truepeak" in r, "C: deprecated limiter type steered to fx_truepeak")

    # D) CLEAN control (cry-wolf): produced song -> no hard items, short verdict
    import random
    rng = random.Random(7)
    mk = lambda base, i: N(round(i * 0.5 + rng.uniform(-0.03, 0.03), 3), 0.4,
                           base + [0, 3, 7, 10, 12][i % 5], round(0.55 + rng.uniform(0, 0.35), 2))
    clean = {"version": 2, "bpm": 124, "lengthBars": 8, "masterGainDb": 0.0,
             "master": [{"id": "fx_trim", "params": {"level": 1.0}},
                        {"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
             "sections": [{"name": "intro", "startBar": 0}, {"name": "drop", "startBar": 4}],
             "tracks": [
                 {"name": "kick", "source": {"kind": "faust", "id": "kick_punch"}, "gainDb": -3,
                  "notes": [N(float(i), 0.2, 36, round(0.9 + rng.uniform(-0.05, 0.05), 2)) for i in range(16, 32)]},
                 {"name": "bass", "source": {"kind": "faust", "id": "bass_warm"}, "gainDb": -6, "pan": 0,
                  "notes": [mk(33, i) for i in range(32, 64)]},
                 {"name": "lead", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -9,
                  "notes": [mk(64, i) for i in range(24, 64)]},
                 {"name": "pad", "source": {"kind": "faust", "id": "warm_pad" if False else "reese"}, "gainDb": -14,
                  "notes": [N(b * 4.0, 3.8, 52 + pc, 0.4 + 0.02 * (b % 3))
                            for b in range(8) for pc in ([0, 4, 7] if b % 2 else [5, 9, 12])]}]}
    r = write("_ears_d", clean)
    ok("0 hard" in r or "DOCTOR: clean." in r, f"D: clean control raises NO hard items ({r.splitlines()[-1][:110]})")
    ok(len(r.splitlines()[-1]) < 170, f"D: clean verdict stays slim ({len(r.splitlines()[-1])} ch)")

    # E) SKETCH noise budget: 1 track, 6 notes -> C3 demoted, verdict tiny
    sketch = {"version": 2, "bpm": 120, "lengthBars": 2, "masterGainDb": 0.0,
              "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
              "tracks": [{"name": "idea", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -8,
                          "notes": [N(i * 0.75 + 0.01 * i, 0.5, 60 + (i * 5) % 12, 0.5 + 0.06 * i) for i in range(6)]}]}
    r = write("_ears_e", sketch)
    last = r.splitlines()[-1]
    ok("[C3]" not in r, "E: 'no low end' demoted while sketching (1 track)")
    ok(len(last) <= 240, f"E: sketch verdict inside the noise budget ({len(last)} ch)")

    # ---- EARS ON TWEAK: the traps enter via mix moves; verdicts ride the tweak
    # tools too, and SILENCE is the law when a tweak is clean ----
    write("_ears_t", trap)   # trap fixture: kick/bass/keys, truepeak master
    r = daw_mcp.TOOLS["update_track"][0]({"song": "_ears_t", "track": "bass", "pan": 0.5})
    ok("DOCTOR:" in r and "[M1]" in r and "mono" in r,
       f"T1: panning the SUB via update_track fires M1 ({r.splitlines()[-1][:80]})")
    r = daw_mcp.TOOLS["update_track"][0]({"song": "_ears_t", "track": "kick", "gainDb": -2.5})
    ok("DOCTOR:" not in r, "T2: a clean gain nudge stays SILENT (no critique spam)")
    r = daw_mcp.TOOLS["update_track"][0]({"song": "_ears_t", "track": "bass", "pan": 0.0,
                                          "gainDb": -5.5})
    ok("DOCTOR:" in r and "[X2]" in r,
       "T2b: a STANDING trap keeps nagging on every touch until fixed (bass carries fx_trim 'gain')")
    r = daw_mcp.TOOLS["set_track_fx"][0]({"song": "_ears_t", "track": "keys",
                                          "fx": [{"id": "fx_trim", "params": {"gain": 2.0}}]})
    ok("DOCTOR:" in r and "[X2]" in r and "level" in r,
       "T3: set_track_fx catches the fx_trim 'gain' zone-trap")
    r = daw_mcp.TOOLS["set_track_fx"][0]({"song": "_ears_t", "track": "keys",
                                          "fx": [{"id": "fx_delay", "params": {"mix": 0.2}}]})
    ok("DOCTOR:" not in r, "T4: a clean fx chain stays SILENT")
    r = daw_mcp.TOOLS["set_track_fx"][0]({"song": "_ears_t", "track": "bass",
                                          "fx": [{"id": "fx_widen", "params": {"width": 0.6}}]})
    ok("DOCTOR:" in r and "WIDENED" in r, "T5: widening the sub fires M1 on the fx tool")
    # (type:'limiter' on a bus is IMPOSSIBLE input — set_buses' validator rejects it
    # upstream, which is better than a verdict. The reachable bus trap is fx_trim.)
    r = daw_mcp.TOOLS["set_buses"][0]({"song": "_ears_t",
                                       "buses": [{"id": "verb", "gainDb": 0,
                                                  "fx": [{"id": "fx_trim", "params": {"gain": 2.0}}]}]})
    ok("DOCTOR:" in r and "[X2]" in r and "level" in r, "T6: fx_trim 'gain' trap on a BUS fires X2")
    scrub("_ears_t")

    # X3: parked dark master filter (the 'barely audible' class); sweeps exempt
    parked = json.loads(json.dumps(dirty))
    parked["master"] = [{"id": "fx_filter", "params": {"cutoff": 500.0, "res": 0.2}},
                        {"id": "fx_truepeak", "params": {"ceiling": -1.2}}]
    r = write("_ears_f", parked)
    ok("[X3]" in r and "parked dark" in r, "T7: parked 500Hz master filter fires X3")
    swept = json.loads(json.dumps(parked))
    swept["automation"] = [{"target": "master[0].cutoff",
                            "points": [{"beat": 0, "v": 500}, {"beat": 16, "v": 8000}]}]
    r = write("_ears_f", swept)
    ok("[X3]" not in r, "T7b: the SAME filter with an automated sweep is exempt")
    open_f = json.loads(json.dumps(parked))
    open_f["master"][0]["params"]["cutoff"] = 9000.0
    r = write("_ears_f", open_f)
    ok("[X3]" not in r, "T7c: an open master filter is no violation")

    # X2 GENERALIZED (zone-truth table, 2026-07-12): setZone matches names
    # EXACTLY — any unknown param is a silent no-op; the doctor knows every
    # zone in instruments/fx_*.dsp now, not just fx_trim's 'gain'
    write("_ears_x", trap)
    r = daw_mcp.TOOLS["set_track_fx"][0]({"song": "_ears_x", "track": "keys",
                                          "fx": [{"id": "fx_delay",
                                                  "params": {"wet": 0.3, "time": 0.4}}]})
    ok("DOCTOR:" in r and "[X2]" in r and "wet" in r,
       f"T8: unknown param 'wet' on fx_delay fires generalized X2 ({r.splitlines()[-1][:80]})")
    r = daw_mcp.TOOLS["set_track_fx"][0]({"song": "_ears_x", "track": "keys",
                                          "fx": [{"id": "fx_ms_eq",
                                                  "params": {"side_low": -2.0, "width": 1.2}}]})
    ok("DOCTOR:" not in r, "T8b: valid zone names on fx_ms_eq stay SILENT")

    # X4: positive masterGainDb AFTER the wall re-opens what the wall closed
    x4 = json.loads(json.dumps(trap))
    x4["masterGainDb"] = 2.5
    r = write("_ears_x", x4)
    ok("[X4]" in r and "wall" in r,
       f"T9: masterGainDb +2.5 after the wall fires X4 ({r.splitlines()[-1][:80]})")
    x4["masterGainDb"] = 0.0
    r = write("_ears_x", x4)
    ok("[X4]" not in r, "T9b: masterGainDb 0 with a wall is lawful")
    scrub("_ears_x")

    # determinism
    ok(write("_ears_a", dirty) == write("_ears_a", dirty), "verdicts deterministic")

    scrub("_ears_a", "_ears_b", "_ears_c", "_ears_d", "_ears_e", "_ears_f")
    daw_mcp.surgical.read_receipts   # (import sanity — receipts module alive)


def make_track_ears_seam():
    """W7 — EARS ON MAKE through the same seam, zero renders: monkeypatch the
    subprocess rail with a PLANTED muddy analysis and assert the band verdict
    lands in make_track's reply (fail-open silently eating it = the bug class
    this battery exists for)."""
    planted = {"clipped_samples": 0, "lufs_integrated": -12.0,
               "band_energy_pct": {"low_20_120": 55.0, "lowmid_120_500": 33.0,
                                   "mid_500_2k": 1.5, "himid_2k_6k": 0.5,
                                   "high_6k_up": 0.2}}

    def fake_run(cmd, timeout=0):
        s = " ".join(str(c) for c in cmd)
        if "loop_gen" in s:
            return 0, "[loop] fake loop born", ""
        if "arrange" in s:
            return 0, "[arrange] fake: 8 bars", ""
        if "analyze2" in s:
            return 0, json.dumps(planted), ""
        return 0, "renderToFile ok=1", ""       # the m1 render

    real_run = daw_mcp.run
    daw_mcp.run = fake_run
    try:
        r = daw_mcp.TOOLS["make_track"][0]({"genre": "trap", "song": "_ears_mt"})
    finally:
        daw_mcp.run = real_run
    ok("EARS: MUD" in r, "MT1: planted mud -> EARS verdict in make_track reply")
    ok("PRESENCE STARVED" in r, "MT2: starved presence named in the same reply")
    clean = json.loads(json.dumps(planted))
    clean["band_energy_pct"] = {"low_20_120": 62.0, "lowmid_120_500": 18.0,
                                "mid_500_2k": 12.0, "himid_2k_6k": 5.0,
                                "high_6k_up": 3.0}

    def fake_run2(cmd, timeout=0):
        s = " ".join(str(c) for c in cmd)
        if "analyze2" in s:
            return 0, json.dumps(clean), ""
        if "loop_gen" in s:
            return 0, "[loop] fake loop born", ""
        if "arrange" in s:
            return 0, "[arrange] fake: 8 bars", ""
        return 0, "renderToFile ok=1", ""

    daw_mcp.run = fake_run2
    try:
        r = daw_mcp.TOOLS["make_track"][0]({"genre": "trap", "song": "_ears_mt"})
    finally:
        daw_mcp.run = real_run
    ok("EARS:" not in r, "MT3: clean bands -> SILENT (no cry-wolf)")
    scrub("_ears_mt")


if __name__ == "__main__":
    main()
    make_track_ears_seam()
    for f in FAIL:
        print("FAIL:", f)
    print(f"ears-on-write battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
