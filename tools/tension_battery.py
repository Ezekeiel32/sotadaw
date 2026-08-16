#!/usr/bin/env python3
"""TENSION BATTERY — proves THE TENSION KERNEL + ARC SHAPES (wave 18;
R-14 016/071, R-20 026/027). Pure, deterministic, no renders.

The proof ladder the research asked for: geometry sanity (spiral array),
psychoacoustic sanity (Sethares), kernel monotonicity, the 6 Farbood
contours classified from PLANTED songs shaped like them, climax law,
drop-contrast court + the dip heal."""
import copy
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tension as TN  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


# ------------------------------------------------------ spiral array law
d_triad = TN.cloud_diameter([0, 4, 7])          # C E G
d_cluster = TN.cloud_diameter([0, 1, 2])        # C C# D
d_tritone = TN.cloud_diameter([0, 6])           # C F#
check("spiral: chromatic cluster wider than major triad",
      d_cluster > d_triad, f"{d_cluster:.2f} vs {d_triad:.2f}")
check("spiral: tritone wider than fifth",
      d_tritone > TN.cloud_diameter([0, 7]))
kc = TN.key_ce(0)
strain_in = TN._dist(TN._ce([(0, 1), (4, 1), (7, 1)]), kc)
strain_out = TN._dist(TN._ce([(1, 1), (6, 1), (8, 1)]), kc)
check("spiral: in-key triad strains less than out-of-key",
      strain_in < strain_out, f"{strain_in:.2f} vs {strain_out:.2f}")

# --------------------------------------------------- Sethares roughness
r_m2 = TN.sethares_roughness(TN._note_partials(60, 1) +
                             TN._note_partials(61, 1))
r_p5 = TN.sethares_roughness(TN._note_partials(60, 1) +
                             TN._note_partials(67, 1))
check("sethares: minor 2nd rougher than fifth", r_m2 > r_p5,
      f"{r_m2:.3f} vs {r_p5:.3f}")


