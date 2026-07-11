#!/usr/bin/env python3
"""semantic_battery.py — the SEMANTIC EARS (V53) regression net.

Proves that CLAP text->audio search finds the RIGHT sound in the user's own
kit corpus. Self-contained: embeds one representative per kit category in
memory (no temp files) and asserts each natural query ranks its expected
family top-1. Family-tolerant (a "kick" may land on any drum kit). A null
(gibberish) query must score below the real queries' average — semantic, not
lexical.

  semantic_battery.py            # core: in-memory kit-category ranking
  semantic_battery.py --e2e      # + exercise clap_query.py on the real index

GUARDIAN-SAFE: if CLAP (torch/transformers/librosa or the checkpoint) is
absent, prints SKIP and exits 0 — semantic search degrades to substring, so
its battery must never redden a box without the model.

Exit code IS the verdict (0 = pass, 1 = regression).
"""
import argparse
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

# (query, {acceptable kit categories}) — family-tolerant, top-1 must land inside
CASES = [
    ("a warm mellow synth pad",        {"warmpad"}),
    ("a punchy kick drum",             {"sota_drums", "gm_drums", "wadddlllttt3_drums"}),
    ("a deep sub bass",                {"sota_bass", "pluckbass"}),
    ("angelic choir vocals",           {"choir"}),
    ("a grand piano melody",           {"piano", "epiano", "sota_keys"}),
    ("lush bowed strings",             {"strings"}),
    ("an electric rhodes keyboard",    {"epiano", "sota_keys", "piano"}),
    ("a plucked bass synth",           {"pluckbass", "sota_bass"}),
]
BAR = 6            # >= this many of len(CASES) must hit
NULL_QUERY = "xqzptl wuuu blaaargh 9931 zzt"


def _reps():
    """One representative wav per FOUNDATION kit category (deterministic:
    first sorted). The universe is corpus-shape-independent: scratch dirs
    ('_'-prefixed probe/AB/diag kits) and per-song IMPORT derivatives (kit.json
    carries source: songs/<x>_stems/... — stems_import's provenance stamp) are
    excluded, because a real imported sub-bass stem legitimately outranks a
    synthesized foundation voice for 'a deep sub bass' and every import would
    redden this net. The --e2e leg still exercises the REAL index, imports
    included."""
    reps = []
    for kd in sorted(glob.glob(os.path.join(ROOT, "kits", "*"))):
        if not os.path.isdir(kd) or os.path.basename(kd).startswith("_"):
            continue
        try:
            src = str(json.load(open(os.path.join(kd, "kit.json"))).get("source", ""))
            if src.replace("\\", "/").startswith("songs/"):
                continue                       # import derivative, not foundation
        except Exception:
            pass                               # no/garbled kit.json -> foundation
        wavs = sorted(glob.glob(os.path.join(kd, "*.wav")))
        if wavs:
            reps.append((os.path.basename(kd), wavs[0]))
    return reps


def core():
    import numpy as np
    import clap_embed
    reps = _reps()
    if len(reps) < 4:
        print("SKIP: too few kit categories to test")
        return 0
    cats = [c for c, _ in reps]
    A = clap_embed.embed_audio([p for _, p in reps])          # (C, 512)
    queries = [q for q, _ in CASES] + [NULL_QUERY]
    T = clap_embed.embed_texts(queries)
    real_tops = []
    hits = 0
    print(f"  index: {len(cats)} kit categories  (device={clap_embed._state['device']})")
    for i, (q, want) in enumerate(CASES):
        s = A @ T[i]
        j = int(np.argmax(s))
        real_tops.append(float(s[j]))
        ok = cats[j] in want
        hits += ok
        print(f"  {'OK ' if ok else 'XX '}{q!r:42s} -> {cats[j]} ({s[j]:.2f})")
    # null: gibberish top-score must be below the real queries' average
    sg = A @ T[-1]
    null_top = float(sg.max())
    real_avg = sum(real_tops) / len(real_tops)
    null_ok = null_top < real_avg
    print(f"  {'OK ' if null_ok else 'XX '}NULL {NULL_QUERY!r} top={null_top:.2f} "
          f"< real-avg {real_avg:.2f}")
    passed = (hits >= BAR) and null_ok
    print(f"  category hits: {hits}/{len(CASES)} (bar {BAR}); null {'ok' if null_ok else 'FAIL'}")
    return 0 if passed else 1


