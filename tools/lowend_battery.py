#!/usr/bin/env python3
"""LOW-END BATTERY — proves THE LOW-END COURT (wave 15; R-4/R-5/R-21/R-25).

Pure, deterministic, no renders. Every check is a planted crime the court
must catch, a lawful take it must pardon, or a heal that must land.
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowend_court as LC  # noqa: E402

FAILS = []


def check(name, cond, note=""):
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {name}" + (f" — {note}" if note and not cond else ""))
    if not cond:
        FAILS.append(name)


def _notes(starts, pitch=36, vel=0.9, ln=0.25):
    return [{"start": float(s), "len": ln, "pitch": pitch, "vel": vel}
            for s in starts]


def four_floor_song(bass_on_kicks=True, pump=False, bars=4):
    kicks = _notes([b for b in range(bars * 4)])
    if bass_on_kicks:
        bass = _notes([b for b in range(bars * 4)], pitch=33)
    else:
        bass = _notes([b + 0.5 for b in range(bars * 4)], pitch=33)
    bt = {"name": "bass", "notes": bass}
    if pump:
        bt["fx"] = [{"id": "fx_pump", "params": {"rate": 2.133, "depth": 0.6,
                                                 "release": 0.234}}]
    return {"bpm": 128, "lengthBars": bars, "tracks": [
        {"name": "kick", "notes": kicks}, bt]}


def psy_song(rolling=True, bars=2):
    kicks = _notes([b for b in range(bars * 4)])
    starts = []
    for b in range(bars * 4):
        if rolling:
            starts += [b + 0.25, b + 0.5, b + 0.75]
        else:
            starts += [b, b + 0.5]  # ON the kick + one legal
    bass = _notes(starts, pitch=28, ln=0.22 if rolling else 0.6)
    return {"bpm": 145, "lengthBars": bars, "tracks": [
        {"name": "kick", "notes": kicks},
        {"name": "psy_bass", "notes": bass}]}


# ------------------------------------------------------------- R-5 kernels
r = LC.sidechain_release_ms(120, 0.25)
check("release kernel: 16th @120bpm = 125ms", abs(r - 125.0) < 1e-6, f"{r}")
r = LC.sidechain_release_ms(120, 0.5)
check("release kernel: 8th @120bpm = 250ms", abs(r - 250.0) < 1e-6, f"{r}")
p = LC.pump_params(128, "house")
check("pump params: rate = bpm/60", abs(p["rate"] - 128 / 60.0) < 0.01,
      str(p))
check("pump params: house depth mid-band (8/12)",
      abs(p["depth"] - 8.0 / 12.0) < 0.01, str(p))
check("pump params: release inside fx_pump zone [0.05,0.7]",
      0.05 <= p["release"] <= 0.7, str(p))
p2 = LC.pump_params(140, "trap")
check("pump params: trap depth gentler than house", p2["depth"] < p["depth"],
      f"{p2['depth']} vs {p['depth']}")

# ------------------------------------------------- R-4/R-21 interlock court
s = four_floor_song(bass_on_kicks=True, pump=False)
v = LC.court_interlock(s, "house")
check("interlock: on-kick unpumped house bass CONVICTED",
      not v["ok"] and any(f["kind"] == "kick_bass_pileup"
                          for f in v["flags"]), str(v))
edits = LC.heal_interlock(s, "house", v)
check("interlock heal: fx_pump inserted", any(
    e["kind"] == "pump_insert" for e in edits), str(edits))
check("interlock heal: re-court OK", LC.court_interlock(s, "house")["ok"])
fx = (s["tracks"][1].get("fx") or [])
check("interlock heal: pump release tempo-locked",
      fx and abs(fx[0]["params"]["release"] -
                 LC.pump_params(128, "house")["release"]) < 1e-6)

s = four_floor_song(bass_on_kicks=False)
check("interlock: offbeat house bass PARDONED",
      LC.court_interlock(s, "house")["ok"])
s = four_floor_song(bass_on_kicks=True, pump=True)
check("interlock: pumped on-kick bass PARDONED",
      LC.court_interlock(s, "house")["ok"])
check("interlock: no law for ambient (skip)",
      LC.court_interlock(four_floor_song(), "ambient").get("skipped") ==
      "no interlock law")

# shadow-808 advisory (never a conviction)
kicks = _notes([0, 1, 2.5, 3, 4, 5, 6.5, 7])
shadow = {"bpm": 140, "tracks": [
    {"name": "kick", "notes": kicks},
    {"name": "808", "notes": copy.deepcopy(kicks)}]}
v = LC.court_interlock(shadow, "trap")
check("shadow_808: 1:1 shadow = ADVISORY, ok stays True",
      v["ok"] and any(a["kind"] == "shadow_808"
                      for a in v.get("advisories", [])), str(v))
free = copy.deepcopy(shadow)
free["tracks"][1]["notes"][2]["start"] = 2.25  # one pickup off-kick
v = LC.court_interlock(free, "trap")
check("shadow_808: one independent pickup clears the advisory",
      not any(a["kind"] == "shadow_808" for a in v.get("advisories", [])))

# --------------------------------------------------------- R-25 KBBB court
s = psy_song(rolling=False)
v = LC.court_kbbb(s, "psytrance")
check("kbbb: on-kick psy bass CONVICTED", not v["ok"], str(v))
edits = LC.heal_kbbb(s, "psytrance", v)
check("kbbb heal: nudges + clamps landed",
      any(e["kind"] == "nudge" for e in edits) and
      any(e["kind"] == "clamp_len" for e in edits), str(edits[:4]))
v2 = LC.court_kbbb(s, "psytrance")
check("kbbb heal: re-court OK", v2["ok"], str(v2))
check("kbbb: rolling 16ths-2/3/4 bass PARDONED",
      LC.court_kbbb(psy_song(rolling=True), "goa")["ok"])
check("kbbb: no law outside psy family",
      LC.court_kbbb(psy_song(rolling=False), "house").get("skipped") ==
      "not a psy-rolling genre")

# ====================================== 097 frequency-division court (w32)
def psy_kick_song(kick_src="kick_808", carve=False):
    kick = {"name": "kick", "source": {"id": kick_src},
            "notes": _notes([float(b) for b in range(8)])}
    if carve:
        kick["fx"] = [{"id": "fx_bell", "params": {"freq": 55.0,
                                                   "gain": -4.0, "q": 2.0}}]
    return {"bpm": 145, "lengthBars": 2, "tracks": [
        kick,
        {"name": "psy_bass", "notes": _notes(
            [b + o for b in range(8) for o in (0.25, 0.5, 0.75)],
            pitch=33, ln=0.22)}]}


s = psy_kick_song()
v = LC.court_freq_division(s, "psytrance")
check("freq_division: boom kick + no carve in psy CONVICTED",
      not v["ok"] and v["flags"][0]["kind"] == "kick_owns_sub", str(v))
edits = LC.heal_freq_division(s, "psytrance", v)
check("freq_division heal: fx_bell carve at the bass root (A1=55Hz)",
      edits and edits[0]["kind"] == "kick_carve" and
      54 <= edits[0]["hz"] <= 56, str(edits))
check("freq_division heal: re-court OK",
      LC.court_freq_division(s, "psytrance")["ok"])
check("freq_division heal: idempotent",
      LC.heal_freq_division(s, "psytrance") == [])
check("freq_division: carved kick passes",
      LC.court_freq_division(psy_kick_song(carve=True), "psytrance")["ok"])
check("freq_division: punchy (non-boom) kick passes",
      LC.court_freq_division(psy_kick_song("kick_punch_tight"),
                             "psytrance")["ok"])
check("freq_division: non-psy genre skipped",
      LC.court_freq_division(psy_kick_song(), "house")
      .get("skipped", "").startswith("not a psy"))

# ============================================ 064 delay grid court (w39)
check("division kernel: 3/16 at 128bpm = 351.56ms (the pop/EDM throw)",
      abs(LC.note_division_ms(128, "3/16") - 351.56) < 0.1,
      str(LC.note_division_ms(128, "3/16")))
dg = {"bpm": 120, "tracks": [
    {"name": "lead", "fx": [{"id": "fx_delay",
                             "params": {"time": 0.375, "feedback": 0.4}}],
     "notes": []}]}
v = LC.court_delay_grid(dg)
check("delay_grid: SECONDS in the ms zone CONVICTED (engine-proven "
      "comb class)",
      not v["ok"] and v["flags"][0]["kind"] == "seconds_in_ms_zone",
      str(v))
eds = LC.heal_delay_grid(dg, v)
check("delay_grid UNIT HEAL: 0.375s -> 375ms (the tempo-lock restored)",
      eds and eds[0]["kind"] == "delay_unit_heal" and
      dg["tracks"][0]["fx"][0]["params"]["time"] == 375.0 and
      LC.court_delay_grid(dg)["ok"], str(eds))
offg = {"bpm": 120, "tracks": [
    {"name": "lead", "fx": [{"id": "fx_delay",
                             "params": {"time": 430, "feedback": 0.4}}],
     "notes": []}]}
v = LC.court_delay_grid(offg)
check("delay_grid: real-ms off-grid = ADVISORY (winners carry them)",
      v["ok"] and any(a["kind"] == "offgrid_delay"
                      for a in v.get("advisories", [])), str(v))
ok_d = {"bpm": 120, "tracks": [
    {"name": "lead", "fx": [{"id": "fx_delay",
                             "params": {"time": 375, "feedback": 0.4}}],
     "notes": []}]}
check("delay_grid: a 3/16 throw at 120bpm passes",
      LC.court_delay_grid(ok_d)["ok"])
slap = {"bpm": 120, "tracks": [
    {"name": "vox", "fx": [{"id": "fx_delay",
                            "params": {"time": 95, "feedback": 0.0}}],
     "notes": []}]}
check("delay_grid: SLAPBACK (95ms, fb 0) exempt — time-domain idiom",
      LC.court_delay_grid(slap)["ok"])

# ---------------------------------------------------- R-5 sidechain court
s = four_floor_song(bass_on_kicks=False, pump=False)
v = LC.court_sidechain(s, "techno")
check("sidechain: unpumped techno bass = advisory, ok True",
      v["ok"] and any(a["kind"] == "no_pump" for a in v["advisories"]))
s = four_floor_song(pump=True)
s["tracks"][1]["fx"][0]["params"]["rate"] = 0.9  # off tempo grid
v = LC.court_sidechain(s, "techno")
check("sidechain: off-grid pump rate = advisory",
      any(a["kind"] == "pump_rate_offgrid" for a in v["advisories"]), str(v))

# ------------------------------------------------------ R-5 808 env court
def env_song(decay_s, slide_ms=None, genre_track="808_sub"):
    params = {"decay": decay_s}
    if slide_ms is not None:
        params["slide"] = slide_ms
    return {"bpm": 140, "tracks": [
        {"name": genre_track,
         "source": {"id": "sub_808_slide", "params": params},
         "notes": _notes([0, 1, 2, 3], pitch=29)}]}


v = LC.court_808_env(env_song(0.1), "trap")
check("env808: 100ms choked decay in TRAP convicted",
      not v["ok"] and v["flags"][0]["kind"] == "env808", str(v))
check("env808: 600ms decay in trap pardoned",
      LC.court_808_env(env_song(0.6), "trap")["ok"])
check("env808: 200ms decay in drill pardoned",
      LC.court_808_env(env_song(0.2), "drill")["ok"])
check("env808: corpus law — Chezy 450ms + eval 1800ms pass under drill",
      LC.court_808_env(env_song(0.45), "drill")["ok"] and
      LC.court_808_env(env_song(1.8), "drill")["ok"])
check("env808: 3s drone under 4x4 house convicted",
      not LC.court_808_env(env_song(3.0), "house")["ok"])
v = LC.court_808_env(env_song(0.6, slide_ms=10), "trap")
check("env808: 10ms glide in trap convicted (window 80-120)",
      not v["ok"] and any(f["kind"] == "glide808" for f in v["flags"]))
s = env_song(0.1, slide_ms=10)
edits = LC.heal_env808(s, "trap")
check("env808 heal: decay + slide clamped to window edges",
      any(e["kind"] == "decay_clamp" for e in edits) and
      any(e["kind"] == "slide_clamp" for e in edits), str(edits))
check("env808 heal: re-court OK", LC.court_808_env(s, "trap")["ok"])
prm = s["tracks"][0]["source"]["params"]
check("env808 heal: native units (decay s, slide ms)",
      prm["decay"] == 0.3 and prm["slide"] == 80.0, str(prm))
check("env808: no law without genre window",
      LC.court_808_env(env_song(0.1), "ambient").get("skipped") ==
      "no 808 env law")

# --------------------------------------------------- R-16 sub width court
s = {"bpm": 120, "tracks": [
    {"name": "sub_808", "pan": 0.5, "notes": _notes([0, 1]),
     "fx": [{"id": "fx_widen", "params": {}}]}]}
v = LC.court_sub_width(s)
check("sub_width: panned + widened sub = TWO convictions",
      not v["ok"] and {f["kind"] for f in v["flags"]} ==
      {"panned_sub", "widened_sub"}, str(v))
edits = LC.heal_sub_width(s, v)
check("sub_width heal: centered + unwidened",
      s["tracks"][0]["pan"] == 0.0 and not s["tracks"][0]["fx"], str(edits))
check("sub_width heal: re-court OK", LC.court_sub_width(s)["ok"])
s = {"bpm": 120, "tracks": [
    {"name": "bass_synth", "pan": 0.4, "notes": _notes([0])}]}
check("sub_width: non-sub bass lane may pan (mid-bass is free)",
      LC.court_sub_width(s)["ok"])

# -------------------------------------------------------- R-18 foley court
s = {"bpm": 90, "tracks": [
    {"name": "vinyl_crackle", "gainDb": 0.0, "notes": _notes([0])}]}
v = LC.court_foley(s)
check("foley: 0dB crackle convicted (foley_loud)",
      not v["ok"] and v["flags"][0]["kind"] == "foley_loud", str(v))
check("foley: missing HP = advisory only",
      any(a["kind"] == "foley_in_sub" for a in v["advisories"]) and
      all(f["kind"] != "foley_in_sub" for f in v["flags"]))
LC.heal_foley(s, v)
check("foley heal: ducked to -8dB + re-court OK",
      s["tracks"][0]["gainDb"] == -8.0 and LC.court_foley(s)["ok"])
s = {"bpm": 90, "tracks": [
    {"name": "texture_pad", "gainDb": -12.0, "notes": _notes([0]),
     "fx": [{"id": "fx_filter", "params": {"cutoff": 300}}]}]}
v = LC.court_foley(s)
check("foley: quiet HP'd texture fully clean",
      v["ok"] and not v["advisories"], str(v))

# ---------------------------------------------------------- aggregate heal
s = four_floor_song(bass_on_kicks=True)
s["tracks"][1]["name"] = "sub_bass"
s["tracks"][1]["pan"] = 0.6
v = LC.court_lowend(s, "house", heal=True)
check("aggregate: convicted house song heals to green",
      v["interlock_after"]["ok"] and v["sub_width_after"]["ok"],
      str({k: w.get("ok") for k, w in v.items() if isinstance(w, dict)}))
check("aggregate: heal ledger carries both courts",
      set(v["heals"]) >= {"interlock", "sub_width"}, str(v.get("heals")))
clean = four_floor_song(bass_on_kicks=False, pump=True)
v = LC.court_lowend(clean, "house")
check("aggregate: clean song ok, no heals key", v["ok"] and "heals" not in v)

print()
if FAILS:
    print(f"lowend_battery: {len(FAILS)} RED — " + "; ".join(FAILS))
    sys.exit(1)
print("lowend_battery: ALL GREEN")
