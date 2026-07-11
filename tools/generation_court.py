#!/usr/bin/env python3
"""THE GENERATION COURT (W46) — engine_null_ci's pattern for the SYMBOLIC
layer. Every loop_gen/arrange output is seeded and deterministic, so a
(genre, seed) pair regenerates BYTE-EXACT: the court seals canonical-JSON
sha256s for an 18-genre panel and any future silent behavior change in the
composition stack (waves W14-W45 and beyond) turns the check RED.

  generation_court.py seal        # (re)write eval/generation_court.json
  generation_court.py check       # regenerate + compare (suite leg)
  generation_court.py --selftest  # prove the court catches a planted change

Reseal ritual: an INTENDED wave changes outputs -> run `seal` in the same
commit and say why in the message (the null-court law). A check that goes
red without a reseal is a regression, full stop.
"""
import hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
GOLD = os.path.join(ROOT, "eval", "generation_court.json")
PANEL = [("trap", 11), ("house", 23), ("synthwave", 42), ("gospel", 13),
         ("dnb", 7), ("funk", 29), ("jazz", 5), ("reggae", 5),
         ("bossanova", 5), ("afrobeat", 5), ("ambient", 5), ("citypop", 5),
         ("techno", 5), ("dubstep", 5), ("drill", 5), ("breakcore", 5),
         ("doom_metal", 5), ("amapiano", 5)]


def canon(path):
    """canonical sha256 of a song json (volatile fields stripped)"""
    s = json.load(open(path))
    s.pop("comment", None)
    return hashlib.sha256(
        json.dumps(s, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def gen_pair(genre, seed, env=None):
    name = f"_court_{genre}"
    e = dict(os.environ)
    if env:
        e.update(env)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "loop_gen.py"),
                    genre, name, "--bars", "4", "--seed", str(seed)],
                   check=True, capture_output=True, cwd=ROOT, env=e, timeout=120)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "arrange.py"),
                    os.path.join(SONGS, name + ".json")],
                   check=True, capture_output=True, cwd=ROOT, env=e, timeout=120)
    h = {"loop": canon(os.path.join(SONGS, name + ".json")),
         "full": canon(os.path.join(SONGS, name + "_full.json"))}
    for suf in (".json", "_full.json"):
        os.remove(os.path.join(SONGS, name + suf))
    return h


def seal():
    gold = {f"{g}:{s}": gen_pair(g, s) for g, s in PANEL}
    os.makedirs(os.path.dirname(GOLD), exist_ok=True)
    json.dump(gold, open(GOLD, "w"), indent=1)
    print(f"sealed {len(gold)} pairs -> {GOLD}")
    return 0


def check(env=None, quiet=False):
    if not os.path.exists(GOLD):
        print("no gold seal — run `generation_court.py seal` first")
        return 1
    gold = json.load(open(GOLD))
    bad = []
    for g, s in PANEL:
        key = f"{g}:{s}"
        if key not in gold:
            bad.append((key, "missing from seal"))
            continue
        h = gen_pair(g, s, env)
        for layer in ("loop", "full"):
            if h[layer] != gold[key][layer]:
                bad.append((key, f"{layer} diverged"))
    if not quiet:
        for k, why in bad:
            print(f"  XX {k}: {why}")
        print(f"generation court: {'ALL SEALED (' + str(len(gold)) + ' pairs)' if not bad else 'RED ' + str(len(bad))}")
    return 1 if bad else 0


def selftest():
    """the court must catch a planted change: one flag off diverges the full"""
    rc_clean = check(quiet=True)
    if rc_clean != 0:
        print("selftest needs a green court first (reseal after intended waves)")
        return 1
    rc_planted = check(env={"SOTADAW_COUNTER": "0"}, quiet=True)
    ok = rc_planted != 0
    print(f"selftest: clean check green + planted flag caught -> "
          f"{'CLEAN' if ok else 'RED (planted change NOT caught)'}")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "seal":
        sys.exit(seal())
    if a and a[0] == "--selftest":
        sys.exit(selftest())
    sys.exit(check())
