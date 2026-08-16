#!/usr/bin/env python3
"""SEMANTIC MAP BATTERY — proves THE SEMANTIC MAP (wave 19; R-28
039/040/103/104/168/169/250). Pure, deterministic, no models."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import semantic_map as SM  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def goal(c, term):
    return next((g for g in c["semantic_goals"] if g["term"] == term), None)


# ------------------------------------------- (term x context x scope) law
c = SM.contract("make the vocal warmer")
g = goal(c, "warm")
check("scope: 'vocal warmer' binds to the vocal", g and g["scope"] == "vocal",
      str(g))
check("context: default eq reading carries the low-mid recipe",
      g and "100-500" in g["recipe"], str(g and g["recipe"]))
c = SM.contract("warm reverb on the vocal")
g = goal(c, "warm")
check("context: 'warm reverb' routes to the SPACE recipe (not EQ)",
      g and g["effect_context"] == "reverb" and "decay" in g["recipe"],
      str(g))
c = SM.contract("warm tape character, a bit of drive")
g = goal(c, "warm")
check("context: 'warm' near gear words = 2nd-harmonic saturation",
      g and g["effect_context"] == "saturation" and
      "2nd-harmonic" in g["recipe"], str(g))
c = SM.contract("vintage feel on the drums")
g = goal(c, "vintage")
check("vintage: THD contract recipe, odd harmonics warned",
      g and "0.5-2%" in g["recipe"] and "odd" in g["recipe"].lower(), str(g))

# ------------------------------------------------------- direction logic
c = SM.contract("this is too bright, fix it")
g = goal(c, "bright")
check("negation: 'too bright' flips to darker", g and g["direction"] == -1,
      str(g))
c = SM.contract("it sounds muddy")
g = goal(c, "muddy")
check("unwanted flaw: naming 'muddy' asks for LESS mass",
      g and g["direction"] == -1 and "200-500" in g["recipe"], str(g))

# ------------------------------------------------------ agreement gate
c = SM.contract("make it boxy and bright")
check("agreement: 'boxy' is LOW -> ambiguity ask-back",
      any(a["term"] == "boxy" for a in c["ambiguities"]))
check("agreement: 'bright' is HIGH -> no ask-back",
      all(a["term"] != "bright" for a in c["ambiguities"]))

# ---------------------------------------------------------- references
c = SM.contract("a deep house groove like moodymann, but brighter")
check("reference: 'like moodymann' extracted with 5 channels",
      c["references"] and c["references"][0]["like"] == "moodymann" and
      "width" in c["references"][0]["extract"], str(c["references"]))

# ------------------------------------------------------------ verdicts
A_BRIGHT = {"spectral_centroid_hz": 4200.0, "stereo_width_db": -8.0,
            "crest_factor_db": 12.0, "lr_correlation": 0.8,
            "band_energy_pct": {"sub": 10, "low": 20, "lowmid": 25,
                                "mid": 25, "high": 20}}
A_DARK = {"spectral_centroid_hz": 900.0, "stereo_width_db": -30.0,
          "crest_factor_db": 6.0, "lr_correlation": 0.99,
          "band_energy_pct": {"sub": 40, "low": 35, "lowmid": 15,
                              "mid": 8, "high": 2}}
c = SM.contract("make it bright")
v = SM.verdict_semantics(c["semantic_goals"], A_BRIGHT)
check("verdict: bright ask + bright take = ok", v[0]["ok"], str(v))
v = SM.verdict_semantics(c["semantic_goals"], A_DARK)
check("verdict: bright ask + dark take = unmet, recipe rides",
      not v[0]["ok"] and "2-6k" in v[0]["note"], str(v))
c = SM.contract("dark and warm")
v = SM.verdict_semantics(c["semantic_goals"], A_DARK)
check("verdict: dark ask + dark take = ok", all(r["ok"] for r in v), str(v))

# punchy routes to CREST, hard-separated from loudness (item 104)
c = SM.contract("punchy drums")
g = goal(c, "punchy")
check("punchy: crest correlate + attack-ms recipe, never 'louder'",
      g and g["correlate"] == "crest_factor_db" and
      "20-30ms" in g["recipe"] and "loud" in g["recipe"], str(g))
v = SM.verdict_semantics(c["semantic_goals"],
                         {"crest_factor_db": 5.0})
check("punchy: crushed take (crest 5dB) = unmet", not v[0]["ok"], str(v))

# wide + the mono-compat guard (r-28 f11)
c = SM.contract("wide pads")
v = SM.verdict_semantics(c["semantic_goals"],
                         {"stereo_width_db": -3.0, "lr_correlation": -0.3})
check("wide: width built on phase (corr -0.3) FAILS the mono guard",
      not v[0]["ok"] and "cancel" in v[0]["note"], str(v))
v = SM.verdict_semantics(c["semantic_goals"],
                         {"stereo_width_db": -6.0, "lr_correlation": 0.5})
check("wide: honest width passes", v[0]["ok"], str(v))

# unmeasured correlates stay advisory (never convict blind)
c = SM.contract("drier vocal")
v = SM.verdict_semantics(c["semantic_goals"], {})
check("unmeasured: space axis rides as ok + recipe note",
      v and v[0]["ok"] and v[0]["got"] == "unmeasured", str(v))

# 'full' disambiguation (telemetry wolf: length vs tone)
for ask in ("full length!", "MAKE A FULL 10 MINUTE GOA TRACK",
            "the full song please", "full version"):
    check(f"full-guard: '{ask[:24]}' is LENGTH, not tone",
          not goal(SM.contract(ask), "full"))
check("full-guard: 'make the bass full and fat' IS tone",
      goal(SM.contract("make the bass full and fat"), "full") is not None)

# item 232 (wave 22): master-scope brightness prefers roll-off
c = SM.contract("make the mix brighter")
v = SM.verdict_semantics(c["semantic_goals"],
                         {"spectral_centroid_hz": 500.0,
                          "rolloff_85_hz": 900.0})
check("232: master 'brighter' verdicts on roll-off (900 > 270 anchor), "
      "centroid ignored", v[0]["ok"], str(v))
c = SM.contract("brighter synth lead")
v = SM.verdict_semantics(c["semantic_goals"],
                         {"spectral_centroid_hz": 4000.0,
                          "rolloff_85_hz": 100.0})
check("232: track-scope keeps centroid (stems lack the sub-mass trap)",
      v[0]["ok"], str(v))

# ------------------------------------------------------- Saitis 3 axes
ax = SM.saitis_axes(A_DARK)
check("saitis: luminance + mass measured, texture honestly None",
      ax["luminance_hz"] == 900.0 and ax["mass_low_pct"] == 75.0 and
      ax["texture_roughness"] is None, str(ax))

# ------------------------------------------- court_instruction seam ride
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music_court as MC  # noqa: E402
song = {"bpm": 124, "lengthBars": 8, "tracks": [
    {"name": "kick", "notes": [{"start": 0, "len": 0.4, "pitch": 36,
                                "vel": 0.9}]}]}
iv = MC.court_instruction("bright punchy techno at 124bpm", song, A_DARK,
                          "techno")
kinds = {c["kind"] for c in iv["contracts"]}
check("instruction court: semantic contracts ride beside hard targets",
      "semantic:bright" in kinds and "semantic:punchy" in kinds and
      "bpm" in kinds, str(sorted(kinds)))
check("instruction court: dark take fails the bright contract",
      any(c["kind"] == "semantic:bright" and not c["ok"]
          for c in iv["contracts"]))
iv2 = MC.court_instruction("make it boxy", song, None, "")
check("instruction court: ambiguities surface on the verdict",
      iv2.get("ambiguities") and iv2["ambiguities"][0]["term"] == "boxy",
      str(iv2.get("ambiguities")))
iv3 = MC.court_instruction("bright lift please", song, None, "")
check("instruction court: pre-render (no analysis) = unmeasured, ok",
      all(c["ok"] for c in iv3["contracts"]
          if c["kind"].startswith("semantic:")))

print()
if FAILS:
    print(f"semantic_map_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("semantic_map_battery: ALL GREEN")
