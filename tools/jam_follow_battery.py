#!/usr/bin/env python3
"""B3 THE FOLLOW battery — the band member plays WITH the human (docs/THE_BAND_SEAT.md).

Pure + zero-render proofs over jam.py's follow kernel:
  - human_context: density/energy/pitch-class/register math, window law, solo mode
  - brain(+human): the energy target BENDS toward the human (follow weight law),
    busy humans get SPACE (melodic rungs comp out, percussion still builds — sticky,
    not oscillating), silent human == legacy behavior byte-for-byte (additive law)
  - build_phrase_song(+pc_mask): melodic rungs SNAP to the human's harmony
    (nearest step, max +-2; farther notes keep pitch; drums never touched)

Usage: python3 tools/jam_follow_battery.py
"""
import glob
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import jam

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)


def N(start, pitch, vel=0.8, ln=0.25):
    return {"start": start, "len": ln, "pitch": pitch, "vel": vel}


def main():
    # ---------- human_context ----------
    ok(jam.human_context([]) is None, "silence -> None (solo mode)")
    sparse = [N(b * 4.0, 48) for b in range(4)]              # one note a bar
    dense = [N(i * 0.25, 60 + (i % 3), 0.95) for i in range(64)]   # 16ths, 4 bars
    hc_sp = jam.human_context(sparse, now_beat=16.0)
    hc_dn = jam.human_context(dense, now_beat=16.0)
    ok(hc_sp is not None and hc_sp["density"] < 0.25, f"sparse take reads sparse ({hc_sp})")
    ok(hc_dn is not None and hc_dn["density"] >= 0.9, f"16ths read dense ({hc_dn})")
    ok(hc_dn["energy"] > hc_sp["energy"], "hot dense take carries more energy")
    old = [N(0.0, 60)]                                        # outside a 4-bar window at beat 32
    ok(jam.human_context(old, now_beat=32.0) is None, "window law: old notes don't count")
    early = [N(i * 0.25, 60, 0.9) for i in range(16)]         # 16ths, but only ONE bar played yet
    hc_e = jam.human_context(early, now_beat=4.0)
    ok(hc_e is not None and hc_e["density"] >= 0.9,
       f"opening-bar law: wall-to-wall 16ths read dense from the first bar ({hc_e})")
    cmin = [N(i * 1.0, p, 0.9) for i, p in enumerate((60, 63, 67, 72, 63, 67))]
    hc_c = jam.human_context(cmin, now_beat=8.0)
    ok(hc_c["pitch_classes"] == [0, 3, 7], f"C-minor take -> pcs [0,3,7] (got {hc_c['pitch_classes']})")
    ok(59.0 < hc_c["register"] < 68.0, "register = mean pitch")
    soft = jam.human_context([N(0, 60, 0.2), N(1, 60, 0.2)], now_beat=4.0)
    loud = jam.human_context([N(0, 60, 1.0), N(1, 60, 1.0)], now_beat=4.0)
    ok(loud["energy"] > soft["energy"] + 0.3, "velocity drives energy")
    ok(jam.human_context(cmin, now_beat=8.0) == hc_c, "deterministic")

    # ---------- brain + human: the target bends ----------
    st = {"active": ["kick", "bass", "hat"], "available": ["hat", "color", "clap", "lead"],
          "level": 0.5, "bright": 0.5, "phrase": 1}
    mv_solo, _ = jam.brain(0.5, 0.5, dict(st))                # in the pocket alone
    ok(mv_solo == "HOLD", f"solo pocket holds (got {mv_solo})")
    hot = {"density": 0.3, "energy": 1.0, "pitch_classes": [0], "register": 60}
    mv_hot, s_hot = jam.brain(0.5, 0.5, dict(st), human=hot)
    ok(mv_hot.startswith("BUILD"), f"hot human bends the target up -> BUILD (got {mv_hot})")
    cold = {"density": 0.05, "energy": 0.0, "pitch_classes": [0], "register": 60}
    mv_cold, _ = jam.brain(0.5, 0.5, dict(st), human=cold)
    ok(mv_cold.startswith("EASE"), f"quiet human bends it down -> EASE (got {mv_cold})")
    # follow weight law: w=0 ignores the human entirely; w=1 is pure follow
    mv_w0, _ = jam.brain(0.5, 0.5, dict(st, follow=0.0), human=hot)
    ok(mv_w0 == "HOLD", f"follow=0 -> the human does not move the band (got {mv_w0})")
    mv_w1, _ = jam.brain(1.0, 0.2, dict(st, follow=1.0), human=hot)
    ok(mv_w1 in ("HOLD", "EVOLVE"), f"follow=1 + measured==human energy -> pocket (got {mv_w1})")

    # ---------- SPACE: comp behind a busy soloist ----------
    busy = {"density": 0.9, "energy": 0.6, "pitch_classes": [0, 3, 7], "register": 62}
    st_lead = dict(st, active=["kick", "bass", "hat", "lead"], phrase=0)
    mv_sp, s_sp = jam.brain(0.6, 0.6, st_lead, human=busy)
    ok(mv_sp == "SPACE -lead" and "lead" not in s_sp["active"],
       f"busy human -> the lead comps out (got {mv_sp})")
    ok("kick" in s_sp["active"] and "bass" in s_sp["active"], "foundation never drops")
    st_perc = dict(st, active=["kick", "bass", "hat"], phrase=0)
    mv_ev, _ = jam.brain(0.6, 0.6, dict(st_perc), human=busy)
    ok(mv_ev in ("EVOLVE", "HOLD"), f"busy + nothing to yield -> normal pocket (got {mv_ev})")
    # busy BUILD skips melodic rungs; percussion still carries the energy
    mv_bd, s_bd = jam.brain(0.2, 0.8, dict(st_perc), human=dict(busy, energy=0.9))
    ok(mv_bd == "BUILD +clap" and "color" not in s_bd["active"],
       f"busy build skips lead/color -> +clap (got {mv_bd})")
    mv_free, s_free = jam.brain(0.2, 0.8, dict(st_perc))
    ok(mv_free == "BUILD +color", f"solo build takes the melodic rung (got {mv_free})")

    # ---------- legacy law: no human == the old band, additively ----------
    seq = [(0.1, 0.6), (0.4, 0.6), (0.62, 0.6), (0.9, 0.5), (0.55, 0.6), (0.58, 0.6)]
    s = {"active": ["kick", "bass"], "available": ["hat", "color", "clap"],
         "level": 0.2, "bright": 0.3, "phrase": 0}
    moves = []
    for i, (m, t) in enumerate(seq):
        mv, s = jam.brain(m, t, dict(s, phrase=i))
        moves.append(mv)
    ok(moves == ["BUILD +hat", "BUILD +color", "EVOLVE", "EASE -color", "EVOLVE", "HOLD"],
       f"3-arg legacy trajectory reproduced exactly (got {moves})")

    # ---------- THE EVOLVE LAW: the pocket breathes, never photocopies ----------
    eb = {"tracks": [
        {"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
         "notes": [N(b, 36, 0.2, 1.0) for b in range(4)]},
        {"name": "hat", "source": {"kind": "faust", "id": "hat"},
         "notes": [N(i * 0.5, 42, 0.8, 0.2) for i in range(8)]},
        {"name": "lead", "source": {"kind": "faust", "id": "flute_lead"},
         "notes": [N(0, 60), N(2, 63)]},
    ]}
    act = ["kick", "hat", "lead"]
    plain = jam.build_phrase_song(eb, act, 0.5, 120, "C")
    thin = jam.build_phrase_song(eb, act, 0.5, 120, "C", evolve=3)   # op 0
    ghost = jam.build_phrase_song(eb, act, 0.5, 120, "C", evolve=1)  # op 1
    fill = jam.build_phrase_song(eb, act, 0.5, 120, "C", evolve=2)   # op 2
    trk = lambda s, nm: next(t for t in s["tracks"] if t["name"] == nm)
    ok(json.dumps(trk(thin, "kick")) == json.dumps(trk(plain, "kick"))
       and json.dumps(trk(thin, "lead")) == json.dumps(trk(plain, "lead")),
       "EVOLVE never touches foundation or melody")
    ok(len(trk(thin, "hat")["notes"]) == 6, f"THIN breathes out every 4th "
       f"({len(trk(thin, 'hat')['notes'])}/8)")
    gv = [n["vel"] for n in trk(ghost, "hat")["notes"]]
    ok(len(gv) == 8 and gv[1] < 0.5 < gv[0], f"GHOST softens alternates ({gv[:4]})")
    ok(len(trk(fill, "hat")["notes"]) == 9, "FILL adds exactly one pickup")
    ok(json.dumps(jam.build_phrase_song(eb, act, 0.5, 120, "C", evolve=1))
       == json.dumps(ghost), "EVOLVE deterministic (seed law)")
    ok(json.dumps(jam.build_phrase_song(eb, ["kick", "lead"], 0.5, 120, "C", evolve=1))
       == json.dumps(jam.build_phrase_song(eb, ["kick", "lead"], 0.5, 120, "C")),
       "no percussion rung active -> EVOLVE is a no-op (foundation sacred)")
    ok(len({json.dumps(trk(s, "hat")["notes"]) for s in (plain, thin, ghost, fill)}) == 4,
       "three ops + plain = four DISTINCT pocket patterns")

    # ---------- THE GROOVE FOLLOW: the human's feel, measured + stamped ----------
    straight = [N(i * 0.25, 60, 0.9) for i in range(32)]
    hs = jam.human_context(straight, now_beat=8.0)
    ok(hs["swing"]["amount"] == 0.5, f"quantized take reads STRAIGHT ({hs['swing']})")
    sw8 = []
    for b in range(8):
        sw8 += [N(b * 1.0, 60, 0.9), N(b * 1.0 + 0.62, 60, 0.85)]
    h8 = jam.human_context(sw8, now_beat=8.0)
    ok(h8["swing"]["grid"] == "8th" and abs(h8["swing"]["amount"] - 0.62) < 0.02,
       f"swung 8ths read as 8th feel ~0.62 ({h8['swing']})")
    sw16 = []
    for b in range(8):
        for half in (0.0, 0.5):
            sw16 += [N(b + half, 60, 0.9), N(b + half + 0.31, 60, 0.85)]
    h16 = jam.human_context(sw16, now_beat=8.0)
    ok(h16["swing"]["grid"] == "16th" and abs(h16["swing"]["amount"] - 0.62) < 0.02,
       f"swung 16ths read as 16th feel ~0.62 ({h16['swing']})")
    ok(jam.human_context([N(0.62, 60)], now_beat=4.0)["swing"]["amount"] == 0.5,
       "insufficient evidence -> straight (never hallucinate a feel)")
    sw_song = jam.build_phrase_song(eb, act, 0.5, 120, "C",
                                    swing={"grid": "8th", "amount": 0.62})
    ok(sw_song.get("swing") == {"grid": "8th", "amount": 0.62},
       f"the phrase carries the human's feel ({sw_song.get('swing')})")
    ok("swing" not in jam.build_phrase_song(eb, act, 0.5, 120, "C",
                                            swing={"grid": "8th", "amount": 0.5}),
       "straight never stamps (solo contract byte-intact)")
    ok("swing" not in jam.build_phrase_song(eb, act, 0.5, 120, "C"), "no human, no stamp")
    ok(jam.build_phrase_song(eb, act, 0.5, 120, "C",
                             swing={"grid": "8th", "amount": 0.9})["swing"]["amount"] == 0.7,
       "feel clamped at 0.7 (never lurch)")

    # ---------- THE HARMONIC JOURNEY: the harmony MOVES, the groove stays ----------
    ok([jam.journey_offset(q) for q in range(10)]
       == [0, 0, -4, -4, 3, 3, -2, -2, 0, 0],
       "journey degrees deterministic (i i VI VI III III VII VII, cycling)")
    ok(jam.journey_offset(2, "C major") == -5 and jam.journey_offset(4, "C major") == -3
       and jam.journey_offset(2, "A minor") == -4,
       "MODE LAW: major DNA walks I V vi IV, minor walks i VI III VII")
    ebj = {"tracks": [
        {"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
         "notes": [N(0, 36), N(1, 36)]},
        {"name": "bass", "source": {"kind": "faust", "id": "bass_warm"},
         "notes": [N(0, 40), N(2, 43)]},
        {"name": "lead", "source": {"kind": "faust", "id": "flute_lead"},
         "notes": [N(0, 64), N(1, 67)]},
    ]}
    aj = ["kick", "bass", "lead"]
    pj0 = jam.build_phrase_song(ebj, aj, 0.5, 120, "C")
    pj4 = jam.build_phrase_song(ebj, aj, 0.5, 120, "C", prog=-4)
    trk2 = lambda s, nm: next(t for t in s["tracks"] if t["name"] == nm)
    ok([n["pitch"] for n in trk2(pj4, "bass")["notes"]] == [36, 39]
       and [n["pitch"] for n in trk2(pj4, "lead")["notes"]] == [60, 63],
       "prog moves BASS + melodic rungs by the degree")
    ok(json.dumps(trk2(pj4, "kick")) == json.dumps(trk2(pj0, "kick")),
       "the groove is sacred: kick untouched by the journey")
    ok(json.dumps(jam.build_phrase_song(ebj, aj, 0.5, 120, "C", prog=0))
       == json.dumps(pj0), "prog=0 is byte-legacy")
    pj_mask = jam.build_phrase_song(ebj, aj, 0.5, 120, "C", prog=-4, pc_mask=[0, 3, 7])
    ok([n["pitch"] for n in trk2(pj_mask, "bass")["notes"]] == [40, 43],
       "PRECEDENCE: a human's mask holds the root — prog forced 0 under a mask")

    # ---------- THE TOUCH FOLLOW: how hard you play shades how hard IT plays ----------
    tb = {"tracks": [
        {"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
         "notes": [N(0, 36, 1.0)]},
        {"name": "bass", "source": {"kind": "faust", "id": "bass_warm"},
         "notes": [N(0, 40, 0.9)]},
        {"name": "hat", "source": {"kind": "faust", "id": "hat"},
         "notes": [N(0, 42, 0.8), N(0.5, 42, 0.6)]},
    ]}
    ta = ["kick", "bass", "hat"]
    soft = jam.build_phrase_song(tb, ta, 0.5, 120, "C", touch=0.0)
    hard = jam.build_phrase_song(tb, ta, 0.5, 120, "C", touch=1.0)
    ok([n["vel"] for n in trk2(soft, "hat")["notes"]] == [0.6, 0.45],
       f"soft touch: hat x0.75 ({[n['vel'] for n in trk2(soft, 'hat')['notes']]})")
    ok([n["vel"] for n in trk2(hard, "hat")["notes"]] == [0.92, 0.69],
       f"hard touch: hat x1.15 ({[n['vel'] for n in trk2(hard, 'hat')['notes']]})")
    ok(trk2(soft, "kick")["notes"][0]["vel"] == 1.0
       and trk2(soft, "bass")["notes"][0]["vel"] == 0.9,
       "FOUNDATION anchored: kick+bass keep their touch (sub stays dominant)")
    ok(json.dumps(jam.build_phrase_song(tb, ta, 0.5, 120, "C"))
       == json.dumps(jam.build_phrase_song(tb, ta, 0.5, 120, "C", touch=None)),
       "no human, no shading (byte-legacy)")
    over = jam.build_phrase_song(
        {"tracks": [{"name": "hat", "source": {"kind": "faust", "id": "hat"},
                     "notes": [N(0, 42, 0.95)]}]}, ["hat"], 0.5, 120, "C", touch=1.0)
    ok(over["tracks"][0]["notes"][0]["vel"] == 1.0, "touch clamps at 1.0 (never blows)")

    # ---------- pc_mask: answer the harmony ----------
    base = {"tracks": [
        {"name": "kick", "source": {"kind": "faust", "id": "hardkick"},
         "notes": [N(0, 36), N(1, 36)]},
        {"name": "lead", "source": {"kind": "faust", "id": "flute_lead"},
         "notes": [N(0, 60), N(1, 61), N(2, 66), N(3, 65)]},
    ]}
    s_m = jam.build_phrase_song(base, ["kick", "lead"], 0.5, 120, "C minor", pc_mask=[0, 3, 7])
    lead = next(t for t in s_m["tracks"] if t["name"] == "lead")
    kick = next(t for t in s_m["tracks"] if t["name"] == "kick")
    got = [n["pitch"] for n in lead["notes"]]
    #  60 (C) in mask -> stays; 61 (C#) -> -1 -> 60; 66 (F#) -> +1 -> 67 (G);
    #  65 (F): +1=F#,-1=E,+2=G(pc7 in mask!) -> 67
    ok(got == [60, 60, 67, 67], f"lead snaps to the human's harmony (got {got})")
    ok([n["pitch"] for n in kick["notes"]] == [36, 36], "drums never touched by the mask")
    far = {"tracks": [{"name": "lead", "source": {"kind": "faust", "id": "flute_lead"},
                       "notes": [N(0, 65)]}]}
    s_far = jam.build_phrase_song(far, ["lead"], 0.5, 120, "C", pc_mask=[0])
    ok(s_far["tracks"][0]["notes"][0]["pitch"] == 65,
       "a note farther than +-2 keeps its pitch (no melodic destruction)")
    s_nom = jam.build_phrase_song(base, ["kick", "lead"], 0.5, 120, "C minor")
    ok([n["pitch"] for n in next(t for t in s_nom["tracks"] if t["name"] == "lead")["notes"]]
       == [60, 61, 66, 65], "no mask -> untouched (5-arg legacy call works)")
    ok(json.dumps(s_m) == json.dumps(jam.build_phrase_song(
        base, ["kick", "lead"], 0.5, 120, "C minor", pc_mask=[0, 3, 7])), "mask deterministic")


