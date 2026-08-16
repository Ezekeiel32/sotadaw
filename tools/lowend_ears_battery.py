#!/usr/bin/env python3
"""LOW-END EARS BATTERY — proves the audio-domain low-end courts (wave 16).

Synthesizes wavs with PLANTED crimes (decorrelated sub, pure-sine 808,
kick/bass co-peak) and lawful takes; every verdict + heal is asserted.
Deterministic (fixed phases, no RNG).
"""
import json
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowend_ears as LE  # noqa: E402

SR = 44100
FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def tone(f, secs, sr=SR, amp=0.5, phase=0.0):
    t = np.arange(int(secs * sr)) / sr
    return amp * np.sin(2 * np.pi * f * t + phase)


def write_wav(path, left, right, sr=SR, subtype="PCM_16"):
    import soundfile as sf
    sf.write(path, np.stack([left, right], axis=1), sr, subtype=subtype)


TMP = tempfile.mkdtemp(prefix="lowend_ears_")


def wavpath(name):
    return os.path.join(TMP, name)


# --------------------------------------------------------------- measure()
# mono sub + driven harmonics + a hat layer = the lawful reference
sub = tone(55, 4.0, amp=0.4) + tone(110, 4.0, amp=0.1) + tone(165, 4.0, amp=0.05)
hat = tone(6000, 4.0, amp=0.05)
write_wav(wavpath("lawful.wav"), sub + hat, sub + hat)
m = LE.measure(wavpath("lawful.wav"))
check("measure: lawful mono sub -> corr ~1", m.get("sub_corr", 0) > 0.98,
      str(m))
check("measure: side ratio ~0", m.get("sub_side_ratio", 1) < 0.02, str(m))
check("measure: driven sub ratio well above sine floor",
      m.get("sine_ratio", 0) > 0.2, str(m))
check("measure: f0 found at 55Hz", abs(m.get("f0_med", 0) - 55) < 4, str(m))

# 24-bit parse law (m1 renders sampwidth=3)
write_wav(wavpath("law24.wav"), sub, sub, subtype="PCM_24")
m24 = LE.measure(wavpath("law24.wav"))
check("measure: 24-bit wav parses identically (the sampwidth law)",
      m24.get("ok") and m24.get("sub_corr", 0) > 0.98 and
      abs(m24.get("f0_med", 0) - 55) < 4, str(m24))

# ------------------------------------------------------- 050 sub-mono court
# planted crime: sub L/R at different phase + different tones (wide patch)
wide_l = tone(55, 4.0, amp=0.4) + tone(80, 4.0, amp=0.2)
wide_r = tone(55, 4.0, amp=0.4, phase=np.pi * 0.9) + tone(67, 4.0, amp=0.2)
write_wav(wavpath("wide.wav"), wide_l + hat, wide_r + hat)
v = LE.court_sub_mono(wavpath("wide.wav"), {}, "house")
check("sub_mono: decorrelated sub CONVICTED",
      not v["ok"] and v["flags"][0]["kind"] == "wide_sub", str(v))
check("sub_mono: lawful take pardoned",
      LE.court_sub_mono(wavpath("lawful.wav"), {}, "house")["ok"])
check("sub_mono: texture genre exempt (eval_ambient law)",
      LE.court_sub_mono(wavpath("wide.wav"), {}, "dark_ambient")
      .get("skipped", "").startswith("texture"))
imported = {"tracks": [{"name": "bass_sketch", "notes": []}]}
check("sub_mono: imported record exempt (witness law)",
      LE.court_sub_mono(wavpath("wide.wav"), imported, "house")
      .get("skipped", "").startswith("imported"))

