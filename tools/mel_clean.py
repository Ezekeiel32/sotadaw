#!/usr/bin/env python3
"""DRY TRUTH pre-rails — single-stem Mel-Band RoFormer cleaners (#51).

Wet stems LIE to the transcription rails: reverb smears onsets and steals f0
confidence (harvest dropped 1/3 of notes on wet stems — the reason fcpe won),
noise floors eat basic-pitch's frame threshold, breath transcribes as phantom
notes. The UVR/MSST community trained surgical single-target cleaners on the
exact arch we already vendor for vocals (third_party/bs_roformer):

    dereverb    anvuew, SDR 19.17      -> (dry, reverb-tail)
    denoise     aufr33, SDR 27.99      -> (clean, noise)
    aspiration  Sucial, SDR 18.98      -> (breath, tone)   [breath = the target]

THE CLOSURE LAW: target = model(mix); residual = mix - target — the two
outputs re-sum to the input EXACTLY (same law as mss_roformer). Transcribe
the DRY side, keep the wet original for truth decks; the removed tail is
honest material for an fx_reverb estimate, never deleted sound.

GPU-GATED BY DEFAULT: roformer attention is ~unusable-slow on CPU for full
stems (the mss_roformer lesson). available(need_gpu=True) is the wiring
gate — no CUDA (or the card is busy training) means callers keep the wet
path, never a silent 30-minute CPU stall inside an import. --device cpu
exists for offline quality passes and the battery's short clips.

Files land in ~/.cache/sotadaw/mss/ (see MODELS). Kill: SOTADAW_NO_DRYCLEAN=1.
Evidence + provenance: docs/A2M_MAX_RESEARCH.md gap 3.
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSS_DIR = os.environ.get("SOTADAW_MSS_DIR",
                         os.path.expanduser("~/.cache/sotadaw/mss"))

MODELS = {
    "dereverb": {"ckpt": "dereverb_anvuew.ckpt", "bytes": 913107578,
                 "yaml": "dereverb_anvuew.yaml", "target": "dry",
                 "residual": "reverb"},
    "denoise": {"ckpt": "denoise_aufr33.ckpt", "bytes": 913097300,
                "yaml": "denoise_aufr33.yaml", "target": "clean",
                "residual": "noise"},
    "aspiration": {"ckpt": "aspiration_sucial.ckpt", "bytes": 835983746,
                   "yaml": "aspiration_sucial.yaml", "target": "breath",
                   "residual": "tone"},
}

_LOADED = {}                                   # model name -> (module, cfg)


def available(model="dereverb", need_gpu=True):
    """Model files on disk (and CUDA unless need_gpu=False)."""
    if os.environ.get("SOTADAW_NO_DRYCLEAN") == "1":
        return False
    m = MODELS.get(model)
    if m is None:
        return False
    try:
        ck = os.path.join(MSS_DIR, m["ckpt"])
        cf = os.path.join(MSS_DIR, m["yaml"])
        if not (os.path.exists(cf) and os.path.exists(ck)
                and os.path.getsize(ck) == m["bytes"]):
            return False
        if need_gpu:
            import torch
            return torch.cuda.is_available()
        return True
    except Exception:
        return False


def _load(model, device):
    if model in _LOADED:
        mod, cfg = _LOADED[model]
        return mod.to(device), cfg
    import torch
    import yaml
    import inspect
    sys.path.insert(0, os.path.join(ROOT, "third_party", "bs_roformer"))
    from mel_band_roformer import MelBandRoformer
    m = MODELS[model]
    cfg = yaml.unsafe_load(open(os.path.join(MSS_DIR, m["yaml"])))
    mk = dict(cfg["model"])
    sig = set(inspect.signature(MelBandRoformer.__init__).parameters)
    net = MelBandRoformer(**{k: v for k, v in mk.items() if k in sig})
    state = torch.load(os.path.join(MSS_DIR, m["ckpt"]), map_location="cpu",
                       weights_only=True)
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    state = {(k[6:] if k.startswith("model.") else k): v
             for k, v in state.items()}
    net.load_state_dict(state)
    net.eval()
    _LOADED[model] = (net, cfg)
    return net.to(device), cfg


def clean(x, sr, model="dereverb", num_overlap=2, device=None, progress=None,
          precision="fp16"):
    """x [N,2] (or mono) at 44100 -> (target [N,2], residual [N,2]) float64.
    Chunked hann overlap-add; target+residual == x exactly (closure law).

    precision on cuda: fp16 is THE working mode (measured 2026-07-12:
    bf16 dies in view_as_complex inside the arch's iSTFT; fp32 has no
    flash-attention kernel; fp16 verdicts matched cpu/fp32 exactly on the
    probe material). cpu is always fp32 — and roformer-slow (minutes per
    12s clip): CPU is for batteries and tiny clips, not stems."""
    import torch
    assert sr == 44100, f"mel_clean runs at 44100 (got {sr})"
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    net, cfg = _load(model, device)
    C = int(cfg["audio"]["chunk_size"])
    step = C // max(1, int(num_overlap))
    N = len(x)
    mix = torch.from_numpy(np.ascontiguousarray(x[:, :2].T)).float()
    pad = C
    mix = torch.nn.functional.pad(mix, (pad, pad + (step - (N % step)) % step))
    total = mix.shape[1]
    out = torch.zeros_like(mix)
    norm = torch.zeros(total)
    win = torch.hann_window(C, periodic=False).clamp(min=1e-3)
    n_chunks = (total - C) // step + 1
    amp_dtype = {"bf16": torch.bfloat16, "fp16": torch.float16}.get(precision)
    with torch.no_grad():
        for ci, a in enumerate(range(0, total - C + 1, step)):
            seg = mix[:, a:a + C].unsqueeze(0).to(device)
            with torch.autocast("cuda", dtype=amp_dtype or torch.float16,
                                enabled=(device == "cuda"
                                         and amp_dtype is not None)):
                v = net(seg)
            v = v.float().cpu()
            if v.dim() == 4:               # (b, stems, ch, t) -> target stem 0
                v = v[:, 0]
            out[:, a:a + C] += v[0] * win
            norm[a:a + C] += win
            if progress and (ci % 2 == 0 or ci == n_chunks - 1):
                progress(ci + 1, n_chunks)
    tgt = (out / norm.clamp(min=1e-6)).numpy().T[pad:pad + N].astype(np.float64)
    res = x[:, :2].astype(np.float64) - tgt
    return tgt, res


def clean_cached(stem_wav, model="dereverb", device=None, say=print):
    """Dry twin for a stem, cached next to it as <stem>_<target>.wav.
    Returns the dry path, or None (unavailable / kill switch / cache miss
    on a gpu-less box). The wet original is never touched."""
    need_gpu = device != "cpu"
    base = os.path.splitext(os.path.abspath(stem_wav))[0]
    tgt_path = f"{base}_{MODELS[model]['target']}.wav"
    if os.path.exists(tgt_path) and \
            os.path.getmtime(tgt_path) >= os.path.getmtime(stem_wav):
        return tgt_path                                # REUSE LAW
    if not available(model, need_gpu=need_gpu):
        return None
    import soundfile as sf
    x, sr = sf.read(stem_wav, always_2d=True)
    if sr != 44100:
        return None                                    # stems are 44.1k; stay honest
    say(f"[mel_clean] {model}: {len(x)/sr:.0f}s "
        f"({'cuda' if need_gpu else 'cpu'})…", flush=True)
    try:
        tgt, _ = clean(x[:, :2], sr, model=model, device=device)
    except Exception as e:                             # CUDA OOM vs a live
        say(f"[mel_clean] {model} skipped ({type(e).__name__}: {e}) "
            f"-> wet stem kept", flush=True)           # training run, etc.
        return None
    # atomic write — tmp must keep .wav (soundfile infers format from the
    # extension; a bare .tmp suffix broke the FIRST live E2E at the finish)
    tmp = tgt_path[:-4] + ".tmp.wav"
    sf.write(tmp, tgt.astype(np.float32), sr, subtype="FLOAT")
    os.replace(tmp, tgt_path)
    return tgt_path


def main():
    import argparse
    import time
    import soundfile as sf
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("in_wav")
    ap.add_argument("out_target")
    ap.add_argument("out_residual", nargs="?")
    ap.add_argument("--model", default="dereverb", choices=sorted(MODELS))
    ap.add_argument("--device", default=None, choices=[None, "cpu", "cuda"])
    ap.add_argument("--overlap", type=int, default=2)
    a = ap.parse_args()
    if not available(a.model, need_gpu=(a.device != "cpu")):
        sys.exit(f"[mel_clean] {a.model} unavailable (files missing, no CUDA, "
                 f"or SOTADAW_NO_DRYCLEAN=1)")
    x, sr = sf.read(a.in_wav, always_2d=True)
    t0 = time.time()
    tgt, res = clean(x[:, :2], sr, model=a.model, device=a.device,
                     num_overlap=a.overlap,
                     progress=lambda i, n: print(f"\r[mel_clean] {i}/{n}",
                                                 end="", flush=True))
    print(f"\n[mel_clean] {a.model}: {len(x)/sr:.0f}s in {time.time()-t0:.0f}s")
    sf.write(a.out_target, tgt.astype(np.float32), sr, subtype="FLOAT")
    if a.out_residual:
        sf.write(a.out_residual, res.astype(np.float32), sr, subtype="FLOAT")


if __name__ == "__main__":
    main()
