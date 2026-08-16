#!/usr/bin/env python3
"""SOUND COURT BATTERY — proves the per-stem timbre law (wave 20;
R-16 018/019, R-7 055). Synthetic stems, deterministic, no renders."""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sound_court as SC  # noqa: E402

SR = 44100
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def env_tone(f, secs, attack_ms, decay_s=0.5, amp=0.5, noise=0.0,
             hits=4, sr=SR):
    """Repeated enveloped hits: tone + optional noise, given attack."""
    n = int(secs * sr)
    y = np.zeros(n)
    rng = np.random.default_rng(7)
    period = n // hits
    for h in range(hits):
        i0 = h * period
        t = np.arange(min(period, n - i0)) / sr
        a = np.minimum(t / max(attack_ms / 1000.0, 1e-4), 1.0)
        d = np.exp(-np.maximum(t - attack_ms / 1000.0, 0) / decay_s)
        sig = np.sin(2 * np.pi * f * t)
        if noise > 0:
            sig = (1 - noise) * sig + noise * rng.standard_normal(len(t))
        y[i0:i0 + len(t)] += amp * a * d * sig
    return y


# ------------------------------------------------------------ measure()
sub = env_tone(50, 4.0, attack_ms=8, decay_s=0.8)
m = SC.measure_stem(sub, SR)
check("measure: 50Hz sub centroid low + tonal + mono + massy",
      m and m["centroid_hz"] < 900 and m["flatness"] < 0.3 and
      m["width_pct"] < 5 and m["low_pct"] > 60, str(m))
check("measure: attack ~8ms lands in class",
      m and m["attack_ms"] is not None and 2 <= m["attack_ms"] <= 40,
      str(m and m["attack_ms"]))
hat = env_tone(9000, 4.0, attack_ms=1, decay_s=0.05, noise=0.9, hits=16)
mh = SC.measure_stem(hat, SR)
check("measure: hat centroid high + noisy",
      mh and mh["centroid_hz"] > 3500 and mh["flatness"] > 0.1, str(mh))
pad = env_tone(440, 6.0, attack_ms=600, decay_s=3.0, hits=2)
mp = SC.measure_stem(pad, SR)
check("measure: pad attack reads slow (>100ms)",
      mp and mp["attack_ms"] and mp["attack_ms"] > 100, str(mp))
check("measure: silent stem = {}", SC.measure_stem(np.zeros(SR * 2), SR)
      == {})

# ---------------------------------------------------------- role table
check("role: names route (808->sub, strings->pad, clap->snare)",
      SC.role_of("808_sub") == "sub" and SC.role_of("warm_strings") == "pad"
      and SC.role_of("clap_layer") == "snare")

v = SC.court_stem(m, "sub", name="808")
check("court: lawful sub passes", v["ok"], str(v))
v = SC.court_stem(mh, "sub", name="808")
check("court: hat-shaped '808' CONVICTED (timbre off-role)",
      not v["ok"] and any(f["kind"] == "timbre_offrole"
                          for f in v["flags"]), str(v))
v = SC.court_stem(mp, "pluck", name="plucky")
check("court: 600ms 'pluck' CONVICTED (attack class)",
      not v["ok"] and any(f["kind"] == "attack_class" for f in v["flags"]),
      str(v))
fast_pad = SC.measure_stem(env_tone(440, 4.0, attack_ms=2, decay_s=2.5,
                                    hits=3), SR)
v = SC.court_stem(fast_pad, "pad", name="big_pad")
check("court: 2ms 'pad' CONVICTED (a pluck wearing a pad's name)",
      not v["ok"] and any(f["kind"] == "attack_class" for f in v["flags"]),
      str(v))
check("court: unknown role skipped",
      SC.court_stem(m, None).get("skipped", "").startswith("no law"))

# heal: attack zone moves into class (only when the param exists)
song = {"tracks": [{"name": "big_pad",
                    "source": {"id": "additive_harm",
                               "params": {"attack": 0.002}}}]}
edits = SC.heal_attack(song, v["flags"])
check("heal: pad attack zone -> class band (geometric center, seconds)",
      edits and 0.05 <= song["tracks"][0]["source"]["params"]["attack"]
      <= 5.0, str(edits))
song2 = {"tracks": [{"name": "big_pad",
                     "source": {"id": "pad_motion", "params": {}}}]}
check("heal: no attack zone = no blind param invention",
      SC.heal_attack(song2, v["flags"]) == [])

# ------------------------------------------------------- role levels 055
levels = {"kick": -14.0, "snare": -17.0, "bass_808": -15.0,
          "lead_vocals": -16.5, "pads": -22.0}
v = SC.court_role_levels(levels, "pop", mix_db=-12.0)
check("levels: vocal -4.5 under mix passes (the r-7 sweet spot)",
      v["ok"], str(v))
v = SC.court_role_levels({"lead_vocals": -26.0, "kick": -14.0},
                         "pop", mix_db=-12.0)
check("levels: buried vocal (14dB under) CONVICTED",
      not v["ok"] and v["flags"][0]["kind"] == "vocal_offset", str(v))
song = {"tracks": [{"name": "lead_vocals", "gainDb": 0.0}]}
edits = SC.heal_vocal_offset(song, v)
check("levels heal: bounded +3dB vocal lift",
      edits and song["tracks"][0]["gainDb"] == 3.0, str(edits))
v = SC.court_role_levels({"lead_vocals": -13.0, "kick": -14.0},
                         "trap", mix_db=-12.0)
check("levels: hip-hop drums~vocal window accepts a hot vocal",
      v["ok"], str(v))
v = SC.court_role_levels({"kick": -10.0, "bass": -20.0}, "house")
check("levels: kick/bass 10dB apart = anchor advisory",
      v["ok"] and any(a["kind"] == "kick_bass_anchor"
                      for a in v["advisories"]), str(v))
v = SC.court_role_levels({"kick": -16.0, "snare": -11.0, "bass": -15.0},
                         "techno")
check("levels: snare 5dB over kick in techno = ordering advisory",
      any(a["kind"] == "ordering" for a in v["advisories"]), str(v))
v = SC.court_role_levels({"kick": -11.0, "snare": -15.0, "bass": -14.0},
                         "rock")
check("levels: rock backbeat law advises snare OVER kick",
      any("backbeat" in a["why"] for a in v["advisories"]), str(v))

print()
if FAILS:
    print(f"sound_court_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("sound_court_battery: ALL GREEN")