def live_leg():
    """B3 LIVE WIRING: jam_live --human, e2e through REAL renders. read_human's
    three file shapes; a DENSE C-minor human makes the set diverge from the solo
    control + comps the melodic rungs out (SPACE, e2e); a SPARSE C-minor human
    snaps the melodic voicing toward [0,3,7] (mask, e2e); the decide feed carries
    the human context for the app's cluster to render."""
    import jam_live as JL
    if not os.path.exists(jam.M1):
        print("  (live leg skipped: m1 not built)")
        return
    d = tempfile.mkdtemp(prefix="follow_live_")
    try:
        # ---- read_human: the three shapes + the torn tail ----
        ja = os.path.join(d, "a.json")
        open(ja, "w").write(json.dumps([N(0, 60), {"bad": 1}]))
        ok(len(JL.read_human(ja)) == 1, "read_human: array form filters non-notes")
        js = os.path.join(d, "s.json")
        open(js, "w").write(json.dumps({"tracks": [{"notes": [N(0, 60), N(1, 63)]}]}))
        ok(len(JL.read_human(js)) == 2, "read_human: song form flattens tracks")
        jl = os.path.join(d, "n.jsonl")
        open(jl, "w").write(json.dumps(N(0, 60)) + "\n" + json.dumps(N(1, 63)) + "\n" + '{"torn')
        ok(len(JL.read_human(jl)) == 2, "read_human: jsonl + torn tail tolerated")
        ok(JL.read_human(os.path.join(d, "nope.json")) == [], "read_human: missing -> []")

        def run(tag, human_path, follow):
            # vibe "peak" BUILDS every phrase -> the solo control provably reaches
            # the melodic rungs (house LADDER: color first), so SPACE and the mask
            # are proven against real melodic material, never vacuously
            ipc = os.path.join(d, "ipc_" + tag)
            res, err = JL.jam_live("house", "peak", phrases=3, seed=7,
                                   name="_folbat_" + tag, bars_per=1, ipc=ipc,
                                   human_path=human_path, follow=follow)
            ok(err is None, f"[{tag}] jam_live ran ({err})")
            feed = []
            fp = os.path.join(ipc, "live.jsonl")
            if os.path.exists(fp):
                for ln in open(fp):
                    try:
                        feed.append(json.loads(ln))
                    except json.JSONDecodeError:
                        pass
            phr = {}
            for pj in glob.glob(os.path.join(ipc, "ph*.json")):
                phr[os.path.basename(pj)] = json.load(open(pj))
            sng = os.path.join(jam.SONGS, "_folbat_" + tag + ".json")
            if os.path.exists(sng):
                os.remove(sng)
            return res, feed, phr

        # ---- solo control vs a DENSE C-minor human (16ths, pre-set noodling too) ----
        hp_dense = os.path.join(d, "dense.jsonl")
        with open(hp_dense, "w") as f:
            for i in range(-16, 12 * 4):
                f.write(json.dumps(N(i * 0.25, (60, 63, 67)[i % 3], 0.95)) + "\n")
        rb, fb, pb = run("solo", None, 0.5)
        ok(rb.get("rail") == "serve",
           f"THE RAIL is ARMED by default (usage is cache weather) ({rb.get('rail')})")
        # THE DEADLINE LEG (deterministic repro of the pulse's -0.3s underrun):
        # wait_reply on a slow render MUST raise TimeoutExpired AT the deadline —
        # the old blocking readline sailed past it and accepted the late reply,
        # so the REPEAT law never fired. Then cancel-as-kill drains and the rail
        # renders TRUE right after (the _StoreOnWait kill contract).
        import jam_live as _JL
        _rail = _JL._ServeRail()
        _rail.boot()
        _big = {"version": 2, "bpm": 120, "lengthBars": 24, "masterGainDb": 0.0,
                "master": [],
                "tracks": [{"name": f"t{_i}", "source": {"kind": "faust", "id": _v},
                            "gainDb": -8,
                            "notes": [{"start": _b * 0.5, "len": 0.4,
                                       "pitch": 40 + _i * 7 + (_b % 12), "vel": 0.8}
                                      for _b in range(192)]}
                           for _i, _v in enumerate(("bass_warm", "flute_lead", "harp"))]}
        _bp = os.path.join(d, "deadline_big.json")
        json.dump(_big, open(_bp, "w"))
        _bw = os.path.join(d, "deadline_big.wav")
        _rid = _rail.submit(_bp, _bw)
        ok(_rid is not None, "deadline leg: the rail accepted the slow render")
        _t0 = time.monotonic()
        try:
            _rail.wait_reply(_rid, timeout=0.6)
            _to = False
        except Exception:
            _to = True
        _dt = time.monotonic() - _t0
        ok(_to and _dt < 1.2,
           f"THE DEADLINE HOLDS: TimeoutExpired at ~0.6s, not when the reply lands ({_dt:.2f}s)")
        _rail.cancel(_rid)
        _sm = {"version": 2, "bpm": 126, "lengthBars": 1, "masterGainDb": 0.0, "master": [],
               "tracks": [{"name": "k", "source": {"kind": "faust", "id": "hardkick"},
                           "gainDb": -4,
                           "notes": [{"start": float(_b), "len": 0.2, "pitch": 36, "vel": 1.0}
                                     for _b in range(4)]}]}
        _sp = os.path.join(d, "deadline_small.json")
        json.dump(_sm, open(_sp, "w"))
        _sw = os.path.join(d, "deadline_small.wav")
        _rid2 = _rail.submit(_sp, _sw)
        _rep2 = _rail.wait_reply(_rid2, timeout=60)
        ok(_rep2.get("ok") == 1 and os.path.getsize(_sw) > 1000,
           "after cancel-as-kill the rail renders TRUE (drain left the pipe clean)")
        _rail.stop()
        os.environ["SOTADAW_RENDER_SERVE"] = "0"
        try:
            r_ks, _f0, _p0 = run("railoff", None, 0.5)
            ok(r_ks.get("rail") == "off",
               f"kill-switch reports the rail OFF ({r_ks.get('rail')})")
        finally:
            os.environ.pop("SOTADAW_RENDER_SERVE", None)
        rd, fd, pd = run("dense", hp_dense, 0.8)
        sess_b = next((e for e in fb if e.get("ev") == "session"), {})
        sess_d = next((e for e in fd if e.get("ev") == "session"), {})
        ok(sess_d.get("human") is True and sess_b.get("human") is False,
           "session feed declares the follow mode")
        dec_d = [e for e in fd if e.get("ev") == "decide"]
        ok(dec_d and all(e.get("human", {}).get("density", 0) > 0.7 for e in dec_d),
           f"decide feed carries the dense human ({[e.get('human', {}).get('density') for e in dec_d]})")
        melodic_d = [t["name"] for p in pd.values() for t in p["tracks"] if t["name"] in jam.MELODIC]
        ok(melodic_d == [],
           f"SPACE e2e: no melodic rung plays behind a busy soloist (got {melodic_d})")
        moves_b = [e.get("move") for e in fb if e.get("ev") == "decide"]
        moves_d = [e.get("move") for e in fd if e.get("ev") == "decide"]
        ok(moves_b != moves_d or json.dumps(pb, sort_keys=True) != json.dumps(pd, sort_keys=True),
           f"the human CHANGES the set (solo {moves_b} vs dense {moves_d})")

        # ---- a SPARSE C-minor human: harmony follows, decisions stay gentle ----
        hp_sparse = os.path.join(d, "sparse.jsonl")
        with open(hp_sparse, "w") as f:
            for i in range(-2, 12):
                f.write(json.dumps(N(float(i), (60, 63, 67)[i % 3], 0.85)) + "\n")
        rs, fs, ps = run("sparse", hp_sparse, 0.3)
        dec_s = [e for e in fs if e.get("ev") == "decide"]
        ok(dec_s and all(e.get("human", {}).get("pitch_classes") == [0, 3, 7] for e in dec_s),
           f"decide feed carries the human's harmony ({[e.get('human', {}).get('pitch_classes') for e in dec_s]})")
        # ---- JIT REACTIVITY: a burst written MID-WINDOW shapes the SAME window ----
        # The old scheduler decided p+1 at p's window START; JIT decides at the
        # last responsible moment. We watch the feed for phrase 0 starting, write
        # a dense C-minor burst ~35% into its window (after the OLD decide point,
        # before the JIT one) and it MUST appear in phrase 0's decide event.
        import threading
        import time as _t
        hp_jit = os.path.join(d, "jit.jsonl")
        open(hp_jit, "w").write("")
        ipc_jit = os.path.join(d, "ipc_jit")

        def burst_writer():
            fp = os.path.join(ipc_jit, "live.jsonl")
            t0 = _t.monotonic()
            while _t.monotonic() - t0 < 30.0:
                try:
                    if os.path.exists(fp) and "phrase_ready" in open(fp).read():
                        break
                except OSError:
                    pass
                _t.sleep(0.02)
            _t.sleep(0.35 * (8 * 60.0 / 126.0))      # 35% into phrase 0's 2-BAR window
            with open(hp_jit, "a") as f:
                for i in range(48):
                    f.write(json.dumps(N(i * 0.25, (60, 63, 67)[i % 3], 0.95)) + "\n")

        tw = threading.Thread(target=burst_writer)
        tw.start()
        # 2-bar windows: with a human present the gate budgets a COLD render
        # (novelty law), and JIT must still engage — half a 2-bar window holds it
        res_j, err_j = JL.jam_live("house", "steady", phrases=3, seed=7,
                                   name="_folbat_jit", bars_per=2, ipc=ipc_jit,
                                   human_path=hp_jit, follow=0.6)
        tw.join(timeout=10.0)
        ok(err_j is None, f"[jit] jam_live ran ({err_j})")
        feed_j = []
        fpj = os.path.join(ipc_jit, "live.jsonl")
        if os.path.exists(fpj):
            for ln in open(fpj):
                try:
                    feed_j.append(json.loads(ln))
                except json.JSONDecodeError:
                    pass
        dj = [e for e in feed_j if e.get("ev") == "decide"]
        d0 = next((e for e in dj if e.get("phrase") == 0), {})
        d1 = next((e for e in dj if e.get("phrase") == 1), {})
        # LOAD-AWARE BY DESIGN (the pulse caught this leg red under suite load):
        # a slammed box inflates ph0's measured gen -> the novelty gate CORRECTLY
        # yields JIT on the roomy window -> the burst legitimately lands at the
        # NEXT decide. Assert what the LAW guarantees load-independently: the
        # burst is heard no later than the first decide after it lands, and the
        # engagement path matches the gate's own observable choice.
        engaged = dj and dj[0].get("t_in_window", 0) >= 0.3
        if engaged:
            ok(d0.get("human", {}).get("density", 0) > 0.5,
               f"JIT engaged: the mid-window burst shaped THAT window's decide "
               f"(p0 density {d0.get('human', {}).get('density')})")
        else:
            print("  (JIT gate yielded under load — asserting the burst at the next decide)")
            ok(d1.get("human", {}).get("density", 0) > 0.5,
               f"gate yielded: the burst is heard at the NEXT decide "
               f"(p1 density {d1.get('human', {}).get('density')})")
        later = dj[1:-1] or dj[1:]
        if not engaged:
            later = later[1:]   # gate yielded under load: the slid burst OWNS decide #1's window
        ok(all(e.get("t_in_window", 1) <= 0.2 for e in later),
           f"novelty gate YIELDS on short human windows ({[e.get('t_in_window') for e in dj]})")
        ok(res_j is not None and all(t["ready"] for t in res_j["timing"][:-1] or res_j["timing"]),
           f"JIT: still NO underruns ({[t['slack_s'] for t in res_j['timing']]})")
        sng_j = os.path.join(jam.SONGS, "_folbat_jit.json")
        if os.path.exists(sng_j):
            os.remove(sng_j)

        # ---- THE CONVERSATION LAW: busy humans get SHORT answers ----
        hp_conv = os.path.join(d, "conv.jsonl")
        with open(hp_conv, "w") as f:            # dense from pre-roll through the set
            for i in range(-8 * 4, 24 * 4):
                f.write(json.dumps(N(i * 0.25, (60, 63, 67)[i % 3], 0.95)) + "\n")
        ipc_c = os.path.join(d, "ipc_conv")
        rc_c, err_c = JL.jam_live("house", "steady", phrases=3, seed=7,
                                  name="_folbat_conv", bars_per=2, ipc=ipc_c,
                                  human_path=hp_conv, follow=0.6)
        ok(err_c is None, f"[conv] jam_live ran ({err_c})")
        fc = [json.loads(l) for l in open(os.path.join(ipc_c, "live.jsonl"))]
        prs = [e for e in fc if e.get("ev") == "phrase_ready"]
        bars_seq = [e.get("bars") for e in prs]
        ok(bars_seq and bars_seq[0] == 1,
           f"CONV: pre-roll noodling shortens the OPENER ({bars_seq})")
        ok(len(bars_seq) > 1 and all(b == 1 for b in bars_seq[1:]),
           f"CONV: busy human -> 1-bar answers throughout ({bars_seq})")
        pos, contig = 0.0, True
        for e in prs:
            contig = contig and abs(float(e["start_beat"]) - pos) < 1e-6
            pos = float(e["start_beat"]) + float(e["bars"]) * 4.0
        ok(contig and abs(pos - 24.0) < 1e-6,
           f"CONV grid law: contiguous phrases, set length preserved ({pos} beats)")
        ipc_c2 = os.path.join(d, "ipc_conv2")
        rc_c2, _e2 = JL.jam_live("house", "steady", phrases=3, seed=7,
                                 name="_folbat_conv2", bars_per=2, ipc=ipc_c2)
        fc2 = [json.loads(l) for l in open(os.path.join(ipc_c2, "live.jsonl"))]
        ok(all(e.get("bars") == 2 for e in fc2 if e.get("ev") == "phrase_ready"),
           "CONV: solo sets never shorten (fixed-length contract intact)")
        for nm in ("_folbat_conv", "_folbat_conv2"):
            pp = os.path.join(jam.SONGS, nm + ".json")
            if os.path.exists(pp):
                os.remove(pp)

        # ---- THE PUNCH-IN (scheduler half): a mid-phrase burst is ANSWERED mid-phrase ----
        # Long quiet phrases (bars_per=4) + a burst just after the downbeat: the
        # JIT-wait watcher must render a SPACE answer for an INTERIOR bar line,
        # and the kept take must show the surgery: [0,4) identical to a solo
        # control, the punched span REPLACED by the pattern restarting at the
        # line (the RESTART SIGNATURE — exact, deterministic).
        def span(doc, a, b):
            out = []
            for t in doc.get("tracks", []):
                for n in t.get("notes", []):
                    if a - 1e-6 <= float(n["start"]) < b - 1e-6:
                        out.append((t["name"], round(float(n["start"]) - a, 4),
                                    int(n["pitch"]), round(float(n.get("vel", 0.8)), 3)))
            return sorted(out)

        ipc_p0 = os.path.join(d, "ipc_pctl")
        rc_p0, _ep0 = JL.jam_live("house", "steady", phrases=2, seed=7,
                                  name="_folbat_pctl", bars_per=4, ipc=ipc_p0)
        ctl = json.load(open(os.path.join(jam.SONGS, "_folbat_pctl.json")))

        hp_punch = os.path.join(d, "punch.jsonl")
        open(hp_punch, "w").write("")
        ipc_p1 = os.path.join(d, "ipc_punch")

        def punch_writer():
            fp = os.path.join(ipc_p1, "live.jsonl")
            t0 = _t.monotonic()
            while _t.monotonic() - t0 < 30.0:
                try:
                    if os.path.exists(fp) and "phrase_ready" in open(fp).read():
                        break
                except OSError:
                    pass
                _t.sleep(0.02)
            _t.sleep(0.6)                        # ~beat 1.3: just after the downbeat
            with open(hp_punch, "a") as f:
                for i in range(128):             # dense C-minor 16ths, beats 0..32
                    f.write(json.dumps(N(i * 0.25, (60, 63, 67)[i % 3], 0.95)) + "\n")

        tp = threading.Thread(target=punch_writer)
        tp.start()
        rc_p1, err_p1 = JL.jam_live("house", "steady", phrases=2, seed=7,
                                    name="_folbat_punch", bars_per=4, ipc=ipc_p1,
                                    human_path=hp_punch, follow=0.6)
        tp.join(timeout=10.0)
        ok(err_p1 is None, f"[punch] jam_live ran ({err_p1})")
        fp1 = [json.loads(l) for l in open(os.path.join(ipc_p1, "live.jsonl"))]
        punches = [e for e in fp1 if e.get("ev") == "punch_ready"]
        ok(len(punches) == 1, f"PUNCH: exactly one mid-phrase answer ({len(punches)})")
        if punches:
            pu = punches[0]
            at = float(pu["at_beat"])
            ok(at % 4.0 == 0.0 and 4.0 <= at < 16.0,
               f"PUNCH lands on an INTERIOR bar line (at_beat {at})")
            ok(int(pu["bars"]) == int((16.0 - at) / 4.0),
               f"PUNCH spans the phrase remainder ({pu['bars']} bars)")
            ok(os.path.exists(pu["wav"]) and os.path.getsize(pu["wav"]) > 1024,
               "PUNCH wav is real")
            pun = json.load(open(os.path.join(jam.SONGS, "_folbat_punch.json")))
            def spanp(doc, a, b):    # pitch grammar (vel carried by the TOUCH law)
                return sorted((nm, st, pi) for nm, st, pi, _v in span(doc, a, b))
            ok(span(pun, 0, 4) == span(ctl, 0, 4),
               "pre-burst material identical to the solo control (vel included)")
            ok(spanp(pun, at, 16) == spanp(ctl, 0, 16 - at),
               "RESTART SIGNATURE: the punched span IS the pattern restarted (pitch grammar)")
            pv = [v for nm, st, pi, v in span(pun, at, 16) if nm not in ("kick", "bass")]
            cv = [v for nm, st, pi, v in span(ctl, 0, 16 - at) if nm not in ("kick", "bass")]
            ok(pv and cv and sum(pv) / len(pv) > sum(cv) / len(cv) + 0.02,
               f"TOUCH in the take: the punch plays HARDER behind a hot human "
               f"({sum(pv)/len(pv):.3f} vs {sum(cv)/len(cv):.3f})")
            if spanp(ctl, at, 16) != spanp(ctl, 0, 16 - at):
                ok(spanp(pun, at, 16) != spanp(ctl, at, 16),
                   "surgery visibly replaced the original remainder")
            else:
                print("  (surgery-diff sub-check skipped: repeating DNA)")
        for nm in ("_folbat_pctl", "_folbat_punch"):
            pp = os.path.join(jam.SONGS, nm + ".json")
            if os.path.exists(pp):
                os.remove(pp)

        # ---- THE FOLLOW, OFFLINE LANE: the band composes AROUND a static take ----
        # (the agent workflow: "here's my riff — jam around it": Rec take or
        #  audio_follow output in, a full composed-around set out, faster than RT)
        hp_off = os.path.join(d, "off.jsonl")
        with open(hp_off, "w") as f:      # dense swung Cm across offline phrases 1-2
            for b in range(16, 48):
                for off, pp, vv in ((0.0, (60, 63, 67)[b % 3], 0.95),
                                    (0.25, (60, 63, 67)[b % 3], 0.4),
                                    (0.62, (63, 67, 60)[b % 3], 0.9),
                                    (0.75, (67, 60, 63)[b % 3], 0.4)):
                    f.write(json.dumps(N(b + off, pp, vv)) + "\n")
        r_off, e_off = jam.jam("house", "peak", phrases=3, seed=7,
                               name="_folbat_off", human_path=hp_off, follow=0.6)
        ok(e_off is None, f"[offline] jam ran ({e_off})")
        r_ctl2, _e2c = jam.jam("house", "peak", phrases=3, seed=7, name="_folbat_offc")
        doc_off = json.load(open(os.path.join(jam.SONGS, "_folbat_off.json")))
        doc_ctl2 = json.load(open(os.path.join(jam.SONGS, "_folbat_offc.json")))
        mel_off = [t["name"] for t in doc_off["tracks"]
                   if t["name"] in jam.MELODIC and t.get("notes")]
        mel_ctl = [t["name"] for t in doc_ctl2["tracks"]
                   if t["name"] in jam.MELODIC and t.get("notes")]
        ok(bool(mel_ctl) and not mel_off,
           f"OFFLINE SPACE: solo grows melody ({mel_ctl}), around-the-take does not ({mel_off})")
        ok(json.dumps(doc_off, sort_keys=True) != json.dumps(doc_ctl2, sort_keys=True),
           "the take CHANGES the offline composition")
        for nm in ("_folbat_off", "_folbat_offc"):
            pp2 = os.path.join(jam.SONGS, nm + ".json")
            if os.path.exists(pp2):
                os.remove(pp2)

        compared = 0
        snapped_ok = True
        for pjname, pdoc in ps.items():
            # HARMONIC JOURNEY compensation: the SOLO control transposes by the
            # journey (masked runs hold the human's root — precedence), and the
            # transform is KNOWN — compare against the un-journeyed control
            # pitch instead of skipping phrases (melodic rungs often arrive
            # only after the journey has already stepped).
            try:
                prog_c = jam.journey_offset(float(int(pjname[2:-5])))
            except ValueError:
                continue
            ctrl = pb.get(pjname)
            for t in pdoc["tracks"]:
                if t["name"] not in jam.MELODIC:
                    continue
                ct = next((x for x in (ctrl or {"tracks": []})["tracks"]
                           if x["name"] == t["name"]), None)
                if ct is None or len(ct["notes"]) != len(t["notes"]):
                    continue                     # decisions diverged: nothing to pair
                for a, b in zip(t["notes"], ct["notes"]):
                    compared += 1
                    if a["pitch"] % 12 not in (0, 3, 7) \
                            and a["pitch"] != b["pitch"] - prog_c:
                        snapped_ok = False
        ok(compared > 0, f"mask e2e compared real melodic notes ({compared})")
        ok(snapped_ok, "mask e2e: every moved melodic note lands in the human's classes")
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()
    live_leg()
    for f in FAIL:
        print("FAIL:", f)
    print(f"jam-follow battery: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