def e2e():
    """Exercise the real CLI path search_library uses (clap_query.py + index)."""
    idx = os.path.join(ROOT, "library", "embeddings.npz")
    if not os.path.exists(idx):
        print("  e2e SKIP: no library/embeddings.npz (run tools/embed_library.py)")
        return 0
    checks = [("a dusty lo-fi snare", {"sota_drums", "gm_drums"}),
              ("a warm analog pad", {"warmpad"})]
    fails = 0
    for q, want in checks:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "clap_query.py"),
                            q, "--k", "3", "--kinds", "kit"],
                           capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except Exception:
            print(f"  e2e XX {q!r}: bad JSON / rc={r.returncode}")
            fails += 1
            continue
        cats = {res.get("category") for res in d.get("results", [])}
        ok = bool(cats & want)
        fails += not ok
        print(f"  e2e {'OK ' if ok else 'XX '}{q!r} -> {sorted(cats)}")
    # AUDIO -> neighbors (the reference-match axis): a choir sample finds choir,
    # and the query file itself is excluded from its own results.
    cho = sorted(glob.glob(os.path.join(ROOT, "kits", "choir", "*.wav")))
    if cho:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "clap_query.py"),
                            "--audio", cho[0], "--k", "3", "--kinds", "kit"],
                           capture_output=True, text=True)
        cats, paths = set(), set()
        try:
            d = json.loads(r.stdout)
            cats = {x.get("category") for x in d.get("results", [])}
            paths = {x.get("path") for x in d.get("results", [])}
        except Exception:
            pass
        ok = ("choir" in cats) and (cho[0] not in paths)
        fails += not ok
        print(f"  e2e {'OK ' if ok else 'XX '}audio->neighbors(choir) -> {sorted(cats)}")
    return 1 if fails else 0


def sim_cli():
    """The --sim contract the eval judge parses (C5 s5): one subprocess, scores
    ride INPUT ORDER, floats, and the matching sound wins the text. Text mirrors
    a proven core CASE — CLAP is text-sensitive ('choir singing' scores the same
    sustained choir one-shot 0.15 vs 0.45; the check is the CLI, not the prompt)."""
    drum = sorted(glob.glob(os.path.join(ROOT, "kits", "sota_drums", "*.wav"))) \
        or sorted(glob.glob(os.path.join(ROOT, "kits", "gm_drums", "*.wav")))
    cho = sorted(glob.glob(os.path.join(ROOT, "kits", "choir", "*.wav")))
    if not (drum and cho):
        print("  sim SKIP: need a drum + a choir kit wav")
        return 0
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "clap_query.py"),
                        "--sim", "angelic choir vocals", "--audio", drum[0], cho[0]],
                       capture_output=True, text=True)
    s = None
    try:
        d = json.loads(r.stdout)
        s = [x["score"] for x in d["similarities"]]
        ok = (d.get("available") and len(s) == 2
              and all(isinstance(v, float) for v in s) and s[1] > s[0])
    except Exception:
        ok = False
    print(f"  {'OK ' if ok else 'XX '}--sim 'angelic choir vocals' [drum, choir] -> "
          f"{s if s is not None else r.stdout[:80]} (choir must win, input order)")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e2e", action="store_true")
    a = ap.parse_args()
    import clap_embed
    if not clap_embed.available():
        print("SKIP: CLAP unavailable (torch/transformers/librosa or checkpoint absent)")
        return 0
    print("== SEMANTIC EARS BATTERY ==")
    rc = core()
    rc = max(rc, sim_cli())
    if a.e2e:
        rc = max(rc, e2e())
    print("PASS" if rc == 0 else "REGRESSION")
    return rc


if __name__ == "__main__":
    sys.exit(main())
