#!/usr/bin/env python3
"""SCALPEL SUITE — natural-language edit asks through the REAL agent, GRADED (CC4 I3).

  scalpel_suite.py [--n K] [--seed S] [--case i,j] [--list]

The first honest measurement of 'surgical edits barely work': each case is a real
producer sentence sent through the real sidecar/agent against a KNOWN 16-bar song;
verify() asserts the musical truth of the proposal (right notes changed, wrong ones
untouched); the scope verdict (surgical.clean) rides the grade. PASS = musically
correct AND in-scope. Results -> eval/scalpel_suite.jsonl + a summary line.

v4 = 50 precision cases — THE CC4 NUMBER (MMAE grid complete + global/exemption, source-swap, nth-selector, truncate, layer, retrograde, fades, motion-pan, zone-fill) (the remaining ~28 of CC4's 50 land as this grows; sloppy
verifiers are worse than fewer cases). Zero mocks — this burns real tokens by design.
"""
import argparse, copy, json, os, random, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
SONG = "_scalpel"
BPM = 120.0


def base_song():
    tr = []
    tr.append({"name": "kick", "source": {"kind": "faust", "id": "kick_punch"}, "gainDb": -4,
               "notes": [{"start": float(b), "len": 0.2, "pitch": 36, "vel": 0.95} for b in range(64)]})
    # 3rd kick deliberately late (case: 'the 3rd kick is late')
    tr[0]["notes"][2]["start"] = 2.07
    # hats stop before the outro (bars 13-16 empty) — fixture bug #3: a fully
    # saturated hat lane made 'copy the drop hats into the outro' a NO-OP by
    # construction (agent did it honestly; empty-diff law refused it; verifier
    # was vacuous on the base). Copy/build-into-outro cases need the space.
    tr.append({"name": "hats", "source": {"kind": "faust", "id": "hat"}, "gainDb": -10,
               "notes": [{"start": b * 0.5, "len": 0.1, "pitch": 42, "vel": 0.5} for b in range(96)]})
    tr.append({"name": "snare", "source": {"kind": "faust", "id": "snare"}, "gainDb": -7,
               "notes": [{"start": b * 4 + o, "len": 0.15, "pitch": 38, "vel": 0.85}
                         for b in range(16) for o in (1.0, 3.0)]})
    tr.append({"name": "bass", "source": {"kind": "faust", "id": "bass_warm"}, "gainDb": -6,
               "notes": [{"start": b * 0.5, "len": 0.45, "pitch": 41 + (b // 8) % 3, "vel": 0.8}
                         for b in range(128)]})
    rng = random.Random(7)
    lead = []
    for b in range(32):
        lead.append({"start": max(0.0, b * 2 + round(rng.uniform(-0.06, 0.06), 3)), "len": 0.6,   # never <0: saves clamp it (fixture bug #2)
                     "pitch": 65 + [0, 3, 5, 7][b % 4], "vel": 0.75})
    tr.append({"name": "lead", "source": {"kind": "faust", "id": "pluck"}, "gainDb": -8, "notes": lead})
    # vox_pad IS a faust voice; 'warmpad' is a SAMPLE KIT — using it as faust/id
    # made the whole song schema-invalid and every scoped editor refused to save
    # (the first live case caught this + the product bug it implies; see stamp 105)
    tr.append({"name": "pad", "source": {"kind": "faust", "id": "vox_pad"}, "gainDb": -12,
               "notes": [{"start": b * 8.0, "len": 7.8, "pitch": p, "vel": 0.5}
                         for b in range(8) for p in (53, 56, 60)]})
    return {"version": 2, "bpm": BPM, "lengthBars": 16, "masterGainDb": 0, "key": "F minor",
            "sections": [{"name": "intro", "startBar": 0}, {"name": "verse", "startBar": 4},
                         {"name": "drop", "startBar": 8}, {"name": "outro", "startBar": 12}],
            "master": [{"id": "fx_truepeak", "params": {"ceiling": -1.2}}], "tracks": tr}


def T(song, name):
    return next(t for t in song["tracks"] if t["name"] == name)


def unchanged(a, b, names):
    return all(json.dumps(T(a, n), sort_keys=True) == json.dumps(T(b, n), sort_keys=True)
               for n in names)


OTHERS = lambda *keep: [n for n in ("kick", "hats", "snare", "bass", "lead", "pad") if n not in keep]

def in_win(n, a, b):
    return a <= n["start"] < b


CASES = [
 ("mute the hats",
  lambda b, p: T(p, "hats").get("muted") is True and unchanged(b, p, OTHERS("hats"))),
 ("make the kick 3 dB louder",
  lambda b, p: abs(T(p, "kick")["gainDb"] - (T(b, "kick")["gainDb"] + 3)) <= 0.75
               and unchanged(b, p, OTHERS("kick"))),
 ("pan the pad a little to the left",
  lambda b, p: -0.5 <= float(T(p, "pad").get("pan", 0)) < -0.02 and unchanged(b, p, OTHERS("pad"))),
 ("delete the snare in the intro",
  lambda b, p: not [n for n in T(p, "snare")["notes"] if in_win(n, 0, 16)]
               and len([n for n in T(p, "snare")["notes"] if n["start"] >= 16])
                   == len([n for n in T(b, "snare")["notes"] if n["start"] >= 16])
               and unchanged(b, p, OTHERS("snare"))),
 ("transpose the lead up an octave in the drop only",
  lambda b, p: all(any(abs(m["start"] - n["start"]) < 0.02 and m["pitch"] == n["pitch"] + 12
                       for m in T(p, "lead")["notes"]) for n in T(b, "lead")["notes"] if in_win(n, 32, 48))
               and all(any(abs(m["start"] - n["start"]) < 0.02 and m["pitch"] == n["pitch"]
                           for m in T(p, "lead")["notes"]) for n in T(b, "lead")["notes"]
                       if not in_win(n, 32, 48))
               and unchanged(b, p, OTHERS("lead"))),
 ("make the hats quieter in the verse only",
  lambda b, p: (sum(n["vel"] for n in T(p, "hats")["notes"] if in_win(n, 16, 32))
                < sum(n["vel"] for n in T(b, "hats")["notes"] if in_win(n, 16, 32)) - 0.5)
               and [round(n["vel"], 3) for n in T(p, "hats")["notes"] if not in_win(n, 16, 32)]
                   == [round(n["vel"], 3) for n in T(b, "hats")["notes"] if not in_win(n, 16, 32)]
               and abs(T(p, "hats")["gainDb"] - T(b, "hats")["gainDb"]) < 0.1
               and unchanged(b, p, OTHERS("hats"))),
 ("quantize the lead tight to the grid",
  lambda b, p: all(min(abs(n["start"] - round(n["start"] * 2) / 2.0),
                       abs(n["start"] - round(n["start"] * 4) / 4.0)) < 0.02
                   for n in T(p, "lead")["notes"]) and unchanged(b, p, OTHERS("lead"))),
 ("humanize the snare a bit",
  lambda b, p: len({round(n["vel"], 3) for n in T(p, "snare")["notes"]}) >= 4
               and any(abs(n["start"] - round(n["start"])) > 0.004 for n in T(p, "snare")["notes"])
               and unchanged(b, p, OTHERS("snare"))),
 ("shorten the bass notes, make them staccato",
  lambda b, p: sum(n["len"] for n in T(p, "bass")["notes"])
               < 0.7 * sum(n["len"] for n in T(b, "bass")["notes"])
               and len(T(p, "bass")["notes"]) == len(T(b, "bass")["notes"])
               and unchanged(b, p, OTHERS("bass"))),
 ("the 3rd kick is late, fix it",
  lambda b, p: abs(sorted(T(p, "kick")["notes"], key=lambda n: n["start"])[2]["start"] - 2.0) < 0.02
               and len(T(p, "kick")["notes"]) == len(T(b, "kick")["notes"])
               and unchanged(b, p, OTHERS("kick"))),
 ("remove the pad from the outro",
  lambda b, p: not [n for n in T(p, "pad")["notes"] if n["start"] >= 48]
               and len([n for n in T(p, "pad")["notes"] if n["start"] < 48])
                   == len([n for n in T(b, "pad")["notes"] if n["start"] < 48])
               and unchanged(b, p, OTHERS("pad"))),
 ("add some reverb to the pad",
  lambda b, p: any("reverb" in str(f.get("id", "")) for f in T(p, "pad").get("fx", []))
               and unchanged(b, p, OTHERS("pad"))),
 ("double the lead an octave up, quieter",
  lambda b, p: (lambda allp: all(any(abs(m["start"] - n["start"]) < 0.03 and m["pitch"] == n["pitch"] + 12
                                     and m["vel"] < n["vel"] for m in allp)
                                 for n in T(b, "lead")["notes"]))(
                   [m for t in p["tracks"] for m in t["notes"] if t["name"] != "pad"])
               and unchanged(b, p, OTHERS("lead"))),
 ("velocity ramp the hats rising through the verse into the drop",
  lambda b, p: (lambda vs: len(vs) > 8 and vs[-1] > vs[0] + 0.15
                and sum(1 for i in range(len(vs) - 1) if vs[i + 1] >= vs[i] - 0.03) > len(vs) * 0.7)(
                   [n["vel"] for n in sorted(T(p, "hats")["notes"], key=lambda x: x["start"])
                    if in_win(n, 16, 32)])
               and unchanged(b, p, OTHERS("hats"))),
 ("delete every other hat in the drop",
  lambda b, p: (lambda dz: abs(len(dz) - 16) <= 2)(
                   [n for n in T(p, "hats")["notes"] if in_win(n, 32, 48)])
               and len([n for n in T(p, "hats")["notes"] if not in_win(n, 32, 48)])
                   == len([n for n in T(b, "hats")["notes"] if not in_win(n, 32, 48)])
               and unchanged(b, p, OTHERS("hats"))),
 ("pitch the last lead note up a third",
  lambda b, p: (lambda lb, lp: lp["pitch"] - lb["pitch"] in (3, 4)
                and abs(lp["start"] - lb["start"]) < 0.02)(
                   sorted(T(b, "lead")["notes"], key=lambda n: n["start"])[-1],
                   sorted(T(p, "lead")["notes"], key=lambda n: n["start"])[-1])
               and all(any(abs(m["start"] - n["start"]) < 0.02 and m["pitch"] == n["pitch"]
                           for m in T(p, "lead")["notes"])
                       for n in sorted(T(b, "lead")["notes"], key=lambda x: x["start"])[:-1])
               and unchanged(b, p, OTHERS("lead"))),
 ("mute the bass and the pad",
  lambda b, p: T(p, "bass").get("muted") is True and T(p, "pad").get("muted") is True
               and unchanged(b, p, OTHERS("bass", "pad"))),
 ("make the pad warmer",
  lambda b, p: (any(f.get("id") == "fx_filter" and float(f.get("params", {}).get("cutoff", 99999)) < 9000
                    for f in T(p, "pad").get("fx", []))
                or any(f.get("id") == "fx_saturate" for f in T(p, "pad").get("fx", []))
                or any(f.get("type") == "eq" and float(f.get("params", {}).get("hiGain", 0)) < -0.5
                       for f in T(p, "pad").get("fx", [])))
               and unchanged(b, p, OTHERS("pad"))),
 ("nudge the whole lead slightly later, about a 32nd",
  lambda b, p: (lambda sb, sp: len(sb) == len(sp)
                and all(0.05 <= (y["start"] - x["start"]) <= 0.30 for x, y in zip(sb, sp)))(
                   sorted(T(b, "lead")["notes"], key=lambda n: n["start"]),
                   sorted(T(p, "lead")["notes"], key=lambda n: n["start"]))
               and unchanged(b, p, OTHERS("lead"))),
 ("strip the intro down to just kick and hats",
  lambda b, p: all(not [n for n in T(p, nm)["notes"] if in_win(n, 0, 16)]
                   for nm in ("snare", "bass", "lead", "pad"))
               and len([n for n in T(p, "kick")["notes"] if in_win(n, 0, 16)]) >= 14
               and len([n for n in T(p, "hats")["notes"] if in_win(n, 0, 16)]) >= 28),
 ("make the drop hit harder",
  lambda b, p: (lambda eb, ep: ep > eb * 1.04)(
                   *[sum(sum(rows[bar] for rows in
                             __import__("energy_curve").energy(s)["tracks"].values())
                         for bar in range(8, 12)) for s in (b, p)])),
 ("open up the filter on the bass",
  # any honest 'open': fx_filter cutoff up, OR the VOICE's own source.cutoff raised /
  # automated upward (the agent chose source.cutoff automation - smarter than my
  # first verifier; corrected f116), OR an eq high-shelf boost
  lambda b, p: ((lambda fp: fp >= 4000)(
      next((float(f.get("params", {}).get("cutoff", 0)) for f in T(p, "bass").get("fx", [])
            if f.get("id") == "fx_filter"), 0))
      or any("cutoff" in a.get("target", "") and len(a.get("points", [])) >= 2
             and a["points"][-1]["v"] > a["points"][0]["v"] + 300
             for a in T(p, "bass").get("automation", []))
      or float((T(p, "bass").get("source", {}).get("params") or {}).get("cutoff", 0)) >= 3000
      or any(f.get("type") == "eq" and float(f.get("params", {}).get("hiGain", 0)) > 1.5
             for f in T(p, "bass").get("fx", [])))
               and unchanged(b, p, OTHERS("bass"))),
 ("bump the tempo to 130",
  lambda b, p: abs(float(p.get("bpm", 0)) - 130.0) < 0.5
               and all(json.dumps(T(p, n)["notes"]) == json.dumps(T(b, n)["notes"])
                       for n in ("kick", "hats", "snare", "bass", "lead", "pad"))),
 ("add some swing to the groove",
  lambda b, p: (isinstance(p.get("swing"), dict) and float(p["swing"].get("amount", .5)) > 0.52)
               or any(0.02 < abs(n["start"] - round(n["start"] * 2) / 2.0) < 0.2
                      for n in T(p, "hats")["notes"])),
 ("add a breakdown section after the drop",
  lambda b, p: any("break" in str(s0.get("name", "")).lower() for s0 in p.get("sections", []))
               and len(p.get("sections", [])) == len(b.get("sections", [])) + 1),
 ("automate a filter sweep on the pad rising into the drop",
  lambda b, p: any(a.get("target", "").startswith("fx[") and "cutoff" in a.get("target", "")
                   and len(a.get("points", [])) >= 2
                   and a["points"][-1]["v"] > a["points"][0]["v"]
                   for a in T(p, "pad").get("automation", [])
                   ) or any("cutoff" in a.get("target", "") and len(a.get("points", [])) >= 2
                            and a["points"][-1]["v"] > a["points"][0]["v"]
                            for a in p.get("automation", []) if isinstance(a, dict))),
 ("add a shaker playing sixteenths",
  lambda b, p: (lambda sh: sh is not None and len(sh["notes"]) >= 48
                and all(abs(n["start"] * 4 - round(n["start"] * 4)) < 0.1 for n in sh["notes"][:16]))(
      next((t for t in p["tracks"] if "shak" in t["name"].lower()), None))
               and unchanged(b, p, ("kick", "hats", "snare", "bass", "lead", "pad"))),
 ("delete the pad track entirely",
  lambda b, p: not any(t["name"] == "pad" for t in p["tracks"])
               and unchanged(b, p, OTHERS("pad"))),
 ("make the lead twice as loud in the drop only",
  # either route is musicianly: velocity 1.5x+ scoped, OR a gainDb automation
  # window (+>=5dB over ~32-48, back to base outside) — the agent chose the
  # automation route with clean edges (verifier correction #5, the #21 lesson)
  lambda b, p: ((all(any(abs(m["start"] - n["start"]) < 0.02 and m["pitch"] == n["pitch"]
                         and m["vel"] > min(1.0, n["vel"] * 1.5) - 0.12
                         for m in T(p, "lead")["notes"])
                     for n in T(b, "lead")["notes"] if in_win(n, 32, 48))
                 and [round(n["vel"], 3) for n in T(p, "lead")["notes"] if not in_win(n, 32, 48)]
                     == [round(n["vel"], 3) for n in T(b, "lead")["notes"] if not in_win(n, 32, 48)])
                or any("gain" in str(a.get("target", "")).lower()
                       and (lambda pts: (lambda inw, outw: inw and outw and min(inw) >= max(outw) + 5.0)(
                            [pt["v"] for pt in pts if 32.5 <= pt.get("beat", -1) <= 47.5] or
                            [pt["v"] for pt in pts if 32 <= pt.get("beat", -1) < 48],
                            [pt["v"] for pt in pts if pt.get("beat", 99) < 31.5 or pt.get("beat", -1) > 48.5]))(
                            a.get("points", []))
                       for a in T(p, "lead").get("automation", [])))
               and unchanged(b, p, OTHERS("lead"))),
 ("delete the snare in the intro and the outro",
  # MULTI-POSITION (MMAE grid): one op, two disjoint windows
  lambda b, p: not [n for n in T(p, "snare")["notes"] if in_win(n, 0, 16) or n["start"] >= 48]
               and len([n for n in T(p, "snare")["notes"] if in_win(n, 16, 48)])
                   == len([n for n in T(b, "snare")["notes"] if in_win(n, 16, 48)])
               and unchanged(b, p, OTHERS("snare"))),
 ("make the hats about half as loud",
  # RELATIVE ATTRIBUTE: 'half as' is arithmetic, not vibes (accept vel OR ~-6dB gain)
  lambda b, p: ((lambda vb, vp: 0.35 <= vp / vb <= 0.65)(
      sum(n["vel"] for n in T(b, "hats")["notes"]),
      max(0.001, sum(n["vel"] for n in T(p, "hats")["notes"])))
      or -7.5 <= T(p, "hats")["gainDb"] - T(b, "hats")["gainDb"] <= -4.5)
               and unchanged(b, p, OTHERS("hats"))),
 ("mute the hats and pan the lead hard left",
  # COMPOUND: two ops, both must land, nothing else
  lambda b, p: T(p, "hats").get("muted") is True
               and float(T(p, "lead").get("pan", 0)) <= -0.7
               and unchanged(b, p, OTHERS("hats", "lead"))),
 ("copy the drop hats into the outro",
  # COPY op: outro (48..64) gains the drop's hat pattern (mod-16 aligned)
  lambda b, p: (lambda drop, outro: len(outro) >= len(drop) - 2 and
                all(any(abs((o["start"] - 48.0) % 16.0 - (d["start"] - 32.0) % 16.0) < 0.03
                        for o in outro) for d in drop[:12]))(
      [n for n in T(b, "hats")["notes"] if in_win(n, 32, 48)],
      [n for n in T(p, "hats")["notes"] if n["start"] >= 48])
               and unchanged(b, p, OTHERS("hats"))),
 ("make everything except the bass quieter by 3 db",
  # NEGATION SCOPE: 5 tracks move together, ONE stays
  lambda b, p: all(abs((T(p, nm)["gainDb"] - T(b, nm)["gainDb"]) + 3.0) <= 0.75
                   for nm in ("kick", "hats", "snare", "lead", "pad"))
               and abs(T(p, "bass")["gainDb"] - T(b, "bass")["gainDb"]) < 0.1
               and all(json.dumps(T(p, nm)["notes"]) == json.dumps(T(b, nm)["notes"])
                       for nm in ("kick", "hats", "snare", "bass", "lead", "pad"))),
 ("double the tempo feel: halftime the drums",
  # FEEL op: kick+snare density halves (or spacing doubles) while bars stay
  lambda b, p: (lambda kb, kp: 0.4 <= kp / kb <= 0.6)(
      len(T(b, "kick")["notes"]), max(1, len(T(p, "kick")["notes"])))
               and (lambda sb, sp: 0.35 <= sp / sb <= 0.65)(
      len(T(b, "snare")["notes"]), max(1, len(T(p, "snare")["notes"])))
               and unchanged(b, p, ("bass", "lead", "pad"))),
 ("give the lead some space with a send to a reverb bus",
  # ROUTING op: bus exists + lead sends to it (the pro paradigm, not insert-only)
  lambda b, p: any("verb" in str(bu.get("id", "")).lower() or
                   any("reverb" in str(f.get("id", "")) for f in bu.get("fx", []))
                   for bu in p.get("buses", []))
               and any(sn.get("bus") for sn in T(p, "lead").get("sends", []))
               and unchanged(b, p, OTHERS("lead"))),
 ("tighten the bass timing to the kick",
  # CROSS-TRACK reference: bass onsets land within 15ms of kick grid (0.03b @126)
  lambda b, p: (lambda notes: sum(1 for n in notes
                                  if min(abs(n["start"] - k) for k in
                                         [x["start"] for x in T(p, "kick")["notes"]] + [1e9])
                                  < 0.04 or abs(n["start"] - round(n["start"] * 2) / 2) < 0.02)
                >= len(notes) * 0.9)(T(p, "bass")["notes"])
               and len(T(p, "bass")["notes"]) == len(T(b, "bass")["notes"])
               and unchanged(b, p, OTHERS("bass"))),
 ("transpose everything down two semitones",
  # GLOBAL + IMPLICIT EXEMPTION: melodic moves, drums are trigger-pitches (stay)
  lambda b, p: all(all(any(abs(m["start"]-n["start"])<0.02 and m["pitch"]==n["pitch"]-2
                           for m in T(p,nm)["notes"]) for n in T(b,nm)["notes"])
                   for nm in ("bass","lead","pad"))
               and all(json.dumps(T(p,nm)["notes"])==json.dumps(T(b,nm)["notes"])
                       for nm in ("kick","hats","snare"))),
 ("swap the lead sound for an epiano",
  # rhodes IS an epiano (correction #6 — the agent out-idiomed the literal id)
  lambda b, p: any(k in str(T(p,"lead").get("source",{}).get("id","")).lower()
                   for k in ("piano","rhodes","keys"))
               and sorted((round(n["start"],3),n["pitch"],round(n.get("vel",.8),3),round(n.get("len",.25),3))
                          for n in T(p,"lead")["notes"])
                   == sorted((round(n["start"],3),n["pitch"],round(n.get("vel",.8),3),round(n.get("len",.25),3))
                          for n in T(b,"lead")["notes"])
               and unchanged(b, p, OTHERS("lead"))),
 ("flatten the kick velocities, make it robotic",
  lambda b, p: len({round(n["vel"],3) for n in T(p,"kick")["notes"]}) == 1
               and len(T(p,"kick")["notes"]) == len(T(b,"kick")["notes"])
               and unchanged(b, p, OTHERS("kick"))),
 ("widen the pad but keep the bass mono",
  # COMPOUND + MONO-LAW COMPLIANCE in one ask
  lambda b, p: any(f.get("id")=="fx_widen" and float(f.get("params",{}).get("width",1))>1.15
                   for f in T(p,"pad").get("fx",[]))
               and not any(f.get("id")=="fx_widen" for f in T(p,"bass").get("fx",[]))
               and abs(float(T(p,"bass").get("pan",0))) < 0.05
               and unchanged(b, p, OTHERS("pad","bass"))),
 ("drop the bass an octave in the intro only",
  lambda b, p: all(any(abs(m["start"]-n["start"])<0.02 and m["pitch"]==n["pitch"]-12
                       for m in T(p,"bass")["notes"]) for n in T(b,"bass")["notes"] if in_win(n,0,16))
               and all(any(abs(m["start"]-n["start"])<0.02 and m["pitch"]==n["pitch"]
                           for m in T(p,"bass")["notes"]) for n in T(b,"bass")["notes"] if not in_win(n,0,16))
               and unchanged(b, p, OTHERS("bass"))),
 ("accent every fourth hat",
  # NTH-SELECTOR: every 4th noticeably louder, the rest untouched
  lambda b, p: (lambda sb, sp: len(sb)==len(sp)
                and sum(1 for i,(x,y) in enumerate(zip(sb,sp)) if i%4==0 and y["vel"]>x["vel"]+0.08)
                    >= len(sb)//4 - 2
                and all(abs(y["vel"]-x["vel"])<0.03 for i,(x,y) in enumerate(zip(sb,sp)) if i%4!=0))(
      sorted(T(b,"hats")["notes"],key=lambda n:n["start"]),
      sorted(T(p,"hats")["notes"],key=lambda n:n["start"]))
               and unchanged(b, p, OTHERS("hats"))),
 ("delete everything after bar 12",
  lambda b, p: all(not [n for n in T(p,nm)["notes"] if n["start"]>=48]
                   for nm in ("kick","hats","snare","bass","lead","pad"))
               and all(len([n for n in T(p,nm)["notes"] if n["start"]<48])
                       == len([n for n in T(b,nm)["notes"] if n["start"]<48])
                       for nm in ("kick","hats","snare","bass","lead","pad"))),
 ("layer a clap with the snare",
  lambda b, p: (lambda cl: cl is not None and
                (lambda cs, ss: len(cs&ss) >= len(ss)-2)(
                    {round(n["start"],2) for n in cl["notes"]},
                    {round(n["start"],2) for n in T(b,"snare")["notes"]}))(
      next((t for t in p["tracks"] if "clap" in t["name"].lower()), None))
               and unchanged(b, p, ("kick","hats","snare","bass","lead","pad"))),
 ("reverse the last four lead notes",
  lambda b, p: (lambda lb, lp: [n["pitch"] for n in lp[-4:]] == [n["pitch"] for n in lb[-4:]][::-1]
                and [n["pitch"] for n in lp[:-4]] == [n["pitch"] for n in lb[:-4]])(
      sorted(T(b,"lead")["notes"],key=lambda n:n["start"]),
      sorted(T(p,"lead")["notes"],key=lambda n:n["start"]))
               and unchanged(b, p, OTHERS("lead"))),
 ("fade the pad in over the intro",
  lambda b, p: any("gain" in str(a.get("target","")).lower() and len(a.get("points",[]))>=2
                   and a["points"][0]["v"] < a["points"][-1]["v"] - 6
                   and a["points"][0].get("beat",99) <= 1
                   for a in T(p,"pad").get("automation",[]))
               and unchanged(b, p, OTHERS("pad"))),
 ("make the hats travel left to right across each bar",
  lambda b, p: any("pan" in str(a.get("target","")).lower() and len(a.get("points",[]))>=2
                   and (lambda vs: min(vs)<-0.2 and max(vs)>0.2)([pt["v"] for pt in a["points"]])
                   for a in T(p,"hats").get("automation",[]))
               and unchanged(b, p, OTHERS("hats"))),
 ("double-time the hats in the bar before the drop",
  # ZONE FILL: bar 8 (beats 28-32) doubles density; elsewhere untouched
  lambda b, p: (lambda zb, zp: len(zp) >= len(zb)*2 - 1)(
      [n for n in T(b,"hats")["notes"] if 28<=n["start"]<32],
      [n for n in T(p,"hats")["notes"] if 28<=n["start"]<32])
               and len([n for n in T(p,"hats")["notes"] if not 28<=n["start"]<32])
                   == len([n for n in T(b,"hats")["notes"] if not 28<=n["start"]<32])
               and unchanged(b, p, OTHERS("hats"))),
 ("swing the hats a little",
  lambda b, p: (isinstance(p.get("swing"), dict)
                and p["swing"].get("grid") in ("8th", "8")
                and float(p["swing"].get("amount", 0.5)) > 0.52)
               or (lambda off: len(off) >= 8 and all(0.02 < d < 0.2 for d in off))(
                   # displacement from the 8TH grid (verifier bug #7: measuring from
                   # whole beats missed a correct 0.5->0.56 swing)
                   [round((n["start"] % 0.5) if (n["start"] % 0.5) < 0.25
                          else 0.5 - (n["start"] % 0.5), 3)
                    for n in T(p, "hats")["notes"]
                    if 0.3 < (n["start"] % 1.0) < 0.7 and (n["start"] % 0.5) > 1e-6])),
]


class Bus:
    def __init__(self, ipc):
        self.ipc, self.rid = ipc, 500

    def events(self):
        try:
            return [json.loads(l) for l in open(os.path.join(self.ipc, "events.jsonl")) if l.strip()]
        except FileNotFoundError:
            return []

    def send(self, req):
        self.rid += 1
        with open(os.path.join(self.ipc, "request.json.tmp"), "w") as f:
            f.write(json.dumps(dict(req, id=self.rid)))
        os.replace(os.path.join(self.ipc, "request.json.tmp"), os.path.join(self.ipc, "request.json"))
        return self.rid

    def wait(self, rid, timeout=420):
        t0 = time.time()
        prop_ev = None
        while time.time() - t0 < timeout:
            for e in self.events():
                if e.get("id") == rid:
                    if e.get("kind") == "proposal":
                        prop_ev = e
                    if e.get("kind") == "done":
                        return prop_ev, e, time.time() - t0
                    if e.get("kind") == "error" and prop_ev is None and "no changes" in str(e.get("text", "")):
                        return None, e, time.time() - t0
            time.sleep(0.4)
        return prop_ev, None, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--case", default="")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for i, (ask, _) in enumerate(CASES):
            print(f"{i:2d}  {ask}")
        return
    idxs = list(range(len(CASES)))
    if a.case:
        idxs = [int(x) for x in a.case.split(",")]
    elif a.n:
        random.Random(a.seed).shuffle(idxs)
        idxs = sorted(idxs[: a.n])
    sys.path.insert(0, os.path.join(ROOT, "tools"))

    # ATOMIC RUN-LOCK (f128): two lessons paid in blood — a foreign cleanup killed a
    # run's sidecar via ls-newest, and a check-then-launch guard raced a dying runner.
    # O_EXCL lock with pid; stale (dead pid) locks are broken with a note.
    lockp = os.path.join(ROOT, "eval", ".scalpel_running")
    os.makedirs(os.path.dirname(lockp), exist_ok=True)
    try:
        fd = os.open(lockp, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode()); os.close(fd)
    except FileExistsError:
        try:
            other = int(open(lockp).read().strip())
            os.kill(other, 0)
            raise SystemExit(f"another suite run is live (pid {other}) — refusing to double-run")
        except (ProcessLookupError, ValueError):
            print(f"[suite] breaking STALE lock (dead pid)")
            os.remove(lockp)
            fd = os.open(lockp, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode()); os.close(fd)
    ipc = tempfile.mkdtemp(prefix="scalpel_ipc_")
    env = dict(os.environ, SOTADAW_IPC=ipc, SOTADAW_NO_UPLINK="1")
    side = subprocess.Popen([os.path.join(ROOT, ".venv", "bin", "python"),
                             os.path.join(ROOT, "agent", "sidecar.py")],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bus = Bus(ipc)
    time.sleep(3)
    os.makedirs(os.path.join(ROOT, "eval"), exist_ok=True)
    out = open(os.path.join(ROOT, "eval", "scalpel_suite.jsonl"), "a")
    results = []
    try:
        for i in idxs:
            ask, verify = CASES[i]
            base = base_song()
            # THE FIXTURE ISOLATION LAW (2026-07-12, the case05/case10 kill):
            # cases 5+10's edits were verifiably PERFECT — they failed because a
            # TIMED-OUT earlier case's run kept composing on the shared song
            # name and re-minted props across the case boundary (the 420s
            # "no proposal" row is the smoking gun: hats carried a prior case's
            # +32 copied notes). Unique per-case names make any late survivor's
            # writes inert by construction; the base rewrite stops being a race.
            song_i = f"{SONG}{os.getpid() % 10000:04d}x{i:02d}"
            json.dump(base, open(os.path.join(SONGS, f"{song_i}.json"), "w"), indent=1)
            for f in (f"_prop_{song_i}.json", f"_prop_{song_i}.wav", f"_prop_{song_i}.ghost.json"):
                pth = os.path.join(SONGS, f)
                os.path.exists(pth) and os.remove(pth)
            rid = bus.send({"type": "prompt", "text": ask, "song": song_i})
            prop_ev, done, dt = bus.wait(rid)
            row = {"t": round(time.time(), 1), "i": i, "ask": ask, "secs": round(dt, 1)}
            pp = os.path.join(SONGS, f"_prop_{song_i}.json")
            if prop_ev is None or not os.path.exists(pp):
                row.update(ok=False, why="no proposal")
            else:
                try:
                    prop = json.load(open(pp))
                    ok = bool(verify(base, prop))
                    srep = prop_ev.get("surgical") or {}
                    row.update(ok=ok, clean=srep.get("clean"),
                               full_write=srep.get("full_write"),
                               why="" if ok else "verify failed")
                    if not ok:   # keep the evidence: failing takes are triage gold
                        fd = os.path.join(ROOT, "eval", "scalpel_fails")
                        os.makedirs(fd, exist_ok=True)
                        shutil.copy(pp, os.path.join(fd, f"case{i:02d}.json"))
                except Exception as e:
                    row.update(ok=False, why=f"verify crashed: {e}")
            results.append(row)
            out.write(json.dumps(row) + "\n")
            out.flush()
            print(f"  [{'PASS' if row['ok'] else 'FAIL'}] #{i:2d} {ask!r} "
                  f"({row['secs']}s{', clean' if row.get('clean') else ''}"
                  f"{', FULL-WRITE' if row.get('full_write') else ''})"
                  + ("" if row["ok"] else f" — {row['why']}"))
    finally:
        try:
            side.send_signal(signal.SIGTERM); side.wait(timeout=5)
        except Exception:
            side.kill()
        shutil.rmtree(ipc, ignore_errors=True)      # OWN ipc only — never ls-newest
        try:
            os.remove(os.path.join(ROOT, "eval", ".scalpel_running"))
        except FileNotFoundError:
            pass
        for f in os.listdir(SONGS):
            if f.startswith(SONG) or f.startswith(f"_prop_{SONG}"):
                os.remove(os.path.join(SONGS, f))
    n_ok = sum(1 for r in results if r["ok"])
    n_clean = sum(1 for r in results if r["ok"] and r.get("clean"))
    med = sorted(r["secs"] for r in results)[len(results) // 2] if results else 0
    print(f"\n== SCALPEL SUITE: {n_ok}/{len(results)} musically correct "
          f"({n_clean} also scope-clean) | median {med:.0f}s ==")


if __name__ == "__main__":
    main()
