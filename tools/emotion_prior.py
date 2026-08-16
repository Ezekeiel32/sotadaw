#!/usr/bin/env python3
"""THE EMOTION PRIOR — feeling words become additive parameter targets
(wave 47; R-20 item 086).

r-20: the emotion->parameter map is ADDITIVE and linear (77-89% of
variance — no interactions needed). Two axes: AROUSAL rides tempo/
loudness/density/register/brightness; VALENCE rides mode/-roughness/
-strain. Eerola sr^2 lever weights: mode 0.29, tempo 0.14, register
0.08, dynamics 0.04. Target emotions -> parameter targets (Happy =
major/fast>110/high/staccato; Sad = minor/slow<90/low/legato/dark;
Tense = minor/loud/low/dissonant; Peaceful = major/slow/soft/mellow).

  EMOTIONS                    the table (deltas, never absolutes —
                              additive onto the genre's own defaults)
  detect(text)                emotion words in an ask
  emotion_prior(text)         the summed additive prior + the plan line
"""
import re

# additive deltas (the genre's defaults stay the base — item 086's law)
EMOTIONS = {
    "happy":    {"mode": "major", "tempo": +12, "register": +3,
                 "density": +0.1, "brightness": +0.15,
                 "articulation": "staccato"},
    "euphoric": {"mode": "major", "tempo": +16, "register": +4,
                 "density": +0.2, "brightness": +0.2,
                 "articulation": "driving"},
    "sad":      {"mode": "minor", "tempo": -18, "register": -3,
                 "density": -0.15, "brightness": -0.2,
                 "articulation": "legato"},
    "melancholic": {"mode": "minor", "tempo": -12, "register": -2,
                    "density": -0.1, "brightness": -0.15,
                    "articulation": "legato"},
    "tense":    {"mode": "minor", "tempo": +6, "register": -2,
                 "density": +0.15, "brightness": +0.05,
                 "articulation": "clipped", "dissonance": +0.2},
    "scary":    {"mode": "minor", "tempo": +4, "register": -4,
                 "density": +0.1, "brightness": -0.1,
                 "articulation": "clipped", "dissonance": +0.3},
    "menacing": {"mode": "minor", "tempo": -4, "register": -4,
                 "density": +0.05, "brightness": -0.15,
                 "articulation": "heavy", "dissonance": +0.2},
    "peaceful": {"mode": "major", "tempo": -14, "register": +1,
                 "density": -0.2, "brightness": -0.05,
                 "articulation": "legato"},
    "dreamy":   {"mode": "major", "tempo": -8, "register": +2,
                 "density": -0.15, "brightness": -0.05,
                 "articulation": "washed"},
    "angry":    {"mode": "minor", "tempo": +10, "register": -1,
                 "density": +0.2, "brightness": +0.1,
                 "articulation": "driving", "dissonance": +0.15},
}
_SYNONYMS = {
    "joyful": "happy", "uplifting": "happy", "ecstatic": "euphoric",
    "sorrowful": "sad", "mournful": "sad", "wistful": "melancholic",
    "nostalgic": "melancholic", "anxious": "tense", "ominous": "menacing",
    "sinister": "menacing", "calm": "peaceful", "serene": "peaceful",
    "ethereal": "dreamy", "furious": "angry", "aggressive": "angry",
    "haunting": "scary", "eerie": "scary",
}
# W87 (r-20 item 219) THE VALENCE LAW: mode->valence is a LEARNED
# prior (cross-cultural evidence; a minor-key EDM/metal take is not
# 'sad') — these mode biases are DEFAULTS a genre/culture node may
# override, never a court floor. Sethares ROUGHNESS is the universal
# tension floor (tension.py's court keeps it culture-independent).
# Eerola sr^2 lever weights (documentation of WHY mode leads the sum)
LEVER_WEIGHTS = {"mode": 0.29, "tempo": 0.14, "register": 0.08,
                 "dynamics": 0.04}


def detect(text):
    t = str(text or "").lower()
    found = []
    for w in list(EMOTIONS) + list(_SYNONYMS):
        if re.search(rf"\b{w}\b", t):
            found.append(_SYNONYMS.get(w, w))
    return sorted(set(found))


def emotion_prior(text):
    """Summed additive prior over detected emotions + the plan line.
    Returns {} when no emotion words ride the ask."""
    hits = detect(text)
    if not hits:
        return {}
    acc = {"tempo": 0, "register": 0, "density": 0.0, "brightness": 0.0,
           "dissonance": 0.0}
    modes, arts = [], []
    for h in hits:
        e = EMOTIONS[h]
        for k in acc:
            acc[k] = round(acc[k] + e.get(k, 0), 2)
        modes.append(e["mode"])
        arts.append(e["articulation"])
    mode = max(set(modes), key=modes.count)
    line = (f"  emotion ({'+'.join(hits)}): bias {mode}, tempo "
            f"{acc['tempo']:+d}bpm, register {acc['register']:+d}st, "
            f"density {acc['density']:+.2f}, brightness "
            f"{acc['brightness']:+.2f}"
            + (f", dissonance {acc['dissonance']:+.2f}"
               if acc["dissonance"] else "")
            + f"; feel: {arts[0]} (ADDITIVE onto the genre's defaults)")
    return {"emotions": hits, "mode_bias": mode, **acc,
            "articulation": arts[0], "plan_line": line}


if __name__ == "__main__":
    import json
    import sys as _s
    print(json.dumps(emotion_prior(" ".join(_s.argv[1:])), indent=1))
