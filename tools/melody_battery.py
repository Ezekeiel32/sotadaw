#!/usr/bin/env python3
"""THE MELODIC MIND battery (wave-12 backlog fold; pure, zero renders).

Proves: LBDM segmentation (exact math + caps), Temperley plausibility
discriminates, motif economy separates loop/development/noise, hook score
prefers hooks, BANDS court flags off-band lanes + verse/chorus sameness,
heal folds wanderers, tessitura clamp centers lines, witness/exempt laws,
melody-features bridge is skip-safe, determinism.
"""
import copy
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import melody_court as M  # noqa: E402

FAILS = 0


def check(name, cond, detail=""):
    global FAILS
    tag = "ok" if cond else "RED"
    print(f"[{tag}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS += 1


def mk(pitches, step=0.5, start=0.0, vel=0.8, lens=None):
    out = []
    t = start
    for i, p in enumerate(pitches):
        ln = (lens[i] if lens else step * 0.9)
        out.append({"start": round(t, 4), "pitch": int(p), "len": ln, "vel": vel})
        t += step
    return out


# ---------------------------------------------------------------- 1. LBDM
line = mk([60, 62, 64, 65, 67, 65, 64, 62], step=0.5)          # phrase 1
line += mk([72, 74, 76, 77, 79, 77, 76, 74], step=0.5, start=6.0)  # gap + leap
bounds = M.lbdm_boundaries(line)
check("lbdm finds the gap+leap boundary", 7 in bounds or 6 in bounds,
      f"bounds={bounds}")

a = M.lbdm_strengths(mk([60, 72, 60, 62, 63, 62, 61, 62, 61, 62], step=0.5))
b = M.lbdm_strengths(mk([60, 84, 60, 62, 63, 62, 61, 62, 61, 62], step=0.5))
check("lbdm octave cap (12 == 24 leap)", abs(a[0] - b[0]) < 1e-9,
      f"{a[0]} vs {b[0]}")

# ------------------------------------------------------------ 2. Temperley
key = M.T.parse_key("C major")
smooth = mk([60, 62, 64, 65, 67, 65, 64, 62, 60, 62, 64, 62], step=0.5)
rng = random.Random(7)
wild = mk([rng.choice(range(40, 96)) for _ in range(12)], step=0.5)
_, s_ok = M.temperley_logp(smooth, key)
_, s_bad = M.temperley_logp(wild, key)
check("temperley: stepwise diatonic > random leaps", s_ok > s_bad + 1.0,
      f"{s_ok:.2f} vs {s_bad:.2f}")

spiked = mk([60, 62, 64, 62, 60, 62, 83, 62, 60, 62, 64, 62, 60, 62], step=0.5)
outs = M.temperley_outliers(spiked, key)
check("temperley outlier: planted spike caught",
      any(o["pitch"] == 83 for o in outs), f"outs={outs}")

# --------------------------------------------------------- 3. motif economy
motif = [60, 63, 65, 67, 65, 63, 60, 60]
loop = mk(motif * 6, step=0.5)
rep_loop = M.motif_economy(loop)["repetition"]
noise = mk([rng.choice(range(55, 80)) for _ in range(48)],
           step=0.5, lens=[rng.choice([0.2, 0.4, 0.9]) for _ in range(48)])
rep_noise = M.motif_economy(noise)["repetition"]
check("motif economy: loop >> noise", rep_loop > 0.6 > rep_noise,
      f"loop={rep_loop} noise={rep_noise}")

# ------------------------------------------------------------ 4. hook score
hook = mk(motif * 4, step=0.5)
wander = mk([60 + ((i * 7) % 23) - 11 for i in range(32)], step=0.5)
check("hook score: hook > wander", M.hook_score(hook) > M.hook_score(wander),
      f"{M.hook_score(hook)} vs {M.hook_score(wander)}")

# ------------------------------------------------------------- 5. the court
def song_with(notes, name="lead", genre_len=16, sections=None, extra=None):
    s = {"bpm": 120, "key": "C major", "lengthBars": genre_len,
         "tracks": [{"name": name, "source": {"kind": "faust", "id": "pluck"},
                     "notes": notes}]}
    if sections:
        s["sections"] = sections
    if extra:
        s["tracks"] += extra
    return s

leapfest = mk([rng.choice([36, 48, 60, 72, 84, 96]) for _ in range(40)], step=0.5)
v = M.court_melody(song_with(leapfest), "pop")
check("court flags a pop leap-fest (>=2 dims off)",
      not v["ok"] and any(f["kind"] == "off_band" for f in v["flags"]),
      json.dumps(v.get("flags"))[:200])

tame = mk((motif + [62, 60, 58, 60]) * 3, step=0.5)
v2 = M.court_melody(song_with(tame), "pop")
check("court passes a tame pop hook", v2["ok"], json.dumps(v2)[:300])

v3 = M.court_melody(song_with(leapfest, name="vocals_sketch"), "pop")
check("witness law: _sketch lanes exempt", v3.get("skipped") == "no melodic lanes")

v4 = M.court_melody(song_with(leapfest), "ambient")
check("exempt genre stands down", v4["ok"] and "exempt" in str(v4.get("skipped")))

# --------------------------------------------- 6. verse/chorus differentiation
sections = [{"name": "verse", "startBar": 0}, {"name": "chorus", "startBar": 4},
            {"name": "verse2", "startBar": 8}, {"name": "chorus2", "startBar": 12}]
same = mk(motif * 2, step=0.5) + mk(motif * 2, step=0.5, start=16.0) + \
    mk(motif * 2, step=0.5, start=32.0) + mk(motif * 2, step=0.5, start=48.0)
vs = M.court_melody(song_with(same, sections=sections), "pop")
check("chorus_indistinct flagged when chorus == verse",
      any(f["kind"] == "chorus_indistinct" for f in vs.get("flags", [])),
      json.dumps(vs.get("flags"))[:200])

lifted = mk(motif * 2, step=0.5) + mk([p + 12 for p in motif] * 2, step=0.5, start=16.0) + \
    mk(motif * 2, step=0.5, start=32.0) + mk([p + 12 for p in motif] * 2, step=0.5, start=48.0)
vl = M.court_melody(song_with(lifted, sections=sections), "pop")
check("lifted chorus passes",
      not any(f["kind"] == "chorus_indistinct" for f in vl.get("flags", [])))

# ----------------------------------------------------------------- 7. heal
base = [60, 62, 64, 62] * 10
for idx, spike in ((7, 88), (17, 39), (27, 90), (33, 38)):
    base[idx] = spike
spike_song = song_with(mk(base, step=0.5))
vv = M.court_melody(spike_song, "pop")
check("wanderer flag fires on 4 planted spikes",
      any(f["kind"] == "wanderer" for f in vv.get("flags", [])),
      json.dumps(vv.get("flags"))[:200])
before = len(M.temperley_outliers(spike_song["tracks"][0]["notes"], key))
edits = M.heal_melody(spike_song, "pop", vv)
after = len(M.temperley_outliers(spike_song["tracks"][0]["notes"], key))
check("heal folds wanderers (ledger + fewer outliers)",
      bool(edits) and after < before, f"edits={len(edits)} {before}->{after}")
check("heal preserves pitch class (octave folds only)",
      all(e["kind"] != "octave_fold"
          or (M.T.name_to_midi(e["old"]) - M.T.name_to_midi(e["new"])) % 12 == 0
          for e in edits))

# ------------------------------------------------------------ 8. tessitura
low_line = mk([46, 48, 50, 48, 46, 44, 48, 50], step=0.5)
edits = M.clamp_tessitura(low_line, "female")
ps = [n["pitch"] for n in low_line]
check("tessitura: line transposed into female window",
      any(e["kind"] == "transpose" for e in edits) and 55 <= sum(ps) / len(ps) <= 74,
      f"mean={sum(ps)/len(ps):.1f} edits={edits[:2]}")

wide = mk([40, 84, 60, 62, 60, 84, 40, 62], step=0.5)
M.clamp_tessitura(wide, "female", ambitus_cap=19)
ps = [n["pitch"] for n in wide]
check("tessitura: ambitus cap enforced", max(ps) - min(ps) <= 19,
      f"span={max(ps)-min(ps)}")

# ------------------------------------------------- 9. mf bridge + determinism
try:
    feats = M.mf_features(tame, 120.0)
    check("melody-features bridge skip-safe", feats is None or isinstance(feats, dict),
          str(feats)[:120])
except Exception as e:
    check("melody-features bridge skip-safe", False, repr(e))

d1 = M.court_melody(song_with(copy.deepcopy(leapfest)), "pop")
d2 = M.court_melody(song_with(copy.deepcopy(leapfest)), "pop")
check("determinism", json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True))

print(f"\nmelody_battery: {'ALL GREEN' if not FAILS else f'{FAILS} RED'}")
sys.exit(1 if FAILS else 0)
