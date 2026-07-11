#!/usr/bin/env python3
"""CRATE SEEDS — the loop generator's shopfront.

The crate (songs/crate/) is the browser rail's loop shelf: drag a card onto a
lane and it lands at the drop bar. A fresh box shipped it EMPTY. This seeds it
with flagship-genre loops straight from the KG DNA (loop_gen, fixed seeds —
regeneration is byte-idempotent), so the stranger's first Files-panel glance
shows MUSIC, not a void.

  python3 tools/crate_seed.py            # (re)generate the seed crate
  python3 tools/crate_seed.py --verify   # + engine-parse every file (m1) and
                                         #   fully render one (real audio proof)

Files are named <genre>_<seed>.json — the stem is the card label in the rail.
"""
import json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
CRATE = os.path.join(ROOT, "songs", "crate")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")

# flagship shelf: broad coverage, fixed seeds = reproducible shopfront
SHELF = [("house", 101), ("techno", 102), ("trap", 103), ("dnb", 104),
         ("ukgarage", 105), ("ambient", 106), ("boombap", 107), ("amapiano", 108)]

def seed():
    import loop_gen
    os.makedirs(CRATE, exist_ok=True)
    made = []
    for genre, sd in SHELF:
        tmp = f"_crate_{genre}"
        out, msg = loop_gen.generate(genre, tmp, 4, sd, None, None)
        if out is None:
            print(f"SKIP {genre}: {msg[:80]}")
            continue
        dst = os.path.join(CRATE, f"{genre}_{sd}.json")
        shutil.move(out, dst)
        made.append(dst)
        print(f"crate <- {os.path.basename(dst)}  ({msg.split('(')[0].strip()})")
    return made

def verify(files):
    bad = 0
    for f in files:
        r = subprocess.run([M1, "list-params", f], capture_output=True, text=True, timeout=120)
        okp = r.returncode == 0 and "PARAMS_JSON" in r.stdout
        print(f"engine-parse {os.path.basename(f)}: {'OK' if okp else 'FAIL'}")
        bad += 0 if okp else 1
    # one full render: the shelf must SOUND, not just parse
    probe = files[0]
    wav = "/tmp/crate_probe.wav"
    r = subprocess.run([M1, "render", probe, wav], capture_output=True, text=True, timeout=300)
    okr = r.returncode == 0 and os.path.exists(wav) and os.path.getsize(wav) > 200000
    print(f"render probe {os.path.basename(probe)}: {'OK' if okr else 'FAIL'} "
          f"({os.path.getsize(wav) if os.path.exists(wav) else 0} bytes)")
    os.path.exists(wav) and os.remove(wav)
    bad += 0 if okr else 1
    return bad

if __name__ == "__main__":
    made = seed()
    rc = 0
    if "--verify" in sys.argv:
        rc = verify(made)
        # regen determinism: the shopfront is reproducible byte-for-byte
        before = {f: open(f).read() for f in made}
        made2 = seed()
        same = all(open(f).read() == before.get(f) for f in made2)
        print(f"regen determinism: {'OK' if same else 'FAIL'}")
        rc += 0 if same else 1
    print(f"crate: {len(made)} loops seeded{' - VERIFY ' + ('GREEN' if rc == 0 else 'RED') if '--verify' in sys.argv else ''}")
    sys.exit(1 if rc else 0)