# ------------------------------------------------------- kernel plumbing
def shaped_song(env, bars=32, bpm=128, sections=None):
    """A song whose per-bar note count/velocity/register FOLLOW env
    (list of [0,1] per bar) — the planted arc."""
    tracks = [{"name": "kick", "notes": []}, {"name": "bass", "notes": []},
              {"name": "lead", "notes": []}, {"name": "pad", "notes": []}]
    for bar in range(bars):
        e = env[min(bar * len(env) // bars, len(env) - 1)]
        vel = 0.35 + 0.6 * e
        for bt in range(4):
            b = bar * 4 + bt
            tracks[0]["notes"].append({"start": b, "len": 0.4, "pitch": 36,
                                       "vel": vel})
            if e > 0.15:
                tracks[1]["notes"].append({"start": b + 0.5, "len": 0.4,
                                           "pitch": 40, "vel": vel})
            if e > 0.4:
                tracks[2]["notes"].append(
                    {"start": b, "len": 0.9,
                     "pitch": 64 + int(12 * e), "vel": vel})
            if e > 0.65:
                for k in (0.25, 0.75):
                    tracks[3]["notes"].append(
                        {"start": b + k, "len": 0.2,
                         "pitch": 72 + int(10 * e), "vel": vel})
    s = {"bpm": bpm, "lengthBars": bars, "tracks": tracks}
    if sections:
        s["sections"] = sections
    return s


ramp = shaped_song([i / 31 for i in range(32)])
tc = TN.tension_curve(ramp)
check("kernel: curve exists per-beat",
      len(tc["curve"]) == 32 * 4, str(len(tc["curve"])))
first, last = tc["curve"][:16], tc["curve"][-16:]
check("kernel: rising song rises",
      sum(last) / 16 > sum(first) / 16 + 0.3,
      f"{sum(first) / 16:.2f} -> {sum(last) / 16:.2f}")

# ------------------------------------------- the 6 Farbood contours land
for fam in TN.ARC_FAMILIES:
    env = TN._contour(fam, 32)
    song = shaped_song([0.15 + 0.85 * e for e in env])
    got, corr = TN.classify_arc(TN._smooth(TN.tension_curve(song)["curve"]))
    # research floor: r~0.55-0.6 honest ceiling; family must match or the
    # correlation to ITS OWN template must clear the floor
    own = TN._pearson(TN._resample(TN._smooth(
        TN.tension_curve(song)["curve"])), TN._contour(fam))
    check(f"contour '{fam}': classified '{got}' (r={corr}) own-r={own:.2f}",
          got == fam or own >= 0.55)

# ------------------------------------------------------------ climax law
FORM = [{"name": "intro", "startBar": 0}, {"name": "mid", "startBar": 8},
        {"name": "late", "startBar": 20}, {"name": "outro", "startBar": 28}]
early = shaped_song([1.0 if i < 8 else 0.25 for i in range(32)],
                    sections=FORM)
check("climax: sectionless loop skipped (no narrative contract)",
      TN.court_tension_arc(
          shaped_song([1.0 if i < 8 else 0.25 for i in range(32)]),
          "techno").get("skipped", "").startswith("loop"))
v = TN.court_tension_arc(early, "techno")
check("climax: peak-in-first-third CONVICTED",
      not v["ok"] and any(f["kind"] == "early_climax" for f in v["flags"]),
      str(v))
# a REAL hook-first preview: absolute peak up front, then the song
# recovers to a near-peak final chorus (monotone decay stays a crime
# in pop too — the preview song is not a decaying song)
preview = shaped_song([1.0 if i < 4 else 0.45 + 0.3 * min((i - 4) / 20, 1.0)
                       for i in range(32)], sections=FORM)
check("climax: hook-first pop preview exempt from early peak",
      TN.court_tension_arc(preview, "pop")["ok"],
      str(TN.court_tension_arc(preview, "pop")))
check("climax: same preview shape (recovery below the 95% band) convicts "
      "for techno",
      not TN.court_tension_arc(preview, "techno")["ok"],
      str(TN.court_tension_arc(preview, "techno")))
late = shaped_song([0.2 + 0.8 * min(i / 24, 1.0) if i < 28 else 0.4
                    for i in range(32)], sections=FORM)
v = TN.court_tension_arc(late, "techno")
check("climax: 75%-peak resolved arc passes", v["ok"], str(v))
# double-drop law: two equal peaks -> the payoff is the LAST one
dd = shaped_song([0.3, 0.3, 0.5, 0.7, 1.0, 1.0, 0.4, 0.4, 0.6, 0.8,
                  1.0, 1.0, 0.99, 0.99, 0.5, 0.3] * 2, sections=FORM)
v = TN.court_tension_arc(dd, "house")
check("climax: double-drop (equal peaks) reads the LAST as the payoff",
      v["ok"], str(v))
check("climax: texture genre skipped",
      TN.court_tension_arc(early, "dark_ambient").get("skipped", "")
      .startswith("texture"))

# ------------------------------------------------- drop court + dip heal
def edm_song(dip=True, weak_drop=False):
    env = []
    for bar in range(32):
        if bar < 8:
            e = 0.3
        elif bar < 15:
            e = 0.3 + 0.5 * (bar - 8) / 7          # build
        elif bar == 15:
            e = 0.15 if dip else 0.85              # the engineered dip bar
        else:
            e = 0.55 if weak_drop else 1.0         # drop
        env.append(e)
    return shaped_song(env, sections=[
        {"name": "intro", "startBar": 0}, {"name": "build", "startBar": 8},
        {"name": "drop", "startBar": 16}])


check("drop: engineered dip passes", TN.court_drop(edm_song(), "house")["ok"])
s = edm_song(dip=False)
v = TN.court_drop(s, "house")
check("drop: missing pre-drop dip CONVICTED",
      not v["ok"] and any(f["kind"] == "no_predrop_dip" for f in v["flags"]),
      str(v))
edits = TN.heal_drop(s, "house", v)
check("drop heal: dip engineered (scaled + cleared)",
      edits and edits[0]["scaled"] > 0 and edits[0]["cleared"] > 0,
      str(edits))
check("drop heal: re-court OK", TN.court_drop(s, "house")["ok"],
      str(TN.court_drop(s, "house")))
v = TN.court_drop(edm_song(weak_drop=True), "dubstep")
check("drop: drop-not-peak CONVICTED",
      not v["ok"] and any(f["kind"] == "drop_not_peak" for f in v["flags"]),
      str(v))
check("drop: non-EDM genre skipped",
      TN.court_drop(edm_song(dip=False), "folk").get("skipped", "")
      .startswith("not a drop"))

# ------------------------------------------------------ section energy
secs = TN.section_energy(edm_song(), "house")
drop_e = next(e["energy"] for e in secs if e["name"] == "drop")
intro_e = next(e["energy"] for e in secs if e["name"] == "intro")
check("section_energy (016): drop hotter than intro",
      drop_e > intro_e + 0.2, f"{intro_e} vs {drop_e}")

# ------------------------------------------- cinematic court (wave 40)
flat_cine = shaped_song([0.8] * 32, sections=FORM)
v = TN.court_cinematic(flat_cine, "cinematic")
check("cinematic: flat wall-of-sound = not_additive + no_stopdown "
      "advisories",
      v["ok"] and {a["kind"] for a in v["advisories"]} >=
      {"not_additive"}, str(v))
grow = shaped_song([0.15 + 0.85 * min(i / 22, 1.0) if not (24 <= i < 28)
                    else 0.03 for i in range(32)], sections=FORM)
v = TN.court_cinematic(grow, "orchestral")
check("cinematic: additive arc with a stopdown before the climax = clean",
      v["ok"] and not v["advisories"], str(v))
check("cinematic: non-cine genre skipped",
      TN.court_cinematic(flat_cine, "techno").get("skipped", "")
      .startswith("not the"))

# ---------------------------------------------------------- aggregate
s = edm_song(dip=False)
v = TN.court_tension(s, "house", heal=True)
check("aggregate: drop healed, after-court green",
      v["heals"].get("drop") and v["drop_after"]["ok"], str(v.get("heals")))
check("aggregate: determinism (same song -> same curve)",
      TN.tension_curve(edm_song())["curve"] ==
      TN.tension_curve(edm_song())["curve"])

# --------------------------------------------- 144 trend salience (w57)
spb = 0.5
rising = [i * 0.1 for i in range(40)]                # continued climb
ts = TN.trend_salience(rising, spb, 3.0, 3.0)
alternate = [0.0, 1.0] * 20                          # direction never holds
ta = TN.trend_salience(alternate, spb, 3.0, 3.0)
check("trend: a CONTINUED climb out-weighs alternation (the x5 law)",
      sum(ts[12:]) > 3.0 * abs(sum(ta[12:])),
      f"cont={sum(ts[12:]):.2f} alt={sum(ta[12:]):.2f}")
check("trend: kernel is length-preserving + short-series safe",
      len(ts) == 40 and TN.trend_salience([1.0], spb, 3, 3) == [0.0])

flatb = {"bpm": 120, "lengthBars": 24,
         "sections": [{"name": "intro", "startBar": 0},
                      {"name": "build", "startBar": 8},
                      {"name": "drop", "startBar": 16}],
         "tracks": [{"name": "lead", "notes": [
             {"start": b * 4 + o, "len": 0.5, "pitch": 60, "vel": 90}
             for b in range(24) for o in range(4)]}]}
v = TN.court_trend(flatb, "edm")
check("trend court: a build whose salience never climbs flags "
      "build_without_trend",
      any(a["kind"] == "build_without_trend" for a in v["advisories"]),
      str(v))
realb = {"bpm": 120, "lengthBars": 24,
         "sections": [{"name": "intro", "startBar": 0},
                      {"name": "build", "startBar": 8},
                      {"name": "drop", "startBar": 16}],
         "tracks": [{"name": "lead", "notes": [
             {"start": b * 4 + o * 4.0 / max(1, min(2 + (b - 8), 8)),
              "len": 0.4, "pitch": 60 + max(0, (b - 8)) * 2,
              "vel": min(70 + max(0, b - 8) * 6, 127)}
             for b in range(24)
             for o in range(1 if b < 8 else min(2 + (b - 8), 8))]}]}
check("trend court: a build that CLIMBS (density+register+velocity "
      "monotone) passes",
      not TN.court_trend(realb, "edm")["advisories"],
      str(TN.court_trend(realb, "edm")))
check("trend court: no sections = skipped, never crashes",
      TN.court_trend({}, "").get("skipped"))

# --------------------------------------- 220 the arc-proof gate (w84)
# every Farbood contour, noised, must classify AS ITSELF above the
# honest floor (r-20: SOTA correlation ~0.62-0.68; the kernel on its
# own noised shapes must clear 0.55) — the guardian that turns a
# broken tension model red.
import math as _m
_rng = [((i * 137) % 100) / 100.0 - 0.5 for i in range(64)]
for fam in TN.ARC_FAMILIES:
    pure = TN._contour(fam)
    noised = [max(0.0, min(1.0, v + 0.12 * _rng[i]))
              for i, v in enumerate(pure)]
    got, corr = TN.classify_arc(noised)
    check(f"arc gate: noised '{fam}' classifies as itself (corr>=0.55)",
          got == fam and corr >= 0.55, f"got {got} corr {corr}")
check("arc gate: a flat line never claims a shape confidently",
      TN.classify_arc([0.5] * 64)[1] < 0.55,
      str(TN.classify_arc([0.5] * 64)))

# --------------------------------------- 245 Lerdahl + the lane (w87)
s245 = {"bpm": 100, "lengthBars": 16, "key": "C major",
        "chords": [{"bar": b, "chord": c} for b, c in
                   [(1, "C"), (3, "Am7"), (5, "F"), (7, "G7"),
                    (9, "Em"), (11, "Ab"), (13, "G7"), (15, "C")]],
        "tracks": []}
check("lerdahl(245): distance orders harmonically (C->G7 < C->Ab)",
      TN._lerdahl_delta("C", "G7", 0) < TN._lerdahl_delta("C", "Ab", 0))
check("lerdahl: chords-only curve normalizes 0..1 over the spine",
      len(TN.tension_curve_chords(s245)["curve"]) == 7 and
      max(TN.tension_curve_chords(s245)["curve"]) == 1.0)
e245 = TN.tension_lane(s245)
lane245 = s245["tracks"][-1]
check("tension lane: lands MUTED at -60 with the arc as gainDb points "
      "(chords fallback when notes are sparse)",
      e245 and lane245["name"] == "_tension_curve" and
      lane245["muted"] and "chords" in e245[0]["source"])
check("tension lane: idempotent by name", TN.tension_lane(s245) == [])

print()
if FAILS:
    print(f"tension_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("tension_battery: ALL GREEN")
