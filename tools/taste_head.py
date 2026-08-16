#!/usr/bin/env python3
"""THE BRAIN BR-C — THE TASTE HEAD (docs/SPEC_THE_BRAIN.md PART II B3).

Chezy's taste, learned: rendered take -> CLAP embedding -> tiny logistic
head -> personal score. RELEASE GATE G3's organ.

THE EMBED-AT-VERDICT LAW (measured 2026-07-16: only 7 of 122 verdict wavs
still exist — props are swept after verdicts): the embedding is banked the
moment the verdict lands, by a fire-and-forget subprocess off the verdict
path (`embed-verdict` subcommand; the sidecar Popens it, KG-crank pattern).
telemetry/clap_bank.jsonl = {t, song, accepted, note, dim, emb[512]}.

SMALL-DATA HONESTY (122 verdicts = 111 accept / 11 reject today):
- train() refuses under MIN_ROWS total or MIN_MINORITY per class — an
  under-fed head is a lie with a confidence interval.
- Evaluation is leave-one-out CV, reported as balanced accuracy (the 91%
  majority class makes raw accuracy meaningless).
- FLOOR LAW: the head persists ONLY if LOO balanced accuracy beats both the
  majority baseline (0.5 balanced) and the nearest-centroid cold floor.
- Head is pure numpy logistic regression + L2; hundreds of params, no torch
  at train/score time (CLAP itself is the only heavy piece, embed-time only).

PRIVACY LAW: telemetry/ is git-ignored and the head never ships in public
builds; G3 degrades to the cold floor for strangers.
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

BANK_NAME = "clap_bank.jsonl"
HEAD_NAME = "taste_head.json"
MIN_ROWS = 24
MIN_MINORITY = 6


def bank_path(root=None):
    return os.path.join(root or DEF_ROOT, "telemetry", BANK_NAME)


def head_path(root=None):
    return os.path.join(root or DEF_ROOT, "telemetry", HEAD_NAME)


def bank_rows(root=None):
    out = []
    try:
        for ln in open(bank_path(root)):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except json.JSONDecodeError:
                continue
            if isinstance(r.get("emb"), list) and r.get("accepted") is not None:
                out.append(r)
    except OSError:
        pass
    return out


def bank_append(song, accepted, emb, note="", root=None, t=None):
    try:
        row = {"t": round(float(time.time() if t is None else t), 1),
               "song": str(song), "accepted": bool(accepted),
               "note": str(note or "")[:200], "dim": len(emb),
               "emb": [round(float(x), 6) for x in emb]}
        p = bank_path(root)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a") as f:
            f.write(json.dumps(row) + "\n")
        return True
    except Exception:
        return False


# ---------------------------------------------------------------- math (numpy)
def _xy(rows):
    import numpy as np
    dim = max(len(r["emb"]) for r in rows)
    X = np.zeros((len(rows), dim), dtype=np.float64)
    y = np.zeros(len(rows), dtype=np.float64)
    for i, r in enumerate(rows):
        e = np.asarray(r["emb"], dtype=np.float64)
        n = np.linalg.norm(e)
        X[i, :len(e)] = e / n if n > 0 else e
        y[i] = 1.0 if r["accepted"] else 0.0
    return X, y


def _fit_logistic(X, y, l2=1.0, iters=300, lr=0.5):
    """Balanced-weighted logistic regression, plain gradient descent.
    Deterministic (zero init). Returns (w, b)."""
    import numpy as np
    n, d = X.shape
    pos = max(y.sum(), 1.0)
    neg = max(n - y.sum(), 1.0)
    sw = np.where(y > 0.5, n / (2.0 * pos), n / (2.0 * neg))
    w = np.zeros(d)
    b = 0.0
    for _ in range(iters):
        z = X @ w + b
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))
        g = (p - y) * sw
        gw = X.T @ g / n + l2 * w / n
        gb = g.mean()
        w -= lr * gw
        b -= lr * gb
    return w, b


def _balanced_acc(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t > 0.5 and p > 0.5)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t <= 0.5 and p <= 0.5)
    npos = max(sum(1 for t in y_true if t > 0.5), 1)
    nneg = max(sum(1 for t in y_true if t <= 0.5), 1)
    return 0.5 * (tp / npos + tn / nneg)


def cold_floor_eval(X, y):
    """Nearest-centroid cold floor, leave-one-out: score = which class
    centroid (computed WITHOUT the held-out row) is closer."""
    import numpy as np
    preds = []
    for i in range(len(y)):
        m = np.ones(len(y), dtype=bool)
        m[i] = False
        Xa, ya = X[m], y[m]
        if ya.sum() < 1 or (len(ya) - ya.sum()) < 1:
            preds.append(1.0)
            continue
        ca = Xa[ya > 0.5].mean(axis=0)
        cr = Xa[ya <= 0.5].mean(axis=0)
        preds.append(1.0 if np.linalg.norm(X[i] - ca) <= np.linalg.norm(X[i] - cr)
                     else 0.0)
    return _balanced_acc(y, preds)


def loo_eval(X, y, l2=1.0):
    preds = []
    for i in range(len(y)):
        import numpy as np
        m = np.ones(len(y), dtype=bool)
        m[i] = False
        w, b = _fit_logistic(X[m], y[m], l2=l2)
        z = float(X[i] @ w + b)
        preds.append(1.0 if z > 0.0 else 0.0)
    return _balanced_acc(y, preds)


def train(root=None, l2=1.0):
    """LEDGER-LAW gate + LOO floors + persist-if-better. Returns a report dict
    (never raises): {"trained": bool, "why"/metrics...}."""
    rows = bank_rows(root)
    npos = sum(1 for r in rows if r["accepted"])
    nneg = len(rows) - npos
    rep = {"rows": len(rows), "accepted": npos, "rejected": nneg, "trained": False}
    if len(rows) < MIN_ROWS or min(npos, nneg) < MIN_MINORITY:
        rep["why"] = (f"under-fed: need >={MIN_ROWS} rows and >={MIN_MINORITY} per "
                      f"class (have {npos}/{nneg}) — cold floor stands, the bank grows")
        return rep
    X, y = _xy(rows)
    head_ba = loo_eval(X, y, l2=l2)
    cold_ba = cold_floor_eval(X, y)
    # FLOOR LAW with a SIGNIFICANCE MARGIN (measured: a null fixture — same
    # cloud, both labels — hit LOO 0.6 vs floor 0.567 on n=30 by luck alone;
    # a bare '>' persists noise). One-tailed 95% on the balanced-accuracy
    # binomial sd: the head must beat the floor by more than chance explains.
    sig = 1.645 * 0.25 * math.sqrt(1.0 / npos + 1.0 / nneg)
    rep.update({"loo_balanced_acc": round(head_ba, 4),
                "cold_floor_balanced_acc": round(cold_ba, 4),
                "majority_balanced_acc": 0.5,
                "significance_margin": round(sig, 4)})
    if head_ba <= max(cold_ba, 0.5) + sig:
        rep["why"] = ("FLOOR LAW: head does not beat the cold floor by the "
                      "significance margin — not persisted")
        return rep
    w, b = _fit_logistic(X, y, l2=l2)
    doc = {"t": round(time.time(), 1), "dim": int(X.shape[1]), "l2": l2,
           "rows": len(rows), "accepted": npos, "rejected": nneg,
           "loo_balanced_acc": round(head_ba, 4),
           "cold_floor_balanced_acc": round(cold_ba, 4),
           "w": [round(float(x), 8) for x in w], "b": round(float(b), 8)}
    p = head_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f)
    os.replace(tmp, p)
    rep["trained"] = True
    return rep


def score_emb(emb, root=None):
    """(p_accept, source) — the head when one is persisted, else the cold
    centroid floor, else (None, 'no-data'): an honest miss, never a guess."""
    try:
        import numpy as np
        e = np.asarray(emb, dtype=np.float64)
        n = np.linalg.norm(e)
        if n > 0:
            e = e / n
        try:
            h = json.load(open(head_path(root)))
            w = np.asarray(h["w"], dtype=np.float64)
            if len(e) < len(w):
                e = np.pad(e, (0, len(w) - len(e)))
            z = float(e[:len(w)] @ w + h["b"])
            return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z)))), "head"
        except OSError:
            pass
        rows = bank_rows(root)
        pos = [r for r in rows if r["accepted"]]
        neg = [r for r in rows if not r["accepted"]]
        if not pos or not neg:
            return None, "no-data"
        X, y = _xy(rows)
        ca = X[y > 0.5].mean(axis=0)
        cr = X[y <= 0.5].mean(axis=0)
        if len(e) < X.shape[1]:
            e = np.pad(e, (0, X.shape[1] - len(e)))
        da, dr = float(np.linalg.norm(e[:X.shape[1]] - ca)), \
            float(np.linalg.norm(e[:X.shape[1]] - cr))
        return (dr / (da + dr + 1e-12)), "cold-floor"
    except Exception:
        return None, "error"


# ---------------------------------------------------------------- CLI lanes
def _embed_wav(wav):
    """CLAP multiwindow embedding for one wav. None on any unavailability
    (no model cache, no packages) — the caller stays fail-open."""
    try:
        import clap_embed
        if not clap_embed.available(allow_download=False):
            return None
        embs = clap_embed.embed_audio_multiwindow([wav], n=3)
        e = embs[0]
        try:
            e = e.tolist()
        except AttributeError:
            pass
        return list(map(float, e))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description="THE TASTE HEAD (BR-C B3)")
    sub = ap.add_subparsers(dest="cmd")
    ev = sub.add_parser("embed-verdict", help="bank one verdict's embedding (sidecar Popen lane)")
    ev.add_argument("song")
    ev.add_argument("--accepted", required=True, choices=("0", "1"))
    ev.add_argument("--wav", required=True)
    ev.add_argument("--note", default="")
    sub.add_parser("train", help="LOO-evaluated train + floor-law persist")
    sub.add_parser("backfill", help="bank surviving prop wavs with their TRUE "
                                    "labels from telemetry/proposals.jsonl")
    sc = sub.add_parser("score", help="score one wav")
    sc.add_argument("wav")
    sub.add_parser("status", help="bank + head status")
    a = ap.parse_args()
    if a.cmd == "embed-verdict":
        emb = _embed_wav(a.wav)
        if emb is None:
            print("clap unavailable — nothing banked (honest miss)")
            return 0
        ok = bank_append(a.song, a.accepted == "1", emb, note=a.note)
        print("banked" if ok else "bank failed")
        return 0
    if a.cmd == "train":
        print(json.dumps(train(), indent=1))
        return 0
    if a.cmd == "backfill":
        # LABEL TRUTH LAW: only rows whose verdict is RECORDED in
        # proposals.jsonl bank here — never an invented label. Each (song,
        # wav mtime) banks once; re-runs are idempotent.
        seen = {(r["song"], r.get("note", "")) for r in bank_rows()}
        banked = 0
        try:
            rows = [json.loads(ln) for ln in
                    open(os.path.join(DEF_ROOT, "telemetry", "proposals.jsonl"))]
        except OSError:
            rows = []
        latest = {}
        for r in rows:                       # last verdict per song wins
            if isinstance(r.get("accepted"), bool):
                latest[r.get("song")] = r
        for song, r in latest.items():
            wav = os.path.join(DEF_ROOT, "songs", f"_prop_{song}.wav")
            if not os.path.exists(wav):
                continue
            tag = f"backfill:{int(os.path.getmtime(wav))}"
            if (song, tag) in seen:
                continue
            emb = _embed_wav(wav)
            if emb is None:
                print(f"{song}: clap unavailable — stopped")
                break
            bank_append(song, r["accepted"], emb, note=tag)
            banked += 1
            print(f"{song}: banked ({'accept' if r['accepted'] else 'reject'})")
        print(f"backfilled {banked}")
        return 0
    if a.cmd == "score":
        emb = _embed_wav(a.wav)
        if emb is None:
            print("clap unavailable")
            return 1
        p, src = score_emb(emb)
        print(json.dumps({"p_accept": None if p is None else round(p, 4),
                          "source": src}))
        return 0
    rows = bank_rows()
    npos = sum(1 for r in rows if r["accepted"])
    has_head = os.path.exists(head_path())
    print(json.dumps({"banked": len(rows), "accepted": npos,
                      "rejected": len(rows) - npos, "head": has_head,
                      "floors": {"min_rows": MIN_ROWS, "min_minority": MIN_MINORITY}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
