#!/usr/bin/env python3
"""STRUCTURE COURTS BATTERY — proves wave 51 (item 170: the four
missing structure courts). Pure."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import structure_court as SC  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def track(name, bars, riff=None, jitter=0.0, pitch=60):
    """bars = list of bar indices that sound; riff = 16th onsets."""
    riff = riff if riff is not None else [0, 4, 8, 12]
    notes = []
    for i, b in enumerate(bars):
        for k, o in enumerate(riff):
            j = jitter * (0.5 - ((i * 7 + k * 3) % 10) / 10.0)
            notes.append({"start": b * 4 + o / 4.0 + j, "len": 0.4,
                          "pitch": pitch + (k % 3), "vel": 96})
    return {"name": name, "notes": notes}


# ---------------------------------------------------- phrase grid
song = {"bpm": 120, "lengthBars": 23,
        "sections": [{"name": "intro", "startBar": 0},
                     {"name": "verse", "startBar": 8},
                     {"name": "chorus", "startBar": 15}],
        "tracks": [track("lead", range(23))]}
v = SC.court_phrase_grid(song)
check("phrase_grid: 7-bar verse + 8-bar tail chorus -> the 7 flags "
      "(4-bar phrase law, wolf-calibrated)",
      any(a["kind"] == "off_grid_section" and a["bars"] == 7
          for a in v["advisories"]), str(v["advisories"]))
song["sections"] = [{"name": "verse", "startBar": 0},
                    {"name": "chorus", "startBar": 20}]
song["lengthBars"] = 40
check("phrase_grid: 20-bar sections pass (%4 law — 2^n-only was the "
      "1791-flag mistake)",
      not SC.court_phrase_grid(song)["advisories"])
dj = {"lengthBars": 60, "sections": [{"name": "deck A (128)", "startBar": 0},
                                     {"name": "deck B (130)", "startBar": 21}],
      "tracks": []}
check("phrase_grid: DJ-set manifests are chapters, not form (skipped)",
      SC.court_phrase_grid(dj).get("skipped", "").startswith("DJ"))

# ---------------------------------------------------- repetition
rep = {"bpm": 120, "lengthBars": 16,
       "tracks": [track("lead", range(16))]}
check("repetition: a looping riff self-similar (no flag)",
      not SC.court_repetition(rep)["advisories"])
wander = {"bpm": 120, "lengthBars": 24, "tracks": [{
    "name": "lead", "notes": [
        {"start": b * 4 + (o + b) % 13 / 4.0, "len": 0.4,
         "pitch": 48 + (b * 5 + o) % 24, "vel": 96}
        for b in range(24) for o in range(2 + b % 3)]}]}
v = SC.court_repetition(wander)
check("repetition: the wanderer (no bar ever recurs) flags "
      "through_composed",
      any(a["kind"] == "through_composed" for a in v["advisories"]),
      str(v))
med = {"bpm": 120, "lengthBars": 32,
       "sections": [{"name": "intro", "startBar": 0},
                    {"name": "verse", "startBar": 4},
                    {"name": "bridge", "startBar": 12},
                    {"name": "drop", "startBar": 20},
                    {"name": "outro", "startBar": 28}],
       "tracks": [track("keys", range(32))]}
v = SC.court_repetition(med)
check("repetition: no section class ever returns = medley advisory",
      any(a["kind"] == "no_section_recurs" for a in v["advisories"]),
      str(v["advisories"]))

# witness law: a transcribed (jittered) lane is OUT of jurisdiction
jit = {"bpm": 120, "lengthBars": 24,
       "tracks": [track("vox_transcribed", range(24),
                        riff=[0, 3, 7, 10], jitter=0.3)]}
check("witness law: jittered transcription lanes never judged "
      "(imports are witnesses)",
      not SC.court_repetition(jit)["advisories"] and
      not SC.court_vocabulary(jit)["advisories"])

# ---------------------------------------------------- contrast
flat = {"bpm": 120, "lengthBars": 16,
        "sections": [{"name": "verse", "startBar": 0},
                     {"name": "chorus", "startBar": 8}],
        "tracks": [track("lead", range(16))]}
v = SC.court_contrast(flat)
check("contrast: identical verse/chorus = no_contrast advisory",
      any(a["kind"] == "no_contrast" for a in v["advisories"]), str(v))
lift = {"bpm": 120, "lengthBars": 16,
        "sections": [{"name": "verse", "startBar": 0},
                     {"name": "chorus", "startBar": 8}],
        "tracks": [track("lead", range(16)),
                   track("pad", range(8, 16), riff=[0, 8], pitch=72)]}
check("contrast: a chorus that adds a lane passes",
      not SC.court_contrast(lift)["advisories"])

# ---------------------------------------------------- vocabulary
spray_riffs = [[i * 3 for i in range(5) if (b + 1) >> i & 1]
               for b in range(20)]        # bar b = bit pattern of b+1:
assert len({tuple(r) for r in spray_riffs}) == 20   # every bar one-off
spray = {"bpm": 120, "lengthBars": 20, "tracks": [{
    "name": "lead", "notes": [
        {"start": b * 4 + o / 4.0, "len": 0.3, "pitch": 60, "vel": 90}
        for b, riff in enumerate(spray_riffs) for o in riff]}]}
v = SC.court_vocabulary(spray)
check("vocabulary: one-off-every-bar sprays past the corpus edge (0.82)",
      any(a["kind"] == "vocabulary_spray" for a in v["advisories"]),
      str(v))
check("vocabulary: a riffing lane speaks a vocabulary (no flag)",
      not SC.court_vocabulary(rep)["advisories"])

# ---------------------------------------------------- aggregate
v = SC.court_structure(wander, "pop")
check("aggregate: advisories pool, ok stays True (advisory-first tier)",
      v["ok"] and v["advisories"] and v["court"] == "structure")
check("aggregate: empty song never crashes",
      SC.court_structure({})["ok"])

print()
if FAILS:
    print(f"structure_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("structure_battery: ALL GREEN")
