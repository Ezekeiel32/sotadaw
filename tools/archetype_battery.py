#!/usr/bin/env python3
"""ARCHETYPE LAWS BATTERY — wave 53 (items 078/079/080). Synthetic
wavs + pure song dicts; no renders."""
import math
import os
import sys
import tempfile
import wave as wavmod

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import movement_court as MV  # noqa: E402
import layer_court as LC  # noqa: E402
import lowend_ears as LE  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


# ------------------------------------------- 079 movement is mandatory
pad = {"name": "pad_warm", "notes": [
    {"start": b * 4.0, "len": 4.0, "pitch": 57, "vel": 90}
    for b in range(24)]}
song = {"bpm": 120, "lengthBars": 24, "tracks": [pad]}
v = MV.court_movement(song)
check("movement: a 24-bar static pad flags static_archetype",
      v["advisories"] and v["advisories"][0]["track"] == "pad_warm",
      str(v))
acts = MV.heal_movement(song, v)
check("heal: fx_filter minted + a 4-point cutoff journey lands",
      acts and pad["fx"][0]["id"] == "fx_filter" and
      len(pad["automation"][0]["points"]) == 4 and
      pad["automation"][0]["target"] == "fx[0].cutoff", str(acts))
check("heal: re-court clean (the journey IS motion)",
      not MV.court_movement(song)["advisories"])

lively = {"name": "reese_bass", "notes": [
    {"start": b * 4.0, "len": 4.0, "pitch": 40,
     "vel": 80 + (b % 4) * 8} for b in range(24)]}
check("movement: velocity life passes (no false static)",
      not MV.court_movement({"bpm": 120, "lengthBars": 24,
                             "tracks": [lively]})["advisories"])
short = {"name": "pad_x", "notes": [
    {"start": b * 4.0, "len": 4.0, "pitch": 57, "vel": 90}
    for b in range(8)]}
check("movement: an 8-bar phrase is a phrase, not a patch (min 16)",
      not MV.court_movement({"bpm": 120, "lengthBars": 8,
                             "tracks": [short]})["advisories"])
# hand work sacred: a lane whose filter already journeys is never touched
handed = {"name": "pad_z", "fx": [{"id": "fx_filter",
                                   "params": {"cutoff": 4000}}],
          "automation": [{"target": "fx[0].cutoff",
                          "points": [{"beat": 0, "v": 800},
                                     {"beat": 64, "v": 9000}]}],
          "notes": [{"start": b * 4.0, "len": 4.0, "pitch": 57, "vel": 90}
                    for b in range(24)]}
check("law: an existing filter journey = motion (never re-healed)",
      not MV.court_movement({"bpm": 120, "lengthBars": 24,
                             "tracks": [handed]})["advisories"])

# ------------------------------------------- 080 band ownership
SR = 44100


def shot(freq, sec=0.4, noise_hi=None):
    t = np.arange(int(SR * sec)) / SR
    x = np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.12)
    if noise_hi:
        rng = np.random.RandomState(3)
        n = rng.randn(len(t)) * np.exp(-t / 0.02)
        from numpy.fft import rfft, irfft, rfftfreq
        S = rfft(n)
        f = rfftfreq(len(t), 1 / SR)
        S[f < noise_hi] = 0
        x = irfft(S, len(t)).real          # PURE click — no sub bleed
    return (x / max(np.abs(x).max(), 1e-9)).astype(np.float64)


sub = shot(45)
body = shot(48)                      # a second sub-owner = dual claim
click = shot(50, noise_hi=2500)      # air/hi-mid owner
v = LC.band_ownership([("kick_sub", sub), ("kick_body", body),
                       ("kick_click", click)], SR)
check("ownership: two sub-claimants (>45% same band) = dual-claim "
      "advisory naming owner + carve",
      any(a["kind"] == "band_dual_claim" and
          {a["owner"], a["carve"]} == {"kick_sub", "kick_body"}
          for a in v["advisories"]), str(v))
v2 = LC.band_ownership([("kick_sub", sub), ("kick_click", click)], SR)
check("ownership: sub + click own different bands (clean stack)",
      not v2["advisories"], str(v2))

# ------------------------------------------- 078 missing fundamental
def write_wav(path, x):
    w = wavmod.open(path, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())
    w.close()


