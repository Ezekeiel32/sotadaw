#!/usr/bin/env python3
"""G-SOUND A/B HARNESS — blind, loudness-matched listening rounds (CC4 I2 rig).

  ab_harness.py build <name> ours.wav theirs.wav [--seed N]   # make a round
  ab_harness.py verdict <name> <trial#> <a|b> [note]          # record a pick
  ab_harness.py score <name>                                  # tally (unblinds)

THE LAW: loudness bias is the oldest A/B lie — both sides get gain-matched to the
QUIETER side's integrated LUFS (never upward past clipping) before shuffling, so
the pick is about MUSIC, not level. Order per trial is seeded-random and stays
sealed in the manifest until `score`. Files land in eval/ab/<name>/trial<i>_{A,B}.wav
— play them cold, record picks, then score.
"""
import argparse, json, os, random, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ABDIR = os.path.join(ROOT, "eval", "ab")


def lufs(path):
    r = subprocess.run([os.path.join(ROOT, ".venv/bin/python"),
                        os.path.join(ROOT, "tools", "analyze2.py"), path],
                       capture_output=True, text=True, timeout=180)
    return float(json.loads(r.stdout)["lufs_integrated"])


def write_gained(src, dst, gain_db):
    import numpy as np, soundfile as sf
    x, sr = sf.read(src, always_2d=True)
    y = x * (10.0 ** (gain_db / 20.0))
    peak = float(abs(y).max())
    if peak > 0.999:                      # never clip to match — pull both later
        y = y * (0.999 / peak)
    sf.write(dst, y, sr)
    return 20.0 * (0 if peak <= 0.999 else __import__("math").log10(0.999 / peak))


def build(name, ours, theirs, seed=1, trials=3):
    d = os.path.join(ABDIR, name)
    os.makedirs(d, exist_ok=True)
    lo, lt = lufs(ours), lufs(theirs)
    target = min(lo, lt)                  # match DOWN to the quieter side
    print(f"[ab] LUFS ours {lo:.1f} theirs {lt:.1f} -> match at {target:.1f}")
    matched = {}
    for tag, src, l in (("ours", ours, lo), ("theirs", theirs, lt)):
        dst = os.path.join(d, f"_m_{tag}.wav")
        write_gained(src, dst, target - l)
        got = lufs(dst)
        print(f"[ab]   {tag}: {l:.1f} -> {got:.1f} LUFS (delta to target {abs(got-target):.2f})")
        if abs(got - target) > 0.6:
            raise SystemExit(f"loudness match failed for {tag} ({got:.1f} vs {target:.1f})")
        matched[tag] = dst
    rng = random.Random(seed)
    # BALANCED BLINDING: a pure coin can deal one side every slot (seed 4 did) —
    # half the trials get ours=A, half ours=B (odd one random), then shuffled.
    orders = ["a"] * (trials // 2) + ["b"] * (trials // 2)
    if len(orders) < trials:
        orders.append(rng.choice("ab"))
    rng.shuffle(orders)
    manifest = {"name": name, "seed": seed, "ours": ours, "theirs": theirs,
                "matched_lufs": round(target, 2), "trials": [], "verdicts": {}}
    for i in range(1, trials + 1):
        ours_is_a = orders[i - 1] == "a"
        for slot, tag in (("A", "ours" if ours_is_a else "theirs"),
                          ("B", "theirs" if ours_is_a else "ours")):
            dst = os.path.join(d, f"trial{i}_{slot}.wav")
            subprocess.run(["cp", matched[tag], dst], check=True)
        manifest["trials"].append({"i": i, "ours_is": "a" if ours_is_a else "b"})
    json.dump(manifest, open(os.path.join(d, "manifest.json"), "w"), indent=1)
    print(f"[ab] round '{name}': {trials} sealed trials in eval/ab/{name}/ — "
          f"play trialN_A vs trialN_B cold, then: ab_harness.py verdict {name} N a|b")


def verdict(name, trial, pick, note=""):
    d = os.path.join(ABDIR, name)
    m = json.load(open(os.path.join(d, "manifest.json")))
    m["verdicts"][str(trial)] = {"pick": pick.lower(), "note": note}
    json.dump(m, open(os.path.join(d, "manifest.json"), "w"), indent=1)
    print(f"[ab] {name} trial {trial}: picked {pick.upper()}")


def score(name):
    d = os.path.join(ABDIR, name)
    m = json.load(open(os.path.join(d, "manifest.json")))
    wins = tot = 0
    for t in m["trials"]:
        v = m["verdicts"].get(str(t["i"]))
        if not v:
            continue
        tot += 1
        ours_won = v["pick"] == t["ours_is"]
        wins += ours_won
        print(f"  trial {t['i']}: ours was {t['ours_is'].upper()} — "
              f"{'OURS' if ours_won else 'THEIRS'} picked"
              + (f"  ({v['note']})" if v.get("note") else ""))
    if tot:
        print(f"[ab] SCORE '{name}': ours {wins}/{tot} ({wins/tot*100:.0f}%) "
              f"at matched {m['matched_lufs']} LUFS")
    else:
        print("[ab] no verdicts recorded yet")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("name"); b.add_argument("ours")
    b.add_argument("theirs"); b.add_argument("--seed", type=int, default=1)
    b.add_argument("--trials", type=int, default=3)
    v = sub.add_parser("verdict"); v.add_argument("name"); v.add_argument("trial", type=int)
    v.add_argument("pick", choices=["a", "b", "A", "B"]); v.add_argument("note", nargs="?", default="")
    s = sub.add_parser("score"); s.add_argument("name")
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.name, os.path.abspath(a.ours), os.path.abspath(a.theirs), a.seed, a.trials)
    elif a.cmd == "verdict":
        verdict(a.name, a.trial, a.pick, a.note)
    else:
        score(a.name)


if __name__ == "__main__":
    main()
