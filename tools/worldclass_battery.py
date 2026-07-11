#!/usr/bin/env python3
"""WORLD-CLASS FLOOR battery — pure proof of tools/worldclass.py.
Every hard class convicts, every heal heals, every exemption holds."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldclass as wc  # noqa: E402

N = 0
FAILS = []


def check(name, ok, detail=""):
    global N
    N += 1
    print(f"[wc-battery] {N:2}. {name:56} {'OK' if ok else 'FAIL ' + str(detail)}")
    if not ok:
        FAILS.append(name)


def base_song(**kw):
    s = {"bpm": 120, "masterGainDb": 0.0,
         "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
         "tracks": [{"name": "keys", "source": {"kind": "faust"},
                     "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 0.8}],
                     "fx": []}]}
    s.update(kw)
    return s


LOUD = {"lufs_integrated": -10.5, "peak_dbfs": -1.4, "clipped_samples": 0}


def main():
    v = wc.floor_verdict(base_song(), LOUD)
    check("clean loud take passes", v["pass"] and not v["hard"], v)

    v = wc.floor_verdict(base_song(),
                         {"lufs_integrated": -44.0, "peak_dbfs": -31.0,
                          "clipped_samples": 0})
    check("silent take convicts", any(h["code"] == "silent_take"
                                      for h in v["hard"]), v)

    v = wc.floor_verdict(base_song(), {"lufs_integrated": -9.0,
                                       "peak_dbfs": 0.0, "clipped_samples": 812})
    check("post-wall clipping convicts", any(h["code"] == "still_clipping"
                                             for h in v["hard"]), v)

    v = wc.floor_verdict(base_song(), {"lufs_integrated": -2.9,
                                       "peak_dbfs": -0.4, "clipped_samples": 0})
    check("crushed louder-than-release convicts",
          any(h["code"] == "crushed" for h in v["hard"]), v)

    s = base_song(master=[{"id": "fx_filter", "params": {"cutoff": 400}},
                          {"id": "fx_truepeak", "params": {"ceiling": -1.2}}])
    v = wc.floor_verdict(s, LOUD)
    check("parked dark master filter convicts (X3)",
          any(h["code"] == "dark_master" for h in v["hard"]), v)
    fixed, rec = wc.heal(s, v)
    v2 = wc.floor_verdict(fixed, LOUD)
    check("dark filter heals + wall still stands last",
          v2["pass"] and rec and fixed["master"][-1]["id"] == "fx_truepeak",
          (rec, fixed["master"]))

    s = base_song(master=[{"id": "fx_filter", "params": {"cutoff": 400}},
                          {"id": "fx_truepeak", "params": {"ceiling": -1.2}}],
                  automation=[{"target": "masterFx[0].cutoff",
                               "points": [{"beat": 0, "v": 0.1}]}])
    v = wc.floor_verdict(s, LOUD)
    check("automated filter sweep exempt (performance)",
          not any(h["code"] == "dark_master" for h in v["hard"]), v)

    s = base_song(masterGainDb=3.0)
    v = wc.floor_verdict(s, LOUD)
    fixed, rec = wc.heal(s, v)
    check("post-wall +gain convicts and heals to 0",
          any(h["code"] == "post_wall_gain" for h in v["hard"])
          and fixed["masterGainDb"] == 0.0, (v, fixed.get("masterGainDb")))

    s = base_song(master=[{"type": "limiter", "params": {}}])
    v = wc.floor_verdict(s, LOUD)
    fixed, rec = wc.heal(s, v)
    check("legacy limiter convicts and upgrades to fx_truepeak",
          any(h["code"] == "legacy_limiter" for h in v["hard"])
          and any(f.get("id") == "fx_truepeak" for f in fixed["master"]), fixed)

    s = base_song()
    s["tracks"][0]["fx"] = [{"id": "fx_trim", "params": {"gain": -3.0}}]
    v = wc.floor_verdict(s, LOUD)
    fixed, rec = wc.heal(s, v)
    check("fx_trim 'gain' no-op convicts and renames to level (X2)",
          any(h["code"] == "trim_noop" for h in v["hard"])
          and fixed["tracks"][0]["fx"][0]["params"] == {"level": -3.0}, fixed)

    s = base_song()
    s["tracks"].append({"name": "bass", "pan": -0.4,
                        "notes": [{"start": 0, "len": 1, "pitch": 36, "vel": 1}],
                        "fx": [{"id": "fx_widen", "params": {"width": 1.6}}]})
    v = wc.floor_verdict(s, LOUD)
    fixed, rec = wc.heal(s, v)
    b = fixed["tracks"][1]
    check("stereo sub convicts; heal centers + strips widener (M1)",
          sum(1 for h in v["hard"] if h["code"] == "sub_stereo") == 2
          and b["pan"] == 0.0 and not b["fx"], (v, b))

    v = wc.floor_verdict(base_song(), True)
    check("metrics-less analysis: structural checks only, no crash",
          isinstance(v, dict) and v["pass"], v)

    s = base_song()
    s0 = __import__("json").dumps(s, sort_keys=True)
    v = wc.floor_verdict(s, LOUD)
    wc.heal(s, v)
    check("kernel is pure: input song never mutated",
          __import__("json").dumps(s, sort_keys=True) == s0)

    want = 13
    ok = not FAILS and N == want
    print(f"[wc-battery] {N}/{want} checks, "
          + ("ALL PASS — the floor holds" if ok else f"RED: {FAILS}"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