tmp = tempfile.mkdtemp(prefix="arch_")
dur = 16 * 0.5                       # 8 notes x 1 beat @120
t = np.arange(int(SR * dur)) / SR
f0 = 440.0 * 2 ** ((33 - 69) / 12.0)          # A1 = 55Hz... need <60: A1=55
f0 = 440.0 * 2 ** ((31 - 69) / 12.0)          # G1 ~ 49Hz
pure = 0.5 * np.sin(2 * np.pi * f0 * t)
satur = np.tanh(2.5 * pure) * 0.5
p_pure, p_sat = os.path.join(tmp, "pure.wav"), os.path.join(tmp, "sat.wav")
write_wav(p_pure, pure)
write_wav(p_sat, satur)
song8 = {"bpm": 120, "lengthBars": 4, "tracks": [
    {"name": "sub_808", "notes": [
        {"start": float(b), "len": 1.0, "pitch": 31, "vel": 100}
        for b in range(8)]}]}
v = LE.court_missing_fundamental(p_pure, song8)
check("fundamental: a PURE 49Hz sine sub (harmonics absent) flags",
      any(a["kind"] == "missing_fundamental" for a in v["advisories"]),
      str(v))
v2 = LE.court_missing_fundamental(p_sat, song8)
check("fundamental: the SATURATED twin passes (harmonics carry it)",
      not v2["advisories"], str(v2))
acts = LE.heal_missing_fundamental(song8, v)
check("heal: fx_bass_grit lands (w69 multiband — sub clean, mids grow "
      "grit)",
      acts and song8["tracks"][0]["fx"][0]["id"] == "fx_bass_grit",
      str(acts))
check("heal: a lane already saturated is never doubled (hand work "
      "sacred)", not LE.heal_missing_fundamental(song8, v))
v3 = LE.court_missing_fundamental(p_pure, {"bpm": 120, "tracks": [
    {"name": "sub_808", "notes": [
        {"start": 0.0, "len": 1.0, "pitch": 31, "vel": 100}]}]})
check("fundamental: <6 sub notes = silent court (no thin evidence)",
      not v3["advisories"])

# ------------------------------------------- 138 heal from the score
own = LC.band_ownership([("kick_sub", sub), ("kick_body", body),
                         ("kick_click", click)], SR)
hsong = {"bpm": 120, "tracks": [
    {"name": "kick_sub", "notes": [{"start": 0, "len": 0.4, "pitch": 36,
                                    "vel": 110}]},
    {"name": "kick_body", "notes": [{"start": 0, "len": 0.4, "pitch": 36,
                                     "vel": 100}]},
    {"name": "kick_click", "notes": [{"start": 0.02, "len": 0.1,
                                      "pitch": 36, "vel": 90}]}]}
eds = LC.heal_layers(hsong, own, pairs=[{"late": "kick_click",
                                         "tau_ms": 6.0}])
carves = [e for e in eds if e["kind"] == "band_carve"]
check("heal(138): the dual-claim carve LANDS on the non-owner "
      "(fx_hipass out of the low band)",
      carves and carves[0]["track"] == "kick_body" and
      hsong["tracks"][1]["fx"][0]["id"] == "fx_hipass", str(eds))
nudges = [e for e in eds if e["kind"] == "transient_nudge"]
check("heal(138): the 6ms flam nudges the late layer into the pocket",
      nudges and abs(hsong["tracks"][2]["notes"][0]["start"]
                     - (0.02 - 6.0 * 120 / 60000.0)) < 1e-6, str(nudges))
check("heal(138): once-markers make the heal idempotent",
      not LC.heal_layers(hsong, own, pairs=[{"late": "kick_click",
                                             "tau_ms": 6.0}]))
mid_own = {"advisories": [{"kind": "band_dual_claim", "band": "mid",
                           "owner": "snare_body", "carve": "snare_air"}]}
msong = {"bpm": 120, "tracks": [{"name": "snare_air", "notes": []}]}
meds = LC.heal_layers(msong, mid_own)
check("heal(138): a contested MID band gets the surgical bell dip, "
      "never LP/HP gutting",
      meds and msong["tracks"][0]["fx"][0]["id"] == "fx_bell" and
      msong["tracks"][0]["fx"][0]["params"]["gain"] == -4.5, str(meds))
check("heal(138): a >20ms offset is intent, not flam (no nudge)",
      not LC.heal_layers({"bpm": 120, "tracks": [
          {"name": "x", "notes": [{"start": 0, "len": 1, "pitch": 36,
                                   "vel": 90}]}]}, None,
          pairs=[{"late": "x", "tau_ms": 35.0}]))

# ------------------------------------------- 214 layer-count guard
v = LC.layer_count_guard(["kick_sub", "kick_body", "kick_click",
                          "kick_boom", "snare_body", "snare_crack"])
check("guard(214): 4 kick layers breach the cap of 3 (snare at 2 is "
      "fine)",
      len(v["advisories"]) == 1 and v["advisories"][0]["family"] == "kick"
      and v["advisories"][0]["count"] == 4, str(v))
