#!/usr/bin/env python3
"""THE CANARY CORPUS — wave 72 (r-32 item 048): SEAL/CHECK for the
END-TO-END generation path (generate -> arrange -> RENDER), extending
the two standing courts one seam deeper:

  generation_court (W46)  seals the SYMBOLIC layer (song.json hashes)
  engine_null_ci   (A7)   seals the ENGINE on a fixed corpus
  THIS              seals GENERATED songs' RENDERS — a silent change
                    anywhere in loop_gen/arrange/voices/fx/engine
                    turns the check red

One resolver each: songs come from generation_court.gen-style calls,
the null compare is engine_null_ci._residual_dbfs verbatim.

  canary_corpus.py seal        (re)render the panel into eval/canary/
  canary_corpus.py check       regenerate + re-render + null vs gold
  canary_corpus.py --selftest  a planted gain change turns it red

Reseal ritual = generation_court's: an INTENDED sound change reseals
in the same commit and says why.
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs")
CANARY = os.path.join(ROOT, "eval", "canary")
MANIFEST = os.path.join(CANARY, "manifest.json")
M1 = os.path.join(ROOT, "app", "build", "m1_artefacts", "Release", "m1")
sys.path.insert(0, os.path.join(ROOT, "tools"))

# small on purpose: renders cost minutes; the symbolic court covers 18
PANEL = [("trap", 11), ("house", 23), ("jazz", 5), ("ambient", 5)]
NULL_FLOOR_DB = -60.0


def _gen(genre, seed, keep_as):
    name = f"_canary_{genre}"
    subprocess.run([sys.executable, os.path.join(ROOT, "tools",
                                                 "loop_gen.py"),
                    genre, name, "--bars", "4", "--seed", str(seed)],
                   check=True, capture_output=True, cwd=ROOT, timeout=120)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools",
                                                 "arrange.py"),
                    os.path.join(SONGS, name + ".json")],
                   check=True, capture_output=True, cwd=ROOT, timeout=120)
    full = os.path.join(SONGS, name + "_full.json")
    shutil.move(full, keep_as)
    os.remove(os.path.join(SONGS, name + ".json"))
    return keep_as


def _render(song_json, out_wav):
    r = subprocess.run([M1, "render", song_json, out_wav],
                       capture_output=True, text=True, timeout=1200)
    if r.returncode != 0 or not os.path.exists(out_wav):
        raise RuntimeError((r.stdout + r.stderr)[-300:])


def seal():
    os.makedirs(CANARY, exist_ok=True)
    man = {}
    for genre, sd in PANEL:
        sj = os.path.join(SONGS, f"_canary_{genre}_gold.json")
        _gen(genre, sd, sj)
        wav = os.path.join(CANARY, f"{genre}_{sd}.wav")
        _render(sj, wav)
        os.remove(sj)
        man[f"{genre}:{sd}"] = os.path.basename(wav)
    json.dump(man, open(MANIFEST, "w"), indent=1)
    print(f"[canary] sealed {len(man)} end-to-end renders -> {CANARY}")
    return 0


def check():
    import engine_null_ci as ENC
    if not os.path.exists(MANIFEST):
        print("canary: no seal — run `canary_corpus.py seal` first")
        return 1
    man = json.load(open(MANIFEST))
    fails = []
    for key, wav_name in man.items():
        genre, sd = key.split(":")
        gold = os.path.join(CANARY, wav_name)
        sj = os.path.join(SONGS, f"_canary_{genre}_chk.json")
        fresh = os.path.join(CANARY, f"_chk_{genre}.wav")
        try:
            _gen(genre, int(sd), sj)
            _render(sj, fresh)
            resid = ENC._residual_dbfs(gold, fresh)
            resid = float(resid[0] if isinstance(resid, (tuple, list))
                          else resid)
            ok = resid <= NULL_FLOOR_DB
            print(f"[{'PASS' if ok else 'FAIL'}] {key}: residual "
                  f"{resid:.1f} dBFS (floor {NULL_FLOOR_DB})")
            if not ok:
                fails.append(key)
        except Exception as e:
            print(f"[FAIL] {key}: {e}")
            fails.append(key)
        finally:
            for p in (sj, fresh):
                if os.path.exists(p):
                    os.remove(p)
    if fails:
        print(f"canary: {len(fails)} RED — {fails} (an intended sound "
              "change reseals IN THE SAME COMMIT and says why)")
        return 1
    print(f"canary: ALL NULL ({len(man)} end-to-end renders)")
    return 0


def selftest():
    """The court must CATCH: a planted +1dB gain on a regenerated take
    must breach the null floor."""
    import engine_null_ci as ENC
    genre, sd = PANEL[0]
    sj = os.path.join(SONGS, f"_canary_{genre}_st.json")
    a = os.path.join(CANARY, "_st_a.wav")
    b = os.path.join(CANARY, "_st_b.wav")
    os.makedirs(CANARY, exist_ok=True)
    try:
        _gen(genre, sd, sj)
        _render(sj, a)
        doc = json.load(open(sj))
        doc["tracks"][0]["gainDb"] = float(
            doc["tracks"][0].get("gainDb", 0) or 0) + 1.0
        json.dump(doc, open(sj, "w"))
        _render(sj, b)
        def _r(x, y):
            v = ENC._residual_dbfs(x, y)
            return float(v[0] if isinstance(v, (tuple, list)) else v)
        clean = _r(a, a)
        planted = _r(a, b)
        okc = clean <= NULL_FLOOR_DB
        okp = planted > NULL_FLOOR_DB
        print(f"[{'PASS' if okc else 'FAIL'}] identity nulls "
              f"({clean:.1f} dBFS)")
        print(f"[{'PASS' if okp else 'FAIL'}] planted +1dB caught "
              f"({planted:.1f} dBFS)")
        return 0 if (okc and okp) else 1
    finally:
        for p in (sj, a, b):
            if os.path.exists(p):
                os.remove(p)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "seal":
        sys.exit(seal())
    if cmd == "--selftest":
        sys.exit(selftest())
    sys.exit(check())
