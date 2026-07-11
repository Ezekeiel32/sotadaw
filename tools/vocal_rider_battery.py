#!/usr/bin/env python3
"""VOCAL RIDER battery — the ride kernel must boost buried verses and cut hot
choruses (bounded, slewed, gated: silence comes home to 0), thinning must
collapse straight lines, the full stems path must produce absolute-gainDb
points the ENGINE parses (m1 resave), and the REAL leg rides an actual
imported rap vocal against its actual stems. Deterministic throughout.
"""
import json, os, shutil, subprocess, sys, tempfile, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import numpy as np
from vocal_rider import ride, thin, plan

N = 0


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        print(f"FAIL {N} — {msg}")
        sys.exit(1)
    print(f"ok {N} — {msg}")


# 1 buried verse boosted, hot chorus cut (target 0 margin)
v = np.array([-26.0] * 40 + [-9.0] * 40)     # vocal: quiet verse then hot chorus
b = np.array([-20.0] * 80)                   # steady backing
d, act = ride(v, b, target=0.0, rng=4.0, slew=1.5)
ok(act.all() and d[20:40].mean() > 2.5 and d[60:80].mean() < -2.5,
   f"verse boosted (+{d[20:40].mean():.1f}) / chorus cut ({d[60:80].mean():.1f}), both bounded")
ok(np.abs(d).max() <= 4.0 + 1e-9, "the ride never leaves ±range")

# 2 slew law
steps = np.abs(np.diff(d))
ok(steps.max() <= 1.5 + 1e-9, f"max change per half-beat {steps.max():.2f} <= slew 1.5")

# 3 gate: silence comes home, never boosted
v2 = np.array([-12.0] * 20 + [-120.0] * 30 + [-12.0] * 20)
b2 = np.array([-6.0] * 70)
d2, act2 = ride(v2, b2, target=0.0)
ok(not act2[25:45].any() and abs(d2[44]) < 0.2,
   f"gated tail decays to {d2[44]:.2f} — the fader comes home in silence")

# 4 thinning collapses straight lines
beats = np.arange(100) * 0.5
flatline = np.zeros(100)
ok(len(thin(beats, flatline)) == 2, "a flat ride thins to its two endpoints")
ramp = np.linspace(0, 4, 100)
ok(len(thin(beats, ramp)) <= 4, "a straight ramp thins to a handful of points")

# 5-8 full path through fake stems (no m1 needed)
tmp = tempfile.mkdtemp(prefix="rider_bat_")
sr = 22050
spb = 60.0 / 120.0
dur = 16 * spb                                       # 16 beats
t = np.arange(int(dur * sr)) / sr
vocal = 0.32 * np.sin(2 * np.pi * 220 * t)
vocal[: len(vocal) // 2] *= 0.18                     # buried first half
rng_ = np.random.default_rng(3)
backing = 0.25 * rng_.standard_normal(len(t))


def wr(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


wr(os.path.join(tmp, "00_vocals.wav"), vocal)
wr(os.path.join(tmp, "01_drums.wav"), backing)
song = {"bpm": 120, "lengthBars": 4, "tracks": [
    {"name": "vocals", "gainDb": -2.0, "source": {"kind": "faust", "id": "pluck"},
     "notes": [{"start": 0, "len": 1, "pitch": 60, "vel": 0.8}]},
    {"name": "drums", "source": {"kind": "faust", "id": "kick_808"},
     "notes": [{"start": 0, "len": 1, "pitch": 36, "vel": 0.9}]}]}
out = plan(song, tmp)
ok(out["available"] and out["track"] == "vocals" and out["baseGainDb"] == -2.0,
   "auto-picks the vocal track, reads its base gain")
pts = out["automation"]["points"]
first_half = [p["v"] for p in pts if p["beat"] < 8]
second_half = [p["v"] for p in pts if p["beat"] >= 8]
ok(len(pts) >= 4 and np.mean(first_half) > np.mean(second_half) + 1.5,
   f"buried half ridden UP vs hot half ({np.mean(first_half):.1f} vs {np.mean(second_half):.1f} dB)")
ok(all(-2.0 - 4.001 <= p["v"] <= -2.0 + 4.001 for p in pts)
   and out["automation"]["target"] == "gainDb",
   "points are ABSOLUTE gainDb around the base, bounded by --range")
ok(json.dumps(plan(song, tmp), sort_keys=True) == json.dumps(out, sort_keys=True),
   "deterministic: same stems, same ride")

# 9 no vocal track degrades clean
out2 = plan({"bpm": 120, "tracks": [{"name": "drums"}]}, tmp)
ok(out2["available"] is False and "--track" in out2["reason"],
   "no vocal-ish track: available:false with a usable hint")

# 10 --write leg + the engine parse court (m1 resave)
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
sp = os.path.join(ROOT, "songs", "_rider_scratch.json")
json.dump(song, open(sp, "w"), indent=1)
try:
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "vocal_rider.py"),
                        "_rider_scratch", "--stems", tmp, "--write"],
                       capture_output=True, text=True, cwd=ROOT)
    w = json.load(open(sp))
    tr = next(t for t in w["tracks"] if t["name"] == "vocals")
    ok(r.returncode == 0 and tr.get("automation")
       and tr["automation"][0]["target"] == "gainDb"
       and len(tr["automation"][0]["points"]) == len(pts),
       "--write lands the ride on the TRACK's automation")
    if os.path.exists(M1):
        rs = subprocess.run([M1, "resave", sp, os.path.join(tmp, "resaved.json")],
                            capture_output=True, text=True)
        rj = json.load(open(os.path.join(tmp, "resaved.json")))
        tr2 = next(t for t in rj["tracks"] if t["name"] == "vocals")
        ok(rs.returncode == 0 and tr2.get("automation")
           and len(tr2["automation"][0]["points"]) == len(pts),
           "the ENGINE parses the ride and keeps every point (m1 resave)")
    else:
        ok(True, "engine-parse leg SKIP (m1 not built)")
finally:
    os.path.exists(sp) and os.remove(sp)

# 11 REAL leg: the imported rap vocal vs its actual stems
sj = os.path.join(ROOT, "songs", "_anxrofo.json")
sd = os.path.join(ROOT, "songs", "_anxrofo_stems")
if os.path.exists(sj) and os.path.isdir(sd):
    rsong = json.load(open(sj))
    have = [t.get("name", "") for t in rsong.get("tracks", [])]
    pick = next((n for n in have if "vocal" in n.lower()), None)
    out3 = plan(rsong, sd, track=pick)
    if out3.get("available"):
        base3 = out3["baseGainDb"]
        p3 = out3["automation"]["points"]
        ok(len(p3) >= 8 and all(base3 - 4.001 <= p["v"] <= base3 + 4.001 for p in p3)
           and out3["active_pct"] > 10,
           f"REAL rap stem ridden: {len(p3)} points, {out3['active_pct']}% active, "
           f"boost ~{out3['mean_boost']} / cut ~{out3['mean_cut']} dB")
    else:
        ok(True, f"real leg SKIP ({out3.get('reason')})")
else:
    ok(True, "real leg SKIP (_anxrofo not present)")

shutil.rmtree(tmp, ignore_errors=True)
print(f"PASS {N}/{N} vocal_rider battery")
