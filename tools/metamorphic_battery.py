#!/usr/bin/env python3
"""METAMORPHIC + SYMBOLIC-INVARIANTS BATTERY — wave 63 (items 182/183).
Pure."""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metamorphic_court as MM  # noqa: E402
import symbolic_invariants as SI  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


SONG = {"bpm": 120, "lengthBars": 16, "key": "C major",
        "chords": [{"bar": 1, "chord": "C"}, {"bar": 3, "chord": "Am7"}],
        "tracks": [
            {"name": "keys", "pan": -0.3, "notes": [
                {"start": b * 4.0 + o, "len": 1.0,
                 "pitch": (60, 64, 67)[o % 3], "vel": 90}
                for b in range(16) for o in range(3)]},
            {"name": "bass", "pan": 0.0, "notes": [
                {"start": b * 4.0, "len": 3.5, "pitch": 36 + (b % 2) * 5,
                 "vel": 100} for b in range(16)]}]}

# ------------------------------------------------- transforms are true
t3 = MM.transpose(SONG, 3)
check("transpose: pitches +3, key C->Eb, chords C->Eb / Am7->Cm7",
      t3["tracks"][0]["notes"][0]["pitch"] == 63 and
      t3["key"].startswith("Eb") and
      t3["chords"][0]["chord"] == "Eb" and
      t3["chords"][1]["chord"] == "Cm7", str(t3["chords"]))
check("tempo_shift: bpm only, beats untouched",
      MM.tempo_shift(SONG, 0.06)["bpm"] == 127.2 and
      MM.tempo_shift(SONG, 0.06)["tracks"][0]["notes"][0]["start"] ==
      SONG["tracks"][0]["notes"][0]["start"])
check("pan_mirror flips signs; lane_reorder keeps content",
      MM.pan_mirror(SONG)["tracks"][0]["pan"] == 0.3 and
      MM.lane_reorder(SONG)["tracks"][0]["name"] == "bass")

# ------------------------------------------------- the court holds
v = MM.run_metamorphic(SONG, "pop")
check("clean take: every neutral transform preserves every verdict",
      v["ok"] and v["checked"] >= 20, str(v))

# ------------------------------------------------- detection power
broken = MM.transpose(SONG, 3)
broken["key"] = "C major"          # the BROKEN transform: pitches moved,
fp_base = MM._fingerprint(SONG, "pop")     # key left behind
fp_bad = MM._fingerprint(broken, "pop")
check("planted bug: pitches-without-key SHIFTS the key verdict "
      "(the court can catch)",
      fp_bad.get("key_sour") != fp_base.get("key_sour") or
      fp_bad.get("key_ok") != fp_base.get("key_ok"),
      f"{fp_base} vs {fp_bad}")

# ------------------------------------------------- 182 the invariants
pm = SI.parallel_motion({"tracks": [
    {"name": "lead", "notes": [
        {"start": float(b), "len": 0.9, "pitch": 60 + b, "vel": 90}
        for b in range(16)]},
    {"name": "harm", "notes": [
        {"start": float(b), "len": 0.9, "pitch": 67 + b, "vel": 90}
        for b in range(16)]}]})
check("parallels: two lanes locked a fifth apart, moving together = "
      "counted", pm["parallel_perfects"] >= 12, str(pm))
v = SI.invariants({"lengthBars": 8, "tracks": [
    {"name": "lead", "notes": [
        {"start": float(b), "len": 0.9, "pitch": 60 + b, "vel": 90}
        for b in range(32)]},
    {"name": "harm", "notes": [
        {"start": float(b), "len": 0.9, "pitch": 67 + b, "vel": 90}
        for b in range(32)]}]}, "citypop")
check("invariants: the lockstep pair flags parallel_perfects "
      "(non-power genre)",
      any(a["kind"] == "parallel_perfects" for a in v["advisories"]),
      str(v["advisories"]))
check("invariants: power-chord genres keep their fifths (genre gate)",
      not any(a["kind"] == "parallel_perfects" for a in
              SI.invariants({"lengthBars": 8, "tracks": [
                  {"name": "gtr", "notes": [
                      {"start": float(b), "len": 0.9, "pitch": 48 + b,
                       "vel": 90} for b in range(32)]},
                  {"name": "gtr2", "notes": [
                      {"start": float(b), "len": 0.9, "pitch": 55 + b,
                       "vel": 90} for b in range(32)]}]},
                  "thrash metal")["advisories"]))

leap = {"lengthBars": 8, "tracks": [{"name": "keys", "notes": []}]}
for b in range(8):
    root = 48 + (b % 2) * 18           # comp leaping wildly
    for p in (root, root + 4, root + 7):
        leap["tracks"][0]["notes"].append(
            {"start": b * 4.0, "len": 4.0, "pitch": p, "vel": 90})
vl = SI.vl_smoothness(leap)
check("voice leading: an 18-semitone comp leap measures rough (>4)",
      vl and vl["mean_semitone_motion"] > 4.0, str(vl))
smooth = {"lengthBars": 8, "tracks": [{"name": "keys", "notes": []}]}
for b in range(8):
    for p in ((60, 64, 67) if b % 2 == 0 else (60, 65, 69)):
        smooth["tracks"][0]["notes"].append(
            {"start": b * 4.0, "len": 4.0, "pitch": p, "vel": 90})
vs = SI.vl_smoothness(smooth)
check("voice leading: C->F/A common-tone comp measures smooth (<=2)",
      vs and vs["mean_semitone_motion"] <= 2.0, str(vs))

ent_drone = SI.pitch_entropy({"tracks": [{"name": "lead", "notes": [
    {"start": float(b), "len": 1.0, "pitch": 60, "vel": 90}
    for b in range(32)]}]})
ent_spray = SI.pitch_entropy({"tracks": [{"name": "lead", "notes": [
    {"start": float(b), "len": 1.0, "pitch": 60 + (b * 7) % 12, "vel": 90}
    for b in range(48)]}]})
check("entropy: a drone ~0 bits, the full-chromatic spray ~3.58",
      ent_drone == 0.0 and ent_spray > 3.3,
      f"drone={ent_drone} spray={ent_spray}")

check("law: empty songs never crash",
      SI.invariants({})["ok"] and MM.run_metamorphic({})["ok"])

print()
if FAILS:
    print(f"metamorphic_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("metamorphic_battery: ALL GREEN")
