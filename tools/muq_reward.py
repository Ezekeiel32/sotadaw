#!/usr/bin/env python3
"""THE MuQ REWARD — wave 96 (r-19 item 024): a PERSONALIZED quality
head on MuQ embeddings (OpenMuQ/MuQ-large-msd-iter, loaded + proven
on this box), trained from the user's OWN accept/reject telemetry.

THE DATA LAW: accepted takes' audio lives (accepts become the base);
rejected takes' audio used to DIE at the verdict — the w96 retention
hook (sidecar) now banks the last 40 reject wavs into
telemetry/rejects/. The head trains the moment >=15 true negatives
exist; until then `status` says exactly how far the dataset is.

  embed <wav>      mean-pooled MuQ vector (1024-d)
  train            accepts (telemetry->songs/*.wav) vs rejects
                   (telemetry/rejects/*.wav) -> library/muq_head.json
                   (pure-numpy logistic regression — no sklearn)
  score <wav>      the personalized preference 0..1
  status           dataset counts + readiness

TRIPWIRE LAW inherited from 217: the score is a line, never a target.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD = os.path.join(ROOT, "library", "muq_head.json")
REJ_DIR = os.path.join(ROOT, "telemetry", "rejects")
MIN_NEG = 15


def _model():
    import torch
    from muq import MuQ
    m = MuQ.from_pretrained("OpenMuQ/MuQ-large-msd-iter")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    return m.to(dev).eval(), dev


def embed(wav, _cache={}):
    """Mean-pooled MuQ embedding over up to 3 x 10s windows (24kHz)."""
    import torch
    import librosa
    if "m" not in _cache:
        _cache["m"], _cache["dev"] = _model()
    m, dev = _cache["m"], _cache["dev"]
    try:
        dur = librosa.get_duration(path=wav)
    except Exception:
        return None
    vecs = []
    for frac in (0.2, 0.5, 0.8):
        off = max((dur - 10.0) * frac, 0.0)
        try:
            x, _ = librosa.load(wav, sr=24000, mono=True, offset=off,
                                duration=10.0)
        except Exception:
            continue
        if x.size < 24000 or float(np.abs(x).max()) < 1e-5:
            continue
        with torch.no_grad():
            t = torch.tensor(x[None, :], device=dev)
            h = m(t).last_hidden_state.mean(dim=1)[0].cpu().numpy()
        vecs.append(h)
    if not vecs:
        return None
    v = np.mean(vecs, axis=0)
    return v / (np.linalg.norm(v) + 1e-9)


def _dataset():
    accepts, rejects = [], []
    tj = os.path.join(ROOT, "telemetry", "proposals.jsonl")
    if os.path.exists(tj):
        for line in open(tj):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("accepted") is True:
                p = os.path.join(ROOT, "songs", f"{r.get('song')}.wav")
                if os.path.exists(p):
                    accepts.append(p)
    if os.path.isdir(REJ_DIR):
        rejects = [os.path.join(REJ_DIR, f) for f in os.listdir(REJ_DIR)
                   if f.endswith(".wav")]
    return sorted(set(accepts)), sorted(rejects)


def status():
    a, r = _dataset()
    ready = len(r) >= MIN_NEG and len(a) >= MIN_NEG
    return {"accept_wavs": len(a), "reject_wavs": len(r),
            "min_needed": MIN_NEG, "ready": ready,
            "note": ("train now" if ready else
                     f"the retention hook banks reject audio as verdicts "
                     f"land — {max(MIN_NEG - len(r), 0)} more rejects "
                     "until the head can train honestly")}


def train():
    a_paths, r_paths = _dataset()
    if len(r_paths) < MIN_NEG or len(a_paths) < MIN_NEG:
        print(json.dumps(status(), indent=1))
        return 1
    X, y = [], []
    for p in a_paths[-60:]:
        v = embed(p)
        if v is not None:
            X.append(v)
            y.append(1.0)
    for p in r_paths:
        v = embed(p)
        if v is not None:
            X.append(v)
            y.append(0.0)
    X = np.array(X)
    y = np.array(y)
    w = np.zeros(X.shape[1])
    b = 0.0
    lr, lam = 0.5, 1e-3
    for _ in range(400):
        z = X @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        g = X.T @ (p - y) / len(y) + lam * w
        w -= lr * g
        b -= lr * float(np.mean(p - y))
    acc = float(((1 / (1 + np.exp(-(X @ w + b))) > 0.5) == (y > 0.5))
                .mean())
    json.dump({"w": w.tolist(), "b": b, "train_acc": round(acc, 3),
               "n_pos": int(y.sum()), "n_neg": int(len(y) - y.sum()),
               "law": "a LINE, never a target (item 217's law rides)"},
              open(HEAD, "w"))
    print(f"[muq_head] trained on {int(y.sum())}+/"
          f"{int(len(y) - y.sum())}- (train acc {acc:.2f}) -> {HEAD}")
    return 0


def score(wav):
    if not os.path.exists(HEAD):
        return {"ok": True, "skipped": "no head trained yet "
                                       "(muq_reward.py status)"}
    h = json.load(open(HEAD))
    v = embed(wav)
    if v is None:
        return {"ok": True, "skipped": "unreadable audio"}
    z = float(np.dot(np.array(h["w"]), v) + h["b"])
    p = 1.0 / (1.0 + np.exp(-z))
    return {"preference": round(p, 3),
            "note": "personalized (this user's accepts vs rejects); "
                    "a line, never a target"}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        print(json.dumps(status(), indent=1))
    elif cmd == "train":
        sys.exit(train())
    elif cmd == "embed":
        v = embed(sys.argv[2])
        print("none" if v is None else f"{v.shape} norm "
                                       f"{float(np.linalg.norm(v)):.3f}")
    elif cmd == "score":
        print(json.dumps(score(sys.argv[2]), indent=1))
