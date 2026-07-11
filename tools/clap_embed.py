#!/usr/bin/env python3
"""clap_embed.py — the CLAP kernel for SEMANTIC EARS (V53).

Loads laion/clap-htsat-unfused through transformers (NO laion_clap package →
zero torch-version conflict with the stems/retune/sing pipelines) and embeds
AUDIO files and TEXT into ONE shared 512-d space, so "a dusty lo-fi snare"
(text) can be ranked against the user's actual samples (audio) by cosine.

Verified on this stack (transformers 5.5.4, 2026-07-07):
  - ClapModel.get_{audio,text}_features(...) returns a BaseModelOutputWithPooling
    whose `.pooler_output` (N, 512) IS the projected joint-space embedding
    (the projection is applied inside the call — do NOT project again).
  - The audio kwarg is `audio=` (5.x renamed it from the deprecated `audios=`).
  - ClapFeatureExtractor wants 48 kHz mono float; librosa loads + resamples.

Laws:
  - CPU by default. GPU only if it reports > ~1.5 GB free (this box's GPU is
    often fully held by another process — never fight it).
  - Graceful: available() is CHEAP (imports + checkpoint cached, no load, no
    network). load() never triggers a multi-GB download unless allow_download.
    Callers that catch ClapUnavailable MUST degrade (semantic → substring),
    never crash the tool.
  - Checkpoint license: laion/clap-htsat-unfused — LAION-CLAP code is Apache-2.0;
    verify the checkpoint's terms before shipping a public build (SPEC §9 gate).

Public API:
  available(allow_download=False) -> bool
  embed_texts(list[str])          -> np.ndarray (N, 512) float32, L2-normalized
  embed_audio(list[path])         -> np.ndarray (N, 512) float32, L2-normalized
                                     (a ZERO row for any unreadable/silent file)
"""
import os
import sys

MODEL_ID = "laion/clap-htsat-unfused"
_SR = 48000
_MAXDUR = 10.0            # CLAP's window; also makes embedding deterministic
_state = {"model": None, "proc": None, "device": None}


class ClapUnavailable(Exception):
    pass


def _model_cached() -> bool:
    """True if the checkpoint is already in the HF cache (no network needed)."""
    import glob
    roots = [os.environ.get("HF_HOME"), os.path.expanduser("~/.cache/huggingface")]
    for r in roots:
        if not r:
            continue
        hub = r if r.rstrip("/").endswith("hub") else os.path.join(r, "hub")
        if glob.glob(os.path.join(hub, "models--laion--clap-htsat-unfused",
                                  "snapshots", "*")):
            return True
    return False


def available(allow_download: bool = False) -> bool:
    try:
        import torch          # noqa: F401
        import transformers   # noqa: F401
        import librosa        # noqa: F401
    except Exception:
        return False
    return True if allow_download else _model_cached()


def _pick_device():
    import torch
    if not torch.cuda.is_available():
        return "cpu"
    try:
        free, _total = torch.cuda.mem_get_info()
        return "cuda" if free > 1_500_000_000 else "cpu"
    except Exception:
        return "cpu"


def load(device: str = None, allow_download: bool = False):
    """Lazy singleton. Returns (model, proc, device) or raises ClapUnavailable."""
    if _state["model"] is not None:
        return _state["model"], _state["proc"], _state["device"]
    if not available(allow_download=allow_download):
        raise ClapUnavailable(
            "CLAP unavailable (need torch+transformers+librosa and the "
            "laion/clap-htsat-unfused checkpoint cached; pass allow_download=True "
            "to fetch it).")
    try:
        import torch
        from transformers import ClapModel, ClapProcessor
        torch.set_num_threads(max(1, min(4, (os.cpu_count() or 4) - 2)))
        dev = device or _pick_device()
        model = ClapModel.from_pretrained(MODEL_ID).to(dev).eval()
        proc = ClapProcessor.from_pretrained(MODEL_ID)
    except Exception as e:
        raise ClapUnavailable(f"CLAP load failed: {e!r}")
    _state.update(model=model, proc=proc, device=dev)
    return model, proc, dev


def _norm(t):
    import torch
    return torch.nn.functional.normalize(t, dim=-1).cpu().numpy().astype("float32")


def embed_texts(texts):
    """Embed a list of text strings → (N, 512) float32, L2-normalized."""
    import numpy as np
    import torch
    model, proc, dev = load()
    out = []
    B = 32
    for i in range(0, len(texts), B):
        chunk = [str(t) for t in texts[i:i + B]]
        inp = proc(text=chunk, return_tensors="pt", padding=True).to(dev)
        with torch.no_grad():
            e = model.get_text_features(**inp).pooler_output
        out.append(_norm(e))
    return np.concatenate(out, 0) if out else np.zeros((0, 512), "float32")


