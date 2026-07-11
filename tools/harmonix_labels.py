#!/usr/bin/env python3
"""THE LABEL GRAMMAR — 912 human-labeled pop structures become a prior.

  harmonix_labels.py stats     -> library/benchmarks/harmonix/label_grammar.json
  harmonix_labels.py eval      -> score segment.py's energy-only labeler vs humans

stats: label vocabulary, bigram transitions (what follows what), position
histograms (where in a song each label lives, thirds), mean durations — mined
from the local MIT Harmonix segments. The durable asset: a data-driven prior
any labeler can lean on.

eval: honest scoreboard for the firing-21 heuristic on human ground truth,
using THEIR boundaries (label-assignment quality isolated from boundary
detection). Energy proxy = mel-frame sums; no vocal stems here, so verse/
chorus discrimination is expected to suffer — the point is measuring it.
"""
import collections, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "library", "benchmarks", "harmonix")
SEGS = os.path.join(BENCH, "segments")
MELS = os.path.join(BENCH, "melspecs")

CANON = {  # fold their fine labels into a working vocabulary
    "intro": "intro", "outro": "outro", "verse": "verse", "chorus": "chorus",
    "bridge": "bridge", "break": "break", "breakdown": "break", "drop": "chorus",
    "inst": "inst", "solo": "inst", "instrumental": "inst",
    "prechorus": "build", "pre-chorus": "build", "build": "build", "buildup": "build",
    "transition": "build", "postchorus": "chorus", "post-chorus": "chorus",
    "quiet": "break", "silence": "break", "end": "end",
}


def canon(label):
    l = re.sub(r"[0-9]+$", "", label.strip().lower())
    return CANON.get(l, CANON.get(l.rstrip("s"), l))


def parse(path):
    rows = []
    for line in open(path):
        p = line.split()
        if len(p) >= 2:
            rows.append((float(p[0]), p[1]))
    return rows


def stats():
    vocab = collections.Counter()
    bigram = collections.Counter()
    pos = collections.defaultdict(lambda: [0, 0, 0])       # thirds of the song
    durs = collections.defaultdict(list)
    for f in sorted(os.listdir(SEGS)):
        rows = parse(os.path.join(SEGS, f))
        if len(rows) < 3 or rows[-1][1] != "end":
            continue
        total = rows[-1][0]
        labs = [(t, canon(l)) for t, l in rows[:-1]]
        for i, (t, l) in enumerate(labs):
            vocab[l] += 1
            end_t = labs[i + 1][0] if i + 1 < len(labs) else total
            durs[l].append(end_t - t)
            if total > 0:
                pos[l][min(2, int(3 * t / total))] += 1
            if i + 1 < len(labs):
                bigram[(l, labs[i + 1][1])] += 1
    top = [l for l, _ in vocab.most_common(12)]
    out = {
        "tracks": 912,
        "vocab": dict(vocab.most_common()),
        "bigrams": {f"{a}>{b}": c for (a, b), c in bigram.most_common(60)},
        "position_thirds": {l: pos[l] for l in top},
        "mean_duration_s": {l: round(sum(d) / len(d), 1) for l, d in durs.items()
                            if len(d) >= 20},
    }
    p = os.path.join(BENCH, "label_grammar.json")
    json.dump(out, open(p, "w"), indent=1)
    print(f"[grammar] {sum(vocab.values())} segments, {len(vocab)} canon labels "
          f"-> {os.path.relpath(p, ROOT)}")
    for l in top[:8]:
        th = pos[l]
        print(f"  {l:8} n={vocab[l]:5}  thirds {th}  mean {out['mean_duration_s'].get(l,'?')}s")
    return out


def eval_labeler(limit=0):
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import numpy as np
    from segment import label_sections
    info = json.load(open(os.path.join(MELS, "info.json")))
    sr, hop = info["SR"], info["HOP_LENGTH"]
    names = sorted(f[:-4] for f in os.listdir(SEGS) if f.endswith(".txt"))
    if limit:
        names = names[:limit]
    OURS2CANON = {"drop": "chorus", "hook": "chorus", "part": None,
                  "intro": "intro", "outro": "outro", "break": "break",
                  "build": "build", "verse": "verse"}
    match = total = labeled = 0
    per = collections.Counter()
    for name in names:
        mp = os.path.join(MELS, f"{name}-mel.npy")
        if not os.path.exists(mp):
            continue
        rows = parse(os.path.join(SEGS, f"{name}.txt"))
        if len(rows) < 4 or rows[-1][1] != "end":
            continue
        mel = np.load(mp)
        if mel.shape[0] > mel.shape[1]:
            mel = mel.T
        env = mel.sum(axis=0)                              # energy proxy per frame
        fps = sr / hop
        bounds = [t for t, _ in rows[1:-1]]
        # label_sections expects audio; the mel-energy envelope AT fps "sample rate"
        # is a faithful RMS proxy for its energy features
        labs = label_sections(env.astype(float), fps, bounds)
        truth = [canon(l) for _, l in rows[:-1]]
        for got, tr in zip(labs, truth):
            got_c = OURS2CANON.get(re.sub(r" \d+$", "", got), None)
            total += 1
            if got_c is None:
                continue
            labeled += 1
            if got_c == tr:
                match += 1
                per[tr] += 1
    print(f"[eval] segments {total} | our labeler committed on {labeled} "
          f"({labeled/max(total,1):.0%}) | correct {match}/{labeled} "
          f"({match/max(labeled,1):.0%} of committed, {match/max(total,1):.0%} overall)")
    print("[eval] correct by class:", dict(per))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "stats":
        stats()
    else:
        eval_labeler(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