song = {"master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}]}
edits = LE.heal_sub_mono(song, v)
check("sub_mono heal: fx_ms_eq inserted BEFORE the wall",
      song["master"][0]["id"] == "fx_ms_eq" and
      song["master"][0]["params"]["side_low"] == -12.0 and
      song["master"][1]["id"] == "fx_truepeak", str(song["master"]))
song2 = {"master": [{"id": "fx_ms_eq", "params": {"side_low": -3.0,
                                                  "low_freq": 250}},
                    {"id": "fx_truepeak", "params": {}}]}
LE.heal_sub_mono(song2, v)
check("sub_mono heal: existing fx_ms_eq deepened, low_freq pulled to 120",
      song2["master"][0]["params"]["side_low"] == -12.0 and
      song2["master"][0]["params"]["low_freq"] == 120.0,
      str(song2["master"][0]))

# --------------------------------------------------- 077 translation court
pure = tone(55, 4.0, amp=0.5)
mids = tone(800, 4.0, amp=0.15) + tone(2400, 4.0, amp=0.08)
write_wav(wavpath("sine808.wav"), pure + mids, pure + mids)
song808 = {"tracks": [{"name": "808",
                       "source": {"id": "sub_808_slide",
                                  "params": {"drive": 1.0}},
                       "notes": [{"start": 0, "len": 1, "pitch": 33,
                                  "vel": 0.9}]}]}
v = LE.court_translation(wavpath("sine808.wav"), song808, "trap")
check("translation: pure-sine trap 808 = ADVISORY, ok stays True",
      v["ok"] and any(a["kind"] == "sine_808"
                      for a in v.get("advisories", [])), str(v))
check("translation: non-phone-first genre stays silent",
      not LE.court_translation(wavpath("sine808.wav"), song808,
                               "techno").get("advisories"))
check("translation: driven sub no advisory",
      not LE.court_translation(wavpath("lawful.wav"), song808,
                               "trap").get("advisories"))
check("translation: no drive-capable source -> skipped",
      LE.court_translation(wavpath("sine808.wav"),
                           {"tracks": [{"name": "bass",
                                        "source": {"id": "pluck_synth"},
                                        "notes": [{"start": 0}]}]},
                           "trap").get("skipped", "").startswith("no drive"))
edits = LE.heal_translation(song808, {"ok": False})
check("translation heal (explicit ask): drive raised into zone",
      edits and edits[0]["kind"] == "drive_up" and
      2.0 <= song808["tracks"][0]["source"]["params"]["drive"] <= 5.0,
      str(edits))

# ------------------------------------------------------- 051 co-peak court
def beatgrid(f_kick, f_bass, secs=8.0, bpm=120):
    n = int(secs * SR)
    y = np.zeros(n)
    spb = 60.0 / bpm
    t = np.arange(int(0.09 * SR)) / SR
    thump = np.sin(2 * np.pi * f_kick * t) * np.exp(-t * 30) * 0.9
    b = 0.0
    while (b + 0.6) * spb * SR < n:
        i = int(b * spb * SR)
        y[i:i + len(thump)] += thump
        j = int((b + 0.5) * spb * SR)          # bass between kicks
        seg = np.arange(int(0.22 * SR)) / SR
        y[j:j + len(seg)] += np.sin(2 * np.pi * f_bass * seg) * 0.4
        b += 1.0
    return y


ksong = {"bpm": 120, "tracks": [
    {"name": "kick", "notes": [{"start": float(b), "len": 0.2, "pitch": 36,
                                "vel": 1.0} for b in range(14)]}]}
y = beatgrid(60, 61)
write_wav(wavpath("copeak.wav"), y, y)
v = LE.court_copeak(wavpath("copeak.wav"), ksong)
check("copeak: kick 60Hz vs bass 61Hz = advisory (same 1/3-oct)",
      v["ok"] and any(a["kind"] == "kick_bass_copeak"
                      for a in v.get("advisories", [])), str(v))
y = beatgrid(60, 95)
write_wav(wavpath("split.wav"), y, y)
v = LE.court_copeak(wavpath("split.wav"), ksong)
check("copeak: kick 60Hz vs bass 95Hz clean (distinct bands)",
      not v.get("advisories"), str(v))
check("copeak: no kick lane -> skipped",
      LE.court_copeak(wavpath("copeak.wav"), {"tracks": []})
      .get("skipped", "").startswith("needs kick"))

# -------------------------------------------- 113 sub key court (wave 31)
CH = [{"beat": 0.0, "chord": "C"}, {"beat": 8.0, "chord": "F"}]
hat5 = tone(6000, 5.0, amp=0.05)
in_key = tone(65.41, 5.0, amp=0.45) + tone(130.8, 5.0, amp=0.1)  # C2+oct
write_wav(wavpath("subC.wav"), in_key + hat5, in_key + hat5)
song_ch = {"bpm": 120, "chords": CH, "tracks": [
    {"name": "808", "notes": [{"start": float(b), "len": 1, "pitch": 36,
                               "vel": 0.9} for b in range(8)]}]}
v = LE.court_sub_key(wavpath("subC.wav"), song_ch, "trap")
check("sub_key: a true-rendering C sub passes (near-zero cents)",
      v["ok"] and abs(v.get("median_cents", 99)) < 20, str(v))
flat = tone(69.3, 5.0, amp=0.45) + tone(138.6, 5.0, amp=0.1)   # C#2 (!)
write_wav(wavpath("subCs.wav"), flat + hat5, flat + hat5)
v = LE.court_sub_key(wavpath("subCs.wav"), song_ch, "trap")
check("sub_key: sub rendering +100c off its C notes CONVICTED "
      "(the flat-sample class)",
      not v["ok"] and v["flags"][0]["kind"] == "sub_detuned" and
      80 <= v["median_cents"] <= 120, str(v))
check("sub_key: no notated sub -> skipped (the note is the contract)",
      LE.court_sub_key(wavpath("subCs.wav"), {"bpm": 120, "tracks": []},
                       "trap").get("skipped", "").startswith("too few"))
check("sub_key: imported record skipped (witness law)",
      LE.court_sub_key(wavpath("subCs.wav"),
                       {"bpm": 120, "chords": CH,
                        "tracks": [{"name": "bass_sketch", "notes": []}]},
                       "trap").get("skipped", "").startswith("imported"))
# glide frames must not vote: a sweeping sub is performance, not detune
t_sw = np.arange(int(5.0 * SR)) / SR
sweep = 0.45 * np.sin(2 * np.pi * (50 * t_sw + 0.5 * 16 * t_sw ** 2))
write_wav(wavpath("subglide.wav"), sweep + hat5, sweep + hat5)
v = LE.court_sub_key(wavpath("subglide.wav"), song_ch, "trap")
check("sub_key: gliding sub never convicts (the MOTION gate skips it)",
      v.get("ok", False), str(v))

# --------------------------------------- 139 kick tuning court (wave 32)
def kick_wav(f_hz, decay_s, secs=8.0, bpm=120):
    n = int(secs * SR)
    y = np.random.default_rng(3).standard_normal(n) * 0.003   # honest floor
    t = np.arange(int(1.5 * SR)) / SR
    boom = np.sin(2 * np.pi * f_hz * t) * np.exp(-t / decay_s) * 0.7
    for b in range(8):
        i = int(b * (60.0 / bpm) * SR)
        y[i:i + len(boom)] += boom[:max(0, min(len(boom), n - i))]
    return y


ksong = {"bpm": 120, "key": "C major", "lengthBars": 2, "tracks": [
    {"name": "kick", "source": {"id": "kick_808"},
     "notes": [{"start": float(b), "len": 1.0, "pitch": 36, "vel": 0.95}
               for b in range(8)]}]}
g_boom = kick_wav(49.0, 0.6)             # G1 = the FIFTH of C: lawful
write_wav(wavpath("kickG.wav"), g_boom, g_boom)
v = LE.court_kick_tuning(wavpath("kickG.wav"), ksong, "gabber")
check("kick_tuning: tonal boom ON the fifth passes (+-50c law)",
      v["ok"] and abs(v.get("median_cents", 99)) < 50, str(v))
fs_boom = kick_wav(46.9, 0.6)            # F#1: 100c under the fifth
write_wav(wavpath("kickFs.wav"), fs_boom, fs_boom)
v = LE.court_kick_tuning(wavpath("kickFs.wav"), ksong, "gabber")
check("kick_tuning: F# boom in C CONVICTED (systematic off-key)",
      not v["ok"] and v["flags"][0]["kind"] == "kick_off_key", str(v))
song_h = json.loads(json.dumps(ksong))
eds = LE.heal_kick_tuning(song_h, v)
check("kick_tuning heal: notated semitone shift + once-per-lane marker",
      eds and eds[0]["kind"] == "kick_retune" and
      abs(eds[0]["semitones"]) == 1 and
      song_h["tracks"][0]["kick_tune_shift"] == eds[0]["semitones"],
      str(eds))
check("kick_tuning heal: never ping-pongs (marker holds)",
      LE.heal_kick_tuning(song_h, v) == [])
punchy = kick_wav(55.0, 0.03)            # 30ms decay: gone by +120ms
write_wav(wavpath("kickP.wav"), punchy, punchy)
v = LE.court_kick_tuning(wavpath("kickP.wav"), ksong, "rock")
check("kick_tuning: percussive kick EXEMPT BY PHYSICS (no fundamental "
      "in the decay-steady region)",
      v.get("ok", False) and "physics" in str(v.get("skipped", "")) or
      "too few tonal" in str(v.get("skipped", "")), str(v))

# --------------------------------------------------------------- aggregate
song = {"bpm": 120, "master": [{"id": "fx_truepeak", "params": {}}],
        "tracks": [{"name": "wide_pad", "notes": [{"start": 0}]}]}
v = LE.court_ears(wavpath("wide.wav"), song, "house", heal=True)
check("aggregate: wide sub healed at the master (ms_eq before wall)",
      v["heals"].get("sub_mono") and song["master"][0]["id"] == "fx_ms_eq",
      str(v.get("heals")))
v = LE.court_ears(wavpath("lawful.wav"), song, "house")
check("aggregate: lawful take fully ok", v["ok"], str(v))

import shutil
shutil.rmtree(TMP, ignore_errors=True)

print()
if FAILS:
    print(f"lowend_ears_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("lowend_ears_battery: ALL GREEN")