check("guard(214): 3 layers = the modern standard, silent",
      not LC.layer_count_guard(["kick_sub", "kick_body",
                                "kick_click"])["advisories"])

# ------------------------------------------- w74 articulations (161)
import articulation as ART
asong = {"bpm": 120, "lengthBars": 8, "tracks": [
    {"name": "strings", "source": {"id": "supersaw_jp"},
     "notes": [{"start": 4.0 + i * 2.0, "len": 1.8, "pitch": 60 + i,
                "vel": 90} for i in range(4)]}]}
eds = ART.apply_articulation(asong, "strings", "staccato")
n0 = asong["tracks"][0]["notes"][0]
check("articulation(161): staccato = 40% lengths + notes pulled 60ms "
      "early + attack zone landed",
      eds and eds[0]["notes_shaped"] == 4 and
      abs(n0["len"] - 1.8 * 0.40) < 1e-6 and
      abs(n0["start"] - (4.0 - 0.06 * 2)) < 1e-3 and
      eds[0]["zones"].get("attack") == 0.008, str(eds))
check("articulation: idempotent per (lane, art)",
      ART.apply_articulation(asong, "strings", "staccato") == [])
lsong = {"bpm": 120, "lengthBars": 8, "tracks": [
    {"name": "cello", "source": {"id": "nosuchvoice"},
     "notes": [{"start": 0.0, "len": 1.0, "pitch": 48, "vel": 90},
               {"start": 2.0, "len": 1.0, "pitch": 50, "vel": 90}]}]}
eds2 = ART.apply_articulation(lsong, "cello", "legato")
check("articulation: legato reaches the NEXT note (len 2.0*1.02) and "
      "zoneless voices get length/offset only",
      eds2 and not eds2[0]["zones"] and
      abs(lsong["tracks"][0]["notes"][0]["len"] - 2.04) < 1e-6, str(eds2))
check("articulation: unknown name = loud error",
      ART.apply_articulation(lsong, "cello", "zzz")[0]["kind"] == "error")

# ------------------------------------------- w77 true legato (162)
lsong2 = {"bpm": 120, "lengthBars": 4, "tracks": [
    {"name": "lead", "source": {"id": "supersaw"},
     "notes": [{"start": 0.0, "len": 1.9, "pitch": 57, "vel": 100},
               {"start": 2.0, "len": 1.9, "pitch": 64, "vel": 100},
               {"start": 8.0, "len": 1.0, "pitch": 60, "vel": 100}]}]}
eds3 = ART.legato_ties(lsong2, "lead", glide_ms=80)
ns = lsong2["tracks"][0]["notes"]
check("legato(162): phrase-internal joins tie into overlaps; the "
      "4-beat rest stays a phrase break",
      eds3[0]["tied"] == 1 and abs(ns[0]["len"] - 2.08) < 1e-6 and
      ns[1]["len"] == 1.9, str(eds3))
check("legato: a retriggering voice SWAPS to lead_legato with glide",
      lsong2["tracks"][0]["source"]["id"] == "lead_legato" and
      lsong2["tracks"][0]["source"]["params"]["glide"] == 80.0)
check("legato: idempotent (legato_tied marker)",
      ART.legato_ties(lsong2, "lead") == [])

# ------------------------------------------- w86 punch heal (243)
ps = {"bpm": 140, "tracks": [{"name": "kick_main", "notes": [
    {"start": 0, "len": 0.5, "pitch": 36, "vel": 110}]}]}
e1 = LC.heal_punch(ps, "kick_main")
check("punch(243): first move = fx_transient attack +2 (safe default), "
      "sustain at the gentle edge",
      e1 and ps["tracks"][0]["fx"][0]["id"] == "fx_transient" and
      ps["tracks"][0]["fx"][0]["params"]["attack"] == 2.0 and
      ps["tracks"][0]["fx"][0]["params"]["sustain"] == -3.0, str(e1))
LC.heal_punch(ps, "kick_main")
LC.heal_punch(ps, "kick_main")
e4 = LC.heal_punch(ps, "kick_main")
check("punch: steps cap at the kick table ceiling (+7), then defers "
      "to the source",
      ps["tracks"][0]["fx"][0]["params"]["attack"] == 7.0 and
      LC.heal_punch(ps, "kick_main") == [])
check("punch: non-drum lanes never dialed",
      LC.heal_punch(ps, "nosuch") == [] and
      LC.heal_punch({"tracks": [{"name": "pad", "notes": []}]},
                    "pad") == [])

print()
if FAILS:
    print(f"archetype_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("archetype_battery: ALL GREEN")