def _load_audio(path):
    import numpy as np
    import librosa
    try:
        a, _ = librosa.load(path, sr=_SR, mono=True, duration=_MAXDUR)
        a = a.astype("float32")
        if a.size == 0 or not np.isfinite(a).all() or float(np.max(np.abs(a))) < 1e-6:
            return None
        return a
    except Exception:
        return None


def _load_audio_at(path, offset_s):
    import numpy as np
    import librosa
    try:
        a, _ = librosa.load(path, sr=_SR, mono=True, offset=max(0.0, offset_s),
                            duration=_MAXDUR)
        a = a.astype("float32")
        if a.size == 0 or not np.isfinite(a).all() or float(np.max(np.abs(a))) < 1e-6:
            return None
        return a
    except Exception:
        return None


def embed_audio_multiwindow(paths, n=3):
    """Embed each file as the L2-renormalized MEAN of n CLAP windows spread
    across its duration (fractions ~0.15/0.45/0.75) → (N, 512) float32.

    embed_audio() hears only the FIRST 10 s (_MAXDUR) — for a full record
    that is the intro, not the record. The A/B real-record ruler (eval R3)
    compares whole songs, so both sides get the same multi-window treatment.
    Unreadable files keep the zero-row law; silent windows are skipped and
    the mean uses whatever windows were audible."""
    import numpy as np
    import librosa
    model, proc, dev = load()
    import torch
    vecs = np.zeros((len(paths), 512), "float32")
    for k, p in enumerate(paths):
        try:
            dur = float(librosa.get_duration(path=p))
        except Exception:
            continue
        span = max(0.0, dur - _MAXDUR)
        offs = [span * f for f in ((0.15, 0.45, 0.75) if n >= 3 else (0.0, 0.5)[:n])]
        if span <= 0.0:
            offs = [0.0]
        arrs = [a for a in (_load_audio_at(p, o) for o in offs) if a is not None]
        if not arrs:
            continue
        inp = proc(audio=arrs, sampling_rate=_SR, return_tensors="pt").to(dev)
        with torch.no_grad():
            e = model.get_audio_features(**inp).pooler_output
        v = _norm(e).mean(axis=0)
        nrm = float(np.linalg.norm(v))
        if nrm > 0:
            vecs[k] = (v / nrm).astype("float32")
    return vecs


def embed_audio(paths):
    """Embed a list of audio file paths → (N, 512) float32, L2-normalized.
    Unreadable/silent files get a ZERO row (they sort last, never crash a run)."""
    import numpy as np
    import torch
    model, proc, dev = load()
    vecs = np.zeros((len(paths), 512), "float32")
    idx, arrs = [], []

    def flush():
        if not arrs:
            return
        inp = proc(audio=list(arrs), sampling_rate=_SR, return_tensors="pt").to(dev)
        with torch.no_grad():
            e = model.get_audio_features(**inp).pooler_output
        v = _norm(e)
        for j, k in enumerate(idx):
            vecs[k] = v[j]
        idx.clear()
        arrs.clear()

    B = 12
    for k, p in enumerate(paths):
        a = _load_audio(p)
        if a is None:
            continue
        idx.append(k)
        arrs.append(a)
        if len(arrs) >= B:
            flush()
    flush()
    return vecs


if __name__ == "__main__":
    # quick self-check: rank a couple of contrasting kit files by a text query
    import glob
    import numpy as np
    if not available():
        print("SKIP: CLAP unavailable (torch/transformers/librosa or checkpoint absent)")
        sys.exit(0)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    picks = []
    for cat in ("warmpad", "sota_drums", "sota_bass", "choir"):
        g = sorted(glob.glob(os.path.join(root, "kits", cat, "*.wav")))
        if g:
            picks.append((cat, g[0]))
    if not picks:
        print("SKIP: no kit audio found")
        sys.exit(0)
    A = embed_audio([p for _, p in picks])
    q = sys.argv[1] if len(sys.argv) > 1 else "a warm mellow synth pad"
    T = embed_texts([q])[0]
    sims = A @ T
    order = np.argsort(-sims)
    print(f"query: {q!r}  (device={_state['device']})")
    for j in order:
        print(f"  {picks[j][0]:12} {sims[j]:.3f}")
