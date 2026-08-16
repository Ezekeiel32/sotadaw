#!/usr/bin/env python3
"""THE PORTABLE SCORE battery — pure proofs for tools/midi_producer.py.

    .venv/bin/python tools/midi_producer_battery.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import midi_producer as mp

PASS = FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


def N(start, ln, pitch, vel=0.8):
    return {"start": start, "len": ln, "pitch": pitch, "vel": vel}


def main():
    print("== ROLES + GM IDENTITY ==")
    check("Kick is drum", mp.role_of("Kick") == "drum")
    check("bass_sketch is bass", mp.role_of("bass_sketch") == "bass")
    check("vocals_sketch is vocal", mp.role_of("vocals_sketch") == "vocal")
    check("guitar_chords is chords", mp.role_of("guitar_chords") == "chords")
    check("piano_lead is lead", mp.role_of("piano_lead") == "lead")
    check("bass program 33", mp.program_of("bass_sketch") == 33)
    check("guitar program 26", mp.program_of("guitar_lead") == 26)
    check("vocals program 52", mp.program_of("vocals_sketch") == 52)
    check("other_lead saw lead", mp.program_of("other_lead") == 81)
    check("alt kick 33 -> GM 35", mp.DRUM_GM_REMAP[33] == 35)
    check("alt hat 44 -> GM 42", mp.DRUM_GM_REMAP[44] == 42)

    print("== DEWAVE (vibrato confetti -> sustained note) ==")
    wavy = [N(i * 0.1, 0.09, 60 + (i % 2), 0.5 + 0.02 * i) for i in range(7)]
    out = mp.dewave(wavy)
    check("7-fragment vibrato -> 1 note", len(out) == 1, f"{len(out)}")
    check("collapsed spans the run", out and abs(
        (out[0]["start"] + out[0]["len"]) - 0.69) < 0.02)
    drift = [N(i * 0.1, 0.09, 60 + i) for i in range(6)]      # walks 60..65
    out = mp.dewave(drift)
    check("melisma drift collapses within span guard", 1 < len(out) < 6,
          f"{len(out)}")
    melody = [N(i * 0.5, 0.45, [60, 67, 64, 72][i % 4]) for i in range(8)]
    check("real melody (wide intervals) untouched",
          len(mp.dewave(melody)) == 8)
    longs = [N(0, 1.0, 60), N(1.05, 1.0, 61)]
    check("long notes never collapse", len(mp.dewave(longs)) == 2)
    stutter = [N(0, 0.1, 60), N(0.15, 0.1, 60)]
    check("same-pitch stutter pair merges", len(mp.dewave(stutter)) == 1)

    print("== DEGUN (machine-gun retriggers) ==")
    guns = [N(0, 0.05, 36, 0.9), N(0.06, 0.05, 36, 0.5), N(0.12, 0.05, 36, 0.7)]
    out = mp.degun(guns, 0.12)
    check("3 kicks 0.06 apart -> 1", len(out) == 1, f"{len(out)}")
    check("stronger hit kept", out and out[0]["vel"] == 0.9)
    sixteenths = [N(i * 0.25, 0.1, 42, 0.7) for i in range(8)]
    check("legit 16ths survive", len(mp.degun(sixteenths, 0.12)) == 8)

    print("== POCKET (feel-preserving pull) ==")
    ns = [N(1.03, 0.5, 60)]
    out = mp.pocket(ns, strength=0.6, grid=0.25, tol=0.09)
    check("in-tol note pulled 60% to grid",
          abs(out[0]["start"] - 1.012) < 0.001, f"{out[0]['start']}")
    ns = [N(1.15, 0.5, 60)]
    check("out-of-tol push kept (the FEEL)",
          mp.pocket(ns)[0]["start"] == 1.15)

    print("== GATE ==")
    mono = [N(0, 2.0, 60), N(1.0, 1.2, 62), N(2.5, 0.2, 64)]
    out = mp.gate(mono, mono=True)
    check("overlap trimmed to next onset", out[0]["len"] <= 1.0)
    check("legato fills a small breath", out[1]["len"] >= 0.9 * 1.5 - 0.01)
    rest = [N(0, 0.3, 60), N(2.0, 0.3, 62)]
    check("a real REST is sacred (no legato across it)",
          mp.gate(rest, mono=True)[0]["len"] <= 0.35)
    poly = [N(0, 1.0, 60 + i, 0.3 + 0.1 * i) for i in range(8)]
    out = mp.gate(poly, mono=False, max_poly=6)
    check("poly capped at 6, weakest dropped", len(out) == 6
          and min(n["pitch"] for n in out) == 62)

    print("== DENSITY ==")
    dense = [N(i * 0.1, 0.09, 60 + i % 12, 0.5 + (i % 5) * 0.1)
             for i in range(40)]                       # 40 notes in bar 0
    out = mp.density(dense, cap_per_bar=16)
    check("bar capped at 16 by salience", len(out) == 16)

    print("== PRODUCE_VELOCITY ==")
    ns = [N(i * 0.5, 0.4, 60, v) for i, v in enumerate(
        [0.05] * 8 + [0.05, 0.2, 0.5, 0.91])]
    out = mp.produce_velocity(ns, "lead")
    vs = [n["vel"] for n in out]
    check("0.05 class lifted audible", min(vs) >= 0.30, f"{min(vs)}")
    check("cap holds", max(vs) <= 0.95)
    order_in = [v["vel"] for v in ns]
    check("rank order preserved", all(
        (a <= b) == (c <= d + 1e-9)
        for (a, b), (c, d) in zip(zip(order_in, order_in[1:]),
                                  zip(vs, vs[1:]))))
    flat = [N(i * 0.25, 0.1, 42, 1.0) for i in range(8)]
    out = mp.produce_velocity(flat, "drum", "Hats")
    vs = [n["vel"] for n in out]
    check("flat hats sit mid-band with offbeat dips",
          len(set(round(v, 2) for v in vs)) >= 2 and max(vs) < 0.95)

    print("== PRODUCE (end-to-end, idempotence) ==")
    song = {"bpm": 94, "tracks": [
        {"name": "vocals_sketch", "notes":
         [N(i * 0.1, 0.09, 60 + (i % 2), 0.9) for i in range(9)]},
        {"name": "Kick", "source": {"kind": "sample", "kit": "x_drums"},
         "notes": [N(0, 0.05, 33, 0.9), N(0.06, 0.05, 33, 0.4)]},
        {"name": "drums", "notes": []},
    ]}
    out, rec = mp.produce(song)
    voc = next(t for t in out["tracks"] if t["name"] == "vocals_sketch")
    kick = next(t for t in out["tracks"] if t["name"] == "Kick")
    check("vocal confetti collapsed", len(voc["notes"]) < 4,
          f"{len(voc['notes'])}")
    check("kick degunned + GM-remapped 33->35",
          len(kick["notes"]) == 1 and kick["notes"][0]["pitch"] == 35)
    check("receipts carry before/after", "vocals_sketch" in rec
          and rec["vocals_sketch"]["before"]["notes"] == 9)
    check("empty lanes untouched", not any(
        t["name"] == "drums" and t.get("notes") for t in out["tracks"]))
    out2, _ = mp.produce(out)
    n1 = sum(len(t.get("notes", [])) for t in out["tracks"])
    n2 = sum(len(t.get("notes", [])) for t in out2["tracks"])
    check("second pass ~stable", abs(n1 - n2) <= max(1, n1 // 20),
          f"{n1}->{n2}")

    print(f"\nmidi_producer battery: {PASS} PASS / {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
