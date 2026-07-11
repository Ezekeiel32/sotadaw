#!/usr/bin/env python3
"""THE FULL-SET PROOF — every band-seat law, COMPOSED, in one real set.

The piecewise batteries prove each law alone; the last three bugs all lived in
law INTERACTIONS (JIT x cache, conversation x novelty, evolve x cold renders).
This is the composition seal: one scripted human journey through a REAL
jam_live set — quiet open, a dense SWUNG C-minor solo mid-set, quiet outro —
and the feed + phrase files + kept take must show ALL the laws at once:

  conversation   bars 2 -> 1 during the solo -> back to 2 after
  space          no melodic rung behind the busy soloist
  groove follow  solo-span phrases stamped swing {8th, ~0.62}; quiet spans NOT
  harmony        decide events carry [0,3,7] during the solo
  grid           phrase starts contiguous, set length exact
  repeat law     any not-ready phrase wears repeat=true (never silence)
  full circle    the kept take renders AUDIBLE through the real engine

Usage: .venv/bin/python tools/band_set_proof.py
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import jam
import jam_live as JL

PASS, FAIL = 0, []


def ok(cond, msg):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append(msg)


def N(start, pitch, vel=0.9, ln=0.25):
    return {"start": start, "len": ln, "pitch": pitch, "vel": vel}


def main():
    if not os.path.exists(jam.M1):
        print("band-set proof: SKIP (m1 not built)")
        return
    d = tempfile.mkdtemp(prefix="band_set_")
    name = "_bandset"
    try:
        # THE SCRIPTED HUMAN: sparse straight pre-roll; silence to beat 16;
        # a DENSE swung-8ths C-minor solo 16..32; silence out. The scheduler
        # rereads per phrase and future notes are invisible until their time.
        # The solo is a REAL soloist's line: swung 8ths (downbeat + off at .62)
        # FILLED with ghost 16ths at .25/.75 — the ghosts push density to 1.0
        # (busy: conversation AND space arm) while staying INVISIBLE to the
        # swing lanes (.25 below, .75 above the windows): feel reads pure 8th.
        # 8 phrases = 64 beats: the 16-beat listening window keeps the solo
        # "in the ears" ~12 beats past its end — the outro must outlive that
        # for the relax-back to show (the composed run taught this).
        hp = os.path.join(d, "human.jsonl")
        with open(hp, "w") as f:
            for b in range(-8, 0):
                f.write(json.dumps(N(float(b), (60, 63, 67)[b % 3], 0.6)) + "\n")
            for b in range(16, 32):
                f.write(json.dumps(N(float(b), (60, 63, 67)[b % 3], 0.95)) + "\n")
                f.write(json.dumps(N(b + 0.25, (60, 63, 67)[b % 3], 0.4)) + "\n")
                f.write(json.dumps(N(b + 0.62, (63, 67, 60)[b % 3], 0.9)) + "\n")
                f.write(json.dumps(N(b + 0.75, (67, 60, 63)[b % 3], 0.4)) + "\n")
        ipc = os.path.join(d, "ipc")
        res, err = JL.jam_live("house", "steady", phrases=8, seed=7, name=name,
                               bars_per=2, ipc=ipc, human_path=hp, follow=0.6)
        ok(err is None, f"the set ran ({err})")
        if res is None:
            return
        feed = []
        for ln in open(os.path.join(ipc, "live.jsonl")):
            try:
                feed.append(json.loads(ln))
            except json.JSONDecodeError:
                pass
        prs = [e for e in feed if e.get("ev") == "phrase_ready"]
        dec = [e for e in feed if e.get("ev") == "decide"]

        # ---- grid: contiguous, exact total ----
        pos, contig = 0.0, True
        for e in prs:
            contig = contig and abs(float(e["start_beat"]) - pos) < 1e-6
            pos = float(e["start_beat"]) + float(e["bars"]) * 4.0
        ok(contig and abs(pos - 64.0) < 1e-6,
           f"grid law: contiguous, 64 beats exact (got {pos})")

        # ---- conversation arc: 2 -> 1 (solo) -> 2 (recovery) ----
        bars = [int(e["bars"]) for e in prs]
        ok(bars[0] == 2, f"quiet open = full statements ({bars})")
        ok(1 in bars, f"the solo shortened the turns ({bars})")
        ok(2 in bars[bars.index(1):] if 1 in bars else False,
           f"the band relaxed back after the solo ({bars})")

        # ---- solo laws by CAUSALITY, not beat-guessing: a phrase is a FOLLOW
        # phrase iff its SPAWNING decide heard the busy human (decide p -> ph
        # p+1) — a phrase whose span overlaps the solo but was decided BEFORE
        # the burst is honestly unstamped (the debug run taught this).
        follow_ph = {int(e["phrase"]) + 1 for e in dec
                     if e.get("human", {}).get("density", 0) > 0.7}
        ok(len(follow_ph) >= 2, f"the solo drove phrases ({sorted(follow_ph)})")
        space_ok, swing_ok, quiet_unstamped = True, False, True
        for i, e in enumerate(prs):
            pj = os.path.join(ipc, f"ph{int(e['phrase'])}.json")
            if not os.path.exists(pj):
                continue
            doc = json.load(open(pj))
            in_solo = int(e["phrase"]) in follow_ph and not e.get("repeat")
            names = [t["name"] for t in doc.get("tracks", [])]
            if in_solo and any(nm in jam.MELODIC for nm in names):
                space_ok = False
            sw = doc.get("swing")
            if in_solo and sw and sw.get("grid") == "8th" \
                    and abs(float(sw.get("amount", 0.5)) - 0.62) < 0.03:
                swing_ok = True
            if float(e["start_beat"]) < 12.0 and sw is not None:
                quiet_unstamped = False
        ok(space_ok, "SPACE: no melodic rung behind the busy soloist")
        ok(swing_ok, "GROOVE: solo-span phrases stamped swing {8th, ~0.62}")
        ok(quiet_unstamped, "quiet spans never stamped (solo contract)")
        solo_dec = [e for e in dec
                    if e.get("human", {}).get("density", 0) > 0.7]
        ok(solo_dec and all(e["human"].get("pitch_classes") == [0, 3, 7]
                            for e in solo_dec),
           f"HARMONY: the solo's classes rode every busy decide ({len(solo_dec)})")

        # ---- repeat law: not-ready always means repeat, never silence ----
        not_ready = [t for t in res["timing"][:-1] if not t["ready"]]
        repeats = [e for e in prs if e.get("repeat")]
        ok(len(repeats) >= len(not_ready),
           f"REPEAT LAW: every late render repeated ({len(not_ready)} late, "
           f"{len(repeats)} repeats)")

        # ---- full circle: the kept take renders AUDIBLE ----
        take = os.path.join(jam.SONGS, f"{name}.json")
        ok(os.path.exists(take), "the kept take exists")
        doc = json.load(open(take))
        ok(float(doc.get("lengthBars", 0)) == 16.0
           and len(doc.get("sections", [])) == len(res["log"]),
           f"take truth: 16 bars, {len(res['log'])} sections")
        import subprocess
        import wave
        import numpy as np
        tw = os.path.join(d, "take.wav")
        subprocess.run([jam.M1, "render", take, tw], capture_output=True, timeout=300)
        ok(os.path.exists(tw), "the take renders")
        if os.path.exists(tw):
            w = wave.open(tw)
            sw_ = w.getsampwidth()
            raw = w.readframes(w.getnframes())
            if sw_ == 3:
                a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
                x = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8)
                     | (a[:, 2].astype(np.int32) << 16))
                x = np.where(x & 0x800000, x - 0x1000000, x).astype(np.float64) / 8388608.0
            else:
                x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
            rms_db = 20.0 * np.log10(float(np.sqrt((x ** 2).mean())) + 1e-12)
            ok(rms_db > -35.0, f"FULL CIRCLE: the set is AUDIBLE ({rms_db:.1f} dB)")
    finally:
        p = os.path.join(jam.SONGS, f"{name}.json")
        if os.path.exists(p):
            os.remove(p)
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()
    for f in FAIL:
        print("FAIL:", f)
    print(f"band-set proof: {PASS}/{PASS + len(FAIL)} {'clean' if not FAIL else 'RED'}")
    sys.exit(1 if FAIL else 0)
